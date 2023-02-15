from flask import Blueprint, render_template, session, redirect
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

@bp.route('/bcnc/ts')
@session_helper.session_check
def bcnc_ts():
    return render_template('bcnc_TS.html')

@bp.route('/bcnc/bi')
@session_helper.session_check
def bcnc_bi():
    return render_template('bcnc_BI.html')