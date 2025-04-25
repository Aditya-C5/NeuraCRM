import logging
from typing import List

from langchain_openai import ChatOpenAI
from langchain.agents.agent_types import AgentType
from langchain_experimental.agents.agent_toolkits import create_csv_agent

from .chains import Chains
from .message_store import MessageStore

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class GPTInstance:
    def __init__(self, llm, chains: Chains, debug=False) -> None:
        logger.info("[GPTInstance] Initializing GPTInstance")
        self.llm = llm
        self.chains = chains
        self.debug = debug

    def process_message(self, message: str, message_store: MessageStore, session_id: str) -> List[str]:
        """
        Process a message and return AI response + follow-up + tangential questions.
        """
        logger.info("[GPTInstance] Processing message: %s", message)
        chat_history = message_store.get_messages(session_id)
        logger.debug("[GPTInstance] Retrieved chat history: %s", chat_history)

        response_chain = self.chains.get_response_chain()
        response = response_chain.invoke({"question": message})
        logger.info("[GPTInstance] Main response: %s", response)

        follow_up = self.get_follow_up_questions(chat_history, response)
        tangential = self.get_tangential_questions(chat_history, response)

        logger.info("[GPTInstance] Follow-up questions: %s", follow_up)
        logger.info("[GPTInstance] Tangential questions: %s", tangential)

        return [response, follow_up, tangential]

    def check_for_response(self, message: str, message_store: MessageStore, session_id: str) -> bool:
        """
        Check whether the AI should respond.
        """
        logger.info("[GPTInstance] Checking if response is needed for: %s", message)
        history = message_store.get_messages(session_id)
        logger.debug("[GPTInstance] Session history: %s", history)

        init_check = self.chains.get_initial_check_chain().invoke({"text": message})
        logger.info("[GPTInstance] Initial check result: %s", init_check)

        if init_check:
            history_check = self.chains.get_history_check_chain().invoke({"text": message, "history": history})
            logger.info("[GPTInstance] History check result: %s", history_check)
            return not history_check
        return False

    def elaborate_on_chosen_point(self, message: str) -> str:
        logger.info("[GPTInstance] Elaborating on message: %s", message)
        return self.chains.get_elaboration_chain().invoke({"text": message})

    def get_follow_up_questions(self, chat_history: List[str], question: str):
        logger.info("[GPTInstance] Getting follow-up questions for: %s", question)
        return self.chains.get_follow_up_questions_chain().invoke({
            "chat_history": chat_history,
            "question": question
        })

    def get_tangential_output(self, question: str):
        logger.info("[GPTInstance] Getting tangential output for: %s", question)
        return self.chains.get_full_response_chain().invoke({"question": question})

    def get_tangential_questions(self, chat_history: List[str], question: str):
        logger.info("[GPTInstance] Getting tangential questions for: %s", question)
        return self.chains.get_tangential_questions_chain().invoke({
            "chat_history": chat_history,
            "question": question
        })
