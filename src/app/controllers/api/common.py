from flask import Blueprint, g, current_app, render_template, redirect, request, make_response, jsonify, send_file, Response, url_for, session
from .services import common_service as cm
from .services import completed_service as cp
from .services import project_service as prj

from app.connectors import DB
from app.helpers import session_helper
from .services import set_menu
import json
import os
from datetime import datetime
from dateutil import relativedelta
from pytz import timezone
bp = Blueprint('api_common', __name__, url_prefix='/api')
CHUNK_SIZE = 800000
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

@bp.route('/author/ajax_get_authorMenu_list', methods=['GET'])
def ajax_get_authorMenu_list():
    try:
        params = request.args.to_dict()
        result = dict()
        result['list'] = cm.get_authorMenu_list(params)
        result['status'] = True
        return jsonify(result)
    except Exception as e:
        print(e)
        return make_response(str(e), 500)

@bp.route('/author/ajax_update_authorMenu', methods=['POST'])
def ajax_update_authorMenu():
    try:
        params = request.form.to_dict()
        cm.update_authorMenu(params)
        return jsonify({"status": True, "message": "성공적으로 추가되었습니다."})
    except Exception as e:
        print(e)
        return make_response(str(e), 500)


@bp.route('/bbs/ajax_get_bbs_datatable', methods=['POST'])
def bbs_ajax_get_bbs_datatable():
    try:
        params = request.form.to_dict()
        result = cm.get_bbs_datatable(params)
        return jsonify(result)
    except Exception as e:
        print(e)
        return make_response(str(e), 500)


@bp.route('/code/ajax_get_groupCode_datatable', methods=['POST'])
def code_ajax_get_groupCode_datatable():
    try:
        params = request.form.to_dict()
        result = cm.get_groupCode_datatable(params)
        return jsonify(result)
    except Exception as e:
        print(e)
        return make_response(str(e), 500)

@bp.route('/code/ajax_get_code_datatable', methods=['POST'])
def code_ajax_get_code_datatable():
    try:
        params = request.form.to_dict()
        result = cm.get_code_datatable(params)
        return jsonify(result)
    except Exception as e:
        print(e)
        return make_response(str(e), 500)

@bp.route('/code/ajax_get_code', methods=['GET'])
def code_ajax_get_code():
    try:
        params = request.args.to_dict()
        result = cm.get_code(params)
        return jsonify(result)
    except Exception as e:
        print(e)
        return make_response(str(e), 500)

@bp.route('/code/ajax_insert_code', methods=['POST'])
def code_ajax_insert_code():
    try:
        params = request.form.to_dict()
        cm.insert_code(params)
        return jsonify({"status" : True, "message" : "성공적으로 추가되었습니다."})
    except Exception as e:
        print(e)
        return make_response(str(e), 500)

@bp.route('/code/ajax_update_code', methods=['POST'])
def code_ajax_update_code():
    try:
        params = request.form.to_dict()
        cm.update_code(params)
        return jsonify({"status" : True, "message" : "성공적으로 변경되었습니다."})
    except Exception as e:
        print(e)
        return make_response(str(e), 500)

@bp.route('/code/ajax_delete_code', methods=['POST'])
def code_ajax_delete_code():
    try:
        params = request.form.to_dict()
        cm.delete_code(params)
        return jsonify({"status" : True, "message" : "성공적으로 삭제되었습니다."})
    except Exception as e:
        print(e)
        return make_response(str(e), 500)



@bp.route('/bnd/ajax_get_bcnc_list', methods=['GET'])
def ajax_get_bcnc_list():
    try:
        params = request.args.to_dict()
        result = dict()
        result['bData'] = cm.get_bcncs()
        result['cData'] = cm.get_chrgs()
        result['dData'] = cm.get_c_chrgs()
        result['status'] = True
        return jsonify(result)
    except Exception as e:
        print(e)
        return make_response(str(e), 500)

@bp.route('/bnd/ajax_get_bnd_new', methods=['GET'])
def ajax_get_bnd_new():
    params = request.args.to_dict()
    for _t in ["m", "s"]:
        for _d in ["start", "end"]:
            if "{}_dlivy_de_{}".format(_t, _d) not in params:
                params["{}_dlivy_de_{}".format(_t, _d)] = ''

    for _t in ["m", "s", "t"]:
        for _d in ["start", "end"]:
            if "{}_pblict_de_{}".format(_t, _d) not in params:
                params["{}_pblict_de_{}".format(_t, _d)] = ''

    result = dict()
    result['color'] = cm.get_bnd_color(params)
    result['bnd'] = cm.get_bnd_data(params)
    result['data'] = cm.get_bnd_projects_new(params)

    return jsonify(result)


@bp.route('/bnd/ajax_get_bnd', methods=['GET'])
def ajax_get_bnd():
    try:
        params = request.args.to_dict()
        for _t in ["m", "s"]:
            for _d in ["start", "end"]:
                if "{}_dlivy_de_{}".format(_t, _d) not in params:
                    params["{}_dlivy_de_{}".format(_t, _d)] = ''

        for _t in ["m", "s", "t"]:
            for _d in ["start", "end"]:
                if "{}_pblict_de_{}".format(_t, _d) not in params:
                    params["{}_pblict_de_{}".format(_t, _d)] = ''

        result = dict()
        result['color'] = cm.get_bnd_color(params)
        result['bnd'] = cm.get_bnd_data(params)
        result['data'] = cm.get_bnd_projects(params)
        result['rate'] = dict()
        result['rcppay'] = dict()

        cntrct_amount = cm.get_bnd_rates(params)
        for c in cntrct_amount:
            cntrct_sn = str(c['cntrct_sn'])
            if cntrct_sn not in result['rate']:
                result['rate'][cntrct_sn] = {"amount" : 0}
            result['rate'][cntrct_sn]["cntrct_amount"] = c['cntrct_amount']
            if cntrct_sn not in result['rcppay']:
                result['rcppay'][cntrct_sn] = {"M" : 0, "S" : 0, "T" : 0}
            #     result['rcppay'][cntrct_sn][rcppay_se_code] = amount
            result['rcppay'][cntrct_sn]['T'] = c['cntrct_amount']
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
            delng_ty_code = 'M' if acc['p_delng_ty_code'] in ('61', '62') else 'S'
            dlivy_de = acc['s_dlivy_de']
            if cntrct_sn not in result['account']:
                result['account'][cntrct_sn] = {"M" : [], "S" : []}
            result['account'][cntrct_sn][delng_ty_code].append(dlivy_de)

        taxbill = cm.get_s6_taxbill_list(params)
        result['taxbill'] = dict()
        for tax in taxbill:
            cntrct_sn = str(tax['cntrct_sn'])
            delng_se_code = 'M' if tax['s_delng_se_code'] == 'S2' else ('S' if tax['s_delng_se_code'] == 'S4' else 'T')
            if delng_se_code == 'T' and tax['prjct_ty_code'] == 'BD':
                continue
            dlivy_de = tax['s_dlivy_de']
            amount = tax['amount']
            if cntrct_sn not in result['taxbill']:
                result['taxbill'][cntrct_sn] = {"M" : [], "S" : [], "T" : []}
            result['taxbill'][cntrct_sn][delng_se_code].append((dlivy_de, amount))

        bd_taxbill = cm.get_bd_taxbill_list(params)
        for tax in bd_taxbill:

            cntrct_sn = str(tax['cntrct_sn'])
            delng_se_code = 'T'
            dlivy_de = tax['s_dlivy_de']
            amount = tax['amount']
            if cntrct_sn not in result['taxbill']:
                result['taxbill'][cntrct_sn] = {"M" : [], "S" : [], "T" : []}
            if cntrct_sn not in result['account']:
                result['account'][cntrct_sn] = {"M" : [], "S" : []}
            result['taxbill'][cntrct_sn][delng_se_code].append((dlivy_de, amount))


        # rcppay = cm.get_i2_rcppay_list(params)
        # for r in rcppay:
        #     cntrct_sn = str(r['cntrct_sn'])
        #     amount = r['amount']
        #     rcppay_se_code = 'M' if r['rcppay_se_code'] == 'I2' else ('S' if r['rcppay_se_code'] == 'I4' else 'T')
        #     if cntrct_sn not in result['rcppay']:
        #         result['rcppay'][cntrct_sn] = {"M" : 0, "S" : 0, "T" : 0}
        #     result['rcppay'][cntrct_sn][rcppay_se_code] = amount

        dscnt_total = cm.get_add_dscnt_list(params)
        for d in dscnt_total:
            cntrct_sn = str(d['cntrct_sn'])
            amount = d['amount']
            delng_ty_code = 'M' if d['p_delng_ty_code'] in ('61', '62') else 'S'
            if cntrct_sn not in result['rcppay']:
                result['rcppay'][cntrct_sn] = {"M" : 0, "S" : 0, "T" : 0}
            result['rcppay'][cntrct_sn][delng_ty_code] = amount

        for cntrct_sn in result['account']:
            if cntrct_sn in result['taxbill']:
                result['account'][cntrct_sn]["max_row"] = max(len(result['account'][cntrct_sn]["M"]), len(result['account'][cntrct_sn]["S"]), len(result['taxbill'][cntrct_sn]["M"]), len(result['taxbill'][cntrct_sn]["T"]))
            else:
                result['account'][cntrct_sn]["max_row"] = max(len(result['account'][cntrct_sn]["M"]), len(result['account'][cntrct_sn]["S"]))


        out_cntrct_sns = []
        for r in result['data']:
            cntrct_sn = str(r['cntrct_sn'])

            for t in ["m", "s"]:
                if params["{}_dlivy_de_start".format(t)] != '' and params["{}_dlivy_de_end".format(t)] != '':
                    st_date = datetime.strptime("20{}-01".format(params["{}_dlivy_de_start".format(t)]), "%Y-%m-%d")
                    ed_date = datetime.strptime("20{}-01".format(params["{}_dlivy_de_end".format(t)]), "%Y-%m-%d")
                    try:
                        is_alright = False
                        m_list = result['account'][cntrct_sn][t.upper()]
                        for m in m_list:
                            m_date = datetime.strptime("20{}-01".format(m.replace("/", "-")), "%Y-%m-%d")
                            if m_date >= st_date and m_date <= ed_date:
                                is_alright = True
                            else:
                                continue
                        if not is_alright:
                            out_cntrct_sns.append(cntrct_sn)
                    except:
                        out_cntrct_sns.append(cntrct_sn)
                elif params["{}_dlivy_de_start".format(t)]:
                    st_date = datetime.strptime("20{}-01".format(params["{}_dlivy_de_start".format(t)]), "%Y-%m-%d")
                    try:
                        is_alright = False
                        m_list = result['account'][cntrct_sn][t.upper()]
                        for m in m_list:
                            m_date = datetime.strptime("20{}-01".format(m.replace("/", "-")), "%Y-%m-%d")
                            if m_date >= st_date:
                                is_alright = True
                            else:
                                continue

                        if not is_alright:
                            out_cntrct_sns.append(cntrct_sn)
                    except Exception as e:
                        out_cntrct_sns.append(cntrct_sn)
                elif params["{}_dlivy_de_end".format(t)] != '':
                    ed_date = datetime.strptime("20{}-01".format(params["{}_dlivy_de_end".format(t)]), "%Y-%m-%d")
                    try:
                        is_alright = False
                        m_list = result['account'][cntrct_sn][t.upper()]
                        for m in m_list:
                            m_date = datetime.strptime("20{}-01".format(m.replace("/", "-")), "%Y-%m-%d")
                            if m_date <= ed_date:
                                is_alright = True
                            else:
                                continue
                        if not is_alright:
                            out_cntrct_sns.append(cntrct_sn)
                    except:
                        out_cntrct_sns.append(cntrct_sn)

            for t in ["m", "s", "t"]:
                if params["{}_pblict_de_start".format(t)] != '' and params["{}_pblict_de_end".format(t)] != '':
                    st_date = datetime.strptime("20{}-01".format(params["{}_pblict_de_start".format(t)]), "%Y-%m-%d")
                    ed_date = datetime.strptime("20{}-01".format(params["{}_pblict_de_end".format(t)]), "%Y-%m-%d")
                    try:
                        is_alright = False
                        m_list = result['taxbill'][cntrct_sn][t.upper()]
                        for m in m_list:
                            m_date = datetime.strptime("20{}-01".format(m[0].replace("/", "-")), "%Y-%m-%d")
                            if m_date >= st_date and m_date <= ed_date:
                                is_alright = True
                            else:
                                continue
                        if not is_alright:
                            out_cntrct_sns.append(cntrct_sn)
                    except Exception as e:
                        out_cntrct_sns.append(cntrct_sn)
                elif params["{}_pblict_de_start".format(t)] != '':
                    st_date = datetime.strptime("20{}-01".format(params["{}_pblict_de_start".format(t)]), "%Y-%m-%d")
                    try:
                        is_alright = False
                        m_list = result['taxbill'][cntrct_sn][t.upper()]
                        for m in m_list:
                            m_date = datetime.strptime("20{}-01".format(m[0].replace("/", "-")), "%Y-%m-%d")
                            if m_date >= st_date:
                                is_alright = True
                            else:
                                continue
                        if not is_alright:
                            out_cntrct_sns.append(cntrct_sn)
                    except Exception as e:
                        out_cntrct_sns.append(cntrct_sn)
                elif params["{}_pblict_de_end".format(t)] != '':
                    ed_date = datetime.strptime("20{}-01".format(params["{}_pblict_de_end".format(t)]), "%Y-%m-%d")
                    try:
                        is_alright = False
                        m_list = result['taxbill'][cntrct_sn][t.upper()]
                        for m in m_list:
                            m_date = datetime.strptime("20{}-01".format(m[0].replace("/", "-")), "%Y-%m-%d")
                            if m_date <= ed_date:
                                is_alright = True
                            else:
                                continue
                        if not is_alright:
                            out_cntrct_sns.append(cntrct_sn)
                    except Exception as e:
                        out_cntrct_sns.append(cntrct_sn)

        result['data'] = [r for r in result['data'] if str(r['cntrct_sn']) not in out_cntrct_sns]
        return jsonify(result)
    except Exception as e:
        print(e)
        return make_response(str(e), 500)

@bp.route('/month/ajax_get_month_plan', methods=['GET'])
def ajax_get_month_plan():
    try:
        params = request.args.to_dict()
        result = dict()
        co_st_list = cm.get_month_co_contract_list(params)
        co_st = dict()
        for co in co_st_list:
            if co['cntrct_sn'] not in co_st:
                co_st[co['cntrct_sn']] = list()
            co_st[co['cntrct_sn']].append(co)
        result['contract'] = cm.get_month_contract_list(params)
        extra_contract = list()
        for r in result['contract']:
            if r['cntrct_sn'] in co_st:
                cntrct_amount = r['cntrct_amount']
                tot = r['tot']
                for co in co_st[r['cntrct_sn']]:
                    co['cntrct_amount'] = cntrct_amount * co['rate'] / 100.0
                    co['tot'] = tot * co['rate'] / 100.0
                    for i in range(1, 13):
                        co["{}m".format(i)] = "" if r["{}m".format(i)] == "" else (r["{}m".format(i)] * co['rate'] / 100.0)
                    extra_contract.append(co)
                for co in co_st[r['cntrct_sn']]:
                    for i in range(1, 13):
                        if co["{}m".format(i)] != "":
                            r["{}m".format(i)] -= co["{}m".format(i)]
                    r['cntrct_amount'] -= co['cntrct_amount']
                    r['tot'] -= co['tot']
        result['contract'] += extra_contract
        result['contract'] = list(sorted(result['contract'], key=lambda r: (r['code_ordr'], r['dept_nm'], r['ofcps_code'], r['bcnc_nm'], r['spt_nm'])))

        result['colored'] = cm.get_month_data(params)
        return jsonify(result)
    except Exception as e:
        print(e)
        return make_response(str(e), 500)

@bp.route('/bcnc/ajax_get_month_sales', methods=['GET'])
def ajax_get_month_sales():
    try:
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

        result['goal'] = cm.get_bcnc_goal(params)

        return jsonify(result)
    except Exception as e:
        print(e)
        return make_response(str(e), 500)

@bp.route('/bcnc/ajax_set_bcnc_data', methods=['GET'])
def ajax_set_bcnc_data():
    try:
        params = request.args.to_dict()
        cm.set_bcnc_data(params)
        return jsonify({"status" : True, "message" : "성공적으로 변경되었습니다."})
    except Exception as e:
        print(e)
        return make_response(str(e), 500)

@bp.route('/bnd/ajax_set_bnd_data', methods=['GET'])
def ajax_set_bnd_data():
    try:
        params = request.args.to_dict()
        cm.set_bnd_data(params)
        return jsonify({"status" : True, "message" : "성공적으로 변경되었습니다."})
    except Exception as e:
        print(e)
        return make_response(str(e), 500)

@bp.route('/money/ajax_set_money_data', methods=['GET'])
def ajax_set_money_data():
    try:
        params = request.args.to_dict()
        cm.set_money_data(params)
        return jsonify({"status" : True, "message" : "성공적으로 변경되었습니다."})
    except Exception as e:
        print(e)
        return make_response(str(e), 500)

@bp.route('/bnd/ajax_update_contract_rate', methods=['GET'])
def ajax_update_contract_rate():
    try:
        params = request.args.to_dict()
        cm.ajax_update_contract_rate(params)
        return jsonify({"status" : True, "message" : "성공적으로 변경되었습니다."})
    except Exception as e:
        print(e)
        return make_response(str(e), 500)

@bp.route('/month/ajax_set_month_data', methods=['GET'])
def ajax_set_month_data():
    try:
        params = request.args.to_dict()
        cm.set_month_data(params)
        return jsonify({"status" : True, "message" : "성공적으로 변경되었습니다."})
    except Exception as e:
        print(e)
        return make_response(str(e), 500)

@bp.route('/memo/ajax_get_memo_list', methods=['GET'])
def memo_ajax_get_memo_list():
    try:
        params = request.args.to_dict()
        result = dict()
        result['memo_list'] = cm.get_memo_list(params)
        result['status'] = True
        return jsonify(result)
    except Exception as e:
        print(e)
        return make_response(str(e), 500)


@bp.route('/memo/ajax_insert_memo', methods=['GET'])
def memo_ajax_insert_memo():
    try:
        params = request.args.to_dict()
        cm.insert_memo(params)
        return jsonify({"status": True, "message": "성공적으로 추가되었습니다."})
    except Exception as e:
        print(e)
        return make_response(str(e), 500)


@bp.route('/partner/ajax_get_partner_datatable', methods=['POST'])
def partner_ajax_get_partner_datatable():
    try:
        params = request.form.to_dict()
        result = cm.get_bcnc_datatable(params)
        result['status'] = True
        return jsonify(result)
    except Exception as e:
        print(e)
        return make_response(str(e), 500)



@bp.route('/partner/ajax_get_partner', methods=['GET'])
def partner_ajax_get_partner():
    try:
        params = request.args.to_dict()
        result = dict()
        result['data'] = cm.get_bcnc(params)
        result['status'] = True
        return jsonify(result)
    except Exception as e:
        print(e)
        return make_response(str(e), 500)

@bp.route('/partner/ajax_insert_partner', methods=['POST'])
def partner_ajax_insert_partner():
    try:
        params = request.form.to_dict()
        cm.insert_bcnc(params)
        return jsonify({"status": True, "message" : "성공적으로 추가되었습니다."})
    except Exception as e:
        print(e)
        return make_response(str(e), 500)


@bp.route('/partner/ajax_update_partner', methods=['POST'])
def partner_ajax_update_partner():
    try:
        params = request.form.to_dict()
        cm.update_bcnc(params)
        return jsonify({"status": True, "message" : "성공적으로 수정되었습니다."})
    except Exception as e:
        print(e)
        return make_response(str(e), 500)

@bp.route('/partner/ajax_delete_partner', methods=['POST'])
def partner_ajax_delete_partner():
    try:
        params = request.form.to_dict()
        cm.delete_bcnc(params)
        return jsonify({"status": True, "message" : "성공적으로 삭제되었습니다."})
    except Exception as e:
        print(e)
        return make_response(str(e), 500)

@bp.route('/money/ajax_get_money_data', methods=['GET'])
def money_ajax_get_money_data():
    try:
        params = request.args.to_dict()
        result = dict()
        contract = cm.get_money_data(params)
        pay = cm.get_pay_data(params)
        result['contract'] = list()
        for _ in range(max(len(contract), len(pay))):
            row = dict()
            if _ < len(contract):
                row['S'] = contract[_]
            if _ < len(pay):
                row['T'] = pay[_]
            result['contract'].append(row)
        # result['contract'] = cm.get_money_data(params)
        params['money_year'] = "-".join(params['s_mt'].split("-")[:2])
        result['money'] = cm.get_money_data_input(params)
        # result['pay'] = cm.get_pay_data(params)
        return jsonify(result)
    except Exception as e:
        print(e)
        return make_response(str(e), 500)

@bp.route('/cowork/ajax_get_cowork_data', methods=['GET'])
def cowork_ajax_get_cowork_data():
    try:
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
    except Exception as e:
        print(e)
        return make_response(str(e), 500)

@bp.route('/overpay/ajax_get_overpay', methods=['GET'])
def overpay_ajax_get_overpay():
    try:
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

        s12_account = cm.get_s12_account_detail_list(params)
        result['s12_account'] = dict()
        for s in s12_account:
            cntrct_sn = str(s['cntrct_sn'])
            s_dlivy_de = str(int(s['s_dlivy_de']))
            amount = s['p_total']
            if cntrct_sn not in result['s12_account']:
                result['s12_account'][cntrct_sn] = {"74" : {str(_) : 0 for _ in range(1, 13)}, "79" : {str(_) : 0 for _ in range(1, 13)}, "100":{str(_) : 0 for _ in range(1, 13)}}
            if s['bcnc_sn'] in (74, 79, 100):
                result['s12_account'][cntrct_sn][str(s['bcnc_sn'])][s_dlivy_de] += amount
            else:
                result['s12_account'][cntrct_sn]["100"][s_dlivy_de] += amount

        s34_account = cm.get_s34_account_list(params)
        result['s34_account'] = dict()
        for s in s34_account:
            cntrct_sn = str(s['cntrct_sn'])
            s_dlivy_de = str(int(s['s_dlivy_de']))
            amount = s['s_total']
            if cntrct_sn not in result['s34_account']:
                result['s34_account'][cntrct_sn] = {str(_) : 0 for _ in range(1, 13)}
            result['s34_account'][cntrct_sn][s_dlivy_de] = amount

        outsrc_taxbill = cm.get_outsrc_taxbill_detail_list(params)
        result['outsrc_taxbill'] = dict()
        for t in outsrc_taxbill:
            cntrct_sn = str(t['cntrct_sn'])
            s_dlivy_de = str(int(t['s_dlivy_de']))
            amount = t['total']
            if cntrct_sn not in result['outsrc_taxbill']:
                result['outsrc_taxbill'][cntrct_sn] = [{str(_) : 0 for _ in range(1, 13)}, {str(_) : 0 for _ in range(1, 13)}]
            result['outsrc_taxbill'][cntrct_sn][t['bcnc_sn']][s_dlivy_de] += amount

        a_e_cost_list = cm.get_a_e_cost_list(params)
        result['a_cost'] = dict()
        for a in a_e_cost_list:
            cntrct_sn = str(a['cntrct_sn'])
            amount = a['amount']
            result['a_cost'][cntrct_sn] = amount

        return jsonify(result)
    except Exception as e:
        print(e)
        return make_response(str(e), 500)

@bp.route('/comp/ajax_get_comp', methods=['GET'])
def ajax_get_comp():
    try:
        params = request.args.to_dict()
        result = dict()
        result['row1'] = cm.get_first(params)
        result['row2'] = cm.get_kisung_suju(params)
        result['row3'] = cm.get_kisung_sales(params)
        result['row4'] = cm.get_kisung_va(params)
        result['row5'] = cm.get_last(params)
        result['goal'] = cm.get_goal(params)

        extra_goal = cm.get_goal_extra(params)
        extra_goal_dict = dict()
        for e in extra_goal:
            if e['dept_code'] not in extra_goal_dict:
                extra_goal_dict[e['dept_code']] = dict()
            extra_goal_dict[e['dept_code']][e['amt_ty_code']] = e

        result['extra_goal'] = list()
        done = []
        for e in extra_goal:
            if e['dept_code'] not in done:
                result['extra_goal'].append(extra_goal_dict[e['dept_code']])
                done.append(e['dept_code'])
        print(result['extra_goal'])
        result['status'] = True
        return jsonify(result)
    except Exception as e:
        print(e)
        return make_response(str(e), 500)

@bp.route('/extra/ajax_get_extra', methods=['GET'])
def extra_ajax_get_extra():
    try:
        params = request.args.to_dict()
        result = dict()
        result['data'] = cm.get_extra(params)
        result['status'] = True
        return jsonify(result)
    except Exception as e:
        print(e)
        return make_response(str(e), 500)

@bp.route('/extra/ajax_insert_extra', methods=['GET'])
def extra_ajax_insert_extra():
    try:
        params = request.args.to_dict()
        cm.insert_extra(params)

        return jsonify({"status" : True, "message" : "성공적으로 추가되었습니다."})
    except Exception as e:
        print(e)
        return make_response(str(e), 500)

@bp.route('/five/ajax_get_five', methods=['GET'])
def five_ajax_get_five():
    try:
        params = request.args.to_dict()
        result = dict()
        result['contractStatusList'] = list()
        if "s_pxcond_mt" not in params:
            params['s_pxcond_mt'] = datetime.now(timezone('Asia/Seoul')).strftime("%Y-12-31")
        else:
            params['s_pxcond_mt'] = datetime.strptime(params["s_pxcond_mt"], "%Y-%m-%d").strftime("%Y-12-31")
        s_pxcond_mt = datetime.strptime(params["s_pxcond_mt"], "%Y-%m-%d")
        dept_codes = ['ST', 'TS1', 'TS2', 'BI']
        amt_ty_codes = [2, 3, 5]
        years = []
        for i in range(4, -1, -1):
            params['s_pxcond_mt'] = (s_pxcond_mt - relativedelta.relativedelta(years=i)).strftime("%Y-%m-%d")
            years.append(params['s_pxcond_mt'].split("-")[0])
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
        result['amt_ty_nm'] = {"2" : "수주", "3": "매출", "5" : "VA"}
        result['dept_nm'] = {"TS1" : "공조1", "TS2": "공조2", "BI" : "빌트인", "ST" : "영업"}
        result['s_pxcond_mt'] = params['s_pxcond_mt']
        result['status'] = True
        result['years'] = years
        return jsonify(result)
    except Exception as e:
        print(e)
        return make_response(str(e), 500)


@bp.route('/vacation/insert_vacation', methods=['POST'])
def insert_vacation():
    try:
        params = request.get_json()
        cm.insert_vacation(params)
        return jsonify({"status" : True, "message" : "성공적으로 추가되었습니다."})
    except Exception as e:
        print(e)
        return make_response(str(e), 500)

@bp.route('/vacation/insert_vacation_out', methods=['POST'])
def insert_vacation_out():
    try:
        params = request.get_json()
        cm.insert_vacation_out(params, 8)
        return jsonify({"status" : True, "message" : "성공적으로 추가되었습니다."})
    except Exception as e:
        print(e)
        return make_response(str(e), 500)

@bp.route('/vacation/insert_vacation_out_go', methods=['POST'])
def insert_vacation_out_go():
    try:
        params = request.get_json()
        cm.insert_vacation_out(params, 9)
        return jsonify({"status" : True, "message" : "성공적으로 추가되었습니다."})
    except Exception as e:
        print(e)
        return make_response(str(e), 500)

@bp.route('/common/do_nothing', methods=['POST'])
def do_nothing():
    return jsonify({"status" : True, "message" : "성공적으로 추가되었습니다."})

@bp.route('/common/ajax_get_blueprint', methods=['GET'])
def ajax_get_blueprint():
    try:
        params = request.args.to_dict()
        result = dict()
        result['data'] = cm.get_blueprint(params)
        params['stdyy'] = params['stdyy'].split("-")[0]
        result['goal'] = cm.get_blueprint_goal(params)
        result['sum'] = cm.get_blueprint_total(params)
        result['total'] = cm.get_blueprint_year_total(params)
        return jsonify(result)
    except Exception as e:
        print(e)
        return make_response(str(e), 500)

@bp.route('/common/insert_blueprint', methods=['GET'])
def insert_blueprint():
    try:
        params = request.args.to_dict()
        result = cm.insert_blueprint(params)
        return jsonify(result)
    except Exception as e:
        print(e)
        return make_response(str(e), 500)

@bp.route('/common/insert_blueprint_goal', methods=['GET'])
def insert_blueprint_goal():
    try:
        params = request.args.to_dict()
        result = cm.insert_blueprint_goal(params)
        return jsonify(result)
    except Exception as e:
        print(e)
        return make_response(str(e), 500)

@bp.route('/common/set_reserve_data', methods=['GET'])
def set_reserve_data():
    try:
        params = request.args.to_dict()
        cm.set_reserve_data(params)
        return jsonify({"status" : True, "message" : "성공적으로 입력되었습니다."})
    except Exception as e:
        print(e)
        return make_response(str(e), 500)

@bp.route('/common/update_blueprint', methods=['GET'])
def update_blueprint():
    try:
        params = request.args.to_dict()
        result = cm.update_blueprint(params)
        return jsonify(result)
    except Exception as e:
        print(e)
        return make_response(str(e), 500)

@bp.route('/common/delete_blueprint', methods=['GET'])
def delete_blueprint():
    try:
        params = request.args.to_dict()
        result = cm.delete_blueprint(params)
        return jsonify(result)
    except Exception as e:
        print(e)
        return make_response(str(e), 500)

@bp.route('/research/ajax_get_research', methods=['GET'])
def ajax_get_research():
    try:
        params = request.args.to_dict()
        result = dict()
        result['data'] = cm.get_research(params)
        result['status'] = True
        return jsonify(result)
    except Exception as e:
        print(e)
        return make_response(str(e), 500)

@bp.route('/research/ajax_insert_research', methods=['GET'])
def ajax_insert_research():
    try:
        params = request.args.to_dict()
        cm.insert_research(params)
        return jsonify({"status" : True, "message" : "성공적으로 입력되었습니다."})
    except Exception as e:
        print(e)
        return make_response(str(e), 500)

@bp.route('/common/get_upload_file_id', methods=['POST'])
def get_upload_file_id():
    try:
        origin_filename = request.form.get("origin_filename")
        if origin_filename is None:
            origin_filename = ""
        ext = request.form.get("ext")
        order = request.form.get("order")
        now = datetime.now(timezone('Asia/Seoul')).strftime("%Y%m%d%H%M%S")
        folder = request.form.get("folder")
        os.makedirs("app/static/files/", exist_ok=True)
        if folder:
            os.makedirs("app/static/files/{}/".format(folder), exist_ok=True)
            filename = "{}/{}_{}.{}".format(folder, now, order, ext)
        else:
            filename = "{}_{}.{}".format(now, order, ext)
        file_sn = cm.insert_file(filename)
        return jsonify({"filename": filename, "filesize": CHUNK_SIZE, "file_sn" : file_sn, "order" : order, "origin_filename" : origin_filename})
    except Exception as e:
        print(e)
        return make_response(str(e), 500)

@bp.route('/common/chunk_upload', methods=['POST'])
def chunk_upload():
    try:
        file = request.files['file']
        filename = file.filename
        try:
            name, ext, idx = filename.split(".")
            save_path = "app/static/files/{}".format("{}.{}".format(name, ext))
            with open(save_path, 'ab') as f:
                f.seek(CHUNK_SIZE*int(idx))
                f.write(file.stream.read())
            return jsonify({"status" : True, "path" : "/static/files/{}".format("{}.{}".format(name, ext))})
        except Exception as e:
            return jsonify({"status" : False, "msg" : str(e)})

    except Exception as e:
        print(e)
        return make_response(str(e), 500)

@bp.route('/common/get_files_name', methods=['POST'])
def get_files_name():
    try:
        params = request.get_json()
        f_sns = params['f_sns']
        result = []
        for f_sn in f_sns:
            row = cm.get_file(f_sn)
            if row:
                result.append(row['file_path'])
        return jsonify(result)
    except Exception as e:
        print(e)
        return make_response(str(e), 500)

@bp.route('/reserve/get_reserve_list', methods=['GET'])
def get_reserve_list():
    try:
        params = request.args.to_dict()
        result = dict()
        result['data'] = prj.get_reserved_project_list(params)
        return jsonify(result)
    except Exception as e:
        print(e)
        return make_response(str(e), 500)

@bp.route('/reserve/ajax_get_outsrcs_by_contract', methods=['POST'])
def ajax_get_outsrcs_by_contract():
    try:
        params = request.form.to_dict()
        outsrcs = cm.get_outsrcs_by_contract(params)
        return jsonify(outsrcs)
    except Exception as e:
        print(e)
        return make_response(str(e), 500)

@bp.route('/common/ajax_get_finance', methods=['GET'])
def ajax_get_finance():
    try:
        params = request.args.to_dict()
        result = dict()
        result['data'] = cm.get_finance(params)
        return jsonify(result)
    except Exception as e:
        print(e)
        return make_response(str(e), 500)

@bp.route('/common/ajax_insert_finance', methods=['GET'])
def ajax_insert_finance():
    try:
        params = request.args.to_dict()
        cm.insert_finance(params)
        return jsonify({"status" : True, "message" : "성공적으로 입력되었습니다."})
    except Exception as e:
        print(e)
        return make_response(str(e), 500)

@bp.route('/common/reserve_out', methods=['GET'])
def reserve_out():
    try:
        params = request.args.to_dict()
        cm.reserve_out(params)
        return jsonify({"status" : True, "message" : "성공적으로 처리되었습니다."})
    except Exception as e:
        print(e)
        return make_response(str(e), 500)

@bp.route('/common/reserve_out_add', methods=['GET'])
def reserve_out_add():
    try:
        params = request.args.to_dict()
        cm.reserve_out_add(params)
        return jsonify({"status" : True, "message" : "성공적으로 처리되었습니다."})
    except Exception as e:
        print(e)
        return make_response(str(e), 500)

@bp.route('/common/insert_bbs', methods=['POST'])
def insert_bbs():
    try:
        params = request.form.to_dict()
        cm.insert_bbs(params)
        return jsonify({"status": True, "message" : "성공적으로 처리되었습니다."})
    except Exception as e:
        print(e)
        return make_response(str(e), 500)


@bp.route('/common/update_bbs', methods=['POST'])
def update_bbs():
    try:
        params = request.form.to_dict()
        cm.update_bbs(params)
        return jsonify({"status": True, "message" : "성공적으로 처리되었습니다."})
    except Exception as e:
        print(e)
        return make_response(str(e), 500)


@bp.route('/common/get_bbs_list', methods=['GET'])
def get_bbs_list():
    try:
        params = request.args.to_dict()
        result = cm.get_bbs_list(params)
        return jsonify(result)
    except Exception as e:
        print(e)
        return make_response(str(e), 500)

@bp.route('/common/get_bbs', methods=['GET'])
def get_bbs():
    try:
        params = request.args.to_dict()
        result = cm.get_bbs(params)
        return jsonify(result)
    except Exception as e:
        print(e)
        return make_response(str(e), 500)

@bp.route('/common/delete_bbs', methods=['GET'])
def delete_bbs():
    try:
        params = request.args.to_dict()
        result = cm.delete_bbs(params)
        return jsonify(result)
    except Exception as e:
        print(e)
        return make_response(str(e), 500)

@bp.route('/common/bnd_set_color', methods=['GET'])
def bnd_set_color():
    try:
        params = request.args.to_dict()
        cm.set_bnd_color(params)
        return jsonify({"status" : True, "message" : "성공적으로 입력되었습니다."})
    except Exception as e:
        print(e)
        return make_response(str(e), 500)
