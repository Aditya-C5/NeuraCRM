# App/server/routes/api_routes.py

from flask import Blueprint, request, jsonify, abort
import os
import requests
from ..utils.data_models import ActionsList, DatabaseList
from ..services import action_service, database_service
from ..utils import message_store



#api_bp = Blueprint("api", __name__)
#actions_instance = ActionsList([])  # Will be initialized on app start
#db_instance = DatabaseList([])  # Will be initialized on app start

"""
@api_bp.route("/api/get-actions", methods=["GET"])
def get_actions_api():
    return action_service.get_actions(actions_instance)

@api_bp.route("/api/actions", methods=["POST"])
def post_action_api():
    new_action = request.json
    return action_service.post_action(actions_instance, new_action)

@api_bp.route("/api/save-action", methods=["POST"])
def save_action_api():
    action = request.json
    result = action_service.save_action_direct(actions_instance, action)
    return jsonify(result)

@api_bp.route("/api/get-databases", methods=["GET"])
def get_databases_api():
    return database_service.get_databases()

@api_bp.route("/api/databases", methods=["POST"])
def post_database_api():
    form_data = request.form
    file = request.files.get("database_file")
    if not file:
        return jsonify({"error": "No file provided"}), 400

    return database_service.post_database(db_instance, file, form_data)

@api_bp.route("/api/get-token", methods=["GET"])
def get_token():
    speech_key = os.environ.get('SPEECH_KEY')
    speech_region = os.environ.get('SPEECH_REGION')

    if not speech_key or not speech_region:
        abort(400, description="Missing SPEECH_KEY or SPEECH_REGION in env.")

    try:
        headers = {
            'Ocp-Apim-Subscription-Key': speech_key,
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        token_url = f'https://{speech_region}.api.cognitive.microsoft.com/sts/v1.0/issueToken'
        token_response = requests.post(token_url, headers=headers)
        token_data = token_response.text.strip()

        return jsonify({'token': token_data, 'region': speech_region})
    except requests.exceptions.RequestException as e:
        abort(500, description=str(e))


@api_bp.route("/api/get-messages", methods=["GET"])
def get_messages():
    session_id = request.form.get("sessionId")
    return jsonify(message_store.get_messages(session_id))


@api_bp.route("/api/demo_custom_api", methods=["POST"])
def demo_custom_api():
    return jsonify(request.json)
"""
def create_api_routes(actions_instance, db_instance):
    api_bp = Blueprint("api", __name__)

    @api_bp.route("/api/get-actions", methods=["GET"])
    def get_actions_api():
        return action_service.get_actions(actions_instance)

    @api_bp.route("/api/actions", methods=["POST"])
    def post_action_api():
        new_action = request.json
        return action_service.post_action(actions_instance, new_action)

    @api_bp.route("/api/save-action", methods=["POST"])
    def save_action_api():
        action = request.json
        result = action_service.save_action_direct(actions_instance, action)
        return jsonify(result)

    @api_bp.route("/api/get-databases", methods=["GET"])
    def get_databases_api():
        return database_service.get_databases()

    @api_bp.route("/api/databases", methods=["POST"])
    def post_database_api():
        form_data = request.form
        file = request.files.get("database_file")
        if not file:
            return jsonify({"error": "No file provided"}), 400
        return database_service.post_database(db_instance, file, form_data)

    @api_bp.route("/api/get-token", methods=["GET"])
    def get_token():
        speech_key = os.environ.get('SPEECH_KEY')
        speech_region = os.environ.get('SPEECH_REGION')

        if not speech_key or not speech_region:
            abort(400, description="Missing SPEECH_KEY or SPEECH_REGION in env.")

        try:
            headers = {
                'Ocp-Apim-Subscription-Key': speech_key,
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            token_url = f'https://{speech_region}.api.cognitive.microsoft.com/sts/v1.0/issueToken'
            token_response = requests.post(token_url, headers=headers)
            token_data = token_response.text.strip()
            return jsonify({'token': token_data, 'region': speech_region})
        except requests.exceptions.RequestException as e:
            abort(500, description=str(e))

    @api_bp.route("/api/get-messages", methods=["GET"])
    def get_messages():
        session_id = request.form.get("sessionId")
        return jsonify(message_store.get_messages(session_id))

    @api_bp.route("/api/demo_custom_api", methods=["POST"])
    def demo_custom_api():
        return jsonify(request.json)

    return api_bp