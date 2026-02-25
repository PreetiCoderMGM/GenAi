from flask import Blueprint, jsonify, request
from gemini import query_llm

gen_ai_bp = Blueprint('gen_ai', __name__)


@gen_ai_bp.route('/ask_llm', methods=['POST'])
def ask_llm():
    try:
        data = request.get_json()

        if not data or "question" not in data:
            return jsonify({"status": "error", "message": "Question is required in request body"}), 400

        question = data["question"]
        answer = query_llm(question)
        if not answer:
            return jsonify({"status": "error", "message": "Could not generate answer."}), 400
        return jsonify({"status": "success", "answer": answer}), 200
    except Exception as ex:
        print(f"Exception occurred in ask_llm, ex: {ex}")
        return jsonify({"status": "error", "message": "Internal server error"}), 500
