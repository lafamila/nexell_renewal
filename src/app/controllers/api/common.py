from flask import Blueprint, g, current_app, render_template, redirect, request, make_response, jsonify, send_file, Response, url_for, session
from .services import common_service as cm
from .services import completed_service as cp

from app.connectors import DB
from app.helpers import session_helper
from .services import set_menu
import json
import os
from datetime import datetime
from dateutil import relativedelta

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
    result['bnd'] = cm.get_bnd_data(params)
    result['data'] = cm.get_bnd_projects(params)
    result['rate'] = dict()
    cntrct_amount = cm.get_bnd_rates(params)
    for c in cntrct_amount:
        cntrct_sn = str(c['cntrct_sn'])
        if cntrct_sn not in result['rate']:
            result['rate'][cntrct_sn] = {"amount" : 0}
        result['rate'][cntrct_sn]["cntrct_amount"] = c['cntrct_amount']
    params['s_year'] = params['bnd_year']
    s12_account = cm.get_s12_account_list(params, s_dlivy_de=False)
    for s in s12_account:
        cntrct_sn = str(s['cntrct_sn'])
        amount = s['p_total']
        if cntrct_sn not in result['rate']:
            result['rate'][cntrct_sn] = {"cntrct_amount" : 0.0, "amount" : 0.0}
        result['rate'][cntrct_sn]["amount"] += amount
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
        delng_se_code = 'M' if tax['s_delng_se_code'] == 'S2' else ('S' if tax['s_delng_se_code'] == 'S4' else 'T')
        dlivy_de = tax['s_dlivy_de']
        amount = tax['amount']
        if cntrct_sn not in result['taxbill']:
            result['taxbill'][cntrct_sn] = {"M" : [], "S" : [], "T" : []}
        result['taxbill'][cntrct_sn][delng_se_code].append((dlivy_de, amount))

    rcppay = cm.get_i2_rcppay_list(params)
    result['rcppay'] = dict()
    for r in rcppay:
        cntrct_sn = str(r['cntrct_sn'])
        amount = r['amount']
        rcppay_se_code = 'M' if r['rcppay_se_code'] == 'I2' else ('S' if r['rcppay_se_code'] == 'I4' else 'T')
        if cntrct_sn not in result['rcppay']:
            result['rcppay'][cntrct_sn] = {"M" : 0, "S" : 0, "T" : 0}
        result['rcppay'][cntrct_sn][rcppay_se_code] = amount

    for cntrct_sn in result['account']:
        if cntrct_sn in result['taxbill']:
            result['account'][cntrct_sn]["max_row"] = max(len(result['account'][cntrct_sn]["M"]), len(result['account'][cntrct_sn]["S"]), len(result['taxbill'][cntrct_sn]["M"]), len(result['taxbill'][cntrct_sn]["T"]))
        else:
            result['account'][cntrct_sn]["max_row"] = max(len(result['account'][cntrct_sn]["M"]), len(result['account'][cntrct_sn]["S"]))


    return jsonify(result)

@bp.route('/month/ajax_get_month_plan', methods=['GET'])
def ajax_get_month_plan():
    params = request.args.to_dict()
    result = dict()
    result['contract'] = cm.get_month_contract_list(params)
    result['colored'] = cm.get_month_data(params)
    return jsonify(result)

@bp.route('/bcnc/ajax_get_month_sales', methods=['GET'])
def ajax_get_month_sales():
    params = request.args.to_dict()
    result = dict()

    result['contract'] = cm.get_bcnc_contract_list(params)

    taxbill = cm.get_s_taxbil_list(params)
    result['taxbill'] = dict()
    for tax in taxbill:
        cntrct_sn = str(tax['cntrct_sn'])
        s_dlivy_de = str(int(tax['s_dlivy_de']))
        amount = tax['total']
        if cntrct_sn not in result['taxbill']:
            result['taxbill'][cntrct_sn] = {str(_) : 0 for _ in range(1, 13)}
        result['taxbill'][cntrct_sn][s_dlivy_de] = amount

    s12_account = cm.get_s12_account_list(params)
    result['s12_account'] = dict()
    for s in s12_account:
        cntrct_sn = str(s['cntrct_sn'])
        s_dlivy_de = str(int(s['s_dlivy_de']))
        amount = s['p_total']
        if cntrct_sn not in result['s12_account']:
            result['s12_account'][cntrct_sn] = {str(_) : 0 for _ in range(1, 13)}
        result['s12_account'][cntrct_sn][s_dlivy_de] = amount

    s34_account = cm.get_s34_account_list(params)
    result['s34_account'] = dict()
    for s in s34_account:
        cntrct_sn = str(s['cntrct_sn'])
        s_dlivy_de = str(int(s['s_dlivy_de']))
        amount = s['s_total']
        if cntrct_sn not in result['s34_account']:
            result['s34_account'][cntrct_sn] = {str(_) : 0 for _ in range(1, 13)}
        result['s34_account'][cntrct_sn][s_dlivy_de] = amount

    outsrc_taxbill = cm.get_outsrc_taxbill_list(params)
    result['outsrc_taxbill'] = dict()
    for t in outsrc_taxbill:
        cntrct_sn = str(t['cntrct_sn'])
        s_dlivy_de = str(int(t['s_dlivy_de']))
        amount = t['total']
        if cntrct_sn not in result['outsrc_taxbill']:
            result['outsrc_taxbill'][cntrct_sn] = {str(_) : 0 for _ in range(1, 13)}
        result['outsrc_taxbill'][cntrct_sn][s_dlivy_de] = amount

    a_e_cost_list = cm.get_a_e_cost_list(params)
    result['a_cost'] = dict()
    for a in a_e_cost_list:
        cntrct_sn = str(a['cntrct_sn'])
        amount = a['amount']
        result['a_cost'][cntrct_sn] = amount

    result['bcnc_data'] = cm.get_bcnc_data(params)



    return jsonify(result)

@bp.route('/bcnc/ajax_set_bcnc_data', methods=['GET'])
def ajax_set_bcnc_data():
    params = request.args.to_dict()
    cm.set_bcnc_data(params)
    return jsonify({"status" : True, "message" : "??????????????? ?????????????????????."})

@bp.route('/bnd/ajax_set_bnd_data', methods=['GET'])
def ajax_set_bnd_data():
    params = request.args.to_dict()
    cm.set_bnd_data(params)
    return jsonify({"status" : True, "message" : "??????????????? ?????????????????????."})

@bp.route('/month/ajax_set_month_data', methods=['GET'])
def ajax_set_month_data():
    params = request.args.to_dict()
    cm.set_month_data(params)

    return jsonify({"status" : True, "message" : "??????????????? ?????????????????????."})

@bp.route('/memo/ajax_get_memo_list', methods=['GET'])
def memo_ajax_get_memo_list():
    params = request.args.to_dict()
    result = dict()
    result['memo_list'] = cm.get_memo_list(params)
    result['status'] = True
    return jsonify(result)


@bp.route('/memo/ajax_insert_memo', methods=['GET'])
def memo_ajax_insert_memo():
    params = request.args.to_dict()
    cm.insert_memo(params)
    return jsonify({"status": True, "message": "??????????????? ?????????????????????."})


@bp.route('/partner/ajax_get_partner_datatable', methods=['POST'])
def partner_ajax_get_partner_datatable():
    params = request.form.to_dict()
    result = cm.get_bcnc_datatable(params)
    result['status'] = True
    return jsonify(result)



@bp.route('/partner/ajax_get_partner', methods=['GET'])
def partner_ajax_get_partner():
    params = request.args.to_dict()
    result = dict()
    result['data'] = cm.get_bcnc(params)
    result['status'] = True
    return jsonify(result)

@bp.route('/partner/ajax_insert_partner', methods=['POST'])
def partner_ajax_insert_partner():
    params = request.form.to_dict()
    cm.insert_bcnc(params)
    return jsonify({"status": True, "message" : "??????????????? ?????????????????????."})
@bp.route('/partner/ajax_update_partner', methods=['POST'])
def partner_ajax_update_partner():
    params = request.form.to_dict()
    cm.update_bcnc(params)
    return jsonify({"status": True, "message" : "??????????????? ?????????????????????."})

@bp.route('/partner/ajax_delete_partner', methods=['POST'])
def partner_ajax_delete_partner():
    params = request.form.to_dict()
    cm.delete_bcnc(params)
    return jsonify({"status": True, "message" : "??????????????? ?????????????????????."})

@bp.route('/money/ajax_get_money_data', methods=['GET'])
def money_ajax_get_money_data():
    params = request.args.to_dict()
    result = dict()
    result['contract'] = cm.get_money_data(params)
    return jsonify(result)

@bp.route('/cowork/ajax_get_cowork_data', methods=['GET'])
def cowork_ajax_get_cowork_data():
    params = request.args.to_dict()
    result = dict()
    result['contract'] = cm.get_cowork_data(params)
    # result['contract'] = cm.get_cowork_data(params)
    # outsrcList = dict()
    # for contract in result['contract']:
    #     project_params = {"s_cntrct_sn" : contract['cntrct_sn'], "s_prjct_sn" : contract['prjct_sn']}
    #     outsrcList[contract['cntrct_sn']] = prj.get_outsrc_report_list(project_params)
    # result['outsrcList'] = outsrcList
    return jsonify(result)

@bp.route('/overpay/ajax_get_overpay', methods=['GET'])
def overpay_ajax_get_overpay():
    params = request.args.to_dict()
    result = dict()
    result['contract'] = cm.get_bcnc_contract_list(params)

    taxbill = cm.get_s_taxbil_list(params)
    result['taxbill'] = dict()
    for tax in taxbill:
        cntrct_sn = str(tax['cntrct_sn'])
        s_dlivy_de = str(int(tax['s_dlivy_de']))
        amount = tax['total']
        if cntrct_sn not in result['taxbill']:
            result['taxbill'][cntrct_sn] = {str(_) : 0 for _ in range(1, 13)}
        result['taxbill'][cntrct_sn][s_dlivy_de] = amount

    s12_account = cm.get_s12_account_list(params)
    result['s12_account'] = dict()
    for s in s12_account:
        cntrct_sn = str(s['cntrct_sn'])
        s_dlivy_de = str(int(s['s_dlivy_de']))
        amount = s['p_total']
        if cntrct_sn not in result['s12_account']:
            result['s12_account'][cntrct_sn] = {str(_) : 0 for _ in range(1, 13)}
        result['s12_account'][cntrct_sn][s_dlivy_de] = amount

    s34_account = cm.get_s34_account_list(params)
    result['s34_account'] = dict()
    for s in s34_account:
        cntrct_sn = str(s['cntrct_sn'])
        s_dlivy_de = str(int(s['s_dlivy_de']))
        amount = s['s_total']
        if cntrct_sn not in result['s34_account']:
            result['s34_account'][cntrct_sn] = {str(_) : 0 for _ in range(1, 13)}
        result['s34_account'][cntrct_sn][s_dlivy_de] = amount

    outsrc_taxbill = cm.get_outsrc_taxbill_list(params)
    result['outsrc_taxbill'] = dict()
    for t in outsrc_taxbill:
        cntrct_sn = str(t['cntrct_sn'])
        s_dlivy_de = str(int(t['s_dlivy_de']))
        amount = t['total']
        if cntrct_sn not in result['outsrc_taxbill']:
            result['outsrc_taxbill'][cntrct_sn] = {str(_) : 0 for _ in range(1, 13)}
        result['outsrc_taxbill'][cntrct_sn][s_dlivy_de] = amount

    a_e_cost_list = cm.get_a_e_cost_list(params)
    result['a_cost'] = dict()
    for a in a_e_cost_list:
        cntrct_sn = str(a['cntrct_sn'])
        amount = a['amount']
        result['a_cost'][cntrct_sn] = amount

    return jsonify(result)

@bp.route('/comp/ajax_get_comp', methods=['GET'])
def ajax_get_comp():
    params = request.args.to_dict()
    result = dict()
    result['row1'] = cm.get_first(params)
    result['row2'] = cm.get_kisung_suju(params)
    result['row3'] = cm.get_kisung_sales(params)
    result['row4'] = cm.get_kisung_va(params)
    result['row5'] = cm.get_last(params)
    result['goal'] = cm.get_goal(params)
    result['status'] = True
    return jsonify(result)

@bp.route('/extra/ajax_get_extra', methods=['GET'])
def extra_ajax_get_extra():
    params = request.args.to_dict()
    result = dict()
    result['data'] = cm.get_extra(params)
    result['status'] = True
    return jsonify(result)

@bp.route('/extra/ajax_insert_extra', methods=['GET'])
def extra_ajax_insert_extra():
    params = request.args.to_dict()
    cm.insert_extra(params)

    return jsonify({"status" : True, "message" : "??????????????? ?????????????????????."})

@bp.route('/five/ajax_get_five', methods=['GET'])
def five_ajax_get_five():
    params = request.args.to_dict()
    result = dict()
    result['contractStatusList'] = list()
    if "s_pxcond_mt" not in params:
        params['s_pxcond_mt'] = datetime.now().strftime("%Y-%m-%d")
    s_pxcond_mt = datetime.strptime(params["s_pxcond_mt"], "%Y-%m-%d")
    dept_codes = ['TS1', 'TS2', 'BI', 'ST']
    amt_ty_codes = [2, 3, 5]
    for i in range(5):
        params['s_pxcond_mt'] = (s_pxcond_mt - relativedelta.relativedelta(months=i)).strftime("%Y-%m-%d")
        row = cp.get_completed_summary(params)
        data = dict()
        for r in row:
            if r['amt_ty_code'] not in data:
                data[r['amt_ty_code']] = {d:None for d in dept_codes}
            if r['dept_code'] in data[r['amt_ty_code']]:
                data[r['amt_ty_code']][r['dept_code']] = r
        for r in data:
            for d in data[r]:
                if data[r][d] is not None:
                    data[r][d]['dept_count'] = len(data[r])
        result['contractStatusList'].append(data)
    result['dept_code_order'] = dept_codes
    result['amt_ty_code_order'] = amt_ty_codes
    result['s_pxcond_mt'] = params['s_pxcond_mt']
    result['status'] = True
    return jsonify(result)


