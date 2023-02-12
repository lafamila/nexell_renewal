from flask import Blueprint, render_template, request, session, redirect
from ..helpers import session_helper
bp = Blueprint('stock', __name__, url_prefix='/stock')

@bp.route('/ts')
@session_helper.session_check
def ts_index_page():
    return render_template('stock_TS.html')

@bp.route('/bi')
@session_helper.session_check
def bi_index_page():
    return render_template('stock_BI.html')
