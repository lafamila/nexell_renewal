from flask import Blueprint, g, current_app, render_template, redirect, request, make_response, jsonify, send_file, Response, url_for, session
from .services import project_service as prj
from .services import member_service as mber
from .services import stock_service as st
from app.connectors import DB
from app.helpers import session_helper
from .services import set_menu
import json
import os
from datetime import datetime

bp = Blueprint('api_stock', __name__, url_prefix='/api/stock')

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


@bp.route('/ajax_get_inventory_datatable_ts', methods=['POST'])
def ajax_get_inventory_datatable_ts():
    params = request.form.to_dict()
    result = st.get_stock_datatable(params, 1)
    result['summary'] = st.get_stock_summary(params, 1)
    return jsonify(result)
@bp.route('/ajax_get_inventory_datatable_bi', methods=['POST'])
def ajax_get_inventory_datatable_bi():
    params = request.form.to_dict()
    result = st.get_stock_datatable(params, 2)
    result['summary'] = st.get_stock_summary(params, 2)

    return jsonify(result)

@bp.route('/ajax_get_stock_log', methods=['GET'])
def ajax_get_stock_log():
    params = request.args.to_dict()
    result = dict()
    result['summary'] = st.get_stock(params)
    result['log'] = st.get_stock_log(params)
    result['status'] = True
    return jsonify(result)

@bp.route('/ajax_get_stock_list', methods=['GET'])
def ajax_get_stock_list():
    params = request.args.to_dict()
    result = dict()
    result['data'] = st.get_stock_list(params, None)
    result['mData'] = st.get_stock_list(params, None, reserved=True)
    result['status'] = True
    return jsonify(result)

@bp.route('/ajax_get_stock_list_bi', methods=['GET'])
def ajax_get_stock_list_bi():
    params = request.args.to_dict()
    result = dict()
    result['data'] = st.get_stock_list(params, 2)
    result['mData'] = st.get_stock_list(params, 2, reserved=True)
    result['status'] = True
    return jsonify(result)

@bp.route('/ajax_get_stock_list_ts', methods=['GET'])
def ajax_get_stock_list_ts():
    params = request.args.to_dict()
    result = dict()
    result['data'] = st.get_stock_list(params, 1)
    result['mData'] = st.get_stock_list(params, 1, reserved=True)
    result['status'] = True
    return jsonify(result)

@bp.route('/ajax_get_contract', methods=['GET'])
def ajax_get_contract():
    params = request.args.to_dict()
    result = dict()
    result['data'] = prj.get_contract(params)
    if result['data']:
        extra_params = dict()
        extra_params['s_cntrct_sn'] = result['data']['cntrct_sn']
        result['inventory'] = st.get_out_list(extra_params)
    result['status'] = True
    return jsonify(result)

@bp.route('/ajax_insert_delete', methods=['POST'])
def ajax_insert_delete():
    params = request.form.to_dict()
    item_sns = request.form.getlist("item_sn[]")
    for item_sn in item_sns:
        st.insert_log(item_sn, 4, None, None, params['ddt_man'])
        st.update_stock_rm(item_sn, params['rm'])
    return jsonify({"status": True, "message": "성공적으로 처리되었습니다."})

@bp.route('/ajax_insert_memo', methods=['POST'])
def ajax_insert_memo():
    params = request.form.to_dict()
    item_sns = request.form.getlist("item_sn[]")
    for item_sn in item_sns:
        st.update_stock_rm(item_sn, params['rm'])
    return jsonify({"status": True, "message": "성공적으로 처리되었습니다."})

@bp.route('/ajax_insert_return', methods=['POST'])
def ajax_insert_return():
    params = request.form.to_dict()
    item_sns = request.form.getlist("item_sn[]")
    for item_sn in item_sns:
        st.insert_log(item_sn, 1, params['invn_sttus_code'], None, params['ddt_man'])
    return jsonify({"status": True, "message": "성공적으로 처리되었습니다."})

@bp.route('/ajax_get_stock_report', methods=['GET'])
def ajax_get_stock_report():
    params = request.args.to_dict()
    result = dict()
    result['summary'] = st.get_stock_report(params)
    result['list'] = st.get_stock_report_list(params)

    return result