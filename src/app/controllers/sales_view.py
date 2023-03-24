from flask import Blueprint, render_template, session, redirect
from ..helpers import session_helper
bp = Blueprint('sales', __name__, url_prefix='/sales')

@bp.route('/')
@session_helper.session_check
def index_page():
    return render_template('sales.html', title="매입/매출 관리 | 넥셀시스템")

@bp.route('/report')
@session_helper.session_check
def report_page():
    return render_template('sales_report.html', title="외상채권 | 넥셀시스템")

@bp.route('/approval')
@session_helper.session_check
def sales_approval_page():
    return render_template("sales_approval.html", title="주문현황 | 넥셀시스템")