import os
import json
import csv
from datetime import date
from werkzeug.datastructures import FileStorage
from ..utils.data_models import DatabaseList


DB_FILE = "./text_db/db.txt"

def post_database(database_list: DatabaseList, database_file: FileStorage, form_data: dict) -> tuple:
    try:
        with open(DB_FILE, "r") as f:
            db_data = json.load(f)
    except json.JSONDecodeError:
        db_data = []

    filename = database_file.filename
    if not filename.endswith('.csv'):
        return {"error": "Invalid file format. Only CSV supported."}, 400

    # Define consistent, safe CSV folder path relative to App/server
    csv_folder = os.path.join(os.path.dirname(__file__), "../csv_db")
    os.makedirs(csv_folder, exist_ok=True)

    # Save path for this uploaded file
    save_path = os.path.join(csv_folder, filename)
    database_file.save(save_path)

    # Extract CSV headers
    with open(save_path, 'r') as csv_file:
        reader = csv.reader(csv_file)
        headers = next(reader)

    # Save only relative path (portable)
    rel_path = os.path.relpath(save_path, start=os.getcwd())

    new_entry = {
        "database_name": form_data.get("database_name"),
        "database_description": form_data.get("database_description"),
        "columns": ", ".join(headers),
        "database_path": rel_path,
        "date": date.today().strftime("%d-%m-%Y")
    }

    db_data.append(new_entry)

    with open(DB_FILE, "w") as f:
        json.dump(db_data, f, indent=4)
        database_list.set_list(db_data)

    return json.dumps(db_data, indent=4), 200
