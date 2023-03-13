from flask import Blueprint, g, current_app, render_template, redirect, request, make_response, jsonify, send_file, Response, url_for, session
from .services import goal_service as gl
from .services import get_member_list, get_contract_list

from app.connectors import DB
from app.helpers import session_helper
from .services import set_menu
import json
import os
from datetime import datetime

bp = Blueprint('api_goal', __name__, url_prefix='/api/goal')

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

@bp.route('/ajax_get_goals_datatable', methods=['POST'])
def ajax_get_goals_datatable():
    params = request.form.to_dict()
    members = get_member_list()
    contracts = gl.get_contract_list_by_amt(params)
    contracts_by_member = dict()
    for c in contracts:
        chrg_sn = c['spt_chrg_sn'] if params['s_amt_ty_code'] != '2' else c['bsn_chrg_sn']
        if chrg_sn not in contracts_by_member:
            contracts_by_member[chrg_sn] = list()
        contracts_by_member[chrg_sn].append(c)

    for m in members:
        if m["value"] not in contracts_by_member:
            continue
        cs = contracts_by_member[m["value"]]
        cntrct_sns = set([c["value"] for c in cs if c["progrs_sttus_code"] != 'B'])
        params["chrg_sn"] = m["value"]
        r_cs = gl.get_goals_by_member(params)
        reg_cntrct_sns = set([r["cntrct_sn"] for r in r_cs])
        remain = list(cntrct_sns - reg_cntrct_sns)
        if remain:
            gl.insert_goals(params, remain)
    result = gl.get_goals(params)
    result['summary'] = gl.get_goals_summary(params)
    return result

@bp.route('/ajax_get_contracts_by_member', methods=['POST'])
def ajax_get_contracts_by_member():
    params = request.form.to_dict()
    contracts = gl.get_contract_list_by_amt_regist(params)
    cntrct_sns = set([c["value"] for c in contracts])
    params["chrg_sn"] = params["s_bsn_chrg_sn"]
    r_cs = gl.get_goals_by_member(params)
    reg_cntrct_sns = set([r["cntrct_sn"] for r in r_cs])
    remain = list(cntrct_sns - reg_cntrct_sns)
    result = [c for c in contracts if c["value"] in remain]
    return jsonify(result)

@bp.route('/ajax_add_goal_member', methods=['GET'])
def ajax_add_goal_member():
    params = request.args.to_dict()
    params["chrg_sn"] = params["s_bsn_chrg_sn"]
    gl.insert_goals(params, [params["cntrct_sn"]])
    return jsonify({"status" : True, "message" : "성공적으로 추가되었습니다."})


@bp.route('/set_goal', methods=['GET'])
def set_goal():
    params = request.args.to_dict()
    gl.set_goals(params)
    return {"status" : True, "message" : "성공적으로 변경되었습니다."}