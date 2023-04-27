from flask import Blueprint, g, current_app, render_template, redirect, request, make_response, jsonify, send_file, Response, url_for, session
from .services import completed_service as cp
from .services import project_service as prj
from .services import stock_service as st

from app.connectors import DB
from app.helpers import session_helper
from .services import set_menu
import json
import os
from datetime import datetime
from dateutil import relativedelta
from collections import OrderedDict

bp = Blueprint('api_completed', __name__, url_prefix='/api/completed')

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

@bp.route('/ajax_get_completed_report_data', methods=['GET'])
def completed_ajax_get_completed_report_data():
    params = request.args.to_dict()
    s_pxcond_dtm = params["s_pxcond_mt"]
    params["s_pxcond_mt"] = "-".join(s_pxcond_dtm.split("-")[:2])
    completedList = cp.get_completed_reportNR(params)
    data = OrderedDict()
    for c in completedList:
        execut_code = c['cntrct_execut_code']
        if execut_code not in ("C", "E"):
            continue
        key = (c["bsn_dept_nm"], c["cntrct_bcnc_nm"], c["spt_nm"], c["spt_chrg_nm"], c['cntrct_sn'])
        if key not in data:
            data[key] = {"C" : [0, 0, 0], "E" : [0, 0, 0, 0], "rate" : None}

        cntrct_amount = int(c["cntrct_amount"]) if c["cntrct_amount"] != '' else 0
        complete_amount = int(c["complete_amount"]) if c["complete_amount"] != '' else 0
        amount = int(c["tax_amount"]) if c["tax_amount"] != '' else (int(c["execut_amount"]) if c["execut_amount"] != '' else 0)
        if execut_code == 'C':
            data[key][execut_code][0] += cntrct_amount
            data[key][execut_code][1] += complete_amount
            data[key][execut_code][2] += amount
        else:
            data[key][execut_code][0] += cntrct_amount
            data[key][execut_code][1] += complete_amount
            if str(c["ct_se_code"]) in ("1", "2", "3", "4"):
                data[key][execut_code][2] += amount
            else:
                data[key][execut_code][3] += amount
        data[key]["rate"] = c['rate']
    result = list()
    for key in data:
        bsn_dept_nm, cntrct_bcnc_nm, spt_nm, spt_chrg_nm, cntrct_sn = key
        row = {"bsn_dept_nm" : bsn_dept_nm, "cntrct_bcnc_nm" : cntrct_bcnc_nm, "spt_nm" : spt_nm, "spt_chrg_nm" : spt_chrg_nm, "cntrct_sn" : cntrct_sn}
        row['c_cntrct_amount'] = data[key]['C'][0]
        row['c_completed_amount'] = data[key]['C'][1]
        row['c_now_amount'] = data[key]['C'][2]
        row['e_cntrct_amount'] = data[key]['E'][0]
        row['e_completed_amount'] = data[key]['E'][1]
        row['e_now_amount1'] = data[key]['E'][2]
        row['e_now_amount2'] = data[key]['E'][3]
        row['rate'] = data[key]['rate']
        if row['c_completed_amount'] == 0 and row['c_now_amount'] == 0 and row['e_completed_amount'] == 0 and row['e_now_amount1'] == 0 and row['e_now_amount2'] == 0:
            continue
        result.append(row)

    return jsonify(result)
@bp.route('/ajax_get_completed_reportNR', methods=['GET'])
def completed_ajax_get_completed_reportNR():
    params = request.args.to_dict()
    result = dict()
    s_pxcond_dtm = params["s_pxcond_mt"]
    params["s_pxcond_mt"] = "-".join(s_pxcond_dtm.split("-")[:2])
    result['contractStatusList'] = cp.get_contract_status_list(params)
    result['executStatusList'] = cp.get_execut_status_list(params)
    result['completedList'] = cp.get_completed_reportNR(params)
    new_params = dict()
    new_params["s_pxcond_mt"] = (datetime.strptime(s_pxcond_dtm, "%Y-%m-%d")-relativedelta.relativedelta(months=1)).strftime("%Y-%m")
    result['lastDate'] = cp.get_completed_reportNR(new_params)


    result['status'] = True
    return jsonify(result)

@bp.route('/get_completed_info', methods=['GET'])
def get_completed_info():
    params = request.args.to_dict()
    result = dict()
    result['bcnc'] = cp.get_completed_bcnc_data(params)
    result['data'] = cp.get_completed(params)
    return jsonify(result)

@bp.route('/insert_completed', methods=['POST'])
def insert_completed():
    params = request.get_json()
    cp.insert_completed(params)
    return jsonify({"status":True, "message" : "성공적으로 처리되었습니다."})
