from flask import session, jsonify, g, render_template
from app.helpers.datatable_helper import dt_query
import json
import datetime
from pytz import timezone

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

def get_expP_list(params):
    query = """SELECT SUM(IF(e.exp_se_code=1,e.exp_cost,0)) AS exp_cost_1
				, SUM(IF(e.exp_se_code=2,e.exp_cost,0)) AS exp_cost_2
				, SUM(IF(e.exp_se_code=3,e.exp_cost,0)) AS exp_cost_3
				, SUM(IF(e.exp_se_code=4,e.exp_cost,0)) AS exp_cost_4
				, SUM(IF(e.exp_se_code=5,e.exp_cost,0)) AS exp_cost_5
				, SUM(IF(e.exp_se_code=6,e.exp_cost,0)) AS exp_cost_6
				, SUM(IF(e.exp_se_code=7,e.exp_cost,0)) AS exp_cost_7
				, SUM(IF(e.exp_se_code=8,e.exp_cost,0)) AS exp_cost_8
				, SUM(IF(e.exp_se_code=9,e.exp_cost,0)) AS exp_cost_9
				, e.plan_order
				, DATE_FORMAT(e.regist_dtm, '%%Y-%%m-%%d %%T') AS regist_dtm
				, e.eng_sn
				FROM expense e
				WHERE 1=1
				AND e.eng_sn = %(s_eng_sn)s
				AND e.exp_ty_code IN ('P')
				GROUP BY plan_order, regist_dtm
				ORDER BY plan_order, regist_dtm
"""
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
				AND eng_sn = %s
				AND exp_ty_code NOT IN ('P')"""

    data = [params["s_eng_sn"]]
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

    query += " ORDER BY exp_de, exp_content "

    g.curs.execute(query, data)
    result = g.curs.fetchall()
    return result

def get_exp_detail_list(params):
    query = """SELECT d.d_sn
				, d.eng_sn
				, d.plan_order
				, d.exp_cost_num
				, (SELECT code_ordr FROM code WHERE parnts_code='EXP_SE_CODE' and code=d.exp_cost_num) AS code_ordr
				, d.cost_content
				, d.cost_1
				, d.cost_2
				, d.regist_dtm
				FROM detail d
				WHERE 1=1
				AND d.eng_sn = %(s_eng_sn)s
				 ORDER BY plan_order, code_ordr, regist_dtm 
    """
    g.curs.execute(query, params)
    result = g.curs.fetchall()
    return result

def get_expP_list2(params):
    query = """SELECT SUM(IF(e.exp_se_code=1,e.exp_cost,0)) AS exp_cost_1
				, SUM(IF(e.exp_se_code=95,e.exp_cost,0)) AS exp_cost_2
				, SUM(IF(e.exp_se_code=96,e.exp_cost,0)) AS exp_cost_3
				, SUM(IF(e.exp_se_code=97,e.exp_cost,0)) AS exp_cost_4
				, SUM(IF(e.exp_se_code=98,e.exp_cost,0)) AS exp_cost_5
				, SUM(IF(e.exp_se_code=99,e.exp_cost,0)) AS exp_cost_6
				, SUM(IF(e.exp_se_code=100,e.exp_cost,0)) AS exp_cost_7
				, SUM(IF(e.exp_se_code=101,e.exp_cost,0)) AS exp_cost_8
				, e.plan_order
				, DATE_FORMAT(e.regist_dtm, '%%Y-%%m-%%d %%T') AS regist_dtm
				, e.eng_sn
				FROM expense e
				WHERE 1=1
				AND e.eng_sn = %(s_eng_sn)s
				AND e.exp_ty_code IN ('P')
				GROUP BY plan_order, regist_dtm
				ORDER BY plan_order, regist_dtm
"""
    g.curs.execute(query, params)
    result = g.curs.fetchall()
    return result

def insert_energybil(params):
    data = dict()
    for key in ["eng_year", "eng_nm", "eng_state", "cp_nm", "cp_code", "np_nm", "xp_nm", "eng_cost", "np_mber", "own_mber", "mber", "rnr", "regist_dtm", "register_id"]:
        if key in params:
            data[key] = params[key]

    if "regist_dtm" not in data:
        data["regist_dtm"] = datetime.datetime.now(timezone('Asia/Seoul'))

    if "register_id" not in data:
        data["register_id"] = session["member"]["member_id"]

    keys = list(data.keys())
    query = "INSERT INTO energy({}) VALUES({})".format(",".join(keys), ",".join(["%({})s".format(k) for k in keys]))
    g.curs.execute(query, data)

def update_energybil(params):
    data = dict()
    for key in ["eng_year", "eng_nm", "eng_state", "cp_nm", "cp_code", "np_nm", "xp_nm", "eng_cost", "np_mber", "own_mber", "mber", "rnr"]:
        if key in params:
            data[key] = params[key]
        else:
            data[key] = None

    data["eng_sn"] = params["s_eng_sn"]
    keys = list(data.keys())
    query = "UPDATE energy SET {} WHERE eng_sn=%(eng_sn)s".format(",".join(["{0}=%({0})s".format(k) for k in keys]))
    g.curs.execute(query, data)


def delete_energybil(params):
    query = """DELETE
				FROM energy
				WHERE 1=1
				AND eng_sn = %(s_eng_sn)s
    """
    g.curs.execute(query, params)

def get_energybil(params):
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


def get_exp_plan_list(params):
    query = """SELECT SUM(IF(e.exp_se_code=1,e.exp_cost,0)) AS cost_1
				, SUM(IF(e.exp_se_code=2,e.exp_cost,0)) AS cost_2
				, SUM(IF(e.exp_se_code=3,e.exp_cost,0)) AS cost_3
				, SUM(IF(e.exp_se_code=4,e.exp_cost,0)) AS cost_4
				, SUM(IF(e.exp_se_code=5,e.exp_cost,0)) AS cost_5
				, SUM(IF(e.exp_se_code=6,e.exp_cost,0)) AS cost_6
				, SUM(IF(e.exp_se_code=7,e.exp_cost,0)) AS cost_7
				, SUM(IF(e.exp_se_code=8,e.exp_cost,0)) AS cost_8
				, SUM(IF(e.exp_se_code=9,e.exp_cost,0)) AS cost_9
				, SUM(IF(e.exp_se_code=95,e.exp_cost,0)) AS cost_95
				, SUM(IF(e.exp_se_code=96,e.exp_cost,0)) AS cost_96
				, SUM(IF(e.exp_se_code=97,e.exp_cost,0)) AS cost_97
				, SUM(IF(e.exp_se_code=98,e.exp_cost,0)) AS cost_98
				, SUM(IF(e.exp_se_code=99,e.exp_cost,0)) AS cost_99
				, SUM(IF(e.exp_se_code=100,e.exp_cost,0)) AS cost_100
				, SUM(IF(e.exp_se_code=101,e.exp_cost,0)) AS cost_101
				, SUM(IF(e.exp_se_code >= 1 AND e.exp_se_code <= 101,e.exp_cost,0)) AS cost_sum
				, e.plan_order
				, e.exp_ty_code
				, c.code_nm AS exp_nm
				FROM expense e
				LEFT JOIN code c
				ON e.exp_ty_code = c.code
				AND c.parnts_code = 'EXP_TY_CODE'
				WHERE 1=1
				AND e.eng_sn = %(s_eng_sn)s
				AND e.exp_ty_code IN ('P', 'O')
				GROUP BY plan_order, exp_ty_code
				ORDER BY plan_order, code_ordr
"""
    g.curs.execute(query, params)
    result = g.curs.fetchall()
    return result

def get_rcppay_report_list(params):
    query = """SELECT e.plan_order
				FROM expense e
				WHERE e.exp_ty_code IN ('I', 'O')
				AND e.eng_sn = %(s_eng_sn)s
				GROUP BY e.plan_order
				ORDER BY e.plan_order
"""
    g.curs.execute(query, params)
    result = g.curs.fetchall()
    for data in result:
        pParams = {"s_eng_sn" : params["s_eng_sn"], "s_plan_order" : data["plan_order"]}
        data['sTaxbilList'] = get_s_taxbil_report_list(pParams)
        data['iRcppayList'] = get_i_rcppay_report_list(pParams)

    return result

def get_s_taxbil_report_list(params):
    query = """SELECT e.exp_de
				, e.exp_ty_code
				, (SELECT code_nm FROM code WHERE ctmmny_sn=1 AND parnts_code='EXP_SE_CODE' AND code=e.exp_se_code) AS exp_se_nm
				, e.exp_content
				, e.exp_cost
				, e.exp_io_type
				, e.exp_bcnc_code
				, e.exp_bcnc_code AS exp_bcnc_nm
				FROM expense e
				WHERE e.eng_sn = %(s_eng_sn)s
				AND e.plan_order = %(s_plan_order)s
				AND e.exp_ty_code = 'O'
				ORDER BY e.exp_de, e.exp_content
"""
    g.curs.execute(query, params)
    result = g.curs.fetchall()
    return result

def get_i_rcppay_report_list(params):
    query = """SELECT e.exp_de
				, e.exp_se_code
				, (SELECT code_nm FROM code WHERE ctmmny_sn=1 AND parnts_code='EXP_SE_CODE' AND code=e.exp_se_code) AS exp_se_nm
				, e.exp_content
				, e.exp_cost
				, e.exp_io_type
				, e.exp_bcnc_code
				, e.exp_bcnc_code AS exp_bcnc_nm
				FROM expense e
				WHERE e.eng_sn = %(s_eng_sn)s
				AND e.plan_order = %(s_plan_order)s
				AND e.exp_ty_code = 'I'
				ORDER BY e.exp_de, e.exp_content
"""
    g.curs.execute(query, params)
    result = g.curs.fetchall()
    return result

def get_plan(params):
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
				AND plan_sn = %(s_plan_sn)s
				"""
    g.curs.execute(query, params)
    result = g.curs.fetchone()
    return result

def insert_plan(params):
    data = dict()
    for key in ["eng_sn", "cntrwk_bgnde", "cntrwk_endde", "cp_a_cost", "cp_b_cost", "cp_c_cost", "todo", "result", "regist_dtm", "register_id"]:
        if key in params:
            data[key] = params[key]

    if "regist_dtm" not in data:
        data["regist_dtm"] = datetime.datetime.now(timezone('Asia/Seoul'))

    if "register_id" not in data:
        data["register_id"] = session["member"]["member_id"]

    keys = list(data.keys())
    query = "INSERT INTO plan({0}) VALUES({1})".format(",".join(keys), ",".join(["%({0})s".format(k) for k in keys]))
    print(query)
    g.curs.execute(query, data)

def insert_exp(params):
    data = dict()
    for key in ["eng_sn", "plan_order", "exp_ty_code", "exp_se_code", "exp_bcnc_code", "exp_io_type", "exp_de", "exp_content", "exp_cost", "regist_dtm", "register_id"]:
        if key in params:
            data[key] = params[key]

    if "regist_dtm" not in data:
        data["regist_dtm"] = datetime.datetime.now(timezone('Asia/Seoul'))

    if "register_id" not in data:
        data["register_id"] = session["member"]["member_id"]

    keys = list(data.keys())
    query = "INSERT INTO expense({}) VALUES({})".format(",".join(keys), ",".join(["%({})s".format(k) for k in keys]))
    g.curs.execute(query, data)

def insert_exp_detail(params):
    data = dict()
    for key in ["eng_sn", "exp_cost_num", "plan_order", "cost_content", "cost_1", "cost_2", "regist_dtm", "register_id"]:
        if key in params:
            data[key] = params[key]

    if "regist_dtm" not in data:
        data["regist_dtm"] = datetime.datetime.now(timezone('Asia/Seoul'))

    if "register_id" not in data:
        data["register_id"] = session["member"]["member_id"]

    keys = list(data.keys())
    query = "INSERT INTO detail({}) VALUES({})".format(",".join(keys), ",".join(["%({})s".format(k) for k in keys]))
    g.curs.execute(query, data)

def insert_expP(params):
    data = dict()
    for key in ["eng_sn", "plan_order", "exp_ty_code", "exp_bcnc_code", "exp_io_type", "exp_de", "exp_content", "regist_dtm", "register_id"]:
        if key in params:
            data[key] = params[key]
        else:
            if key in ('exp_de',):
                data[key] = datetime.datetime.now(timezone('Asia/Seoul')).strftime("%Y-%m-%d")

    if "regist_dtm" not in data:
        data["regist_dtm"] = datetime.datetime.now(timezone('Asia/Seoul'))

    if "register_id" not in data:
        data["register_id"] = session["member"]["member_id"]


    order = {"1" : 1, "2" : 2, "3": 7, "4":3, "5":4, "6": 5, "7": 8, "8": 6}
    if "exp_cost" in params:
        for idx, exp_cost in enumerate(params["exp_cost"], 1):
            data['exp_cost'] = exp_cost
            data["exp_se_code"] = order[str(idx)]
            keys = list(data.keys())
            query = "INSERT INTO expense({}) VALUES({})".format(",".join(keys), ",".join(["%({})s".format(k) for k in keys]))
            g.curs.execute(query, data)

def insert_expP2(params):
    data = dict()
    for key in ["eng_sn", "plan_order", "exp_ty_code", "exp_bcnc_code", "exp_io_type", "exp_de", "exp_content", "regist_dtm", "register_id"]:
        if key in params:
            data[key] = params[key]
        else:
            if key in ('exp_de',):
                data[key] = datetime.datetime.now(timezone('Asia/Seoul')).strftime("%Y-%m-%d")

    if "regist_dtm" not in data:
        data["regist_dtm"] = datetime.datetime.now(timezone('Asia/Seoul'))

    if "register_id" not in data:
        data["register_id"] = session["member"]["member_id"]

    order = {"1" : 1, "2" : 95, "3": 96, "4":97, "5":98, "6": 99, "7": 100, "8": 101}
    if "exp_cost" in params:
        for idx, exp_cost in enumerate(params["exp_cost"], 1):
            data['exp_cost'] = exp_cost
            data["exp_se_code"] = order[str(idx)]
            keys = list(data.keys())
            query = "INSERT INTO expense({}) VALUES({})".format(",".join(keys), ",".join(["%({})s".format(k) for k in keys]))
            g.curs.execute(query, data)

def update_plan(params):
    data = dict()
    for key in ["eng_sn", "cntrwk_bgnde", "cntrwk_endde", "cp_a_cost", "cp_b_cost", "cp_c_cost", "todo", "result"]:
        if key in params:
            data[key] = params[key]
        else:
            data[key] = None

    data["plan_sn"] = params["s_plan_sn"]
    keys = list(data.keys())
    query = "UPDATE plan SET {} WHERE plan_sn=%(plan_sn)s".format(",".join(["{0}=%({0})s".format(k) for k in keys]))
    g.curs.execute(query, data)

def update_exp_detail(params):
    data = dict()
    for key in ["eng_sn", "plan_order", "exp_cost_num", "cost_content", "cost_1", "cost_2"]:
        if key in params:
            data[key] = params[key]
        else:
            data[key] = None

    data["d_sn"] = params["d_sn"]
    keys = list(data.keys())
    query = "UPDATE detail SET {} WHERE d_sn=%(d_sn)s".format(",".join(["{0}=%({0})s".format(k) for k in keys]))
    g.curs.execute(query, data)

def update_exp(params):
    data = dict()
    for key in ["eng_sn", "plan_order", "exp_ty_code", "exp_se_code", "exp_bcnc_code", "exp_io_type", "exp_de", "exp_content", "exp_cost"]:
        if key in params:
            data[key] = params[key]
        else:
            data[key] = None

    data["exp_sn"] = params["s_exp_sn"]
    keys = list(data.keys())
    query = "UPDATE expense SET {} WHERE exp_sn=%(exp_sn)s".format(",".join(["{0}=%({0})s".format(k) for k in keys]))
    g.curs.execute(query, data)

def update_expP(params):
    data = dict()
    for key in ["eng_sn", "plan_order", "exp_ty_code", "exp_bcnc_code", "exp_io_type", "exp_de", "exp_content"]:
        if key in params:
            data[key] = params[key]
        else:
            if key in ('exp_de', ):
                data[key] = datetime.datetime.now(timezone('Asia/Seoul')).strftime("%Y-%m-%d")
            else:
                data[key] = None
    order = {"1" : 1, "2" : 2, "3": 7, "4":3, "5":4, "6": 5, "7": 8, "8": 6}
    if "exp_cost" in params:
        for idx, exp_cost in enumerate(params["exp_cost"], 1):
            data['exp_cost'] = exp_cost
            keys = list(data.keys())
            data["exp_se_code"] = order[str(idx)]
            data["regist_dtm"] = params["s_regist_dtm"]
            query = "UPDATE expense SET {} WHERE exp_se_code=%(exp_se_code)s AND regist_dtm=%(regist_dtm)s".format(
                ",".join(["{0}=%({0})s".format(k) for k in keys]))
            g.curs.execute(query, data)

def update_expP2(params):
    data = dict()
    for key in ["eng_sn", "plan_order", "exp_ty_code", "exp_bcnc_code", "exp_io_type", "exp_de", "exp_content"]:
        if key in params:
            data[key] = params[key]
        else:
            if key in ('exp_de', ):
                data[key] = datetime.datetime.now(timezone('Asia/Seoul')).strftime("%Y-%m-%d")
            else:
                data[key] = None
    order = {"1" : 1, "2" : 95, "3": 96, "4":97, "5":98, "6": 99, "7": 100, "8": 101}
    if "exp_cost" in params:
        for idx, exp_cost in enumerate(params["exp_cost"], 1):
            data['exp_cost'] = exp_cost
            keys = list(data.keys())
            data["exp_se_code"] = order[str(idx)]
            data["regist_dtm"] = params["s_regist_dtm"]
            query = "UPDATE expense SET {} WHERE exp_se_code=%(exp_se_code)s AND regist_dtm=%(regist_dtm)s".format(
                ",".join(["{0}=%({0})s".format(k) for k in keys]))
            g.curs.execute(query, data)


def delete_plan(params):
    query  = """DELETE
    				FROM plan
    				WHERE 1=1
    				AND plan_sn = %(s_plan_sn)s
    """
    g.curs.execute(query, params)

def delete_exp(params):
    query  = """DELETE
    				FROM expense
    				WHERE 1=1
    				AND exp_sn = %(s_exp_sn)s
    """
    g.curs.execute(query, params)

def delete_expP(params):
    query  = """DELETE
    				FROM expense
    				WHERE 1=1
    				AND DATE_FORMAT(regist_dtm, '%%Y-%%m-%%d %%T') = %(s_regist_dtm)s
    				AND eng_sn=%(s_eng_sn)s
    """
    g.curs.execute(query, params)

def delete_expP2(params):
    query  = """DELETE
    				FROM expense
    				WHERE 1=1
    				AND DATE_FORMAT(regist_dtm, '%%Y-%%m-%%d %%T') = %(s_regist_dtm)s
    				AND eng_sn=%(s_eng_sn)s
    """
    g.curs.execute(query, params)

def delete_exp_detail(params):
    query  = """DELETE
    				FROM detail
    				WHERE 1=1
    				AND d_sn = %(s_d_sn)s
    """
    g.curs.execute(query, params)

def get_exp(params):
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
				AND e.exp_sn = %(s_exp_sn)s
"""
    g.curs.execute(query, params)
    result = g.curs.fetchone()
    return result

def get_expP(params):
    query = """SELECT SUM(IF(e.exp_se_code=1,e.exp_cost,0)) AS exp_cost_1
				, SUM(IF(e.exp_se_code=2,e.exp_cost,0)) AS exp_cost_2
				, SUM(IF(e.exp_se_code=3,e.exp_cost,0)) AS exp_cost_3
				, SUM(IF(e.exp_se_code=4,e.exp_cost,0)) AS exp_cost_4
				, SUM(IF(e.exp_se_code=5,e.exp_cost,0)) AS exp_cost_5
				, SUM(IF(e.exp_se_code=6,e.exp_cost,0)) AS exp_cost_6
				, SUM(IF(e.exp_se_code=7,e.exp_cost,0)) AS exp_cost_7
				, SUM(IF(e.exp_se_code=8,e.exp_cost,0)) AS exp_cost_8
				, e.plan_order AS plan_order
				, DATE_FORMAT(e.regist_dtm, '%%Y-%%m-%%d %%T') AS regist_dtm
				, e.eng_sn AS eng_sn
				FROM expense e
				WHERE 1=1
				AND DATE_FORMAT(e.regist_dtm, '%%Y-%%m-%%d %%T') = %(s_regist_dtm)s
				AND e.exp_ty_code IN ('P')
				AND e.eng_sn=%(s_eng_sn)s
				GROUP BY plan_order, regist_dtm
"""
    g.curs.execute(query, params)
    result = g.curs.fetchone()
    return result

def get_expP2(params):
    query = """SELECT SUM(IF(e.exp_se_code=1,e.exp_cost,0)) AS exp_cost_1
				, SUM(IF(e.exp_se_code=95,e.exp_cost,0)) AS exp_cost_2
				, SUM(IF(e.exp_se_code=96,e.exp_cost,0)) AS exp_cost_3
				, SUM(IF(e.exp_se_code=97,e.exp_cost,0)) AS exp_cost_4
				, SUM(IF(e.exp_se_code=98,e.exp_cost,0)) AS exp_cost_5
				, SUM(IF(e.exp_se_code=99,e.exp_cost,0)) AS exp_cost_6
				, SUM(IF(e.exp_se_code=100,e.exp_cost,0)) AS exp_cost_7
				, SUM(IF(e.exp_se_code=101,e.exp_cost,0)) AS exp_cost_8
				, e.plan_order AS plan_order
				, DATE_FORMAT(e.regist_dtm, '%%Y-%%m-%%d %%T') AS regist_dtm
				, e.eng_sn AS eng_sn
				FROM expense e
				WHERE 1=1
				AND DATE_FORMAT(e.regist_dtm, '%%Y-%%m-%%d %%T') = %(s_regist_dtm)s
				AND e.exp_ty_code IN ('P')
				AND e.eng_sn=%(s_eng_sn)s
				GROUP BY plan_order, regist_dtm
"""
    g.curs.execute(query, params)
    result = g.curs.fetchone()
    return result