from flask import Blueprint, g, current_app, render_template, redirect, request, make_response, jsonify, send_file, Response, url_for, session
from .services import sales_service as sales
from .services import project_service as prj
from .services import stock_service as st
from .services import common_service as cm

from app.connectors import DB
from app.helpers import session_helper
from .services import set_menu
import json
import os
from datetime import datetime
from dateutil import relativedelta
from pytz import timezone
bp = Blueprint('api_sales', __name__, url_prefix='/api/sales')

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

def make_row(cntrct_sn, dlivy_de, bcnc_nm, cntrct_nm, dept_nm, price_1, price_2, price_3, price_sum, price_4, delng_se_nm, expect_de, rcppay_de, rcppay_amount, diff, taxbil_sn='', taxbil_yn='Y', bcnc_sn='', sales_expect_de=''):
    data = {}
    data['cntrct_sn'] = cntrct_sn
    data['dlivy_de'] = dlivy_de
    data['bcnc_nm'] = bcnc_nm
    data['cntrct_nm'] = cntrct_nm
    data['dept_nm'] = dept_nm
    data['price_1'] = price_1
    data['price_2'] = price_2
    data['price_3'] = price_3
    data['price_sum'] = price_sum
    data['price_4'] = price_4
    data['delng_se_nm'] = delng_se_nm
    data['expect_de'] = expect_de
    data['rcppay_de'] = rcppay_de
    data['rcppay_amount'] = rcppay_amount
    data['taxbil_sn'] = taxbil_sn
    data['taxbil_yn'] = taxbil_yn
    data['diff'] = diff
    data['bcnc_sn'] = bcnc_sn
    data['sales_expect_de'] = sales_expect_de
    return data

@bp.route('/ajax_get_sales_datatable', methods=['POST'])
def ajax_get_sales_datatable():
    try:
        params = request.form.to_dict()
        result = sales.get_sales_datatable(params)
        result['summary'] = sales.get_sales_summary(params)
        return jsonify(result)
    except Exception as e:
        print(e)
        return make_response(str(e), 500)

@bp.route('/ajax_get_sales_approval_datatable', methods=['POST'])
def ajax_get_sales_approval_datatable():
    try:
        params = request.form.to_dict()
        result = sales.get_sales_approval_datatable(params)
        return jsonify(result)
    except Exception as e:
        print(e)
        return make_response(str(e), 500)

@bp.route('/ajax_get_inventory', methods=['GET'])
def ajax_get_inventory():
    try:
        params = request.args.to_dict()
        result = dict()
        result['sales'] = sales.get_account_list2(params)
        result['status'] = True
        return jsonify(result)
    except Exception as e:
        print(e)
        return make_response(str(e), 500)

@bp.route('/ajax_get_sales', methods=['GET'])
def ajax_get_sales():
    try:
        params = request.args.to_dict()
        result = dict()
        result['data'] = sales.get_account(params)
        result['status'] = True
        return jsonify(result)
    except Exception as e:
        print(e)
        return make_response(str(e), 500)

@bp.route('/ajax_insert_sales', methods=['POST'])
def ajax_insert_sales():
    try:
        params = request.form.to_dict()
        delng_sn = sales.insert_account(params)

        delng_se_code = params['delng_se_code']
        bcnc_sn = params['bcnc_sn']
        delng_ty_code = params['delng_ty_code']
        # 구입->창고
        if delng_se_code == 'P' and bcnc_sn == '74' and delng_ty_code == '1' and "invn_sttus_code" in params and params["invn_sttus_code"] and ("cntrct_sn" not in params or params["cntrct_sn"] == "") and int(params['dlnt']) > 0:
            # print(params)
            # print(request.form.getlist("item_sn[]"))
            for _ in range(int(params['dlnt'])):
                item_sn = st.insert_stock(params, 0)
                st.insert_log(item_sn, 1, params['invn_sttus_code'], delng_sn, params['ddt_man'])


        elif delng_se_code == 'P' and bcnc_sn == '100' and delng_ty_code == '2' and "invn_sttus_code" in params and params["invn_sttus_code"] and ("cntrct_sn" not in params or params["cntrct_sn"] == "") and int(params['dlnt']) > 0:
            for _ in range(int(params['dlnt'])):
                item_sn = st.insert_stock(params, 0)
                st.insert_log(item_sn, 1, params['invn_sttus_code'], delng_sn, params['ddt_man'])

        # 창고->전시
        elif delng_se_code == 'P' and bcnc_sn == '79' and delng_ty_code in ('62', '61') and "invn_sttus_code" in params and params["invn_sttus_code"] and "cntrct_sn" in params and params["cntrct_sn"] and int(params['dlnt']) > 0:
            item_sns = request.form.getlist("item_sn[]")
            if len(item_sns) > 0:
                for item_sn in item_sns:
                    st.insert_log(item_sn, 2, params['cntrct_sn'], delng_sn, params['ddt_man'])

            # 바로 구매->전시
            else:
                # for _ in range(int(params['dlnt'])):
                #     item_sn = st.insert_stock(params, 0)
                #     st.insert_log(item_sn, 2, params['cntrct_sn'], delng_sn, params['ddt_man'])
                params['s_delng_sn'] = delng_sn
                sales.delete_account(params)
                return jsonify({"status": False, "message": "재고를 선택해주세요."})

        # 창고->판매
        elif delng_se_code == 'P' and bcnc_sn == '79' and delng_ty_code == '1' and "invn_sttus_code" in params and params["invn_sttus_code"] and "cntrct_sn" in params and params["cntrct_sn"] and int(params['dlnt']) > 0:
            item_sns = request.form.getlist("item_sn[]")
            if len(item_sns) > 0:
                for item_sn in item_sns:
                    st.insert_log(item_sn, 3, params['cntrct_sn'], delng_sn, params['ddt_man'])
            # 바로 구매->판매
            else:
                # for _ in range(int(params['dlnt'])):
                #     item_sn = st.insert_stock(params, 0)
                #     st.insert_log(item_sn, 3, params['cntrct_sn'], delng_sn, params['ddt_man'])
                params['s_delng_sn'] = delng_sn
                sales.delete_account(params)
                return jsonify({"status": False, "message": "재고를 선택해주세요."})

        # 현장->반품
        elif delng_se_code == 'P' and bcnc_sn == '79' and delng_ty_code == '1' and "invn_sttus_code" in params and params["invn_sttus_code"] and "cntrct_sn" in params and params["cntrct_sn"] and int(params['dlnt']) < 0:
            for _ in range(-1*int(params['dlnt'])):
                item_sn = st.insert_stock(params, 0)
                st.insert_log(item_sn, 3, params['cntrct_sn'], delng_sn, params['ddt_man'])
                st.insert_log(item_sn, 1, params['invn_sttus_code'], delng_sn, params['ddt_man'])

        # 구매->현장 전시???
        elif delng_se_code == 'P' and bcnc_sn in ('74', '100') and delng_ty_code == '61' and "invn_sttus_code" in params and params["invn_sttus_code"] == "0" and "cntrct_sn" in params and params["cntrct_sn"] and int(params['dlnt']) > 0:
            for _ in range(int(params['dlnt'])):
                item_sn = st.insert_stock(params, 0)
                st.insert_log(item_sn, 2, params['cntrct_sn'], delng_sn, params['ddt_man'])

        return jsonify({"status": True, "message": "성공적으로 추가되었습니다."})
    except Exception as e:
        print(e)
        return make_response(str(e), 500)

@bp.route('/ajax_update_sales', methods=['POST'])
def ajax_update_sales():
    try:
        params = request.form.to_dict()
        sales.update_account(params)
        stocks = st.get_stock_by_account(params['s_delng_sn'], isReturn=False)
        for stock in stocks:
            st.update_stock_type(stock['stock_sn'], params['use_type'])
        return jsonify({"status": True, "message": "성공적으로 변경되었습니다."})
    except Exception as e:
        print(e)
        return make_response(str(e), 500)

@bp.route('/ajax_delete_sales', methods=['POST'])
def ajax_delete_sales():
    try:
        params = request.form.to_dict()
        sales.delete_account(params)
        return jsonify({"status": True, "message": "성공적으로 삭제되었습니다."})
    except Exception as e:
        print(e)
        return make_response(str(e), 500)

@bp.route('/ajax_get_contract', methods=['GET'])
def ajax_get_contract():
    try:
        params = request.args.to_dict()
        result = dict()
        result['data'] = prj.get_contract(params)
        if result['data']:
            if result['data']['prjct_creat_at'] == 'Y':
                projectParams = {"s_cntrct_sn" : result['data']['cntrct_sn']}
                result['project'] = prj.get_project_list(projectParams)
            salesParams = {"s_cntrct_sn" : result['data']['cntrct_sn']}
            result['sales'] = sales.get_account_list(salesParams)
        result['status'] = True
        return jsonify(result)
    except Exception as e:
        print(e)
        return make_response(str(e), 500)


@bp.route('/ajax_get_sales_report', methods=['GET'])
def ajax_get_sales_report():
    try:
        params = request.args.to_dict()
        result = dict()
        result['data'] = sales.get_account_report(params)
        result['pAccountList'] = sales.get_p_account_list(params)
        result['sAccountList'] = sales.get_s_account_list(params)
        if "s_ddt_man" in params and params["s_ddt_man"]:
            y, m, d = map(int, params["s_ddt_man"].split("-"))
            result['date'] = "{}년 {}월 {}일".format(y, m, d)
        result['status'] = True
        return jsonify(result)
    except Exception as e:
        print(e)
        return make_response(str(e), 500)


@bp.route('/ajax_get_sales_expect_report', methods=['GET'])
def ajax_get_sales_expect_report():
    try:
        params = request.args.to_dict()
        table_data = {}
        if "expect_de" in params:
            result = []
            s_expect_de = params['expect_de']
            for i in range(3):
                params["expect_de"] = (datetime.strptime(s_expect_de, "%Y-%m-%d") + relativedelta.relativedelta(months=i)).strftime("%Y-%m-15")
                s_result = sales.get_expect_s_list(params)
                t_result = sales.get_expect_t_list(params)
                r_result = sales.get_expect_r_list(params)

                s_dict = dict()
                for s in s_result:
                    key = (s['bcnc_sn'], s['cntrct_sn'], "-".join(s['expect_de'].split("-")[:2]))
                    if key not in s_dict:
                        s_dict[key] = list()
                    s_dict[key].append(s)

                t_dict = dict()
                for t in t_result:
                    key = (t['bcnc_sn'], t['cntrct_sn'], "-".join(t['expect_de'].split("-")[:2]))
                    if key not in t_dict:
                        t_dict[key] = t
                    else:
                        t_dict[key]['price_total'] += t['price_total']
                        t_dict[key]['taxbil_sn'] = ",".join(
                            list(set(t_dict[key]['taxbil_sn'].split(",")) | set(t['taxbil_sn'].split(","))))

                r_dict = dict()
                for r in r_result:
                    key = r['taxbil_sn']
                    if key not in r_dict:
                        r_dict[key] = list()
                    r_dict[key].append(r)


                total_result = {-1: list(), 0: list(), 1: list(), 2: list()}
                for key in set(s_dict.keys()) | set(t_dict.keys()):
                    bcnc_sn, cntrct_sn, expect_de = key
                    if key in s_dict and key in t_dict:
                        s_rows = s_dict[key]
                        t = t_dict[key]
                        r_rows = list()
                        for taxbil_sn in t['taxbil_sn'].split(","):
                            if int(taxbil_sn) in r_dict:
                                r_rows += r_dict[int(taxbil_sn)]
                        price_3 = t['price_total'] - sum([s['price_1'] + s['price_2'] for s in s_rows])
                        # taxbil_sn = t['taxbil_sn'] if t['taxbil_yn'] == 'Y' else ''
                        taxbil_sn = t['taxbil_sn']
                        taxbil_yn = t['taxbil_yn']
                        diff = t['price_total'] - sum([r['amount'] for r in r_rows])
                        order = -1 if diff == 0 else (1 if len(r_rows) == 0 else 0)
                        rows = max(len(s_rows), len(r_rows))
                        for i in range(rows):
                            p3 = price_3 if i == 0 else 0
                            if i < len(s_rows) and i < len(r_rows):
                                data = make_row(s_rows[i]['cntrct_sn'], s_rows[i]['dlivy_de'], s_rows[i]['bcnc_nm'], s_rows[i]['cntrct_nm'],
                                                s_rows[i]['dept_nm'], s_rows[i]['price_1'], s_rows[i]['price_2'], price_3, s_rows[i]['price_1'] + s_rows[i]['price_2'] + p3,
                                                t['price_total'], t['delng_se_nm'], expect_de, r_rows[i]['rcppay_de'],
                                                r_rows[i]['amount'], diff, taxbil_sn, taxbil_yn, s_rows[i]['bcnc_sn'], s_rows[i]['expect_de'])
                            elif i < len(r_rows):
                                data = make_row(t['cntrct_sn'], '', t['bcnc_nm'], t['cntrct_nm'], t['dept_nm'], 0, 0, price_3, p3, t['price_total'],
                                                t['delng_se_nm'], expect_de, r_rows[i]['rcppay_de'], r_rows[i]['amount'], diff,
                                                taxbil_sn, taxbil_yn, '', '')
                            else:
                                data = make_row(s_rows[i]['cntrct_sn'], s_rows[i]['dlivy_de'], s_rows[i]['bcnc_nm'], s_rows[i]['cntrct_nm'],
                                                s_rows[i]['dept_nm'], s_rows[i]['price_1'], s_rows[i]['price_2'], price_3, s_rows[i]['price_1'] + s_rows[i]['price_2'] + p3,
                                                t['price_total'], t['delng_se_nm'], expect_de, '', '', diff, taxbil_sn, taxbil_yn, s_rows[i]['bcnc_sn'], s_rows[i]['expect_de'])
                            total_result[order].append(data)
                    elif key in s_dict:
                        s_rows = s_dict[key]
                        order = 2
                        for i in range(len(s_rows)):
                            data = make_row(s_rows[i]['cntrct_sn'], s_rows[i]['dlivy_de'], s_rows[i]['bcnc_nm'], s_rows[i]['cntrct_nm'], s_rows[i]['dept_nm'],
                                            s_rows[i]['price_1'], s_rows[i]['price_2'], '', s_rows[i]['price_1']+s_rows[i]['price_2'], '', '', '', '', '',
                                            (s_rows[i]['price_1'] + s_rows[i]['price_2']), '', '', s_rows[i]['bcnc_sn'], s_rows[i]['expect_de'])
                            total_result[order].append(data)
                    else:
                        t = t_dict[key]
                        r_rows = list()
                        for taxbil_sn in t['taxbil_sn'].split(","):
                            if int(taxbil_sn) in r_dict:
                                r_rows += r_dict[int(taxbil_sn)]
                        price_3 = t['price_total']
                        # taxbil_sn = t['taxbil_sn'] if t['taxbil_yn'] == 'Y' else ''
                        taxbil_sn = t['taxbil_sn']
                        taxbil_yn = t['taxbil_yn']
                        diff = t['price_total'] - sum([r['amount'] for r in r_rows])
                        order = -1 if diff == 0 else (1 if len(r_rows) == 0 else 0)
                        if len(r_rows) == 0:
                            data = make_row(t['cntrct_sn'], t['dlivy_de'], t['bcnc_nm'], t['cntrct_nm'], t['dept_nm'], 0, 0, price_3, price_3, t['price_total'],
                                            t['delng_se_nm'], expect_de, '', '', diff,
                                            taxbil_sn, taxbil_yn, '', '')
                            total_result[order].append(data)
                        for i in range(len(r_rows)):
                            p3 = price_3 if i ==0  else 0
                            data = make_row(t['cntrct_sn'], t['dlivy_de'], t['bcnc_nm'], t['cntrct_nm'], t['dept_nm'], 0, 0, price_3, p3, t['price_total'],
                                            t['delng_se_nm'], expect_de, r_rows[i]['rcppay_de'], r_rows[i]['amount'], diff,
                                            taxbil_sn, taxbil_yn, '', '')
                            total_result[order].append(data)

                total_rows = {-1: list(), 0: list()}
                t_result = sales.get_expect_p_t_list(params)
                r_result = sales.get_expect_p_r_list(params)

                t_dict = dict()
                for t in t_result:
                    key = (t['bcnc_sn'], t['cntrct_sn'], "-".join(t['expect_de'].split("-")[:2]))
                    if key not in t_dict:
                        t_dict[key] = t
                    else:
                        t_dict[key]['price_total'] += t['price_total']
                        t_dict[key]['taxbil_sn'] = ",".join(
                            list(set(t_dict[key]['taxbil_sn'].split(",")) | set(t['taxbil_sn'].split(","))))

                r_dict = dict()
                for r in r_result:
                    key = r['taxbil_sn']
                    if key not in r_dict:
                        r_dict[key] = list()
                    r_dict[key].append(r)

                for key in t_dict:
                    row = []
                    t = t_dict[key]
                    bcnc_sn, cntrct_sn, expect_de = key
                    diff = t['price_total']
                    for taxbil_sn in t['taxbil_sn'].split(","):
                        if int(taxbil_sn) in r_dict:
                            r_rows = r_dict[int(taxbil_sn)]
                            for r in r_rows:
                                row.append({"bcnc_nm": t["bcnc_nm"], "cntrct_nm": t["cntrct_nm"], "price": t["price_total"],
                                            "expect_de": t["expect_de"], "rcppay_de": r["rcppay_de"],
                                            "rcppay_amount": r["amount"]})
                                diff -= r['amount']
                        else:
                            row.append({"bcnc_nm": t["bcnc_nm"], "cntrct_nm": t["cntrct_nm"], "price": t["price_total"],
                                        "expect_de": t["expect_de"], "rcppay_de": '', "rcppay_amount": ''})
                    if diff == 0:
                        total_rows[-1] += row
                    else:
                        total_rows[0] += row

                result.append({"expect_de" : datetime.strptime(params["expect_de"], "%Y-%m-%d").strftime("%Y-%m"), "data" : total_result, "pData" : total_rows})


            table_data["termData"] = result

        s_result = sales.get_expect_s_list(dict())
        t_result = sales.get_expect_t_list(dict())
        r_result = sales.get_expect_r_list(dict())
        s_dict = dict()
        for s in s_result:
            key = (s['bcnc_sn'], s['cntrct_sn'], "-".join(s['expect_de'].split("-")[:2]))
            if key not in s_dict:
                s_dict[key] = list()
            s_dict[key].append(s)

        t_dict = dict()
        for t in t_result:
            key = (t['bcnc_sn'], t['cntrct_sn'], "-".join(t['expect_de'].split("-")[:2]))
            if key not in t_dict:
                t_dict[key] = t
            else:
                t_dict[key]['price_total'] += t['price_total']
                t_dict[key]['taxbil_sn'] = ",".join(
                    list(set(t_dict[key]['taxbil_sn'].split(",")) | set(t['taxbil_sn'].split(","))))

        r_dict = dict()
        for r in r_result:
            key = r['taxbil_sn']
            if key not in r_dict:
                r_dict[key] = list()
            r_dict[key].append(r)

        total_long_result = {-1: list(), 0: list(), 1: list(), 2: list()}
        for key in set(s_dict.keys()) | set(t_dict.keys()):
            bcnc_sn, cntrct_sn, expect_de = key
            if key in s_dict and key in t_dict:
                s_rows = s_dict[key]
                t = t_dict[key]
                r_rows = list()
                for taxbil_sn in t['taxbil_sn'].split(","):
                    if int(taxbil_sn) in r_dict:
                        r_rows += r_dict[int(taxbil_sn)]
                price_3 = t['price_total'] - sum([s['price_1'] + s['price_2'] for s in s_rows])
                # taxbil_sn = t['taxbil_sn'] if t['taxbil_yn'] == 'Y' else ''
                taxbil_sn = t['taxbil_sn']
                taxbil_yn = t['taxbil_yn']
                diff = t['price_total'] - sum([r['amount'] for r in r_rows])
                order = -1 if diff == 0 else (1 if len(r_rows) == 0 else 0)
                rows = max(len(s_rows), len(r_rows))
                for i in range(rows):
                    data = {}
                    p3 = price_3 if i == 0 else 0
                    if i < len(s_rows) and i < len(r_rows):
                        data = make_row(s_rows[i]['cntrct_sn'], s_rows[i]['dlivy_de'], s_rows[i]['bcnc_nm'], s_rows[i]['cntrct_nm'],
                                        s_rows[i]['dept_nm'], s_rows[i]['price_1'], s_rows[i]['price_2'], price_3, s_rows[i]['price_1']+s_rows[i]['price_2']+p3,
                                        t['price_total'], t['delng_se_nm'], expect_de, r_rows[i]['rcppay_de'],
                                        r_rows[i]['amount'], diff, taxbil_sn, taxbil_yn, s_rows[i]['bcnc_sn'], s_rows[i]['expect_de'])
                    elif i < len(r_rows):
                        data = make_row(t['cntrct_sn'], '', t['bcnc_nm'], t['cntrct_nm'], t['dept_nm'], 0, 0, price_3, p3, t['price_total'],
                                        t['delng_se_nm'], expect_de, r_rows[i]['rcppay_de'], r_rows[i]['amount'], diff,
                                        taxbil_sn, taxbil_yn, '', '')
                    else:
                        data = make_row(s_rows[i]['cntrct_sn'], s_rows[i]['dlivy_de'], s_rows[i]['bcnc_nm'], s_rows[i]['cntrct_nm'],
                                        s_rows[i]['dept_nm'], s_rows[i]['price_1'], s_rows[i]['price_2'], price_3, s_rows[i]['price_1']+s_rows[i]['price_2']+p3,
                                        t['price_total'], t['delng_se_nm'], expect_de, '', '', diff, taxbil_sn, taxbil_yn, s_rows[i]['bcnc_sn'], s_rows[i]['expect_de'])
                    total_long_result[order].append(data)
            elif key in s_dict:
                s_rows = s_dict[key]
                order = 2
                for i in range(len(s_rows)):
                    data = make_row(s_rows[i]['cntrct_sn'], s_rows[i]['dlivy_de'], s_rows[i]['bcnc_nm'], s_rows[i]['cntrct_nm'],
                                    s_rows[i]['dept_nm'], s_rows[i]['price_1'], s_rows[i]['price_2'], '', s_rows[i]['price_1']+s_rows[i]['price_2'], '', '', expect_de, '',
                                    '', (s_rows[i]['price_1'] + s_rows[i]['price_2']), '', '', s_rows[i]['bcnc_sn'], s_rows[i]['expect_de'])
                    total_long_result[order].append(data)
            else:
                t = t_dict[key]
                r_rows = list()
                for taxbil_sn in t['taxbil_sn'].split(","):
                    if int(taxbil_sn) in r_dict:
                        r_rows += r_dict[int(taxbil_sn)]
                price_3 = t['price_total']
                # taxbil_sn = t['taxbil_sn'] if t['taxbil_yn'] == 'Y' else ''
                taxbil_sn = t['taxbil_sn']
                taxbil_yn = t['taxbil_yn']
                diff = t['price_total'] - sum([r['amount'] for r in r_rows])
                order = -1 if diff == 0 else (1 if len(r_rows) == 0 else 0)
                if len(r_rows) == 0:
                    data = make_row(t['cntrct_sn'], t['dlivy_de'], t['bcnc_nm'], t['cntrct_nm'], t['dept_nm'], 0, 0, price_3, price_3,
                                    t['price_total'], t['delng_se_nm'], expect_de, '',
                                    '', diff, taxbil_sn, taxbil_yn, '', '')
                    total_long_result[order].append(data)

                for i in range(len(r_rows)):
                    p3 = price_3 if i == 0 else 0
                    data = {}
                    data = make_row(t['cntrct_sn'], t['dlivy_de'], t['bcnc_nm'], t['cntrct_nm'], t['dept_nm'], 0, 0, price_3, p3,
                                    t['price_total'], t['delng_se_nm'], expect_de, r_rows[i]['rcppay_de'],
                                    r_rows[i]['amount'], diff, taxbil_sn, taxbil_yn, '', '')
                    total_long_result[order].append(data)

        for key in total_long_result:
            results = total_long_result[key]
            finals_data = dict()
            for f in results:
                if (f['cntrct_sn'], f['taxbil_sn']) not in finals_data:
                    finals_data[(f['cntrct_sn'], f['taxbil_sn'])] = []
                finals_data[(f['cntrct_sn'], f['taxbil_sn'])].append(f)

            sorted_finals = []
            for cntrct_sn in sorted(list(finals_data.keys()), key=lambda x: finals_data[x][0]['dlivy_de']):
                sorted_finals += finals_data[cntrct_sn]
            total_long_result[key] = sorted_finals

        finals = []
        for key in total_long_result:
            if key == -1:
                continue
            results = total_long_result[key]
            func = lambda x: x['expect_de'] != '0000-00' and datetime.strptime(datetime.now(timezone('Asia/Seoul')).strftime("%Y-%m-01"), "%Y-%m-%d") > datetime.strptime(x['expect_de'], "%Y-%m")
            finals += filter(func, results)

        finals_data = dict()
        for f in finals:
            if (f['cntrct_sn'], f['taxbil_sn']) not in finals_data:
                finals_data[(f['cntrct_sn'], f['taxbil_sn'])] = []
            finals_data[(f['cntrct_sn'], f['taxbil_sn'])].append(f)

        sorted_finals = []
        for cntrct_sn in sorted(list(finals_data.keys()), key=lambda x: finals_data[x][0]['dlivy_de']):
            sorted_finals += finals_data[cntrct_sn]
        table_data["longTermData"] = sorted_finals

        return jsonify(table_data)
    except Exception as e:
        print(e)
        return make_response(str(e), 500)

@bp.route('/equip_to_account', methods=['GET'])
def equip_to_account():
    try:
        params = request.args.to_dict()
        equipment = cm.get_equipment(params)
        prjct = prj.get_project_by_cntrct_nm(equipment["cntrct_sn"])
        cntrct = prj.get_contract({"s_cntrct_sn" : equipment["cntrct_sn"]})

        row = dict()
        row['cntrct_sn'] = equipment['cntrct_sn']
        row['prjct_sn'] = prjct['prjct_sn']
        row['ctmmny_sn'] = 1
        row['regist_dtm'] = datetime.now(timezone('Asia/Seoul'))
        row['register_id'] = session['member']['member_id']
        row['delng_se_code'] = 'P'
        row['ddt_man'] = params['dlivy_de']
        row['bcnc_sn'] = equipment['bcnc_sn']
        row['prdlst_se_code'] = equipment['prdlst_se_code']
        row['model_no'] = equipment['model_no']
        row['delng_ty_code'] = equipment['delng_ty_code']
        row['dlnt'] = params["before_dlnt"]
        row['dlamt'] = equipment['pamt']
        keys = list(row.keys())
        g.curs.execute("INSERT INTO account({0}) VALUES ({1})".format(",".join(keys), ",".join(["%({})s".format(key) for key in keys])), row)
        delng_sn = g.curs.lastrowid
        row['delng_se_code'] = 'S'
        row['dlivy_de'] = params['dlivy_de']
        row['cnnc_sn'] = delng_sn
        row['bcnc_sn'] = cntrct["bcnc_sn"]
        row['dlamt'] = equipment['samt']
        row['delng_ty_code'] = params["delng_ty_code"]
        if 'expect_de' in params and params['expect_de'] == '':
            params['expect_de'] = None
        row['expect_de'] = params['expect_de']
        keys = list(row.keys())
        g.curs.execute("INSERT INTO account({0}) VALUES ({1})".format(",".join(keys), ",".join(["%({})s".format(key) for key in keys])), row)
        params['last_dlnt'] = equipment['before_dlnt'] + int(params["before_dlnt"])
        g.curs.execute("UPDATE equipment SET dlivy_de=%(dlivy_de)s, before_dlnt=%(last_dlnt)s WHERE eq_sn=%(eq_sn)s", params)
        return jsonify({"status" : True, "message" : "성공적으로 추가되었습니다."})

    except Exception as e:
        print(e)
        return make_response(str(e), 500)

@bp.route('/insert_BF_ms_equip', methods=['POST'])
def insert_BF_ms_equip():
    try:
        pParams = request.get_json()
        params = {}
        for key in pParams:
            if (key.startswith("m_") or key.startswith("s_")) and key.endswith("[]"):
                if key[2:] in params:
                    params[key[2:]] += pParams[key]
                else:
                    params[key[2:]] = pParams[key]
            else:
                params[key] = pParams[key]
        if params['msh_approval_type'] in ('S', 'B'):
            delng_sns = sales.insert_ms_BF_equip(params)
            stock_sns = [(stock_sn, delng_sn, model_no, dlnt, prduct_ty_code) for delng_ty_code, stock_sn, delng_sn, model_no, dlnt, prduct_ty_code in zip(params["delng_ty_code[]"], params["stock_sn[]"], delng_sns, params["model_no[]"], params["qy[]"], params["prduct_ty_code[]"]) if dlnt != '' and model_no != '']
            for stock_sn, delng_sn, model_no, dlnt, prduct_ty_code in stock_sns:

                if stock_sn == "":
                    for _ in range(int(dlnt)):
                        s_params = {"use_type" : "", "prduct_se_code" : "2", "prduct_ty_code" : prduct_ty_code, "model_no" : model_no}
                        stock_sn = st.insert_stock(s_params, 0)
                        st.insert_log(stock_sn, 2, params['cntrct_sn'], delng_sn, datetime.now(timezone('Asia/Seoul')))
                else:
                    st.insert_log(stock_sn, 2, params['cntrct_sn'], delng_sn, datetime.now(timezone('Asia/Seoul')))
            return jsonify({"status" : True, "message" : "성공적으로 처리되었습니다."})
        else:
            sales.insert_ms_BF_equip(params)
            for delng_sn, dlnt, invn_sttus_code, return_de in zip(params["delng_sn[]"], params["return_dlnt[]"], params["stock_place[]"], params["return_de[]"]):
                if dlnt != '' and invn_sttus_code != '' and return_de != '':
                    stocks = st.get_stock_by_account(delng_sn, isOut=True)
                    for s in stocks[:min(len(stocks), int(dlnt))]:
                        st.insert_log(s['stock_sn'], 1, invn_sttus_code, None, return_de)

            return jsonify({"status" : True, "message" : "성공적으로 처리되었습니다."})
    except Exception as e:
        print(e)
        return make_response(str(e), 500)


@bp.route('/insert_BD_ms_equip', methods=['POST'])
def insert_BD_ms_equip():
    # try:
        pParams = request.get_json()
        params = {}
        for key in pParams:
            if (key.startswith("m_") or key.startswith("s_")) and key.endswith("[]"):
                if key[2:] in params:
                    params[key[2:]] += pParams[key]
                else:
                    params[key[2:]] = pParams[key]
            else:
                params[key] = pParams[key]
        if params['msh_approval_type'] in ('S', 'B'):
            delng_sns = sales.insert_ms_BF_equip(params)
            stock_sns = [(stock_sn, delng_sn, model_no, dlnt, prduct_ty_code) for delng_ty_code, stock_sn, delng_sn, model_no, dlnt, prduct_ty_code in zip(params["delng_ty_code[]"], params["stock_sn[]"], delng_sns, params["model_no[]"], params["qy[]"], params["prduct_ty_code[]"])]
            for stock_sn, delng_sn, model_no, dlnt, prduct_ty_code in stock_sns:

                if stock_sn == "":
                    for _ in range(int(dlnt)):
                        s_params = {"use_type" : "", "prduct_se_code" : "2", "prduct_ty_code" : prduct_ty_code, "model_no" : model_no}
                        stock_sn = st.insert_stock(s_params, 0)
                        st.insert_log(stock_sn, 2, params['cntrct_sn'], delng_sn, datetime.now(timezone('Asia/Seoul')))
                else:
                    st.insert_log(stock_sn, 2, params['cntrct_sn'], delng_sn, datetime.now(timezone('Asia/Seoul')))
            return jsonify({"status" : True, "message" : "성공적으로 처리되었습니다."})
        else:
            sales.insert_ms_BF_equip(params)
            for delng_sn, dlnt, invn_sttus_code, return_de in zip(params["delng_sn[]"], params["return_dlnt[]"], params["stock_place[]"], params["return_de[]"]):
                if dlnt != '' and invn_sttus_code != '' and return_de != '':
                    stocks = st.get_stock_by_account(delng_sn, isOut=True)
                    for s in stocks[:min(len(stocks), int(dlnt))]:
                        st.insert_log(s['stock_sn'], 1, invn_sttus_code, None, return_de)

            return jsonify({"status" : True, "message" : "성공적으로 처리되었습니다."})
    # except Exception as e:
    #     print(e)
    #     return make_response(str(e), 500)


@bp.route('/insert_ms_equip', methods=['POST'])
def insert_ms_equip():
    try:
        params = request.get_json()
        if params['msh_approval_type'] in ('S', 'B'):
            delng_sns = sales.insert_ms_equip(params)
            stock_sns = [(stock_sn, delng_sn, model_no, dlnt, prduct_ty_code) for delng_ty_code, stock_sn, delng_sn, model_no, dlnt, prduct_ty_code in zip(params["delng_ty_code[]"], params["delng_sn[]"], delng_sns, params["model_no[]"], params["dlnt[]"], params["prduct_ty_code[]"])]
            for stock_sn, delng_sn, model_no, dlnt, prduct_ty_code in stock_sns:

                if stock_sn == "":
                    for _ in range(int(dlnt)):
                        s_params = {"use_type" : "", "prduct_se_code" : "1", "prduct_ty_code" : prduct_ty_code, "model_no" : model_no}
                        stock_sn = st.insert_stock(s_params, 0)
                        st.insert_log(stock_sn, 2, params['cntrct_sn'], delng_sn, datetime.now(timezone('Asia/Seoul')))
                else:
                    st.insert_log(stock_sn, 2, params['cntrct_sn'], delng_sn, datetime.now(timezone('Asia/Seoul')))
            return jsonify({"status" : True, "message" : "성공적으로 처리되었습니다."})
        else:
            sales.insert_ms_equip(params)
            for delng_sn, dlnt, invn_sttus_code, return_de in zip(params["delng_sn[]"], params["return_dlnt[]"], params["stock_place[]"], params["return_de[]"]):

                stocks = st.get_stock_by_account(delng_sn, isOut=True)
                for s in stocks[:min(len(stocks), int(dlnt))]:
                    st.insert_log(s['stock_sn'], 1, invn_sttus_code, None, return_de)

            return jsonify({"status" : True, "message" : "성공적으로 처리되었습니다."})
    except Exception as e:
        print(e)
        return make_response(str(e), 500)


@bp.route('/get_model_list', methods=['GET'])
def get_model_list():
    try:
        params = request.args.to_dict()
        result = dict()
        result['model'] = sales.get_model_list(params)
        result['modelList'] = dict()
        for d in result['model']:
            stocks = st.get_stock_by_account(d['delng_sn'])
            for stock in stocks:
                pParams = {"s_stock_sn": stock['stock_sn']}
                if "approval_sn" in params and params["approval_sn"]:
                    pParams["approval_sn"] = params["approval_sn"]
                detail = st.get_stock_log(pParams)
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
                            result['modelList'][d['delng_sn']] = {"count": 0, "return_de": None, "return_place": None}
                        result['modelList'][d['delng_sn']]["count"] += 1
                        result['modelList'][d['delng_sn']]["return_de"] = candidateDate
                        result['modelList'][d['delng_sn']]["return_place"] = candidatePlace
                        break
                    candidate = False
                    candidateDate = None
                    candidatePlace = None

        result['after'] = []
        delng_sns = [acc['delng_sn'] for acc in result['model']]
        if delng_sns:
            g.curs.execute("SELECT log_sn, stock_sn, cnnc_sn FROM stock_log WHERE delng_sn IN ({})".format(
                ",".join(['%s'] * len(delng_sns))), delng_sns)
            stocks = g.curs.fetchall(transform=False)
            for stock in stocks:
                if stock['cnnc_sn'] is not None:
                    result['after'].append(stock['stock_sn'])
        return jsonify(result)

    except Exception as e:
        print(e)
        return make_response(str(e), 500)


@bp.route('/insert_equipment', methods=['POST'])
def insert_equipment():
    try:
        params = request.get_json()
        sales.insert_equipment(params)
        return jsonify({"status" : True, "message" : "성공적으로 처리되었습니다."})

    except Exception as e:
        print(e)
        return make_response(str(e), 500)


@bp.route('/insert_general_sales_NR', methods=['POST'])
def insert_general_sales_NR():
    try:
        params = request.get_json()
        sales.insert_general_sales_NR(params)
        return jsonify({"status" : True, "message" : "성공적으로 처리되었습니다."})
    except Exception as e:
        print(e)
        return make_response(str(e), 500)

@bp.route('/insert_general_sales_BD', methods=['POST'])
def insert_general_sales_BD():
    try:
        params = request.get_json()
        sales.insert_general_sales_BD(params)
        return jsonify({"status" : True, "message" : "성공적으로 처리되었습니다."})
    except Exception as e:
        print(e)
        return make_response(str(e), 500)

@bp.route('/insert_equipment_BD_samsung', methods=['POST'])
def insert_equipment_BD_samsung():
    try:
        params = request.get_json()
        sales.insert_equipment_BD_samsung(params)
        return jsonify({"status" : True, "message" : "성공적으로 처리되었습니다."})
    except Exception as e:
        print(e)
        return make_response(str(e), 500)

@bp.route('/insert_equipment_samsung', methods=['POST'])
def insert_equipment_samsung():
    try:
        params = request.get_json()
        sales.insert_equipment_samsung(params)
        return jsonify({"status" : True, "message" : "성공적으로 처리되었습니다."})
    except Exception as e:
        print(e)
        return make_response(str(e), 500)

@bp.route('/insert_equipment_other', methods=['POST'])
def insert_equipment_other():
    try:
        params = request.get_json()
        params["_type"] = "타사장비"
        sales.insert_equipment_samsung(params)
        return jsonify({"status" : True, "message" : "성공적으로 처리되었습니다."})
    except Exception as e:
        print(e)
        return make_response(str(e), 500)

@bp.route('/insert_equipment_sub', methods=['POST'])
def insert_equipment_sub():
    try:
        params = request.get_json()
        sales.insert_equipment_sub(params)
        return jsonify({"status" : True, "message" : "성공적으로 처리되었습니다."})
    except Exception as e:
        print(e)
        return make_response(str(e), 500)

@bp.route('/insert_equipment_other_sub', methods=['POST'])
def insert_equipment_other_sub():
    try:
        params = request.get_json()
        sales.insert_equipment_other_sub(params)
        return jsonify({"status" : True, "message" : "성공적으로 처리되었습니다."})
    except Exception as e:
        print(e)
        return make_response(str(e), 500)

@bp.route('/update_equipment', methods=['POST'])
def update_equipment():
    try:
        params = request.get_json()
        params["establish"] = False
        prj.insert_c_extra_project(params)
        del params["option_bigo"]
        sales.insert_equipment(params)
        return jsonify({"status" : True, "message" : "성공적으로 처리되었습니다."})
    except Exception as e:
        print(e)
        return make_response(str(e), 500)

@bp.route('/update_equipment_establish', methods=['POST'])
def update_equipment_establish():
    try:
        params = request.get_json()
        params["establish"] = True
        prj.insert_c_extra_project(params)
        sales.update_equipment_establish(params)
        return jsonify({"status" : True, "message" : "성공적으로 처리되었습니다."})
    except Exception as e:
        print(e)
        return make_response(str(e), 500)

@bp.route('/update_equipment_establish_new', methods=['POST'])
def update_equipment_establish_new():
    try:
        params = request.get_json()
        params["establish"] = True
        prj.insert_c_extra_project(params)
        sales.update_equipment_establish(params)

        del params["option_bigo"]
        sales.insert_equipment_new(params)
        return jsonify({"status" : True, "message" : "성공적으로 처리되었습니다."})


        return jsonify({"status" : True, "message" : "성공적으로 처리되었습니다."})
    except Exception as e:
        print(e)
        return make_response(str(e), 500)


@bp.route('/ajax_insert_direct', methods=['GET'])
def ajax_insert_direct():
    try:
        params = request.args.to_dict()
        sales.insert_direct(params)
        return jsonify({"status": True, "message" : "성공적으로 입력되었습니다."})
    except Exception as e:
        print(e)
        return make_response(str(e), 500)

@bp.route('/ajax_update_direct', methods=['GET'])
def ajax_update_direct():
    try:
        params = request.args.to_dict()
        sales.update_direct(params)
        return jsonify({"status": True, "message" : "성공적으로 수정되었습니다."})
    except Exception as e:
        print(e)
        return make_response(str(e), 500)

@bp.route('/ajax_update_account_expect_de', methods=['GET'])
def ajax_update_account_expect_de():
    try:
        params = request.args.to_dict()
        sales.update_account_expect_de(params)
        return jsonify({"status": True, "message" : "성공적으로 수정되었습니다."})
    except Exception as e:
        print(e)
        return make_response(str(e), 500)
