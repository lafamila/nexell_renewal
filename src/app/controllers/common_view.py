from flask import Blueprint, render_template, make_response, session, redirect
from ..helpers import session_helper
bp = Blueprint('common', __name__, url_prefix='/')

@bp.route('/bnd')
@session_helper.session_check
def bnd_page():
    return render_template('bnd.html', title="빌트인현장현황 | 넥셀시스템")

@bp.route('/bcnc/<dept_code>')
@session_helper.session_check
def bcnc_page(dept_code):
    dept = {"bi" : "빌트인", "ts" : "공조"}
    if dept_code not in dept:
        return make_response('', 404)
    return render_template('bcnc.html', dept_code=dept_code.upper(), dept_nm=dept[dept_code], title="월별 매출현황({}) | 넥셀시스템".format(dept[dept_code]))

@bp.route('/month')
@session_helper.session_check
def month_page():
    return render_template("month.html", title="월별수주계획 | 넥셀시스템")
@bp.route('/partner')
@session_helper.session_check
def partner_page():
    return render_template("partner.html", title="거래처관리 | 넥셀시스템")

@bp.route('/money')
@session_helper.session_check
def money_page():
    return render_template("money.html", title="자금계획서 | 넥셀시스템")

@bp.route('/cowork')
@session_helper.session_check
def cowork_page():
    return render_template("cowork.html", title="설치비관리 | 넥셀시스템")

@bp.route('/overpay')
@session_helper.session_check
def overpay_page():
    return render_template("overpay.html", title="과집행현장 | 넥셀시스템")

@bp.route('/extra')
@session_helper.session_check
def extra_page():
    return render_template("extra.html", title="영업외이익현황 | 넥셀시스템")

@bp.route('/finance')
@session_helper.session_check
def finance_page():
    return render_template("finance.html", title="재무상태관리 | 넥셀시스템")

@bp.route('/reserve')
@session_helper.session_check
def reserve_page():
    return render_template("reserve.html", title="하자이행 유보현황 | 넥셀시스템")


@bp.route('/five')
@session_helper.session_check
def five_page():
    return render_template("five.html", title="5년간종합현황 | 넥셀시스템")

@bp.route('/blueprint')
@session_helper.session_check
def blueprint_page():
    return render_template("blueprint.html", title="설계진행현황 | 넥셀시스템")


@bp.route('/research')
@session_helper.session_check
def research_page():
    return render_template("research.html", title="연구소현황관리 | 넥셀시스템")


