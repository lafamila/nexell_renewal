from flask import Blueprint, render_template, make_response, session, redirect, request
from ..helpers import session_helper
from .api.services import refresh_code_list

bp = Blueprint('bbs', __name__, url_prefix='/bbs')

@bp.route('/')
@session_helper.session_check
def index_page():
    return render_template('bbs.html', title="공지사항관리 | 넥셀시스템", **refresh_code_list())

@bp.route('/report')
@session_helper.session_check
def report_page():
    bbs_sn = request.args.get("bbs_sn")
    if bbs_sn is None:
        _type = "new"
    else:
        _type = "show"
    return render_template('bbs_report.html', bbs_sn=bbs_sn, _type=_type, title="공지사항 | 넥셀시스템", **refresh_code_list())