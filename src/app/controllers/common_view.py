from flask import Blueprint, render_template, make_response, session, redirect
from ..helpers import session_helper
bp = Blueprint('common', __name__, url_prefix='/')

@bp.route('/work')
@session_helper.session_check
def work_page():
    return render_template('work.html')

@bp.route('/bnd')
@session_helper.session_check
def bnd_page():
    return render_template('bnd.html')

@bp.route('/bcnc/<dept_code>')
@session_helper.session_check
def bcnc_page(dept_code):
    dept = {"bi" : "빌트인", "ts" : "공조"}
    if dept_code not in dept:
        return make_response('', 404)
    return render_template('bcnc.html', dept_code=dept_code.upper(), dept_nm=dept[dept_code])

@bp.route('/month')
@session_helper.session_check
def month_page():
    return render_template("month.html")