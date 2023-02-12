from flask import Blueprint, g, current_app, render_template, redirect, request, make_response, jsonify, send_file, Response, url_for, session
from .services import project_service as prj
from .services import member_service as mber
from .services import stock_service as st
from app.connectors import DB
from app.helpers import session_helper
from .services import set_menu
import json
import os
from datetime import datetime

bp = Blueprint('api_stock', __name__, url_prefix='/api/stock')

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


@bp.route('ajax_get_inventory_datatable_ts', methods=['POST'])
def ajax_get_inventory_datatable_ts():
    params = request.form.to_dict()
    result = st.get_stock_datatable(params, "TS")
    result['summary'] = st.get_stock_summary(params, "TS")
    return jsonify(result)
@bp.route('ajax_get_inventory_datatable_bi', methods=['POST'])
def ajax_get_inventory_datatable_bi():
    params = request.form.to_dict()
    result = st.get_stock_datatable(params, "BI")
    result['summary'] = st.get_stock_summary(params, "BI")

    return jsonify(result)