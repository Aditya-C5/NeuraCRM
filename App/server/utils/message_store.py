import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MessageStore:
    """
    Class to store and manage chat messages and associated data.
    """

    def __init__(self):
        logger.info("[MessageStore] Initializing store")
        self.messages = {}
        self.ai_messages = {}
        self.follow_up_questions = {}
        self.selected_questions_responses = {}

    def add_message(self, formatted_message):
        try:
            session_id = formatted_message['sessionId']
            text = formatted_message['text']
            logger.info("[MessageStore] Adding message to session %s: %s", session_id, text)
            self.messages.setdefault(session_id, []).append(text)
        except Exception as e:
            logger.error("[MessageStore] Failed to add message: %s", e)

    def get_messages(self, session_id):
        logger.info("[MessageStore] Retrieving messages for session %s", session_id)
        return self.messages.get(session_id, [])

    def clear_messages(self):
        logger.info("[MessageStore] Clearing all stored messages")
        self.messages = {}
        self.ai_messages = {}

    def add_ai_message(self, data):
        try:
            session_id = data['sessionId']
            ai_message = data['aiMessage']
            logger.info("[MessageStore] Adding AI message to session %s", session_id)
            self.ai_messages.setdefault(session_id, []).append(ai_message)
        except Exception as e:
            logger.error("[MessageStore] Failed to add AI message: %s", e)

    def get_ai_messages(self, session_id):
        logger.info("[MessageStore] Retrieving AI messages for session %s", session_id)
        return self.ai_messages.get(session_id, [])

    def add_follow_up_questions(self, data):
        try:
            session_id = data['sessionId']
            questions = data['followUpQuestions']
            logger.info("[MessageStore] Adding follow-up questions to session %s", session_id)
            self.follow_up_questions.setdefault(session_id, []).append(questions)
        except Exception as e:
            logger.error("[MessageStore] Failed to add follow-up questions: %s", e)

    def get_follow_up_questions(self, session_id):
        logger.info("[MessageStore] Retrieving follow-up questions for session %s", session_id)
        return self.follow_up_questions.get(session_id, [])

    def add_selected_question_and_response(self, session_id, selected_question, response):
        try:
            logger.info("[MessageStore] Storing selected question response for session %s: %s", session_id, selected_question)
            self.selected_questions_responses.setdefault(session_id, {})[selected_question] = response
        except Exception as e:
            logger.error("[MessageStore] Failed to store selected question and response: %s", e)

    def get_selected_questions(self, session_id):
        logger.info("[MessageStore] Retrieving selected questions for session %s", session_id)
        return list(self.selected_questions_responses.get(session_id, {}).keys())

    def get_selected_question_response(self, session_id, selected_question):
        logger.info("[MessageStore] Retrieving response for selected question in session %s: %s", session_id, selected_question)
        return self.selected_questions_responses.get(session_id, {}).get(selected_question)
