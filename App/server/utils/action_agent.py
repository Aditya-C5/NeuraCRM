import logging
from typing import List
from typing_extensions import TypedDict

from langgraph.graph import StateGraph, END
from langchain_core.messages import AIMessage
from .csv_agent import CSVAgentGPTInstance
from .message_store import MessageStore
from .chains import Chains
from .helpers import generate_full_text_query

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# ---------------------------
# Database Agent
# ---------------------------

class DBAgentGraphState(TypedDict):
    query: str
    database: str
    output: str
    verbose: bool


class DBAgent:
    def __init__(self, llm, chains: Chains, database_list):
        self.llm = llm
        self.chains = chains
        self.database_list = database_list
        self.multi_db_router_chain = chains.get_multi_db_router_chain(database_list)
        self.csv_agent = CSVAgentGPTInstance()
        self.initial_check = chains.get_initial_check_chain()
        self.full_response = chains.get_full_response_chain()
        self.general_response = chains.get_general_response_chain()

    def db_router_node(self, state: DBAgentGraphState):
        logger.info("[DBAgent] Entering db_router_node with query: %s", state["query"])
        query = state["query"]
        if state["verbose"]: logger.info("[DBAgent] Routing query to database")
        output = self.multi_db_router_chain.invoke({"query": query})
        logger.info("[DBAgent] Routing output: %s", output)
        return {"database": output.get("choice", "NA")}

    def db_router_edge(self, state: DBAgentGraphState):
        logger.info("[DBAgent] Evaluating edge for database: %s", state["database"])
        if not self.database_list.get_list() or state["database"] == "NA":
            logger.info("[DBAgent] Falling back to general")
            return "general"
        return "db_query"

    def database_query(self, state: DBAgentGraphState):
        logger.info("[DBAgent] Running database_query for: %s", state["query"])
        query = state["query"]
        db_paths = []
        for db_name in state["database"]:
            db_entry = next((db for db in self.database_list.get_list() if db["database_name"] == db_name), None)
            if db_entry:
                db_paths.append(db_entry["db_path"])

        logger.info("[DBAgent] Found database paths: %s", db_paths)
        if len(db_paths) == 1:
            result = self.csv_agent.get_csv_agent_output(db_paths[0], query)
        else:
            result = self.csv_agent.get_csv_agent_output(db_paths, query)

        logger.info("[DBAgent] Database query result: %s", result)
        return {"output": result}

    def general(self, state: DBAgentGraphState):
        logger.info("[DBAgent] Falling back to general handler for: %s", state["query"])
        question = state["query"]
        needs_llm = self.initial_check.invoke({"text": question})
        logger.info("[DBAgent] LLM check result: %s", needs_llm)
        response = (
            self.full_response.invoke({"question": question}) if needs_llm
            else self.general_response.invoke({"query": question})
        )
        logger.info("[DBAgent] General response: %s", response)
        return {"output": response}

    def build_workflow(self):
        logger.info("[DBAgent] Building workflow")
        workflow = StateGraph(DBAgentGraphState)
        workflow.add_node("db_router_node", self.db_router_node)
        workflow.add_node("db_query", self.database_query)
        workflow.add_node("general", self.general)

        workflow.set_entry_point("db_router_node")
        workflow.add_conditional_edges("db_router_node", self.db_router_edge, {
            "general": "general",
            "db_query": "db_query"
        })
        workflow.add_edge("db_query", END)
        workflow.add_edge("general", END)

        return workflow.compile()

    def run_agent(self, query: str, session_id=None, verbose=True):
        logger.info("[DBAgent] Running agent for query: %s", query)
        agent = self.build_workflow()
        result = agent.invoke({"query": query, "verbose": verbose, "sessionId": session_id})
        logger.info("[DBAgent] Agent result: %s", result)
        return result


# ---------------------------
# Action Agent
# ---------------------------

class ActionAgentGraphState(TypedDict):
    query: str
    actions: str
    actions_prompts: List[str]
    query_output: List[str]
    output: str
    verbose: bool


class ActionAgent:
    def __init__(self, llm, chains: Chains, actions_list, database_list, gpt_instance, message_store: MessageStore):
        self.llm = llm
        self.chains = chains
        self.actions_list = actions_list
        self.database_list = database_list
        self.gpt = gpt_instance
        self.store = message_store

        self.action_router = chains.get_action_router_chain(actions_list)
        self.generate_prompt = chains.get_generate_action_prompt_chain()
        self.extract_api_input = chains.get_api_extract_input_chain()
        self.dba = DBAgent(llm, chains, database_list)

    def actions_router_node(self, state):
        logger.info("[ActionAgent] Routing query: %s", state["query"])
        query = state["query"].lower()
        actions = self.actions_list.get_list()

        def relevance_score(action):
            score = 0
            if any(word in query for word in action["action_name"].lower().split()):
                score += 2
            for word in action["action_description"].lower().split():
                if word in query:
                    score += 1
            for param in action["input"]:
                if param.lower() in query:
                    score += 2
            return score

        matches = sorted([(a, relevance_score(a)) for a in actions], key=lambda x: x[1], reverse=True)
        matches = [a for a, s in matches if s >= 2]
        logger.info("[ActionAgent] Matched actions: %s", matches)

        api_keywords = ['create', 'send', 'email', 'schedule']
        if any(k in query for k in api_keywords):
            logger.info("[ActionAgent] Detected API-type query")
            return {"actions": "api_type_node"}

        if matches:
            return {
                "actions": "generate_action_prompt",
                "selected_actions": matches[:2]  # Top 2
            }

        return {"actions": "fallback_to_ai"}

    def fallback_response(self, state):
        logger.info("[ActionAgent] Fallback response for: %s", state["query"])
        response = self.gpt.process_message(state["query"], self.store, state.get("sessionId", ""))
        logger.info("[ActionAgent] Fallback response result: %s", response)
        return {
            "output": response[0],
            "followUpQuestions": response[1],
            "tangentialQuestions": response[2]
        }

    def actions_router_edge(self, state):
        logger.info("[ActionAgent] Determining next edge for actions: %s", state["actions"])
        if state["actions"] == "fallback_to_ai":
            return "fallback"
        if not self.actions_list.get_list() or state["actions"] == "NA":
            return "general"
        return "api_type_node" if "api_type_node" in state["actions"] else "generate_action_prompt"

    def generate_action_prompt(self, state):
        logger.info("[ActionAgent] Generating action prompts for: %s", state.get("selected_actions", []))
        prompts = []
        for action in state.get("selected_actions", []):
            prompt = self.generate_prompt.invoke({
                "action_description": action["action_description"],
                "action_input": action["input"],
                "action_output": action["output"],
                "query": state["query"]
            })
            prompts.append(prompt)
        logger.info("[ActionAgent] Generated prompts: %s", prompts)
        return {"actions_prompts": prompts}

    def api_type_node(self, state):
        logger.info("[ActionAgent] Handling API type node for actions: %s", state["actions"])
        selected = next((a for a in self.actions_list.get_list() if a["action_name"] in state["actions"]), None)
        extracted = self.extract_api_input.invoke({
            "query": state["query"],
            "action_name": selected["action_name"],
            "action_desc": selected["action_description"],
            "action_input": str(selected["input"])
        })
        logger.info("[ActionAgent] Extracted API input: %s", extracted)
        return {
            "output": {
                "action_name": selected["action_name"],
                "action_desc": selected["action_description"],
                "action_type": "api_call",
                "api_service": selected["api_service"],
                "extracted_inputs": extracted
            }
        }

    def db_query(self, state):
        logger.info("[ActionAgent] Executing DB query")
        if not state.get("actions_prompts"):
            return {"query_output": [self.dba.run_agent(state["query"])]}
        results = [self.dba.run_agent(prompt) for prompt in state["actions_prompts"]]
        logger.info("[ActionAgent] DB query results: %s", results)
        return {"query_output": results}

    def generate_final_output(self, state):
        logger.info("[ActionAgent] Generating final output")

        query_output = state.get("query_output")

        # 🔒 If no query_output, fallback to output directly
        if not query_output:
            fallback_response = state.get("output") or "~ I'm not sure how to help with that."
            logger.info("[ActionAgent] Using fallback output: %s", fallback_response)
            return {"output": fallback_response}

        # Normalize to list
        if isinstance(query_output, dict):
            query_output = [query_output]

        outputs = []
        for r in query_output:
            val = r.get("output")
            if isinstance(val, dict):
                outputs.append(val)
            elif isinstance(val, str):
                outputs.append({"answer": val})  # 👈 compatibility with prompt
            else:
                logger.warning("[ActionAgent] Skipping unexpected output type: %s", type(val))

        logger.debug("[ActionAgent] Final outputs to feed into prompt: %s", outputs)

        if not outputs:
            raise ValueError("Received empty outputs list in final output chain.")

        final_chain = self.chains.get_final_output_chain(outputs)
        result = final_chain.invoke({"query": state["query"]})

        logger.info("[ActionAgent] Final result: %s", result)

        # ✅ Wrap result in dict (LangGraph expects this)
        if isinstance(result, AIMessage):
            return {"output": result.content}
        return {"output": str(result)}


    def build_workflow(self):
        logger.info("[ActionAgent] Building workflow")
        workflow = StateGraph(ActionAgentGraphState)
        workflow.add_node("actions_router_node", self.actions_router_node)
        workflow.add_node("generate_action_prompt", self.generate_action_prompt)
        workflow.add_node("db_query", self.db_query)
        workflow.add_node("generate_final_output", self.generate_final_output)
        workflow.add_node("api_type_node", self.api_type_node)
        workflow.add_node("fallback", self.fallback_response)

        workflow.set_entry_point("actions_router_node")

        workflow.add_conditional_edges("actions_router_node", self.actions_router_edge, {
            "generate_action_prompt": "generate_action_prompt",
            "api_type_node": "api_type_node",
            "fallback": "fallback",
            "general": "db_query"
        })
        workflow.add_edge("generate_action_prompt", "db_query")
        workflow.add_edge("db_query", "generate_final_output")
        workflow.add_edge("generate_final_output", END)
        workflow.add_edge("api_type_node", END)
        workflow.add_edge("fallback", END)

        return workflow.compile()

    def run_agent(self, query: str, session_id=None, verbose=True):
        logger.info("[ActionAgent] Running agent for query: %s", query)

        agent = self.build_workflow()
        state = {
            "query": query,
            "verbose": verbose,
            "sessionId": session_id
        }

        result = agent.invoke(state)
        logger.debug("[ActionAgent] Raw agent result: %s", result)

        # Generate final output from collected intermediate state
        output = self.generate_final_output(result)

        logger.info("[ActionAgent] Final result: %s", output)

        return {
            "query": query,
            "actions": result.get("actions", "unknown"),
            "actions_prompts": result.get("actions_prompts", []),
            "query_output": result.get("query_output"),
            "output": output,
            "verbose": verbose
        }

