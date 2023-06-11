from flask import Blueprint, g, current_app, render_template, redirect, request, make_response, jsonify, send_file, Response, url_for, session
from .services import energy_service as eng
from app.connectors import DB
from app.helpers import session_helper
from .services import set_menu
import json
import os
from datetime import datetime

bp = Blueprint('api_energy', __name__, url_prefix='/api/energy')
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


@bp.route('/ajax_get_energy_datatable', methods=['POST'])
def ajax_get_energy_datatable():
    try:
        params = request.form.to_dict()
        result = eng.get_energy_datatable(params)
        result['summary'] = eng.get_energy_summary(params)

        return jsonify(result)
    except Exception as e:
        return make_response(str(e), 500)

@bp.route('/ajax_get_energy', methods=['GET'])
def ajax_get_energy():
    try:
        params = request.args.to_dict()
        result = dict()
        result['data'] = eng.get_energy(params)
        return jsonify(result)
    except Exception as e:
        return make_response(str(e), 500)

@bp.route('/ajax_get_plan_list', methods=['GET'])
def ajax_get_plan_list():
    try:
        params = request.args.to_dict()
        result = dict()
        result['data'] = eng.get_plan_list(params)
        return jsonify(result)
    except Exception as e:
        return make_response(str(e), 500)

@bp.route('/ajax_get_exp_list', methods=['GET'])
def ajax_get_exp_list():
    try:
        params = request.args.to_dict()
        result = dict()
        result['data'] = eng.get_exp_list(params)
        result['plan'] = eng.get_plan_list(params)
        return jsonify(result)
    except Exception as e:
        return make_response(str(e), 500)
