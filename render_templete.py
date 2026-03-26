from flask import render_template, Blueprint

auth_bp = Blueprint('auth_bp', __name__)


@auth_bp.route("/login")
def login_page():
    return render_template("login.html")


@auth_bp.route("/sign_up")
def sign_up_page():
    return render_template("sign_up.html")
