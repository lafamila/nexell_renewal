from flask import Blueprint, g, current_app, render_template, redirect, request, make_response, jsonify, send_file, Response, url_for, session
from .services import sales_service as sales
from .services import project_service as prj
from .services import stock_service as st

from app.connectors import DB
from app.helpers import session_helper
from .services import set_menu
import json
import os
from datetime import datetime

bp = Blueprint('api_sales', __name__, url_prefix='/api/sales')

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

@bp.route('/ajax_get_sales_datatable', methods=['POST'])
def ajax_get_sales_datatable():
    params = request.form.to_dict()
    result = sales.get_sales_datatable(params)
    result['summary'] = sales.get_sales_summary(params)
    return jsonify(result)

@bp.route('/ajax_get_inventory', methods=['GET'])
def ajax_get_inventory():
    params = request.args.to_dict()
    result = dict()
    result['sales'] = sales.get_account_list2(params)
    result['status'] = True
    return jsonify(result)

@bp.route('/ajax_get_sales', methods=['GET'])
def ajax_get_sales():
    params = request.args.to_dict()
    result = dict()
    result['data'] = sales.get_account(params)
    result['status'] = True
    return jsonify(result)

@bp.route('/ajax_insert_sales', methods=['POST'])
def ajax_insert_sales():
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

@bp.route('/ajax_update_sales', methods=['POST'])
def ajax_update_sales():
    params = request.form.to_dict()
    sales.update_account(params)
    return jsonify({"status": True, "message": "성공적으로 변경되었습니다."})

@bp.route('/ajax_delete_sales', methods=['POST'])
def ajax_delete_sales():
    params = request.form.to_dict()
    sales.delete_account(params)
    return jsonify({"status": True, "message": "성공적으로 삭제되었습니다."})

@bp.route('/ajax_get_contract', methods=['GET'])
def ajax_get_contract():
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
    return result