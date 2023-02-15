from flask import session, jsonify, g
from app.helpers.datatable_helper import dt_query
from collections import OrderedDict
import datetime

def get_work(params):
    query = """SELECT t.*, IFNULL(s.memo_sn, -1) AS memo_sn, IFNULL(s.memo_state, -1) AS memo_state FROM
				(SELECT e.work_row
				, e.work_month
				, e.work_data
				FROM work e
				WHERE 1=1
				AND e.work_year=%(work_year)s
				AND e.work_sn IN (SELECT MAX(ex.work_sn) FROM work ex WHERE ex.work_year=%(work_year)s GROUP BY ex.work_row, ex.work_month)
				) t LEFT OUTER JOIN (SELECT * FROM work_memo WHERE work_date=DATE_FORMAT(now(), %(format)s)) s ON t.work_row=s.work_row"""
    params['format'] = '%Y-%m-%d'
    g.curs.execute(query, params)
    result = g.curs.fetchall()
    return result

def get_bcncs():
    query = """SELECT DISTINCT c.bcnc_sn AS num
				, (SELECT bcnc_nm FROM bcnc WHERE bcnc_sn=c.bcnc_sn) AS name
				FROM contract c
				WHERE 1=1
				AND c.prjct_ty_code IN ('BD', 'BF')
				AND c.prjct_creat_at IN ('Y')
				AND c.progrs_sttus_code NOT IN ('C')
            """
    g.curs.execute(query, ())
    result = g.curs.fetchall()
    return result

def get_chrgs():
    query = """SELECT DISTINCT c.bsn_chrg_sn AS num
				, (SELECT mber_nm FROM member WHERE mber_sn=c.bsn_chrg_sn) AS name
				FROM contract c
				WHERE 1=1
				AND c.prjct_ty_code IN ('BD', 'BF')
				AND c.prjct_creat_at IN ('Y')
				AND c.progrs_sttus_code NOT IN ('C')
            """
    g.curs.execute(query, ())
    result = g.curs.fetchall()
    return result

def get_c_chrgs():
    query = """SELECT DISTINCT SUBSTRING_INDEX(SUBSTRING_INDEX(ch.charger_nm, ' ', 1), ' ', -1) AS num
				, SUBSTRING_INDEX(SUBSTRING_INDEX(ch.charger_nm, ' ', 1), ' ', -1) AS name
				FROM charger ch LEFT JOIN contract c
				ON ch.cntrct_sn=c.cntrct_sn
				WHERE 1=1
				AND c.prjct_ty_code IN ('BD', 'BF')
				AND c.prjct_creat_at IN ('Y')
				AND c.progrs_sttus_code NOT IN ('C')
				AND ch.charger_se_code = '1'
            """
    g.curs.execute(query, ())
    result = g.curs.fetchall()
    return result

def get_s12_account_list(params, s_dlivy_de=True):

    query = """SELECT DATE_FORMAT(s.dlivy_de, %s) AS s_dlivy_de
				, c.cntrct_sn
				, IFNULL(SUM((s.dlnt * p.dlamt)), 0) AS p_total
				FROM account s
				LEFT JOIN account p
				ON s.ctmmny_sn=p.ctmmny_sn AND s.cntrct_sn=p.cntrct_sn AND s.prjct_sn=p.prjct_sn AND s.cnnc_sn=p.delng_sn
				LEFT JOIN contract c
				ON s.cntrct_sn=c.cntrct_sn
                LEFT OUTER JOIN member m
				ON m.mber_sn=c.spt_chrg_sn
				WHERE s.ctmmny_sn = 1
				AND s.delng_se_code = 'S'
				AND p.delng_ty_code IN ('1', '2')
				AND s.delng_ty_code <> 14
                AND (c.progrs_sttus_code IN ('P') OR (c.progrs_sttus_code='C' AND c.update_dtm BETWEEN '{0}-01-01 00:00:00' AND '{0}-12-31 23:59:59'))
							
""".format(params['s_year'])
    if s_dlivy_de:
        query += "				AND s.dlivy_de BETWEEN '{0}-01-01 00:00:00' AND '{0}-12-31 23:59:59'".format(params['s_year'])
    data = ['%m']
    if "s_dept_code" in params and params["s_dept_code"]:
        if params["s_dept_code"] == "TS":
            query += " AND m.dept_code LIKE %s "
            data.append("TS%")
        else:
            query += " AND m.dept_code='BI' "
    query += " GROUP BY s_dlivy_de, c.cntrct_sn"
    print(query, data)
    g.curs.execute(query, data)
    result = g.curs.fetchall()
    return result

def get_s34_account_list(params):
    query = """SELECT DATE_FORMAT(a.dlivy_de, %s) AS s_dlivy_de
				, c.cntrct_sn
				, SUM((a.dlnt * a.dlamt)) AS s_total
				FROM account a
				LEFT JOIN account ac
				ON a.ctmmny_sn=ac.ctmmny_sn AND a.cntrct_sn=ac.cntrct_sn AND a.prjct_sn=ac.prjct_sn AND a.cnnc_sn=ac.delng_sn
				LEFT JOIN contract c
				ON a.cntrct_sn=c.cntrct_sn
                LEFT OUTER JOIN member m
				ON m.mber_sn=c.spt_chrg_sn
				WHERE a.ctmmny_sn = 1
				AND a.delng_se_code = 'S'
				AND ac.delng_ty_code IN ('3', '4')
				AND a.dlivy_de BETWEEN '{0}-01-01 00:00:00' AND '{0}-12-31 23:59:59'
                AND (c.progrs_sttus_code IN ('P') OR (c.progrs_sttus_code='C' AND c.update_dtm BETWEEN '{0}-01-01 00:00:00' AND '{0}-12-31 23:59:59'))
""".format(params['s_year'])
    data = ['%m']
    if "s_dept_code" in params and params["s_dept_code"]:
        if params["s_dept_code"] == "TS":
            query += " AND m.dept_code LIKE %s "
            data.append("TS%")
        else:
            query += " AND m.dept_code='BI' "
    query += " GROUP BY s_dlivy_de, c.cntrct_sn"
    g.curs.execute(query, data)
    result = g.curs.fetchall()
    return result

def get_s6_account_list(params):
    query = """SELECT CAST(DATE_FORMAT(s.dlivy_de, %s) AS CHAR ) AS s_dlivy_de
    				, p.delng_ty_code AS p_delng_ty_code
    				, c.cntrct_sn
    				FROM account s
    				LEFT JOIN account p
    				ON s.ctmmny_sn=p.ctmmny_sn AND s.cntrct_sn=p.cntrct_sn AND s.prjct_sn=p.prjct_sn AND s.cnnc_sn=p.delng_sn
    				LEFT JOIN contract c 
    				ON s.cntrct_sn=c.cntrct_sn
                    LEFT JOIN charger ch
                    ON c.cntrct_sn=ch.cntrct_sn AND ch.charger_se_code='1'
    				WHERE s.ctmmny_sn = 1
    				AND s.delng_se_code = 'S'
    				AND p.delng_ty_code IN ('61', '62')
    """
    data = ['%y/%m']
    if "s_resrv_type" in params and params['s_resrv_type']:
        query += " AND c.prjct_ty_code=%s"
        data.append(params["s_resrv_type"])
    else:
        query += " AND c.prjct_ty_code IN ('BD', 'BF')"

    query += """ AND c.prjct_creat_at IN ('Y')
                 AND c.progrs_sttus_code NOT IN ('C')  """

    if "s_resrv_bcnc" in params and params['s_resrv_bcnc']:
        query += " AND bcnc_sn=%s"
        data.append(params["s_resrv_bcnc"])

    if "s_resrv_chrg" in params and params['s_resrv_chrg']:
        query += " AND bsn_chrg_sn=%s"
        data.append(params["s_resrv_chrg"])

    if "s_resrv_c_chrg" in params and params['s_resrv_c_chrg']:
        query += " AND SUBSTRING_INDEX(SUBSTRING_INDEX(charger_nm, ' ', 1), ' ', -1)=%s"
        data.append(params["s_resrv_c_chrg"])

    query += """ GROUP BY s_dlivy_de, p.delng_ty_code, c.cntrct_sn
    	         ORDER BY s_dlivy_de ASC """
    g.curs.execute(query, data)
    result = g.curs.fetchall()
    return result

def get_i2_rcppay_list(params):
    query = """SELECT SUM(r.amount) AS amount
				, r.rcppay_se_code
				, c.cntrct_sn
				FROM rcppay r
                LEFT JOIN contract c 
                ON r.cntrct_sn=c.cntrct_sn
                LEFT JOIN charger ch
                ON c.cntrct_sn=ch.cntrct_sn AND ch.charger_se_code='1'
				WHERE r.ctmmny_sn = 1
				AND r.rcppay_se_code IN ('I1', 'I2', 'I4')
    """
    data = []
    if "s_resrv_type" in params and params['s_resrv_type']:
        query += " AND c.prjct_ty_code=%s"
        data.append(params["s_resrv_type"])
    else:
        query += " AND c.prjct_ty_code IN ('BD', 'BF')"

    query += """ AND c.prjct_creat_at IN ('Y')
                 AND c.progrs_sttus_code NOT IN ('C')  """

    if "s_resrv_bcnc" in params and params['s_resrv_bcnc']:
        query += " AND bcnc_sn=%s"
        data.append(params["s_resrv_bcnc"])

    if "s_resrv_chrg" in params and params['s_resrv_chrg']:
        query += " AND bsn_chrg_sn=%s"
        data.append(params["s_resrv_chrg"])

    if "s_resrv_c_chrg" in params and params['s_resrv_c_chrg']:
        query += " AND SUBSTRING_INDEX(SUBSTRING_INDEX(charger_nm, ' ', 1), ' ', -1)=%s"
        data.append(params["s_resrv_c_chrg"])

    query += """ GROUP BY r.rcppay_se_code, c.cntrct_sn """
    g.curs.execute(query, data)
    result = g.curs.fetchall()
    return result

def get_s_taxbil_list(params):
    query = """SELECT DATE_FORMAT(t.pblicte_de, %s) AS s_dlivy_de
    				, SUM(t.splpc_am + IFNULL(t.vat,0)) AS total
    				, c.cntrct_sn
    				FROM taxbil t
                    LEFT JOIN contract c
                    ON t.cntrct_sn=c.cntrct_sn
                    LEFT OUTER JOIN member m
                    ON m.mber_sn=c.spt_chrg_sn
    				WHERE t.ctmmny_sn = 1
     				AND t.delng_se_code = 'S' 
    				AND t.pblicte_de BETWEEN '{0}-01-01 00:00:00' AND '{0}-12-31 23:59:59'
                    AND (c.progrs_sttus_code IN ('P') OR (c.progrs_sttus_code='C' AND c.update_dtm BETWEEN '{0}-01-01 00:00:00' AND '{0}-12-31 23:59:59'))				
    """.format(params['s_year'])
    data = ['%m']
    if "s_dept_code" in params and params["s_dept_code"]:
        if params["s_dept_code"] == "TS":
            query += " AND m.dept_code LIKE %s "
            data.append("TS%")
        else:
            query += " AND m.dept_code='BI' "
    query += " GROUP BY s_dlivy_de, c.cntrct_sn"
    g.curs.execute(query, data)
    result = g.curs.fetchall()
    return result

def get_outsrc_taxbill_list(params):
    query = """SELECT DATE_FORMAT(t.pblicte_de, %s) AS s_dlivy_de
    				, SUM(t.splpc_am + IFNULL(t.vat, 0)) AS total
    				, c.cntrct_sn
    				FROM taxbil t
                    LEFT JOIN contract c
                    ON t.cntrct_sn=c.cntrct_sn
                    LEFT OUTER JOIN member m
                    ON m.mber_sn=c.spt_chrg_sn
    				WHERE t.ctmmny_sn = 1
    				AND t.delng_se_code = 'P' 
    				AND t.pblicte_de BETWEEN '{0}-01-01 00:00:00' AND '{0}-12-31 23:59:59'
                    AND (c.progrs_sttus_code IN ('P') OR (c.progrs_sttus_code='C' AND c.update_dtm BETWEEN '{0}-01-01 00:00:00' AND '{0}-12-31 23:59:59'))				
""".format(params['s_year'])

    data = ['%m']
    if "s_dept_code" in params and params["s_dept_code"]:
        if params["s_dept_code"] == "TS":
            query += " AND m.dept_code LIKE %s "
            data.append("TS%")
        else:
            query += " AND m.dept_code='BI' "
    query += " GROUP BY s_dlivy_de, c.cntrct_sn"
    g.curs.execute(query, data)
    result = g.curs.fetchall()
    return result

def get_s6_taxbill_list(params):
    query = """SELECT CAST(DATE_FORMAT(t.pblicte_de, %s) AS CHAR ) AS s_dlivy_de
    				, t.delng_se_code AS s_delng_se_code
    				, c.cntrct_sn
    				, SUM(t.splpc_am + IFNULL(t.vat, 0)) as amount
    				FROM taxbil t
    				LEFT JOIN contract c 
    				ON t.cntrct_sn=c.cntrct_sn
                    LEFT JOIN charger ch
                    ON c.cntrct_sn=ch.cntrct_sn AND ch.charger_se_code='1'
    				WHERE t.delng_se_code IN ('S1', 'S2', 'S4')
    				AND t.taxbil_yn = 'Y'
    """
    data = ['%y/%m']
    if "s_resrv_type" in params and params['s_resrv_type']:
        query += " AND c.prjct_ty_code=%s"
        data.append(params["s_resrv_type"])
    else:
        query += " AND c.prjct_ty_code IN ('BD', 'BF')"

    query += """ AND c.prjct_creat_at IN ('Y')
                 AND c.progrs_sttus_code NOT IN ('C')  """

    if "s_resrv_bcnc" in params and params['s_resrv_bcnc']:
        query += " AND bcnc_sn=%s"
        data.append(params["s_resrv_bcnc"])

    if "s_resrv_chrg" in params and params['s_resrv_chrg']:
        query += " AND bsn_chrg_sn=%s"
        data.append(params["s_resrv_chrg"])

    if "s_resrv_c_chrg" in params and params['s_resrv_c_chrg']:
        query += " AND SUBSTRING_INDEX(SUBSTRING_INDEX(charger_nm, ' ', 1), ' ', -1)=%s"
        data.append(params["s_resrv_c_chrg"])

    query += """ GROUP BY s_dlivy_de, s_delng_se_code, c.cntrct_sn
    	         ORDER BY s_dlivy_de ASC """
    g.curs.execute(query, data)
    result = g.curs.fetchall()
    return result

def get_bnd_rates(params):
    query = """SELECT c.cntrct_sn
                    , CASE WHEN c.prjct_ty_code IN ('NR') THEN
                        (SELECT IFNULL(SUM(IFNULL(co.QY, 0)*IFNULL(co.SALAMT,0)),0) FROM cost co WHERE co.cntrct_sn = c.cntrct_sn AND co.cntrct_execut_code IN ('A', 'C'))
                        WHEN c.prjct_ty_code IN ('BF') AND c.progrs_sttus_code <> 'B' THEN
                        (SELECT IFNULL(SUM(ROUND(IFNULL(co.QY, 0)*IFNULL(co.puchas_amount,0)*0.01*(100.0-IFNULL(co.dscnt_rt, 0))*IFNULL(co.fee_rt, 0)*0.01)),0) FROM cost co WHERE co.cntrct_sn = c.cntrct_sn AND co.cntrct_execut_code IN ('C'))
                        WHEN c.prjct_ty_code IN ('BD') AND c.progrs_sttus_code <> 'B' THEN
                        (SELECT IFNULL(SUM(IFNULL(co.QY, 0)*IFNULL(co.SALAMT,0)),0) FROM cost co WHERE co.cntrct_sn = c.cntrct_sn AND co.cntrct_execut_code IN ('A', 'C'))
                        WHEN c.prjct_ty_code IN ('BD') AND c.progrs_sttus_code = 'B' THEN
                        (SELECT IFNULL(SUM(IFNULL(co.QY, 0)*IFNULL(co.SALAMT,0)),0) FROM cost co WHERE co.cntrct_sn = c.cntrct_sn AND (co.cost_date > '0000-00-00') AND co.cntrct_execut_code IN ('C'))
                        ELSE 0
                        END AS cntrct_amount
    				FROM contract c
                    LEFT JOIN charger ch
                    ON c.cntrct_sn=ch.cntrct_sn
                    AND ch.charger_se_code='1'
    				WHERE 1=1
    """
    data = []
    if "s_resrv_type" in params and params['s_resrv_type']:
        query += " AND c.prjct_ty_code=%s"
        data.append(params["s_resrv_type"])
    else:
        query += " AND c.prjct_ty_code IN ('BD', 'BF')"

    query += """ AND c.prjct_creat_at IN ('Y')
                 AND c.progrs_sttus_code NOT IN ('C')  """

    if "s_resrv_bcnc" in params and params['s_resrv_bcnc']:
        query += " AND bcnc_sn=%s"
        data.append(params["s_resrv_bcnc"])

    if "s_resrv_chrg" in params and params['s_resrv_chrg']:
        query += " AND bsn_chrg_sn=%s"
        data.append(params["s_resrv_chrg"])

    if "s_resrv_c_chrg" in params and params['s_resrv_c_chrg']:
        query += " AND SUBSTRING_INDEX(SUBSTRING_INDEX(charger_nm, ' ', 1), ' ', -1)=%s"
        data.append(params["s_resrv_c_chrg"])

    query += " GROUP BY c.cntrct_sn"
    g.curs.execute(query, params)
    result = g.curs.fetchall()
    return result

def get_bnd_projects(params):
    query = """SELECT c.cntrct_sn
				, c.bcnc_sn
				, DATE_FORMAT(c.cntrwk_endde, %s) AS cntrwk_endde
				, DATE_FORMAT(c.cntrct_de, %s) AS cntrct_de
				, c.bsn_chrg_sn
				, (SELECT mber_nm FROM member WHERE mber_sn=c.bsn_chrg_sn) AS bsn_chrg_nm
				, (SELECT bcnc_nm FROM bcnc WHERE bcnc_sn=c.bcnc_sn) AS bcnc_nm
				, c.spt_nm
				, SUBSTRING_INDEX(SUBSTRING_INDEX(ch.charger_nm, ' ', 1), ' ', -1) AS chrg_nm
				, ch.charger_sn AS chrg_sn
				, IF(c.prjct_ty_code IN ('BD'), '직계약', '수수료') AS prjct_ty_nm
				, c.progrs_sttus_code
				, c.prjct_ty_code
				, CASE WHEN c.prjct_ty_code IN ('NR') THEN
				(SELECT IFNULL(SUM(IFNULL(co.QY, 0)*IFNULL(co.SALAMT,0)),0) FROM cost co WHERE co.cntrct_sn = c.cntrct_sn AND co.cntrct_execut_code IN ('A', 'C'))
				WHEN c.prjct_ty_code IN ('BF') AND c.progrs_sttus_code <> 'B' THEN
				(SELECT IFNULL(SUM(ROUND(IFNULL(co.QY, 0)*IFNULL(co.puchas_amount,0)*0.01*(100.0-IFNULL(co.dscnt_rt, 0))*IFNULL(co.fee_rt, 0)*0.01)),0) FROM cost co WHERE co.cntrct_sn = c.cntrct_sn AND co.cntrct_execut_code IN ('C'))
				WHEN c.prjct_ty_code IN ('BD') AND c.progrs_sttus_code <> 'B' THEN
				(SELECT IFNULL(SUM(IFNULL(co.QY, 0)*IFNULL(co.SALAMT,0)),0) FROM cost co WHERE co.cntrct_sn = c.cntrct_sn AND co.cntrct_execut_code IN ('A', 'C'))
				WHEN c.prjct_ty_code IN ('BD') AND c.progrs_sttus_code = 'B' THEN
				(SELECT IFNULL(SUM(IFNULL(co.QY, 0)*IFNULL(co.SALAMT,0)),0) FROM cost co WHERE co.cntrct_sn = c.cntrct_sn AND (co.cost_date > '0000-00-00') AND co.cntrct_execut_code IN ('C'))
				ELSE 0
				END AS cntrct_amount
				, IF(c.progrs_sttus_code = 'P', 1, IF(c.progrs_sttus_code = 'B', 2, 3)) AS progrs_order
				FROM contract c
				LEFT JOIN charger ch
				ON c.cntrct_sn=ch.cntrct_sn
				AND ch.charger_se_code='1'
				WHERE 1=1
            """
    data = ["%y/%c/%d", "%y/%c/%d"]
    if "s_resrv_type" in params and params['s_resrv_type']:
        query += " AND c.prjct_ty_code=%s"
        data.append(params["s_resrv_type"])
    else:
        query += " AND c.prjct_ty_code IN ('BD', 'BF')"

    query += """ AND c.prjct_creat_at IN ('Y')
                 AND c.progrs_sttus_code NOT IN ('C')  """

    if "s_resrv_bcnc" in params and params['s_resrv_bcnc']:
        query += " AND bcnc_sn=%s"
        data.append(params["s_resrv_bcnc"])

    if "s_resrv_chrg" in params and params['s_resrv_chrg']:
        query += " AND bsn_chrg_sn=%s"
        data.append(params["s_resrv_chrg"])

    if "s_resrv_c_chrg" in params and params['s_resrv_c_chrg']:
        query += " AND SUBSTRING_INDEX(SUBSTRING_INDEX(charger_nm, ' ', 1), ' ', -1)=%s"
        data.append(params["s_resrv_c_chrg"])

    query += " ORDER BY progrs_order, cntrct_de "
    g.curs.execute(query, data)
    result = g.curs.fetchall()
    return result

def get_bcnc_contract_list(params):
    query = """SELECT c.cntrct_sn				
                , c.bcnc_sn
				, (SELECT bcnc_nm FROM bcnc WHERE bcnc_sn=c.bcnc_sn) AS bcnc_nm
				, c.spt_nm
				, m.dept_code
				, (SELECT code_nm FROM code WHERE ctmmny_sn=1 AND parnts_code='DEPT_CODE' AND code=m.dept_code) AS dept_nm
				, c.bsn_chrg_sn
				, GET_MEMBER_NAME(c.bsn_chrg_sn, 'S') AS bsn_chrg_nm
				, c.spt_chrg_sn
				, GET_MEMBER_NAME(c.spt_chrg_sn, 'S') AS spt_chrg_nm
				, (SELECT code_ordr FROM code WHERE ctmmny_sn=1 AND parnts_code='DEPT_CODE' AND code=m.dept_code) AS code_ordr
				, CASE WHEN c.prjct_ty_code IN ('NR') THEN
				(SELECT IFNULL(SUM(IFNULL(co.QY, 0)*IFNULL(co.SALAMT,0)),0) FROM cost co WHERE co.cntrct_sn = c.cntrct_sn AND co.cntrct_execut_code IN ('A', 'C'))
				WHEN c.prjct_ty_code IN ('BF') AND c.progrs_sttus_code <> 'B' THEN
				(SELECT IFNULL(SUM(ROUND(IFNULL(co.QY, 0)*IFNULL(co.puchas_amount,0)*0.01*(100.0-IFNULL(co.dscnt_rt, 0))*IFNULL(co.fee_rt, 0)*0.01)),0) FROM cost co WHERE co.cntrct_sn = c.cntrct_sn AND co.cntrct_execut_code IN ('C'))
				WHEN c.prjct_ty_code IN ('BD') AND c.progrs_sttus_code <> 'B' THEN
				(SELECT IFNULL(SUM(IFNULL(co.QY, 0)*IFNULL(co.SALAMT,0)),0) FROM cost co WHERE co.cntrct_sn = c.cntrct_sn AND co.cntrct_execut_code IN ('A', 'C'))
				WHEN c.prjct_ty_code IN ('BD') AND c.progrs_sttus_code = 'B' THEN
				(SELECT IFNULL(SUM(IFNULL(co.QY, 0)*IFNULL(co.SALAMT,0)),0) FROM cost co WHERE co.cntrct_sn = c.cntrct_sn AND (co.cost_date > '0000-00-00') AND co.cntrct_execut_code IN ('C'))
				ELSE 0
				END AS cntrct_amount
                FROM contract c
                LEFT OUTER JOIN member m
				ON m.mber_sn=c.spt_chrg_sn
				LEFT OUTER JOIN project p
				ON p.cntrct_sn=c.cntrct_sn
                WHERE 1=1
                AND (c.progrs_sttus_code IN ('P') OR (c.progrs_sttus_code='C' AND c.update_dtm BETWEEN '{0}-01-01 00:00:00' AND '{0}-12-31 23:59:59'))
                """.format(params['s_year'])
    data = []
    if "s_dept_code" in params and params["s_dept_code"]:
        if params["s_dept_code"] == "TS":
            query += " AND m.dept_code LIKE %s "
            data.append("TS%")
        else:
            query += " AND m.dept_code='BI' "
    query += " ORDER BY code_ordr ASC, spt_chrg_nm ASC, bcnc_nm ASC, spt_nm ASC"
    g.curs.execute(query, data)
    result = g.curs.fetchall()
    return result

def get_a_e_cost_list(params):
    query = """SELECT c.cntrct_sn,
                SUM(puchas_amount * qy) AS amount
				FROM cost co
				LEFT JOIN contract c
				ON co.cntrct_sn=c.cntrct_sn
                LEFT OUTER JOIN member m
				ON m.mber_sn=c.spt_chrg_sn
				WHERE 1=1
                AND (c.progrs_sttus_code IN ('P') OR (c.progrs_sttus_code='C' AND c.update_dtm BETWEEN '{0}-01-01 00:00:00' AND '{0}-12-31 23:59:59'))
				AND extra_sn = 0
				AND cntrct_execut_code = 'E'
                AND ct_se_code IN ('1', '2', '3', '4', '5')				
""".format(params['s_year'])
    data = []
    if "s_dept_code" in params and params["s_dept_code"]:
        if params["s_dept_code"] == "TS":
            query += " AND m.dept_code LIKE %s "
            data.append("TS%")
        else:
            query += " AND m.dept_code='BI' "
    query += " GROUP BY c.cntrct_sn "
    g.curs.execute(query, data)
    result = g.curs.fetchall()
    return result

def set_bcnc_data(params):
    row = g.curs.execute("SELECT bcnc_sn FROM bcnced WHERE bcnc_year=%(bcnc_year)s AND bcnc_row=%(bcnc_row)s AND bcnc_month=%(bcnc_month)s", params)
    if row:
        result = g.curs.fetchone()
        params['bcnc_sn'] = result['bcnc_sn']
        if "bcnc_data" in params:
            g.curs.execute("UPDATE bcnced SET bcnc_data=%(bcnc_data)s, bcnc_class=%(bcnc_class)s WHERE bcnc_sn=%(bcnc_sn)s", params)
        else:
            g.curs.execute("UPDATE bcnced SET bcnc_class=%(bcnc_class)s WHERE bcnc_sn=%(bcnc_sn)s", params)

    else:
        if "bcnc_data" not in params:
            params["bcnc_data"] = ""
        g.curs.execute("INSERT INTO bcnced(bcnc_year, bcnc_row, bcnc_month, bcnc_data, bcnc_class) VALUES(%(bcnc_year)s, %(bcnc_row)s, %(bcnc_month)s, %(bcnc_data)s, %(bcnc_class)s)", params)

def set_bnd_data(params):
    row = g.curs.execute("SELECT bnd_sn FROM bnd WHERE bnd_year=%(bnd_year)s AND bnd_row=%(bnd_row)s AND bnd_month=%(bnd_month)s", params)
    if row:
        result = g.curs.fetchone()
        params['bnd_sn'] = result['bnd_sn']
        if "bnd_data" in params:
            g.curs.execute("UPDATE bnd SET bnd_data=%(bnd_data)s, bnd_class=%(bnd_class)s WHERE bnd_sn=%(bnd_sn)s", params)
        else:
            g.curs.execute("UPDATE bnd SET bnd_class=%(bnd_class)s WHERE bnd_sn=%(bnd_sn)s", params)

    else:
        if "bnd_data" not in params:
            params["bnd_data"] = ""
        g.curs.execute("INSERT INTO bnd(bnd_year, bnd_row, bnd_month, bnd_data, bnd_class) VALUES(%(bnd_year)s, %(bnd_row)s, %(bnd_month)s, %(bnd_data)s, %(bnd_class)s)", params)

def get_bcnc_data(params):
    g.curs.execute("SELECT bcnc_sn, bcnc_year, bcnc_row, bcnc_month, bcnc_data, bcnc_class FROM bcnced WHERE bcnc_year=%s", params['s_year'])
    result = g.curs.fetchall()
    return result

def get_bnd_data(params):
    g.curs.execute("SELECT bnd_sn, bnd_year, bnd_row, bnd_month, bnd_data, bnd_class FROM bnd WHERE bnd_year=%s", params['bnd_year'])
    result = g.curs.fetchall()
    return result