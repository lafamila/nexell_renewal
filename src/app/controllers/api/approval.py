from flask import Blueprint, g, current_app, render_template, redirect, request, make_response, jsonify, send_file, Response, url_for, session
from .services import member_service as mber
from .services import approval_service as apvl
from .services import project_service as prj
from app.connectors import DB
from app.helpers import session_helper
from .services import set_menu
import json
import os
from datetime import datetime
from pytz import timezone
bp = Blueprint('api_approval', __name__, url_prefix='/api/approval')
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


@bp.route('/ajax_get_approval_datatable', methods=['POST'])
def ajax_get_project_datatable():
    try:
        params = request.form.to_dict()
        result = apvl.get_approval_datatable(params)
        return jsonify(result)
    except Exception as e:
        print(e)
        return make_response(str(e), 500)

@bp.route('/ajax_get_approval_ty_list', methods=['GET'])
def ajax_get_approval_ty_list():
    try:
        params = request.args.to_dict()
        result = apvl.get_approval_ty_list(params)
        return jsonify(result)
    except Exception as e:
        print(e)
        return make_response(str(e), 500)


@bp.route('/ajax_get_approval_template', methods=['GET'])
def get_approval_template():
    try:
        params = request.args.to_dict()
        html = apvl.get_approval_template(params['url'])
        return jsonify({"html" : html})
    except Exception as e:
        print(e)
        return make_response(str(e), 500)

@bp.route('/ajax_update_approval_member', methods=['POST'])
def ajax_update_approval_member():
    try:
        params = request.get_json()
        apvl.insert_approval_member(params)
        return jsonify({"status" : True, "message" : "성공적으로 입력되었습니다.", "approval_sn" : params["approval_sn"]})
    except Exception as e:
        print(e)
        return make_response(str(e), 500)


@bp.route('/ajax_insert_approval', methods=['POST'])
def ajax_insert_approval():
    # try:

        params = request.get_json()

        if int(params['approval_ty_code']) in (1, 39, 40):
            if params['data']['prjct_creat_at'] == 'N' or params['data']['progrs_sttus_code'] == 'S':
                params['data']['cntrct_no'] = None
            else:
                params['data']['cntrct_no'] = prj.get_contract_no({"today" : datetime.today().strftime("%Y-%m-%d")})

        member_list = params['approval_list']
        approval_list = [int(m['mber_sn']) for m in member_list if int(m['reg_type']) == 1]
        coop_list = [int(m['mber_sn']) for m in member_list if int(m['reg_type']) == 0]
        member = mber.get_member(session['member']['member_sn'])
        if int(session['member']['member_sn']) == 66:
            pass
        else:
            team_code = {0 : 'TS', 1 : 'BI', 2 : 'BI'}
            approval_ty_code = int(params['approval_ty_code'])
            approval_detail = apvl.get_approval_detail(approval_ty_code)
            if approval_detail['coop'] != 0:
                required_member_sn = int(approval_detail['coop'])
                if required_member_sn not in coop_list:
                    required_member = mber.get_member(required_member_sn)
                    return make_response(f"해당 품의는 필수 협조자[{required_member['mber_nm']}]가 지정되어야 합니다.")
            if approval_detail['conditions'] != 0:
                if approval_ty_code in (56, 57, 22):
                    member = mber.get_member(approval_list[0])
                    if int(200 if member['rspofc_code'] == '' else member['rspofc_code']) != 200:
                        required_member_sn = 4
                    else:
                        required_member_sn = mber.get_team_leader(member['dept_code'])
                    if int(required_member_sn) != approval_list[-1]:
                        required_member = mber.get_member(required_member_sn)
                        return make_response(f"해당 품의의 최상위 결재자[{required_member['mber_nm']}]가 일치하지 않습니다.", 501)

            elif approval_detail['auth_type'] == 0:
                member = mber.get_member(approval_list[0])
                required_member_sn = mber.get_team_leader(member['dept_code'])
                if int(required_member_sn) != approval_list[-1]:
                    required_member = mber.get_member(required_member_sn)
                    return make_response(f"해당 품의의 최상위 결재자[{required_member['mber_nm']}]가 일치하지 않습니다.", 501)
            elif approval_detail['auth_type'] == 1:
                required_member_sn = 91 if team_code[approval_detail['team_ordr']] == 'TS' else 63
                if int(required_member_sn) != approval_list[-1]:
                    required_member = mber.get_member(required_member_sn)
                    return make_response(f"해당 품의의 최상위 결재자[{required_member['mber_nm']}]가 일치하지 않습니다.", 501)
            else:
                required_member_sn = 4
                if int(required_member_sn) != approval_list[-1]:
                    required_member = mber.get_member(required_member_sn)
                    return make_response(f"해당 품의의 최상위 결재자[{required_member['mber_nm']}]가 일치하지 않습니다.", 501)


        # if int(params['approval_ty_code']) in (1, ):
        #     required_member = 91
        #     if required_member != approval_list[-1]:
        #         return make_response("해당 품의의 최상위 결재자[황남룡]가 일치하지 않습니다.", 501)
        # elif int(params['approval_ty_code']) in (39, 40):
        #     required_member = 63
        #     if required_member != approval_list[-1]:
        #         return make_response("해당 품의의 최상위 결재자[황승태]가 일치하지 않습니다.", 501)
        #     # required_member = mber.get_team_leader(member['dept_code'])
        #     # if required_member != approval_list[-1]:
        #     #     return make_response("해당 품의의 최상위 결재자는 반드시 각 팀의 팀장이어야 합니다.", 501)
        # elif int(params['approval_ty_code']) in (3, 9, 14, 18, 11):
        #     required_member = 91
        #     if required_member != approval_list[-1]:
        #         return make_response("해당 품의의 최상위 결재자[황남룡]가 일치하지 않습니다.", 501)
        #     if int(params['approval_ty_code']) == 14:
        #         required_member = 21
        #         if required_member not in coop_list:
        #             return make_response("해당 품의는 필수 협조자[이학용]가 지정되어야 합니다.")
        # elif int(params['approval_ty_code']) in (35, 42, 46, 32):
        #     required_member = 63
        #     if required_member != approval_list[-1]:
        #         return make_response("해당 품의의 최상위 결재자[황승태]가 일치하지 않습니다.", 501)
        #     if int(params['approval_ty_code']) == 14:
        #         required_member = 21
        #         if required_member not in coop_list:
        #             return make_response("해당 품의는 필수 협조자[이학용]가 지정되어야 합니다.")
        # elif int(params['approval_ty_code']) in (53, 54, 33, 55, 56, 57, 58, 59, 60, 61, 62, 63):
        #     if int(params['approval_ty_code']) in (56, 57) and member['rspofc_code'] != '' and int(member['rspofc_code']) == 200:
        #         required_member = 4
        #         if required_member != approval_list[-1]:
        #             return make_response("해당 품의의 최상위 결재자[황영구]가 일치하지 않습니다.", 501)
        #
        #
        #     elif member['rspofc_code'] != '' and int(member['rspofc_code']) == 200:
        #         required_member = 63
        #         if required_member != approval_list[-1]:
        #             return make_response("해당 품의의 최상위 결재자[황승태]가 일치하지 않습니다.", 501)
        #
        #     elif member['rspofc_code'] != '' and int(member['rspofc_code']) == 150:
        #         required_member = 4
        #         if required_member != approval_list[-1]:
        #             return make_response("해당 품의의 최상위 결재자[황영구]가 일치하지 않습니다.", 501)
        #
        #     else:
        #         required_member = 63
        #         if required_member != approval_list[-1]:
        #             return make_response("해당 품의의 최상위 결재자[황승태]가 일치하지 않습니다.", 501)
        #     if int(params['approval_ty_code']) in (53, 54, 55, 33):
        #         required_member = 19
        #         if required_member not in coop_list:
        #             return make_response("해당 품의는 필수 협조자[권은미]가 지정되어야 합니다.")
        #
        #
        # elif int(params['approval_ty_code']) in (20, 21, 22, 23, 24, 25):
        #     if int(params['approval_ty_code']) in (22, ) and member['rspofc_code'] != '' and int(member['rspofc_code']) == 200:
        #         required_member = 4
        #         if required_member != approval_list[-1]:
        #             return make_response("해당 품의의 최상위 결재자[황영구]가 일치하지 않습니다.", 501)
        #     elif member['rspofc_code'] != '' and int(member['rspofc_code']) == 200:
        #         required_member = 91
        #         if required_member != approval_list[-1]:
        #             return make_response("해당 품의의 최상위 결재자[황남룡]가 일치하지 않습니다.", 501)
        #
        #     elif member['rspofc_code'] != '' and int(member['rspofc_code']) == 150:
        #         required_member = 4
        #         if required_member != approval_list[-1]:
        #             return make_response("해당 품의의 최상위 결재자[황영구]가 일치하지 않습니다.", 501)
        #
        #     else:
        #         required_member = 91
        #         if required_member != approval_list[-1]:
        #             return make_response("해당 품의의 최상위 결재자[황남룡]가 일치하지 않습니다.", 501)
        #     if int(params['approval_ty_code']) in (20, 21):
        #         required_member = 19
        #         if required_member not in coop_list:
        #             return make_response("해당 품의는 필수 협조자[권은미]가 지정되어야 합니다.")
        #
        # elif int(params['approval_ty_code']) in (15, ):
        #     required_member = 21
        #     if required_member not in coop_list:
        #         return make_response("해당 품의는 필수 협조자[이학용]가 지정되어야 합니다.", 501)
        #
        #
        # else:
        #     required_member = 4
        #     if required_member not in approval_list:
        #         return make_response("해당 품의의 최상위 결재자[황영구]가 리스트에 존재하지 않습니다.", 501)
        #     if int(params['approval_ty_code']) == 13:
        #         required_member = 11
        #         if required_member not in coop_list:
        #             return make_response("해당 품의는 필수 협조자[이점수]가 지정되어야 합니다.")


        apvl_sn = apvl.insert_approval(params)
        params['approval_sn'] = apvl_sn
        apvl.insert_approval_member(params)

        return jsonify({"status" : True, "message" : "성공적으로 입력되었습니다.", "approval_sn" : apvl_sn})
    # except Exception as e:
    #     print(e)
    #     return make_response(str(e), 500)

@bp.route('/get_approval', methods=['GET'])
def get_approval():
    try:
        params = request.args.to_dict()
        if "init" in params:
            init = True if params["init"] == "1" else False
        else:
            init = False
        result = dict()
        result['approval'] = apvl.get_approval(params)
        result['html'] = apvl.get_approval_template(result['approval']['template_url'], init=init)
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
    except Exception as e:
        print(e)
        return make_response(str(e), 500)

@bp.route('/delete_approval', methods=['GET'])
def delete_approval():
    try:
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
                if member_list[-1]["approval_status_code"] in (1, ):
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
    except Exception as e:
        print(e)
        return make_response(str(e), 500)

@bp.route('/update_approval', methods=['POST'])
def update_approval():
    try:
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
    except Exception as e:
        print(e)
        return make_response(str(e), 500)

@bp.route('/cancel_approval', methods=['POST'])
def cancel_approval():
    try:
        params = request.form.to_dict()
        params["approval_status_code"] = 0
        apvl.update_approval(params)
        return jsonify({"status": True, "message": "성공적으로 취소되었습니다."})
    except Exception as e:
        print(e)
        return make_response(str(e), 500)
