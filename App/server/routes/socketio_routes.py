
from flask_socketio import emit
#from ..main import socketio, gpt_instance, message_store, action_agent_instance
from ..services import gpt_service, copilot_service, action_service
from ..utils.data_models import ActionsList

"""
actions_instance = ActionsList([])  # TEMP — replace with injected shared instance later


@socketio.on('data')
def handle_data(data):
    result = gpt_service.process_transcribed_message(data, gpt_instance, action_agent_instance, message_store)
    if not result.get("skip"):
        emit('should-generate-message', 1)
        emit('ai-response', {'aiMessage': result['aiMessage']})
        emit('follow-up-questions', {
            'headerText': result['headerText'],
            'followUpQuestions': result['followUpQuestions']
        })
        emit('tangential-questions', {
            'sessionId': data['sessionId'],
            'headerText': result['headerText'],
            'tangentialQuestions': result['tangentialQuestions']
        })


@socketio.on('selected-question')
def handle_selected_question(data):
    result = gpt_service.process_follow_up_selection(data, gpt_instance, message_store)
    emit('tangential-questions-response', result)


@socketio.on('copilot-query')
def handle_copilot_query(data):
    result = copilot_service.run_copilot_query(data, action_agent_instance)
    emit('copilot-output', result)

@socketio.on("action-item-check")
def handle_action_item_check(data):
    
    Handle 'action-item-check' event from frontend.
    This ensures frontend listener gets a response and doesn't hang.
    

    # add custom validation logic here
    result = {
        "status": "received",
        "valid": True,
        "echo": data  # Echo the data back for now
    }

    emit("action-item-check", result)

@socketio.on("connect")
def handle_connect():
    emit("connected", {"data": "connected"})

@socketio.on('extract')
def handle_extract(data):
    
    Triggered when frontend ends transcription and requests action item extraction.
    
    extracted_items = action_service.extract_action_items(data)
    emit('action-item-check', extracted_items)


@socketio.on('create-action-item')
def handle_create_action_item(data):
    
    Triggered when frontend confirms an action item.
    
    result = action_service.create_action_item_from_data(data)
    emit('action-item-created', result)  # OPTIONAL: update to match frontend expectation


@socketio.on('api-call')
def handle_api_call(data):
    
    Handles dynamic API calls like Jira, Gmail, or custom endpoints.
    
    result = action_service.handle_dynamic_api_call(data, actions_instance)
    emit('api-response', result)
"""
def register_socketio_handlers(socketio, gpt_instance, action_agent_instance, message_store, actions_instance):

    from ..services import gpt_service, copilot_service, action_service

    @socketio.on('data')
    def handle_data(data):
        result = gpt_service.process_transcribed_message(data, gpt_instance, action_agent_instance, message_store)
        if not result.get("skip"):
            emit('should-generate-message', 1)
            emit('ai-response', {'aiMessage': result['aiMessage']})
            emit('follow-up-questions', {
                'headerText': result['headerText'],
                'followUpQuestions': result['followUpQuestions']
            })
            emit('tangential-questions', {
                'sessionId': data['sessionId'],
                'headerText': result['headerText'],
                'tangentialQuestions': result['tangentialQuestions']
            })

    @socketio.on('selected-question')
    def handle_selected_question(data):
        result = gpt_service.process_follow_up_selection(data, gpt_instance, message_store)
        emit('tangential-questions-response', result)

    @socketio.on('copilot-query')
    def handle_copilot_query(data):
        result = copilot_service.run_copilot_query(data, action_agent_instance)
        emit('copilot-output', result)

    @socketio.on('extract')
    def handle_extract(data):
        extracted_items = action_service.extract_action_items(data)
        emit('action-item-check', extracted_items)

    @socketio.on('create-action-item')
    def handle_create_action_item(data):
        result = action_service.create_action_item_from_data(data)
        emit('action-item-created', result)

    @socketio.on('api-call')
    def handle_api_call(data):
        result = action_service.handle_dynamic_api_call(data, actions_instance)
        emit('api-response', result)

    @socketio.on("action-item-check")
    def handle_action_item_check(data):
        emit("action-item-check", {
            "status": "received",
            "valid": True,
            "echo": data
        })

    @socketio.on("connect")
    def handle_connect():
        emit("connected", {"data": "connected"})