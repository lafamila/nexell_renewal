from flask import Blueprint, g, current_app, render_template, redirect, request, make_response, jsonify, send_file, Response, url_for, session
from .services import completed_service as cp
from .services import dashboard_service as db
from .services import approval_service as apvl
from app.connectors import DB
from app.helpers import session_helper
from .services import set_menu
import json
import os
from datetime import datetime

bp = Blueprint('api_dashboard', __name__, url_prefix='/api/dashboard')
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

@bp.route('/ajax_get_completed_sales', methods=['GET'])
def ajax_get_completed_sales():
    params = request.args.to_dict()
    if "s_pxcond_mt" not in params:
        params['s_pxcond_mt'] = datetime.now().strftime("%Y-%m-%d")
    result = dict()
    result['data'] = db.get_completed_sales(params)
    return jsonify(result)

@bp.route('/ajax_get_completed_suju', methods=['GET'])
def ajax_get_completed_suju():
    params = request.args.to_dict()
    if "s_pxcond_mt" not in params:
        params['s_pxcond_mt'] = datetime.now().strftime("%Y-%m-%d")
    result = dict()
    result['data'] = db.get_completed_suju(params)
    return jsonify(result)

@bp.route('/ajax_get_completed_suju_b', methods=['GET'])
def ajax_get_completed_suju_b():
    params = request.args.to_dict()
    if "s_pxcond_mt" not in params:
        params['s_pxcond_mt'] = datetime.now().strftime("%Y-%m-%d")
    result = dict()
    result['data'] = db.get_completed_suju_b(params)
    return jsonify(result)

@bp.route('/ajax_get_completed_year_summary', methods=['GET'])
def ajax_get_completed_year_summary():
    params = request.args.to_dict()
    result = dict()
    result['data'] = list()
    result['data'].append(db.get_kisung_suju(params))
    result['data'].append(db.get_kisung_sales(params))
    result['data'].append(db.get_kisung_va(params))
    return jsonify(result)

@bp.route('/ajax_get_completed_summary', methods=['GET'])
def ajax_get_completed_summary():
    params = request.args.to_dict()
    if "s_pxcond_mt" not in params:
        params['s_pxcond_mt'] = datetime.now().strftime("%Y-%m-%d")
    result = dict()
    result['contractStatusList'] = cp.get_completed_summary(params)
    result['s_pxcond_mt'] = params['s_pxcond_mt']
    result['status'] = True
    return jsonify(result)

@bp.route('/ajax_get_biss_state', methods=['GET'])
def ajax_get_biss_state():
    params = request.args.to_dict()
    result = dict()

    result['list'] = db.get_biss_summery(params)
    result['data'] = db.get_all_member_project(params)
    result['status'] = True
    return jsonify(result)

@bp.route('/ajax_get_sales_summary', methods=['GET'])
def ajax_get_sales_summary():
    params = request.args.to_dict()
    result = dict()

    result['list'] = db.get_sales_summery(params)
    result['one'] = db.get_sales_one_summery(params)
    result['status'] = True
    return jsonify(result)

@bp.route('/ajax_get_projects_by_dept_member', methods=['GET'])
def ajax_get_projects_by_dept_member():
    params = request.args.to_dict()
    result = dict()
    result['data'] = db.get_projects_by_dept_member(params)
    return jsonify(result)

@bp.route('/ajax_get_month_report', methods=['GET'])
def ajax_get_month_report():
    params = request.args.to_dict()
    if "s_pxcond_mt" not in params:
        params['s_pxcond_mt'] = datetime.now().strftime("%Y-%m-%d")
    result = dict()
    result['contractStatusList'] = cp.get_completed_summary(params)
    params["s_stdyy"], params["s_month"], _ = map(int, params['s_pxcond_mt'].split("-"))
    params["s_pxcond_m"] = "-".join(params['s_pxcond_mt'].split("-")[:2])
    contracts = db.get_goal_contract(params)
    result['contractList'] = dict()
    for c in contracts:
        if c['dept_code'] not in result['contractList']:
            result['contractList'][c['dept_code']] = dict()
        if c['amt_ty_code'] not in result['contractList'][c['dept_code']]:
            result['contractList'][c['dept_code']][c['amt_ty_code']] = list()
        result['contractList'][c['dept_code']][c['amt_ty_code']].append(c)
    for r in result['contractStatusList']:
        if r['dept_code'] not in result['contractList']:
            result['contractList'][r['dept_code']] = dict()
    return jsonify(result)

@bp.route('/ajax_set_dashboard_data', methods=['GET'])
def ajax_set_dashboard_data():
    params = request.args.to_dict()
    db.set_dashboard_data(params)
    return jsonify({"status" : True, "message" : "??????????????? ?????????????????????."})
