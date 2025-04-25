import os
import json
import logging
from typing import List, Optional
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

BASE_DIR = os.path.dirname(os.path.dirname(__file__))  # Points to 'app/server'


class ActionsList:
    def __init__(self, actions_list: list):
        logger.info("[ActionsList] Initializing with %d actions", len(actions_list))
        self.actions_list = actions_list

    def set_list(self, actions_list: list):
        logger.info("[ActionsList] Setting new list with %d actions", len(actions_list))
        self.actions_list = actions_list

    def get_list(self) -> list:
        try:
            path = os.path.join(BASE_DIR, "text_db", "actions.txt")
            logger.info("[ActionsList] Loading actions list from: %s", path)
            with open(path, "r") as f:
                data = json.load(f)
                logger.info("[ActionsList] Successfully loaded %d actions", len(data))
                return data
        except Exception as e:
            logger.error("[ActionsList] Failed to load actions list: %s", e)
            return []


class DatabaseList:
    def __init__(self, database_list: list):
        logger.info("[DatabaseList] Initializing with %d databases", len(database_list))
        self.database_list = database_list

    def set_list(self, database_list: list):
        logger.info("[DatabaseList] Setting new list with %d databases", len(database_list))
        self.database_list = database_list

    def get_list(self) -> list:
        try:
            path = os.path.join(BASE_DIR, "text_db", "db.txt")
            logger.info("[DatabaseList] Loading database list from: %s", path)
            with open(path, "r") as f:
                data = json.load(f)

            for db in data:
                # Resolve relative path to absolute
                rel_path = db.get("database_path") or db.get("db_path")
                if rel_path:
                    abs_path = os.path.abspath(os.path.join(BASE_DIR, rel_path.lstrip("./\\")))
                    db["db_path"] = abs_path
                    logger.debug("[DatabaseList] Resolved path → db_path: %s", abs_path)

                    if not os.path.exists(abs_path):
                        logger.warning("[DatabaseList] WARNING: File does not exist at: %s", abs_path)
                else:
                    logger.warning("[DatabaseList] No valid path key ('database_path' or 'db_path') found in entry: %s", db)

            logger.info("[DatabaseList] Successfully loaded %d databases", len(data))
            return data
        except Exception as e:
            logger.error("[DatabaseList] Failed to load database list: %s", e)
            return []



class Entities(BaseModel):
    names: Optional[List[str]] = Field(
        ...,
        description="All the object, event entities that appear in the text"
    )
