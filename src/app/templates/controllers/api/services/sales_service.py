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

def get_sales_approval_datatable(params):
    query = """SELECT IFNULL(dlivy_de, '') AS dlivy_de
                    , eq_sn
                    , order_de
                    , prdlst_se_code
                    , (SELECT code_nm FROM code WHERE parnts_code='PRDLST_SE_CODE' AND code=e.prdlst_se_code) AS prdlst_se_nm
                    , model_no
                    , cntrct_sn
                    , (SELECT spt_nm FROM contract WHERE cntrct_sn=e.cntrct_sn) AS spt_nm
                    , dlnt
                    , pamt
                    , bcnc_sn
                    , (SELECT bcnc_nm FROM bcnc WHERE bcnc_sn=e.bcnc_sn) AS bcnc_nm
                    FROM equipment e
                    WHERE 1=1
                    AND ((e.dlivy_de BETWEEN '{0} 00:00:00' AND '{1} 23:59:59') or e.dlivy_de IS NULL)
                    """.format(params['s_ddt_man_start'], params['s_ddt_man_end'])
    data = []
    if "s_bcnc_sn" in params and params['s_bcnc_sn']:
        query += " AND a.bcnc_sn=%s"
        data.append(params["s_bcnc_sn"])

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
        if key not in ("s_delng_sn", "item_sn[]", "invn_sttus_code", "prduct_se_code", "prduct_ty_code", "use_type"):
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

def insert_ms_BF_equip(params):
    if params['msh_approval_type'] in ('S', 'B'):
        params['regist_dtm'] = datetime.datetime.now()
        params['register_id'] = session['member']['member_id']
        cntrct_sn = params["cntrct_sn"]
        if params['msh_approval_type'] == 'S':
            g.curs.execute(
                "UPDATE contract SET mh_place=%s, mh_count=%s, mh_period=%s, mh_approval_step=1 WHERE cntrct_sn=%s",
                (params['mh_place'], params['mh_count'], params['mh_period'], cntrct_sn))
        else:
            g.curs.execute(
                "SELECT delng_sn FROM account WHERE cntrct_sn=%(cntrct_sn)s AND (delng_se_code='P' and delng_ty_code IN ('61', '62', '64', '65')) OR cnnc_sn IN (SELECT delng_sn FROM account WHERE delng_se_code='P' and delng_ty_code IN ('61', '62', '64', '65') AND cntrct_sn=%(cntrct_sn)s)",
                params)
            accounts = g.curs.fetchall()
            delng_sns = [acc['delng_sn'] for acc in accounts]
            for delng_sn in delng_sns:
                delete_account({"s_delng_sn": delng_sn})

            g.curs.execute("SELECT log_sn, stock_sn, cnnc_sn FROM stock_log WHERE delng_sn IN ({})".format(
                ",".join(['%s'] * len(delng_sns))), delng_sns)
            stocks = g.curs.fetchall(transform=False)
            for stock in stocks:
                if stock['cnnc_sn'] is None:
                    g.curs.execute("DELETE FROM stock WHERE stock_sn=%s", stock['stock_sn'])
                g.curs.execute("DELETE FROM stock_log WHERE log_sn=%s", stock['log_sn'])

            g.curs.execute("UPDATE contract SET mh_place=%s, mh_count=%s, mh_period=%s WHERE cntrct_sn=%s",
                           (params['mh_place'], params['mh_count'], params['mh_period'], cntrct_sn))

        prjct = get_project_by_cntrct_nm(params["cntrct_sn"])
        prjct_sn = prjct['prjct_sn']
        ddt_man = datetime.datetime.now()
        data = OrderedDict()
        for key in params:
            if key.endswith("[]"):
                if key == "pamount[]":
                    data["dlamt"] = [int(d.replace(",", "")) for d in params[key]]
                elif key == "dlivy_amt[]":
                    data["dlivy_amt"] = [int(d.replace(",", "")) for d in params[key]]
                elif key == "dc[]":
                    data["add_dscnt_rt"] = [int(dc.replace(",", "")) * 100.0 / (int(qy.replace(",", "")) * int(dlivy_amt.replace(",", ""))) if int(dlivy_amt.replace(",", "")) != 0 else 0 for dc, qy, dlivy_amt in zip(params["dc[]"], params["qy[]"], params["dlivy_amt[]"])]
                elif key == "qy[]":
                    data["dlnt"] = [int(d.replace(",", "")) for d in params[key]]
                elif key == "dc_rate[]":
                    data["dscnt_rt"] = [float(d.replace("%", "")) for d in params[key] ]
                elif key in ("expect_de[]",):
                    data["wrhousng_de"] = params[key]
                elif key in ("delng_sn[]", "prduct_ty_code[]", "stock_sn[]", "return_de[]", "return_dlnt[]", "stock_place[]"):
                    continue
                else:
                    data[key.replace("[]", "")] = params[key]

        input_data = []
        for i, key in enumerate(data):
            if i == 0:
                for row in data[key]:
                    input_data.append({key: row})
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
        delng_sns = []
        for i in input_data:
            g.curs.execute(query, i)
            delng_sn = g.curs.lastrowid
            delng_sns.append(delng_sn)
        for row in input_data:
            query = """INSERT INTO cost(cntrct_sn, prjct_sn, cntrct_execut_code, ct_se_code, purchsofc_sn, model_no, qy, puchas_amount, dscnt_rt, add_dscnt_rt, cost_date, extra_sn, regist_dtm, register_id, dspy_se_code)
                        VALUES (%(cntrct_sn)s, %(prjct_sn)s, 'E', %(delng_ty_code)s, %(bcnc_sn)s, %(model_no)s, %(dlnt)s, %(b61)s, 0.0, %(add_dscnt_rt)s ,'0000-00-00', 0, %(regist_dtm)s, %(register_id)s, %(dspy_se_code)s)"""
            row['b61'] = row['dlamt'] * row['dlnt']
            row['dspy_se_code'] = 1 if int(row['delng_ty_code']) in (61, 62) else 2
            g.curs.execute(query, row)

        return delng_sns
    else:
        cntrct_sn = params["cntrct_sn"]
        g.curs.execute("UPDATE contract SET mh_approval_step=2 WHERE cntrct_sn=%s", (cntrct_sn,))


def insert_ms_equip(params):
    if params['msh_approval_type'] in ('S', 'B'):

        cntrct_sn = params["cntrct_sn"]
        if params['msh_approval_type'] == 'S':
            g.curs.execute("UPDATE contract SET mh_place=%s, mh_count=%s, mh_period=%s, mh_approval_step=1 WHERE cntrct_sn=%s", (params['mh_place'], params['mh_count'], params['mh_period'], cntrct_sn))
        else:
            g.curs.execute("SELECT delng_sn FROM account WHERE cntrct_sn=%(cntrct_sn)s AND (delng_se_code='P' and delng_ty_code IN ('61', '62')) OR cnnc_sn IN (SELECT delng_sn FROM account WHERE delng_se_code='P' and delng_ty_code IN ('61', '62') AND cntrct_sn=%(cntrct_sn)s)", params)
            accounts = g.curs.fetchall()
            delng_sns = [acc['delng_sn'] for acc in accounts]
            for delng_sn in delng_sns:
                delete_account({"s_delng_sn" : delng_sn})

            g.curs.execute("SELECT log_sn, stock_sn, cnnc_sn FROM stock_log WHERE delng_sn IN ({})".format(",".join(['%s']*len(delng_sns))), delng_sns)
            stocks = g.curs.fetchall(transform=False)
            for stock in stocks:
                if stock['cnnc_sn'] is None:
                    g.curs.execute("DELETE FROM stock WHERE stock_sn=%s", stock['stock_sn'])
                g.curs.execute("DELETE FROM stock_log WHERE log_sn=%s", stock['log_sn'])

            g.curs.execute("UPDATE contract SET mh_place=%s, mh_count=%s, mh_period=%s WHERE cntrct_sn=%s", (params['mh_place'], params['mh_count'], params['mh_period'], cntrct_sn))

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
                elif key in ("delng_sn[]", "prduct_ty_code[]"):
                    continue
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
            if 'delng_ty_code' not in row or row['delng_ty_code'] == '':
                row['delng_ty_code'] = '61'

        sub_query = [key for key in input_data[0]]
        params_query = ["%({})s".format(key) for key in input_data[0]]

        query = """INSERT INTO account({}) VALUES ({})""".format(",".join(sub_query), ",".join(params_query))
        delng_sns = []
        for i in input_data:
            g.curs.execute(query, i)
            delng_sn = g.curs.lastrowid
            delng_sns.append(delng_sn)
        return delng_sns
    else:
        cntrct_sn = params["cntrct_sn"]
        g.curs.execute("UPDATE contract SET mh_approval_step=2 WHERE cntrct_sn=%s", (cntrct_sn, ))


        # sub_query = [key for key in data]
        # params_query = ["%({})s".format(key) for key in data]

def insert_equipment_sub(params):
    data = OrderedDict()
    data['cntrct_sn'] = params['cntrct_sn']
    order_des = params['order_de[]']
    prdlst_se_codes = params['prdlst_se_code[]']
    damts = params['damt[]']
    damt2s = params['damt2[]']
    bcnc_sns = params['bcnc_sn[]']
    for order_de, prdlst_se_code, pamt, samt, bcnc_sn in zip(order_des, prdlst_se_codes, damts, damt2s, bcnc_sns):
        data['order_de'] = order_de
        data['prdlst_se_code'] = prdlst_se_code
        data['model_no'] = '자재'
        data['dlnt'] = 1
        data['pamt'] = int(pamt.replace(",", "")) if pamt != '' else None
        data['samt'] = int(samt.replace(",", "")) if samt != '' else None
        data['bcnc_sn'] = bcnc_sn
        g.curs.execute("INSERT INTO equipment({}) VALUES ({})".format(",".join([key for key in data.keys()]), ",".join(["%({})s".format(key) for key in data.keys()])), data)

def get_model_list(params):
    query = """SELECT p.delng_sn
                    , p.bcnc_sn
                    , p.prdlst_se_code
                    , p.model_no
                    , p.dlnt
                    , p.dlamt
                    , p.wrhousng_de
                    , p.delng_ty_code
                    , p.add_dscnt_rt
                    , (SELECT prduct_ty_code FROM stock WHERE stock_sn=sl.stock_sn) AS prduct_ty_code
                    , IFNULL(s.dlivy_de, '') AS dlivy_de
                    FROM account p
                    LEFT OUTER JOIN account s
                    ON s.cnnc_sn=p.delng_sn
                    LEFT OUTER JOIN (SELECT x.delng_sn, MAX(x.stock_sn) AS stock_sn FROM stock_log x INNER JOIN (SELECT stock_sn, MIN(log_sn) AS m_log_sn FROM stock_log GROUP BY delng_sn) y ON x.stock_sn=y.stock_sn AND x.log_sn=y.m_log_sn GROUP BY delng_sn) sl
                    ON sl.delng_sn=p.delng_sn
                    WHERE 1=1

                    AND p.delng_se_code='P'
                    AND p.cntrct_sn=%(s_cntrct_sn)s
                    AND p.delng_ty_code IN ('61', '62', '64', '65')
                    """
    g.curs.execute(query, params)
    result = g.curs.fetchall()
    return result

def insert_equipment_other_sub(params):
    data = OrderedDict()
    data['cntrct_sn'] = params['cntrct_sn']
    order_des = params['order_de[]']
    model_nos = params['model_no[]']
    prdlst_se_codes = params['prdlst_se_code[]']
    dlnts = params['dlnt[]']
    damts = params['damt[]']
    bcnc_sns = params['bcnc_sn[]']
    for order_de, model_no, prdlst_se_code, damt, dlnt, bcnc_sn in zip(order_des, model_nos, prdlst_se_codes, damts, dlnts, bcnc_sns):
        data['order_de'] = order_de
        data['prdlst_se_code'] = prdlst_se_code
        data['model_no'] = '자재'
        data['dlnt'] = dlnt
        data['pamt'] = int(damt.replace(",", ""))*dlnt if damt != '' else None
        data['samt'] = data['pamt']
        data['bcnc_sn'] = bcnc_sn
        g.curs.execute("INSERT INTO equipment({}) VALUES ({})".format(",".join([key for key in data.keys()]), ",".join(["%({})s".format(key) for key in data.keys()])), data)


def update_equipment_establish(params):
    prjct = get_project_by_cntrct_nm(params["cntrct_sn"])
    company = {}
    for key in params:
        if key.startswith("company"):
            if key.split("_")[0] not in company:
                company[key.split("_")[0]] = dict()
            company[key.split("_")[0]]["_".join(key.split("_")[1:])] = params[key]
    print(company)
    for idx, c in company.items():
        if idx.replace("company", "") == '':
            continue
        if c['name'] == '':
            continue

        if c['date'] == '':
            c['date'] = None
        c['cntrct_sn'] = params['cntrct_sn']
        c['prjct_sn'] = prjct['prjct_sn']
        human = c['human'].replace(",", "")
        direct = c['direct'].replace(",", "")
        daily = c['daily'].replace(",", "")
        s = c['sum'].replace(",", "")
        human = int(human) if human != '' else 0
        direct = int(direct) if direct != '' else 0
        daily = int(daily) if daily != '' else 0
        s = int(s) if s != '' else 0

        c['pymnt_mth'] = "{}-{}-{}-{}".format(human, direct, daily, s)

        human = c['human_change'].replace(",", "")
        direct = c['direct_change'].replace(",", "")
        daily = c['daily_change'].replace(",", "")
        s = c['sum_change'].replace(",", "")
        human = int(human) if human != '' else 0
        direct = int(direct) if direct != '' else 0
        daily = int(daily) if daily != '' else 0
        s = int(s) if s != '' else 0

        c['outsrc_dtls'] = "{}-{}-{}-{}".format(human, direct, daily, s)
        query = """SELECT outsrc_sn FROM outsrc WHERE cntrct_sn=%(cntrct_sn)s AND prjct_sn=%(prjct_sn)s"""
        g.curs.execute(query, c)
        outsrcs = g.curs.fetchall()
        if int(idx.replace("company", ""))-1 < len(outsrcs):
            outsrc = outsrcs[int(idx.replace("company", ""))-1]
            c['outsrc_sn'] = outsrc['outsrc_sn']

            query = """UPDATE outsrc SET outsrc_fo_sn=%(name)s, cntrct_de=%(date)s, pymnt_mth=%(pymnt_mth)s, outsrc_dtls=%(outsrc_dtls)s, rspnber_nm=%(owner)s, rspnber_telno=%(owner_telno)s, charger_nm=%(dam)s, charger_telno=%(dam_telno)s WHERE outsrc_sn=%(outsrc_sn)s"""

            g.curs.execute(query, c)
            outsrc_sn = outsrc['outsrc_sn']
            query = """DELETE FROM outsrc_item WHERE outsrc_sn=%s"""
            g.curs.execute(query, (outsrc_sn, ))
            for item_nm, item_dlnt, item_damt in zip(c['item_name[]'], c['item_dlnt[]'], c['item_damt[]']):
                if item_nm != '':
                    dlnt = int(item_dlnt.replace(",", ""))
                    damt = int(item_damt.replace(",", ""))
                    query = """INSERT INTO outsrc_item(outsrc_sn, item_nm, item_dlnt, item_damt) VALUES (%s, %s, %s, %s)"""
                    g.curs.execute(query, (outsrc_sn, item_nm, dlnt, damt))
        else:
            c['register_id'] = session['member']['member_id']
            query = """INSERT INTO outsrc(cntrct_sn, prjct_sn, outsrc_fo_sn, cntrct_de, pymnt_mth, rspnber_nm, rspnber_telno, charger_nm, charger_telno, regist_dtm, register_id)
                        VALUES(%(cntrct_sn)s, %(prjct_sn)s, %(name)s, %(date)s, %(pymnt_mth)s, %(owner)s, %(owner_telno)s, %(dam)s, %(dam_telno)s, NOW(), %(register_id)s)"""
            g.curs.execute(query, c)
            outsrc_sn = g.curs.lastrowid

            for item_nm, item_dlnt, item_damt in zip(c['item_name[]'], c['item_dlnt[]'], c['item_damt[]']):
                if item_nm != '':
                    dlnt = int(item_dlnt.replace(",", ""))
                    damt = int(item_damt.replace(",", ""))
                    query = """INSERT INTO outsrc_item(outsrc_sn, item_nm, item_dlnt, item_damt) VALUES (%s, %s, %s, %s)"""
                    g.curs.execute(query, (outsrc_sn, item_nm, dlnt, damt))


def insert_equipment(params):
    cost_data = []
    prjct = get_project_by_cntrct_nm(params["cntrct_sn"])
    for key in params:
        if key.endswith("[]"):
            continue

        elif key.startswith("E_") and not key.endswith("_alpha"):
            cntrct_execut_code, ct_se_code  = key.split("_")
            value = params[key].replace(",", "")
            if value == '':
                continue
            column = "puchas_amount" if cntrct_execut_code == 'E' else "salamt"
            cost_data.append({"cntrct_sn" : params["cntrct_sn"], "prjct_sn" : prjct["prjct_sn"], "cntrct_execut_code" : cntrct_execut_code, "ct_se_code" : ct_se_code, "qy" : 1, column : int(value), "extra_sn" : 0, "regist_dtm" : datetime.datetime.now(), "register_id" : session["member"]["member_id"]})


    for data in cost_data:
        sub_query = [key for key in data]
        params_query = ["%({})s".format(key) for key in data]

        query = """INSERT INTO cost({}) VALUES ({})""".format(",".join(sub_query), ",".join(params_query))
        g.curs.execute(query, data)


    company = {}
    for key in params:
        if key.startswith("company"):
            if key.split("_")[0] not in company:
                company[key.split("_")[0]] = dict()
            company[key.split("_")[0]]["_".join(key.split("_")[1:])] = params[key]

    for idx, c in company.items():
        if idx.replace("company", "") == '':
            continue
        if c['name'] == '':
            continue

        if c['date'] == '':
            c['date'] = None
        c['cntrct_sn'] = params['cntrct_sn']
        c['prjct_sn'] = prjct['prjct_sn']
        human = c['human'].replace(",", "")
        direct = c['direct'].replace(",", "")
        daily = c['daily'].replace(",", "")
        s = c['sum'].replace(",", "")
        human = int(human) if human != '' else 0
        direct = int(direct) if direct != '' else 0
        daily = int(daily) if daily != '' else 0
        s = int(s) if s != '' else 0

        c['pymnt_mth'] = "{}-{}-{}-{}".format(human, direct, daily, s)
        c['register_id'] = session['member']['member_id']
        query = """INSERT INTO outsrc(cntrct_sn, prjct_sn, outsrc_fo_sn, cntrct_de, pymnt_mth, rspnber_nm, rspnber_telno, charger_nm, charger_telno, regist_dtm, register_id)
                    VALUES(%(cntrct_sn)s, %(prjct_sn)s, %(name)s, %(date)s, %(pymnt_mth)s, %(owner)s, %(owner_telno)s, %(dam)s, %(dam_telno)s, NOW(), %(register_id)s)"""
        g.curs.execute(query, c)
        outsrc_sn = g.curs.lastrowid

        for item_nm, item_dlnt, item_damt in zip(c['item_name[]'], c['item_dlnt[]'], c['item_damt[]']):
            if item_nm != '':
                dlnt = int(item_dlnt.replace(",", ""))
                damt = int(item_damt.replace(",", ""))
                query = """INSERT INTO outsrc_item(outsrc_sn, item_nm, item_dlnt, item_damt) VALUES (%s, %s, %s, %s)"""
                g.curs.execute(query, (outsrc_sn, item_nm, dlnt, damt))

    equipments_dict = {}
    equipments_other_dict = {}
    row_length = 0
    row_length_other = 0
    for key in params:
        if key.endswith("[]") and not key.startswith("company") and not key.endswith("other[]"):
            equipments_dict[key] = params[key]
            row_length = len(params[key])
        elif key.endswith("other[]") and not key.startswith('company'):
            equipments_other_dict[key] = params[key]
            row_length_other = len(params[key])

    equipments = []
    for _ in range(row_length):
        equipments.append({"cntrct_sn" : params["cntrct_sn"]})
    equipments_other = []
    for _ in range(row_length_other):
        equipments_other.append({"cntrct_sn" : params["cntrct_sn"]})
    for key, value in equipments_dict.items():
        for i, v in enumerate(value):
            if not key.endswith("other[]"):
                k = key.replace("[]", "")
                if k in ("cnt_dlnt", "dlamt"):
                    equipments[i][k] = 0 if v.replace(",", "") == '' else int(v.replace(",", ""))
                elif k == 'samount':
                    equipments[i][k] = None if v.replace(",", "") == '' else int(v.replace(",", ""))
                else:
                    equipments[i][k] = v
    for key, value in equipments_other_dict.items():
        for i, v in enumerate(value):
            if key.endswith("other[]"):
                k = key.replace("_other[]", "")
                if k in ("cnt_dlnt", "dlamt"):
                    equipments_other[i][k] = 0 if v.replace(",", "") == '' else int(v.replace(",", ""))
                elif k == 'samount':
                    equipments_other[i][k] = None if v.replace(",", "") == '' else int(v.replace(",", ""))
                else:
                    equipments_other[i][k] = v

    equipments = [eq for eq in equipments if eq['bcnc_sn'] != '' and eq['dlamt'] != 0 and eq['model_no'] != '']
    equipments_other = [eq for eq in equipments_other if eq['bcnc_sn'] != '' and eq['dlamt'] != 0 and eq['model_no'] != '']
    query = """INSERT INTO expect_equipment(cntrct_sn, model_no, prdlst_se_code, bcnc_sn, delng_ty_code, cnt_dlnt, dlamt, samt, rm)
                VALUES (%(cntrct_sn)s, %(model_no)s, %(prdlst_se_code)s, %(bcnc_sn)s, %(delng_ty_code)s, %(cnt_dlnt)s, %(dlamt)s, %(samount)s, %(rm)s)"""
    g.curs.executemany(query, equipments)
    g.curs.executemany(query, equipments_other)


def insert_equipment_samsung(params):
    row_length = len(params['equip_sn[]'])
    order_de = datetime.datetime.now().strftime("%Y-%m-%d")
    data = []
    for _ in range(row_length):
        data.append({"cntrct_sn" : params["cntrct_sn"], "order_de" : order_de})

    for key in params:
        if key.endswith("[]"):
            for i, v in enumerate(params[key]):
                k = key.replace("[]", "")
                if k in ("dlnt", "dlamt", "samount"):
                    value = None if v.replace(",", "") == "" else int(v.replace(",", ""))
                else:
                    value = v
                data[i][k] = value

    real_data = []
    for d in data:
        if d['dlnt'] is not None:
            real_data.append(d)
    query = """INSERT INTO equipment(order_de, cntrct_sn, prdlst_se_code, model_no, dlnt, pamt, samt, bcnc_sn, cnnc_sn, delng_ty_code) 
    VALUES(%(order_de)s, %(cntrct_sn)s, %(prdlst_se_code)s, %(model_no)s, %(dlnt)s, %(dlamt)s, %(samount)s, %(bcnc_sn)s, %(equip_sn)s, %(delng_ty_code)s) """
    g.curs.executemany(query, real_data)
