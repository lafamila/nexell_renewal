from flask import Blueprint, render_template, make_response, session, redirect
from ..helpers import session_helper
bp = Blueprint('energy', __name__, url_prefix='/energy')

@bp.route('/')
@session_helper.session_check
def index_page():
    return render_template('energy.html', title="프로젝트관리 | 넥셀시스템")
