from flask import Blueprint, render_template, session, redirect
from ..helpers import session_helper
bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

@bp.route('/')
@session_helper.session_check
def index_page():
    return render_template('dashboard.html')
