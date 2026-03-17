from flask import Blueprint, jsonify, request
from gemini import query_llm
import datetime
import json
import os

gen_ai_bp = Blueprint('gen_ai', __name__)

chat_db_file_path = os.path.join(os.getcwd(), "DB", "chat.json")


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


@gen_ai_bp.route('/ask_llm', methods=['POST'])
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
            add_data = append_to_json(res_data)
            if not add_data:
                print(f"Unable to add data in file.")
            return jsonify({"status": "error", "message": "Could not generate answer."}), 400

        res_data = {"question": question, "answer": answer, "status": "Pass", "ts": str(datetime.datetime.now()),
                    "user_id": 1}
        add_data = append_to_json(res_data)
        if not add_data:
            print(f"Unable to add data in file.")
        return jsonify({"status": "success", "answer": answer}), 200
    except Exception as ex:
        print(f"Exception occurred in ask_llm, ex: {ex}")
        return jsonify({"status": "error", "message": "Internal server error"}), 500


@gen_ai_bp.route('/get_chat', methods=['GET'])
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
