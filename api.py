from flask import Blueprint, jsonify, request
from gemini import query_llm, file_summary
import datetime
import json
import os
from bl import get_user, append_to_json, get_files_db
from setting import user_db_file_path, chat_db_file_path
import setting
from utils import get_guid

api_bp = Blueprint('api_bp', __name__)


@api_bp.route('/api/ask_llm/<user_id>', methods=['POST'])
def ask_llm(user_id):
    try:
        user_id = int(user_id)
        file_id = int(request.args.get("file_id")) if request.args.get("file_id") else None
        data = request.get_json()
        if not data or "question" not in data:
            return jsonify({"status": "error", "message": "Question is required in request body"}), 400

        all_files = get_files_db()
        file = None
        for f in all_files:
            if f['file_id'] == file_id:
                file = f
                break
        if not file:
            return jsonify({"status": "error", "message": f"Invalid file id: {file_id}"}), 404
        if file['user_id'] != user_id:
            return jsonify({"status": "error", "message": f"Invalid file id: {file_id} for user: {user_id}"}), 404

        question = data["question"]
        answer = file_summary(file['file_path'], question)
        if not answer:
            res_data = {"question": question, "answer": "", "status": "Fail", "ts": str(datetime.datetime.now()),
                        "user_id": 1}
            add_data = append_to_json(res_data, filepath=chat_db_file_path)
            if not add_data:
                print(f"Unable to add data in file.")
            return jsonify({"status": "error", "message": "Could not generate answer."}), 400

        res_data = {"question": question, "answer": answer, "status": "Pass", "ts": str(datetime.datetime.now()),
                    "user_id": 1, "file_id": file_id}
        add_data = append_to_json(res_data, filepath=chat_db_file_path)
        if not add_data:
            print(f"Unable to add data in file.")
        return jsonify({"status": "success", "answer": answer}), 200
    except Exception as ex:
        print(f"Exception occurred in ask_llm, ex: {ex}")
        return jsonify({"status": "error", "message": "Internal server error"}), 500


@api_bp.route('/api/get_chat/<user_id>', methods=['GET'])
def get_chat(user_id: int):
    try:
        file_id = int(request.args.get("file_id")) if request.args.get("file_id") else None
        user_id = int(user_id)
        number_of_rec = 10
        # Check if file exists
        if not os.path.exists(chat_db_file_path):
            return jsonify({"status": "error", "message": "Db file not found"}), 404
        all_files = get_files_db()
        file = None
        for f in all_files:
            if f['file_id'] == file_id:
                file = f
                break
        if not file:
            return jsonify({"status": "error", "message": f"Invalid file id: {file_id}"}), 404
        if file['user_id'] != user_id:
            return jsonify({"status": "error", "message": f"Invalid file id: {file_id} for user: {user_id}"}), 404

        # Check if file is not empty
        with open(chat_db_file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        user_data = []
        for d in data:
            if d['user_id'] == user_id and d['file_id'] == file_id:
                user_data.append(d)
        sorted_data = sorted(user_data, key=lambda x: x.get("ts", ""), reverse=True)
        data = sorted_data[:number_of_rec]
        return jsonify({"data": data}), 200
    except Exception as ex:
        print(f"Exception occurred while getting chat, ex: {ex}")
        return jsonify({"status": "error", "message": "Internal server error"}), 500


@api_bp.route('/api/sign_up', methods=['POST'])
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


@api_bp.route('/api/login', methods=['POST'])
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


@api_bp.route('/api/add_file/<user_id>', methods=['POST'])
def add_file(user_id):
    try:
        user_id = int(user_id)
        if 'file' not in request.files:
            return jsonify({"status": "error", "message": "No file part in request"}), 400

        file = request.files['file']

        # Check if file is selected
        if file.filename == '':
            return jsonify({"status": "error", "message": "No file selected"}), 400

        file_ext = file.filename.split(".")[-1]
        if file_ext not in ['txt', "json", "csv"]:
            return jsonify({"status": "error", "message": "Unsupported file format."}), 400

        # Save file
        save_file_name = f"{get_guid()}_{file.filename}"
        file_path = os.path.join(setting.DataFolderPath, save_file_name)
        file.save(file_path)
        all_files = get_files_db()
        next_file_id = max([i['file_id'] for i in all_files]) + 1 if all_files else 1
        file_meta_data = {"display_file_name": file.filename, "user_id": user_id,
                          "upload_ts": str(datetime.datetime.now()),
                          "file_path": file_path, "file_id": next_file_id}
        add_data = append_to_json(file_meta_data, filepath=setting.files_db_file_path)
        if not add_data:
            return jsonify({"status": "error", "message": f"Unable to add file: {file.filename}."}), 422

        return jsonify({"status": "Success", "message": "File uploaded successfully",
                        "file_name": file.filename, "file_path": file_path}), 200
    except Exception as ex:
        print(f"Exception occurred in adding user, ex: {ex}")
        return jsonify({"status": "error", "message": "Internal server error"}), 500


@api_bp.route('/api/get_files/<user_id>', methods=['GET'])
def get_files(user_id: int):
    try:
        user_id = int(user_id)
        number_of_rec = 10
        # Check if file exists
        if not os.path.exists(setting.files_db_file_path):
            return jsonify({"status": "error", "message": "Db file not found"}), 404
        # Check if file is not empty
        with open(setting.files_db_file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        file_data = []
        for d in data:
            if d['user_id'] == user_id:
                file_data.append(d)
        sorted_data = sorted(file_data, key=lambda x: x.get("upload_ts", ""), reverse=True)
        data = sorted_data[:number_of_rec]
        return jsonify({"data": data}), 200
    except Exception as ex:
        print(f"Exception occurred while getting files, ex: {ex}")
        return jsonify({"status": "error", "message": "Internal server error"}), 500
