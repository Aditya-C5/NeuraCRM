# App/server/services/gpt_service.py

from ..utils.message_store import MessageStore
from ..utils.gpt_instance import GPTInstance
from ..utils.data_models import ActionsList, DatabaseList
from ..utils.action_agent import ActionAgent


def process_transcribed_message(data, gpt_instance: GPTInstance, action_agent: ActionAgent, message_store: MessageStore):
    """
    Handles incoming 'data' from SocketIO when a new message is transcribed.

    Args:
        data: dict with keys 'sessionId', 'transcribedList'
    """
    session_id = data['sessionId']
    new_message = data['transcribedList'][-1]

    formatted_message = {
        'sessionId': session_id,
        'text': f"{new_message['speakerId']}: {new_message['text'].strip()}"
    }

    message_store.add_message(formatted_message)

    response_needed = gpt_instance.check_for_response(new_message['text'], message_store, session_id)
    if not response_needed:
        return {"skip": True}

    # Use ActionAgent to check for action routing
    action_result = action_agent.actions_router_node({
        'query': new_message['text'],
        'verbose': True
    })

    # If no matching action is found, fallback to GPT processing
    if action_result.get('actions') == "fallback_to_ai":
        [ai_response, follow_ups, tangents] = gpt_instance.process_message(
            new_message['text'], message_store, session_id)
    else:
        # Even if action found, still use GPT for response generation
        [ai_response, follow_ups, tangents] = gpt_instance.process_message(
            new_message['text'], message_store, session_id)

    message_store.add_ai_message({
        'sessionId': session_id,
        'aiMessage': ai_response
    })
    message_store.add_follow_up_questions({
        'sessionId': session_id,
        'followUpQuestions': follow_ups
    })

    return {
        'aiMessage': ai_response,
        'followUpQuestions': follow_ups,
        'tangentialQuestions': tangents,
        'headerText': new_message['text']
    }


def process_follow_up_selection(data, gpt_instance: GPTInstance, message_store: MessageStore):
    """
    Handles the 'selected-question' event when user selects a follow-up.

    Args:
        data: dict with keys 'sessionId', 'selectedQuestion', 'idx', 'page'
    """
    session_id = data['sessionId']
    selected_question = data['selectedQuestion']

    prev_selected = message_store.get_selected_questions(session_id)
    if selected_question in prev_selected:
        response = message_store.get_selected_question_response(session_id, selected_question)
    else:
        response = gpt_instance.get_tangential_output(selected_question)
        message_store.add_selected_question_and_response(session_id, selected_question, response)

    return {
        'response': response,
        'idx': data['idx'],
        'page': data['page']
    }
