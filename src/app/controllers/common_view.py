from flask import Blueprint, render_template, session, redirect
from ..helpers import session_helper
bp = Blueprint('common', __name__, url_prefix='/')

@bp.route('/work')
@session_helper.session_check
def work_page():
    return render_template('work.html')
