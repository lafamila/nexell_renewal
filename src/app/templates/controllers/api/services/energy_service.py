from flask import session, jsonify, g, render_template
from app.helpers.datatable_helper import dt_query
import json

def get_energy_datatable(params):
    start = params["s_year_start"].split("-")[0]
    end = params["s_year_end"].split("-")[0]
    query = """SELECT e.eng_sn
				, e.eng_year AS eng_year
				, e.eng_state
				, e.cp_nm
				, e.cp_code
				, e.eng_nm
				, e.np_nm
				, e.xp_nm
				, IFNULL((SELECT p.cntrwk_bgnde FROM plan p WHERE p.eng_sn=e.eng_sn AND p.plan_sn IN (SELECT MIN(plan_sn) FROM plan GROUP BY eng_sn)), '') AS cntrwk_bgnde
				, IFNULL((SELECT p.cntrwk_endde FROM plan p WHERE p.eng_sn=e.eng_sn AND p.plan_sn IN (SELECT MAX(plan_sn) FROM plan GROUP BY eng_sn)), '') AS cntrwk_endde
				, '연구소' AS prjct_ty_nm
				, IFNULL(e.eng_cost, 0) AS eng_cost
				, (SELECT SUM(IFNULL(cp_a_cost, 0)+IFNULL(cp_b_cost, 0)+IFNULL(cp_c_cost, 0)) FROM plan p WHERE p.eng_sn=e.eng_sn GROUP BY p.eng_sn) AS ex_cost
				, (SELECT SUM(IFNULL(cp_a_cost, 0)+IFNULL(cp_b_cost, 0)+IFNULL(cp_c_cost, 0)) FROM plan p WHERE p.eng_sn=e.eng_sn GROUP BY p.eng_sn)  AS cost
				, (SELECT SUM(IFNULL(ep.exp_cost, 0)) FROM expense ep WHERE ep.eng_sn=e.eng_sn AND ep.exp_ty_code='P' GROUP BY ep.eng_sn) AS tot_cost
				, (SELECT SUM(IFNULL(ep.exp_cost, 0)) FROM expense ep WHERE ep.eng_sn=e.eng_sn AND ep.exp_ty_code='O' GROUP BY ep.eng_sn) AS use_cost
				, CASE WHEN e.cp_nm = '넥셀시스템' THEN 0
				WHEN e.cp_nm = '국토교통부' THEN 1
				WHEN e.cp_nm = '과학기술정보통신부' THEN 2
				WHEN e.cp_nm = '산업통상자원부' THEN 3
				ELSE 4
				END AS cp_ordr_order
				, e.rnr
				, e.mber
				, IF(e.cp_nm='넥셀시스템', 0, 1) AS cp_ordr
				, '1' AS ctmmny_sn
				FROM energy e
				WHERE 1=1
				AND e.eng_year BETWEEN '{0}'
				AND '{1}'
""".format(start, end)

    data = []


    if "s_eng_state" in params and params['s_eng_state']:
        query += " AND e.eng_state=%s"
        data.append(params["s_eng_state"])

    return dt_query(query, data, params)



def get_energy_summary(params):
    start = params["s_year_start"].split("-")[0]
    end = params["s_year_end"].split("-")[0]
    query = """SELECT IFNULL(COUNT(e.eng_sn),0) AS total_count
				, IFNULL(SUM((SELECT SUM(IFNULL(ep.exp_cost, 0)) FROM expense ep WHERE ep.eng_sn=e.eng_sn AND ep.exp_ty_code='P' GROUP BY ep.eng_sn)),0) AS total_amount
				FROM energy e
				WHERE 1=1
				AND e.eng_year BETWEEN '{0}'
				AND '{1}'
""".format(start, end)
    data = []
    if "s_eng_state" in params and params['s_eng_state']:
        query += " AND e.eng_state=%s"
        data.append(params["s_eng_state"])

    g.curs.execute(query, data)
    result = g.curs.fetchall()
    return result

def get_energy(params):
    query = """SELECT e.eng_sn
				, e.eng_year
				, e.eng_nm
				, e.eng_state
				, e.cp_nm
				, e.cp_code
				, e.np_nm
				, e.np_mber
				, e.own_mber
				, e.mber
				, e.rnr
				, e.xp_nm
				, e.eng_cost
				FROM energy e
				WHERE 1=1
				AND e.eng_sn = %(s_eng_sn)s
"""
    g.curs.execute(query, params)
    result = g.curs.fetchone()
    return result

def get_plan_list(params):
    query = """SELECT eng_sn
				, plan_sn
				, cntrwk_bgnde
				, cntrwk_endde
				, cp_a_cost
				, cp_b_cost
				, cp_c_cost
				, todo
				, result
				, regist_dtm
				, register_id
				FROM plan
				WHERE 1=1
				AND eng_sn = %(s_eng_sn)s
				ORDER BY plan_sn"""
    g.curs.execute(query, params)
    result = g.curs.fetchall()
    return result

def get_exp_list(params):
    query = """SELECT e.eng_sn
				, e.exp_sn
				, e.exp_de
				, e.plan_order
				, e.exp_ty_code
				, (SELECT code_nm FROM code WHERE ctmmny_sn=1 AND parnts_code='EXP_TY_CODE' AND code=e.exp_ty_code) AS exp_ty_nm
				, e.exp_se_code
				, (SELECT code_nm FROM code WHERE ctmmny_sn=1 AND parnts_code='EXP_SE_CODE' AND code=e.exp_se_code) AS exp_se_nm
				, e.exp_bcnc_code
				, e.exp_bcnc_code AS exp_bcnc_nm
				, e.exp_io_type
				, IF(e.exp_io_type=0,'현금', '카드') AS exp_io_nm
				, e.exp_content
				, e.exp_cost
				, e.regist_dtm
				, e.register_id
				FROM expense e
				WHERE 1=1
				AND eng_sn = %(s_eng_sn)s
				AND exp_ty_code NOT IN ('P')"""

    data = []
    if "s_exp_bcnc_code" in params and params['s_exp_bcnc_code']:
        query += " AND exp_bcnc_code LIKE %s"
        data.append("%{}%".format(params["s_exp_bcnc_code"]))

    if "s_exp_se_code" in params and params['s_exp_se_code']:
        query += " AND exp_se_code = %s"
        data.append(params["s_exp_se_code"])

    if "s_exp_ty_code" in params and params['s_exp_ty_code']:
        query += " AND exp_ty_code = %s"
        data.append(params["s_exp_ty_code"])

    if "s_exp_content" in params and params['s_exp_content']:
        query += " AND exp_content LIKE %s"
        data.append("%{}%".format(params["s_exp_content"]))

    if "s_start" in params and params['s_start'] and "s_end" in params and params['s_end']:
        query += " AND exp_de BETWEEN %s AND %s"
        data.append(params["s_start"])
        data.append(params["s_end"])

    query += " ORDER BY exp_de, exp_content ";

    g.curs.execute(query, data)
    result = g.curs.fetchall()
    return result