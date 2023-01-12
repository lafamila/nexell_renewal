from flask import Blueprint, g, current_app, render_template, redirect, request, make_response, jsonify, send_file, Response, url_for, session
from .services import member_service as mber
from src.app.connectors import DB
from src.app.helpers import session_helper
from .services import get_menu
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
    g.db.commit()

    g.curs.close()
    g.db.close()
    return response

@bp.route('/query', methods=['POST'])
def query():
    query = request.form.get("query")
    result = '"""'
    for line in query.split("\n"):
        if len(line.strip()) > 0:
            result += line.strip().replace("$sql", "").replace('.=', '').replace('"', '').replace(";", "").strip() + "\n"
    result += '"""'
    return jsonify({"text" : result})