from flask import Blueprint, render_template, session, redirect, request
from ..helpers import session_helper
from .api.services import refresh_code_list, get_member_list_by_sn, get_approval_by_sn, get_approval_ty_code_by_sn
import json
bp = Blueprint('approval', __name__, url_prefix='/approval')

@bp.route('/')
@session_helper.session_check
def index_page():
    _type = request.args.get("type")
    return render_template('approval.html', title="전자결재 | 넥셀시스템", **refresh_code_list(), _type=_type if _type is not None else "")

@bp.route('/report')
@session_helper.session_check
def report_page():
    params = request.args.to_dict()
    if "approval_ty_code" in params:
        approval = get_approval_by_sn(params)
        approval_sn = None
        init = "init"
    elif "approval_sn" in params:
        approval_sn = params["approval_sn"]
        approval_data = get_approval_ty_code_by_sn(params)
        approval = get_approval_by_sn(approval_data)
        init = "show"
    return render_template("approval_report.html", title="전자결재 | 넥셀시스템", init=init, approval=approval, approval_sn=approval_sn, loginSN=session['member']['member_sn'], member_list_by_sn=get_member_list_by_sn(), **refresh_code_list())

@bp.route('/copy')
@session_helper.session_check
def report_copy_page():
    params = request.args.to_dict()
    approval_sn = params["approval_sn"]
    approval_data = get_approval_ty_code_by_sn(params)
    approval_data['approval_data'] = json.loads(approval_data['approval_data'])
    approval = get_approval_by_sn(approval_data)
    return render_template("approval_report_copy.html", title="전자결재 | 넥셀시스템", approval=approval, approval_data=approval_data, loginSN=session['member']['member_sn'], member_list_by_sn=get_member_list_by_sn(), **refresh_code_list())