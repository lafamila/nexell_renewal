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
from pytz import timezone
bp = Blueprint('api_completed', __name__, url_prefix='/api/completed')

@bp.before_request
def connect():
    g.db = DB()
    g.curs = g.db.cursor()

@bp.after_request
def disconnect(response):
    if response.status_code != 500:
        g.db.commit()

    g.curs.close()
    g.db.close()
    return response

@bp.route('/ajax_get_completed_report_data', methods=['GET'])
def completed_ajax_get_completed_report_data():
    params = request.args.to_dict()
    s_pxcond_dtm = params["s_pxcond_mt"]
    params["purpose"] = "data"
    params["s_pxcond_mt"] = "-".join(s_pxcond_dtm.split("-")[:2])
    completedList = cp.get_completed_reportNR(params)
    data = OrderedDict()
    for c in completedList:
        execut_code = c['cntrct_execut_code']
        if execut_code not in ("C", "E"):
            continue
        key = (c["bsn_dept_nm"], c["cntrct_bcnc_nm"], c["spt_nm"], c["spt_chrg_nm"], c['cntrct_sn'])
        if key not in data:
            data[key] = {"C" : [0, 0, 0], "E" : [0, 0, 0, 0], "rate" : None, "rm" : ""}

        cntrct_amount = int(c["cntrct_amount"]) if c["cntrct_amount"] != '' else 0
        complete_amount = int(c["complete_amount"]) if c["complete_amount"] != '' else 0
        amount = float(c["tax_amount"]) if c["tax_amount"] != 0.0 else (float(c["excut_amount"]) if c["excut_amount"] != 0.0 else 0.0)
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
        if c['rm'] != '' and data[key]["rm"] != c['rm']:
            data[key]["rm"] = c["rm"]
    result = list()
    for key in data:
        bsn_dept_nm, cntrct_bcnc_nm, spt_nm, spt_chrg_nm, cntrct_sn = key
        indirect = cp.get_indirect_data({"cntrct_sn" : cntrct_sn})
        before_indirect = 0
        now_indirect = 0
        for i_tax in indirect["taxbilList"]:
            if i_tax["pblicte_de"] < datetime.strptime(params["s_pxcond_mt"]+"-01", "%Y-%m-%d").date():
                before_indirect += int(i_tax["splpc_am"]) + int(i_tax["vat"])
            elif i_tax["pblicte_de"].strftime("%Y-%m-01") == params["s_pxcond_mt"]+"-01":
                now_indirect += int(i_tax["splpc_am"]) + int(i_tax["vat"])


        row = {"bsn_dept_nm" : bsn_dept_nm, "cntrct_bcnc_nm" : cntrct_bcnc_nm, "spt_nm" : spt_nm, "spt_chrg_nm" : spt_chrg_nm, "cntrct_sn" : cntrct_sn}
        row['c_cntrct_amount'] = data[key]['C'][0]
        row['c_completed_amount'] = data[key]['C'][1]
        row['c_now_amount'] = data[key]['C'][2]
        row['e_cntrct_amount'] = data[key]['E'][0]
        # row['e_completed_amount'] = data[key]['E'][1] + before_indirect
        # row['e_now_amount1'] = data[key]['E'][2] + now_indirect
        row['e_completed_amount'] = data[key]['E'][1]
        row['e_now_amount1'] = data[key]['E'][2]
        row['e_now_amount2'] = data[key]['E'][3]
        row['rate'] = data[key]['rate']
        row['rm'] = data[key]['rm']
        row['va'] = indirect["va_total"]
        if row['c_completed_amount'] == 0 and row['c_now_amount'] == 0 and row['e_completed_amount'] == 0 and row['e_now_amount1'] == 0 and row['e_now_amount2'] == 0:
            continue
        result.append(row)

    return jsonify(result)

@bp.route('/ajax_get_completed_report_data_new', methods=['GET'])
def completed_ajax_get_completed_report_data_new():
    params = request.args.to_dict()
    s_pxcond_dtm = params["s_pxcond_mt"]
    params["purpose"] = "data"
    params["s_pxcond_mt"] = "-".join(s_pxcond_dtm.split("-")[:2])
    completedList = cp.get_completed_reportNR_new(params)
    data = OrderedDict()
    for c in completedList:
        execut_code = c['cntrct_execut_code']
        if execut_code not in ("C", "E"):
            continue
        key = (c["bsn_dept_nm"], c["cntrct_bcnc_nm"], c["spt_nm"], c["spt_chrg_nm"], c['cntrct_sn'])
        if key not in data:
            data[key] = {"C" : [0, 0, 0], "E" : [0, 0, 0, 0], "rate" : None, "rm" : ""}

        cntrct_amount = int(c["cntrct_amount"]) if c["cntrct_amount"] != '' else 0
        complete_amount = int(c["complete_amount"]) if c["complete_amount"] != '' else 0
        amount = float(c["tax_amount"]) if c["tax_amount"] != 0.0 else (float(c["excut_amount"]) if c["excut_amount"] != 0.0 else 0.0)
        if execut_code == 'C':
            data[key][execut_code][0] += cntrct_amount
            data[key][execut_code][1] += complete_amount
            data[key][execut_code][2] += amount
        else:
            data[key][execut_code][0] += cntrct_amount
            data[key][execut_code][1] += complete_amount
            if str(c["ct_se_code"]) in ("1", "2", "3", "4", "8"):
                data[key][execut_code][2] += amount
            else:
                data[key][execut_code][3] += amount
        data[key]["rate"] = c['rate']
        if c['rm'] != '' and data[key]["rm"] != c['rm']:
            data[key]["rm"] = c["rm"]
    result = list()
    for key in data:
        bsn_dept_nm, cntrct_bcnc_nm, spt_nm, spt_chrg_nm, cntrct_sn = key
        indirect = cp.get_indirect_data({"cntrct_sn" : cntrct_sn})

        row = {"bsn_dept_nm" : bsn_dept_nm, "cntrct_bcnc_nm" : cntrct_bcnc_nm, "spt_nm" : spt_nm, "spt_chrg_nm" : spt_chrg_nm, "cntrct_sn" : cntrct_sn}
        row['c_cntrct_amount'] = data[key]['C'][0]
        row['c_completed_amount'] = data[key]['C'][1]
        row['c_now_amount'] = data[key]['C'][2]
        row['e_cntrct_amount'] = data[key]['E'][0]
        # row['e_completed_amount'] = data[key]['E'][1] + before_indirect
        # row['e_now_amount1'] = data[key]['E'][2] + now_indirect
        row['e_completed_amount'] = data[key]['E'][1]
        row['e_now_amount1'] = cp.get_s1(cntrct_sn, params["s_pxcond_mt"])
        # row['e_now_amount1'] = data[key]['E'][2]
        # row['e_now_amount2'] = (data[key]['E'][2] + data[key]['E'][3]) - cp.get_s1(cntrct_sn, params["s_pxcond_mt"])
        row['e_now_amount2'] = cp.get_s2(cntrct_sn, params["s_pxcond_mt"])
        row['rate'] = cp.get_s(cntrct_sn) * 100.0 / row['c_cntrct_amount'] if row['c_cntrct_amount'] != 0 else 0.0
        row['rm'] = data[key]['rm']
        row['va'] = indirect["va_total"]
        if row['c_completed_amount'] == 0 and row['c_now_amount'] == 0 and row['e_completed_amount'] == 0 and row['e_now_amount1'] == 0 and row['e_now_amount2'] == 0:
            continue
        result.append(row)

    return jsonify(result)
    # except Exception as e:
    #     print(e)
    #     return make_response(str(e), 500)

@bp.route('/ajax_get_completed_reportNR', methods=['GET'])
def completed_ajax_get_completed_reportNR():
    try:
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
    except Exception as e:
        print(e)
        return make_response(str(e), 500)

@bp.route('/ajax_get_completed_reportNR_new', methods=['GET'])
def completed_ajax_get_completed_reportNR_new():
    # try:
        params = request.args.to_dict()
        result = dict()
        s_pxcond_dtm = params["s_pxcond_mt"]
        params["s_pxcond_mt"] = "-".join(s_pxcond_dtm.split("-")[:2])
        result['contractStatusList'] = cp.get_contract_status_list(params)
        result['executStatusList'] = cp.get_execut_status_list(params)
        result['completedList'] = cp.get_completed_reportNR_new(params)
        new_params = dict()
        new_params["s_pxcond_mt"] = (datetime.strptime(s_pxcond_dtm, "%Y-%m-%d")-relativedelta.relativedelta(months=1)).strftime("%Y-%m")
        result['lastDate'] = cp.get_completed_reportNR_new(new_params)


        result['status'] = True
        return jsonify(result)
    # except Exception as e:
    #     print(e)
    #     return make_response(str(e), 500)


@bp.route('/get_completed_info', methods=['GET'])
def get_completed_info():
    try:
        params = request.args.to_dict()
        result = dict()
        result['bcnc'] = cp.get_completed_bcnc_data(params)
        result['data'] = cp.get_completed(params)
        return jsonify(result)
    except Exception as e:
        print(e)
        return make_response(str(e), 500)

@bp.route('/insert_completed', methods=['POST'])
def insert_completed():
    try:
        params = request.get_json()
        cp.insert_completed(params)
        return jsonify({"status":True, "message" : "성공적으로 처리되었습니다."})

    except Exception as e:
        print(e)
        return make_response(str(e), 500)

@bp.route('/ajax_insert_completed', methods=['POST'])
def ajax_insert_completed():
    try:
        params = request.form.to_dict()
        cp.delete_pxcond(params)
        cp.insert_pxcond(params)
        return jsonify({"status" : True, "message" : "성공적으로 입력되었습니다."})
    except Exception as e:
        print(e)
        return make_response(str(e), 500)


@bp.route('/ajax_update_completed', methods=['POST'])
def ajax_update_completed():
    try:
        params = request.form.to_dict()
        status = cp.update_pxcond(params)
        return jsonify({"status" : status})
    except Exception as e:
        print(e)
        return make_response(str(e), 500)

