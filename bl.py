import json
import os


chat_db_file_path = os.path.join(os.getcwd(), "DB", "chat.json")
user_db_file_path = os.path.join(os.getcwd(), "DB", "user.json")


def get_user(filepath=user_db_file_path):
    try:
        with open(filepath, "r") as f:
            data = json.load(f)
        if not isinstance(data, list):
            data = []
        return data
    except Exception as ex:
        print(ex)
        print(f"Unable to get users ex: {ex}")
        return []


def append_to_json(new_data, filepath=chat_db_file_path):
    try:
        data = []
        # Create file if it does not exist
        if not os.path.exists(filepath):
            with open(filepath, "w") as f:
                json.dump([], f)
        # Read existing data safely
        if os.path.getsize(filepath) > 0:
            try:
                with open(filepath, "r") as f:
                    data = json.load(f)
                # Ensure it's a list
                if not isinstance(data, list):
                    data = []
            except json.JSONDecodeError:
                data = []
        # Append new record
        data.append(new_data)
        # Write updated data
        with open(filepath, "w") as f:
            json.dump(data, f, indent=4)
        return True
    except Exception as ex:
        print(f"Could not add data: {new_data} in filepath: {filepath}, ex: {ex}")
        return False
