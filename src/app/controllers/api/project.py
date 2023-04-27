from flask import Blueprint, g, current_app, render_template, redirect, request, make_response, jsonify, send_file, Response, url_for, session
from .services import project_service as prj
from .services import member_service as mber
from .services import charger_service as chrg
from .services import dspy_cost_service as dsp
from .services import sales_service as sales
from .services import stock_service as st
from app.connectors import DB
from app.helpers import session_helper
from .services import set_menu
import json
import os
from datetime import datetime

bp = Blueprint('api_project', __name__, url_prefix='/api/project')

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


@bp.route('/ajax_get_project_datatable', methods=['POST'])
def ajax_get_project_datatable():
    params = request.form.to_dict()
    result = prj.get_project_datatable(params)
    result['contract'] = prj.get_contract_summary(params)
    result['count'] = prj.get_contract_count_summary(params)
    result['member'] = mber.get_member(session["member"]["member_sn"])
    return jsonify(result)

@bp.route('/ajax_get_reportNR', methods=['GET'])
def ajax_get_reportNR():
    params = request.args.to_dict()
    result = {}

    result['contract'] = prj.get_contract(params)
    result['project'] = prj.get_project(params)
    result['charger'] = chrg.get_charger_list(params)

    result['construct'] = prj.get_construct(params)

    result['aCostList'] = prj.get_a_cost_list(params)
    result['bCostList'] = prj.get_b_cost_list(params)
    result['extraCostList'] = prj.get_extra_cost_list(params)
    result['c5CostList'] = prj.get_c5_cost_list(params)
    result['e5CostList'] = prj.get_e5_cost_list(params)

    result['rcppayList'] = prj.get_rcppay_report_list(params)
    result['etcRcppayList'] = prj.get_etc_rcppay_report_list(params)

    result['s1AccountList'] = prj.get_s1_account_report_list(params)
    result['s2AccountList'] = prj.get_s2_account_report_list(params)
    result['s3AccountList'] = prj.get_s3_account_report_list(params)
    result['s4AccountList'] = prj.get_s4_account_report_list(params)
    result['s61AccountList'] = prj.get_s61_account_report_list(params)
    result['sModelCostList'] = prj.get_model_cost_list(params)
    result['sOptionCostList'] = prj.get_option_cost_list(params)
    result['outsrcList'] = prj.get_outsrc_report_list(params)
    result['outsrcItem'] = dict()
    for outsrc in result['outsrcList']:
        s_params = {key:value for key, value in params.items()}
        s_params["s_outsrc_fo_sn"] = outsrc["outsrc_fo_sn"]
        result['outsrcItem'][outsrc["outsrc_fo_sn"]] = prj.get_outsrc_detail(s_params)
    result['modelList'] = dict()
    for d in result['sModelCostList']:
        stocks = st.get_stock_by_account(d['delng_sn'])
        for stock in stocks:
            detail = st.get_stock_log({"s_stock_sn" : stock['stock_sn']})
            from pprint import pprint
            candidate = False
            candidateDate = None
            candidatePlace = None
            for log in detail[::-1]:
                if log['stock_sttus'] == 1:
                    candidate = True
                    candidateDate = log['ddt_man']
                    candidatePlace = log['cntrct_nm']
                    continue
                if candidate and log['log_sn'] == stock['log_sn']:
                    if d['delng_sn'] not in result['modelList']:
                        result['modelList'][d['delng_sn']] = {"count" : 0, "return_de" : None, "return_place" : None}
                    result['modelList'][d['delng_sn']]["count"] += 1
                    result['modelList'][d['delng_sn']]["return_de"] = candidateDate
                    result['modelList'][d['delng_sn']]["return_place"] = candidatePlace
                    break
                candidate = False
                candidateDate = None
                candidatePlace = None
            # if detail['item_sttus'] == 1
    result['dspyCostList'] = dsp.get_dspy_cost_list(params)
    result["status"] = True
    return jsonify(result)

@bp.route('/ajax_get_reportBD', methods=['GET'])
def ajax_get_reportBD():
    params = request.args.to_dict()
    result = {}

    result['contract'] = prj.get_contract(params)
    result['project'] = prj.get_project(params)
    result['charger'] = chrg.get_charger_list(params)

    result['cCostListExtra'] = prj.get_c_cost_list_extra(params)
    result['eCostListExtra'] = prj.get_e_cost_list_extra(params)
    result['gCostListExtra'] = prj.get_g_cost_list_extra(params)
    result['cCostList'] = prj.get_c_cost_list(params)
    result['eCostList'] = prj.get_e_cost_list(params)
    result['gCostList'] = prj.get_g_cost_list(params)

    result['sTaxbilList'] = prj.get_s_taxbil_report_list(params)
    result['iRcppayList'] = prj.get_i_rcppay_report_list(params)

    result['s2TaxbilList'] = {"M" : [], "S" : []}
    s2TaxbilList = prj.get_s2_taxbil_report_list(params)
    for s in s2TaxbilList:
        if s['delng_se_code'] == 'S2':
            result['s2TaxbilList']['M'].append(s)
        else:
            result['s2TaxbilList']['S'].append(s)

    result['i2RcppayList'] = {"M" : [], "S" : []}
    i2RcppayList = prj.get_i2_rcppay_report_list(params)
    for i in i2RcppayList:
        if i['rcppay_se_code'] == 'I2':
            result['i2RcppayList']['M'].append(i)
        else:
            result['i2RcppayList']['S'].append(i)
    result['s3TaxbilList'] = prj.get_s3_taxbil_report_list(params)
    result['i3RcppayList'] = prj.get_i3_rcppay_report_list(params)
    s3TaxbilList = prj.get_s3_taxbil_report_list(params)
    i3RcppayList = prj.get_i3_rcppay_report_list(params)
    s3TaxbilList = {s['taxbil_sn'] : s for s in s3TaxbilList}
    for i in i3RcppayList:
        if i['cnnc_sn'] != '' and i['cnnc_sn'] in s3TaxbilList:
            if 'rcppay' not in s3TaxbilList[i['cnnc_sn']]:

                s3TaxbilList[i['cnnc_sn']]['rcppay'] = list()
            s3TaxbilList[i['cnnc_sn']]['rcppay'].append(i)

    result['si3List'] = s3TaxbilList
    result['s63List'] = prj.get_sale_model_list(params)
    result['si3ListLength'] = sum([1 if 'rcppay' not in s else len(s['rcppay']) for s in s3TaxbilList.values()])
    result['s63ListLength'] = len(result['s63List'])
    result['sOptionCostList'] = prj.get_option_cost_list(params)


    result['s12AccountList'] = prj.get_s12_account_report_list(params)
    result['s6AccountList'] = prj.get_s6_account_report_list(params)
    result['s7AccountList'] = prj.get_s7_account_report_list(params)

    #TODO : modelList api
    result['sModelCostList'] = sales.get_model_list(params)
    result['modelList'] = dict()
    for d in result['sModelCostList']:
        stocks = st.get_stock_by_account(d['delng_sn'])
        for stock in stocks:
            detail = st.get_stock_log({"s_stock_sn" : stock['stock_sn']})
            candidate = False
            candidateDate = None
            candidatePlace = None
            for log in detail[::-1]:
                if log['stock_sttus'] == 1:
                    candidate = True
                    candidateDate = log['ddt_man']
                    candidatePlace = log['cntrct_nm']
                    continue
                if candidate and log['log_sn'] == stock['log_sn']:
                    if d['delng_sn'] not in result['modelList']:
                        result['modelList'][d['delng_sn']] = {"count" : 0, "return_de" : None, "return_place" : None}
                    result['modelList'][d['delng_sn']]["count"] += 1
                    result['modelList'][d['delng_sn']]["return_de"] = candidateDate
                    result['modelList'][d['delng_sn']]["return_place"] = candidatePlace
                    break
                candidate = False
                candidateDate = None
                candidatePlace = None
    result['etcRcppayList'] = prj.get_etc_rcppay_report_list(params)
    result['dspyCostList'] = dsp.get_dspy_cost_list(params)
    result["status"] = True

    return result


@bp.route('/ajax_get_reportBF', methods=['GET'])
def ajax_get_reportBF():
    params = request.args.to_dict()
    result = {}

    result['contract'] = prj.get_contract(params)
    result['project'] = prj.get_project(params)
    result['charger'] = chrg.get_charger_list(params)

    result['cCostListExtra'] = prj.get_c_cost_list_extra(params)
    result['eCostListExtra'] = prj.get_e_cost_list_extra(params)
    result['gCostListExtra'] = prj.get_g_cost_list_extra(params)
    result['cCostList'] = prj.get_c_cost_list(params)
    result['eCostList'] = prj.get_e_cost_list(params)
    result['gCostList'] = prj.get_g_cost_list(params)

    result['s1TaxbilList'] = prj.get_s1_taxbil_report_list(params)
    result['i1RcppayList'] = prj.get_i1_rcppay_report_list(params)
    result['s2TaxbilList'] = {"M" : [], "S" : []}
    s2TaxbilList = prj.get_s2_taxbil_report_list(params)
    for s in s2TaxbilList:
        if s['delng_se_code'] == 'S2':
            result['s2TaxbilList']['M'].append(s)
        else:
            result['s2TaxbilList']['S'].append(s)

    result['i2RcppayList'] = {"M" : [], "S" : []}
    i2RcppayList = prj.get_i2_rcppay_report_list(params)
    for i in i2RcppayList:
        if i['rcppay_se_code'] == 'I2':
            result['i2RcppayList']['M'].append(i)
        else:
            result['i2RcppayList']['S'].append(i)
    result['s3TaxbilList'] = prj.get_s3_taxbil_report_list(params)
    result['i3RcppayList'] = prj.get_i3_rcppay_report_list(params)
    s3TaxbilList = prj.get_s3_taxbil_report_list(params)
    i3RcppayList = prj.get_i3_rcppay_report_list(params)
    s3TaxbilList = {s['taxbil_sn'] : s for s in s3TaxbilList}
    for i in i3RcppayList:
        if i['cnnc_sn'] != '' and i['cnnc_sn'] in s3TaxbilList:
            if 'rcppay' not in s3TaxbilList[i['cnnc_sn']]:

                s3TaxbilList[i['cnnc_sn']]['rcppay'] = list()
            s3TaxbilList[i['cnnc_sn']]['rcppay'].append(i)

    result['si3List'] = s3TaxbilList
    result['s63List'] = prj.get_sale_model_list(params)
    result['si3ListLength'] = sum([1 if 'rcppay' not in s else len(s['rcppay']) for s in s3TaxbilList.values()])
    result['s63ListLength'] = len(result['s63List'])
    result['sOptionCostList'] = prj.get_option_cost_list(params)

    result['s6AccountList'] = prj.get_s6_account_report_list(params)
    result['sModelCostList'] = sales.get_model_list(params)
    result['modelList'] = dict()
    for d in result['sModelCostList']:
        stocks = st.get_stock_by_account(d['delng_sn'])
        for stock in stocks:
            detail = st.get_stock_log({"s_stock_sn" : stock['stock_sn']})
            candidate = False
            candidateDate = None
            candidatePlace = None
            for log in detail[::-1]:
                if log['stock_sttus'] == 1:
                    candidate = True
                    candidateDate = log['ddt_man']
                    candidatePlace = log['cntrct_nm']
                    continue
                if candidate and log['log_sn'] == stock['log_sn']:
                    if d['delng_sn'] not in result['modelList']:
                        result['modelList'][d['delng_sn']] = {"count" : 0, "return_de" : None, "return_place" : None}
                    result['modelList'][d['delng_sn']]["count"] += 1
                    result['modelList'][d['delng_sn']]["return_de"] = candidateDate
                    result['modelList'][d['delng_sn']]["return_place"] = candidatePlace
                    break
                candidate = False
                candidateDate = None
                candidatePlace = None
    result['s7AccountList'] = prj.get_s7_account_report_list(params)

    result['etcRcppayList'] = prj.get_etc_rcppay_report_list(params)
    result['dspyCostList'] = dsp.get_dspy_cost_list(params)
    result["status"] = True

    return result

@bp.route('/ajax_get_finals', methods=['POST'])
def ajax_get_finals():
    params = request.form.to_dict()
    result = prj.get_finals(params)
    result['count'] = prj.get_finals_summary(params)
    return jsonify(result)

@bp.route('/ajax_insert_finals', methods=['GET'])
def ajax_insert_finals():
    params = request.args.to_dict()
    prj.insert_finals(params)
    return jsonify({"status": True, "message": "성공적으로 입력되었습니다."})

@bp.route('/ajax_update_finals', methods=['GET'])
def ajax_update_finals():
    params = request.args.to_dict()
    prj.update_finals(params)
    return jsonify({"status" : True, "message" : "성공적으로 입력되었습니다."})


@bp.route('/ajax_delete_finals', methods=['GET'])
def ajax_delete_finals():
    params = request.args.to_dict()
    prj.delete_finals(params)
    return jsonify({"status" : True, "message" : "성공적으로 처리되었습니다."})

@bp.route('/get_contract_no', methods=['GET'])
def get_contract_no():
    params = request.args.to_dict()
    result = prj.get_contract_no(params)
    return jsonify(result)

@bp.route('/insert_project', methods=['POST'])
def insert_project():
    params = request.get_json()
    prj.insert_project(params)
    return jsonify({"status" : True, "message" : "성공적으로 추가되었습니다."})

@bp.route('/get_b_projects', methods=['GET'])
def get_b_projects():
    params = request.args.to_dict()
    result = prj.get_b_projects(params)
    return jsonify(result)

@bp.route('/get_p_projects', methods=['GET'])
def get_p_projects():
    params = request.args.to_dict()
    result = prj.get_p_projects(params)
    return jsonify(result)

@bp.route('/get_all_projects', methods=['GET'])
def get_all_projects():
    params = request.args.to_dict()
    result = prj.get_all_projects(params)
    return jsonify(result)

@bp.route('/insert_b_project', methods=['POST'])
def insert_b_project():
    params = request.get_json()
    prj.insert_b_project(params)
    return jsonify({"status" : True, "message" : "성공적으로 처리되었습니다."})

@bp.route('/insert_BD_b_project', methods=['POST'])
def insert_BD_b_project():
    params = request.get_json()
    prj.insert_b_bd_project(params)
    return jsonify({"status" : True, "message" : "성공적으로 처리되었습니다."})

@bp.route('/insert_BF_b_project', methods=['POST'])
def insert_BF_b_project():
    params = request.get_json()
    prj.insert_b_bf_project(params)
    return jsonify({"status" : True, "message" : "성공적으로 처리되었습니다."})

@bp.route('/get_cost_bf_bd', methods=['GET'])
def get_cost_bf_bd():
    params = request.args.to_dict()
    result = dict()
    prjct = prj.get_project_by_cntrct_nm(params["s_cntrct_sn"])
    params["s_prjct_sn"] = prjct["prjct_sn"]
    result['cCostList'] = prj.get_c_cost_list(params)
    result['cCostListByExtra'] = dict()
    for cost in result['cCostList']:
        extra_sn = cost['extra_sn']
        if extra_sn not in result['cCostListByExtra']:
            result['cCostListByExtra'][extra_sn] = list()
        result['cCostListByExtra'][extra_sn].append(cost)

    result['cCostListExtra'] = prj.get_c_cost_list_extra(params)
    result['eCostListExtra'] = prj.get_e_cost_list_extra(params)
    result['eCostList'] = prj.get_e_cost_list(params)
    result['gCostList'] = prj.get_g_cost_list(params)
    result['samsungList'] = prj.get_expect_equip_list(params)
    return jsonify(result)


@bp.route('/get_costs_bd', methods=['GET'])
def get_costs_bd():
    params = request.args.to_dict()
    result = dict()
    prjct = prj.get_project_by_cntrct_nm(params["s_cntrct_sn"])
    params["s_prjct_sn"] = prjct["prjct_sn"]
    result['aCostList'] = prj.get_a_cost_list(params)
    result['bCostList'] = prj.get_b_cost_list(params)
    extra_cost_list = prj.get_max_extra_cost_list(params)
    result['extraCostList'] = dict()
    for extra_cost in extra_cost_list:
        if extra_cost['extra_sn'] not in result['extraCostList']:
            result['extraCostList'][extra_cost['extra_sn']] = list()
        result['extraCostList'][extra_cost['extra_sn']].append(extra_cost)
    result['samsungList'] = prj.get_expect_equip_list(params)
    result['otherList'] = prj.get_expect_equip_other_list(params)
    result['etcRcppayList'] = prj.get_etc_rcppay_report_list(params)
    result['outsrcList'] = prj.get_outsrc_list(params)
    result['outsrcItem'] = dict()
    result['prjct'] = prjct
    for outsrc in result['outsrcList']:
        s_params = {key:value for key, value in params.items()}
        s_params["s_outsrc_fo_sn"] = outsrc["outsrc_fo_sn"]
        result['outsrcItem'][outsrc["outsrc_fo_sn"]] = prj.get_outsrc_detail(s_params)

    return jsonify(result)

@bp.route('/get_outsrc_detail', methods=['GET'])
def get_outsrc_detail():
    params = request.args.to_dict()
    prjct = prj.get_project_by_cntrct_nm(params['s_cntrct_sn'])
    params['s_prjct_sn'] = prjct['prjct_sn']
    result = prj.get_outsrc_detail(params)
    return jsonify(result)

@bp.route('/get_option_cost', methods=['GET'])
def get_option_cost():
    params = request.args.to_dict()
    result = prj.get_option_cost_list(params)
    return jsonify(result)

@bp.route('/insert_BF_option_cost', methods=['POST'])
def insert_BF_option_cost():
    params = request.get_json()
    prj.insert_option_cost(params)
    if params['opt_approval_type'] != 'S':
        prj.insert_b_option_bf_project(params)

    return jsonify({"status" : True, "message" : "성공적으로 처리되었습니다."})


@bp.route('/insert_BD_option_cost', methods=['POST'])
def insert_BD_option_cost():
    params = request.get_json()
    prj.insert_option_cost(params)
    if params['opt_approval_type'] != 'S':
        prj.insert_b_option_bd_project(params)

    return jsonify({"status" : True, "message" : "성공적으로 처리되었습니다."})

@bp.route('/insert_option_cost', methods=['POST'])
def insert_option_cost():
    params = request.get_json()
    prj.insert_option_cost(params)
    return jsonify({"status" : True, "message" : "성공적으로 처리되었습니다."})

@bp.route('/insert_BF_c_project', methods=['POST'])
def insert_BF_c_project():
    params = request.get_json()
    prj.delete_option_bf_project(params)
    params["cost_date"] = datetime.now().strftime("%Y-%m-%d")
    prj.insert_b_option_bf_project(params)

    prj.insert_BF_c_project(params)
    return jsonify({"status" : True, "message" : "성공적으로 처리되었습니다."})

@bp.route('/update_BF_c_project', methods=['POST'])
def update_BF_c_project():
    params = request.get_json()
    params["cost_date"] = datetime.now().strftime("%Y-%m-%d")
    prj.insert_b_option_bf_project(params)
    prj.update_BF_c_project(params)
    return jsonify({"status" : True, "message" : "성공적으로 처리되었습니다."})

@bp.route('/insert_BD_c_project', methods=['POST'])
def insert_BD_c_project():
    params = request.get_json()
    prj.delete_option_bd_project(params)
    params["cost_date"] = datetime.now().strftime("%Y-%m-%d")
    prj.insert_b_option_bd_project(params)
    prj.insert_bd_expect_equipment(params)
    prj.insert_BF_c_project(params)
    return jsonify({"status" : True, "message" : "성공적으로 처리되었습니다."})


@bp.route('/update_BD_c_project', methods=['POST'])
def update_BD_c_project():
    params = request.get_json()
    params["cost_date"] = datetime.now().strftime("%Y-%m-%d")
    prj.insert_b_option_bd_project(params)
    prj.insert_bd_expect_equipment(params)
    prj.update_BF_c_project(params)

    return jsonify({"status" : True, "message" : "성공적으로 처리되었습니다."})

    return jsonify({"status" : True, "message" : "성공적으로 처리되었습니다."})

@bp.route('/insert_c_project', methods=['POST'])
def insert_c_project():
    params = request.get_json()
    prj.insert_c_project(params)
    return jsonify({"status" : True, "message" : "성공적으로 처리되었습니다."})

@bp.route('/insert_biss', methods=['POST'])
def insert_biss():
    params = request.get_json()
    prj.update_biss(params)
    return jsonify({"status":True, "message" : "성공적으로 처리되었습니다."})

@bp.route('/update_c_project', methods=['POST'])
def update_c_project():
    params = request.get_json()
    prj.update_c_project(params)
    return jsonify({"status":True, "message" : "성공적으로 처리되었습니다."})

@bp.route('/ajax_update_flaw_co', methods=['GET'])
def ajax_update_flaw_co():
    params = request.args.to_dict()
    prj.update_flaw_co(params)
    return jsonify({"status": True, "message" : "성공적으로 처리되었습니다."})
