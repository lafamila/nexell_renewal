from flask import Blueprint, render_template, make_response, session, redirect
from ..helpers import session_helper
bp = Blueprint('fund', __name__, url_prefix='/fund')

@bp.route('/')
@session_helper.session_check
def index_page():
    return render_template('fund.html')

@bp.route('/stat')
@session_helper.session_check
def stat_page():
    return render_template('fund_stat.html')