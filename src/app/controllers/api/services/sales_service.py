from flask import session, jsonify, g
from app.helpers.datatable_helper import dt_query
from .project_service import get_project_by_cntrct_nm
from collections import OrderedDict
import datetime
import calendar
def get_sales_datatable(params):
    query = """SELECT a.ctmmny_sn
				, a.cntrct_sn
				, a.prjct_sn
				, a.delng_sn
				, a.delng_se_code
				, (SELECT code_nm FROM code WHERE ctmmny_sn=1 AND parnts_code='DELNG_SE_CODE' AND code=a.delng_se_code) AS delng_se_nm
				, a.ddt_man
				, a.delng_ty_code AS delng_ty_code1
				, (SELECT code_nm FROM code WHERE ctmmny_sn=1 AND parnts_code='CT_SE_CODE' AND code=a.delng_ty_code) AS delng_ty_nm1
				, a.delng_ty_code AS delng_ty_code2
				, (SELECT code_nm FROM code WHERE ctmmny_sn=1 AND parnts_code='SELNG_TY_CODE' AND code=a.delng_ty_code) AS delng_ty_nm2
				, a.bcnc_sn
				, (SELECT bcnc_nm FROM bcnc WHERE ctmmny_sn=a.ctmmny_sn AND bcnc_sn=a.bcnc_sn) AS bcnc_nm
				, a.prdlst_se_code
				, (SELECT code_nm FROM code WHERE ctmmny_sn=1 AND parnts_code='PRDLST_SE_CODE' AND code=a.prdlst_se_code) AS prdlst_se_nm
				, a.model_no
				, IFNULL(a.dlnt, 0) AS dlnt
				, IFNULL(a.dlamt, 0) AS dlamt
				, IFNULL(a.dlnt, 0) * IFNULL(a.dlamt, 0) AS dlamtlnt
				, a.dlivy_de
				, a.dlivy_amt
				, a.dscnt_rt
				, a.cnnc_sn
				, m.dept_code
				, (SELECT code_nm FROM code WHERE ctmmny_sn=1 AND parnts_code='DEPT_CODE' AND code=m.dept_code) AS dept_nm
				, a.regist_dtm
				, a.register_id
				, a.update_dtm
				, a.updater_id
				, c.spt_nm
				FROM account a
				LEFT OUTER JOIN contract c
				ON a.ctmmny_sn=c.ctmmny_sn AND a.cntrct_sn=c.cntrct_sn
				LEFT OUTER JOIN member m
				ON m.mber_sn=c.bsn_chrg_sn
				WHERE 1=1
				AND a.ctmmny_sn = 1
				AND a.ddt_man BETWEEN '{0} 00:00:00' AND '{1} 23:59:59'
""".format(params['s_ddt_man_start'], params['s_ddt_man_end'])

    data = []
    if "s_delng_se_code" in params and params['s_delng_se_code']:
        query += " AND a.delng_se_code=%s"
        data.append(params["s_delng_se_code"])

    if "s_delng_ty_code1" in params and params['s_delng_ty_code1']:
        query += " AND a.delng_ty_code=%s"
        data.append(params["s_delng_ty_code1"])

    if "s_delng_ty_code2" in params and params['s_delng_ty_code2']:
        query += " AND a.delng_ty_code=%s"
        data.append(params["s_delng_ty_code2"])

    if "s_bcnc_sn" in params and params['s_bcnc_sn']:
        query += " AND a.bcnc_sn=%s"
        data.append(params["s_bcnc_sn"])

    if "s_dept_code" in params and params['s_dept_code']:
        query += " AND m.dept_code=%s"
        data.append(params["s_dept_code"])

    if "s_prdlst_se_code" in params and params['s_prdlst_se_code']:
        query += " AND a.prdlst_se_code=%s"
        data.append(params["s_prdlst_se_code"])

    if "s_model_no" in params and params['s_model_no']:
        query += " AND a.model_no=%s"
        data.append(params["s_model_no"])

    if "s_spt_nm" in params and params['s_spt_nm']:
        query += " AND c.spt_nm LIKE %s"
        data.append('%{}%'.format(params["s_spt_nm"]))


    return dt_query(query, data, params)

def get_sales_summary(params):
    query = """SELECT IFNULL(COUNT(a.delng_sn),0) AS total_count
				, IFNULL(SUM(IFNULL(a.dlnt, 0)*IFNULL(a.dlamt, 0)),0) AS total_amount
				FROM account a
				LEFT OUTER JOIN contract c
				ON a.ctmmny_sn=c.ctmmny_sn AND a.cntrct_sn=c.cntrct_sn
				WHERE 1=1
				AND a.ctmmny_sn = 1
				AND a.ddt_man BETWEEN '{0} 00:00:00' AND '{1} 23:59:59'
				""".format(params['s_ddt_man_start'], params['s_ddt_man_end'])

    data = []
    if "s_delng_se_code" in params and params['s_delng_se_code']:
        query += " AND a.delng_se_code=%s"
        data.append(params["s_delng_se_code"])

    if "s_delng_ty_code1" in params and params['s_delng_ty_code1']:
        query += " AND a.delng_ty_code=%s"
        data.append(params["s_delng_ty_code1"])

    if "s_delng_ty_code2" in params and params['s_delng_ty_code2']:
        query += " AND a.delng_ty_code=%s"
        data.append(params["s_delng_ty_code2"])

    if "s_bcnc_sn" in params and params['s_bcnc_sn']:
        query += " AND a.bcnc_sn=%s"
        data.append(params["s_bcnc_sn"])

    if "s_dept_code" in params and params['s_dept_code']:
        query += " AND m.dept_code=%s"
        data.append(params["s_dept_code"])

    if "s_prdlst_se_code" in params and params['s_prdlst_se_code']:
        query += " AND a.prdlst_se_code=%s"
        data.append(params["s_prdlst_se_code"])

    if "s_model_no" in params and params['s_model_no']:
        query += " AND a.model_no=%s"
        data.append(params["s_model_no"])

    if "s_spt_nm" in params and params['s_spt_nm']:
        query += " AND c.spt_nm LIKE %s"
        data.append('%{}%'.format(params["s_spt_nm"]))

    g.curs.execute(query, data)
    result = g.curs.fetchone()
    return result

def get_account_list(params):
    query = """SELECT a.ctmmny_sn
				, a.cntrct_sn
				, a.prjct_sn
				, a.delng_sn
				, a.delng_se_code
				, (SELECT code_nm FROM code WHERE ctmmny_sn=1 AND parnts_code='DELNG_SE_CODE' AND code=a.delng_se_code) AS delng_se_nm
				, a.ddt_man
				, a.delng_ty_code AS delng_ty_code1
				, (SELECT code_nm FROM code WHERE ctmmny_sn=1 AND parnts_code='CT_SE_CODE' AND code=a.delng_ty_code) AS delng_ty_nm1
				, a.delng_ty_code AS delng_ty_code2
				, (SELECT code_nm FROM code WHERE ctmmny_sn=1 AND parnts_code='SELNG_TY_CODE' AND code=a.delng_ty_code) AS delng_ty_nm2
				, a.bcnc_sn
				, (SELECT bcnc_nm FROM bcnc WHERE ctmmny_sn=a.ctmmny_sn AND bcnc_sn=a.bcnc_sn) AS bcnc_nm
				, a.prdlst_se_code
				, IFNULL((SELECT code_nm FROM code WHERE ctmmny_sn=1 AND parnts_code='PRDLST_SE_CODE' AND code=a.prdlst_se_code), '') AS prdlst_se_nm
				, IFNULL(a.model_no, '') AS model_no
				, a.dlnt
				, a.dlamt
				, a.dlivy_de
				, a.dlivy_amt
				, a.dscnt_rt
				, a.cnnc_sn
				, a.regist_dtm
				, a.register_id
				, a.update_dtm
				, a.updater_id
				, c.spt_nm
				FROM account a
				LEFT OUTER JOIN account s
				ON a.delng_sn = s.cnnc_sn
				LEFT OUTER JOIN contract c
				ON a.ctmmny_sn=c.ctmmny_sn AND a.cntrct_sn=c.cntrct_sn
				WHERE 1=1
				AND a.ctmmny_sn = 1
				AND a.cntrct_sn = %(s_cntrct_sn)s
				AND a.delng_se_code = 'P'
				AND s.cnnc_sn IS NULL
"""
    g.curs.execute(query, params)
    result = g.curs.fetchall()
    return result

def get_account_list2(params):
    query = """SELECT distinct a.delng_sn
				, a.delng_se_code
				, (SELECT code_nm FROM code WHERE ctmmny_sn=1 AND parnts_code='DELNG_SE_CODE' AND code=a.delng_se_code) AS delng_se_nm
				, a.ddt_man
				, a.delng_ty_code AS delng_ty_code1
				, (SELECT code_nm FROM code WHERE ctmmny_sn=1 AND parnts_code='CT_SE_CODE' AND code=a.delng_ty_code) AS delng_ty_nm1
				, a.delng_ty_code AS delng_ty_code2
				, (SELECT code_nm FROM code WHERE ctmmny_sn=1 AND parnts_code='SELNG_TY_CODE' AND code=a.delng_ty_code) AS delng_ty_nm2
				, a.bcnc_sn
				, (SELECT bcnc_nm FROM bcnc WHERE ctmmny_sn=a.ctmmny_sn AND bcnc_sn=a.bcnc_sn) AS bcnc_nm
				, a.prdlst_se_code
				, IFNULL((SELECT code_nm FROM code WHERE ctmmny_sn=1 AND parnts_code='PRDLST_SE_CODE' AND code=a.prdlst_se_code), '') AS prdlst_se_nm
				, IFNULL(a.model_no, '') AS model_no
				, a.dlnt
				, a.dlamt
				, a.dlivy_de
				, a.dlivy_amt
				, a.dscnt_rt
				, a.cnnc_sn
				, a.regist_dtm
				, a.register_id
				, a.update_dtm
				, a.updater_id
				FROM account a
				LEFT OUTER JOIN account s
				ON a.delng_sn = s.cnnc_sn
				WHERE 1=1
				AND a.delng_se_code = 'P'
				AND s.cnnc_sn IS NULL"""
    g.curs.execute(query)
    result = g.curs.fetchall()
    return result

def get_account(params):
    query = """SELECT a.ctmmny_sn
				, a.cntrct_sn
				, a.prjct_sn
				, a.delng_sn
				, a.delng_se_code
				, (SELECT code_nm FROM code WHERE ctmmny_sn=1 AND parnts_code='DELNG_SE_CODE' AND code=a.delng_se_code) AS delng_se_nm
				, a.ddt_man
				, a.delng_ty_code AS delng_ty_code1
				, (SELECT code_nm FROM code WHERE ctmmny_sn=1 AND parnts_code='PUCHAS_TY_CODE' AND code=a.delng_ty_code) AS delng_ty_nm1
				, a.delng_ty_code AS delng_ty_code2
				, (SELECT code_nm FROM code WHERE ctmmny_sn=1 AND parnts_code='SELNG_TY_CODE' AND code=a.delng_ty_code) AS delng_ty_nm2
				, a.bcnc_sn
				, (SELECT bcnc_nm FROM bcnc WHERE ctmmny_sn=a.ctmmny_sn AND bcnc_sn=a.bcnc_sn) AS bcnc_nm
				, a.prdlst_se_code
				, (SELECT code_nm FROM code WHERE ctmmny_sn=1 AND parnts_code='PRDLST_SE_CODE' AND code=a.prdlst_se_code) AS prdlst_se_nm
				, a.model_no
				, IFNULL(a.dlnt, 0) AS dlnt
				, IFNULL(a.dlamt, 0) AS dlamt
				, a.wrhousng_de
				, a.dlivy_de
				, a.expect_de
				, a.dlivy_amt
				, a.dscnt_rt
				, a.add_dscnt_rt
				, a.rm
				, a.cnnc_sn
				, a.regist_dtm
				, a.register_id
				, a.update_dtm
				, a.updater_id
				, c.spt_nm
				FROM account a
				LEFT OUTER JOIN contract c
				ON a.ctmmny_sn=c.ctmmny_sn AND a.cntrct_sn=c.cntrct_sn
				WHERE 1=1
				AND a.ctmmny_sn = 1
				AND a.delng_sn = %(s_delng_sn)s
"""
    g.curs.execute(query, params)
    result = g.curs.fetchone()
    return result


def insert_account(params):
    data = OrderedDict()
    for key in params:
        if key not in ("item_sn[]", "invn_sttus_code", "prduct_se_code", "prduct_ty_code", "use_type"):
            if params[key] != '':
                data[key] = params[key]
    if "ctmmny_sn" not in data:
        data["ctmmny_sn"] = 1

    if "regist_dtm" not in data:
        data["regist_dtm"] = datetime.datetime.now()

    if "register_id" not in data:
        data["register_id"] = session["member"]["member_id"]
    print(data)
    sub_query = [key for key in data]
    params_query = ["%({})s".format(key) for key in data]

    query = """INSERT INTO account({}) VALUES ({})""".format(",".join(sub_query), ",".join(params_query))
    g.curs.execute(query, data)
    return g.curs.lastrowid

def update_account(params):
    data = OrderedDict()

    for key in params:
        if key not in ("s_delng_sn", "item_sn[]", "invn_sttus_code", "prduct_se_code", "prduct_ty_code"):
            if params[key] != '':
                data[key] = params[key]

    if "ctmmny_sn" not in params:
        params["ctmmny_sn"] = 1

    if "update_dtm" not in params:
        params["update_dtm"] = datetime.datetime.now()

    if "updater_id" not in params:
        params["updater_id"] = session["member"]["member_id"]

    sub_query = ["{0}=%({0})s".format(key) for key in data]
    query = """UPDATE account SET {} WHERE delng_sn=%(s_delng_sn)s""".format(",".join(sub_query))
    g.curs.execute(query, params)

def delete_account(params):
    query = """DELETE FROM account WHERE 1=1 AND delng_sn=%(s_delng_sn)s"""
    g.curs.execute(query, params)

def get_account_report(params):
    query = """SELECT p.bcnc_sn AS p_bcnc_sn
				, (SELECT CONCAT(esntl_delng_no) FROM bcnc WHERE bcnc_sn=p.bcnc_sn) AS p_bcnc_nm
				, p.model_no AS p_model_no
				, p.dlnt AS p_dlnt
				, p.dlamt AS p_dlamt
				, (p.dlnt * p.dlamt) AS p_dlamt_sum
				, s.bcnc_sn AS s_bcnc_sn
				, (SELECT bcnc_nm FROM bcnc WHERE bcnc_sn=s.bcnc_sn) AS s_bcnc_nm
				, s.cntrct_sn AS s_cntrct
				, (SELECT spt_nm FROM contract WHERE ctmmny_sn=s.ctmmny_sn AND cntrct_sn=s.cntrct_sn) AS s_spt_nm
				, s.model_no AS s_model_no
				, s.dlnt AS s_dlnt
				, s.dlamt AS s_dlamt
				, (s.dlnt * s.dlamt) AS s_dlamt_sum
				, s.delng_ty_code AS s_delng_ty_code
				, s.delng_sn AS s_delng_sn
				, (SELECT m.dept_code FROM contract c LEFT OUTER JOIN member m ON m.mber_sn = c.bsn_chrg_sn WHERE c.cntrct_sn=s.cntrct_sn) AS dept_code
				, (SELECT code_nm FROM code WHERE ctmmny_sn=1 AND parnts_code='DEPT_CODE' AND code=dept_code) AS dept_nm
				FROM account p
				LEFT JOIN account s
				ON p.ctmmny_sn=s.ctmmny_sn AND p.cntrct_sn=s.cntrct_sn AND p.delng_sn = s.cnnc_sn AND s.ddt_man=%(s_ddt_man)s
				WHERE p.ctmmny_sn = 1
				AND p.ddt_man = %(s_ddt_man)s
				AND p.delng_se_code = 'P'
				UNION
				SELECT p.bcnc_sn AS p_bcnc_sn
				, (SELECT CONCAT(esntl_delng_no) FROM bcnc WHERE bcnc_sn=p.bcnc_sn) AS p_bcnc_nm
				, p.model_no AS p_model_no
				, p.dlnt AS p_dlnt
				, p.dlamt AS p_dlamt
				, (p.dlnt * p.dlamt) AS p_dlamt_sum
				, s.bcnc_sn AS s_bcnc_sn
				, (SELECT bcnc_nm FROM bcnc WHERE bcnc_sn=s.bcnc_sn) AS s_bcnc_nm
				, s.cntrct_sn AS s_cntrct
				, (SELECT spt_nm FROM contract WHERE ctmmny_sn=s.ctmmny_sn AND cntrct_sn=s.cntrct_sn) AS s_spt_nm
				, s.model_no AS s_model_no
				, s.dlnt AS s_dlnt
				, s.dlamt AS s_dlamt
				, (s.dlnt * s.dlamt) AS s_dlamt_sum
				, s.delng_ty_code AS s_delng_ty_code
				, s.delng_sn AS s_delng_sn
				, (SELECT m.dept_code FROM contract c LEFT OUTER JOIN member m ON m.mber_sn = c.bsn_chrg_sn WHERE c.cntrct_sn=s.cntrct_sn) AS dept_code
				, (SELECT code_nm FROM code WHERE ctmmny_sn=1 AND parnts_code='DEPT_CODE' AND code=dept_code) AS dept_nm
				FROM account p
				RIGHT JOIN account s
				ON p.ctmmny_sn=s.ctmmny_sn AND p.cntrct_sn=s.cntrct_sn AND p.delng_sn = s.cnnc_sn AND p.ddt_man=%(s_ddt_man)s
				WHERE s.ctmmny_sn = 1
				AND s.ddt_man = %(s_ddt_man)s
				AND s.delng_se_code = 'S'
				AND p.delng_sn IS NULL
            """
    g.curs.execute(query, params)
    result = g.curs.fetchall()
    return result

def get_p_account_list(params):
    params['s_start_ddt_man'] = datetime.datetime.strptime(params["s_ddt_man"], "%Y-%m-%d").strftime("%Y-%m-01")
    params['s_end_ddt_man'] = params['s_ddt_man']
    query = """SELECT b.esntl_delng_no
				, CASE b.esntl_delng_no
				WHEN '' THEN '타사매입'
				ELSE MAX(b.bcnc_nm)
				END AS esntl_delng_nm
				, SUM(a.dlnt * a.dlamt) AS dlamt
				FROM account a
				LEFT JOIN bcnc b
				ON a.ctmmny_sn=b.ctmmny_sn AND a.bcnc_sn=b.bcnc_sn
				WHERE a.ctmmny_sn = 1
				AND a.ddt_man BETWEEN %(s_start_ddt_man)s AND %(s_end_ddt_man)s
				AND a.delng_se_code = 'P'
				GROUP BY b.esntl_delng_no
				ORDER BY b.esntl_delng_no DESC"""
    g.curs.execute(query, params)
    result = g.curs.fetchall()
    return result

def get_s_account_list(params):
    params['s_start_ddt_man'] = datetime.datetime.strptime(params["s_ddt_man"], "%Y-%m-%d").strftime("%Y-%m-01")
    params['s_end_ddt_man'] = params['s_ddt_man']
    query = """SELECT a.delng_ty_code
				, c.code_nm AS delng_ty_nm
				, SUM(a.dlnt * a.dlamt) AS dlamt
				FROM account a
				LEFT JOIN code c
				ON c.parnts_code='SELNG_TY_CODE' AND c.code=a.delng_ty_code
				WHERE a.ctmmny_sn = 1
				AND a.ddt_man BETWEEN %(s_start_ddt_man)s AND %(s_end_ddt_man)s
				AND a.delng_se_code = 'S'
				GROUP BY a.delng_ty_code, c.code_nm
				ORDER BY c.code_ordr"""
    g.curs.execute(query, params)
    result = g.curs.fetchall()
    return result


def get_expect_s_list(params):

    query = """SELECT GROUP_CONCAT(s.delng_sn) AS delng_sn
            , DATE_FORMAT(s.dlivy_de, '%%y-%%m') AS dlivy_de
            , s.bcnc_sn AS bcnc_sn
            , s.cntrct_sn AS cntrct_sn
            , s.expect_de AS expect_de
            , (SELECT spt_nm FROM contract WHERE cntrct_sn=s.cntrct_sn) AS cntrct_nm
            , (SELECT m.dept_code FROM contract c LEFT OUTER JOIN member m ON m.mber_sn = c.bsn_chrg_sn WHERE c.cntrct_sn=s.cntrct_sn) AS dept_code
            , (SELECT code_nm FROM code WHERE ctmmny_sn=1 AND parnts_code='DEPT_CODE' AND code=dept_code) AS dept_nm
            , (SELECT bcnc_nm FROM bcnc WHERE bcnc_sn=s.bcnc_sn) AS bcnc_nm
            , SUM(IFNULL(IF(p.delng_ty_code IN ('1', '2'), s.dlnt*s.dlamt, 0), 0)) AS price_1
            , SUM(IFNULL(IF(p.delng_ty_code IN ('3', '4'), s.dlnt*s.dlamt, 0), 0)) AS price_2"""
    if "expect_de" in params:
        ymd = params['expect_de']
        y, m, d = ymd.split("-")
        _, l = calendar.monthrange(int(y), int(m))
        f = 1
        first_day = "{}-{}-{}".format(y.zfill(4), m.zfill(2), str(f).zfill(2))
        last_day = "{}-{}-{}".format(y.zfill(4), m.zfill(2), str(l).zfill(2))
        query += " FROM (SELECT * FROM account WHERE delng_se_code='S' AND delng_ty_code='12' AND expect_de BETWEEN '{0} 00:00:00' AND '{1} 23:59:59') s ".format(first_day, last_day)

    else:
        query += " FROM (SELECT * FROM account WHERE delng_se_code='S' AND delng_ty_code='12' AND expect_de > '0000-00-00') s "
    query += """ LEFT JOIN (SELECT * FROM account WHERE delng_se_code='P') p 
            ON s.cnnc_sn=p.delng_sn
            WHERE 1=1
            GROUP BY DATE_FORMAT(s.dlivy_de, '%%y-%%m'), s.bcnc_sn, s.cntrct_sn
            ORDER BY dlivy_de ASC
            """
    g.curs.execute(query)
    result = g.curs.fetchall()
    return result

def get_expect_t_list(params):

    query = """SELECT GROUP_CONCAT(t.taxbil_sn) AS taxbil_sn
            , t.taxbil_yn AS taxbil_yn
            , t.pblicte_trget_sn AS bcnc_sn
            , DATE_FORMAT(t.pblicte_de, '%%y-%%m') AS dlivy_de
            , t.collct_de AS expect_de
            , t.cntrct_sn AS cntrct_sn
            , (SELECT spt_nm FROM contract WHERE cntrct_sn=t.cntrct_sn) AS cntrct_nm
            , (SELECT m.dept_code FROM contract c LEFT OUTER JOIN member m ON m.mber_sn = c.bsn_chrg_sn WHERE c.cntrct_sn=t.cntrct_sn) AS dept_code
            , (SELECT code_nm FROM code WHERE ctmmny_sn=1 AND parnts_code='DEPT_CODE' AND code=dept_code) AS dept_nm
            , (SELECT bcnc_nm FROM bcnc WHERE bcnc_sn=t.pblicte_trget_sn) AS bcnc_nm
            , (SELECT code_nm FROM code WHERE parnts_code='DELNG_SE_CODE' AND code=t.delng_se_code) AS delng_se_nm
            , SUM(t.splpc_am + IFNULL(t.vat, 0)) AS price_total
            FROM taxbil t
            WHERE 1=1
            AND t.delng_se_code LIKE 'S%%' """
    if "expect_de" in params:
        ymd = params['expect_de']
        y, m, d = ymd.split("-")
        _, l = calendar.monthrange(int(y), int(m))
        f = 1
        first_day = "{}-{}-{}".format(y.zfill(4), m.zfill(2), str(f).zfill(2))
        last_day = "{}-{}-{}".format(y.zfill(4), m.zfill(2), str(l).zfill(2))

        query += " AND t.collct_de BETWEEN '{0} 00:00:00' AND '{1} 23:59:59' ".format(first_day, last_day)
    else:
        query += " AND t.collct_de > '0000-00-00' "


    query += """ GROUP BY t.cntrct_sn, t.pblicte_trget_sn, t.collct_de
            """
    g.curs.execute(query)
    result = g.curs.fetchall()
    return result

def get_expect_r_list(params):
    query = """SELECT t.taxbil_sn AS taxbil_sn
            , r.rcppay_de AS rcppay_de
            , r.amount AS amount
            FROM (SELECT * FROM rcppay WHERE acntctgr_code IN ('108', '110', '501') AND rcppay_se_code IN ('I', 'I1', 'I2', 'I3')) r """
    if "expect_de" in params:
        ymd = params['expect_de']
        y, m, d = ymd.split("-")
        _, l = calendar.monthrange(int(y), int(m))
        f = 1
        first_day = "{}-{}-{}".format(y.zfill(4), m.zfill(2), str(f).zfill(2))
        last_day = "{}-{}-{}".format(y.zfill(4), m.zfill(2), str(l).zfill(2))

        query += " LEFT JOIN (SELECT * FROM taxbil WHERE delng_se_code LIKE 'S%%' AND collct_de BETWEEN '{0} 00:00:00' AND '{1} 23:59:59') t ".format(first_day, last_day)
    else:
        query += " LEFT JOIN (SELECT * FROM taxbil WHERE delng_se_code LIKE 'S%%' AND collct_de > '0000-00-00') t "

    query += """ ON r.cntrct_sn = t.cntrct_sn AND r.prvent_sn = t.pblicte_trget_sn AND t.taxbil_sn = r.cnnc_sn
            WHERE 1=1
            AND t.collct_de > '0000-00-00'
            UNION
            SELECT taxbil_sn AS taxbil_sn
            , rcppay_de AS rcppay_de
            , amount
            FROM direct
            WHERE 1=1
            """
    g.curs.execute(query)
    result = g.curs.fetchall()
    return result

def get_expect_p_t_list(params):
    ymd = params['expect_de']
    y, m, d = ymd.split("-")
    _, l = calendar.monthrange(int(y), int(m))
    f = 1
    first_day = "{}-{}-{}".format(y.zfill(4), m.zfill(2), str(f).zfill(2))
    last_day = "{}-{}-{}".format(y.zfill(4), m.zfill(2), str(l).zfill(2))

    query = """SELECT GROUP_CONCAT(t.taxbil_sn) AS taxbil_sn
            , t.taxbil_yn AS taxbil_yn
            , t.pblicte_trget_sn AS bcnc_sn
            , DATE_FORMAT(t.pblicte_de, '%%y-%%m') AS dlivy_de
            , t.collct_de AS expect_de
            , t.cntrct_sn AS cntrct_sn
            , (SELECT spt_nm FROM contract WHERE cntrct_sn=t.cntrct_sn) AS cntrct_nm
            , (SELECT bcnc_nm FROM bcnc WHERE bcnc_sn=t.pblicte_trget_sn) AS bcnc_nm
            , SUM(t.splpc_am + IFNULL(t.vat, 0)) AS price_total
            FROM taxbil t
            WHERE 1=1
            AND t.delng_se_code LIKE 'P%%'
            AND t.collct_de BETWEEN '{0} 00:00:00' AND '{1} 23:59:59'
            GROUP BY t.cntrct_sn, t.pblicte_trget_sn, t.collct_de
            """.format(first_day, last_day)
    g.curs.execute(query)
    result = g.curs.fetchall()
    return result

def get_expect_p_r_list(params):
    ymd = params['expect_de']
    y, m, d = ymd.split("-")
    _, l = calendar.monthrange(int(y), int(m))
    f = 1
    first_day = "{}-{}-{}".format(y.zfill(4), m.zfill(2), str(f).zfill(2))
    last_day = "{}-{}-{}".format(y.zfill(4), m.zfill(2), str(l).zfill(2))

    query = """SELECT t.taxbil_sn AS taxbil_sn
            , r.rcppay_de AS rcppay_de
            , r.amount AS amount
            FROM (SELECT * FROM rcppay WHERE acntctgr_code IN ('638', '146', '624', '501') AND rcppay_se_code IN ('O')) r
            LEFT JOIN (SELECT * FROM taxbil WHERE delng_se_code LIKE 'P%%' AND collct_de BETWEEN '{0} 00:00:00' AND '{1} 23:59:59') t
            ON r.cntrct_sn = t.cntrct_sn AND r.prvent_sn = t.pblicte_trget_sn AND t.taxbil_sn = r.cnnc_sn
            WHERE 1=1
            AND t.collct_de >= '{0} 00:00:00'
            """.format(first_day, last_day)
    g.curs.execute(query)
    result = g.curs.fetchall()
    return result


def insert_ms_equip(params):
    if params['msh_approval_type'] == 'S':
        cntrct_sn = params["cntrct_sn"]
        prjct = get_project_by_cntrct_nm(params["cntrct_sn"])
        prjct_sn = prjct['prjct_sn']
        ddt_man = datetime.datetime.now()
        data = OrderedDict()
        for key in params:
            if key.endswith("[]"):
                if key in ("dlamt[]", "dlnt[]"):
                    data[key.replace("[]", "")] = [int(d.replace(",", "")) for d in params[key]]
                elif key in ("expect_de[]", ):
                    data["wrhousng_de"] = params[key]
                else:
                    data[key.replace("[]", "")] = params[key]
        input_data = []
        for i, key in enumerate(data):
            if i == 0:
                for row in data[key]:
                    input_data.append({key : row})
            else:
                for j, row in enumerate(data[key]):
                    input_data[j][key] = row
        for row in input_data:
            row['cntrct_sn'] = cntrct_sn
            row['prjct_sn'] = prjct_sn
            row['ctmmny_sn'] = 1
            row['regist_dtm'] = datetime.datetime.now()
            row['register_id'] = session['member']['member_id']
            row['delng_se_code'] = 'P'
            row['ddt_man'] = datetime.datetime.now()

        sub_query = [key for key in input_data[0]]
        params_query = ["%({})s".format(key) for key in input_data[0]]

        query = """INSERT INTO account({}) VALUES ({})""".format(",".join(sub_query), ",".join(params_query))
        g.curs.executemany(query, input_data)



        # sub_query = [key for key in data]
        # params_query = ["%({})s".format(key) for key in data]
