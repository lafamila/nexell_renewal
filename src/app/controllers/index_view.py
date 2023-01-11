from flask import Blueprint, render_template, session, redirect
from ..helpers import session_helper
bp = Blueprint('index', __name__, url_prefix='/')

@bp.route('/', methods=['GET'])
@session_helper.session_check
def index_page():
    # return redirect('/login')
    print(session.keys())
    return render_template("index2.html")

@bp.route('/login', methods=['GET'])
@session_helper.session_clear
def login_page():
    return render_template("login.html")
