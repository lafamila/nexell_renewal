from flask import session, jsonify, g
import onetimepass as otp
import random
import string
import urllib
import datetime
from pytz import timezone
from app.helpers.class_helper import Map
from app.helpers.datatable_helper import dt_query
from collections import OrderedDict
import itertools
import calendar
from .project_service import get_project_by_cntrct_nm, get_contract
from dateutil.relativedelta import relativedelta
def get_completed_summary(params):
    year = int(params['s_pxcond_mt'].split("-")[0])
    month = int(params['s_pxcond_mt'].split("-")[1])
    query = """SELECT t.amt_ty_code AS amt_ty_code
				, (SELECT code_nm FROM code WHERE ctmmny_sn=1 AND parnts_code='AMT_TY_CODE' AND code=t.amt_ty_code) AS amt_ty_nm
				, t.dept_code
				, IF(dept_code='ETC', '기타', (SELECT code_nm FROM code WHERE ctmmny_sn=1 AND parnts_code='DEPT_CODE' AND code=t.dept_code)) AS dept_nm
				, SUM(IFNULL(m_contract_amount, 0)) AS m_contract_amount
				, SUM(IFNULL(y_contract_amount, 0)) AS y_contract_amount
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
    if year >= 2024:
        query += """, (SELECT COUNT(code) FROM code WHERE ctmmny_sn=1 AND parnts_code='DEPT_CODE' AND (code LIKE 'TS%%' OR code LIKE 'BI%%' OR code = 'NE' OR code IN ('ST', 'EL', 'CT', 'MA'))) - (SELECT COUNT(code) FROM code WHERE ctmmny_sn=1 AND parnts_code='DEPT_CODE' AND code IN ('EL', 'CT', 'MA')) + 1 AS dept_count"""
    elif year >= 2023:
        query += """, (SELECT COUNT(code) FROM code WHERE ctmmny_sn=1 AND parnts_code='DEPT_CODE' AND (code LIKE 'TS%%' OR code LIKE 'BI%%' OR code IN ('ST', 'EL', 'CT', 'MA'))) - (SELECT COUNT(code) FROM code WHERE ctmmny_sn=1 AND parnts_code='DEPT_CODE' AND code IN ('EL', 'CT', 'MA')) + 1 AS dept_count"""
    else:
        query += """, (SELECT COUNT(code) FROM code WHERE ctmmny_sn=1 AND parnts_code='DEPT_CODE' AND (code LIKE 'TS%%' OR code LIKE 'BI%%')) AS dept_count"""

    query += """
                , IF(dept_code='ETC', 99, (SELECT code_ordr FROM code WHERE ctmmny_sn=1 AND parnts_code='DEPT_CODE' AND code=t.dept_code )) AS dept_order
				FROM (
				SELECT z.amt_ty_code
				, IF(m.dept_code IN ('EL','CT', 'MA'), 'ETC', m.dept_code) AS dept_code
				, CASE WHEN z.amt_ty_code = '2' THEN GET_SUJU_AMOUNT({0}, z.mber_sn, 'M')
				WHEN z.amt_ty_code = '3' THEN GET_PXCOND_MONTH_AMOUNT('C', {0}, z.mber_sn)
				WHEN z.amt_ty_code = '5' THEN GET_VA_MONTH_AMOUNT({1}, z.mber_sn)
				END AS m_contract_amount
				, CASE WHEN z.amt_ty_code = '2' THEN GET_SUJU_AMOUNT({0}, z.mber_sn, 'A')
				WHEN z.amt_ty_code = '3' THEN GET_PXCOND_TOTAL_AMOUNT('C', {1}, z.mber_sn)
				WHEN z.amt_ty_code = '5' THEN GET_VA_TOTAL_AMOUNT({1}, z.mber_sn)
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
				, IFNULL(g.stdyy, '{2}') AS stdyy
				FROM member m
				LEFT OUTER JOIN (SELECT x.amt_ty_code, y.mber_sn FROM (SELECT code AS amt_ty_code FROM `code` WHERE parnts_code='AMT_TY_CODE' AND USE_AT='Y') x LEFT OUTER JOIN member y ON y.mber_sn=y.mber_sn) z
				ON m.mber_sn=z.mber_sn
				LEFT OUTER JOIN (SELECT stdyy, amt_ty_code, mber_sn, SUM(IFNULL(1m, 0)) AS 1m, SUM(IFNULL(2m, 0)) AS 2m, SUM(IFNULL(3m, 0)) AS 3m, SUM(IFNULL(4m, 0)) AS 4m, SUM(IFNULL(5m, 0)) AS 5m, SUM(IFNULL(6m, 0)) AS 6m, SUM(IFNULL(7m, 0)) AS 7m, SUM(IFNULL(8m, 0)) AS 8m, SUM(IFNULL(9m, 0)) AS 9m, SUM(IFNULL(10m, 0)) AS 10m, SUM(IFNULL(11m, 0)) AS 11m, SUM(IFNULL(12m, 0)) AS 12m FROM goal WHERE stdyy = SUBSTRING({0}, 1, 4) AND amt_ty_code IN ('2','3','5', '8', '9') GROUP BY mber_sn, amt_ty_code, stdyy) g
				ON m.mber_sn=g.mber_sn AND g.amt_ty_code=z.amt_ty_code
				WHERE 1=1				
				"""
    if year >= 2024:
        query += """ AND (m.dept_code LIKE 'TS%%' OR m.dept_code LIKE 'BI%%' OR m.dept_code = 'NE' OR m.dept_code IN ('ST'))"""
    elif year >= 2023:
        query += """ AND (m.dept_code LIKE 'TS%%' OR m.dept_code LIKE 'BI%%' OR m.dept_code IN ('ST', 'EL', 'CT', 'MA'))"""
    else:
        query += """ AND (m.dept_code LIKE 'TS%%' OR m.dept_code LIKE 'BI%%')"""

    query += """
                ORDER BY g.amt_ty_code, m.dept_code
				) t
				GROUP BY t.amt_ty_code, t.dept_code
				ORDER BY t.amt_ty_code, dept_order, t.dept_code"""

    g.curs.execute(query.format("'{}'".format(params['s_pxcond_mt']), "'{}-{}'".format(str(year).zfill(4), str(month).zfill(2)), str(year).zfill(4)))
    result = g.curs.fetchall()

    g.curs.execute("SELECT parnts_code AS p, code AS v, code_nm AS nm, code_ordr AS ordr FROM code WHERE PARNTS_CODE IN ('AMT_TY_CODE', 'DEPT_CODE')")
    codes = g.curs.fetchall()
    code_nms = {(c["p"], c["v"]) : (c["nm"], c["ordr"]) for c in codes}
    code_nms[('DEPT_CODE', 'ETC')] = ("기타", 999)
    dept_codes = ['TS1', 'TS2', 'TS3', 'BI']
    amt_ty_codes = ['2', '3', '5']
    if year >= 2024:
        dept_codes = ['ST', 'TS1', 'TS2', 'BI', 'NE']
    elif year >= 2023:
        dept_codes = ['ST', 'TS1', 'TS2', 'BI', 'ETC']

    tables = {(r['amt_ty_code'], r['dept_code']) : r for r in result}
    table_result = []
    for amt_ty_code, dept_code in itertools.product(amt_ty_codes, dept_codes):
        if "purpose" in params:
            if amt_ty_code in ('3', '5') and dept_code == 'ST':
                continue
        if (amt_ty_code, dept_code) not in tables:
            table_result.append(new_row(amt_ty_code, code_nms[("AMT_TY_CODE", amt_ty_code)][0], dept_code, code_nms[("DEPT_CODE", dept_code)][0], code_nms[("DEPT_CODE", dept_code)][1]))
        else:
            table_result.append(tables[(amt_ty_code, dept_code)])

    if "purpose" in params:
        for r in table_result:
            if r['amt_ty_code'] == '2':
                r['dept_count'] = len(dept_codes)
            else:
                r['dept_count'] = len([dept for dept in dept_codes if dept != 'ST'])
    else:
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
				, SUM(IFNULL(1m,0)) AS m1
				, SUM(IFNULL(2m,0)) AS m2
				, SUM(IFNULL(3m,0)) AS m3
				, SUM(IFNULL(4m,0)) AS m4
				, SUM(IFNULL(5m,0)) AS m5
				, SUM(IFNULL(6m,0)) AS m6
				, SUM(IFNULL(7m,0)) AS m7
				, SUM(IFNULL(8m,0)) AS m8
				, SUM(IFNULL(9m,0)) AS m9
				, SUM(IFNULL(10m,0)) AS m10
				, SUM(IFNULL(11m,0)) AS m11
				, SUM(IFNULL(12m,0)) AS m12
				, (SELECT COUNT(code) FROM code WHERE ctmmny_sn=1 AND parnts_code='DEPT_CODE' AND code IN ('TS1', 'TS2')) AS dept_count
				FROM (
				SELECT z.amt_ty_code
				, m.dept_code
				, CASE WHEN z.amt_ty_code = '2' THEN GET_SUJU_AMOUNT(%(s_pxcond_mt)s, z.mber_sn, 'M')
				WHEN z.amt_ty_code = '3' THEN GET_PXCOND_MONTH_AMOUNT('C', %(s_pxcond_mt)s, z.mber_sn)
				WHEN z.amt_ty_code = '5' THEN GET_VA_MONTH_AMOUNT(%(s_pxcond_mt)s, z.mber_sn)
				END AS m_contract_amount
				, CASE WHEN g.amt_ty_code = '2' THEN GET_SUJU_AMOUNT(%(s_pxcond_mt)s, z.mber_sn, 'A')
				WHEN z.amt_ty_code = '3' THEN GET_PXCOND_TOTAL_AMOUNT('C', %(s_pxcond_mt)s, z.mber_sn)
				WHEN z.amt_ty_code = '5' THEN GET_VA_TOTAL_AMOUNT(%(s_pxcond_mt)s, z.mber_sn)
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
				FROM member m
				LEFT OUTER JOIN (SELECT x.amt_ty_code, y.mber_sn FROM (SELECT code AS amt_ty_code FROM `code` WHERE parnts_code='AMT_TY_CODE' AND USE_AT='Y') x LEFT OUTER JOIN member y ON y.mber_sn=y.mber_sn) z
				ON m.mber_sn=z.mber_sn
				LEFT OUTER JOIN (SELECT stdyy, amt_ty_code, mber_sn, SUM(IFNULL(1m, 0)) AS 1m, SUM(IFNULL(2m, 0)) AS 2m, SUM(IFNULL(3m, 0)) AS 3m, SUM(IFNULL(4m, 0)) AS 4m, SUM(IFNULL(5m, 0)) AS 5m, SUM(IFNULL(6m, 0)) AS 6m, SUM(IFNULL(7m, 0)) AS 7m, SUM(IFNULL(8m, 0)) AS 8m, SUM(IFNULL(9m, 0)) AS 9m, SUM(IFNULL(10m, 0)) AS 10m, SUM(IFNULL(11m, 0)) AS 11m, SUM(IFNULL(12m, 0)) AS 12m FROM goal WHERE stdyy = SUBSTRING(%(s_pxcond_mt)s, 1, 4) AND amt_ty_code IN ('2','3','5', '8', '9') GROUP BY mber_sn, amt_ty_code, stdyy) g
				ON m.mber_sn=g.mber_sn AND g.amt_ty_code=z.amt_ty_code
				WHERE 1=1
				AND z.amt_ty_code IN ('2','3','5','6')
				AND m.dept_code IN ('TS1', 'TS2')
				ORDER BY z.amt_ty_code, m.dept_code
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
				ORDER BY bsn_dept_code""".format(first_year, last_year, last_day)
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
    query = """SELECT t.prjct_ty_code AS prjct_ty_code
				, t.prjct_creat_at AS prjct_creat_at
				, t.bsn_dept_code AS bsn_dept_code
				, (SELECT code_nm FROM code WHERE ctmmny_sn='1' AND parnts_code='DEPT_CODE' AND code=t.bsn_dept_code) AS bsn_dept_nm
				, t.bsn_chrg_sn AS bsn_chrg_sn
				, GET_MEMBER_NAME(t.bsn_chrg_sn, 'M') AS bsn_chrg_nm
				, t.cntrct_bcnc_sn AS cntrct_bcnc_sn
				, (SELECT bcnc_nm FROM bcnc WHERE bcnc_sn=t.cntrct_bcnc_sn) AS cntrct_bcnc_nm
				, t.spt_chrg_sn AS spt_chrg_sn
				, GET_MEMBER_NAME(t.spt_chrg_sn, 'M') AS spt_chrg_nm
				, t.spt_nm AS spt_nm
				, t.cntrwk_bgnde AS cntrwk_bgnde
				, t.cntrwk_endde AS cntrwk_endde
				, t.cntrct_de AS cntrct_de
				, t.progrs_sttus_code AS progrs_sttus_code
				, t.cntrct_sn AS cntrct_sn
				, t.prjct_sn AS prjct_sn
				, t.cntrct_execut_code AS cntrct_execut_code
				, (SELECT code_nm FROM code WHERE ctmmny_sn='1' AND parnts_code='CNTRCT_EXECUT_CODE' AND code=t.cntrct_execut_code) AS cntrct_execut_nm
				, t.ct_se_code AS ct_se_code
				, (SELECT code_nm FROM code WHERE ctmmny_sn='1' AND parnts_code='CT_SE_CODE' AND code=t.ct_se_code) AS ct_se_nm
				, t.purchsofc_sn AS purchsofc_sn
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
				, (SELECT rm FROM pxcond WHERE cntrct_sn=t.cntrct_sn AND cntrct_execut_code=t.cntrct_execut_code AND bcnc_sn=t.purchsofc_sn AND pxcond_mt='{0}' ORDER BY pxcond_mt DESC LIMIT 1) AS rm
				, (SELECT ofcps_code FROM member WHERE mber_sn=t.spt_chrg_sn) AS ofcps_code
				FROM 
				(SELECT
				  tx.prjct_ty_code
				  , tx.bsn_dept_code
				  , tx.cntrct_bcnc_sn
				  , tx.bsn_chrg_sn
				  , tx.prjct_creat_at
				  , tx.cntrct_de
				  , tx.progrs_sttus_code
				  , tx.spt_chrg_sn
				  , tx.spt_nm
				  , tx.cntrwk_bgnde
				  , tx.cntrwk_endde
				  , tx.cntrct_sn
				  , tx.prjct_sn
				  , tx.cntrct_execut_code
				  , tx.ct_se_code
				  , tx.purchsofc_sn
				  , SUM(tx.cntrct_amount) AS cntrct_amount
				  FROM
                    (
                        SELECT distinct ct.prjct_ty_code
                        , mm.dept_code AS bsn_dept_code
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
                        , p.prjct_sn
                        , 'E' AS CNTRCT_EXECUT_CODE
                        , '4' AS ct_se_code
                        , 355 AS PURCHSOFC_SN
                        , 0 AS cntrct_amount
                        FROM (SELECT x.* FROM cost x INNER JOIN (SELECT cntrct_sn, MAX(extra_sn) AS m_extra_sn FROM cost WHERE 1=1 GROUP BY cntrct_sn) y ON x.cntrct_sn=y.cntrct_sn AND x.extra_sn=y.m_extra_sn AND x.purchsofc_sn IS NOT NULL) co
                        JOIN contract ct
                        ON co.cntrct_sn=ct.cntrct_sn
                        LEFT OUTER JOIN member m
                        ON ct.bsn_chrg_sn=m.mber_sn
                        LEFT OUTER JOIN member mm
                        ON ct.spt_chrg_sn=mm.mber_sn
                        LEFT OUTER JOIN project p
                        ON ct.cntrct_sn=p.cntrct_sn
                        WHERE {4}
                        AND {5}
                        AND ct.cntrct_sn IN (SELECT c.cntrct_sn FROM contract c WHERE c.progrs_sttus_code <> 'C' OR (c.progrs_sttus_code = 'C' AND c.update_dtm BETWEEN '{2} 00:00:00' AND '{3} 23:59:59'))
                        AND ((co.ct_se_code IN ('61','62', '63','7') AND co.cntrct_execut_code = 'C') OR co.ct_se_code NOT IN ('61','62', '63','7')) 
                        AND (co.cost_date <= '{1}' or co.cost_date IS NULL)
                        AND co.cntrct_execut_code NOT IN ('B', 'D')
                        AND co.purchsofc_sn NOT IN ('691')
                        AND ct.prjct_ty_code = 'NR'
                        AND (ct.progrs_sttus_code = 'P' OR (ct.progrs_sttus_code = 'C' AND ct.update_dtm >= '{0} 23:59:59'))
                        AND mm.dept_code IN ('TS1', 'TS2')
                        AND ct.cntrct_de < '{1}' 				
                        UNION
                        SELECT distinct ct.prjct_ty_code
                        , mm.dept_code AS bsn_dept_code
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
                        , p.prjct_sn
                        , 'E' AS CNTRCT_EXECUT_CODE
                        , '5' AS ct_se_code
                        , 146 AS PURCHSOFC_SN
                        , CASE WHEN co.cntrct_execut_code = 'C' AND co.ct_se_code NOT IN ('9') THEN IFNULL(co.qy*co.salamt, 0)
                        WHEN co.cntrct_execut_code = 'C' AND co.ct_se_code IN ('9') THEN IFNULL(ROUND((co.puchas_amount*((100-co.dscnt_rt)/100))*co.qy * (co.fee_rt/100)), 0)
                        WHEN co.cntrct_execut_code = 'A' THEN IFNULL(co.qy*co.salamt, 0)
                        ELSE IFNULL(co.qy*co.puchas_amount, 0)
                        END AS cntrct_amount
                        FROM (SELECT x.* FROM cost x INNER JOIN (SELECT cntrct_sn, MAX(extra_sn) AS m_extra_sn FROM cost WHERE 1=1 GROUP BY cntrct_sn) y ON x.cntrct_sn=y.cntrct_sn AND x.extra_sn=y.m_extra_sn AND x.purchsofc_sn IS NOT NULL) co
                        JOIN contract ct
                        ON co.cntrct_sn=ct.cntrct_sn
                        LEFT OUTER JOIN member m
                        ON ct.bsn_chrg_sn=m.mber_sn
                        LEFT OUTER JOIN member mm
                        ON ct.spt_chrg_sn=mm.mber_sn
                        LEFT OUTER JOIN project p
                        ON ct.cntrct_sn=p.cntrct_sn
                        WHERE {4}
                        AND {5}
                        AND ct.cntrct_sn IN (SELECT c.cntrct_sn FROM contract c WHERE c.progrs_sttus_code <> 'C' OR (c.progrs_sttus_code = 'C' AND c.update_dtm BETWEEN '{2} 00:00:00' AND '{3} 23:59:59'))
                        AND ((co.ct_se_code IN ('61','62', '63','7') AND co.cntrct_execut_code = 'C') OR co.ct_se_code NOT IN ('61','62', '63','7')) 
                        AND (co.cost_date <= '{1}' or co.cost_date IS NULL)
                        AND co.cntrct_execut_code NOT IN ('B', 'D')
                        AND co.purchsofc_sn NOT IN ('691')
                        AND ct.prjct_ty_code = 'NR'
                        AND (ct.progrs_sttus_code = 'P' OR (ct.progrs_sttus_code = 'C' AND ct.update_dtm >= '{0} 23:59:59'))
                        AND mm.dept_code IN ('TS1', 'TS2')
                        AND ct.cntrct_de < '{1}' 
                        UNION
                        SELECT ct.prjct_ty_code
                        , mm.dept_code AS bsn_dept_code
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
                        , p.prjct_sn
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
                        FROM (SELECT x.* FROM cost x INNER JOIN (SELECT cntrct_sn, MAX(extra_sn) AS m_extra_sn FROM cost WHERE 1=1 GROUP BY cntrct_sn) y ON x.cntrct_sn=y.cntrct_sn AND x.extra_sn=y.m_extra_sn AND x.purchsofc_sn IS NOT NULL) co
                        JOIN contract ct
                        ON co.cntrct_sn=ct.cntrct_sn
                        LEFT OUTER JOIN member m
                        ON ct.bsn_chrg_sn=m.mber_sn
                        LEFT OUTER JOIN member mm
                        ON ct.spt_chrg_sn=mm.mber_sn
                        LEFT OUTER JOIN project p
                        ON ct.cntrct_sn=p.cntrct_sn
                        WHERE {4}
                        AND {5}
                        AND ct.cntrct_sn IN (SELECT c.cntrct_sn FROM contract c WHERE c.progrs_sttus_code <> 'C' OR (c.progrs_sttus_code = 'C' AND c.update_dtm BETWEEN '{2} 00:00:00' AND '{3} 23:59:59'))
                        AND ((co.ct_se_code IN ('61','62', '63','7') AND co.cntrct_execut_code = 'C') OR co.ct_se_code NOT IN ('61','62', '63','7')) 
                        AND (co.cost_date <= '{1}' or co.cost_date IS NULL)
                        AND co.cntrct_execut_code NOT IN ('B', 'D')
                        AND co.purchsofc_sn NOT IN ('691')
                        AND ct.prjct_ty_code = 'NR'
                        AND (ct.progrs_sttus_code = 'P' OR (ct.progrs_sttus_code = 'C' AND ct.update_dtm >= '{0} 23:59:59'))
                        AND mm.dept_code IN ('TS1', 'TS2')
                        AND ct.cntrct_de < '{1}'
                    ) tx
                    GROUP BY 
                    prjct_ty_code, cntrct_sn, prjct_sn, cntrct_execut_code, ct_se_code, purchsofc_sn
                    """.format(first_day, last_day, first_year, last_year, "co.cntrct_execut_code = %(s_cntrct_execut_code)s " if 's_cntrct_execut_code' in params and params['s_cntrct_execut_code'] else " 1=1 ", " co.ct_se_code NOT IN ('10')" if "purpose" in params else " co.ct_se_code NOT IN ('10', '8')")

    query += """ ) t
				GROUP BY bsn_dept_code, cntrct_bcnc_sn, spt_chrg_sn, spt_nm, cntrct_sn, cntrct_execut_code, ct_se_code, purchsofc_sn
				ORDER BY bsn_dept_code, spt_chrg_nm,  cntrct_bcnc_nm, spt_nm, cntrct_sn, cntrct_bcnc_sn, cntrct_execut_code, ct_se_code, purchsofc_sn """

    print(query)
    g.curs.execute(query, params)
    result = g.curs.fetchall()
    return result


def get_s1(cntrct_sn, pxcond_ym):
    p_total = 0
    pxcond_st = pxcond_ym+"-01"
    pxcond_ed = pxcond_ym+"-31"
    query = """SELECT IFNULL(SUM(s.dlnt * p.dlamt), 0) AS p_total
    				FROM account s
    				LEFT JOIN account p
    				ON s.ctmmny_sn=p.ctmmny_sn AND s.cntrct_sn=p.cntrct_sn AND s.prjct_sn=p.prjct_sn AND s.cnnc_sn=p.delng_sn
    				WHERE s.ctmmny_sn = 1
    				AND s.cntrct_sn = %s
    				AND s.delng_se_code = 'S'
    				AND p.delng_ty_code IN ('1')
    				AND s.delng_ty_code <> 14
    				AND s.dlivy_de BETWEEN %s AND %s
    """
    g.curs.execute(query, (cntrct_sn, pxcond_st, pxcond_ed))
    result = g.curs.fetchone()
    if result:
        print(result)
        p_total += result['p_total'] if 'p_total' in result else 0
    query = """SELECT IFNULL(SUM(a.dlnt * ac.dlamt), 0) AS p_total
    				FROM account a
    				LEFT JOIN account ac
    				ON a.ctmmny_sn=ac.ctmmny_sn AND a.cntrct_sn=ac.cntrct_sn AND a.prjct_sn=ac.prjct_sn AND a.cnnc_sn=ac.delng_sn
    				WHERE a.ctmmny_sn = 1
    				AND a.cntrct_sn = %s
    				AND a.delng_se_code = 'S'
    				AND ac.delng_ty_code = '2'
    				AND a.delng_ty_code <> 14
    				AND a.dlivy_de BETWEEN %s AND %s
    """
    g.curs.execute(query, (cntrct_sn, pxcond_st, pxcond_ed))
    result = g.curs.fetchone()
    if result:
        p_total += result['p_total'] if 'p_total' in result else 0

    query = """SELECT IFNULL(SUM(a.dlnt * a.dlamt),0) AS p_total
				FROM account a
				LEFT JOIN account ac
				ON a.ctmmny_sn=ac.ctmmny_sn AND a.cntrct_sn=ac.cntrct_sn AND a.prjct_sn=ac.prjct_sn AND a.cnnc_sn=ac.delng_sn
				WHERE a.ctmmny_sn = 1
				AND a.cntrct_sn = %s
				AND a.delng_se_code = 'S'
				AND ac.delng_ty_code = '3'
                AND a.dlivy_de BETWEEN %s AND %s

    """
    g.curs.execute(query, (cntrct_sn, pxcond_st, pxcond_ed))
    result = g.curs.fetchone()
    if result:
        p_total += result['p_total'] if 'p_total' in result else 0

    query = """SELECT IFNULL(SUM(a.dlnt * ac.dlamt),0) AS p_total
    				FROM account a
    				LEFT JOIN account ac
    				ON a.ctmmny_sn=ac.ctmmny_sn AND a.cntrct_sn=ac.cntrct_sn AND a.prjct_sn=ac.prjct_sn AND a.cnnc_sn=ac.delng_sn
    				WHERE a.ctmmny_sn = 1
    				AND a.cntrct_sn = %s
    				AND a.delng_se_code = 'S'
    				AND ac.delng_ty_code = '4'
                    AND a.dlivy_de BETWEEN %s AND %s
    """
    g.curs.execute(query, (cntrct_sn, pxcond_st, pxcond_ed))
    result = g.curs.fetchone()
    if result:
        p_total += result['p_total'] if 'p_total' in result else 0



    query = """SELECT IFNULL(SUM(t.splpc_am + IFNULL(t.vat, 0)),0) AS p_total
                FROM taxbil t
                WHERE t.ctmmny_sn = 1
                AND t.cntrct_sn = %s
                AND t.delng_se_code = 'P' 
                AND t.pblicte_trget_sn = 116 
                AND t.pblicte_de BETWEEN %s AND %s"""
    g.curs.execute(query, (cntrct_sn, pxcond_st, pxcond_ed))
    result = g.curs.fetchone()
    if result:
        p_total += result['p_total'] if 'p_total' in result else 0


    return p_total

def get_s2(cntrct_sn, pxcond_ym):
    p_total = 0
    pxcond_st = pxcond_ym+"-01"
    pxcond_ed = pxcond_ym+"-31"
    query = """SELECT o.cntrct_sn
    				, o.outsrc_fo_sn
    				FROM outsrc o
    				LEFT OUTER JOIN reserved r
    				ON o.outsrc_fo_sn=r.outsrc_fo_sn AND o.cntrct_sn=r.cntrct_sn
    				WHERE o.cntrct_sn = %s
    				AND o.outsrc_fo_sn NOT IN (116)
    """
    g.curs.execute(query, cntrct_sn)
    result = g.curs.fetchall()
    check_146 = False
    for i, r in enumerate(result):
        outsrc_fo_sn = r['outsrc_fo_sn']
        if int(outsrc_fo_sn) == 146:
            check_146 = True

        query = """SELECT IFNULL(SUM(t.splpc_am + IFNULL(t.vat,0)),0) AS p_total
				FROM taxbil t
				WHERE t.ctmmny_sn = 1
				AND t.cntrct_sn = %s
				AND t.delng_se_code = 'P' 
				AND t.pblicte_trget_sn = %s 
                AND t.pblicte_de BETWEEN %s AND %s"""
        g.curs.execute(query, (cntrct_sn, outsrc_fo_sn, pxcond_st, pxcond_ed))
        r = g.curs.fetchone()
        if r:
            p_total += r['p_total'] if 'p_total' in r else 0
    if not check_146:
        query = """SELECT IFNULL(SUM(t.splpc_am + IFNULL(t.vat,0)),0) AS p_total
        				FROM taxbil t
        				WHERE t.ctmmny_sn = 1
        				AND t.cntrct_sn = %s
        				AND t.delng_se_code = 'P' 
        				AND t.pblicte_trget_sn = 146
                        AND t.pblicte_de BETWEEN %s AND %s"""
        g.curs.execute(query, (cntrct_sn, pxcond_st, pxcond_ed))
        r = g.curs.fetchone()
        if r:
            p_total += r['p_total'] if 'p_total' in r else 0

    return p_total

def get_s(cntrct_sn):
    query = """SELECT IFNULL(s.amt, 0) AS s_sum
                FROM contract c
				LEFT OUTER JOIN (SELECT SUM(IFNULL(splpc_am, 0) + IFNULL(vat, 0)) AS amt, cntrct_sn FROM taxbil WHERE delng_se_code='S' GROUP BY cntrct_sn) s
				ON s.cntrct_sn=c.cntrct_sn
				WHERE c.cntrct_sn=%s
"""
    g.curs.execute(query, cntrct_sn)
    result = g.curs.fetchone()
    return result.get('s_sum', 0)

def get_completed_reportNR_new(params):
    CT_SE_CODE_ORDER = {0: 0, 1: 1, 2: 2, 5: 3, '': 4, 3: 5, 4: 6, 8: 7}
    ymd = params['s_pxcond_mt']
    y, m = ymd.split("-")
    _, l = calendar.monthrange(int(y), int(m))
    f = 1
    first_day = "{}-{}-{}".format(y.zfill(4), m.zfill(2), str(f).zfill(2))
    last_day = "{}-{}-{}".format(y.zfill(4), m.zfill(2), str(l).zfill(2))
    first_year = "{}-01-01".format(y.zfill(4))
    last_year = "{}-12-31".format(y.zfill(4))
    #ct_se_code, cntrct_amount, excut_amount, ofcps_code
    result = []
    query = """SELECT GET_MEMBER_NAME(mm.mber_sn, 'M') AS spt_chrg_nm
                    , GET_MEMBER_NAME(m.mber_sn, 'M') AS bsn_chrg_nm
                    , mm.dept_code AS spt_dept_code
                    , m.dept_code AS bsn_dept_code
                    , mm.mber_sn AS spt_chrg_sn
                    , m.mber_sn AS bsn_chrg_sn
                    , (SELECT code_nm FROM code WHERE parnts_code='DEPT_CODE' AND code=mm.dept_code) AS spt_dept_nm
                    , (SELECT code_nm FROM code WHERE parnts_code='DEPT_CODE' AND code=m.dept_code) AS bsn_dept_nm
                    , c.bcnc_sn AS cntrct_bcnc_sn
                    , (SELECT bcnc_nm FROM bcnc WHERE bcnc_sn=c.bcnc_sn) AS cntrct_bcnc_nm
                    , c.spt_nm AS spt_nm
                    , c.prjct_creat_at AS prjct_creat_at
                    , c.cntrwk_bgnde AS cntrwk_bgnde
                    , c.cntrwk_endde AS cntrwk_endde
                    , c.cntrct_de AS cntrct_de
                    , c.progrs_sttus_code AS progrs_sttus_code
                    , c.cntrct_sn AS cntrct_sn
                    , p.prjct_sn AS prjct_sn
                    , DATE_FORMAT(c.regist_dtm, '%%Y-%%m-%%d')
                    , (SELECT rate FROM pxcond WHERE cntrct_sn=c.cntrct_sn AND rate IS NOT NULL ORDER BY pxcond_mt DESC LIMIT 1) AS rate
                    
                 FROM contract c
                         LEFT OUTER JOIN member mm
                         ON c.spt_chrg_sn=mm.mber_sn                
                         LEFT OUTER JOIN member m
                         ON c.bsn_chrg_sn=m.mber_sn
                         LEFT OUTER JOIN project p 
                         ON c.cntrct_sn=p.cntrct_sn
                         WHERE 1=1
                         # AND (c.progrs_sttus_code <> 'C' OR (c.progrs_sttus_code = 'C' AND c.update_dtm BETWEEN '{2} 00:00:00' AND '{3} 23:59:59'))
                         AND p.prjct_sn IS NOT NULL
                         AND c.progrs_sttus_code = 'P'
                         AND c.prjct_ty_code = 'NR'
                         # AND (c.progrs_sttus_code = 'P' OR (c.progrs_sttus_code = 'C' AND c.update_dtm >= '{0} 23:59:59'))
                         AND mm.dept_code IN ('TS1', 'TS2')
                         AND c.cntrct_de < '{1}'
                         ORDER BY spt_dept_code, cntrct_bcnc_nm, DATE_FORMAT(c.regist_dtm, '%%Y-%%m-%%d') DESC, mm.ofcps_code, spt_chrg_nm, spt_nm, cntrct_sn, cntrct_bcnc_sn    
    """.format(first_day, last_day, first_year, last_year)

    g.curs.execute(query, params)
    data = g.curs.fetchall()
    for d in data:
        result_part = []
        d['s_pxcond_mt'] = params['s_pxcond_mt']
        bcncs = []
        query = """
                    SELECT IF(pa.bcnc_sn=3, IFNULL(SUM(IF(pa.ddt_man < CONCAT(SUBSTRING(%(s_pxcond_mt)s, 1, 7),'-01'), sa.dlnt*sa.dlamt, 0)), 0), IFNULL(SUM(IF(pa.ddt_man < CONCAT(SUBSTRING(%(s_pxcond_mt)s, 1, 7),'-01'), pa.dlnt*pa.dlamt, 0)), 0)) AS complete_amount
                         , IF(pa.bcnc_sn=3, IFNULL(SUM(IF(pa.ddt_man < CONCAT(SUBSTRING(%(s_pxcond_mt)s, 1, 7),'-01'), 0,sa.dlnt*sa.dlamt)), 0), IFNULL(SUM(IF(pa.ddt_man < CONCAT(SUBSTRING(%(s_pxcond_mt)s, 1, 7),'-01'), 0, pa.dlnt*pa.dlamt)), 0)) AS tax_amount                         
                         , 'E' AS cntrct_execut_code
                         , pa.bcnc_sn AS purchsofc_sn
                         , (SELECT bcnc_nm FROM bcnc WHERE bcnc_sn=pa.bcnc_sn) AS purchsofc_nm
                         , (SELECT rm FROM pxcond WHERE cntrct_sn=pa.cntrct_sn AND cntrct_execut_code='E' AND bcnc_sn=pa.bcnc_sn AND pxcond_mt='{0}' ORDER BY pxcond_mt DESC LIMIT 1) AS rm
                    FROM account pa
                     LEFT JOIN account sa 
                     ON sa.cnnc_sn=pa.delng_sn
                     WHERE sa.delng_ty_code IN (11, 12)
                        AND pa.cntrct_sn = %(cntrct_sn)s
                        AND (pa.ddt_man < CONCAT(SUBSTRING(%(s_pxcond_mt)s, 1, 7),'-01') OR pa.ddt_man BETWEEN CONCAT(%(s_pxcond_mt)s,'-01') AND CONCAT(%(s_pxcond_mt)s,'-31'))
                    GROUP BY purchsofc_sn, cntrct_execut_code
                """.format(first_day)
        g.curs.execute(query, d)
        bcncs += g.curs.fetchall()

        query = """
                    SELECT IFNULL(SUM(IF(pxcond_mt < CONCAT(%(s_pxcond_mt)s,'-01'),excut_amount, 0)), 0) AS complete_amount                         
                         , IFNULL(SUM(IF(pxcond_mt < CONCAT(%(s_pxcond_mt)s,'-01'),0, excut_amount)), 0) AS tax_amount                         
                         , bcnc_sn AS purchsofc_sn
                         , 'E' AS cntrct_execut_code
                         , (SELECT bcnc_nm FROM bcnc WHERE bcnc_sn=p.bcnc_sn) AS purchsofc_nm
                         , (SELECT rm FROM pxcond WHERE cntrct_sn=p.cntrct_sn AND cntrct_execut_code='E' AND bcnc_sn=p.bcnc_sn AND pxcond_mt='{0}' ORDER BY pxcond_mt DESC LIMIT 1) AS rm
                    FROM pxcond p
                     WHERE p.cntrct_sn = %(cntrct_sn)s
                        AND (pxcond_mt < CONCAT(%(s_pxcond_mt)s,'-01') OR pxcond_mt BETWEEN CONCAT(%(s_pxcond_mt)s,'-01') AND CONCAT(%(s_pxcond_mt)s,'-31'))
                    GROUP BY purchsofc_sn
                """.format(first_day)
        g.curs.execute(query, d)
        pxconds = g.curs.fetchall()

        query = """
                    SELECT IFNULL(SUM(IF(t.pblicte_de < CONCAT(SUBSTRING(%(s_pxcond_mt)s,1,7),'-01'), t.SPLPC_AM+IFNULL(t.VAT, 0), 0) ), 0) AS complete_amount                       
                         , IFNULL(SUM(IF(t.pblicte_de < CONCAT(SUBSTRING(%(s_pxcond_mt)s,1,7),'-01'), 0, t.SPLPC_AM+IFNULL(t.VAT, 0)) ), 0) AS tax_amount                       
                         , pblicte_trget_sn AS purchsofc_sn
                         , IF(t.delng_se_code IN ('S', 'S1', 'S3'), 'C', 'E') AS cntrct_execut_code
                         , (SELECT bcnc_nm FROM bcnc WHERE bcnc_sn=pblicte_trget_sn) AS purchsofc_nm
                         , (SELECT rm FROM pxcond WHERE cntrct_sn=t.cntrct_sn AND cntrct_execut_code=IF(t.delng_se_code IN ('S', 'S1', 'S3'), 'C', 'E') AND bcnc_sn=t.pblicte_trget_sn AND pxcond_mt='{0}' ORDER BY pxcond_mt DESC LIMIT 1) AS rm
                    FROM taxbil t
                     WHERE t.cntrct_sn = %(cntrct_sn)s
                        AND (t.pblicte_de < CONCAT(SUBSTRING(%(s_pxcond_mt)s,1,7),'-01') OR t.pblicte_de BETWEEN CONCAT(SUBSTRING(%(s_pxcond_mt)s,1,7),'-01') AND CONCAT(SUBSTRING(%(s_pxcond_mt)s,1,7),'-31'))
                        AND t.delng_se_code IN ('S', 'S1', 'S3', 'P')
                    GROUP BY purchsofc_sn
                """.format(first_day)
        g.curs.execute(query, d)
        bcncs += g.curs.fetchall()


        query = """
                    SELECT co.purchsofc_sn AS purchsofc_sn
                        , CASE WHEN co.cntrct_execut_code = 'C' THEN '0'
                            ELSE co.ct_se_code
                            END AS ct_se_code
                        , SUM(CASE WHEN co.cntrct_execut_code = 'C' AND co.ct_se_code NOT IN ('9') THEN IFNULL(co.qy*co.salamt, 0)
                            WHEN co.cntrct_execut_code = 'C' AND co.ct_se_code IN ('9') THEN IFNULL(ROUND((co.puchas_amount*((100-co.dscnt_rt)/100))*co.qy * (co.fee_rt/100)), 0)
                            WHEN co.cntrct_execut_code = 'A' THEN IFNULL(co.qy*co.salamt, 0)
                            ELSE IFNULL(co.qy*co.puchas_amount, 0)
                            END) AS cntrct_amount
                        , (SELECT bcnc_nm FROM bcnc WHERE bcnc_sn=co.purchsofc_sn) AS purchsofc_nm
                        , 0 AS complete_amount
                        , 0 AS tax_amount
                        , co.cntrct_execut_code AS cntrct_execut_code
                        , (SELECT rm FROM pxcond WHERE cntrct_sn=co.cntrct_sn AND cntrct_execut_code=co.cntrct_execut_code AND bcnc_sn=co.purchsofc_sn AND pxcond_mt='{1}' ORDER BY pxcond_mt DESC LIMIT 1) AS rm
                    FROM (SELECT x.* FROM cost x INNER JOIN (SELECT cntrct_sn, MAX(extra_sn) AS m_extra_sn FROM cost WHERE 1=1 GROUP BY cntrct_sn) y ON x.cntrct_sn=y.cntrct_sn AND x.extra_sn=y.m_extra_sn AND x.purchsofc_sn IS NOT NULL) co
                        JOIN contract ct
                        ON co.cntrct_sn=ct.cntrct_sn
                        LEFT OUTER JOIN member m
                        ON ct.bsn_chrg_sn=m.mber_sn
                        LEFT OUTER JOIN member mm
                        ON ct.spt_chrg_sn=mm.mber_sn
                        LEFT OUTER JOIN project p
                        ON ct.cntrct_sn=p.cntrct_sn
                        WHERE  1=1
                        AND (co.ct_se_code NOT IN ('10'))
                        AND ct.cntrct_sn = %(cntrct_sn)s
                        AND ((co.ct_se_code IN ('61','62', '63','7') AND co.cntrct_execut_code = 'C') OR co.ct_se_code NOT IN ('61','62', '63','7'))
                        AND (co.cost_date <= '{0}' or co.cost_date IS NULL)
                        AND co.cntrct_execut_code NOT IN ('B', 'D')
                        AND co.purchsofc_sn NOT IN ('691')
                        AND mm.dept_code IN ('TS1', 'TS2')
                    GROUP BY purchsofc_sn,  CASE WHEN co.cntrct_execut_code = 'C' THEN '0'
                            ELSE co.ct_se_code
                            END, cntrct_execut_code
                """.format(last_day, first_day)
        g.curs.execute(query, d)
        costs = g.curs.fetchall()
        indirect_idx = -1
        for idx, cost in enumerate(costs):
            if cost['ct_se_code'] == '0' and cost['cntrct_execut_code'] == 'C':
                indirect_idx = idx
        for idx, cost in enumerate(costs):
            if cost['ct_se_code'] == '0' and cost['cntrct_execut_code'] == 'C' and indirect_idx != -1:
                if indirect_idx != idx and indirect_idx < len(costs):
                    indirect = costs[indirect_idx]
                    cost['cntrct_amount'] += indirect['cntrct_amount']
                    cost['complete_amount'] += indirect['complete_amount']
                    cost['tax_amount'] += indirect['tax_amount']
                    del costs[indirect_idx]
        costs = {(cost['purchsofc_sn'], cost['cntrct_execut_code']) : cost for cost in costs}
        pxconds = {(pxcond['purchsofc_sn'], pxcond['cntrct_execut_code']) : pxcond for pxcond in pxconds}


        query = """
                    SELECT o.cntrct_sn
                        , o.prjct_sn
                        , o.outsrc_fo_sn
                        , (SELECT bcnc_nm FROM bcnc WHERE ctmmny_sn=1 AND bcnc_sn=o.outsrc_fo_sn) AS outsrc_fo_nm
                        , o.cntrct_de
                        , o.outsrc_sn
                        , rspnber_nm
                        , rspnber_telno
                        , charger_nm
                        , charger_telno
                        , pymnt_mth
                        , outsrc_dtls
                        FROM outsrc o
                        WHERE o.cntrct_sn = %(cntrct_sn)s
                        AND (o.pymnt_mth <> '' OR o.outsrc_dtls <> '')
                """
        g.curs.execute(query, d)
        outsrcs = g.curs.fetchall()
        human_cntrct_amounts = [0, 0]
        establish_cntrct_amounts = {0 : {}, 1 : {}}
        for outsrc in outsrcs:
            if outsrc['pymnt_mth'] != '' and len(outsrc['pymnt_mth'].split("-")) == 4:
                if int(outsrc['outsrc_fo_sn']) not in establish_cntrct_amounts[0]:
                    establish_cntrct_amounts[0][int(outsrc['outsrc_fo_sn'])] = 0
                establish_cntrct_amounts[0][int(outsrc['outsrc_fo_sn'])] += int(outsrc['pymnt_mth'].split("-")[0]) + int(outsrc['pymnt_mth'].split("-")[1])
                human_cntrct_amounts[0] += int(outsrc['pymnt_mth'].split("-")[2])
            if outsrc['outsrc_dtls'] != '' and len(outsrc['outsrc_dtls'].split("-")) == 4:
                if int(outsrc['outsrc_fo_sn']) not in establish_cntrct_amounts[1]:
                    establish_cntrct_amounts[1][int(outsrc['outsrc_fo_sn'])] = 0
                establish_cntrct_amounts[1][int(outsrc['outsrc_fo_sn'])] += int(outsrc['outsrc_dtls'].split("-")[0]) + int(outsrc['outsrc_dtls'].split("-")[1])
                human_cntrct_amounts[1] += int(outsrc['outsrc_dtls'].split("-")[2])
        human_cntrct_amount = human_cntrct_amounts[1] if human_cntrct_amounts[1] != 0 else human_cntrct_amounts[0]
        establish_cntrct_amount = establish_cntrct_amounts[1] if sum(establish_cntrct_amounts[1].values()) != 0 else establish_cntrct_amounts[0]
        human_inserted = False
        for bcnc in bcncs:
            key = (bcnc['purchsofc_sn'], bcnc['cntrct_execut_code'])
            if key == (74, 'E') and d['cntrct_sn'] in (12679, 12458):
                print(bcnc)
                print(key in costs)
            if key in costs:
                cntrct_amount = costs[key]['cntrct_amount']
                ct_se_code = costs[key]['ct_se_code']
                del costs[key]
            else:
                cntrct_amount = 0
                ct_se_code = ''
            if bcnc['purchsofc_sn'] == 146 and bcnc['cntrct_execut_code'] == 'E':
                cntrct_amount = human_cntrct_amount
                human_inserted = True
            elif ct_se_code != '' and int(ct_se_code) == 5 and bcnc['cntrct_execut_code']  == 'E' and int(bcnc['purchsofc_sn']) in establish_cntrct_amount:
                cntrct_amount = establish_cntrct_amount[int(bcnc['purchsofc_sn'])]
            bcnc.update(d)
            bcnc.update({"cntrct_amount" : cntrct_amount, "excut_amount" :0, "ct_se_code" : ct_se_code})
            if key in pxconds:
                bcnc['excut_amount'] = pxconds[key]['tax_amount']
            result_part.append(bcnc)
        for cost in costs.values():
            if cost['cntrct_amount'] != 0.0:
                cost.update(d)
                cost.update({"excut_amount" : 0})
                key = (cost['purchsofc_sn'], cost['cntrct_execut_code'])
                if key in pxconds:
                    cost['excut_amount'] = pxconds[key]['tax_amount']
                if cost['purchsofc_sn'] == 146 and cost['cntrct_execut_code'] == 'E':
                    cost['cntrct_amount'] = human_cntrct_amount
                    human_inserted = True

                elif cost['ct_se_code'] != '' and int(cost['ct_se_code']) == 5 and cost['cntrct_execut_code'] == 'E' and int(cost['purchsofc_sn']) in establish_cntrct_amount:
                    cost['cntrct_amount'] = establish_cntrct_amount[int(cost['purchsofc_sn'])]
                result_part.append(cost)

        if human_cntrct_amount != 0 and not human_inserted:
            if len(result_part) > 0:
                raw = {key:value for key, value in result_part[-1].items()}
                raw['cntrct_amount'] = human_cntrct_amount
                raw['tax_amount'] = 0.0
                raw['cntrct_execut_code'] = 'E'
                raw['purchsofc_sn'] = 146
                raw['purchsofc_nm'] = '일용직'
                raw['ct_se_code'] = ''
                raw['excut_amount'] = 0.0
                raw['complete_amount'] = 0
                result_part.append(raw)

        result_part = sorted(result_part, key=lambda d: (d['cntrct_execut_code'], CT_SE_CODE_ORDER[''] if d['ct_se_code'] == '' else CT_SE_CODE_ORDER[int(d['ct_se_code'])] if int(d['ct_se_code']) in CT_SE_CODE_ORDER else 99))
        if len(result_part) == 0:
            print('"{}"'.format(d['spt_nm']))
        result +=  result_part

    # ct_se_code in (1, 2, 4) : SELECT IFNULL(SUM(pa.dlnt*pa.dlamt), 0) FROM account pa, sa WHERE sa.delng_ty_code IN (11, 12) AND pa.bcnc_sn = p_bcnc_sn AND pa.delng_se_code = p_delng_se_code
# ct_se_code in (3) :  SELECT IFNULL(SUM(sa.dlnt*sa.dlamt), 0) FROM account pa, sa WHERE sa.delng_ty_code IN (11, 12) AND pa.bcnc_sn = p_bcnc_sn AND pa.delng_se_code = p_delng_se_code
# ct_se_code in (8) : SELECT IFNULL(SUM(excut_amount), 0) FROM pxcond AND bcnc_sn = p_bcnc_sn AND cntrct_execut_code = p_cntrct_execut_code
# Else : SELECT IFNULL(SUM(t.SPLPC_AM+IFNULL(t.VAT, 0)), 0)


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

def get_completed_bcnc_data(params):
    result = dict()
    if "approval_sn" not in params:
        params['s_pxcond_mt'] = (datetime.datetime.now(timezone('Asia/Seoul')) + relativedelta(months=-1)).strftime("%Y-%m")
    else:
        g.curs.execute("SELECT DATE_FORMAT(DATE_SUB(reg_dtm, INTERVAL 1 MONTH), '%%Y-%%m') AS reg_time FROM approval WHERE approval_sn=%(approval_sn)s", params)
        params['s_pxcond_mt'] = g.curs.fetchone()['reg_time']
    query = """SELECT GET_ACCOUNT_COMPLETE_AMOUNT(c.cntrct_sn, c.bcnc_sn, 'P', %(s_pxcond_mt)s) AS completed_1
                    , GET_TAXBIL_COMPLETE_AMOUNT(c.cntrct_sn, c.bcnc_sn, 'C', %(s_pxcond_mt)s) AS completed_2
                    , GET_PXCOND_COMPLETE_AMOUNT(c.cntrct_sn, c.bcnc_sn, 'S', %(s_pxcond_mt)s) AS completed_3
                FROM contract c
                WHERE c.cntrct_sn=%(s_cntrct_sn)s"""
    g.curs.execute(query, params)
    result['before'] = g.curs.fetchone()

    if "approval_sn" not in params:
        params['s_pxcond_mt'] = (datetime.datetime.now(timezone('Asia/Seoul'))).strftime("%Y-%m")
    else:
        g.curs.execute("SELECT DATE_FORMAT(reg_dtm, '%%Y-%%m') AS reg_time FROM approval WHERE approval_sn=%(approval_sn)s", params)
        params['s_pxcond_mt'] = g.curs.fetchone()['reg_time']
    query = """SELECT GET_ACCOUNT_COMPLETE_AMOUNT(c.cntrct_sn, c.bcnc_sn, 'P', %(s_pxcond_mt)s) AS completed_1
                    , GET_TAXBIL_COMPLETE_AMOUNT(c.cntrct_sn, c.bcnc_sn, 'C', %(s_pxcond_mt)s) AS completed_2
                    , GET_PXCOND_COMPLETE_AMOUNT(c.cntrct_sn, c.bcnc_sn, 'S', %(s_pxcond_mt)s) AS completed_3
                FROM contract c
                WHERE c.cntrct_sn=%(s_cntrct_sn)s"""
    g.curs.execute(query, params)
    result['now'] = g.curs.fetchone()
    return result

def get_completed(params):
    now = datetime.datetime.now(timezone('Asia/Seoul'))
    first = now.replace(day=1)
    last_month = first - datetime.timedelta(days=1)
    params["s_pxcond_mt"] = last_month.strftime("%Y-%m-01")
    query = """SELECT cntrct_sn
                    , excut_amount
                    , bcnc_sn
                    FROM pxcond
                    WHERE 1=1
                    AND cntrct_sn=%(s_cntrct_sn)s 
                    AND pxcond_mt=%(s_pxcond_mt)s 
                    AND bcnc_sn=%(s_outsrc_fo_sn)s 
                    AND cntrct_execut_code='E'
                    """
    g.curs.execute(query, params)
    result = g.curs.fetchone()
    data = None
    if result is None:
        data = {int(params["s_outsrc_fo_sn"]) : 0}
    else:
        data = {int(result["bcnc_sn"]) : result["excut_amount"]}

    query = """SELECT cntrct_sn
                    , excut_amount
                    , bcnc_sn
                    FROM pxcond
                    WHERE 1=1
                    AND cntrct_sn=%(s_cntrct_sn)s 
                    AND pxcond_mt=%(s_pxcond_mt)s 
                    AND bcnc_sn=146
                    AND cntrct_execut_code='E'
                    """
    g.curs.execute(query, params)
    result = g.curs.fetchone()
    if result is None:
        data[146] = 0
    else:
        data[146] = result["excut_amount"]


    return data

def insert_completed(params):
    from pprint import pprint
    pprint(params)
    a_now_tot = 0
    a_tot = 0
    for body_a, body_a_now, body_b, body_b_now in zip(params["body_a[]"], params["body_a_now[]"], params["body_b[]"], params["body_b_now[]"]):
        a = body_a.replace(",", "")
        a_now = body_a_now.replace(",", "")
        b = body_b.replace(",", "")
        b_now = body_b_now.replace(",", "")
        a = int(a) if a != '' else 0
        a_now = int(a_now) if a_now != '' else 0
        b = int(b) if b != '' else 0
        b_now = int(b_now) if b_now != '' else 0
        a_tot += a
        a_now_tot += a_now
    rate = a_now_tot*100.0/a_tot if a_tot != 0 else None
    if "now_est_1" in params:
        now_est_1 = int(params["now_est_1"].replace(",", "")) if params["now_est_1"].replace(",", "") != "" else 0
    else:
        now_est_1 = 0
    if "now_est_2" in params:
        now_est_2 = int(params["now_est_2"].replace(",", "")) if params["now_est_2"].replace(",", "") != "" else 0
    else:
        now_est_2 = 0
    if "now_est_3" in params:
        now_est_3 = int(params["now_est_3"].replace(",", "")) if params["now_est_3"].replace(",", "") != "" else 0
    else:
        now_est_3 = 0

    data = dict()
    data["cntrct_sn"] = params["cntrct_sn"]
    prjct = get_project_by_cntrct_nm(params["cntrct_sn"])
    prjct_sn = prjct['prjct_sn']
    data["prjct_sn"] = prjct_sn
    now = datetime.datetime.now(timezone('Asia/Seoul'))
    first = now.replace(day=1)
    last_month = first - datetime.timedelta(days=1)
    data["pxcond_mt"] = last_month.strftime("%Y-%m-01")
    data["cntrct_execut_code"] = 'E'
    data["ct_se_code"] = '5'
    data["regist_dtm"] = datetime.datetime.now(timezone('Asia/Seoul'))
    data["register_id"] = session["member"]["member_id"]
    data['ctmmny_sn'] = 1
    data["rm"] = params["option_bigo"].strip()


    data["bcnc_sn"] = params["outsrc_fo_sn"]
    data["excut_amount"] = now_est_1 + now_est_2
    data["rate"] = rate
    delete_pxcond(data)
    insert_pxcond(data)


    data["bcnc_sn"] = 146
    data["excut_amount"] = now_est_3
    delete_pxcond(data)
    insert_pxcond(data)


def update_pxcond(params):
    data = {}
    if "cntrct_sn" in params and params["cntrct_sn"]:
        data["cntrct_sn"] = params["cntrct_sn"]

    if "rate" in params and params["rate"]:
        data["rate"] = params["rate"]

    query = """SELECT MAX(pxcond_mt) AS m_pxcond_mt FROM pxcond WHERE cntrct_sn=%(cntrct_sn)s"""
    g.curs.execute(query, data)
    row = g.curs.fetchone()

    if row['m_pxcond_mt'] != '':
        data["pxcond_mt"] = row["m_pxcond_mt"]
        query = """UPDATE pxcond SET rate=%(rate)s WHERE cntrct_sn=%(cntrct_sn)s AND pxcond_mt=%(pxcond_mt)s"""
        g.curs.execute(query, data)
        return True
    else:
        return False


def insert_pxcond(params):
    data = {}

    if "cntrct_sn" in params and params["cntrct_sn"]:
        data["cntrct_sn"] = params["cntrct_sn"]

    if "prjct_sn" in params and params["prjct_sn"]:
        data["prjct_sn"] = params["prjct_sn"]

    if "pxcond_mt" in params and params["pxcond_mt"]:
        data["pxcond_mt"] = "{}-01".format("-".join(params["pxcond_mt"].split("-")[:2]))

    if "bcnc_sn" in params and params["bcnc_sn"]:
        data["bcnc_sn"] = params["bcnc_sn"]

    if "cntrct_execut_code" in params and params["cntrct_execut_code"]:
        data["cntrct_execut_code"] = params["cntrct_execut_code"]

    if "ct_se_code" in params and params["ct_se_code"]:
        data["ct_se_code"] = params["ct_se_code"]

    if "excut_amount" in params and params["excut_amount"]:
        data["excut_amount"] = params["excut_amount"]


    if "regist_dtm" not in data:
        data["regist_dtm"] = datetime.datetime.now(timezone('Asia/Seoul'))

    if "register_id" not in data:
        data["register_id"] = session["member"]["member_id"]

    data['ctmmny_sn'] = 1

    if "rate" in params:
        data["rate"] = params["rate"]
    else:
        data["rate"] = None
    if "rm" in params and params["rm"] != "":
        data["rm"] = params["rm"]
    else:
        data["rm"] = None

    sub_query = [key for key in data]
    params_query = ["%({})s".format(key) for key in data]

    query = """INSERT INTO pxcond({}) VALUES ({})""".format(",".join(sub_query), ",".join(params_query))
    g.curs.execute(query, data)
    return g.curs.lastrowid


def delete_pxcond(params):
    data = {}
    if "cntrct_sn" in params and params["cntrct_sn"]:
        data["cntrct_sn"] = params["cntrct_sn"]

    if "prjct_sn" in params and params["prjct_sn"]:
        data["prjct_sn"] = params["prjct_sn"]

    if "pxcond_mt" in params and params["pxcond_mt"]:
        data["pxcond_mt"] = "{}-01".format("-".join(params["pxcond_mt"].split("-")[:2]))

    if "bcnc_sn" in params and params["bcnc_sn"]:
        data["bcnc_sn"] = params["bcnc_sn"]

    if "cntrct_execut_code" in params and params["cntrct_execut_code"]:
        data["cntrct_execut_code"] = params["cntrct_execut_code"]

    if "ct_se_code" in params and params["ct_se_code"]:
        data["ct_se_code"] = params["ct_se_code"]

    keys = list(data.keys())
    query = "DELETE FROM pxcond WHERE {}".format(" AND ".join(["{0}=%({0})s".format(k) for k in keys]))
    g.curs.execute(query, data)

def get_indirect_data(params):
    query = """SELECT t.pblicte_de
    				, t.splpc_am
    				, IFNULL(t.vat, 0) AS vat
    				, (t.splpc_am + IFNULL(t.vat, 0)) AS total
    				, t.pblicte_trget_sn
    				, (SELECT bcnc_nm FROM bcnc WHERE ctmmny_sn=t.ctmmny_sn AND bcnc_sn=t.pblicte_trget_sn) AS pblicte_trget_nm
    				, t.rm
    				FROM taxbil t
    				WHERE t.ctmmny_sn = 1
    				AND t.cntrct_sn = %(cntrct_sn)s
    				AND t.delng_se_code = 'P' 
    				AND t.pblicte_trget_sn = 116
    				ORDER BY t.pblicte_de, t.pblicte_trget_sn"""
    g.curs.execute(query, params)
    result = dict()
    result["taxbilList"] = g.curs.fetchall(transform=False)

    query = """SELECT cntrct_execut_code AS cntrct_execut_code
    				, ct_se_code AS ct_se_code
    				, extra_sn AS extra_sn
    				, SUM(CASE cntrct_execut_code
    				WHEN 'E' THEN puchas_amount * qy
    				WHEN 'C' THEN salamt*qy
    				END) AS amount
    				, DATE_FORMAT(MIN(regist_dtm), '%%Y-%%m-%%d') AS dtm
    				FROM (SELECT x.* FROM cost x INNER JOIN (SELECT cntrct_sn, MAX(extra_sn) AS m_extra_sn FROM cost WHERE 1=1 GROUP BY cntrct_sn) y ON x.cntrct_sn=y.cntrct_sn AND x.extra_sn=y.m_extra_sn) co
    				WHERE 1=1
    				AND cntrct_sn = %(cntrct_sn)s
    				GROUP BY cntrct_execut_code, ct_se_code, extra_sn
    				ORDER BY extra_sn, cntrct_execut_code"""

    g.curs.execute(query, params)

    rows = g.curs.fetchall()
    result["indirect_total"] = 0
    result["va_total"] = 0
    for r in rows:
        if r["cntrct_execut_code"] == "C" :
            result["va_total"] += r["amount"] if r["amount"] != '' else 0
        else:
            result["va_total"] -= r["amount"] if r["amount"] != '' else 0

        if r["cntrct_execut_code"] == "E" and int(r["ct_se_code"]) == 8:
            result["indirect_total"] += r["amount"] if r["amount"] != '' else 0
    return result