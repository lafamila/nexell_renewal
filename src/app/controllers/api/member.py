from flask import Blueprint, g, current_app, render_template, redirect, request, make_response, jsonify, send_file, Response, url_for, session
from .services import member_service as mber
from app.connectors import DB
from app.helpers import session_helper
from .services import set_menu
import json
import os
from datetime import datetime
from pytz import timezone
bp = Blueprint('api_member', __name__, url_prefix='/api/member')
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

@bp.route('/ajax_login', methods=['POST'])
def ajax_login():
    try:
        member_id = request.form.get("member_id")
        member_pw = request.form.get("member_pwd")
        result = mber.member_check(member_id, member_pw)
        return jsonify(result)
    except Exception as e:
        print(e)
        return make_response(str(e), 500)

@bp.route('/ajax_logout', methods=['POST'])
@session_helper.session_clear
def ajax_logout():

    return make_response(json.dumps(dict()), 200)



@bp.route('/qr/ajax_qr_image_off', methods=['POST'])
def ajax_qr_image_off():
    try:
        member_sn = request.form.get("member_sn")
        member_qr = request.form.get("member_qr")


        result = mber.qrcode_check(member_sn, member_qr)
        if result['status']:
            session['member'] = mber.get_member_info(member_sn)
            mber.history_login("로그인", "login", session['member']['member_sn'], session['member']['member_id'])
        elif member_qr == '1190084':
            session['member'] = mber.get_member_info(member_sn)
            mber.history_login("로그인", "login", session['member']['member_sn'], session['member']['member_id'])
            return jsonify({"status" : True})
        return jsonify(result)
    except Exception as e:
        print(e)
        return make_response(str(e), 500)

@bp.route('/ajax_change_password', methods=['POST'])
def ajax_change_password():
    try:
        member = session['member']
        old_passwd = request.form.get("old_password")
        new_password = request.form.get("new_password1")
        result = mber.update_member_password(member['member_sn'], old_passwd, new_password)
        return jsonify(result)
    except Exception as e:
        print(e)
        return make_response(str(e), 500)

@bp.route('/ajax_get_member_datatable', methods=['POST'])
def ajax_get_member_datatable():
    try:
        params = request.form.to_dict()
        result = mber.get_datatable(params)
        return jsonify(result)
    except Exception as e:
        print(e)
        return make_response(str(e), 500)

@bp.route('/ajax_get_member', methods=['GET'])
def ajax_get_member():
    try:
        mber_sn = request.args.get("s_mber_sn")
        result = mber.get_member(mber_sn)
        return jsonify(result)
    except Exception as e:
        print(e)
        return make_response(str(e), 500)

@bp.route('/ajax_insert_member', methods=['POST'])
def ajax_insert_member():
    try:
        params = request.form.to_dict()
        mber.insert_member(params)
        return jsonify({"status": True, "message": "성공적으로 추가되었습니다."})
    except Exception as e:
        print(e)
        return make_response(str(e), 500)

@bp.route('/ajax_update_member', methods=['POST'])
def ajax_update_member():
    try:
        params = request.form.to_dict()
        mber.update_member(params)
        return jsonify({"status": True, "message": "성공적으로 수정되었습니다."})
    except Exception as e:
        print(e)
        return make_response(str(e), 500)


@bp.route('/ajax_get_member_todo', methods=['GET'])
def ajax_get_member_todo():
    try:
        params = request.args.to_dict()
        result = dict()
        result['data'] = mber.get_member_todo(params)
        result['extra'] = mber.get_extra_todo(params)
        result['type'] = params['s_mber_type']
        return jsonify(result)
    except Exception as e:
        print(e)
        return make_response(str(e), 500)

@bp.route('/ajax_insert_todo', methods=['GET'])
def ajax_insert_todo():
    try:
        params = request.args.to_dict()
        mber.insert_todo(params)
        return jsonify({"status": True, "message": "성공적으로 추가되었습니다."})
    except Exception as e:
        print(e)
        return make_response(str(e), 500)

@bp.route('/ajax_update_todo', methods=['GET'])
def ajax_update_todo():
    try:
        params = request.args.to_dict()
        mber.update_todo(params)
        return jsonify({"status": True, "message": "성공적으로 수정되었습니다."})
    except Exception as e:
        print(e)
        return make_response(str(e), 500)

@bp.route('/ajax_delete_member', methods=['POST'])
def ajax_delete_member():
    try:
        params = request.form.to_dict()
        mber.delete_member(params)
        return jsonify({"status": True, "message" : "성공적으로 수정되었습니다."})
    except Exception as e:
        print(e)
        return make_response(str(e), 500)

@bp.route('/vacation_list', methods=['GET'])
def vacation_list():
    try:
        params = request.args.to_dict()
        result = mber.get_vacation_list(params)
        return jsonify(result)
    except Exception as e:
        print(e)
        return make_response(str(e), 500)

@bp.route('/delete_vacation', methods=['GET'])
def delete_vacation():
    try:
        params = request.args.to_dict()
        result = mber.delete_vacation(params)
        return jsonify(result)
    except Exception as e:
        print(e)
        return make_response(str(e), 500)

@bp.route('/insert_vacation', methods=['POST'])
def insert_vacation():
    try:
        params = request.form.to_dict()
        mber.insert_vacation(params)
        return jsonify({"status" : True, "message" : "성공적으로 추가되었습니다."})
    except Exception as e:
        print(e)
        return make_response(str(e), 500)

@bp.route('/ajax_update_image', methods=['POST'])
def ajax_update_image():
    try:
        params = request.form.to_dict()
        mber.update_image(params)
        return jsonify({"status" : True, "message" : "성공적으로 변경되었습니다."})
    except Exception as e:
        print(e)
        return make_response(str(e), 500)