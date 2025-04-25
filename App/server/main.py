# app/server/main.py
# To run: (.venv) PS C:\Users\rusht\Desktop\NeuraCRM_updated\app> python -m server.main

from flask import Flask
from flask_cors import CORS
from flask_socketio import SocketIO
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
import json

from .utils import (
    MessageStore, GPTInstance, ActionAgent, Chains, ActionsList, DatabaseList
)
from .routes.socketio_routes import register_socketio_handlers
from .routes.api_routes import create_api_routes

# Load environment variables
load_dotenv()

# App and SocketIO setup
app = Flask(__name__)
CORS(app, support_credentials=True)
socketio = SocketIO(app, cors_allowed_origins="*")
app.secret_key = 'random secret key!'

# Initialize core components
message_store = MessageStore()
llm_instance = ChatOpenAI(model="gpt-4o", temperature=0)
chain_instance = Chains(llm_instance)
gpt_instance = GPTInstance(llm_instance, chain_instance, debug=True)

with open("server/text_db/db.txt", 'r') as db_file:
    database_list = json.load(db_file)
db_instance = DatabaseList(database_list)

with open("server/text_db/actions.txt", 'r') as act_file:
    actions_list = json.load(act_file)
actions_instance = ActionsList(actions_list)

action_agent_instance = ActionAgent(
    llm_instance,
    chain_instance,
    actions_instance,
    db_instance,
    gpt_instance,
    message_store
)

# Register API routes
#app.register_blueprint(api_bp)

# 🔗 Register API + Socket Routes
app.register_blueprint(create_api_routes(actions_instance, db_instance))
register_socketio_handlers(socketio, gpt_instance, action_agent_instance, message_store, actions_instance)

if __name__ == "__main__":
    socketio.run(app, port=9000, debug=True)

