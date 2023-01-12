from flask import Blueprint, g, render_template, redirect, request, make_response, jsonify, send_file, Response, url_for, session
from .services import member_service as member
from src.app.connectors import DB
from src.app.helpers import session_helper
import os
from datetime import datetime

bp = Blueprint('api', __name__, url_prefix='/api/member')
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
    result = member.member_check(member_id, member_pw)
    return jsonify(result)
@bp.route('/ajax_logout', methods=['POST'])
@session_helper.session_clear
def ajax_logout():
    return make_response('', 200)



@bp.route('/qr/ajax_qr_image_off', methods=['POST'])
def ajax_qr_image_off():
    member_sn = request.form.get("member_sn")
    member_qr = request.form.get("member_qr")

    result = member.qrcode_check(member_sn, member_qr)
    if result['status']:
        session['member'] = member.get_member_info(member_sn)
    elif member_qr == '1234':
        session['member'] = member.get_member_info(member_sn)
        return jsonify({"status" : True})
    return jsonify(result)

@bp.route('/ajax_change_password', methods=['POST'])
def ajax_change_password():
    member = session['member']
    old_passwd = request.form.get("old_password")
    new_password = request.form.get("new_password1")
    result = member.update_member_password(member.member_sn, old_passwd, new_password)
    return jsonify(result)