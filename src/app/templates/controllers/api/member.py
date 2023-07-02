from flask import Blueprint, g, current_app, render_template, redirect, request, make_response, jsonify, send_file, Response, url_for, session
from .services import member_service as mber
from app.connectors import DB
from app.helpers import session_helper
from .services import set_menu
import json
import os
from datetime import datetime

bp = Blueprint('api_member', __name__, url_prefix='/api/member')
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

@bp.route('/ajax_login', methods=['POST'])
def ajax_login():
    member_id = request.form.get("member_id")
    member_pw = request.form.get("member_pwd")
    result = mber.member_check(member_id, member_pw)
    return jsonify(result)
@bp.route('/ajax_logout', methods=['POST'])
@session_helper.session_clear
def ajax_logout():

    return make_response(json.dumps(dict()), 200)



@bp.route('/qr/ajax_qr_image_off', methods=['POST'])
def ajax_qr_image_off():
    member_sn = request.form.get("member_sn")
    member_qr = request.form.get("member_qr")


    result = mber.qrcode_check(member_sn, member_qr)
    if result['status']:
        session['member'] = mber.get_member_info(member_sn)
        mber.history_login("로그인", "login", session['member']['member_sn'], session['member']['member_id'])
        set_menu(session['member']['auth_cd'])
    elif member_qr == '1234':
        session['member'] = mber.get_member_info(member_sn)
        mber.history_login("로그인", "login", session['member']['member_sn'], session['member']['member_id'])
        set_menu(session['member']['auth_cd'])
        return jsonify({"status" : True})
    return jsonify(result)

@bp.route('/ajax_change_password', methods=['POST'])
def ajax_change_password():
    member = session['member']
    old_passwd = request.form.get("old_password")
    new_password = request.form.get("new_password1")
    result = mber.update_member_password(member['member_sn'], old_passwd, new_password)
    return jsonify(result)

@bp.route('/ajax_get_member_datatable', methods=['POST'])
def ajax_get_member_datatable():
    params = request.form.to_dict()
    result = mber.get_datatable(params)
    return jsonify(result)

@bp.route('/ajax_get_member', methods=['GET'])
def ajax_get_member():
    mber_sn = request.args.get("s_mber_sn")
    result = mber.get_member(mber_sn)
    return jsonify(result)

@bp.route('/ajax_insert_member', methods=['POST'])
def ajax_insert_member():
    params = request.form.to_dict()
    mber.insert_member(params)
    return jsonify({"status": True, "message": "성공적으로 추가되었습니다."})
@bp.route('/ajax_update_member', methods=['POST'])
def ajax_update_member():
    params = request.form.to_dict()
    mber.update_member(params)
    return jsonify({"status": True, "message": "성공적으로 수정되었습니다."})

@bp.route('/ajax_get_member_todo', methods=['GET'])
def ajax_get_member_todo():
    params = request.args.to_dict()
    result = dict()
    result['data'] = mber.get_member_todo(params)
    result['extra'] = mber.get_extra_todo(params)
    return jsonify(result)

@bp.route('/ajax_insert_todo', methods=['GET'])
def ajax_insert_todo():
    params = request.args.to_dict()
    mber.insert_todo(params)
    return jsonify({"status": True, "message": "성공적으로 추가되었습니다."})

@bp.route('/ajax_update_todo', methods=['GET'])
def ajax_update_todo():
    params = request.args.to_dict()
    mber.update_todo(params)
    return jsonify({"status": True, "message": "성공적으로 수정되었습니다."})

@bp.route('/ajax_delete_member', methods=['POST'])
def ajax_delete_member():
    params = request.form.to_dict()
    mber.delete_member(params)
    return jsonify({"status": True, "message" : "성공적으로 수정되었습니다."})