from flask import Blueprint, g, current_app, render_template, redirect, request, make_response, jsonify, send_file, Response, url_for, session
from .services import fund_service as fnd
from .services import project_service as prj

from app.connectors import DB
from app.helpers import session_helper
from .services import set_menu
import json
import os
from datetime import datetime

bp = Blueprint('api_fund', __name__, url_prefix='/api/fund')
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

@bp.route('/ajax_get_fund_datatable', methods=['POST'])
def ajax_get_fund_datatable():
    try:
        params = request.form.to_dict()
        result = fnd.get_rcppay_datatable(params)
        result['eSummary'] = fnd.get_rcppay_summary(params, exist=True)
        result['nSummary'] = fnd.get_rcppay_summary(params, exist=False)
        return jsonify(result)
    except Exception as e:
        print(e)
        return make_response(str(e), 500)

@bp.route('/ajax_get_fund', methods=['GET'])
def ajax_get_fund():
    try:
        params = request.args.to_dict()
        result = dict()
        result['data'] = fnd.get_rcppay(params)
        result['status'] = True
        return jsonify(result)
    except Exception as e:
        print(e)
        return make_response(str(e), 500)

@bp.route('/ajax_insert_fund', methods=['POST'])
def ajax_insert_fund():
    try:
        params = request.form.to_dict()
        fnd.insert_rcppay(params)
        return jsonify({"status": True, "message": "성공적으로 입력되었습니다."})
    except Exception as e:
        print(e)
        return make_response(str(e), 500)

@bp.route('/ajax_update_fund', methods=['POST'])
def ajax_update_fund():
    try:
        params = request.form.to_dict()
        fnd.update_rcppay(params)
        return jsonify({"status": True, "message": "성공적으로 수정되었습니다."})
    except Exception as e:
        print(e)
        return make_response(str(e), 500)

@bp.route('/ajax_delete_fund', methods=['POST'])
def ajax_delete_fund():
    try:
        params = request.form.to_dict()
        fnd.delete_rcppay(params)
        return jsonify({"status" : True, "message" : "성공적으로 삭제되었습니다."})
    except Exception as e:
        print(e)
        return make_response(str(e), 500)

@bp.route('/ajax_delete_fund_many', methods=['POST'])
def ajax_delete_fund_many():
    try:
        params = request.get_json()
        fnd.delete_rcppay_many(params)
        return jsonify({"status" : True, "message" : "성공적으로 삭제되었습니다."})
    except Exception as e:
        print(e)
        return make_response(str(e), 500)

@bp.route('/ajax_copy_funds', methods=['POST'])
def ajax_copy_funds():
    try:
        params = request.get_json()
        fnd.copy_rcppays(params)
        return jsonify({"status" : True, "message" : "성공적으로 복사되었습니다."})
    except Exception as e:
        print(e)
        return make_response(str(e), 500)


@bp.route('/ajax_get_fund_report', methods=['GET'])
def ajax_get_fund_report():
    try:
        params = request.args.to_dict()
        result = dict()
        if "s_rcppay_de" in params and params["s_rcppay_de"]:
            y, m, d = map(int, params["s_rcppay_de"].split("-"))
            result['date'] = "{}년 {}월 {}일".format(y, m, d)

        result['list'] = fnd.get_report(params)
        result['summary1'] = fnd.get_rcppay_summary1(params)
        result['summary11'] = fnd.get_rcppay_summary11(params)
        result['summary2'] = fnd.get_rcppay_summary2(params)
        result['s1'] = fnd.get_rcppay_summary_s1(params)
        result['s2'] = fnd.get_rcppay_summary_s2(params)
        result['status'] = True
        return jsonify(result)
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
        result['status'] = True
        return jsonify(result)
    except Exception as e:
        print(e)
        return make_response(str(e), 500)

@bp.route('/ajax_get_fund_datatable1', methods=['POST'])
def ajax_get_fund_datatable1():
    try:
        params = request.form.to_dict()
        result = fnd.get_fund_stat_datatable1(params)
        result['summary1'] = fnd.get_fund_stat_summary1(params)
        result['status'] = True
        return jsonify(result)
    except Exception as e:
        print(e)
        return make_response(str(e), 500)

@bp.route('/ajax_get_fund_datatable2', methods=['POST'])
def ajax_get_fund_datatable2():
    try:
        params = request.form.to_dict()
        result = fnd.get_fund_stat_datatable2(params)
        result['summary2'] = fnd.get_fund_stat_summary2(params)
        result['status'] = True
        return jsonify(result)
    except Exception as e:
        print(e)
        return make_response(str(e), 500)

@bp.route('/ajax_insert_memo', methods=['GET'])
def ajax_insert_memo():
    try:
        params = request.args.to_dict()
        fnd.insert_memo(params)
        return jsonify({"status": True, "message" : "성공적으로 입력되었습니다."})
    except Exception as e:
        print(e)
        return make_response(str(e), 500)

@bp.route('/ajax_get_memo_list2', methods=['GET'])
def ajax_get_memo_list2():
    try:
        params = request.args.to_dict()
        result = dict()
        result['memo_list'] = fnd.get_memo_list2(params)
        result['status'] = True
        return jsonify(result)
    except Exception as e:
        print(e)
        return make_response(str(e), 500)

@bp.route('/ajax_get_values', methods=['GET'])
def ajax_get_values():
    try:
        params = request.args.to_dict()
        result = dict()
        result['temp'] = fnd.get_values(params)
        result['status'] = True
        return jsonify(result)
    except Exception as e:
        print(e)
        return make_response(str(e), 500)
