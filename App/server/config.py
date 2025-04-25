# App/server/config.py

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Server config
DEBUG = True
SECRET_KEY = os.getenv("SECRET_KEY", "dev-key")

# File paths
ACTIONS_FILE_PATH = "./text_db/actions.txt"
DB_FILE_PATH = "./text_db/db.txt"
CSV_UPLOAD_DIR = "./csv_db"

# Azure Speech API
SPEECH_KEY = os.getenv("SPEECH_KEY")
SPEECH_REGION = os.getenv("SPEECH_REGION")

# OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Neo4j (local or AuraDB)
NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")
AURA_INSTANCEID = os.getenv("AURA_INSTANCEID")
AURA_INSTANCENAME = os.getenv("AURA_INSTANCENAME")

# Jira (optional, used in action_service)
JIRA_DOMAIN = os.getenv("JIRA_DOMAIN")
JIRA_EMAIL = os.getenv("JIRA_EMAIL")
JIRA_API_KEY = os.getenv("JIRA_API_KEY")
