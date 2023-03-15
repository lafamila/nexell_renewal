from flask import Blueprint, render_template, session, redirect
from ..helpers import session_helper
bp = Blueprint('sales', __name__, url_prefix='/sales')

@bp.route('/')
@session_helper.session_check
def index_page():
    return render_template('sales.html')

@bp.route('/report')
@session_helper.session_check
def report_page():
    return render_template('sales_report.html')

@bp.route('/approval')
@session_helper.session_check
def sales_approval_page():
    return render_template("sales_approval.html")