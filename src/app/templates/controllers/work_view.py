from flask import Blueprint, render_template, make_response, session, redirect
from ..helpers import session_helper
from .api.services import refresh_code_list

bp = Blueprint('work', __name__, url_prefix='/work')

@bp.route('/')
@session_helper.session_check
def index_page():
    return render_template('work.html', title="근태현황관리 | 넥셀시스템", **refresh_code_list())


@bp.route('/year')
@session_helper.session_check
def year_page():
    return render_template('work_year.html', title="연차현황 | 넥셀시스템", **refresh_code_list())

@bp.route('/personal')
@session_helper.session_check
def personal_page():
    return render_template('work_personal.html', title="개인근태현황 | 넥셀시스템", **refresh_code_list())

@bp.route('/daily')
@session_helper.session_check
def daily_page():
    return render_template('work_daily.html', title="일일근태현황 | 넥셀시스템", **refresh_code_list())