import json
import logging
from typing import List

from langchain_core.messages import AIMessage
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
from langchain_core.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    FewShotChatMessagePromptTemplate,
)
from langchain_core.runnables import RunnableParallel, RunnableSequence, RunnableLambda
from langchain_openai import OpenAIEmbeddings
from langchain_neo4j import Neo4jGraph, Neo4jVector

from .helpers import generate_full_text_query
from .data_models import Entities

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class Chains:
    def __init__(self, llm):
        logger.info("[Chains] Initializing Chains class")
        self.llm = llm
        self.graph_db = Neo4jGraph()
        self.vector_index = Neo4jVector.from_existing_graph(
            OpenAIEmbeddings(),
            search_type="hybrid",
            node_label="Document",
            text_node_properties=["text"],
            embedding_node_property="embedding"
        )

    def BooleanOutputParser(self, ai_message: AIMessage) -> bool:
        logger.info("[Chains] Parsing boolean output")
        try:
            return 'yes' in ai_message.content.lower()
        except Exception as e:
            logger.warning(f"[Chains] BooleanOutputParser error: {e}")
            return False

    def safeListOutputParser(self, ai_message):
        logger.info("[Chains] Parsing safe list output")
        try:
            message_text = ai_message.content
            logger.debug(f"[Chains] Raw AI message content: {message_text!r}")
            questions_list = json.loads(message_text)
            if isinstance(questions_list, list):
                return message_text
        except Exception as e:
            logger.warning(f"[Chains] safeListOutputParser failed: {e}")
            logger.warning(f"[Chains] Offending message content: {ai_message.content!r}")
        return json.dumps([])


    def get_initial_check_chain(self):
        logger.info("[Chains] Creating initial check chain")
        prompt = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template("You can only answer yes or no."),
            HumanMessagePromptTemplate.from_template("Is the following text a business-related question?\n\nText: {text}")
        ])
        return prompt | self.llm | StrOutputParser() | self.BooleanOutputParser

    def get_history_check_chain(self):
        logger.info("[Chains] Creating history check chain")
        prompt = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template("You can only answer yes or no."),
            HumanMessagePromptTemplate.from_template(
                "Previous questions: {history}\nLatest question: {text}"
            )
        ])
        return prompt | self.llm | StrOutputParser() | self.BooleanOutputParser

    def get_elaboration_chain(self):
        logger.info("[Chains] Creating elaboration chain")
        prompt = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template("Please elaborate on the entity in the following text."),
            HumanMessagePromptTemplate.from_template("Text: {text}")
        ])
        return prompt | self.llm | StrOutputParser()

    def get_follow_up_questions_chain(self):
        logger.info("[Chains] Creating follow-up questions chain")
        template = """You are given a full chat history and the latest user question.\n{chat_history}\n\nQuestion: {question}\n[...]"""
        prompt = ChatPromptTemplate.from_template(template)
        return RunnableParallel({
            "chat_history": lambda x: x["chat_history"],
            "question": lambda x: x["question"],
        }) | prompt | self.llm | self.safeListOutputParser

    def get_tangential_questions_chain(self):
        logger.info("[Chains] Creating tangential questions chain")
        template = """Chat History:\n{chat_history}\n\nLatest Inquiry:\n{question}\n[...]"""
        prompt = ChatPromptTemplate.from_template(template)
        return RunnableParallel({
            "chat_history": lambda x: x["chat_history"],
            "question": lambda x: x["question"],
        }) | prompt | self.llm | self.safeListOutputParser

    def get_entity_chain(self):
        logger.info("[Chains] Creating entity extraction chain")
        prompt = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template("Extract object, event entities from the given text."),
            HumanMessagePromptTemplate.from_template("Text: {text}")
        ])
        return prompt | self.llm.with_structured_output(Entities)

    def structured_retriever(self, entities):
        logger.info("[Chains] Performing structured retrieval for entities: %s", entities)
        result = ""
        try:
            if not entities or not entities.names:
                logger.warning("[Chains] No entities found or 'names' is None")
                return result
            self.graph_db.query("CREATE FULLTEXT INDEX entity IF NOT EXISTS FOR (e:__Entity__) ON EACH [e.id]")
            for entity in entities.names:
                response = self.graph_db.query(
                    """CALL db.index.fulltext.queryNodes('entity', $query, {limit: 5})
                    YIELD node, score
                    CALL {
                        WITH node
                        MATCH (node)-[r:!MENTIONS]->(neighbor)
                        RETURN node.id + ' - ' + type(r) + ' -> ' + neighbor.id AS output
                        UNION ALL
                        WITH node
                        MATCH (node)<-[r:!MENTIONS]-(neighbor)
                        RETURN neighbor.id + ' - ' + type(r) + ' -> ' + node.id AS output
                    }
                    RETURN output LIMIT 50""",
                    {"query": generate_full_text_query(entity)},
                )
                logger.info("[Chains] Retrieved structured data for %s: %s", entity, response)
                result += "\n".join([el['output'] for el in response])
        except Exception as e:
            logger.error(f"[Chains] Structured retrieval failed: {e}")
        return result

    def get_context(self, message: str) -> str:
        logger.info("[Chains] Generating context for message: %s", message)
        try:
            entities = self.get_entity_chain().invoke({"text": message})
            logger.info(f"[Chains] Extracted entities: {entities}")
            structured_data = self.structured_retriever(entities)
            unstructured_data = [doc.page_content for doc in self.vector_index.similarity_search(message)]
            return f"""Structured data:\n{structured_data}\n\nUnstructured data:\n{'#Document '.join(unstructured_data)}"""
        except Exception as e:
            logger.error(f"[Chains] get_context failed: {e}")
            return "No relevant context found."

    def get_response_chain(self):
        logger.info("[Chains] Creating response chain")
        template = """Answer the question based only on the following context:\n{context}\n\nQuestion: {question}\nUse point form with '~' bullets."""
        prompt = ChatPromptTemplate.from_template(template)
        return RunnableParallel({
            "context": lambda x: self.get_context(x["question"]),
            "question": lambda x: x["question"],
        }) | prompt | self.llm | StrOutputParser()

    def get_full_response_chain(self):
        logger.info("[Chains] Creating full response chain")
        template = """Answer the question based only on the following context:\n{context}\n\nQuestion: {question}\nAnswer:"""
        prompt = ChatPromptTemplate.from_template(template)
        return RunnableParallel({
            "context": lambda x: self.get_context(x["question"]),
            "question": lambda x: x["question"],
        }) | prompt | self.llm | StrOutputParser()

    def get_action_router_chain(self, actions_list):
        logger.info("[Chains] Creating action router chain")
        from langchain_core.prompts import ChatPromptTemplate

        choose_action_prompt = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(
                """
                You are an intelligent assistant.
                Your task is to match a user's query to a list of actions based on the inputs required for each action.
                Return the JSON with a single key 'name' and value being a list of matching action names.
                Return 'NA' if nothing matches.
                """
            ),
            SystemMessagePromptTemplate.from_template(
                "\n".join([
                    f"Action type: {action['action_type']}\n"
                    f"Action name: {action['action_name']}\n"
                    f"Action description: {action['action_description']}\n"
                    f"Action input: {action['input']}\n"
                    f"Action output: {action['output']}\n"
                    for action in actions_list.get_list()
                ])
            ),
            HumanMessagePromptTemplate.from_template("Query: {query}")
        ])

        return choose_action_prompt | self.llm | JsonOutputParser()

    def get_generate_action_prompt_chain(self):
        logger.info("[Chains] Creating generate action prompt chain")
        from langchain_core.prompts import ChatPromptTemplate, FewShotChatMessagePromptTemplate

        examples = [
            {
                "query": "Summarize the sales for Shop A.",
                "action_description": "Search for which product had the most sales from a specific shop.",
                "action_input": ["sales", "shop name"],
                "action_output": ["product name", "product ID"],
                "answer": "First, give me the name of the product that had the most sales from Shop A. Then, use that product name to find the product ID."
            },
            {
                "query": "Give report on Customer A.",
                "action_description": "Give the full details of a customer.",
                "action_input": ["customer name"],
                "action_output": ["customer ID", "customer name", "customer email", "customer phone", "customer address", "gender", "age"],
                "answer": "Give me the customer ID, customer name, customer email, customer phone, customer address, gender, age of Customer A."
            }
        ]

        example_prompt = ChatPromptTemplate.from_messages([
            ("system", 
            "Query: {query}\n"
            "Action description: {action_description}\n"
            "Action input: {action_input}\n"
            "Action output: {action_output}\n"
            "Answer: {answer}")
        ])

        few_shot_prompt = FewShotChatMessagePromptTemplate(
            examples=examples,
            example_prompt=example_prompt
        )

        main_prompt = ChatPromptTemplate.from_messages([
            ("system", 
            "You are an intelligent assistant. Generate systematic prompts based on the action's inputs and outputs."),
            ("system", 
            "I will give you examples to learn from."),
            few_shot_prompt,
            ("system", 
            "Do not include any explanation. Just return the answer."),
            ("human", "Query: {query}\nAction description: {action_description}\nAction input: {action_input}\nAction output: {action_output}")
        ])

        return main_prompt | self.llm | StrOutputParser()

    def get_api_extract_input_chain(self):
        logger.info("[Chains] Creating API extract input chain")
        from langchain_core.prompts import ChatPromptTemplate

        prompt = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(
                """
                You are an expert at extracting API input parameters from a user query.
                Your task is to extract each input for the API call from the user's text.
                Return a JSON where keys are the input names and values are either extracted values or empty strings if not found.

                - Keep the input names exactly as given (do not rename).
                - Use snake_case for the keys in JSON (if needed).
                - Only include the specified keys in the output.
                """
            ),
            HumanMessagePromptTemplate.from_template(
                "Query: {query}\nInputs: {action_input}"
            )
        ])

        return prompt | self.llm | JsonOutputParser()

    def get_multi_db_router_chain(self, database_list):
        logger.info("[Chains] Creating multi DB router chain")
        from langchain_core.prompts import ChatPromptTemplate, FewShotChatMessagePromptTemplate

        example_prompt = ChatPromptTemplate.from_messages([
            ("system", 
            "Database name: {database_name}\n"
            "Description: {database_description}\n"
            "Columns: {columns}")
        ])

        few_shot_prompt = FewShotChatMessagePromptTemplate(
            example_prompt=example_prompt,
            examples=database_list.get_list()
        )

        router_prompt = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(
                """
                You are a database router assistant.
                Your task is to match a user query to one or more databases based on descriptions and columns.
                Return a JSON with a single key 'choice' and a list of database names as the value.
                If no match is found, return 'choice': 'NA'.
                """
            ),
            few_shot_prompt,
            HumanMessagePromptTemplate.from_template("Query: {query}")
        ])

        return router_prompt | self.llm | JsonOutputParser()

    def get_general_response_chain(self):
        logger.info("[Chains] Creating general response chain")
        from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate

        general_response_prompt = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(
                """
                You are an intelligent CRM assistant named Waffles Copilot.

                Guidelines:
                1. If the query is not CRM-related (e.g., weather, stock price), politely redirect the user.
                2. If the user asks about you (e.g., \"who are you?\"), explain your role.
                3. If the message is hateful or inappropriate, respond firmly and redirect.
                4. If the query is in a non-English language, respond that you can only understand English.

                Always keep your answers short and professional.
                """
            ),
            HumanMessagePromptTemplate.from_template("Query: {query}")
        ])

        return general_response_prompt | self.llm | StrOutputParser()



    def get_final_output_chain(self, outputs: list):
        logger.info("[Chains] Building final output chain...")

        try:
            logger.debug("[Chains] Raw outputs passed: %s", outputs)

            if not outputs or not isinstance(outputs, list):
                raise ValueError("Expected a non-empty list of outputs in final output chain.")

            first = outputs[0]
            if not isinstance(first, dict) or "output" not in first:
                raise ValueError(f"Invalid structure in outputs[0]: {first}")

            db_result = first["output"]

            if isinstance(db_result, list):
                db_result = "\n".join(str(item) for item in db_result)

            if not isinstance(db_result, str):
                raise TypeError(f"[Chains] db_result must be a string, got: {type(db_result)}")

            # Build a prompt template
            prompt_template = ChatPromptTemplate.from_messages([
                ("system", "You are a helpful CRM assistant."),
                ("human", "Here is the database result:\n\n{db_result}\n\nSummarize this for the user.")
            ])

            # 👇 COMBINE the prompt and LLM into a runnable chain
            chain = RunnableLambda(lambda _: {"db_result": db_result}) | prompt_template | self.llm

            logger.debug("[Chains] Final output chain created successfully.")
            return chain

        except Exception as e:
            logger.error("[Chains] Failed to build final output chain: %s", e)
            raise






