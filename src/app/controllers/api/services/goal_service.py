from flask import session, jsonify, g
from app.helpers.datatable_helper import dt_query
from collections import OrderedDict
import datetime
import calendar
from pytz import timezone
def get_contract_list_by_amt(params):
    query = """SELECT cntrct_sn AS value
				, cntrct_nm AS label
				, cntrct_no AS etc1
				, cntrct_de AS etc2
				, CONCAT(
				cntrct_no, '.',
				cntrct_nm, '.',
				cntrct_de
				) AS etc3
				, (SELECT bcnc_nm FROM bcnc WHERE bcnc_sn=c.bcnc_sn) AS bcnc_nm
				, prjct_creat_at
				, (SELECT COUNT(prjct_sn) FROM project WHERE cntrct_sn=c.cntrct_sn) AS prjct_cnt
				, c.spt_chrg_sn
				, c.bsn_chrg_sn
				, c.progrs_sttus_code
				FROM contract c
				WHERE 1=1
				AND ctmmny_sn = 1
                """
    data = []
    if params["s_amt_ty_code"] == "2":
        query += " AND (progrs_sttus_code = 'B' OR (progrs_sttus_code = 'P' AND regist_dtm BETWEEN '{0}-01-01 00:00:00' AND '{0}-12-31 23:59:59'))".format(params['s_year'])
    else:
        query += " AND progrs_sttus_code = 'P' "

    if "s_bsn_chrg_sn" in params and params["s_bsn_chrg_sn"]:
        query += " AND c.bsn_chrg_sn=%s"
        data.append(params["s_bsn_chrg_sn"])
    g.curs.execute(query, data)
    result = g.curs.fetchall()
    return result

def get_contract_list_by_amt_regist(params):
    query = """SELECT cntrct_sn AS value
				, cntrct_nm AS label
				, cntrct_no AS etc1
				, cntrct_de AS etc2
				, CONCAT(
				cntrct_no, '.',
				cntrct_nm, '.',
				cntrct_de
				) AS etc3
				, (SELECT bcnc_nm FROM bcnc WHERE bcnc_sn=c.bcnc_sn) AS bcnc_nm
				, prjct_creat_at
				, (SELECT COUNT(prjct_sn) FROM project WHERE cntrct_sn=c.cntrct_sn) AS prjct_cnt
				, c.spt_chrg_sn
				, c.bsn_chrg_sn
				, c.progrs_sttus_code
				FROM contract c
				WHERE 1=1
				AND ctmmny_sn = 1
                """
    data = []
    if params["s_amt_ty_code"] == "2":
        query += " AND (progrs_sttus_code IN ('B', 'P', 'S'))".format(params['s_year'])
    else:
        query += " AND (progrs_sttus_code IN ('B', 'P', 'S'))".format(params['s_year'])

    if "s_bsn_chrg_sn" in params and params["s_bsn_chrg_sn"]:
        query += " AND c.bsn_chrg_sn=%s"
        data.append(params["s_bsn_chrg_sn"])

    if "s_spt_chrg_sn" in params and params["s_spt_chrg_sn"]:
        query += " AND c.spt_chrg_sn=%s"
        data.append(params["s_spt_chrg_sn"])

    g.curs.execute(query, data)
    result = g.curs.fetchall()
    return result

def get_goals_summary(params):
    query = """SELECT g.stdyy
                , g.amt_ty_code
                , (SELECT code_nm FROM code WHERE parnts_code='AMT_TY_CODE' AND code=g.amt_ty_code) AS amt_ty_nm
                , m.dept_code
                , (SELECT code_nm FROM code WHERE parnts_code='DEPT_CODE' AND code=m.dept_code) AS dept_nm
                , SUM(IFNULL(g.1m, 0)) AS 1m
                , SUM(IFNULL(g.2m, 0)) AS 2m
                , SUM(IFNULL(g.3m, 0)) AS 3m
                , SUM(IFNULL(g.4m, 0)) AS 4m
                , SUM(IFNULL(g.5m, 0)) AS 5m
                , SUM(IFNULL(g.6m, 0)) AS 6m
                , SUM(IFNULL(g.7m, 0)) AS 7m
                , SUM(IFNULL(g.8m, 0)) AS 8m
                , SUM(IFNULL(g.9m, 0)) AS 9m
                , SUM(IFNULL(g.10m, 0)) AS 10m
                , SUM(IFNULL(g.11m, 0)) AS 11m
                , SUM(IFNULL(g.12m, 0)) AS 12m
                , SUM((IFNULL(g.1m, 0) + IFNULL(g.2m, 0) + IFNULL(g.3m, 0)+ IFNULL(g.4m, 0)+ IFNULL(g.5m, 0)+ IFNULL(g.6m, 0)+ IFNULL(g.7m, 0)+ IFNULL(g.8m, 0)+ IFNULL(g.9m, 0)+ IFNULL(g.10m, 0)+ IFNULL(g.11m, 0)+ IFNULL(g.12m, 0))) AS tot
				, (SELECT code_ordr FROM code WHERE ctmmny_sn=1 AND parnts_code='DEPT_CODE' AND code=m.dept_code) AS code_ordr
                FROM goal g
                LEFT JOIN member m ON g.mber_sn=m.mber_sn
                LEFT OUTER JOIN contract c ON g.cntrct_sn=c.cntrct_sn
                WHERE 1=1
                AND m.mber_sttus_code='H'
                AND (c.cntrct_sn <> 0 or g.cntrct_sn=-1)
    """
    data = []
    if "s_amt_ty_code" in params and params["s_amt_ty_code"]:
        query += " and g.amt_ty_code=%s"
        data.append(params["s_amt_ty_code"])

    if "s_year" in params and params["s_year"]:
        query += " and g.stdyy=%s"
        data.append(params["s_year"])

    if "s_dept_code" in params and params["s_dept_code"]:
        query += " and m.dept_code=%s"
        data.append(params["s_dept_code"])

    if "s_bcnc_sn" in params and params["s_bcnc_sn"]:
        query += " and c.bcnc_sn=%s"
        data.append(params["s_bcnc_sn"])

    if "s_mber_sn" in params and params["s_mber_sn"]:
        query += " and g.mber_sn=%s"
        data.append(params["s_mber_sn"])

    if "s_spt_nm" in params and params["s_spt_nm"]:
        query += " and c.spt_nm LIKE %s"
        data.append("%{}%".format(params["s_spt_nm"]))
    query += " GROUP BY stdyy, amt_ty_code, dept_code"
    query += " ORDER BY code_ordr ASC"
    g.curs.execute(query, data)
    result = g.curs.fetchall()
    return result
def get_goals(params):
    query = """SELECT g.stdyy
                , g.amt_ty_code
                , g.mber_sn
                , GET_MEMBER_NAME(g.mber_sn, 'S') AS mber_nm
                , c.bcnc_sn
                , (SELECT bcnc_nm FROM bcnc WHERE bcnc_sn=c.bcnc_sn) AS bcnc_nm
                , m.dept_code
                , (SELECT code_nm FROM code WHERE parnts_code='DEPT_CODE' AND code=m.dept_code) AS dept_nm
                , g.cntrct_sn
                , IFNULL(c.spt_nm, '') AS spt_nm
                , g.1m
                , g.2m
                , g.3m
                , g.4m
                , g.5m
                , g.6m
                , g.7m
                , g.8m
                , g.9m
                , g.10m
                , g.11m
                , g.12m
                , (IFNULL(g.1m, 0) + IFNULL(g.2m, 0) + IFNULL(g.3m, 0)+ IFNULL(g.4m, 0)+ IFNULL(g.5m, 0)+ IFNULL(g.6m, 0)+ IFNULL(g.7m, 0)+ IFNULL(g.8m, 0)+ IFNULL(g.9m, 0)+ IFNULL(g.10m, 0)+ IFNULL(g.11m, 0)+ IFNULL(g.12m, 0)) AS tot
				, (SELECT code_ordr FROM code WHERE ctmmny_sn=1 AND parnts_code='DEPT_CODE' AND code=m.dept_code) AS code_ordr
                FROM goal g
                LEFT JOIN member m ON g.mber_sn=m.mber_sn
                LEFT OUTER JOIN contract c ON g.cntrct_sn=c.cntrct_sn
                WHERE 1=1
                AND m.mber_sttus_code='H'
                AND (c.cntrct_sn <> 0 or g.cntrct_sn = -1)
    """
    data = []
    if "s_amt_ty_code" in params and params["s_amt_ty_code"]:
        query += " and g.amt_ty_code=%s"
        data.append(params["s_amt_ty_code"])

    if "s_year" in params and params["s_year"]:
        query += " and g.stdyy=%s"
        data.append(params["s_year"])

    if "s_dept_code" in params and params["s_dept_code"]:
        query += " and m.dept_code=%s"
        data.append(params["s_dept_code"])

    if "s_bcnc_sn" in params and params["s_bcnc_sn"]:
        query += " and c.bcnc_sn=%s"
        data.append(params["s_bcnc_sn"])

    if "s_mber_sn" in params and params["s_mber_sn"]:
        query += " and g.mber_sn=%s"
        data.append(params["s_mber_sn"])

    if "s_spt_nm" in params and params["s_spt_nm"]:
        query += " and c.spt_nm LIKE %s"
        data.append("%{}%".format(params["s_spt_nm"]))

    params["custom_order"] = ["stdyy", "code_ordr", "mber_nm", "IF(c.bcnc_sn = 244, 1, 0) ASC", "bcnc_nm", "spt_nm"]
    return dt_query(query, data, params)

def get_goals_by_member(params):
    query = """SELECT g.stdyy
                , g.amt_ty_code
                , g.mber_sn
                , g.cntrct_sn
               FROM goal g
               WHERE g.mber_sn=%(chrg_sn)s
               AND g.amt_ty_code=%(s_amt_ty_code)s
               AND g.stdyy=%(s_year)s
            """
    g.curs.execute(query, params)
    result = g.curs.fetchall()
    return result

def insert_goals(params, cntrct_sns):
    stdyy = params["s_year"]
    amt_ty_code = params["s_amt_ty_code"]
    mber_sn = params["chrg_sn"]
    data = [(stdyy, amt_ty_code, mber_sn, cntrct_sn) for cntrct_sn in cntrct_sns]
    query = "INSERT INTO goal(stdyy, amt_ty_code, mber_sn, cntrct_sn, regist_dtm, register_id) VALUES (%s, %s, %s, %s, NOW(), 'nexell')"
    g.curs.executemany(query, data)

def set_goals(params):
    if int(params['data']) == 0 :
        params['data'] = None
    query = """UPDATE goal SET {}=%(data)s WHERE stdyy=%(s_year)s AND amt_ty_code=%(s_amt_ty_code)s AND cntrct_sn=%(s_cntrct_sn)s AND mber_sn=%(s_mber_sn)s""".format(params["column"])
    g.curs.execute(query, params)

def delete_goal(params):
    query = "DELETE FROM goal WHERE stdyy=%(stdyy)s AND amt_ty_code=%(amt_ty_code)s AND mber_sn=%(mber_sn)s AND cntrct_sn=%(cntrct_sn)s"
    g.curs.execute(query, params)