from flask import Blueprint, render_template, make_response, session, redirect
from ..helpers import session_helper
from .api.services import refresh_code_list

bp = Blueprint('completed', __name__, url_prefix='/completed')

# @bp.route('/')
# @session_helper.session_check
# def index_page():
#     return render_template("completed_new.html", title="기성현황 | 넥셀시스템", **refresh_code_list())

@bp.route('/')
@session_helper.session_check
def index_renewal_page():
    return render_template("completed_new_new.html", title="기성현황 | 넥셀시스템", **refresh_code_list())

@bp.route('/report')
@session_helper.session_check
def report_page():
    return render_template("completed_report_new.html", title="기성현황 집계표(공조) | 넥셀시스템", **refresh_code_list())

@bp.route('/report/old')
@session_helper.session_check
def report_renewal_page():
    return render_template("completed_report.html", title="기성현황 집계표(공조) | 넥셀시스템", **refresh_code_list())

