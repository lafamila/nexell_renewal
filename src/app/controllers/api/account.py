from flask import Blueprint, g, render_template, redirect, request, make_response, jsonify, send_file, Response, url_for, session
from .services import account_service as account
from src.app.connectors import DB
import os
from datetime import datetime

bp = Blueprint('api', __name__, url_prefix='/api/account')
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

    return jsonify(account.member_check(member_id, member_pw))



@bp.route('/qr/ajax_qr_image_off', methods=['POST'])
def ajax_qr_image_off():
    member_sn = request.form.get("member_sn")
    member_qr = request.form.get("member_qr")

    return jsonify(account.qrcode_check(member_sn, member_qr))