from flask import Blueprint, g, current_app, render_template, redirect, request, make_response, jsonify, send_file, Response, url_for, session
from .services import project_service as prj
from .services import completed_service as cp
from .services import dashboard_service as db
from .services import approval_service as apvl
from app.connectors import DB
from app.helpers import session_helper
from .services import set_menu
import json
import os
from datetime import datetime

bp = Blueprint('api_dashboard', __name__, url_prefix='/api/dashboard')
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

@bp.route('/ajax_get_completed_sales', methods=['GET'])
def ajax_get_completed_sales():
    try:
        params = request.args.to_dict()
        if "s_pxcond_mt" not in params:
            params['s_pxcond_mt'] = datetime.now().strftime("%Y-%m-%d")
        result = dict()
        result['data'] = db.get_completed_sales(params)
        return jsonify(result)
    except Exception as e:
        print(e)
        return make_response(str(e), 500)

@bp.route('/ajax_get_completed_suju', methods=['GET'])
def ajax_get_completed_suju():
    try:
        params = request.args.to_dict()
        if "s_pxcond_mt" not in params:
            params['s_pxcond_mt'] = datetime.now().strftime("%Y-%m-%d")
        result = dict()
        result['data'] = db.get_completed_suju(params)
        return jsonify(result)
    except Exception as e:
        print(e)
        return make_response(str(e), 500)

@bp.route('/ajax_get_completed_suju_b', methods=['GET'])
def ajax_get_completed_suju_b():
    try:
        params = request.args.to_dict()
        if "s_pxcond_mt" not in params:
            params['s_pxcond_mt'] = datetime.now().strftime("%Y-%m-%d")
        result = dict()
        result['data'] = db.get_completed_suju_b(params)
        return jsonify(result)
    except Exception as e:
        print(e)
        return make_response(str(e), 500)


@bp.route('/ajax_get_completed_year_summary', methods=['GET'])
def ajax_get_completed_year_summary():
    try:
        params = request.args.to_dict()
        result = dict()
        result['data'] = list()
        result['data'].append(db.get_kisung_suju(params))
        result['data'].append(db.get_kisung_sales(params))
        result['data'].append(db.get_kisung_va(params))
        return jsonify(result)
    except Exception as e:
        print(e)
        return make_response(str(e), 500)


@bp.route('/ajax_get_completed_summary', methods=['GET'])
def ajax_get_completed_summary():
    try:
        params = request.args.to_dict()
        if "s_pxcond_mt" not in params:
            params['s_pxcond_mt'] = datetime.now().strftime("%Y-%m-%d")
        result = dict()
        result['contractStatusList'] = cp.get_completed_summary(params)
        result['s_pxcond_mt'] = params['s_pxcond_mt']
        result['status'] = True
        return jsonify(result)
    except Exception as e:
        print(e)
        return make_response(str(e), 500)


@bp.route('/ajax_get_biss_state', methods=['GET'])
def ajax_get_biss_state():
    try:
        params = request.args.to_dict()
        result = dict()

        result['list'] = db.get_biss_summery(params)
        result['data'] = db.get_all_member_project(params)
        result['status'] = True
        return jsonify(result)
    except Exception as e:
        print(e)
        return make_response(str(e), 500)

@bp.route('/ajax_get_sales_summary', methods=['GET'])
def ajax_get_sales_summary():
    try:
        params = request.args.to_dict()
        result = dict()

        result['list'] = db.get_sales_summery(params)
        result['one'] = db.get_sales_one_summery(params)
        result['status'] = True
        return jsonify(result)
    except Exception as e:
        print(e)
        return make_response(str(e), 500)


@bp.route('/ajax_get_projects_by_dept_member', methods=['GET'])
def ajax_get_projects_by_dept_member():
    try:
        params = request.args.to_dict()
        result = dict()
        result['data'] = db.get_projects_by_dept_member(params)
        return jsonify(result)
    except Exception as e:
        print(e)
        return make_response(str(e), 500)

@bp.route('/ajax_get_month_report', methods=['GET'])
def ajax_get_month_report():
    try:
        params = request.args.to_dict()
        if "s_pxcond_mt" not in params:
            params['s_pxcond_mt'] = datetime.now().strftime("%Y-%m-%d")
        result = dict()
        result['contractStatusList'] = cp.get_completed_summary(params)
        params["s_stdyy"], params["s_month"], _ = map(int, params['s_pxcond_mt'].split("-"))
        params["s_pxcond_m"] = "-".join(params['s_pxcond_mt'].split("-")[:2])
        contracts = db.get_goal_contract(params)
        result['contractList'] = dict()
        cntrct_sns = dict()
        for c in contracts:
            if c['dept_code'] not in result['contractList']:
                result['contractList'][c['dept_code']] = dict()
            if str(c['amt_ty_code']) not in result['contractList'][c['dept_code']]:
                result['contractList'][c['dept_code']][str(c['amt_ty_code'])] = list()
            result['contractList'][c['dept_code']][str(c['amt_ty_code'])].append(c)
            cntrct_sns[(c['dept_code'], c['amt_ty_code'], c['cntrct_sn'])] = 1

        # 직접추가한 현장
        extra_contracts = db.get_extra_goal_contract(params)
        for c in extra_contracts:
            if (c['dept_code'], c['amt_ty_code'], c['cntrct_sn']) not in cntrct_sns:
                if c['dept_code'] not in result['contractList']:
                    result['contractList'][c['dept_code']] = dict()
                if str(c['amt_ty_code']) not in result['contractList'][c['dept_code']]:
                    result['contractList'][c['dept_code']][str(c['amt_ty_code'])] = list()
                result['contractList'][c['dept_code']][str(c['amt_ty_code'])].append(c)
                cntrct_sns[(c['dept_code'], c['amt_ty_code'], c['cntrct_sn'])] = 1

        # 정렬
        for dept_code in result['contractList']:
            for amt_ty_code in result['contractList'][dept_code]:
                temp = result['contractList'][dept_code][amt_ty_code]
                result['contractList'][dept_code][amt_ty_code] = list(sorted(temp, key=lambda k: (k["bcnc_nm"], k["cntrct_nm"])))

        # 요약/디테일 부서 일치
        for r in result['contractStatusList']:
            if r['dept_code'] not in result['contractList']:
                result['contractList'][r['dept_code']] = dict()

        # 단납건/장려금 점검값 및 세부내역값
        goal_89 = db.get_goal_89(params)
        goal_data = dict()
        for g in goal_89:
            if int(g['dashboard_row']) not in goal_data:
                goal_data[int(g['dashboard_row'])] = dict()
            goal_data[int(g['dashboard_row'])][g['dashboard_column']] = g['dashboard_data']

        DEPT_CNTRCT_SN = {"ST" : -1, "TS1" : -2, "TS2" : -3, "BI" : -4, "ETC" : -5}


        # 1,4,7,10월 장려금
        if int(params['s_pxcond_m'].split("-")[1]) % 3 == 1:


            for r in result['contractStatusList']:
                if str(r['amt_ty_code']) == '3' and (r['ty8_goal_amount'] != 0 or r['ty9_goal_amount'] != 0):
                    if '3' not in result['contractList'][r['dept_code']]:
                        result['contractList'][r['dept_code']]['3'] = []
                    row = {'value': r['ty8_goal_amount'], 'stdyy': str(params["s_stdyy"]).zfill(4), 'amt_ty_code': 3,
                     'dept_code': r['dept_code'], 'cntrct_sn': DEPT_CNTRCT_SN[r['dept_code']], 'cntrct_nm': '장려금', 'bcnc_sn': '', 'bcnc_nm': '',
                     'amount': r['ty9_goal_amount']}
                    dashboard_row = DEPT_CNTRCT_SN[r['dept_code']]
                    if dashboard_row in goal_data:
                        if 'rmT' in goal_data[dashboard_row]:
                            row['dashboard_rm'] = goal_data[dashboard_row]['rmT']
                        else:
                            row['dashboard_rm'] = ''
                        if 'valueT' in goal_data[dashboard_row]:
                            row['dashboard_value'] = goal_data[dashboard_row]['valueT']
                        else:
                            row['dashboard_value'] = ''
                    else:
                        row['dashboard_value'] = ''
                        row['dashboard_rm'] = ''
                    result['contractList'][r['dept_code']]['3'].append(row)
                elif str(r['amt_ty_code']) == '3':
                    if '3' not in result['contractList'][r['dept_code']]:
                        result['contractList'][r['dept_code']]['3'] = []
                    row = {'value': 0, 'stdyy': str(params["s_stdyy"]).zfill(4), 'amt_ty_code': 3,
                     'dept_code': r['dept_code'], 'cntrct_sn': DEPT_CNTRCT_SN[r['dept_code']], 'cntrct_nm': '장려금', 'bcnc_sn': '', 'bcnc_nm': '',
                     'amount': 0}
                    dashboard_row = DEPT_CNTRCT_SN[r['dept_code']]
                    if dashboard_row in goal_data:
                        if 'rmT' in goal_data[dashboard_row]:
                            row['dashboard_rm'] = goal_data[dashboard_row]['rmT']
                        else:
                            row['dashboard_rm'] = ''
                        if 'valueT' in goal_data[dashboard_row]:
                            row['dashboard_value'] = goal_data[dashboard_row]['valueT']
                        else:
                            row['dashboard_value'] = ''
                    else:
                        row['dashboard_value'] = ''
                        row['dashboard_rm'] = ''
                    result['contractList'][r['dept_code']]['3'].append(row)


        # 기타 단납건 (차액)
        total_amount_2 = dict()
        total_amount_3 = dict()
        for r in result['contractStatusList']:
            if r['amt_ty_code'] == '3':
                total_amount_3[r['dept_code']] = r['ty9_goal_amount'] + r['m_contract_amount']
            if r['amt_ty_code'] == '2':
                total_amount_2[r['dept_code']] = r['m_contract_amount']

        for dept_code in result['contractList']:
            if '3' in result['contractList'][dept_code]:
                remain = total_amount_3[dept_code] - sum([c['amount'] for c in result['contractList'][dept_code]['3']])
            else:
                remain = total_amount_3[dept_code]
            row = {'value': 0, 'stdyy': str(params["s_stdyy"]).zfill(4), 'amt_ty_code': 3,
                   'dept_code': dept_code, 'cntrct_sn': DEPT_CNTRCT_SN[dept_code]-len(DEPT_CNTRCT_SN), 'cntrct_nm': '단납 건(1,000만원 이하)',
                   'bcnc_sn': '', 'bcnc_nm': '',
                   'amount': remain}
            dashboard_row = DEPT_CNTRCT_SN[dept_code] - len(DEPT_CNTRCT_SN)
            if dashboard_row in goal_data:
                if 'rmT' in goal_data[dashboard_row]:
                    row['dashboard_rm'] = goal_data[dashboard_row]['rmT']
                else:
                    row['dashboard_rm'] = ''
                if 'valueT' in goal_data[dashboard_row]:
                    row['dashboard_value'] = goal_data[dashboard_row]['valueT']
                else:
                    row['dashboard_value'] = ''
            else:
                row['dashboard_value'] = ''
                row['dashboard_rm'] = ''
            if '3' not in result['contractList'][dept_code]:
                result['contractList'][dept_code]['3'] = list()
            result['contractList'][dept_code]['3'].append(row)


        for dept_code in result['contractList']:
            if '2' in result['contractList'][dept_code]:
                remain = total_amount_2[dept_code] - sum([c['amount'] for c in result['contractList'][dept_code]['2']])
            else:
                remain = total_amount_2[dept_code]
            row = {'value': 0, 'stdyy': str(params["s_stdyy"]).zfill(4), 'amt_ty_code': 2,
                   'dept_code': dept_code, 'cntrct_sn': DEPT_CNTRCT_SN[dept_code]-(len(DEPT_CNTRCT_SN)*2), 'cntrct_nm': '단납 건(5,000만원 이하)',
                   'bcnc_sn': '', 'bcnc_nm': '',
                   'amount': remain}
            dashboard_row = DEPT_CNTRCT_SN[dept_code] - (len(DEPT_CNTRCT_SN)*2)
            if dashboard_row in goal_data:
                if 'rmS' in goal_data[dashboard_row]:
                    row['dashboard_rm'] = goal_data[dashboard_row]['rmS']
                else:
                    row['dashboard_rm'] = ''
                if 'valueS' in goal_data[dashboard_row]:
                    row['dashboard_value'] = goal_data[dashboard_row]['valueS']
                else:
                    row['dashboard_value'] = ''
            else:
                row['dashboard_value'] = ''
                row['dashboard_rm'] = ''
            if '2' not in result['contractList'][dept_code]:
                result['contractList'][dept_code]['2'] = list()
            result['contractList'][dept_code]['2'].append(row)

        return jsonify(result)
    except Exception as e:
        print(e)
        return make_response(str(e), 500)

@bp.route('/ajax_set_extra_goal_contract', methods=['GET'])
def ajax_set_extra_goal_contract():
    try:
        params = request.args.to_dict()
        if "s_pxcond_mt" not in params:
            params['s_pxcond_mt'] = datetime.now().strftime("%Y-%m-%d")
        params["s_stdyy"], params["s_month"], _ = map(int, params['s_pxcond_mt'].split("-"))
        params["s_pxcond_m"] = "-".join(params['s_pxcond_mt'].split("-")[:2])
        cntrct_sns = dict()
        extra_contracts = db.get_extra_goal_contract(params)
        for c in extra_contracts:
            cntrct_sns[(c['dept_code'], c['amt_ty_code'], c['cntrct_sn'])] = 1
        if (params['s_dept_code'], params['s_amt_ty_code'], params['s_cntrct_sn']) not in cntrct_sns:
            db.set_extra_goal_contract(params)
        return jsonify({"status" : True, "message" : "성공적으로 입력되었습니다."})
    except Exception as e:
        print(e)
        return make_response(str(e), 500)

@bp.route('/ajax_get_extra_goal_contract', methods=['GET'])
def ajax_get_extra_goal_contract():
    try:
        params = request.args.to_dict()
        if "s_pxcond_mt" not in params:
            params['s_pxcond_mt'] = datetime.now().strftime("%Y-%m-%d")
        params["s_stdyy"], params["s_month"], _ = map(int, params['s_pxcond_mt'].split("-"))
        params["s_pxcond_m"] = "-".join(params['s_pxcond_mt'].split("-")[:2])
        result = db.get_extra_goal_contract(params)
        return jsonify(result)
    except Exception as e:
        print(e)
        return make_response(str(e), 500)

@bp.route('/ajax_delete_extra_goal_contract', methods=['GET'])
def ajax_delete_extra_goal_contract():
    try:
        params = request.args.to_dict()
        db.delete_extra_goal_contract(params)
        return jsonify({"status" : True, "message" : "성공적으로 입력되었습니다."})
    except Exception as e:
        print(e)
        return make_response(str(e), 500)


@bp.route('/ajax_set_dashboard_data', methods=['GET'])
def ajax_set_dashboard_data():
    try:
        params = request.args.to_dict()
        db.set_dashboard_data(params)
        return jsonify({"status" : True, "message" : "성공적으로 입력되었습니다."})
    except Exception as e:
        print(e)
        return make_response(str(e), 500)

@bp.route('/ajax_get_completed_va', methods=['GET'])
def ajax_get_completed_va():
    try:
        params = request.args.to_dict()
        if "s_pxcond_mt" not in params:
            params['s_pxcond_mt'] = datetime.now().strftime("%Y-%m-%d")
        result = dict()
        result['data'] = db.get_completed_va(params)
        return jsonify(result)
    except Exception as e:
        print(e)
        return make_response(str(e), 500)



@bp.route('/ajax_get_logit', methods=['GET'])
def ajax_get_logit():
    try:
        params = request.args.to_dict()
        if "s_pxcond_mt" not in params:
            params['s_pxcond_mt'] = datetime.now().strftime("%Y-%m-%d")
        result = dict()
        logitechs = db.get_logitech_report(params)
        result['data'] = list()
        for l in logitechs:
            if l['logi_now'] != '' or l['other_now'] != '' or l['logi_before'] != '' or l['other_before'] != '':
                result['data'].append(l)
        return jsonify(result)
    except Exception as e:
        print(e)
        return make_response(str(e), 500)

@bp.route('/ajax_get_logitech_detail', methods=['GET'])
def ajax_get_logitech_detail():
    try:
        params = request.args.to_dict()

        detail = db.get_logitech_detail(params)
        result = {"logitech" : list(), "other" : list(), "contract" : prj.get_contract(params)}
        for d in detail:
            result[d['p_type']].append(d)
        return jsonify(result)
    except Exception as e:
        print(e)
        return make_response(str(e), 500)
