from flask import Blueprint, g, current_app, render_template, redirect, request, make_response, jsonify, send_file, Response, url_for, session
from .services import common_service as cm
from .services import project_service as prj

from app.connectors import DB
from app.helpers import session_helper
from .services import set_menu
import json
import os
from datetime import datetime

bp = Blueprint('api_common', __name__, url_prefix='/api')

@bp.before_request
def connect():
    g.db = DB()
    g.curs = g.db.cursor()

@bp.after_request
def disconnect(response):
    g.db.commit()

    g.curs.close()
    g.db.close()
    return response

@bp.route('/work/ajax_get_work', methods=['GET'])
def ajax_get_work():
    params = request.args.to_dict()
    result = dict()
    result['data'] = cm.get_work(params)
    result['status'] = True
    return jsonify(result)

@bp.route('/bnd/ajax_get_bcnc_list', methods=['GET'])
def ajax_get_bcnc_list():
    params = request.args.to_dict()
    result = dict()
    result['bData'] = cm.get_bcncs()
    result['cData'] = cm.get_chrgs()
    result['dData'] = cm.get_c_chrgs()
    result['status'] = True
    return jsonify(result)

@bp.route('/bnd/ajax_get_bnd', methods=['GET'])
def ajax_get_bnd():
    params = request.args.to_dict()
    result = dict()
    result['data'] = cm.get_bnd_projects(params)
    accounts = cm.get_s6_account_list(params)
    result['account'] = dict()
    for acc in accounts:
        cntrct_sn = str(acc['cntrct_sn'])
        delng_ty_code = 'M' if acc['p_delng_ty_code'] == '61' else 'S'
        dlivy_de = acc['s_dlivy_de']
        if cntrct_sn not in result['account']:
            result['account'][cntrct_sn] = {"M" : [], "S" : []}
        result['account'][cntrct_sn][delng_ty_code].append(dlivy_de)

    taxbill = cm.get_s6_taxbill_list(params)
    result['taxbill'] = dict()
    for tax in taxbill:
        cntrct_sn = str(tax['cntrct_sn'])
        delng_se_code = 'M' if tax['s_delng_se_code'] == 'S2' else 'T'
        dlivy_de = tax['s_dlivy_de']
        amount = tax['amount']
        if cntrct_sn not in result['taxbill']:
            result['taxbill'][cntrct_sn] = {"M" : [], "T" : []}
        result['taxbill'][cntrct_sn][delng_se_code].append((dlivy_de, amount))

    rcppay = cm.get_i2_rcppay_list(params)
    result['rcppay'] = dict()
    for r in rcppay:
        cntrct_sn = str(r['cntrct_sn'])
        amount = r['amount']
        rcppay_se_code = 'M' if r['rcppay_se_code'] == 'I2' else 'T'
        if cntrct_sn not in result['rcppay']:
            result['rcppay'][cntrct_sn] = {"M" : 0, "T" : 0}
        result['rcppay'][cntrct_sn][rcppay_se_code] = amount

    for cntrct_sn in result['account']:
        if cntrct_sn in result['taxbill']:
            result['account'][cntrct_sn]["max_row"] = max(len(result['account'][cntrct_sn]["M"]), len(result['account'][cntrct_sn]["S"]), len(result['taxbill'][cntrct_sn]["M"]), len(result['taxbill'][cntrct_sn]["T"]))
        else:
            result['account'][cntrct_sn]["max_row"] = max(len(result['account'][cntrct_sn]["M"]), len(result['account'][cntrct_sn]["S"]))


    return jsonify(result)