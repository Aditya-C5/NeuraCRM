# App/server/services/jira_service.py

def extract_action_item(data):
    """
    Mock extractor for Jira-style action items from input data.
    Replace with actual NLP logic or Jira analysis.
    """
    class ActionItem:
        def __init__(self, summary, description):
            self.summary = summary
            self.description = description

    # For now, return fake data for structure testing
    return [
        ActionItem("Follow up with client", "Check in with client by Monday."),
        ActionItem("Prepare proposal", "Create a proposal for Project X.")
    ]


def create_action_item(data):
    """
    Stub for creating a Jira action item (custom or API-based).
    """
    print(f"[Mock] Creating action item with data: {data}")


def create_issue(endpoint, title, description, auth):
    """
    Stub for hitting Jira's REST API — can be extended.
    """
    print(f"[Mock] Calling Jira API at {endpoint} with:")
    print(f"Title: {title}\nDescription: {description}\nAuth: {auth}")
    return {"status": "mocked"}
