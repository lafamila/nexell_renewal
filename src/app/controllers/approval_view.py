from flask import Blueprint, render_template, session, redirect, request
from ..helpers import session_helper
from .api.services import refresh_code_list, get_member_list_by_sn, get_approval_by_sn
bp = Blueprint('approval', __name__, url_prefix='/approval')

@bp.route('/')
@session_helper.session_check
def index_page():
    return render_template('approval.html', title="전자결재 | 넥셀시스템", **refresh_code_list())

@bp.route('/report')
@session_helper.session_check
def report_page():
    params = request.args.to_dict()
    if "approval_ty_code" in params:
        approval = get_approval_by_sn(params)
        init = True
    elif "approval_sn" in params:
        init = False
        #approval 정보 가져오기 (approval_sn 으로 approval_ty_code 알아내서)
        approval = None
    return render_template("approval_report.html", title="전자결재 | 넥셀시스템", init=init, approval=approval, member_list_by_sn=get_member_list_by_sn(), **refresh_code_list())