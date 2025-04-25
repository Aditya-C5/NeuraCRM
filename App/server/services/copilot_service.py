# App/server/services/copilot_service.py
"""
def run_copilot_query(data, action_agent_instance):
    
    Handles the copilot-query event.

    Args:
        data (dict): Expects 'query' key
        action_agent_instance: An instance of ActionAgent

    Returns:
        dict or str: Result or error message
    
    try:
        result = action_agent_instance.run_agent(data["query"])
        return result
    except Exception as e:
        return "Sorry, there seems to be an error. Please try again or contact the developers!"
"""
import logging
logger = logging.getLogger(__name__)

def run_copilot_query(data, action_agent_instance):
    try:
        query = data.get("query")
        session_id = data.get("sessionId")
        if not query:
            return {"error": "Missing 'query' in request"}
        
        result = action_agent_instance.run_agent(query, session_id=session_id)
        return result
    except Exception as e:
        logger.exception("Copilot query failed:")
        return {"error": "Internal server error. Please contact support."}
