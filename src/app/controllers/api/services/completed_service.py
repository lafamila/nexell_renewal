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
import calendar
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
				FROM (SELECT stdyy, amt_ty_code, mber_sn, SUM(IFNULL(1m, 0)) AS 1m, SUM(IFNULL(2m, 0)) AS 2m, SUM(IFNULL(3m, 0)) AS 3m, SUM(IFNULL(4m, 0)) AS 4m, SUM(IFNULL(5m, 0)) AS 5m, SUM(IFNULL(6m, 0)) AS 6m, SUM(IFNULL(7m, 0)) AS 7m, SUM(IFNULL(8m, 0)) AS 8m, SUM(IFNULL(9m, 0)) AS 9m, SUM(IFNULL(10m, 0)) AS 10m, SUM(IFNULL(11m, 0)) AS 11m, SUM(IFNULL(12m, 0)) AS 12m FROM goal WHERE stdyy = SUBSTRING({0}, 1, 4) AND amt_ty_code IN ('2','3','5', '8', '9') GROUP BY mber_sn, amt_ty_code, stdyy) g
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

    g.curs.execute(query.format("'{}'".format(params['s_pxcond_mt']), "'{}-{}'".format(str(year).zfill(4), str(month).zfill(2))))
    result = g.curs.fetchall()

    g.curs.execute("SELECT parnts_code AS p, code AS v, code_nm AS nm, code_ordr AS ordr FROM code WHERE PARNTS_CODE IN ('AMT_TY_CODE', 'DEPT_CODE')")
    codes = g.curs.fetchall()
    code_nms = {(c["p"], c["v"]) : (c["nm"], c["ordr"]) for c in codes}
    code_nms[('DEPT_CODE', 'ETC')] = ("기타", 999)
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

def get_contract_status_list(params):
    query = """SELECT t.amt_ty_code
				, (SELECT code_nm FROM code WHERE ctmmny_sn=1 AND parnts_code='AMT_TY_CODE' AND code=t.amt_ty_code) AS amt_ty_nm
				, t.dept_code
				, (SELECT code_nm FROM code WHERE ctmmny_sn=1 AND parnts_code='DEPT_CODE' AND code=t.dept_code) AS dept_nm
				, IFNULL(SUM(m_contract_amount), 0) AS m_contract_amount
				, IFNULL(SUM(y_contract_amount), 0) AS y_contract_amount
				, SUM(ty8_goal_amount) AS ty8_goal_amount
				, SUM(ty9_goal_amount) AS ty9_goal_amount
				, SUM(ty8_goal_amount_sum) AS ty8_goal_amount_sum
				, SUM(ty9_goal_amount_sum) AS ty9_goal_amount_sum
				, SUM(ty8_goal_amount_total) AS ty8_goal_amount_total
				, SUM(1m) AS m1
				, SUM(2m) AS m2
				, SUM(3m) AS m3
				, SUM(4m) AS m4
				, SUM(5m) AS m5
				, SUM(6m) AS m6
				, SUM(7m) AS m7
				, SUM(8m) AS m8
				, SUM(9m) AS m9
				, SUM(10m) AS m10
				, SUM(11m) AS m11
				, SUM(12m) AS m12
				, (SELECT COUNT(code) FROM code WHERE ctmmny_sn=1 AND parnts_code='DEPT_CODE' AND code LIKE 'TS%%') AS dept_count
				FROM (
				SELECT g.amt_ty_code
				, m.dept_code
				, CASE WHEN g.amt_ty_code = '2' THEN GET_SUJU_AMOUNT(%(s_pxcond_mt)s, g.mber_sn, 'M')
				WHEN g.amt_ty_code = '3' THEN GET_PXCOND_MONTH_AMOUNT('C', %(s_pxcond_mt)s, g.mber_sn)
				WHEN g.amt_ty_code = '5' THEN GET_VA_MONTH_AMOUNT(%(s_pxcond_mt)s, g.mber_sn)
				END AS m_contract_amount
				, CASE WHEN g.amt_ty_code = '2' THEN GET_SUJU_AMOUNT(%(s_pxcond_mt)s, g.mber_sn, 'A')
				WHEN g.amt_ty_code = '3' THEN GET_PXCOND_TOTAL_AMOUNT('C', %(s_pxcond_mt)s, g.mber_sn)
				WHEN g.amt_ty_code = '5' THEN GET_VA_TOTAL_AMOUNT(%(s_pxcond_mt)s, g.mber_sn)
				END AS y_contract_amount
				, GET_GOAL_AMOUNT(%(s_pxcond_mt)s, '8', g.mber_sn, 'M') AS ty8_goal_amount
				, GET_GOAL_AMOUNT(%(s_pxcond_mt)s, '9', g.mber_sn, 'M') AS ty9_goal_amount
				, GET_GOAL_AMOUNT(%(s_pxcond_mt)s, '8', g.mber_sn, 'A') AS ty8_goal_amount_sum
				, GET_GOAL_AMOUNT(%(s_pxcond_mt)s, '9', g.mber_sn, 'A') AS ty9_goal_amount_sum
				, GET_GOAL_AMOUNT(%(s_pxcond_mt)s, '8', g.mber_sn, 'Y') AS ty8_goal_amount_total
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
				FROM goal g
				LEFT JOIN member m
				ON m.mber_sn=g.mber_sn
				WHERE g.stdyy = SUBSTRING(%(s_pxcond_mt)s, 1, 4)
				AND g.amt_ty_code IN ('2','3','5','6')
				AND m.dept_code LIKE 'TS%%'
				ORDER BY g.amt_ty_code, m.dept_code
				) t
				GROUP BY t.amt_ty_code, t.dept_code"""
    g.curs.execute(query, params)
    result = g.curs.fetchall()
    return result

def get_execut_status_list(params):
    ymd = params['s_pxcond_mt']
    y, m = ymd.split("-")
    _, l = calendar.monthrange(int(y), int(m))
    f = 1
    last_day = "{}-{}-{}".format(y.zfill(4), m.zfill(2), str(l).zfill(2))
    first_year = "{}-01-01".format(y.zfill(4))
    last_year = "{}-12-31".format(y.zfill(4))

    query = """SELECT t.spt_chrg_sn AS mber_sn
				, GET_MEMBER_NAME(t.spt_chrg_sn, 'M') AS mber_nm
				, IFNULL(GET_PXCOND_MONTH_AMOUNT2('C', %(s_pxcond_mt)s, t.spt_chrg_sn),0) AS m_contract_amount
				, SUM(excut_amount) AS m_excut_amount
				, IFNULL(GET_PXCOND_TOTAL_AMOUNT2('C', %(s_pxcond_mt)s, t.spt_chrg_sn),0) AS y_contract_amount
				, SUM(complete_amount) AS y_excut_amount
				, (SELECT COUNT(cntrct_sn) FROM contract WHERE spt_chrg_sn=t.spt_chrg_sn AND (progrs_sttus_code IN ('P', 'S')) AND cntrct_de<='{2}') AS spt_cnt
				, (SELECT ofcps_code FROM member WHERE mber_sn=t.spt_chrg_sn) AS ofcps_code
				, (SELECT code_ordr FROM code WHERE parnts_code='DEPT_CODE' AND code=mb.dept_code) AS code_ordr
				, IF(mb.mber_sttus_code = 'H', 0, 1) AS sttus_ordr
				FROM (
				SELECT t.spt_chrg_sn
				, t.cntrct_sn
				, t.bsn_chrg_sn
				, CASE WHEN ct_se_code IN ('1','2','4') THEN GET_ACCOUNT_COMPLETE_AMOUNT3(t.cntrct_sn, t.purchsofc_sn, 'P', %(s_pxcond_mt)s)
				WHEN ct_se_code IN ('3') THEN GET_ACCOUNT_COMPLETE_AMOUNT3(t.cntrct_sn, t.purchsofc_sn, 'S', %(s_pxcond_mt)s)
				ELSE GET_TAXBIL_COMPLETE_AMOUNT3(t.cntrct_sn, t.purchsofc_sn, t.cntrct_execut_code, %(s_pxcond_mt)s)
				END AS complete_amount
				, CASE WHEN ct_se_code IN ('1','2','4') THEN GET_ACCOUNT_EXCUT_AMOUNT(t.cntrct_sn, t.purchsofc_sn, 'P', %(s_pxcond_mt)s)
				WHEN ct_se_code IN ('3') THEN GET_ACCOUNT_EXCUT_AMOUNT(t.cntrct_sn, t.purchsofc_sn, 'S', %(s_pxcond_mt)s)
				ELSE GET_TAXBIL_EXCUT_AMOUNT(t.cntrct_sn, t.purchsofc_sn, t.cntrct_execut_code, %(s_pxcond_mt)s)
				END AS excut_amount
				, (SELECT rm FROM pxcond WHERE cntrct_sn=t.cntrct_sn AND cntrct_execut_code=t.cntrct_execut_code AND bcnc_sn=t.purchsofc_sn ORDER BY pxcond_mt DESC LIMIT 1) AS rm
				FROM (
				SELECT m.dept_code AS bsn_dept_code
				, ct.bcnc_sn AS cntrct_bcnc_sn
				, ct.bsn_chrg_sn
				, ct.spt_chrg_sn
				, ct.spt_nm
				, co.cntrct_sn
				, co.cntrct_execut_code
				, CASE WHEN co.cntrct_execut_code = 'C' THEN '0'
				ELSE co.ct_se_code
				END AS ct_se_code
				, co.purchsofc_sn
				FROM cost co
				JOIN contract ct
				ON co.cntrct_sn=ct.cntrct_sn
				LEFT OUTER JOIN member m
				ON ct.bsn_chrg_sn=m.mber_sn
				WHERE ct.cntrct_sn IS NOT NULL
				AND co.ct_se_code NOT IN ('61','62','7','10')
				AND ct.prjct_ty_code = 'NR'
				AND co.cntrct_execut_code IN ('E')
				AND m.dept_code NOT IN ('MA')
				AND m.mber_sttus_code IN ('H')
				AND ct.cntrct_sn IN (SELECT cntrct_sn FROM contract WHERE progrs_sttus_code <> 'C' OR (progrs_sttus_code = 'C' AND update_dtm BETWEEN '{0} 00:00:00' AND '{1} 23:59:59'))
				AND ct.cntrct_sn IN (SELECT cntrct_sn FROM contract WHERE progrs_sttus_code <> 'C' OR (progrs_sttus_code = 'C' AND update_dtm <= '{2} 23:59:59'))
				) t
				GROUP BY bsn_dept_code, bsn_chrg_sn, cntrct_bcnc_sn, spt_chrg_sn, spt_nm, cntrct_sn, cntrct_execut_code, ct_se_code, purchsofc_sn
				) t
				JOIN member mb
				ON mb.mber_sn=t.spt_chrg_sn
				GROUP BY spt_chrg_sn
				ORDER BY sttus_ordr, code_ordr, ofcps_code, mber_nm """.format(first_year, last_year, last_day)

    g.curs.execute(query, params)
    result = g.curs.fetchall()
    return result

def get_completed_reportNR_M2(params):
    ymd = params['s_pxcond_mt']
    y, m = ymd.split("-")
    _, l = calendar.monthrange(int(y), int(m))
    f = 1
    first_day = "{}-{}-{}".format(y.zfill(4), m.zfill(2), str(f).zfill(2))
    last_day = "{}-{}-{}".format(y.zfill(4), m.zfill(2), str(l).zfill(2))
    first_year = "{}-01-01".format(y.zfill(4))
    last_year = "{}-12-31".format(y.zfill(4))
    query = """SELECT t.bsn_dept_code
				, (SELECT code_nm FROM code WHERE ctmmny_sn='1' AND parnts_code='DEPT_CODE' AND code=t.bsn_dept_code) AS bsn_dept_nm
				, t.cntrct_execut_code
				, (SELECT code_nm FROM code WHERE ctmmny_sn='1' AND parnts_code='CNTRCT_EXECUT_CODE' AND code=t.cntrct_execut_code) AS cntrct_execut_nm
				, t.ct_se_code
				, (SELECT code_nm FROM code WHERE ctmmny_sn='1' AND parnts_code='CT_SE_CODE' AND code=t.ct_se_code) AS ct_se_nm
				, SUM(t.cntrct_amount) AS cntrct_amount
				, GET_TAXBIL_COMPLETE_AMOUNT_M(t.cntrct_sn, t.purchsofc_sn, t.cntrct_execut_code, %(s_pxcond_mt)s) AS complete_amount
				, SUM(GET_TAXBIL_EXCUT_AMOUNT_M(t.cntrct_sn, t.purchsofc_sn, t.cntrct_execut_code, %(s_pxcond_mt)s)) AS tax_amount
				, GET_CONTRACT_AMOUNT(t.cntrct_sn, t.cntrct_execut_code, %(s_pxcond_mt)s) AS c_amt_sum
				, GET_PXCOND_AMOUNT(t.cntrct_sn, t.cntrct_execut_code, %(s_pxcond_mt)s) AS p_amt_sum
				, (SELECT rm FROM pxcond WHERE cntrct_sn=t.cntrct_sn AND cntrct_execut_code=t.cntrct_execut_code AND bcnc_sn=t.purchsofc_sn ORDER BY pxcond_mt DESC LIMIT 1) AS rm
				, (SELECT ofcps_code FROM member WHERE mber_sn=t.spt_chrg_sn) AS ofcps_code
				FROM (
				SELECT ct.prjct_ty_code
				, m.dept_code AS bsn_dept_code
				, ct.bcnc_sn AS cntrct_bcnc_sn
				, ct.bsn_chrg_sn
				, ct.prjct_creat_at
				, ct.cntrct_de
				, ct.progrs_sttus_code
				, ct.spt_chrg_sn
				, ct.spt_nm
				, ct.cntrwk_bgnde
				, ct.cntrwk_endde
				, co.cntrct_sn
				, co.cntrct_execut_code
				, co.ct_se_code
				, co.purchsofc_sn
				, CASE WHEN co.cntrct_execut_code = 'C' THEN IFNULL(co.qy*co.salamt, 0)
				ELSE IFNULL(co.qy*co.puchas_amount, 0)
				END AS cntrct_amount
				FROM cost co
				JOIN contract ct
				ON co.cntrct_sn=ct.cntrct_sn
				LEFT OUTER JOIN member m
				ON ct.bsn_chrg_sn=m.mber_sn
				WHERE 1=1
				AND ct.cntrct_sn IN (SELECT cntrct_sn FROM contract WHERE progrs_sttus_code <> 'C' OR (progrs_sttus_code = 'C' AND update_dtm BETWEEN '{0} 00:00:00' AND '{1} 23:59:59'))
				AND co.cost_date <= '{2}'
				AND ((co.ct_se_code IN ('61', '62', '63') AND co.cntrct_execut_code = 'C') OR (co.ct_se_code IN ('62', '61', '63') AND co.cntrct_execut_code = 'E'))
				AND ct.prjct_ty_code = 'NR'
				AND ct.cntrct_de < '{2}'
				) t
				GROUP BY bsn_dept_code, cntrct_execut_code, ct_se_code
				ORDER BY bsn_dept_code """.format(first_year, last_year, last_day)
    g.curs.execute(query, params)
    result = g.curs.fetchall()
    return result
def get_completed_reportNR(params):
    ymd = params['s_pxcond_mt']
    y, m = ymd.split("-")
    _, l = calendar.monthrange(int(y), int(m))
    f = 1
    first_day = "{}-{}-{}".format(y.zfill(4), m.zfill(2), str(f).zfill(2))
    last_day = "{}-{}-{}".format(y.zfill(4), m.zfill(2), str(l).zfill(2))
    first_year = "{}-01-01".format(y.zfill(4))
    last_year = "{}-12-31".format(y.zfill(4))
    query = """SELECT t.prjct_ty_code
				, t.prjct_creat_at
				, t.bsn_dept_code
				, (SELECT code_nm FROM code WHERE ctmmny_sn='1' AND parnts_code='DEPT_CODE' AND code=t.bsn_dept_code) AS bsn_dept_nm
				, t.bsn_chrg_sn
				, GET_MEMBER_NAME(t.bsn_chrg_sn, 'M') AS bsn_chrg_nm
				, t.cntrct_bcnc_sn
				, (SELECT bcnc_nm FROM bcnc WHERE bcnc_sn=t.cntrct_bcnc_sn) AS cntrct_bcnc_nm
				, t.spt_chrg_sn
				, GET_MEMBER_NAME(t.spt_chrg_sn, 'M') AS spt_chrg_nm
				, t.spt_nm
				, t.cntrwk_bgnde
				, t.cntrwk_endde
				, t.cntrct_de
				, t.progrs_sttus_code
				, t.cntrct_sn
				, t.cntrct_execut_code
				, (SELECT code_nm FROM code WHERE ctmmny_sn='1' AND parnts_code='CNTRCT_EXECUT_CODE' AND code=t.cntrct_execut_code) AS cntrct_execut_nm
				, t.ct_se_code
				, (SELECT code_nm FROM code WHERE ctmmny_sn='1' AND parnts_code='CT_SE_CODE' AND code=t.ct_se_code) AS ct_se_nm
				, t.purchsofc_sn
				, (SELECT bcnc_nm FROM bcnc WHERE bcnc_sn=t.purchsofc_sn) AS purchsofc_nm
				, SUM(t.cntrct_amount) AS cntrct_amount
				, (SELECT rate FROM pxcond WHERE pxcond_mt<='{0}' AND cntrct_sn=t.cntrct_sn AND rate IS NOT NULL ORDER BY pxcond_mt DESC LIMIT 1) AS rate
				, CASE WHEN ct_se_code IN ('1','2','4') THEN GET_ACCOUNT_COMPLETE_AMOUNT(t.cntrct_sn, t.purchsofc_sn, 'P', %(s_pxcond_mt)s)
				WHEN ct_se_code IN ('3') THEN GET_ACCOUNT_COMPLETE_AMOUNT(t.cntrct_sn, t.purchsofc_sn, 'S', %(s_pxcond_mt)s)
				WHEN ct_se_code IN ('8') THEN GET_PXCOND_COMPLETE_AMOUNT(t.cntrct_sn, t.purchsofc_sn, 'S', %(s_pxcond_mt)s)
				ELSE GET_TAXBIL_COMPLETE_AMOUNT(t.cntrct_sn, t.purchsofc_sn, t.cntrct_execut_code, %(s_pxcond_mt)s)
				END AS complete_amount
				, CASE WHEN ct_se_code IN ('1','2','4') THEN GET_ACCOUNT_EXCUT_AMOUNT(t.cntrct_sn, t.purchsofc_sn, 'P', %(s_pxcond_mt)s)
				WHEN ct_se_code IN ('3') THEN GET_ACCOUNT_EXCUT_AMOUNT(t.cntrct_sn, t.purchsofc_sn, 'S', %(s_pxcond_mt)s)
				WHEN ct_se_code IN ('8') THEN GET_PXCOND_EXCUT_AMOUNT(t.cntrct_sn, t.purchsofc_sn, t.cntrct_execut_code, %(s_pxcond_mt)s)
				ELSE GET_TAXBIL_EXCUT_AMOUNT(t.cntrct_sn, t.purchsofc_sn, t.cntrct_execut_code, %(s_pxcond_mt)s)
				END AS tax_amount
				, CASE WHEN ct_se_code IN ('1','2','4') THEN GET_ACCOUNT_EXCUT_AMOUNT(t.cntrct_sn, t.purchsofc_sn, 'P', %(s_pxcond_mt)s)
				WHEN ct_se_code IN ('3') THEN GET_ACCOUNT_EXCUT_AMOUNT(t.cntrct_sn, t.purchsofc_sn, 'S', %(s_pxcond_mt)s)
				ELSE GET_PXCOND_EXCUT_AMOUNT(t.cntrct_sn, t.purchsofc_sn, t.cntrct_execut_code, %(s_pxcond_mt)s)
				END AS excut_amount
				, GET_CONTRACT_AMOUNT(t.cntrct_sn, t.cntrct_execut_code, %(s_pxcond_mt)s) AS c_amt_sum
				, GET_PXCOND_AMOUNT(t.cntrct_sn, t.cntrct_execut_code, %(s_pxcond_mt)s) AS p_amt_sum
				, (SELECT rm FROM pxcond WHERE cntrct_sn=t.cntrct_sn AND cntrct_execut_code=t.cntrct_execut_code AND bcnc_sn=t.purchsofc_sn ORDER BY pxcond_mt DESC LIMIT 1) AS rm
				, (SELECT ofcps_code FROM member WHERE mber_sn=t.spt_chrg_sn) AS ofcps_code
				FROM (
				SELECT ct.prjct_ty_code
				, m.dept_code AS bsn_dept_code
				, ct.bcnc_sn AS cntrct_bcnc_sn
				, ct.bsn_chrg_sn
				, ct.prjct_creat_at
				, ct.cntrct_de
				, IF(ct.progrs_sttus_code = 'C' AND ct.update_dtm >= '{0} 23:59:59', 'P', ct.progrs_sttus_code) AS progrs_sttus_code
				, ct.spt_chrg_sn
				, ct.spt_nm
				, ct.cntrwk_bgnde
				, ct.cntrwk_endde
				, co.cntrct_sn
				, co.cntrct_execut_code
				, CASE WHEN co.cntrct_execut_code = 'C' THEN '0'
				ELSE co.ct_se_code
				END AS ct_se_code
				, co.purchsofc_sn
				, CASE WHEN co.cntrct_execut_code = 'C' AND co.ct_se_code NOT IN ('9') THEN IFNULL(co.qy*co.salamt, 0)
				WHEN co.cntrct_execut_code = 'C' AND co.ct_se_code IN ('9') THEN IFNULL(ROUND((co.puchas_amount*((100-co.dscnt_rt)/100))*co.qy * (co.fee_rt/100)), 0)
				WHEN co.cntrct_execut_code = 'A' THEN IFNULL(co.qy*co.salamt, 0)
				ELSE IFNULL(co.qy*co.puchas_amount, 0)
				END AS cntrct_amount
				FROM cost co
				JOIN contract ct
				ON co.cntrct_sn=ct.cntrct_sn
				LEFT OUTER JOIN member m
				ON ct.bsn_chrg_sn=m.mber_sn
				WHERE 1=1
				AND ct.cntrct_sn IN (SELECT c.cntrct_sn FROM contract c WHERE c.progrs_sttus_code <> 'C' OR (c.progrs_sttus_code = 'C' AND c.update_dtm BETWEEN '{2} 00:00:00' AND '{3} 23:59:59'))
				AND co.cost_date <= '{1}'
				AND co.cntrct_execut_code NOT IN ('B', 'D')
				AND co.ct_se_code NOT IN ('10')
				AND ((co.ct_se_code IN ('61','62', '63','7', '8') AND co.cntrct_execut_code = 'C') OR co.ct_se_code NOT IN ('61','62', '63','7', '8'))
				AND ct.prjct_ty_code = 'NR'
				AND m.dept_code NOT IN ('MA')
				AND ct.cntrct_de < '{1}' """.format(first_day, last_day, first_year, last_year)
    if 's_cntrct_execut_code' in params and params['s_cntrct_execut_code']:
        query += " AND co.cntrct_execut_code = %(s_cntrct_execut_code)s "

    query += """ ) t
				GROUP BY bsn_dept_code, cntrct_bcnc_sn, spt_chrg_sn, spt_nm, cntrct_sn, cntrct_execut_code, ct_se_code, purchsofc_sn
				ORDER BY bsn_dept_code, cntrct_bcnc_sn, ofcps_code, spt_chrg_sn, spt_nm, cntrct_sn, cntrct_execut_code, ct_se_code, purchsofc_sn """

    g.curs.execute(query, params)
    result = g.curs.fetchall()
    return result

def get_partner_contract_status(params):
    ymd = params['s_pxcond_mt']
    y, m = ymd.split("-")
    _, l = calendar.monthrange(int(y), int(m))
    f = 1
    first_year = "{}-01-01".format(y.zfill(4))
    last_year = "{}-12-31".format(y.zfill(4))
    query = """SELECT t.bsn_dept_code
				, (SELECT code_nm FROM code WHERE ctmmny_sn='1' AND parnts_code='DEPT_CODE' AND code=t.bsn_dept_code) AS bsn_dept_nm
				, t.purchsofc_sn
				, (SELECT bcnc_nm FROM bcnc WHERE bcnc_sn=t.purchsofc_sn) AS cntrct_bcnc_nm
				, SUM(t.cntrct_amount) AS cntrct_amount
				, SUM(t.complete_amount) AS complete_amount
				, SUM(t.y_complete_amount) AS y_complete_amount
				, SUM(t.excut_amount) AS excut_amount
				FROM (
				SELECT t.prjct_ty_code
				, t.purchsofc_sn
				, t.bsn_dept_code
				, t.cntrct_bcnc_sn
				, SUM(t.cntrct_amount) AS cntrct_amount
				, CASE WHEN ct_se_code IN ('1','2','4') THEN GET_ACCOUNT_COMPLETE_AMOUNT(t.cntrct_sn, t.purchsofc_sn, 'P', %(s_pxcond_mt)s)
				WHEN ct_se_code IN ('3') THEN GET_ACCOUNT_COMPLETE_AMOUNT(t.cntrct_sn, t.purchsofc_sn, 'S', %(s_pxcond_mt)s)
				ELSE GET_TAXBIL_COMPLETE_AMOUNT(t.cntrct_sn, t.purchsofc_sn, t.cntrct_execut_code, %(s_pxcond_mt)s)
				END AS complete_amount
				, CASE WHEN ct_se_code IN ('1','2','4') THEN GET_ACCOUNT_COMPLETE_AMOUNT3(t.cntrct_sn, t.purchsofc_sn, 'P', %(s_pxcond_mt)s)
				WHEN ct_se_code IN ('3') THEN GET_ACCOUNT_COMPLETE_AMOUNT3(t.cntrct_sn, t.purchsofc_sn, 'S', %(s_pxcond_mt)s)
				ELSE GET_TAXBIL_COMPLETE_AMOUNT3(t.cntrct_sn, t.purchsofc_sn, t.cntrct_execut_code, %(s_pxcond_mt)s)
				END AS y_complete_amount
				, CASE WHEN ct_se_code IN ('1','2','4') THEN GET_ACCOUNT_EXCUT_AMOUNT(t.cntrct_sn, t.purchsofc_sn, 'P', %(s_pxcond_mt)s)
				WHEN ct_se_code IN ('3') THEN GET_ACCOUNT_EXCUT_AMOUNT(t.cntrct_sn, t.purchsofc_sn, 'S', %(s_pxcond_mt)s)
				ELSE GET_TAXBIL_EXCUT_AMOUNT(t.cntrct_sn, t.purchsofc_sn, t.cntrct_execut_code, %(s_pxcond_mt)s)
				END AS excut_amount
				FROM (
				SELECT ct.prjct_ty_code
				, m.dept_code AS bsn_dept_code
				, co.purchsofc_sn AS cntrct_bcnc_sn
				, ct.bsn_chrg_sn
				, ct.spt_chrg_sn
				, ct.spt_nm
				, ct.cntrwk_bgnde
				, ct.cntrwk_endde
				, co.cntrct_sn
				, co.cntrct_execut_code
				, CASE WHEN co.cntrct_execut_code = 'C' THEN '0'
				ELSE co.ct_se_code
				END AS ct_se_code
				, co.purchsofc_sn
				, CASE WHEN co.cntrct_execut_code = 'C' AND co.ct_se_code NOT IN ('9') THEN IFNULL(co.qy*co.salamt, 0)
				WHEN co.cntrct_execut_code = 'C' AND co.ct_se_code IN ('9') THEN IFNULL(ROUND((co.puchas_amount*((100-co.dscnt_rt)/100))*co.qy * (co.fee_rt/100)), 0)
				WHEN co.cntrct_execut_code = 'A' THEN IFNULL(co.qy*co.salamt, 0)
				ELSE IFNULL(co.qy*co.puchas_amount, 0)
				END AS cntrct_amount
				FROM cost co
				JOIN contract ct
				ON co.cntrct_sn=ct.cntrct_sn
				LEFT OUTER JOIN member m
				ON ct.bsn_chrg_sn=m.mber_sn
				WHERE ct.cntrct_sn IS NOT NULL
				AND co.ct_se_code NOT IN ('61','62','7','10')
				AND ct.prjct_ty_code = 'NR'
				AND co.cntrct_execut_code = 'C'
				AND m.dept_code NOT IN ('MA')
				AND ct.cntrct_sn IN (SELECT cntrct_sn FROM contract WHERE progrs_sttus_code <> 'C' OR (progrs_sttus_code = 'C' AND update_dtm BETWEEN '{0} 00:00:00' AND '{1} 23:59:59'))
				) t
				GROUP BY bsn_dept_code, bsn_chrg_sn, purchsofc_sn, spt_chrg_sn, spt_nm, cntrct_sn, cntrct_execut_code, ct_se_code, purchsofc_sn
				) t
				GROUP BY bsn_dept_code, purchsofc_sn
				ORDER BY bsn_dept_code, cntrct_amount DESC, purchsofc_sn """.format(first_year, last_year)
    g.curs.execute(query, params)
    result = g.curs.fetchall()
    return result

def get_partner_status_list(params):
    ymd = params['s_pxcond_mt']
    y, m = ymd.split("-")
    _, l = calendar.monthrange(int(y), int(m))
    f = 1
    first_year = "{}-01-01".format(y.zfill(4))
    last_year = "{}-12-31".format(y.zfill(4))
    query = """SELECT t.ct_se_code
				, (SELECT code_nm FROM code WHERE ctmmny_sn=1 AND parnts_code='CT_SE_CODE' AND code=t.ct_se_code) AS ct_se_nm
				, t.purchsofc_sn
				, (SELECT bcnc_nm FROM bcnc WHERE bcnc_sn=t.purchsofc_sn) AS purchsofc_nm
				, SUM(t.cntrct_amount) AS cntrct_amount
				, SUM(t.complete_amount) AS complete_amount
				, SUM(t.y_complete_amount) AS y_complete_amount
				, SUM(t.excut_amount) AS excut_amount
				, SUM(t.spt_cnt) AS spt_cnt
				FROM (
				SELECT t.ct_se_code
				, t.purchsofc_sn
				, SUM(t.cntrct_amount) AS cntrct_amount
				, CASE WHEN ct_se_code IN ('1','2','4') THEN GET_ACCOUNT_COMPLETE_AMOUNT(t.cntrct_sn, t.purchsofc_sn, 'P', %(s_pxcond_mt)s)
				WHEN ct_se_code IN ('3') THEN GET_ACCOUNT_COMPLETE_AMOUNT(t.cntrct_sn, t.purchsofc_sn, 'S', %(s_pxcond_mt)s)
				ELSE GET_TAXBIL_COMPLETE_AMOUNT(t.cntrct_sn, t.purchsofc_sn, t.cntrct_execut_code, %(s_pxcond_mt)s)
				END AS complete_amount
				, CASE WHEN ct_se_code IN ('1','2','4') THEN GET_ACCOUNT_COMPLETE_AMOUNT3(t.cntrct_sn, t.purchsofc_sn, 'P', %(s_pxcond_mt)s)
				WHEN ct_se_code IN ('3') THEN GET_ACCOUNT_COMPLETE_AMOUNT3(t.cntrct_sn, t.purchsofc_sn, 'S', %(s_pxcond_mt)s)
				ELSE GET_TAXBIL_COMPLETE_AMOUNT3(t.cntrct_sn, t.purchsofc_sn, t.cntrct_execut_code, %(s_pxcond_mt)s)
				END AS y_complete_amount
				, CASE WHEN ct_se_code IN ('1','2','4') THEN GET_ACCOUNT_EXCUT_AMOUNT(t.cntrct_sn, t.purchsofc_sn, 'P', %(s_pxcond_mt)s)
				WHEN ct_se_code IN ('3') THEN GET_ACCOUNT_EXCUT_AMOUNT(t.cntrct_sn, t.purchsofc_sn, 'S', %(s_pxcond_mt)s)
				ELSE GET_TAXBIL_EXCUT_AMOUNT(t.cntrct_sn, t.purchsofc_sn, t.cntrct_execut_code, %(s_pxcond_mt)s)
				END AS excut_amount
				, COUNT(DISTINCT t.cntrct_sn) AS spt_cnt
				FROM (
				SELECT ct.prjct_ty_code
				, m.dept_code AS bsn_dept_code
				, ct.bcnc_sn AS cntrct_bcnc_sn
				, ct.bsn_chrg_sn
				, ct.spt_chrg_sn
				, ct.spt_nm
				, ct.cntrwk_bgnde
				, ct.cntrwk_endde
				, co.cntrct_sn
				, co.cntrct_execut_code
				, CASE WHEN co.cntrct_execut_code = 'C' THEN '0'
				ELSE co.ct_se_code
				END AS ct_se_code
				, co.purchsofc_sn
				, CASE WHEN co.cntrct_execut_code = 'C' AND co.ct_se_code NOT IN ('9') THEN IFNULL(co.qy*co.salamt, 0)
				WHEN co.cntrct_execut_code = 'C' AND co.ct_se_code IN ('9') THEN IFNULL(ROUND((co.puchas_amount*((100-co.dscnt_rt)/100))*co.qy * (co.fee_rt/100)), 0)
				WHEN co.cntrct_execut_code = 'A' THEN IFNULL(co.qy*co.salamt, 0)
				ELSE IFNULL(co.qy*co.puchas_amount, 0)
				END AS cntrct_amount
				FROM cost co
				JOIN contract ct
				ON co.cntrct_sn=ct.cntrct_sn
				LEFT OUTER JOIN member m
				ON ct.bsn_chrg_sn=m.mber_sn
				WHERE ct.cntrct_sn IS NOT NULL
				AND co.ct_se_code NOT IN ('61','62','7','10')
				AND ct.prjct_ty_code = 'NR'
				AND co.cntrct_execut_code = 'E'
				AND ((co.ct_se_code IN ('8') AND co.cntrct_execut_code = 'C') OR co.ct_se_code NOT IN ('8'))
				AND ct.cntrct_sn IN (SELECT cntrct_sn FROM contract WHERE progrs_sttus_code <> 'C' OR (progrs_sttus_code = 'C' AND update_dtm BETWEEN '{0} 00:00:00' AND '{1} 23:59:59'))
				) t
				GROUP BY bsn_dept_code, bsn_chrg_sn, cntrct_bcnc_sn, spt_chrg_sn, spt_nm, cntrct_sn, cntrct_execut_code, ct_se_code, purchsofc_sn
				) t
				GROUP BY ct_se_code, purchsofc_sn
				ORDER BY cntrct_amount DESC, CAST(ct_se_code AS INT), purchsofc_sn """.format(first_year, last_year)

    g.curs.execute(query, params)
    result = g.curs.fetchall()
    return result