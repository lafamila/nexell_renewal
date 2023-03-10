from flask import session, jsonify, g
from app.helpers.datatable_helper import dt_query
from collections import OrderedDict
import datetime
import calendar

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
        query += " AND c.bcnc_sn=%s"
        data.append(params["s_resrv_bcnc"])

    if "s_resrv_chrg" in params and params['s_resrv_chrg']:
        query += " AND c.bsn_chrg_sn=%s"
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
    g.curs.execute(query, data)
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
				, IF(c.prjct_ty_code IN ('BD'), '?????????', '?????????') AS prjct_ty_nm
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
				, c.cntrwk_bgnde
				, c.cntrwk_endde
				, CONCAT(c.cntrwk_bgnde,' ~ ',c.cntrwk_endde) AS cntrwk_period
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

def set_month_data(params):
    row = g.curs.execute("SELECT month_sn FROM month WHERE month_year=%(month_year)s AND month_row=%(month_row)s AND month_month=%(month_month)s", params)
    if row:
        result = g.curs.fetchone()
        params['month_sn'] = result['month_sn']
        if "month_data" in params:
            g.curs.execute("UPDATE month SET month_data=%(month_data)s, month_class=%(month_class)s WHERE month_sn=%(month_sn)s", params)
        else:
            g.curs.execute("UPDATE month SET month_class=%(month_class)s WHERE month_sn=%(month_sn)s", params)

    else:
        if "month_data" not in params:
            params["month_data"] = ""
        g.curs.execute("INSERT INTO month(month_year, month_row, month_month, month_data, month_class) VALUES(%(month_year)s, %(month_row)s, %(month_month)s, %(month_data)s, %(month_class)s)", params)

def get_bcnc_data(params):
    g.curs.execute("SELECT bcnc_sn, bcnc_year, bcnc_row, bcnc_month, bcnc_data, bcnc_class FROM bcnced WHERE bcnc_year=%s", params['s_year'])
    result = g.curs.fetchall()
    return result

def get_bnd_data(params):
    g.curs.execute("SELECT bnd_sn, bnd_year, bnd_row, bnd_month, bnd_data, bnd_class FROM bnd WHERE bnd_year=%s", params['bnd_year'])
    result = g.curs.fetchall()
    return result

def get_month_data(params):
    g.curs.execute("SELECT month_sn, month_year, month_row, month_month, month_data, month_class FROM month WHERE month_year=%s", params['s_year'])
    result = g.curs.fetchall()
    return result

def get_month_contract_list(params):
    query = """SELECT g.stdyy AS year
                    , g.1m AS 1m
                    , g.2m AS 2m
                    , g.3m AS 3m
                    , g.4m AS 4m
                    , g.5m AS 5m
                    , g.6m AS 6m
                    , g.7m AS 7m
                    , g.8m AS 8m
                    , g.9m AS 9m
                    , g.10m AS 10m
                    , g.11m AS 11m
                    , g.12m AS 12m
                    , (IFNULL(g.1m, 0) + IFNULL(g.2m, 0) + IFNULL(g.3m, 0)+ IFNULL(g.4m, 0)+ IFNULL(g.5m, 0)+ IFNULL(g.6m, 0)+ IFNULL(g.7m, 0)+ IFNULL(g.8m, 0)+ IFNULL(g.9m, 0)+ IFNULL(g.10m, 0)+ IFNULL(g.11m, 0)+ IFNULL(g.12m, 0)) AS tot
                    , g.cntrct_sn AS cntrct_sn
                    , c.spt_nm
    				, (SELECT code_nm FROM code WHERE ctmmny_sn=1 AND parnts_code='DEPT_CODE' AND code=m.dept_code) AS dept_nm
    				, m.dept_code
    				, c.bcnc_sn
    				, (SELECT bcnc_nm FROM bcnc WHERE bcnc_sn=c.bcnc_sn) AS bcnc_nm
    				, (SELECT code_ordr FROM code WHERE parnts_code='DEPT_CODE' AND code=m.dept_code) AS code_ordr
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
                    , DATE_FORMAT(c.cntrct_de, %s) AS cntrct_de
                    FROM (SELECT * FROM goal WHERE amt_ty_code='2' AND cntrct_sn <> 0 AND stdyy=%s) g
                    LEFT JOIN contract c ON g.cntrct_sn=c.cntrct_sn
                    LEFT JOIN member m ON g.mber_sn=m.mber_sn        
                    WHERE (IFNULL(g.1m, 0) + IFNULL(g.2m, 0) + IFNULL(g.3m, 0)+ IFNULL(g.4m, 0)+ IFNULL(g.5m, 0)+ IFNULL(g.6m, 0)+ IFNULL(g.7m, 0)+ IFNULL(g.8m, 0)+ IFNULL(g.9m, 0)+ IFNULL(g.10m, 0)+ IFNULL(g.11m, 0)+ IFNULL(g.12m, 0)) > 0
                    ORDER BY code_ordr, bcnc_nm, spt_nm
            """
    data = ["%Y-%m", params['s_year']]
    g.curs.execute(query, data)
    result = g.curs.fetchall()
    return result

def insert_memo(params):
    data = OrderedDict()
    for key in params:
        if key not in (None,):
            if params[key] != '':
                data[key] = params[key]

    if "regist_dtm" not in data:
        data["regist_dtm"] = datetime.datetime.now()

    if "register_id" not in data:
        data["register_id"] = session["member"]["member_id"]

    sub_query = [key for key in data]
    params_query = ["%({})s".format(key) for key in data]

    query = """INSERT INTO memo({}) VALUES ({})""".format(",".join(sub_query), ",".join(params_query))
    g.curs.execute(query, data)
    return g.curs.lastrowid

def get_memo_list(params):
    query = """SELECT memo_ty
				, memo_id
				, memo
				FROM memo m
				WHERE memo_sn IN (SELECT MAX(memo_sn) FROM memo WHERE memo_ty = %(s_memo_ty)s AND memo_de <= %(s_memo_de)s GROUP BY memo_ty, memo_id)
				AND memo_id <> ''
				AND memo_de <= %(s_memo_de)s """
    g.curs.execute(query, params)
    result = g.curs.fetchall()
    return result

def get_bcnc_datatable(params):
    query = """SELECT ctmmny_sn
				, bcnc_sn
				, bcnc_se_code
				, (SELECT code_nm FROM code WHERE ctmmny_sn=1 AND parnts_code='BCNC_SE_CODE' AND code=b.bcnc_se_code) AS bcnc_se_nm
				, bcnc_nm
				, bcnc_telno
				, bcnc_adres
				, rprsntv_nm
				, bizrno
				, bsnm_se_code
				, (SELECT code_nm FROM code WHERE ctmmny_sn=1 AND parnts_code='BSNM_SE_CODE' AND code=b.bsnm_se_code) AS bsnm_se_nm
				, esntl_delng_no
				, use_at
				, regist_dtm
				, register_id
				, update_dtm
				, updater_id
				FROM bcnc b
				WHERE 1=1
				AND ctmmny_sn = '1' """
    data = []
    if "s_bcnc_nm" in params and params['s_bcnc_nm']:
        query += " AND bcnc_nm LIKE %s"
        data.append('%{}%'.format(params["s_bcnc_nm"]))

    if "s_bizrno" in params and params['s_bizrno']:
        query += " AND bizrno LIKE %s"
        data.append('%{}%'.format(params["s_bizrno"]))

    if "s_bsnm_se_code" in params and params['s_bsnm_se_code']:
        query += " AND bsnm_se_code=%s"
        data.append(params["s_bsnm_se_code"])

    if "s_bcnc_se_code" in params and params['s_bcnc_se_code']:
        query += " AND bcnc_se_code=%s"
        data.append(params["s_bcnc_se_code"])

    if "s_rprsntv_nm" in params and params['s_rprsntv_nm']:
        query += " AND rprsnty_nm LIKE %s"
        data.append('%{}%'.format(params["s_rprsntv_nm"]))

    return dt_query(query, data, params)


def get_bcnc(params):
    query = """SELECT ctmmny_sn
				, bcnc_sn
				, bcnc_se_code
				, bcnc_nm
				, bcnc_telno
				, bcnc_adres
				, rprsntv_nm
				, bizrno
				, bsnm_se_code
				, esntl_delng_no
				, use_at
				, regist_dtm
				, register_id
				, update_dtm
				, updater_id
				FROM bcnc
				WHERE 1=1
				AND ctmmny_sn = '1'
				AND bcnc_sn = %(s_bcnc_sn)s """
    g.curs.execute(query, params)
    result = g.curs.fetchone()
    return result


def insert_bcnc(params):
    data = OrderedDict()
    for key in params:
        if key not in (None,):
            if params[key] != '':
                data[key] = params[key]

    if "ctmmny_sn" not in data:
        data["ctmmny_sn"] = '1'

    if "use_at" not in data:
        data["use_at"] = 'Y'

    if "regist_dtm" not in data:
        data["regist_dtm"] = datetime.datetime.now()

    if "register_id" not in data:
        data["register_id"] = session["member"]["member_id"]

    sub_query = [key for key in data]
    params_query = ["%({})s".format(key) for key in data]

    query = """INSERT INTO bcnc({}) VALUES ({})""".format(",".join(sub_query), ",".join(params_query))
    g.curs.execute(query, data)
    return g.curs.lastrowid

def update_bcnc(params):
    required = (None, )
    bcnc_sn = params["bcnc_sn"]

    data = OrderedDict()
    for key in params:
        if key not in ("bcnc_sn"):
            if key in required:
                if params[key] != '':
                    data[key] = key
            else:
                data[key] = params[key]
    sub_query = ["{0}=%({0})s".format(key) for key in data]
    query = """UPDATE bcnc SET {}, UPDATE_DTM=NOW() WHERE bcnc_sn=%(bcnc_sn)s""".format(",".join(sub_query))
    g.curs.execute(query, params)

def delete_bcnc(params):
    g.curs.execute("DELETE FROM bcnc WHERE bcnc_sn=%(bcnc_sn)s", params)

def get_money_data(params):
    query = """ SELECT c.cntrct_sn AS cntrct_sn
                , c.spt_nm AS cntrct_nm
				, t.delng_se_code AS delng_se_code
				, (SELECT code_nm FROM code WHERE ctmmny_sn=1 AND parnts_code='DELNG_SE_CODE' AND code=t.delng_se_code) AS delng_se_nm
                , t.pblicte_trget_sn AS bcnc_sn
                , (SELECT bcnc_nm FROM bcnc WHERE bcnc_sn=t.pblicte_trget_sn) AS bcnc_nm
				, (SELECT code_nm FROM code WHERE parnts_code='DEPT_CODE' AND code=m.dept_code) AS dept_nm
				, MIN(t.collct_de) AS collct_de
				, SUM(t.splpc_am + IFNULL(t.vat, 0)) AS amount
				, MIN(IFNULL(r.rcppay_de, '9999-99-99')) AS rcppay_de
				, SUM(IFNULL(r.price_1, 0)) AS price_1
				, SUM(IFNULL(r.price_2, 0)) AS price_2		
                , (SELECT code_ordr FROM code WHERE parnts_code='DEPT_CODE' AND code=m.dept_code) AS code_ordr						
                FROM (SELECT * FROM taxbil WHERE delng_se_code LIKE 'S%%' AND DATE_FORMAT(collct_de, '%%Y-%%m') = %(s_mt)s) t
                LEFT JOIN contract c
                ON t.cntrct_sn=c.cntrct_sn
                LEFT JOIN member m
                ON c.spt_chrg_sn=m.mber_sn
                LEFT OUTER JOIN (SELECT cnnc_sn
                                , MAX(rcppay_de) AS rcppay_de
                                , SUM(IF(bil_exprn_de IS NULL, amount, 0)) AS price_1
                                , SUM(IF(bil_exprn_de IS NULL, 0, amount)) AS price_2
                                 FROM rcppay 
                                 WHERE rcppay_se_code LIKE 'I%%' AND cnnc_sn IS NOT NULL
                                 GROUP BY cnnc_sn) r 
                ON t.taxbil_sn=r.cnnc_sn
                WHERE 1=1
                AND c.progrs_sttus_code IN ('P', 'B')
                GROUP BY c.cntrct_sn, t.pblicte_trget_sn, t.delng_se_code, DATE_FORMAT(t.collct_de, '%%Y-%%m')
                ORDER BY code_ordr, bcnc_sn, cntrct_nm
            """
    g.curs.execute(query, params)
    result = g.curs.fetchall()
    return result

def get_cowork_data(params):
    query = """SELECT c.cntrct_sn
                    , p.prjct_sn
                    , c.bcnc_sn
                    , o.outsrc_sn
                    , (SELECT bcnc_nm FROM bcnc WHERE bcnc_sn=c.bcnc_sn) AS bcnc_nm
                    , c.spt_nm AS spt_nm
                    , m.dept_code
                    , (SELECT code_nm FROM code WHERE ctmmny_sn=1 AND parnts_code='DEPT_CODE' AND code=m.dept_code) AS dept_nm
                    , c.bsn_chrg_sn AS bsn_chrg_sn
                    , GET_MEMBER_NAME(c.bsn_chrg_sn, 'S') AS bsn_chrg_nm
                    , (SELECT bcnc_nm FROM bcnc WHERE ctmmny_sn=1 AND bcnc_sn=o.outsrc_fo_sn) AS outsrc_fo_nm
                    , CASE co.cntrct_execut_code
                    WHEN 'E' THEN co.puchas_amount
                    WHEN 'C' THEN co.salamt
                    END AS amount
                    , co.qy AS qy
                    , co.model_no AS model_no  
                    , o.cntrct_de AS cntrct_de         
    				FROM (SELECT * FROM cost WHERE cntrct_execut_code = 'E' AND ct_se_code IN ('5')) co
    				LEFT JOIN outsrc o ON co.purchsofc_sn=o.outsrc_fo_sn AND co.prjct_sn=o.prjct_sn
    				LEFT JOIN contract c ON o.cntrct_sn=c.cntrct_sn
                    LEFT JOIN member m ON m.mber_sn=c.bsn_chrg_sn
                    LEFT JOIN project p ON p.cntrct_sn=c.cntrct_sn
                    WHERE 1=1
                    AND o.cntrct_de BETWEEN '{0}' AND '{1}'
                    """.format(params['s_start_de'], params['s_end_de'])
    #                    AND c.progrs_sttus_code IN ('P', 'B')

    data = []
    if "s_bcnc_sn" in params and params["s_bcnc_sn"]:
        query += " AND c.bcnc_sn=%s"
        data.append(params["s_bcnc_sn"])
    if "s_spt_nm" in params and params["s_spt_nm"]:
        query += " AND c.spt_nm LIKE %s"
        data.append("%{}%".format(params["s_spt_nm"]))
    if "s_dept_code" in params and params["s_dept_code"]:
        query += " AND m.dept_code=%s"
        data.append(params["s_dept_code"])
    if "s_bsn_chrg_sn" in params and params["s_bsn_chrg_sn"]:
        query += " AND c.bsn_chrg_sn=%s"
        data.append(params["s_bsn_chrg_sn"])
    query += " ORDER BY o.cntrct_de, c.cntrct_sn"
    g.curs.execute(query, data)
    result = g.curs.fetchall()
    return result

## ??????????????? ????????? ????????? ???
# def get_completed_reportBALL(params):
#     s_pxcond_mt = params['s_pxcond_mt']
#     year = s_pxcond_mt.split("-")[0]
#     month = s_pxcond_mt.split("-")[1]
#     day = calendar.monthrange(int(year), int(month))[-1]
#     day = str(day).zfill(2)
#     params['s_pxcond_mt'] = "{}-{}".format(year, month)
#
#     query = """SELECT t.prjct_ty_code
# 				, t.prjct_creat_at
# 				, t.bsn_dept_code
# 				, (SELECT code_nm FROM code WHERE ctmmny_sn=1 AND parnts_code='PRJCT_TY_CODE' AND code=t.prjct_ty_code) AS bsn_dept_nm
# 				, t.bsn_chrg_sn
# 				, GET_MEMBER_NAME(t.bsn_chrg_sn, 'M') AS bsn_chrg_nm
# 				, t.cntrct_bcnc_sn
# 				, (SELECT bcnc_nm FROM bcnc WHERE bcnc_sn=t.cntrct_bcnc_sn) AS cntrct_bcnc_nm
# 				, t.spt_chrg_sn
# 				, GET_MEMBER_NAME(t.spt_chrg_sn, 'M') AS spt_chrg_nm
# 				, t.spt_nm
# 				, t.cntrwk_bgnde
# 				, t.cntrwk_endde
# 				, t.cntrct_sn
# 				, t.cntrct_execut_code
# 				, t.progrs_sttus_code
# 				, (SELECT code_nm FROM code WHERE ctmmny_sn=1 AND parnts_code='CNTRCT_EXECUT_CODE' AND code=t.cntrct_execut_code) AS cntrct_execut_nm
# 				, t.ct_se_code
# 				, (SELECT code_nm FROM code WHERE ctmmny_sn=1 AND parnts_code='CT_SE_CODE' AND code=t.ct_se_code) AS ct_se_nm
# 				, t.purchsofc_sn
# 				, (SELECT bcnc_nm FROM bcnc WHERE bcnc_sn=t.purchsofc_sn) AS purchsofc_nm
# 				, SUM(t.cntrct_amount) AS cntrct_amount
# 				, SUM(t.extra_amount) AS extra_amount
# 				, CASE WHEN ct_se_code IN ('1','2','4') THEN GET_ACCOUNT_COMPLETE_AMOUNT(t.cntrct_sn, t.purchsofc_sn, 'P', %(s_pxcond_mt)s)
# 				WHEN ct_se_code IN ('3') THEN GET_ACCOUNT_COMPLETE_AMOUNT(t.cntrct_sn, t.purchsofc_sn, 'S', %(s_pxcond_mt)s)
# 				WHEN ct_se_code IN ('8') THEN GET_PXCOND_COMPLETE_AMOUNT(t.cntrct_sn, t.purchsofc_sn, 'S', %(s_pxcond_mt)s)
# 				WHEN ct_se_code IN ('61') THEN GET_ACCOUNT_COMPLETE_AMOUNT_M(t.cntrct_sn, t.purchsofc_sn, 'P', %(s_pxcond_mt)s)
# 				ELSE GET_TAXBIL_COMPLETE_AMOUNT(t.cntrct_sn, t.purchsofc_sn, t.cntrct_execut_code, %(s_pxcond_mt)s)
# 				END AS complete_amount
# 				, CASE WHEN ct_se_code IN ('1','2','4') THEN GET_ACCOUNT_EXCUT_AMOUNT(t.cntrct_sn, t.purchsofc_sn, 'P', %(s_pxcond_mt)s)
# 				WHEN ct_se_code IN ('3') THEN GET_ACCOUNT_EXCUT_AMOUNT(t.cntrct_sn, t.purchsofc_sn, 'S', %(s_pxcond_mt)s)
# 				WHEN ct_se_code IN ('8') THEN GET_PXCOND_EXCUT_AMOUNT(t.cntrct_sn, t.purchsofc_sn, t.cntrct_execut_code, %(s_pxcond_mt)s)
# 				WHEN ct_se_code IN ('61') THEN GET_ACCOUNT_EXCUT_AMOUNT_M(t.cntrct_sn, t.purchsofc_sn, 'P', %(s_pxcond_mt)s)
# 				ELSE GET_TAXBIL_EXCUT_AMOUNT(t.cntrct_sn, t.purchsofc_sn, t.cntrct_execut_code, %(s_pxcond_mt)s)
# 				END AS tax_amount
# 				, CASE WHEN ct_se_code IN ('1','2','4') THEN GET_ACCOUNT_EXCUT_AMOUNT(t.cntrct_sn, t.purchsofc_sn, 'P', %(s_pxcond_mt)s)
# 				WHEN ct_se_code IN ('3') THEN GET_ACCOUNT_EXCUT_AMOUNT(t.cntrct_sn, t.purchsofc_sn, 'S', %(s_pxcond_mt)s)
# 				ELSE GET_PXCOND_EXCUT_AMOUNT(t.cntrct_sn, t.purchsofc_sn, t.cntrct_execut_code, %(s_pxcond_mt)s)
# 				END AS excut_amount
# 				, GET_TAXBIL_COMPLETE_AMOUNT_M(t.cntrct_sn, t.purchsofc_sn, 'C', %(s_pxcond_mt)s) AS complete_amount_m
# 				, GET_TAXBIL_EXCUT_AMOUNT_M(t.cntrct_sn, t.purchsofc_sn, 'C', %(s_pxcond_mt)s) AS tax_amount_m
# 				, (SELECT rm FROM pxcond WHERE cntrct_sn=t.cntrct_sn AND cntrct_execut_code=t.cntrct_execut_code AND bcnc_sn=t.purchsofc_sn ORDER BY pxcond_mt DESC LIMIT 1) AS rm
#                         FROM (
#                         SELECT ct.prjct_ty_code
#                         , m.dept_code AS bsn_dept_code
#                         , ct.bcnc_sn AS cntrct_bcnc_sn
#                         , ct.bsn_chrg_sn
#                         , ct.prjct_creat_at
#                         , ct.spt_chrg_sn
#                         , ct.spt_nm
#                         , ct.cntrwk_bgnde
#                         , ct.cntrwk_endde
#                         , IF(ct.progrs_sttus_code = 'C' AND ct.update_dtm >= '{2} 23:59:59', 'P', ct.progrs_sttus_code) AS progrs_sttus_code
#                         , co.cntrct_sn
#                         , co.cntrct_execut_code
#                         , CASE WHEN co.cntrct_execut_code = 'C' THEN '0'
#                         WHEN co.cntrct_execut_code = 'A' THEN '0'
#                         ELSE co.ct_se_code
#                         END AS ct_se_code
#                         , co.purchsofc_sn
#                         , CASE WHEN co.cntrct_execut_code = 'C' AND co.ct_se_code NOT IN ('9') THEN IFNULL(co.qy*co.salamt, 0)
#                         WHEN co.cntrct_execut_code = 'C' AND co.ct_se_code IN ('9') THEN IFNULL(ROUND((co.puchas_amount*((100-co.dscnt_rt)/100))*co.qy * (co.fee_rt/100)), 0)
#                         WHEN co.cntrct_execut_code = 'E' AND co.ct_se_code IN ('61') THEN IFNULL(ROUND(co.qy*co.puchas_amount*((100-co.dscnt_rt)/100)), 0)
#                         WHEN co.cntrct_execut_code = 'A' THEN IFNULL(co.qy*co.salamt, 0)
#                         ELSE IFNULL(co.qy*co.puchas_amount, 0)
#                         END AS cntrct_amount
#                         , CASE WHEN co.cntrct_execut_code = 'E' AND co.ct_se_code IN ('61') THEN IFNULL(ROUND(co.qy*co.puchas_amount*((co.add_dscnt_rt)/100)), 0)
#                         ELSE 0
#                         END AS extra_amount
#                         FROM cost co
#                         JOIN contract ct
#                         ON co.cntrct_sn=ct.cntrct_sn
#                         LEFT OUTER JOIN member m
#                         ON ct.bsn_chrg_sn=m.mber_sn
#                         WHERE 1=1
#                         AND ct.cntrct_sn IN (SELECT cntrct_sn FROM contract WHERE progrs_sttus_code <> 'C' OR (progrs_sttus_code = 'C' AND update_dtm BETWEEN '{0} 00:00:00' AND '{1} 23:59:59'))
#                         AND co.ct_se_code NOT IN ('62','7','10')
#                         AND ct.prjct_ty_code IN ('BD','BF')
#                         AND co.cntrct_execut_code NOT IN ('B','D')
# """.format("{}-01-01".format(year), "{}-12-31".format(year), "{}-{}-01".format(year, month))
#     if "s_cntrct_execut_code" in params and params["s_cntrct_execut_code"]:
#         query += "      AND co.cntrct_execut_code = %(s_cntrct_execut_code)s "
#
#     query += """    ) t
# 				GROUP BY prjct_ty_code, bsn_chrg_sn, cntrct_bcnc_sn, spt_chrg_sn, spt_nm, cntrct_sn, cntrct_execut_code, ct_se_code, purchsofc_sn
# 				ORDER BY prjct_ty_code, bsn_chrg_sn, cntrct_bcnc_sn, spt_chrg_sn, spt_nm, cntrct_sn, cntrct_execut_code, ct_se_code, purchsofc_sn
#              """
#
#     g.curs.execute(query, params)
#     result = g.curs.fetchall()
#     return result