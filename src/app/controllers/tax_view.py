from flask import Blueprint, render_template, make_response, session, redirect
from ..helpers import session_helper
from .api.services import refresh_code_list

bp = Blueprint('tax', __name__, url_prefix='/tax')

@bp.route('/')
@session_helper.session_check
def index_page():
    return render_template('tax.html', title="세금계산서 관리 | 넥셀시스템", **refresh_code_list())
