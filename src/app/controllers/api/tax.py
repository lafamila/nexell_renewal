from flask import Blueprint, g, current_app, render_template, redirect, request, make_response, jsonify, send_file, Response, url_for, session
from .services import tax_service as tx
from .services import project_service as prj

from app.connectors import DB
from app.helpers import session_helper
from .services import set_menu
import json
import os
from datetime import datetime

from pytz import timezone

bp = Blueprint('api_tax', __name__, url_prefix='/api/tax')
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

@bp.route('/ajax_get_tax_datatable', methods=['POST'])
def ajax_get_tax_datatable():
    try:
        params = request.form.to_dict()
        result = tx.get_taxbil_datatable(params)
        result['summary'] = tx.get_taxbil_summary(params)
        return jsonify(result)
    except Exception as e:
        print(e)
        return make_response(str(e), 500)

@bp.route('/ajax_get_tax', methods=['GET'])
def ajax_get_tax():
    try:
        params = request.args.to_dict()
        result = dict()
        result['data'] = tx.get_taxbil(params)
        result['status'] = True
        return jsonify(result)
    except Exception as e:
        print(e)
        return make_response(str(e), 500)

@bp.route('/ajax_insert_tax', methods=['POST'])
def ajax_insert_tax():
    try:
        params = request.form.to_dict()
        tx.insert_taxbil(params)
        return jsonify({"status" : True, "message" : "성공적으로 입력되었습니다."})
    except Exception as e:
        print(e)
        return make_response(str(e), 500)


@bp.route('/ajax_update_tax', methods=['POST'])
def ajax_update_tax():
    try:
        params = request.form.to_dict()
        tx.update_taxbil(params)
        return jsonify({"status" : True, "message" : "성공적으로 수정되었습니다."})
    except Exception as e:
        print(e)
        return make_response(str(e), 500)


@bp.route('/ajax_delete_tax', methods=['POST'])
def ajax_delete_tax():
    try:
        params = request.form.to_dict()
        tx.delete_taxbil(params)
        return jsonify({"status" : True, "message" : "성공적으로 삭제되었습니다."})
    except Exception as e:
        print(e)
        return make_response(str(e), 500)

@bp.route('/ajax_get_tax_list', methods=['GET'])
def ajax_get_tax_list():
    try:
        params = request.args.to_dict()
        result = dict()
        result['tax'] = tx.get_taxbil_list(params)
        result['status'] = True
        return jsonify(result)
    except Exception as e:
        print(e)
        return make_response(str(e), 500)
