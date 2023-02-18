from flask import Blueprint, g, current_app, render_template, redirect, request, make_response, jsonify, send_file, Response, url_for, session
from .services import work_service as wk
from .services import project_service as prj

from app.connectors import DB
from app.helpers import session_helper
from .services import set_menu
import json
import os
from datetime import datetime

bp = Blueprint('api_work', __name__, url_prefix='/api/work')

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

@bp.route('/ajax_get_work', methods=['GET'])
def ajax_get_work():
    params = request.args.to_dict()
    result = dict()
    result['data'] = wk.get_work(params)
    result['status'] = True
    return jsonify(result)

@bp.route('/ajax_get_year_datatable', methods=['POST'])
def ajax_get_year_datatable():
    params = request.form.to_dict()
    result = wk.get_work_datatable(params)
    # result = dict()
    # result['data'] = []
    return jsonify(result)

@bp.route('/ajax_set_work_data', methods=['GET'])
def ajax_set_work_data():
    params = request.args.to_dict()
    wk.set_work_data(params)
    return jsonify({"status" : True, "message" : "성공적으로 변경되었습니다."})

