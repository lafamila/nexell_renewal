from flask import Blueprint, render_template, request, session, redirect
from ..helpers import session_helper
from .api.services import refresh_code_list

bp = Blueprint('stock', __name__, url_prefix='/stock')

@bp.route('/ts')
@session_helper.session_check
def ts_index_page():
    return render_template('stock_TS.html', title="창고현황(공조) | 넥셀시스템", **refresh_code_list())

@bp.route('/bi')
@session_helper.session_check
def bi_index_page():
    return render_template('stock_BI.html', title="창고현황(빌트인) | 넥셀시스템", **refresh_code_list())

@bp.route('/search')
@session_helper.session_check
def search_page():
    params = request.args.get("before")
    if not params:
        params = ""

    add_params = request.args.get("after")
    if not add_params:
        add_params = ""

    response = request.args.get("response")
    if not response:
        response = "0"
    return render_template("stock_search.html", title="창고검색 | 넥셀시스템", params=params, add_params=add_params, response=response, **refresh_code_list())
