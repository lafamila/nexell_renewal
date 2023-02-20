from flask import Blueprint, render_template, make_response, session, redirect
from ..helpers import session_helper
bp = Blueprint('work', __name__, url_prefix='/work')

@bp.route('/')
@session_helper.session_check
def index_page():
    return render_template('work.html')


@bp.route('/year')
@session_helper.session_check
def year_page():
    return render_template('work_year.html')

@bp.route('/personal')
@session_helper.session_check
def personal_page():
    return render_template('work_personal.html')

@bp.route('/daily')
@session_helper.session_check
def daily_page():
    return render_template('work_daily.html')