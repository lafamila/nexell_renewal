from flask import Blueprint, render_template, session, redirect
from ..helpers import session_helper
from .api.services import refresh_code_list

bp = Blueprint('index', __name__, url_prefix='/')

@bp.route('/', methods=['GET'])
@session_helper.session_check
def index_page():
    # return redirect('/login')
    return render_template("index.html", title="홈 | 넥셀시스템", **refresh_code_list())

@bp.route('/login', methods=['GET'])
@session_helper.session_clear
def login_page():
    return render_template("login.html", title="로그인 | 넥셀시스템", **refresh_code_list())


@bp.route('/html/printNew.html', methods=['GET'])
def printNew():
    return render_template("common/printNew.html", title="출력 | 넥셀시스템", **refresh_code_list())

@bp.route('/dev_test', methods=['GET'])
@session_helper.session_check
def dev_test():
    return render_template("dev_test.html", **refresh_code_list())

@bp.route('/dev_test2', methods=['GET'])
@session_helper.session_check
def dev_test2():
    return render_template("dev_test2.html", **refresh_code_list())

@bp.route('/index/almost', methods=['GET'])
@session_helper.session_check
def index_almost():
    return render_template("index_project_almost.html", title="팝업 | 넥셀시스템", **refresh_code_list())

@bp.route('/index/bnd', methods=['GET'])
@session_helper.session_check
def bnd():
    return render_template("index_project_bnd.html", title="팝업 | 넥셀시스템", **refresh_code_list())

