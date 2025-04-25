import re
import logging
from langchain_community.vectorstores.neo4j_vector import remove_lucene_chars

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def generate_full_text_query(input: str) -> str:
    """
    Generate a Neo4j-compatible fuzzy full-text search query.

    Args:
        input (str): The string to turn into a Lucene fuzzy query

    Returns:
        str: Full-text fuzzy search query string
    """
    logger.info("[Helpers] Generating full text query for input: %s", input)
    cleaned = remove_lucene_chars(input)
    words = [word for word in cleaned.split() if word]
    if not words:
        logger.warning("[Helpers] No valid words found after cleaning input")
        return ""

    query_parts = [f"{word}~2" for word in words]
    result = " AND ".join(query_parts)
    logger.info("[Helpers] Final generated query: %s", result)
    return result