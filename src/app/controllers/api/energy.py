from flask import Blueprint, g, current_app, render_template, redirect, request, make_response, jsonify, send_file, Response, url_for, session
from .services import energy_service as eng
from app.connectors import DB
from app.helpers import session_helper
from .services import set_menu
import json
import os
from datetime import datetime
from pytz import timezone
bp = Blueprint('api_energy', __name__, url_prefix='/api/energy')
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


@bp.route('/ajax_get_energy_datatable', methods=['POST'])
def ajax_get_energy_datatable():
    try:
        params = request.form.to_dict()
        result = eng.get_energy_datatable(params)
        result['summary'] = eng.get_energy_summary(params)

        return jsonify(result)
    except Exception as e:
        print(e)
        return make_response(str(e), 500)

@bp.route('/ajax_get_energy', methods=['GET'])
def ajax_get_energy():
    try:
        params = request.args.to_dict()
        result = dict()
        result['data'] = eng.get_energy(params)
        result['status'] = True
        return jsonify(result)
    except Exception as e:
        print(e)
        return make_response(str(e), 500)

@bp.route('/ajax_get_plan_list', methods=['GET'])
def ajax_get_plan_list():
    try:
        params = request.args.to_dict()
        result = dict()
        result['data'] = eng.get_plan_list(params)
        result['status'] = True
        return jsonify(result)
    except Exception as e:
        print(e)
        return make_response(str(e), 500)

@bp.route('/ajax_get_exp_list', methods=['GET'])
def ajax_get_exp_list():
    try:
        params = request.args.to_dict()
        result = dict()
        result['data'] = eng.get_exp_list(params)
        result['plan'] = eng.get_plan_list(params)
        result['status'] = True
        return jsonify(result)
    except Exception as e:
        print(e)
        return make_response(str(e), 500)

@bp.route('/ajax_get_expP_list', methods=['GET'])
def ajax_get_expP_list():
    try:
        params = request.args.to_dict()
        result = dict()
        result['data'] = eng.get_expP_list(params)
        result['plan'] = eng.get_plan_list(params)
        result['status'] = True
        return jsonify(result)
    except Exception as e:
        print(e)
        return make_response(str(e), 500)

@bp.route('/ajax_get_exp_detail_list', methods=['GET'])
def ajax_get_exp_detail_list():
    try:
        params = request.args.to_dict()
        result = dict()
        result['data'] = eng.get_exp_detail_list(params)
        result['plan'] = eng.get_plan_list(params)
        result['status'] = True
        return jsonify(result)
    except Exception as e:
        print(e)
        return make_response(str(e), 500)

@bp.route('/ajax_get_expP_list2', methods=['GET'])
def ajax_get_expP_list2():
    try:
        params = request.args.to_dict()
        result = dict()
        result['data'] = eng.get_expP_list2(params)
        result['plan'] = eng.get_plan_list(params)
        result['status'] = True
        return jsonify(result)
    except Exception as e:
        print(e)
        return make_response(str(e), 500)


@bp.route('/ajax_insert_energy', methods=['POST'])
def ajax_insert_energy():
    try:
        params = request.form.to_dict()
        eng.insert_energybil(params)
        result = dict()
        result['debug'] = params
        result['status'] = True

        return jsonify(result)
    except Exception as e:
        print(e)
        return make_response(str(e), 500)



@bp.route('/ajax_update_energy', methods=['POST'])
def ajax_update_energy():
    try:
        params = request.form.to_dict()
        eng.update_energybil(params)
        result = dict()
        result['status'] = True

        return jsonify(result)
    except Exception as e:
        print(e)
        return make_response(str(e), 500)

@bp.route('/ajax_delete_energy', methods=['POST'])
def ajax_delete_energy():
    try:
        params = request.form.to_dict()
        eng.delete_energybil(params)
        result = dict()
        result['status'] = True

        return jsonify(result)
    except Exception as e:
        print(e)
        return make_response(str(e), 500)

@bp.route('/ajax_get_report', methods=['GET'])
def ajax_get_report():
    try:
        params = request.args.to_dict()
        result = dict()
        result['project'] = eng.get_energybil(params)
        result['plan'] = eng.get_plan_list(params)
        result['expense'] = eng.get_exp_list(params)
        result['detail'] = eng.get_exp_detail_list(params)
        result['ep'] = dict()
        for ep in eng.get_exp_plan_list(params):
            if ep['plan_order'] not in result['ep']:
                result['ep'][ep['plan_order']] = []
            result['ep'][ep['plan_order']].append(ep)
        result['rcppayList'] = eng.get_rcppay_report_list(params)
        result['status'] = True
        return jsonify(result)
    except Exception as e:
        print(e)
        return make_response(str(e), 500)


@bp.route('/ajax_get_plan', methods=['GET'])
def ajax_get_plan():
    try:
        params = request.args.to_dict()
        result = dict()
        result['data'] = eng.get_plan(params)
        result['status'] = True
        return jsonify(result)
    except Exception as e:
        print(e)
        return make_response(str(e), 500)

@bp.route('/ajax_insert_plan', methods=['POST'])
def ajax_insert_plan():
    try:
        params = request.form.to_dict()
        eng.insert_plan(params)
        result = dict()
        result['status'] = True
        return jsonify(result)
    except Exception as e:
        print(e)
        return make_response(str(e), 500)

@bp.route('/ajax_update_plan', methods=['POST'])
def ajax_update_plan():
    try:
        params = request.form.to_dict()
        eng.update_plan(params)
        result = dict()
        result['status'] = True
        return jsonify(result)
    except Exception as e:
        print(e)
        return make_response(str(e), 500)

@bp.route('/ajax_delete_plan', methods=['GET'])
def ajax_delete_plan():
    try:
        params = request.args.to_dict()
        eng.delete_plan(params)
        result = dict()
        result['status'] = True
        return jsonify(result)
    except Exception as e:
        print(e)
        return make_response(str(e), 500)

@bp.route('/ajax_delete_exp', methods=['GET'])
def ajax_delete_exp():
    try:
        params = request.args.to_dict()
        eng.delete_exp(params)
        result = dict()
        result['status'] = True
        return jsonify(result)
    except Exception as e:
        print(e)
        return make_response(str(e), 500)

@bp.route('/ajax_delete_expP', methods=['GET'])
def ajax_delete_expP():
    try:
        params = request.args.to_dict()
        eng.delete_expP(params)
        result = dict()
        result['status'] = True
        return jsonify(result)
    except Exception as e:
        print(e)
        return make_response(str(e), 500)

@bp.route('/ajax_delete_expP2', methods=['GET'])
def ajax_delete_expP2():
    try:
        params = request.args.to_dict()
        eng.delete_expP2(params)
        result = dict()
        result['status'] = True
        return jsonify(result)
    except Exception as e:
        print(e)
        return make_response(str(e), 500)

@bp.route('/ajax_delete_exp_detail', methods=['GET'])
def ajax_delete_exp_detail():
    try:
        params = request.args.to_dict()
        eng.delete_exp_detail(params)
        result = dict()
        result['status'] = True
        return jsonify(result)
    except Exception as e:
        print(e)
        return make_response(str(e), 500)

@bp.route('/ajax_get_exp', methods=['GET'])
def ajax_get_exp():
    try:
        params = request.args.to_dict()
        result = dict()
        result['data'] = eng.get_exp(params)
        result['status'] = True
        return jsonify(result)
    except Exception as e:
        print(e)
        return make_response(str(e), 500)

@bp.route('/ajax_get_expP', methods=['GET'])
def ajax_get_expP():
    try:
        params = request.args.to_dict()
        result = dict()
        result['data'] = eng.get_expP(params)
        result['status'] = True
        return jsonify(result)
    except Exception as e:
        print(e)
        return make_response(str(e), 500)

@bp.route('/ajax_get_expP2', methods=['GET'])
def ajax_get_expP2():
    try:
        params = request.args.to_dict()
        result = dict()
        result['data'] = eng.get_expP2(params)
        result['status'] = True
        return jsonify(result)
    except Exception as e:
        print(e)
        return make_response(str(e), 500)

@bp.route('/ajax_get_exp_detail', methods=['GET'])
def ajax_get_exp_detail():
    try:
        params = request.args.to_dict()
        result = dict()
        result['data'] = eng.get_exp_detail_list(params)
        result['plan'] = eng.get_plan_list(params)
        result['status'] = True
        return jsonify(result)
    except Exception as e:
        print(e)
        return make_response(str(e), 500)

@bp.route('/ajax_insert_exp', methods=['POST'])
def ajax_insert_exp():
    try:
        params = request.form.to_dict()
        eng.insert_exp(params)
        result = dict()
        result['status'] = True
        return jsonify(result)
    except Exception as e:
        print(e)
        return make_response(str(e), 500)

@bp.route('/ajax_insert_exp_detail', methods=['POST'])
def ajax_insert_exp_detail():
    try:
        params = request.form.to_dict()
        eng.insert_exp_detail(params)
        result = dict()
        result['status'] = True
        return jsonify(result)
    except Exception as e:
        print(e)
        return make_response(str(e), 500)

@bp.route('/ajax_update_exp', methods=['POST'])
def ajax_update_exp():
    try:
        params = request.form.to_dict()
        eng.update_exp(params)
        result = dict()
        result['status'] = True
        return jsonify(result)
    except Exception as e:
        print(e)
        return make_response(str(e), 500)

@bp.route('/ajax_update_exp_detail', methods=['POST'])
def ajax_update_exp_detail():
    try:
        params = request.form.to_dict()
        eng.update_exp_detail(params)
        result = dict()
        result['status'] = True
        return jsonify(result)
    except Exception as e:
        print(e)
        return make_response(str(e), 500)

@bp.route('/ajax_update_expP', methods=['POST'])
def ajax_update_expP():
    try:
        params = request.form.to_dict()
        params["exp_cost"] = request.form.getlist("exp_cost[]")
        eng.update_expP(params)
        result = dict()
        result['status'] = True
        return jsonify(result)
    except Exception as e:
        print(e)
        return make_response(str(e), 500)

@bp.route('/ajax_update_expP2', methods=['POST'])
def ajax_update_expP2():
    try:
        params = request.form.to_dict()
        params["exp_cost"] = request.form.getlist("exp_cost[]")
        eng.update_expP2(params)
        result = dict()
        result['status'] = True
        return jsonify(result)
    except Exception as e:
        print(e)
        return make_response(str(e), 500)

@bp.route('/ajax_insert_expP', methods=['POST'])
def ajax_insert_expP():
    try:
        params = request.form.to_dict()
        params["exp_cost"] = request.form.getlist("exp_cost[]")
        eng.insert_expP(params)
        result = dict()
        result['status'] = True
        return jsonify(result)
    except Exception as e:
        print(e)
        return make_response(str(e), 500)

@bp.route('/ajax_insert_expP2', methods=['POST'])
def ajax_insert_expP2():
    try:
        params = request.form.to_dict()
        params["exp_cost"] = request.form.getlist("exp_cost[]")
        eng.insert_expP2(params)
        result = dict()
        result['status'] = True
        return jsonify(result)
    except Exception as e:
        print(e)
        return make_response(str(e), 500)
