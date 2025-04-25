# App/server/services/action_service.py

import json
import requests
from ..utils.data_models import ActionsList
from .jira_service import extract_action_item, create_action_item, create_issue
from .gmail_service import send_email

ACTIONS_FILE = "./text_db/actions.txt"

def get_actions(actions_list: ActionsList) -> str:
    try:
        with open(ACTIONS_FILE, "r") as f:
            return f.read()
    except Exception:
        return json.dumps([])


def post_action(actions_list: ActionsList, new_action: dict) -> tuple:
    with open(ACTIONS_FILE, "r") as f:
        try:
            existing = json.load(f)
        except json.JSONDecodeError:
            existing = []

    data = {
        "action_type": "api_call" if new_action.get("action_type") == "API" else "query_database",
        "action_name": new_action.get("action_name"),
        "action_description": new_action.get("description"),
        "api_endpoint": new_action.get("api_endpoint"),
        "api_service": new_action.get("api_service"),
        "input": [inp["value"] for inp in new_action.get("query_inputs", [])],
        "output": [out["value"] for out in new_action.get("query_outputs", [])],
        "api_auth": {obj["key"]: obj["value"] for obj in new_action.get("auth", [])}
    }

    existing.append(data)

    with open(ACTIONS_FILE, "w") as f:
        data_json = json.dumps(existing, indent=4)
        f.write(data_json)
        actions_list.set_list(existing)

    return data_json, 200


def save_action_direct(actions_list: ActionsList, action: dict) -> dict:
    file_path = ACTIONS_FILE
    with open(file_path, "r") as f:
        try:
            actions = json.load(f)
        except json.JSONDecodeError:
            actions = []

    actions.append(action)

    with open(file_path, "w") as f:
        json.dump(actions, f, indent=4)
        actions_list.set_list(actions)

    return action

# (add at the bottom of App/server/services/action_service.py)

def extract_action_items(data):
    from .jira_service import extract_action_item  # now valid
    try:
        extracted = extract_action_item(data)
        formatted = [{
            "id": extracted.index(item),
            "summary": item.summary,
            "description": item.description
        } for item in extracted]
        return formatted
    except Exception:
        return []


def create_action_item_from_data(data):
    from .jira_service import create_action_item  # now valid
    try:
        create_action_item(data)
        return {"status": "success"}
    except Exception:
        return {"status": "error"}


def handle_dynamic_api_call(data, actions_list: ActionsList) -> dict:
    from .jira_service import create_issue
    from App.server.services.gmail_service import send_email
    import requests

    api_service = data.get("api_service", "").lower()

    try:
        if api_service == "jira":
            jira_action = next(
                action for action in actions_list.get_list()
                if action.get("api_service", "").lower() == "jira"
            )
            endpoint = jira_action["api_endpoint"]
            auth = jira_action["api_auth"]
            title = data["extracted_inputs"]["issue_title"]
            description = data["extracted_inputs"]["issue_description"]

            create_issue(endpoint, title, description, auth)

            return {
                'status': "success",
                'extracted_inputs': data['extracted_inputs'],
                'index': data['index']
            }

        elif api_service == "gmail":
            gmail_action = next(
                action for action in actions_list.get_list()
                if action.get("api_service", "").lower() == "gmail"
            )
            subject = data['extracted_inputs']['email_subject']
            body = data['extracted_inputs']['email_body']
            recipient = data['extracted_inputs']['email_recipient']
            auth = gmail_action.get("api_auth")

            send_email(subject, body, recipient, auth)

            return {
                'status': "success",
                'extracted_inputs': data['extracted_inputs'],
                'index': data['index']
            }

        elif api_service == "custom":
            custom_action = next(
                action for action in actions_list.get_list()
                if action.get("action_name") == data['action_name']
            )
            endpoint = custom_action.get("api_endpoint")
            requests.post(endpoint, json=data['extracted_inputs'])

            return {
                'status': "success",
                'extracted_inputs': data['extracted_inputs'],
                'index': data['index']
            }

        else:
            return {
                'status': "error",
                'error': "Unknown API service",
                'index': data['index']
            }

    except Exception:
        return {
            'status': "error",
            'extracted_inputs': data.get('extracted_inputs', {}),
            'index': data.get('index', -1)
        }
