from flask import Blueprint, g, current_app, render_template, redirect, request, make_response, jsonify, send_file, Response, url_for, session
from .services import completed_service as cp
from .services import project_service as prj
from .services import stock_service as st

from app.connectors import DB
from app.helpers import session_helper
from .services import set_menu
import json
import os
from datetime import datetime
from dateutil import relativedelta

bp = Blueprint('api_completed', __name__, url_prefix='/api/completed')

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

@bp.route('/ajax_get_completed_reportNR', methods=['GET'])
def completed_ajax_get_completed_reportNR():
    params = request.args.to_dict()
    result = dict()
    s_pxcond_dtm = params["s_pxcond_mt"]
    params["s_pxcond_mt"] = "-".join(s_pxcond_dtm.split("-")[:2])
    result['contractStatusList'] = cp.get_contract_status_list(params)
    result['executStatusList'] = cp.get_execut_status_list(params)
    result['completedList'] = cp.get_completed_reportNR(params)
    result['modelTemp'] = cp.get_completed_reportNR_M2(params)
    result['completedList2'] = cp.get_partner_contract_status(params)
    result['completedList3'] = cp.get_partner_status_list(params)
    new_params = dict()
    new_params["s_pxcond_mt"] = (datetime.strptime(s_pxcond_dtm, "%Y-%m-%d")-relativedelta.relativedelta(months=1)).strftime("%Y-%m")
    result['lastDate'] = cp.get_completed_reportNR(new_params)

    # TODO : modelList api
    result['modelList'] = dict()
    # $result['modelList'] = array();
    # foreach($this->m_completed->get_completed_reportNR_M2($params) as $model) {
    #   if (!array_key_exists($model['bsn_dept_code'], $result['modelList'])){
    #       $result['modelList'][$model['bsn_dept_code']] = array();
    #   }
    #   $result['modelList'][$model['bsn_dept_code']][$model['cntrct_execut_code']] = $model;
    # }

    result['status'] = True
    return jsonify(result)