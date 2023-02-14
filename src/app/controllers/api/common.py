from flask import Blueprint, g, current_app, render_template, redirect, request, make_response, jsonify, send_file, Response, url_for, session
from .services import common_service as cm

from app.connectors import DB
from app.helpers import session_helper
from .services import set_menu
import json
import os
from datetime import datetime

bp = Blueprint('api_common', __name__, url_prefix='/api')

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

@bp.route('/work/ajax_get_work', methods=['GET'])
def ajax_get_work():
    params = request.args.to_dict()
    result = dict()
    result['data'] = cm.get_work(params)
    result['status'] = True
    return result