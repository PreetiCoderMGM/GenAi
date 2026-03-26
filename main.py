from flask import Flask

from GenAi.render_templete import auth_bp
from api import gen_ai_bp
from flask_cors import CORS


def create_app():
    app = Flask(__name__)
    CORS(app, resources={r"/*": {"origins": "*"}})
    app.register_blueprint(gen_ai_bp)
    app.register_blueprint(auth_bp)
    return app


if __name__ == "__main__":
    flask_app = create_app()
    flask_app.run(debug=True, port=5002)
