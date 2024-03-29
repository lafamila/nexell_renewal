from flask import Blueprint, render_template, session, redirect
from ..helpers import session_helper
from .api.services import refresh_code_list

bp = Blueprint('member', __name__, url_prefix='/member')

@bp.route('/')
@session_helper.session_check
def index_page():
    return render_template('member.html', title="사용자관리 | 넥셀시스템", **refresh_code_list())
