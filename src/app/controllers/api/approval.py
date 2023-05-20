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
    apvl_sn = apvl.insert_approval(params)
    params['approval_sn'] = apvl_sn
    apvl.insert_approval_member(params)
    return jsonify({"status" : True, "message" : "성공적으로 입력되었습니다.", "approval_sn" : apvl_sn})

@bp.route('/get_approval', methods=['GET'])
def get_approval():
    params = request.args.to_dict()

    result = dict()
    result['approval'] = apvl.get_approval(params)
    result['html'] = apvl.get_approval_template(result['approval']['template_url'], init=False)
    result['member_list'] = apvl.get_approval_member(params)
    required_m_list = [r for r in result['member_list'] if r['reg_type'] in (0, 1)]
    last_member = None
    next_member = None
    isFired = False
    isMyTurn = False
    isFirst = result['approval']['reg_mber'] == session['member']['member_sn']
    isCancelable = False
    isDone = False
    for i, member in enumerate(required_m_list):
        if member['approval_status_code'] == -1:
            isFired = True
            break
    if isFired:
        isMyTurn = False
        isCancelable = False
    else:
        for i, member in enumerate(required_m_list):
            if member['approval_status_code'] == 1:
                last_member = (member['mber_sn'], i)
            elif member['approval_status_code'] == 0:
                next_member = (member['mber_sn'], i)
                break
        if next_member is None:
            isDone = True
        elif next_member[0] == session['member']['member_sn']:
            isMyTurn = True

        if last_member is not None and last_member[0] == session['member']['member_sn'] and next_member is not None:
            isCancelable = True

    result['approval']['approval_data'] = json.loads(result['approval']['approval_data'])
    result['myTurn'] = isMyTurn
    result['isFirst'] = isFirst
    result['cancelable'] = isCancelable
    return jsonify(result)

@bp.route('/delete_approval', methods=['GET'])
def delete_approval():
    params = request.args.to_dict()
    approval = apvl.get_approval(params)
    if int(session['member']['auth_cd']) == 1:
        member_list = apvl.get_approval_member(params)
        deletable = False
        msg = "진행중인 결재자가 있어 삭제가 불가능합니다."
        if not member_list:
            deletable = False
            msg = "최종 결재가 완료되지 않아 삭제가 불가능합니다."
        else:
            if member_list[-1]["approval_status_code"] in 1:
                deletable = True
                msg = "성공적으로 삭제되었습니다."
            elif -1 in [m["approval_status_code"] for m in member_list]:
                deletable = True
                msg = "성공적으로 삭제되었습니다."

            elif member_list[0]["approval_status_code"] == 0:
                deletable = False
                msg = "상신중인 품의는 삭제가 불가능합니다."

        if deletable:
            apvl.delete_approval(params)


    elif int(approval['reg_mber']) == int(session['member']['member_sn']):

        member_list = apvl.get_approval_member(params)
        deletable = False
        msg = "진행중인 결재자가 있어 삭제가 불가능합니다."
        if not member_list:
            deletable = True
            msg = "성공적으로 삭제되었습니다."
        else:
            if member_list[-1]["approval_status_code"] == 1:
                deletable = False
                msg = "최종 결재가 완료되어 삭제가 불가능합니다."
            elif member_list[0]["approval_status_code"] == 0:
                deletable = True
                msg = "성공적으로 삭제되었습니다."
            elif -1 in [m["approval_status_code"] for m in member_list]:
                deletable = True
                msg = "성공적으로 삭제되었습니다."

        if deletable:
            apvl.delete_approval(params)

    else:
        deletable = False
        msg = "기안자가 아니면 삭제할 수 없습니다."
    return jsonify({"status" : deletable, "message" : msg})
@bp.route('/update_approval', methods=['POST'])
def update_approval():
    params = request.form.to_dict()

    member_id = session['member']['member_id']
    member_pw = params['password']

    result = mber.member_check(member_id, member_pw)
    if result['status']:
        apvl.update_approval(params)
        member_list = apvl.get_approval_member(params)
        member_list = [m for m in member_list if m['reg_type'] in (0, 1)]
        isEnd = True
        for m in member_list:
            if m['approval_status_code'] in (-1, 0):
                isEnd = False
        if isEnd:
            approval = apvl.get_approval(params)
            approval['approval_data'] = json.loads(approval['approval_data'])
            return jsonify({"status" : True, "isEnd" : True, "approval" : approval})
    else:
        return jsonify({"status" : False, "message" : "비밀번호가 일치하지 않습니다."})
    return jsonify({"status" : True, "isEnd" : False, "message" : "성공적으로 처리되었습니다."})

@bp.route('/cancel_approval', methods=['POST'])
def cancel_approval():
    params = request.form.to_dict()
    params["approval_status_code"] = 0
    apvl.update_approval(params)
    return jsonify({"status": True, "message": "성공적으로 취소되었습니다."})
