from flask import Blueprint, g, current_app, render_template, redirect, request, make_response, jsonify, send_file, Response, url_for, session
from .services import work_service as wk
from .services import project_service as prj

from app.connectors import DB
from app.helpers import session_helper
from .services import set_menu
import json
import os
from datetime import datetime

bp = Blueprint('api_work', __name__, url_prefix='/api/work')
LIMIT_TIMER = ["1200", "0900", "0840", "0840", "0840", "0840", "1200"]
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

@bp.route('/ajax_get_work', methods=['GET'])
def ajax_get_work():
    params = request.args.to_dict()
    result = dict()
    result['data'] = wk.get_work(params)
    result['status'] = True
    return jsonify(result)

@bp.route('/ajax_get_year_datatable', methods=['POST'])
def ajax_get_year_datatable():
    params = request.form.to_dict()
    result = wk.get_work_datatable(params)
    # result = dict()
    # result['data'] = []
    return jsonify(result)

@bp.route('/ajax_get_personal', methods=['GET'])
def ajax_get_personal():
    params = request.args.to_dict()
    params["s_mber_sn"] = session["member"]["member_sn"]
    params["s_mber_nm"] = session["member"]["member_nm"]
    result = wk.get_work_datatable(params)
    result['calendar'] = wk.get_work_calendar(params)
    timers = wk.get_work_time(params)
    result['timer'] = {}
    for t in timers:
        work_date = t['work_date']
        y, m, d = work_date[:4], work_date[4:6], work_date[6:]
        result['timer'][int(d)] = (t['start_time'], t['end_time'])
    print(result['timer'])
    for _ in result['calendar']['rows']:
        for i, d in enumerate(_):
            if d != '':
                if d in result['timer']:
                    start_time, end_time = result['timer'][d]
                    s = "{}:{}".format(start_time[-6:-4], start_time[-4:-2])
                    _class = "color-blue"
                    status = "근무"
                    print(LIMIT_TIMER[i], start_time[-6:-2])
                    if int(LIMIT_TIMER[i]) < int(start_time[-6:-2]):
                        _class = "color-red"
                        status = "지각"
                    if end_time is None:
                        result['timer'][d] = "<span class='{0}'>{1}</span><br>출근 : {2}<br>퇴근 미등록".format(_class, status, s)
                    else:
                        e = "{}:{}".format(end_time[-6:-4], end_time[-4:-2])
                        result['timer'][d] = "<span class='{0}'>{1}</span><br>출근 : {2}<br>퇴근 {3}".format(_class, status, s, e)
                else:
                    result['timer'][d] = "출근 미등록<br>퇴근 미등록"
    # TODO : 휴가 결재 내역에서 가져와서 덮어씌울 것
    return jsonify(result)


@bp.route('/ajax_set_work_data', methods=['GET'])
def ajax_set_work_data():
    params = request.args.to_dict()
    wk.set_work_data(params)
    return jsonify({"status" : True, "message" : "성공적으로 변경되었습니다."})

