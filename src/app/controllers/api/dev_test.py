from flask import Blueprint, g, current_app, render_template, redirect, request, make_response, jsonify, send_file, Response, url_for, session
from .services import member_service as mber
from app.connectors import DB
from app.helpers import session_helper
from .services import set_menu
import json
import os
from datetime import datetime

bp = Blueprint('test', __name__, url_prefix='/api')
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

@bp.route('/query', methods=['POST'])
def query():
    query = request.form.get("query")
    result = '"""'
    for i, line in enumerate(query.split("\n")):
        if len(line.strip()) > 0:
            if i > 0:
                result += '\t\t\t\t'
            result += line.strip().replace("$sql", "").replace('.=', '').replace('"', '').replace('{$s_ctmmny_sn}', "'1'").replace("%", "%%").replace(";", "").strip() + "\n"
    result += '"""'
    return jsonify({"text" : result})

@bp.route('/subquery', methods=['POST'])
def subquery():
    data = request.get_json()
    result = ""
    for d in data:
        if not d['like']:
            result += """    if "{0}" in params and params['{0}']:
        query += " AND {1}=%s"
        data.append(params["{0}"])""".format(d["data"], d["column"])
        else:
            result += """    if "{0}" in params and params['{0}']:
        query += " AND {1} LIKE %s"
        data.append('%{{}}%'.format(params["{0}"]))""".format(d["data"], d["column"])
        result += "\n\n"
    return jsonify({"text" : result})