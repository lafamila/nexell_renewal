from flask import Blueprint, g, current_app, render_template, redirect, request, make_response, jsonify, send_file, Response, url_for, session
from .services import card_service as cd
from .services import project_service as prj
from .services import get_code_list
from app.connectors import DB
from app.helpers import session_helper
from .services import set_menu
import json
import os
from datetime import datetime

bp = Blueprint('api_card', __name__, url_prefix='/api/card')
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

@bp.route('/ajax_get_card_datatable', methods=['POST'])
def ajax_get_card_datatable():
    try:
        params = request.form.to_dict()
        result = cd.get_cardbil_datatable(params)
        result['summary'] = cd.get_cardbil_summary(params)
        result['status'] = True
        return jsonify(result)
    except Exception as e:
        return make_response(str(e), 500)

@bp.route('/ajax_get_card', methods=['GET'])
def ajax_get_card():
    try:
        params = request.args.to_dict()
        result = dict()
        result['data'] = cd.get_cardbil(params)
        result['status'] = True
        return jsonify(result)
    except Exception as e:
        return make_response(str(e), 500)

@bp.route('/ajax_insert_card', methods=['POST'])
def ajax_insert_card():
    try:
        params = request.form.to_dict()
        cd.insert_cardbil(params)
        return jsonify({"status": True, "message": "성공적으로 입력되었습니다."})
    except Exception as e:
        return make_response(str(e), 500)


@bp.route('/ajax_update_card', methods=['POST'])
def ajax_update_card():
    try:
        params = request.form.to_dict()
        cd.update_cardbil(params)
        return jsonify({"status": True, "message": "성공적으로 수정되었습니다."})
    except Exception as e:
        return make_response(str(e), 500)


@bp.route('/ajax_delete_card', methods=['POST'])
def ajax_delete_card():
    try:
        params = request.form.to_dict()
        cd.delete_cardbil(params)
        return jsonify({"status": True, "message": "성공적으로 삭제되었습니다."})
    except Exception as e:
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
        return make_response(str(e), 500)


@bp.route('/ajax_get_card_dashboard', methods=['GET'])
def ajax_get_card_dashboard():
    try:
        params = request.args.to_dict()
        result = dict()
        result['data'] = cd.get_card_dashboard(params)
        result['title'] = "연간 카드 지출 내역"
        result['status'] = True
        return jsonify(result)
    except Exception as e:
        return make_response(str(e), 500)

@bp.route('/ajax_get_card_report', methods=['GET'])
def ajax_get_card_report():
    try:
        params = request.args.to_dict()
        result = dict()
        result['data'] = dict()
        for code in get_code_list('card_code'.upper()):
            label = code['label']
            result['data'][label] = dict()
            result['data'][label]['rows'] = cd.get_report(params, code['value'])
            result['data'][label]['total'] = cd.get_total(params, code['value'])

        if "card_de" in params and params['card_de']:
            result['title'] = "{}월 카드 지출 내역".format(int(params["card_de"].split("-")[1]))
        result['status'] = True
        return jsonify(result)
    except Exception as e:
        return make_response(str(e), 500)

@bp.route('/ajax_get_card_dashboard_year', methods=['GET'])
def ajax_get_card_dashboard_year():
    try:
        params = request.args.to_dict()
        result = dict()
        result['data'] = cd.get_card_dashboard_year(params)
        result['title'] = "연간 부서별 카드 지출 내역"
        result['status'] = True
        return jsonify(result)
    except Exception as e:
        return make_response(str(e), 500)
