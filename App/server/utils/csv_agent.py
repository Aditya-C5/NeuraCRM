from langchain_openai import ChatOpenAI
from langchain.agents.agent_types import AgentType
from langchain_experimental.agents.agent_toolkits import create_csv_agent
import logging
import os

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class CSVAgentGPTInstance:
    def __init__(self, debug=False) -> None:
        logger.info("[CSVAgent] Initializing CSVAgentGPTInstance with debug=%s", debug)
        self.llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo")
        self.debug = debug

    def get_csv_agent(self, db_path: str):
        # Ensure path is absolute
        if not os.path.isabs(db_path):
            db_path = os.path.abspath(db_path)
        logger.info("[CSVAgent] Creating CSV agent for path: %s", db_path)

        return create_csv_agent(
            self.llm,
            db_path,
            verbose=self.debug,
            agent_type=AgentType.OPENAI_FUNCTIONS,
            allow_dangerous_code=True,
        )

    def get_csv_agent_output(self, db_path: str, question: str) -> str:
        # Ensure path is absolute
        if not os.path.isabs(db_path):
            db_path = os.path.abspath(db_path)
        logger.info("[CSVAgent] Getting CSV agent output for question: %s", question)
        agent = self.get_csv_agent(db_path)
        result = agent.invoke(question)
        logger.info("[CSVAgent] Output result: %s", result)
        return result
