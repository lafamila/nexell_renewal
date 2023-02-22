from flask import session, jsonify, g
import onetimepass as otp
import random
import string
import urllib
import datetime
from app.helpers.class_helper import Map
from app.helpers.datatable_helper import dt_query
from collections import OrderedDict
import itertools
def get_completed_summary(params):
    year = int(params['s_pxcond_mt'].split("-")[0])
    month = int(params['s_pxcond_mt'].split("-")[1])
    query = """SELECT t.amt_ty_code AS amt_ty_code
				, (SELECT code_nm FROM code WHERE ctmmny_sn=1 AND parnts_code='AMT_TY_CODE' AND code=t.amt_ty_code) AS amt_ty_nm
				, t.dept_code
				, IF(dept_code='ETC', '기타', (SELECT code_nm FROM code WHERE ctmmny_sn=1 AND parnts_code='DEPT_CODE' AND code=t.dept_code)) AS dept_nm
				, SUM(IFNULL(m_contract_amount, 0)) AS m_contract_amount
				, IFNULL(SUM(y_contract_amount), 0) AS y_contract_amount
				, SUM(IFNULL(ty8_goal_amount, 0)) AS ty8_goal_amount
				, SUM(IFNULL(ty9_goal_amount, 0)) AS ty9_goal_amount
				, SUM(IFNULL(ty8_goal_amount_sum, 0)) AS ty8_goal_amount_sum
				, SUM(IFNULL(ty9_goal_amount_sum, 0)) AS ty9_goal_amount_sum
				, SUM(IFNULL(ty8_goal_amount_total, 0)) AS ty8_goal_amount_total
				, SUM(IFNULL(1m, 0)) AS m1
				, SUM(IFNULL(2m, 0)) AS m2
				, SUM(IFNULL(3m, 0)) AS m3
				, SUM(IFNULL(4m, 0)) AS m4
				, SUM(IFNULL(5m, 0)) AS m5
				, SUM(IFNULL(6m, 0)) AS m6
				, SUM(IFNULL(7m, 0)) AS m7
				, SUM(IFNULL(8m, 0)) AS m8
				, SUM(IFNULL(9m, 0)) AS m9
				, SUM(IFNULL(10m, 0)) AS m10
				, SUM(IFNULL(11m, 0)) AS m11
				, SUM(IFNULL(12m, 0)) AS m12
				"""
    if year >= 2023:
        query += """, (SELECT COUNT(code) FROM code WHERE ctmmny_sn=1 AND parnts_code='DEPT_CODE' AND (code LIKE 'TS%%' OR code LIKE 'BI%%' OR code IN ('ST', 'EL', 'CT', 'MA'))) - (SELECT COUNT(code) FROM code WHERE ctmmny_sn=1 AND parnts_code='DEPT_CODE' AND code IN ('EL', 'CT', 'MA')) + 1 AS dept_count"""
    else:
        query += """, (SELECT COUNT(code) FROM code WHERE ctmmny_sn=1 AND parnts_code='DEPT_CODE' AND (code LIKE 'TS%%' OR code LIKE 'BI%%')) AS dept_count"""

    query += """
                , IF(dept_code='ETC', 99, (SELECT code_ordr FROM code WHERE ctmmny_sn=1 AND parnts_code='DEPT_CODE' AND code=t.dept_code )) AS dept_order
				FROM (
				SELECT g.amt_ty_code
				, IF(m.dept_code IN ('EL','CT', 'MA'), 'ETC', m.dept_code) AS dept_code
				, CASE WHEN g.amt_ty_code = '2' THEN GET_SUJU_AMOUNT({0}, g.mber_sn, 'M')
				WHEN g.amt_ty_code = '3' THEN GET_PXCOND_MONTH_AMOUNT('C', {0}, g.mber_sn)
				WHEN g.amt_ty_code = '5' THEN GET_VA_MONTH_AMOUNT({1}, g.mber_sn)
				END AS m_contract_amount
				, CASE WHEN g.amt_ty_code = '2' THEN GET_SUJU_AMOUNT({0}, g.mber_sn, 'A')
				WHEN g.amt_ty_code = '3' THEN GET_PXCOND_TOTAL_AMOUNT('C', {1}, g.mber_sn)
				WHEN g.amt_ty_code = '5' THEN GET_VA_TOTAL_AMOUNT({1}, g.mber_sn)
				END AS y_contract_amount
				, GET_GOAL_AMOUNT({0}, '8', g.mber_sn, 'M') AS ty8_goal_amount  
				, GET_GOAL_AMOUNT({0}, '9', g.mber_sn, 'M') AS ty9_goal_amount
				, GET_GOAL_AMOUNT({0}, '8', g.mber_sn, 'A') AS ty8_goal_amount_sum
				, GET_GOAL_AMOUNT({0}, '9', g.mber_sn, 'A') AS ty9_goal_amount_sum
				, GET_GOAL_AMOUNT({0}, '8', g.mber_sn, 'Y') AS ty8_goal_amount_total
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
				, g.stdyy
				FROM (SELECT stdyy, amt_ty_code, mber_sn, SUM(IFNULL(1m, 0)) AS 1m, SUM(IFNULL(2m, 0)) AS 2m, SUM(IFNULL(3m, 0)) AS 3m, SUM(IFNULL(4m, 0)) AS 4m, SUM(IFNULL(5m, 0)) AS 5m, SUM(IFNULL(6m, 0)) AS 6m, SUM(IFNULL(7m, 0)) AS 7m, SUM(IFNULL(8m, 0)) AS 8m, SUM(IFNULL(9m, 0)) AS 9m, SUM(IFNULL(10m, 0)) AS 10m, SUM(IFNULL(11m, 0)) AS 11m, SUM(IFNULL(12m, 0)) AS 12m FROM goal WHERE stdyy = SUBSTRING({0}, 1, 4) AND amt_ty_code IN ('2','3','5') GROUP BY mber_sn, amt_ty_code, stdyy) g
				JOIN member m
				ON m.mber_sn=g.mber_sn
				WHERE 1=1				
				"""
    if year >= 2023:
        query += """ AND (m.dept_code LIKE 'TS%%' OR m.dept_code LIKE 'BI%%' OR m.dept_code IN ('ST', 'EL', 'CT', 'MA'))"""
    else:
        query += """ AND (m.dept_code LIKE 'TS%%' OR m.dept_code LIKE 'BI%%')"""

    query += """
                ORDER BY g.amt_ty_code, m.dept_code
				) t
				GROUP BY t.amt_ty_code, t.dept_code
				ORDER BY t.amt_ty_code, dept_order, t.dept_code"""

    g.curs.execute(query.format("'{}'".format(params['s_pxcond_mt']), month))
    result = g.curs.fetchall()

    g.curs.execute("SELECT parnts_code AS p, code AS v, code_nm AS nm, code_ordr AS ordr FROM code WHERE PARNTS_CODE IN ('AMT_TY_CODE', 'DEPT_CODE')")
    codes = g.curs.fetchall()
    code_nms = {(c["p"], c["v"]) : (c["nm"], c["ordr"]) for c in codes}
    code_nms[('DEPT_CODE', 'ETC')] = "기타"
    dept_codes = ['TS1', 'TS2', 'TS3', 'BI']
    amt_ty_codes = ['2', '3', '5']
    if year >= 2023:
        dept_codes = ['ST', 'TS1', 'TS2', 'BI', 'ETC']

    tables = {(r['amt_ty_code'], r['dept_code']) : r for r in result}
    table_result = []
    for amt_ty_code, dept_code in itertools.product(amt_ty_codes, dept_codes):
        if (amt_ty_code, dept_code) not in tables:
            table_result.append(new_row(amt_ty_code, code_nms[("AMT_TY_CODE", amt_ty_code)][0], dept_code, code_nms[("DEPT_CODE", dept_code)][0], code_nms[("DEPT_CODE", dept_code)][1]))
        else:
            table_result.append(tables[(amt_ty_code, dept_code)])

    for r in table_result:
        r['dept_count'] = len(dept_codes)

    return table_result

def new_row(amt_ty_code, amt_ty_nm, dept_code, dept_nm, dept_ordr):
    row = {"amt_ty_code" : amt_ty_code, "amt_ty_nm" : amt_ty_nm, "dept_code" : dept_code, "dept_nm" : dept_nm}
    row['m_contract_amount'] = 0
    row['y_contract_amount'] = 0
    row['ty8_goal_amount'] = 0
    row['ty9_goal_amount'] = 0
    row['ty8_goal_amount_sum'] = 0
    row['ty9_goal_amount_sum'] = 0
    row['ty8_goal_amount_total'] = 0
    for _ in range(1, 13):
        row["m{}".format(_)] = 0
    row["dept_count"] = 0
    row["dept_order"] = dept_ordr
    return row