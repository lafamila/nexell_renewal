from flask import Blueprint, render_template, session, redirect
from ..helpers import session_helper
bp = Blueprint('index', __name__, url_prefix='/')

@bp.route('/', methods=['GET'])
@session_helper.session_check
def index_page():
    # return redirect('/login')
    return render_template("index.html", title="홈 | 넥셀시스템")

@bp.route('/login', methods=['GET'])
@session_helper.session_clear
def login_page():
    return render_template("login.html")


@bp.route('/html/printNew.html', methods=['GET'])
def printNew():
    return render_template("common/printNew.html")

@bp.route('/dev_test', methods=['GET'])
@session_helper.session_check
def dev_test():
    return render_template("dev_test.html")

@bp.route('/dev_test2', methods=['GET'])
@session_helper.session_check
def dev_test2():
    return render_template("dev_test2.html")
