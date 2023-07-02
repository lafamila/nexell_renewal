from flask import Blueprint, render_template, session, redirect, request
from ..helpers import session_helper
from .api.services import refresh_code_list

bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

@bp.route('/')
@session_helper.session_check
def index_page():
    return render_template('dashboard.html', title="대시보드 | 넥셀시스템", **refresh_code_list())

@bp.route('/logitech')
@session_helper.session_check
def logitech_page():
    cntrct_sn = request.args.get("cntrct_sn")
    return render_template('dashboard_logitech.html', cntrct_sn=cntrct_sn, title="일별 지급자재 매입현황 | 넥셀시스템", **refresh_code_list())

