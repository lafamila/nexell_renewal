from flask import Blueprint, render_template, redirect
from ..helpers import session_helper
bp = Blueprint('index', __name__, url_prefix='/')


@bp.route('/', methods=['GET'])
def index_page():
    return redirect('/login')
    # return render_template("index.html")

@session_helper.session_clear
@bp.route('/login', methods=['GET'])
def login_page():
    return render_template("login.html")
