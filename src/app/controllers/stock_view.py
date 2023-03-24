from flask import Blueprint, render_template, request, session, redirect
from ..helpers import session_helper
bp = Blueprint('stock', __name__, url_prefix='/stock')

@bp.route('/ts')
@session_helper.session_check
def ts_index_page():
    return render_template('stock_TS.html', title="창고현황(공조) | 넥셀시스템")

@bp.route('/bi')
@session_helper.session_check
def bi_index_page():
    return render_template('stock_BI.html', title="창고현황(빌트인) | 넥셀시스템")
