from flask import Blueprint, g, current_app, render_template, redirect, request, make_response, jsonify, send_file, Response, url_for, session
from .services import member_service as mber
from .services import approval_service as apvl
from app.connectors import DB
from app.helpers import session_helper
from .services import set_menu
import json
import os
from datetime import datetime

bp = Blueprint('api_approval', __name__, url_prefix='/api/approval')
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


@bp.route('/ajax_get_approval_datatable', methods=['POST'])
def ajax_get_project_datatable():
    params = request.form.to_dict()
    result = apvl.get_approval_datatable(params)
    return jsonify(result)

@bp.route('/ajax_get_approval_ty_list', methods=['GET'])
def ajax_get_approval_ty_list():
    params = request.args.to_dict()
    result = apvl.get_approval_ty_list(params)
    return jsonify(result)


@bp.route('/ajax_get_approval_template', methods=['GET'])
def get_approval_template():
    params = request.args.to_dict()
    html = apvl.get_approval_template(params['url'])
    return jsonify({"html" : html})

@bp.route('/ajax_insert_approval', methods=['POST'])
def ajax_insert_approval():
    params = request.get_json()
    json_data = params['data']
    params['data'] = json.dumps(json_data)
    apvl_sn = apvl.insert_approval(params)
    params['apvl_sn'] = apvl_sn
    apvl.insert_approval_member(params)
    print(params)