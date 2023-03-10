from flask import Blueprint, render_template, make_response, session, redirect
from ..helpers import session_helper
bp = Blueprint('common', __name__, url_prefix='/')

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
@bp.route('/partner')
@session_helper.session_check
def partner_page():
    return render_template("partner.html")

@bp.route('/money')
@session_helper.session_check
def money_page():
    return render_template("money.html")

@bp.route('/cowork')
@session_helper.session_check
def cowork_page():
    return render_template("cowork.html")

@bp.route('/overpay')
@session_helper.session_check
def overpay_page():
    return render_template("overpay.html")

@bp.route('/extra')
@session_helper.session_check
def extra_page():
    return render_template("extra.html")

@bp.route('/finance')
@session_helper.session_check
def finance_page():
    return render_template("finance.html")

@bp.route('/reserve')
@session_helper.session_check
def reserve_page():
    return render_template("reserve.html")


@bp.route('/five')
@session_helper.session_check
def five_page():
    return render_template("five.html")


