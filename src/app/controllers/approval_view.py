from flask import Blueprint, render_template, session, redirect
from ..helpers import session_helper
bp = Blueprint('approval', __name__, url_prefix='/approval')

@bp.route('/')
@session_helper.session_check
def index_page():
    return render_template('approval.html', title="전자결재 | 넥셀시스템")
