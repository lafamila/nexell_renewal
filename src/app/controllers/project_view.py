from flask import Blueprint, render_template, request, session, redirect
from ..helpers import session_helper
bp = Blueprint('project', __name__, url_prefix='/project')

@bp.route('/')
@session_helper.session_check
def index_page():
    return render_template('project.html')

@bp.route('/report/NR')
@session_helper.session_check
def report_NR():
    s_cntrct_sn = request.args.get("s_cntrct_sn")
    s_prjct_sn = request.args.get("s_prjct_sn")
    params = request.args.to_dict()
    return render_template('project_NR.html', title="프로젝트 보고서", params=params)

@bp.route('/report/BD')
@session_helper.session_check
def report_BD():
    s_cntrct_sn = request.args.get("s_cntrct_sn")
    s_prjct_sn = request.args.get("s_prjct_sn")
    params = request.args.to_dict()
    return render_template('project_BD.html', title="프로젝트 보고서", params=params)

@bp.route('/report/BF')
@session_helper.session_check
def report_BF():
    s_cntrct_sn = request.args.get("s_cntrct_sn")
    s_prjct_sn = request.args.get("s_prjct_sn")
    params = request.args.to_dict()
    return render_template('project_BF.html', title="프로젝트 보고서", params=params)