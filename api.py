from flask import Blueprint, jsonify, request
from gemini import query_llm
import datetime
import json
import os

gen_ai_bp = Blueprint('gen_ai', __name__)

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


@gen_ai_bp.route('/api/ask_llm', methods=['POST'])
def ask_llm():
    try:
        data = request.get_json()
        if not data or "question" not in data:
            return jsonify({"status": "error", "message": "Question is required in request body"}), 400
        question = data["question"]
        answer = query_llm(question)
        if not answer:
            res_data = {"question": question, "answer": "", "status": "Fail", "ts": str(datetime.datetime.now()),
                        "user_id": 1}
            add_data = append_to_json(res_data, filepath=chat_db_file_path)
            if not add_data:
                print(f"Unable to add data in file.")
            return jsonify({"status": "error", "message": "Could not generate answer."}), 400

        res_data = {"question": question, "answer": answer, "status": "Pass", "ts": str(datetime.datetime.now()),
                    "user_id": 1}
        add_data = append_to_json(res_data, filepath=chat_db_file_path)
        if not add_data:
            print(f"Unable to add data in file.")
        return jsonify({"status": "success", "answer": answer}), 200
    except Exception as ex:
        print(f"Exception occurred in ask_llm, ex: {ex}")
        return jsonify({"status": "error", "message": "Internal server error"}), 500


@gen_ai_bp.route('/api/get_chat', methods=['GET'])
def get_chat():
    try:
        number_of_rec = 10
        # Check if file exists
        if not os.path.exists(chat_db_file_path):
            return jsonify({"status": "error", "message": "Db file not found"}), 404
        # Check if file is not empty
        with open(chat_db_file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        sorted_data = sorted(data, key=lambda x: x.get("ts", ""), reverse=True)
        data = sorted_data[:number_of_rec]
        return jsonify({"data": data}), 200
    except Exception as ex:
        print(f"Exception occurred in ask_llm, ex: {ex}")
        return jsonify({"status": "error", "message": "Internal server error"}), 500


@gen_ai_bp.route('/api/sign_up', methods=['POST'])
def sign_up():
    try:
        data = request.get_json()
        if not data or "email" not in data or "name" not in data or "password" not in data:
            return jsonify({"status": "error", "message": "Invalid data or argument."}), 400
        email = data["email"]
        name = data["name"]
        password = data["password"]
        all_users = get_user()
        all_user_id = []
        for user in all_users:
            if user['email'] == email:
                return jsonify({"status": "error", "message": f"User with email: {email} already exist."}), 422
            all_user_id.append(user['user_id'])
        next_user_id = max(all_user_id) + 1 if all_user_id else 1
        user_data = {"email": email, "name": name, "password": password, "user_id": next_user_id,
                     "sign_up_ts": str(datetime.datetime.now())}
        add_data = append_to_json(user_data, filepath=user_db_file_path)
        if not add_data:
            return jsonify({"status": "error", "message": f"Unable to add User with email: {email}."}), 422
        return jsonify({"status": "Success", "message": f"User with email: {email} added as user id:"
                                                        f" {next_user_id}"}), 200
    except Exception as ex:
        print(f"Exception occurred in adding user, ex: {ex}")
        return jsonify({"status": "error", "message": "Internal server error"}), 500


@gen_ai_bp.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        if not data or "email" not in data or "password" not in data:
            return jsonify({"status": "error", "message": "Invalid data or argument."}), 400
        email = data["email"]
        password = data["password"]
        all_users = get_user()

        temp_user = None
        for user in all_users:
            if user['email'] == email:
                temp_user = user
                break

        if not temp_user:
            return jsonify({"status": "error", "message": f"Invalid email: {email}, plz sign up."}), 400

        if temp_user['password'] != password:
            return jsonify({"status": "error", "message": f"Invalid password for"
                                                          f" user id: {temp_user['user_id']}."}), 400

        login_res = {"is_login": True, "user_id": temp_user['user_id'], "ts": datetime.datetime.now()}
        return jsonify({"status": "Success", "message": f"User with email: {email} logged in successfully:",
                        'data': login_res}), 200
    except Exception as ex:
        print(f"Exception occurred in adding user, ex: {ex}")
        return jsonify({"status": "error", "message": "Internal server error"}), 500
