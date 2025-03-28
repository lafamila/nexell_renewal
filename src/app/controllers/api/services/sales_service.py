from flask import session, jsonify, g
from app.helpers.datatable_helper import dt_query
from .project_service import get_project_by_cntrct_nm, get_contract
from collections import OrderedDict
import datetime
from pytz import timezone
import calendar
import json
from dateutil.relativedelta import relativedelta

def get_sales_datatable(params):
    query = """SELECT a.ctmmny_sn
				, a.cntrct_sn
				, a.prjct_sn
				, a.delng_sn
				, a.delng_se_code
				, (SELECT code_nm FROM code WHERE ctmmny_sn=1 AND parnts_code='DELNG_SE_CODE' AND code=a.delng_se_code) AS delng_se_nm
				, IFNULL(a.ddt_man, '9999-99-99') AS ddt_man
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
				AND ((a.ddt_man BETWEEN '{0} 00:00:00' AND '{1} 23:59:59') {2})
""".format(params['s_ddt_man_start'], params['s_ddt_man_end'], '' if int(params['s_ddt_man_show']) == 1 else ' or a.ddt_man IS NULL')

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
        query += " AND a.model_no LIKE %s"
        data.append("%{}%".format(params["s_model_no"]))

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
                    , e.cntrct_sn
                    , (SELECT spt_nm FROM contract WHERE cntrct_sn=e.cntrct_sn) AS spt_nm
                    , dlnt
                    , pamt
                    , e.bcnc_sn
                    , before_dlnt
                    , (SELECT bcnc_nm FROM bcnc WHERE bcnc_sn=e.bcnc_sn) AS bcnc_nm
                    FROM equipment e
                    LEFT OUTER JOIN contract c
                    ON e.cntrct_sn=c.cntrct_sn
                    WHERE 1=1
                    AND ((e.dlivy_de BETWEEN '{0} 00:00:00' AND '{1} 23:59:59') or e.dlivy_de IS NULL)
                    AND before_dlnt < dlnt
                    AND deleted = 0
                    """.format(params['s_ddt_man_start'], params['s_ddt_man_end'])
    data = []
    if "s_bcnc_sn" in params and params['s_bcnc_sn']:
        query += " AND e.bcnc_sn=%s"
        data.append(params["s_bcnc_sn"])

    if "s_prdlst_se_code" in params and params['s_prdlst_se_code']:
        query += " AND e.prdlst_se_code=%s"
        data.append(params["s_prdlst_se_code"])

    if "s_model_no" in params and params['s_model_no']:
        query += " AND e.model_no LIKE %s"
        data.append('%{}%'.format(params["s_model_no"]))

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
				LEFT OUTER JOIN member m
				ON c.bsn_chrg_sn=m.mber_sn
				WHERE 1=1
				AND a.ctmmny_sn = 1
				AND ((a.ddt_man BETWEEN '{0} 00:00:00' AND '{1} 23:59:59') {2})
				""".format(params['s_ddt_man_start'], params['s_ddt_man_end'], '' if int(params['s_ddt_man_show']) == 1 else ' or a.ddt_man IS NULL')

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
        query += " AND a.model_no LIKE %s"
        data.append("%{}%".format(params["s_model_no"]))

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
        data["regist_dtm"] = datetime.datetime.now(timezone('Asia/Seoul'))

    if "register_id" not in data:
        data["register_id"] = session["member"]["member_id"]
    sub_query = [key for key in data]
    params_query = ["%({})s".format(key) for key in data]

    query = """INSERT INTO account({}) VALUES ({})""".format(",".join(sub_query), ",".join(params_query))
    g.curs.execute(query, data)

    if "cnnc_sn" in params and 'dlivy_de' in params and params["dlivy_de"] != '':
        row = g.curs.execute("SELECT log_sn FROM stock_log WHERE delng_sn=%(cnnc_sn)s", params)
        if row:
            log_sns = g.curs.fetchall()
            for log in log_sns:
                log['dlivy_de'] = params['dlivy_de']
            g.curs.executemany("UPDATE stock_log SET ddt_man=%(dlivy_de)s WHERE log_sn=%(log_sn)s", log_sns)

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
        params["update_dtm"] = datetime.datetime.now(timezone('Asia/Seoul'))

    if "updater_id" not in params:
        params["updater_id"] = session["member"]["member_id"]

    sub_query = ["{0}=%({0})s".format(key) for key in data]
    query = """UPDATE account SET {} WHERE delng_sn=%(s_delng_sn)s""".format(",".join(sub_query))
    g.curs.execute(query, params)

    if "cnnc_sn" in params and 'dlivy_de' in params and params["dlivy_de"] != '':
        row = g.curs.execute("SELECT log_sn FROM stock_log WHERE delng_sn=%(cnnc_sn)s", params)
        if row:
            log_sns = g.curs.fetchall()
            for log in log_sns:
                log['dlivy_de'] = params['dlivy_de']
            g.curs.executemany("UPDATE stock_log SET ddt_man=%(dlivy_de)s WHERE log_sn=%(log_sn)s", log_sns)

    row = g.curs.execute("SELECT delng_sn, sales_type, json_data FROM account_temp WHERE delng_sn=%(s_delng_sn)s", params)
    if row:
        data = g.curs.fetchone()
        json_data = json.loads(data['json_data'])
        g.curs.execute("SELECT ddt_man FROM account WHERE delng_sn=%(s_delng_sn)s", params)
        account = g.curs.fetchall(transform=False)[0]
        if account['ddt_man'] is not None:
            json_data['ddt_man'] = account['ddt_man']
            if data['sales_type'] == 0:
                g.curs.execute("""INSERT INTO stock_log(stock_sn, stock_sttus, cntrct_sn, delng_sn, ddt_man, cnnc_sn) VALUES(%(stock_sn)s, 3, %(cntrct_sn)s, %(delng_sn)s, %(ddt_man)s, %(cnnc_sn)s)""", json_data)
            else:
                g.curs.execute("""INSERT INTO stock_log(stock_sn, stock_sttus, cntrct_sn, delng_sn, ddt_man, cnnc_sn) VALUES(%(stock_sn)s, 3, %(cntrct_sn)s, %(delng_sn)s, %(ddt_man)s, %(cnnc_sn)s)""", json_data)
                if json_data['rm'] != '' and json_data['stock_sn'] != '':
                    query = """INSERT INTO bnd_sales_table_log(delng_sn, sale_type, dlnt, dlamt, ddt_man) VALUES(%(delng_sn)s, %(rm)s, %(dlnt)s, %(dlamt)s, %(ddt_man)s)"""
                    g.curs.execute(query, json_data)
            g.curs.execute("DELETE FROM account_temp WHERE delng_sn=%(s_delng_sn)s", params)

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
            , m.mber_nm AS chrg_nm
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
        query += " FROM (SELECT * FROM account WHERE delng_se_code='S' AND delng_ty_code='12' AND expect_de >= '2019-01-01') s "
    query += """ LEFT JOIN (SELECT * FROM account WHERE delng_se_code='P') p 
            LEFT JOIN (SELECT cntrct_sn, spt_chrg_sn, bsn_chrg_sn FROM contract WHERE 1=1) c ON p.cntrct_sn=c.cntrct_sn
            LEFT JOIN member m ON c.spt_chrg_sn=m.mber_sn
            ON s.cnnc_sn=p.delng_sn
            WHERE 1=1
            AND s.dlivy_de IS NOT NULL
            GROUP BY DATE_FORMAT(s.dlivy_de, '%%y-%%m'), s.bcnc_sn, s.cntrct_sn
            ORDER BY dlivy_de ASC
            """
    g.curs.execute(query)
    print(query)
    result = g.curs.fetchall()
    return result

def get_expect_t_list(params):

    query = """SELECT GROUP_CONCAT(t.taxbil_sn) AS taxbil_sn
            , t.taxbil_yn AS taxbil_yn
            , t.pblicte_trget_sn AS bcnc_sn
            , DATE_FORMAT(t.pblicte_de, '%%y-%%m') AS dlivy_de
            , m.mber_nm AS chrg_nm
            , t.collct_de AS expect_de
            , t.cntrct_sn AS cntrct_sn
            , (SELECT spt_nm FROM contract WHERE cntrct_sn=t.cntrct_sn) AS cntrct_nm
            , (SELECT m.dept_code FROM contract c LEFT OUTER JOIN member m ON m.mber_sn = c.bsn_chrg_sn WHERE c.cntrct_sn=t.cntrct_sn) AS dept_code
            , (SELECT code_nm FROM code WHERE ctmmny_sn=1 AND parnts_code='DEPT_CODE' AND code=dept_code) AS dept_nm
            , (SELECT bcnc_nm FROM bcnc WHERE bcnc_sn=t.pblicte_trget_sn) AS bcnc_nm
            , (SELECT code_nm FROM code WHERE parnts_code='DELNG_SE_CODE' AND code=t.delng_se_code) AS delng_se_nm
            , SUM(t.splpc_am + IFNULL(t.vat, 0)) AS price_total
            FROM taxbil t
            LEFT JOIN (SELECT cntrct_sn, spt_chrg_sn, bsn_chrg_sn FROM contract WHERE 1=1) c ON t.cntrct_sn=c.cntrct_sn
            LEFT JOIN member m ON c.spt_chrg_sn=m.mber_sn
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
        query += " AND t.collct_de >= '2019-01-01' "


    query += """ GROUP BY t.cntrct_sn, t.pblicte_trget_sn, t.collct_de
            """
    g.curs.execute(query)
    result = g.curs.fetchall()
    return result

def get_expect_r_list(params):
    query = """SELECT t.taxbil_sn AS taxbil_sn
            , r.rcppay_de AS rcppay_de
            , r.amount AS amount
            , m.mber_nm AS chrg_nm
            FROM (SELECT * FROM rcppay WHERE acntctgr_code IN ('108', '110', '501') AND rcppay_se_code IN ('I', 'I1', 'I2', 'I3', 'I4')) r """
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
            LEFT JOIN (SELECT cntrct_sn, spt_chrg_sn, bsn_chrg_sn FROM contract WHERE 1=1) c ON t.cntrct_sn=c.cntrct_sn
            LEFT JOIN member m ON c.spt_chrg_sn=m.mber_sn
            WHERE 1=1
            AND t.collct_de > '0000-00-00'
            UNION
            (SELECT d.taxbil_sn AS taxbil_sn
            , d.rcppay_de AS rcppay_de
            , d.amount
            , m.mber_nm AS chrg_nm
            FROM direct d LEFT JOIN taxbil t ON d.taxbil_sn=t.taxbil_sn
            LEFT JOIN (SELECT cntrct_sn, spt_chrg_sn, bsn_chrg_sn FROM contract WHERE 1=1) c ON t.cntrct_sn=c.cntrct_sn
            LEFT JOIN member m ON c.spt_chrg_sn=m.mber_sn
            WHERE 1=1)
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
            FROM (SELECT * FROM rcppay WHERE acntctgr_code IN ('638', '146', '624', '501', '634') AND rcppay_se_code IN ('O')) r
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
        params['regist_dtm'] = datetime.datetime.now(timezone('Asia/Seoul'))
        params['register_id'] = session['member']['member_id']
        cntrct_sn = params["cntrct_sn"]
        if params['msh_approval_type'] == 'S':
            g.curs.execute(
                "UPDATE contract SET mh_place=%s, mh_count=%s, mh_period=%s, mh_approval_step=1 WHERE cntrct_sn=%s",
                (params['mh_place'], params['mh_count'], params['mh_period']+"~"+params['mh_period_end'], cntrct_sn))
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
                           (params['mh_place'], params['mh_count'], params['mh_period']+"~"+params['mh_period_end'], cntrct_sn))

        prjct = get_project_by_cntrct_nm(params["cntrct_sn"])
        prjct_sn = prjct['prjct_sn']
        ddt_man = datetime.datetime.now(timezone('Asia/Seoul'))
        data = OrderedDict()
        print(params)
        for key in params:
            if key.endswith("[]"):
                if key == "pamount[]":
                    data["dlamt"] = [int(d.replace(",", "")) if d.replace(",", "") != "" else 0 for d in params[key]]
                elif key == "dlivy_amt[]":
                    data["dlivy_amt"] = [int(d.replace(",", "")) if d.replace(",", "") != "" else 0 for d in params[key]]
                elif key == "add_dc_rate[]":
                    data["add_dscnt_rt"] = [float(d.replace("%", "")) if d != '' else 0.0 for d in params[key] ]
                elif key == "qy[]":
                    data["dlnt"] = [int(d.replace(",", "")) if d.replace(",", "") != "" else 0 for d in params[key]]
                elif key == "dc_rate[]":
                    data["dscnt_rt"] = [float(d.replace("%", "")) if d.replace("%", "") != "" else 0.0 for d in params[key] ]
                elif key in ("expect_de[]",):
                    data["wrhousng_de"] = params[key]
                elif key in ("delng_sn[]", "prduct_ty_code[]", "stock_sn[]", "return_de[]", "return_dlnt[]", "stock_place[]", "dc[]"):
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
        deletes = []
        for i in range(len(input_data)):
            row = input_data[i]
            if row['dlamt'] == 0 and row['dlivy_amt'] == 0 and row['dlnt'] == 0 and row['add_dscnt_rt'] == 0.0 and row['dscnt_rt'] == 0.0 and row['model_no'].strip() == '':
                deletes.append(i)

        for i in deletes[::-1]:
            del input_data[i]

        print(input_data)
        for row in input_data:
            row['cntrct_sn'] = cntrct_sn
            row['prjct_sn'] = prjct_sn
            row['ctmmny_sn'] = 1
            row['regist_dtm'] = datetime.datetime.now(timezone('Asia/Seoul'))
            row['register_id'] = session['member']['member_id']
            row['delng_se_code'] = 'P'
            row['ddt_man'] = datetime.datetime.now(timezone('Asia/Seoul')) if int(row['bcnc_sn']) == 79 else None

        sub_query = [key for key in input_data[0]]
        params_query = ["%({})s".format(key) for key in input_data[0]]

        query = """INSERT INTO account({}) VALUES ({})""".format(",".join(sub_query), ",".join(params_query))
        delng_sns = []
        for i in input_data:
            g.curs.execute(query, i)
            delng_sn = g.curs.lastrowid
            delng_sns.append(delng_sn)
        if params['msh_approval_type'] == 'B':
            g.curs.execute("DELETE FROM cost WHERE cntrct_sn=%(cntrct_sn)s AND cntrct_execut_code='E' AND ct_se_code IN ('61', '62', '64', '65')", params)
        for row in input_data:
            query = """INSERT INTO cost(cntrct_sn, prjct_sn, cntrct_execut_code, ct_se_code, purchsofc_sn, model_no, qy, puchas_amount, dscnt_rt, add_dscnt_rt, cost_date, extra_sn, regist_dtm, register_id, dspy_se_code)
                        VALUES (%(cntrct_sn)s, %(prjct_sn)s, 'E', %(delng_ty_code)s, %(bcnc_sn)s, %(model_no)s, %(dlnt)s, %(b61)s, 0.0, %(add_dscnt_rt)s ,'0000-00-00', 0, %(regist_dtm)s, %(register_id)s, %(dspy_se_code)s)"""
            row['b61'] = row['dlamt']
            add_dc = (row['add_dscnt_rt'] / 100.0) * (row['dlivy_amt'])
            row['add_dscnt_rt'] = (add_dc * 100.0 / row['b61']) if row['b61'] != 0 else 0.0
            row['dspy_se_code'] = 1 if int(row['delng_ty_code']) in (61, 62) else 2
            g.curs.execute(query, row)

        return delng_sns
    else:
        prjct = get_project_by_cntrct_nm(params["cntrct_sn"])
        cntrct_sn = params["cntrct_sn"]
        g.curs.execute("UPDATE contract SET mh_approval_step=2 WHERE cntrct_sn=%s", (cntrct_sn,))

    if "option_bigo" in params and params["option_bigo"].strip() != '':
        query = """SELECT partclr_matter FROM project WHERE prjct_sn=%s"""
        g.curs.execute(query, (prjct["prjct_sn"],))
        result = g.curs.fetchone()
        if result and result["partclr_matter"]:
            before = result["partclr_matter"]
        else:
            before = ""
        partclr_matter = "{}\n\n{} {}\n{}".format(before, datetime.datetime.now(timezone('Asia/Seoul')).strftime("%Y-%m-%d"),
                                                  "M,S/H 설치·회수", params["option_bigo"])

        query = """UPDATE project SET partclr_matter=%s WHERE prjct_sn=%s"""
        if prjct["prjct_sn"] is not None:
            g.curs.execute(query, (partclr_matter, prjct["prjct_sn"]))



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

            g.curs.execute("UPDATE contract SET mh_place=%s, mh_count=%s, mh_period=%s WHERE cntrct_sn=%s", (params['mh_place'], params['mh_count'], params['mh_period']+"~"+params['mh_period_end'], cntrct_sn))

        prjct = get_project_by_cntrct_nm(params["cntrct_sn"])
        prjct_sn = prjct['prjct_sn']
        ddt_man = datetime.datetime.now(timezone('Asia/Seoul'))
        data = OrderedDict()
        for key in params:
            if key.endswith("[]"):
                if key in ("dlamt[]", "dlnt[]"):
                    data[key.replace("[]", "")] = [int(d.replace(",", "")) if d.replace(",", "") != '' else 0 for d in params[key]]
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

        deletes = []
        for i in range(len(input_data)):
            row = input_data[i]
            if row['dlamt'] == 0 and row['dlnt'] == 0 and row['model_no'].strip() == '':
                deletes.append(i)
            elif row['bcnc_sn'] == '' or int(row['bcnc_sn']) not in (74,79):
                deletes.append(i)

        for i in deletes[::-1]:
            del input_data[i]


        for row in input_data:
            row['cntrct_sn'] = cntrct_sn
            row['prjct_sn'] = prjct_sn
            row['ctmmny_sn'] = 1
            row['regist_dtm'] = datetime.datetime.now(timezone('Asia/Seoul'))
            row['register_id'] = session['member']['member_id']
            row['delng_se_code'] = 'P'
            row['ddt_man'] = datetime.datetime.now(timezone('Asia/Seoul')) if int(row['bcnc_sn']) == 79 else None
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
        prjct = get_project_by_cntrct_nm(params["cntrct_sn"])
        cntrct_sn = params["cntrct_sn"]
        g.curs.execute("UPDATE contract SET mh_approval_step=2 WHERE cntrct_sn=%s", (cntrct_sn, ))

    if "option_bigo" in params and params["option_bigo"].strip() != '':
        query = """SELECT partclr_matter FROM project WHERE prjct_sn=%s"""
        g.curs.execute(query, (prjct["prjct_sn"],))
        result = g.curs.fetchone()
        if result and result["partclr_matter"]:
            before = result["partclr_matter"]
        else:
            before = ""
        partclr_matter = "{}\n\n{} {}\n{}".format(before, datetime.datetime.now(timezone('Asia/Seoul')).strftime("%Y-%m-%d"),
                                                  "M,S/H 설치·회수", params["option_bigo"])

        query = """UPDATE project SET partclr_matter=%s WHERE prjct_sn=%s"""
        if prjct["prjct_sn"] is not None:
            g.curs.execute(query, (partclr_matter, prjct["prjct_sn"]))

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
        if order_de == '' or prdlst_se_code == '':
            continue
        data['order_de'] = order_de
        data['prdlst_se_code'] = prdlst_se_code
        data['model_no'] = '자재'
        data['dlnt'] = 1
        data['pamt'] = int(pamt.replace(",", "")) if pamt != '' else None
        data['samt'] = int(samt.replace(",", "")) if samt != '' else None
        data['bcnc_sn'] = bcnc_sn
        data['delng_ty_code'] = 3
        g.curs.execute("INSERT INTO equipment({}) VALUES ({})".format(",".join([key for key in data.keys()]), ",".join(["%({})s".format(key) for key in data.keys()])), data)

    if "option_bigo" in params and params["option_bigo"].strip() != '':
        query = """SELECT partclr_matter FROM project WHERE prjct_sn=%s"""
        prjct = get_project_by_cntrct_nm(params["cntrct_sn"])
        g.curs.execute(query, (prjct["prjct_sn"],))
        result = g.curs.fetchone()
        if result and result["partclr_matter"]:
            before = result["partclr_matter"]
        else:
            before = ""
        partclr_matter = "{}\n\n{} {}\n{}".format(before, datetime.datetime.now(timezone('Asia/Seoul')).strftime("%Y-%m-%d"),
                                                  "로지텍자재", params["option_bigo"])

        query = """UPDATE project SET partclr_matter=%s WHERE prjct_sn=%s"""
        if prjct["prjct_sn"] is not None:
            g.curs.execute(query, (partclr_matter, prjct["prjct_sn"]))

def get_model_list(params, purpose=None):
    query = """SELECT p.delng_sn
                    , p.bcnc_sn
                    , p.prdlst_se_code
                    , p.model_no
                    , p.dlnt
                    , p.dlamt
                    , p.dlivy_amt
                    , p.wrhousng_de
                    , p.delng_ty_code
                    , p.dscnt_rt
                    , p.add_dscnt_rt
    				, (SELECT bcnc_nm FROM bcnc WHERE bcnc_sn=p.bcnc_sn) AS bcnc_nm
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
    if purpose is not None:
        query += "                    ORDER BY dlivy_de ASC"
    g.curs.execute(query, params)
    result = g.curs.fetchall()
    return result

def insert_equipment_other_BD(params):
    prjct = get_project_by_cntrct_nm(params["cntrct_sn"])
    cntrct = get_contract({"s_cntrct_sn": params["cntrct_sn"]})

    parseInt = lambda x: 0 if x.replace(",", "") == '' else int(x.replace(",", ""))
    for bcnc_sn, cntrct_amount, dlivy_amt, dlnt, amount, model_no, pamount, prdlst_se_code in zip(params["bcnc_sn[]"], params["cntrct_amount[]"], params["dlivy_amt[]"], params["dlnt[]"], params["amount[]"], params["model_no[]"], params["pamount[]"], params["prdlst_se_code[]"]):

        row = dict()
        row['cntrct_sn'] = params['cntrct_sn']
        row['prjct_sn'] = prjct['prjct_sn']
        row['ctmmny_sn'] = 1
        row['regist_dtm'] = datetime.datetime.now(timezone('Asia/Seoul'))
        row['register_id'] = session['member']['member_id'] if "member" in session else "nexelll"
        row['delng_se_code'] = 'P'
        row['ddt_man'] = None
        row['bcnc_sn'] = 100
        row['prdlst_se_code'] = prdlst_se_code
        row['model_no'] = model_no
        row['delng_ty_code'] = 2
        row['dlnt'] = parseInt(dlnt)
        row['dlamt'] = parseInt(pamount)
        keys = list(row.keys())
        g.curs.execute("INSERT INTO account({0}) VALUES ({1})".format(",".join(keys), ",".join(["%({})s".format(key) for key in keys])), row)
        delng_sn = g.curs.lastrowid
        row['delng_se_code'] = 'S'
        row['dlivy_de'] = None
        row['bcnc_sn'] = bcnc_sn
        row['cnnc_sn'] = delng_sn
        row['bcnc_sn'] = cntrct["bcnc_sn"]
        row['dlamt'] = parseInt(cntrct_amount)
        row['delng_ty_code'] = 11
        row['expect_de'] = None
        keys = list(row.keys())
        g.curs.execute("INSERT INTO account({0}) VALUES ({1})".format(",".join(keys), ",".join(["%({})s".format(key) for key in keys])), row)
        if "option_bigo" in params and params["option_bigo"].strip() != '':
            query = """SELECT partclr_matter FROM project WHERE prjct_sn=%s"""
            prjct = get_project_by_cntrct_nm(params["cntrct_sn"])
            g.curs.execute(query, (prjct["prjct_sn"],))
            result = g.curs.fetchone()
            if result and result["partclr_matter"]:
                before = result["partclr_matter"]
            else:
                before = ""
            partclr_matter = "{}\n\n{} {}\n{}".format(before, datetime.datetime.now(timezone('Asia/Seoul')).strftime(
                "%Y-%m-%d"),
                                                      "타사자재", params["option_bigo"])

            query = """UPDATE project SET partclr_matter=%s WHERE prjct_sn=%s"""
            if prjct["prjct_sn"] is not None:
                g.curs.execute(query, (partclr_matter, prjct["prjct_sn"]))



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
        if order_de == '' or prdlst_se_code == '':
            continue
        data['order_de'] = order_de
        data['prdlst_se_code'] = prdlst_se_code
        data['model_no'] = '자재'
        data['dlnt'] = int(dlnt.replace(",", ""))
        data['pamt'] = int(damt.replace(",", ""))*int(dlnt.replace(",", "")) if damt != '' else None
        data['samt'] = data['pamt']
        data['bcnc_sn'] = 355
        data['bigo'] = model_no
        data['delng_ty_code'] = 4
        g.curs.execute("INSERT INTO equipment({}) VALUES ({})".format(",".join([key for key in data.keys()]), ",".join(["%({})s".format(key) for key in data.keys()])), data)

    if "option_bigo" in params and params["option_bigo"].strip() != '':
        query = """SELECT partclr_matter FROM project WHERE prjct_sn=%s"""
        prjct = get_project_by_cntrct_nm(params["cntrct_sn"])
        g.curs.execute(query, (prjct["prjct_sn"],))
        result = g.curs.fetchone()
        if result and result["partclr_matter"]:
            before = result["partclr_matter"]
        else:
            before = ""
        partclr_matter = "{}\n\n{} {}\n{}".format(before, datetime.datetime.now(timezone('Asia/Seoul')).strftime("%Y-%m-%d"),
                                                  "타사자재", params["option_bigo"])

        query = """UPDATE project SET partclr_matter=%s WHERE prjct_sn=%s"""
        if prjct["prjct_sn"] is not None:
            g.curs.execute(query, (partclr_matter, prjct["prjct_sn"]))

def update_equipment_establish(params):
    prjct = get_project_by_cntrct_nm(params["cntrct_sn"])
    row = g.curs.execute("SELECT IFNULL(max(extra_sn), 0) as m_extra_sn FROM cost WHERE cntrct_execut_code IN ('C', 'E') and cntrct_sn=%s", params['cntrct_sn'])
    if row:
        extra_sn = g.curs.fetchone()['m_extra_sn']
    else:
        extra_sn = 0
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

        if 'human_change' in c:
            human = c['human_change'].replace(",", "")
            direct = c['direct_change'].replace(",", "")
            daily = c['daily_change'].replace(",", "")
            s = c['sum_change'].replace(",", "")
            human = int(human) if human != '' else 0
            direct = int(direct) if direct != '' else 0
            daily = int(daily) if daily != '' else 0
            s = int(s) if s != '' else 0

            c['outsrc_dtls'] = "{}-{}-{}-{}".format(human, direct, daily, s)
        else:
            c['outsrc_dtls'] = None

        c['register_id'] = session['member']['member_id']
        query = """SELECT outsrc_sn FROM outsrc WHERE cntrct_sn=%(cntrct_sn)s AND prjct_sn=%(prjct_sn)s AND outsrc_fo_sn NOT IN (116, 146)"""
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
            for item_type, item_nm, item_dlnt, item_damt, item_total in zip(c['item_type[]'], c['item_name[]'],
                                                                            c['item_dlnt[]'], c['item_damt[]'],
                                                                            c['item_total[]']):
                if item_nm != '':
                    if item_type == '':
                        item_type = '0'

                    dlnt = int(item_dlnt.replace(",", ""))
                    total = int(item_total.replace(",", ""))
                    damt = int(item_damt.replace(",", ""))
                    query = """INSERT INTO outsrc_item(outsrc_sn, item_nm, item_dlnt, item_damt) VALUES (%s, %s, %s, %s)"""
                    g.curs.execute(query, (outsrc_sn, item_nm, dlnt, damt))
                    pParams = {}
                    for key in ["cntrct_sn", "prjct_sn", "name", "register_id"]:
                        pParams[key] = c[key]
                    pParams["model_no"] = item_nm
                    pParams["cost_type"] = int(item_type)
                    pParams["qy"] = dlnt
                    pParams["puchas_amount"] = total / dlnt
                    pParams["extra_sn"] = extra_sn
                    if int(item_type) == 3:
                        row = g.curs.execute(
                            "SELECT outsrc_sn FROM outsrc WHERE cntrct_sn=%(cntrct_sn)s AND outsrc_fo_sn=146", c)
                        if row == 0:
                            query = """INSERT INTO outsrc(cntrct_sn, prjct_sn, outsrc_fo_sn, cntrct_de, pymnt_mth, rspnber_nm, rspnber_telno, charger_nm, charger_telno, regist_dtm, register_id)
                                        VALUES(%(cntrct_sn)s, %(prjct_sn)s, 146, NULL, NULL, NULL, NULL, NULL, NULL, NOW(), %(register_id)s)"""
                            g.curs.execute(query, c)
                            outsrc_sn = g.curs.lastrowid
                        else:
                            outsrc_sn = g.curs.fetchone()['outsrc_sn']

                    query = """INSERT INTO cost(cntrct_sn, prjct_sn, cntrct_execut_code, ct_se_code, purchsofc_sn, model_no, qy, puchas_amount, extra_sn, regist_dtm, register_id, cost_type)
                                VALUES (%(cntrct_sn)s, %(prjct_sn)s, 'E', '5', %(name)s, %(model_no)s, %(qy)s, %(puchas_amount)s, %(extra_sn)s, NOW(), %(register_id)s, %(cost_type)s)"""
                    g.curs.execute(query, pParams)
            if s != 0:
                pParams = {}
                for key in ["cntrct_sn", "prjct_sn", "name", "register_id"]:
                    pParams[key] = c[key]
                pParams["model_no"] = ""
                pParams["cost_type"] = 4
                pParams["qy"] = 1
                pParams["puchas_amount"] = -1 * s
                pParams["extra_sn"] = extra_sn

                query = """INSERT INTO cost(cntrct_sn, prjct_sn, cntrct_execut_code, ct_se_code, purchsofc_sn, model_no, qy, puchas_amount, extra_sn, regist_dtm, register_id, cost_type)
                            VALUES (%(cntrct_sn)s, %(prjct_sn)s, 'E', '5', %(name)s, %(model_no)s, %(qy)s, %(puchas_amount)s, %(extra_sn)s, NOW(), %(register_id)s, %(cost_type)s)"""
                g.curs.execute(query, pParams)


        else:
            query = """INSERT INTO outsrc(cntrct_sn, prjct_sn, outsrc_fo_sn, cntrct_de, pymnt_mth, rspnber_nm, rspnber_telno, charger_nm, charger_telno, regist_dtm, register_id)
                        VALUES(%(cntrct_sn)s, %(prjct_sn)s, %(name)s, %(date)s, %(pymnt_mth)s, %(owner)s, %(owner_telno)s, %(dam)s, %(dam_telno)s, NOW(), %(register_id)s)"""
            g.curs.execute(query, c)
            outsrc_sn = g.curs.lastrowid

            for item_type, item_nm, item_dlnt, item_damt, item_total in zip(c['item_type[]'], c['item_name[]'],
                                                                            c['item_dlnt[]'], c['item_damt[]'],
                                                                            c['item_total[]']):
                if item_nm != '':
                    if item_type == '':
                        item_type = '0'

                    dlnt = int(item_dlnt.replace(",", ""))
                    total = int(item_total.replace(",", ""))
                    damt = int(item_damt.replace(",", ""))
                    query = """INSERT INTO outsrc_item(outsrc_sn, item_nm, item_dlnt, item_damt) VALUES (%s, %s, %s, %s)"""
                    g.curs.execute(query, (outsrc_sn, item_nm, dlnt, damt))
                    pParams = {}
                    for key in ["cntrct_sn", "prjct_sn", "name", "register_id"]:
                        pParams[key] = c[key]
                    pParams["model_no"] = item_nm
                    pParams["cost_type"] = int(item_type)
                    pParams["qy"] = dlnt
                    pParams["puchas_amount"] = total / dlnt
                    pParams["extra_sn"] = extra_sn
                    if int(item_type) == 3:
                        row = g.curs.execute(
                            "SELECT outsrc_sn FROM outsrc WHERE cntrct_sn=%(cntrct_sn)s AND outsrc_fo_sn=146", c)
                        if row == 0:
                            query = """INSERT INTO outsrc(cntrct_sn, prjct_sn, outsrc_fo_sn, cntrct_de, pymnt_mth, rspnber_nm, rspnber_telno, charger_nm, charger_telno, regist_dtm, register_id)
                                        VALUES(%(cntrct_sn)s, %(prjct_sn)s, 146, NULL, NULL, NULL, NULL, NULL, NULL, NOW(), %(register_id)s)"""
                            g.curs.execute(query, c)
                            outsrc_sn = g.curs.lastrowid
                        else:
                            outsrc_sn = g.curs.fetchone()['outsrc_sn']

                    query = """INSERT INTO cost(cntrct_sn, prjct_sn, cntrct_execut_code, ct_se_code, purchsofc_sn, model_no, qy, puchas_amount, extra_sn, regist_dtm, register_id, cost_type)
                                VALUES (%(cntrct_sn)s, %(prjct_sn)s, 'E', '5', %(name)s, %(model_no)s, %(qy)s, %(puchas_amount)s, %(extra_sn)s, NOW(), %(register_id)s, %(cost_type)s)"""
                    g.curs.execute(query, pParams)


def insert_equipment_new(params):
    cost_data = []
    prjct = get_project_by_cntrct_nm(params["cntrct_sn"])


    company = {}
    for key in params:
        if key.startswith("company"):
            if key.split("_")[0] not in company:
                company[key.split("_")[0]] = dict()
            company[key.split("_")[0]]["_".join(key.split("_")[1:])] = params[key]

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

    equipments_update = [eq for eq in equipments if eq['cnt_dlnt'] <= 0]
    equipments = [eq for eq in equipments if eq['cnt_dlnt'] > 0]

    equipments_other_update = [eq for eq in equipments_other if eq['cnt_dlnt'] <= 0]
    equipments_other = [eq for eq in equipments_other if eq['cnt_dlnt'] > 0]

    query = """INSERT INTO expect_equipment(cntrct_sn, model_no, prdlst_se_code, bcnc_sn, delng_ty_code, cnt_dlnt, dlamt, samt, rm)
                VALUES (%(cntrct_sn)s, %(model_no)s, %(prdlst_se_code)s, %(bcnc_sn)s, %(delng_ty_code)s, %(cnt_dlnt)s, %(dlamt)s, %(samount)s, %(rm)s)"""
    if equipments:
        g.curs.executemany(query, equipments)
    if equipments_other:
        g.curs.executemany(query, equipments_other)
    if equipments_update:
        for eq in equipments_update:
            query = """SELECT * FROM expect_equipment WHERE cntrct_sn=%(cntrct_sn)s AND model_no=%(model_no)s AND dlamt=%(dlamt)s"""
            row = g.curs.execute(query, eq)
            if row:
                before = g.curs.fetchone(transform=False)
                del before['equip_sn']
                del before['reg_time']
                if before['samt'] is None:
                    before['samt'] = 0
                before['samt'] = int(before['samt']*int(eq['cnt_dlnt'])/before['cnt_dlnt'])
                before['cnt_dlnt'] = int(eq['cnt_dlnt'])
                keys = list(before.keys())
                query = """INSERT INTO expect_equipment({0}) VALUES ({1})""".format(",".join(keys), ",".join(["%({})s".format(k) for k in keys]))
                g.curs.execute(query, before)

    if equipments_other_update:
        for eq in equipments_other_update:
            query = """SELECT * FROM expect_equipment WHERE cntrct_sn=%(cntrct_sn)s AND model_no=%(model_no)s"""
            row = g.curs.execute(query, eq)
            if row:
                before = g.curs.fetchone(transform=False)
                del before['equip_sn']
                del before['reg_time']
                if before['samt'] is None:
                    before['samt'] = 0
                before['samt'] = int(before['samt']*int(eq['cnt_dlnt'])/before['cnt_dlnt'])
                before['cnt_dlnt'] = int(eq['cnt_dlnt'])
                keys = list(before.keys())
                query = """INSERT INTO expect_equipment({0}) VALUES ({1})""".format(",".join(keys), ",".join(["%({})s".format(k) for k in keys]))
                g.curs.execute(query, before)


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
            if cntrct_execut_code == 'E' and ct_se_code == '5':
                continue

            column = "puchas_amount" if cntrct_execut_code == 'E' else "salamt"
            if cntrct_execut_code == 'E' and ct_se_code == '8':

                cost_data.append({"cntrct_sn" : params["cntrct_sn"], "prjct_sn" : prjct["prjct_sn"], "cntrct_execut_code" : cntrct_execut_code, "ct_se_code" : ct_se_code, "qy" : 1, column : int(value), "extra_sn" : 0, "regist_dtm" : datetime.datetime.now(timezone('Asia/Seoul')), "register_id" : session["member"]["member_id"], "cost_type" : "2"})
            else:
                cost_data.append({"cntrct_sn" : params["cntrct_sn"], "prjct_sn" : prjct["prjct_sn"], "cntrct_execut_code" : cntrct_execut_code, "ct_se_code" : ct_se_code, "qy" : 1, column : int(value), "extra_sn" : 0, "regist_dtm" : datetime.datetime.now(timezone('Asia/Seoul')), "register_id" : session["member"]["member_id"]})


    for data in cost_data:
        sub_query = [key for key in data]
        params_query = ["%({})s".format(key) for key in data]
        query = """SELECT cntrwk_ct_sn FROM cost WHERE cntrct_sn=%(cntrct_sn)s AND prjct_sn=%(prjct_sn)s AND cntrct_execut_code=%(cntrct_execut_code)s AND ct_se_code=%(ct_se_code)s AND extra_sn=0"""
        row = g.curs.execute(query, data)
        if row:
            cntrwk_ct_sn = g.curs.fetchone()['cntrwk_ct_sn']
            g.curs.execute("DELETE FROM cost WHERE cntrwk_ct_sn=%s", (cntrwk_ct_sn, ))
        query = """INSERT INTO cost({}) VALUES ({})""".format(",".join(sub_query), ",".join(params_query))
        g.curs.execute(query, data)


    company = {}
    for key in params:
        if key.startswith("company"):
            if key.split("_")[0] not in company:
                company[key.split("_")[0]] = dict()
            company[key.split("_")[0]]["_".join(key.split("_")[1:])] = params[key]

    isThereDaily = []
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
        if s != 0:
            cost_param = {"cntrct_sn": params["cntrct_sn"], "prjct_sn": prjct["prjct_sn"], "cntrct_execut_code": 'E',
                 "ct_se_code": '5', "qy": 1, column: -s, "extra_sn": 0,
                 "regist_dtm": datetime.datetime.now(timezone('Asia/Seoul')),
                 "register_id": session["member"]["member_id"], 'purchsofc_sn' : c["name"]}
            sub_query = [key for key in cost_param]
            params_query = ["%({})s".format(key) for key in cost_param]
            query = """SELECT cntrwk_ct_sn FROM cost WHERE cntrct_sn=%(cntrct_sn)s AND prjct_sn=%(prjct_sn)s AND cntrct_execut_code=%(cntrct_execut_code)s AND ct_se_code=%(ct_se_code)s AND extra_sn=0"""
            row = g.curs.execute(query, cost_param)
            if row:
                cntrwk_ct_sn = g.curs.fetchone()['cntrwk_ct_sn']
                g.curs.execute("DELETE FROM cost WHERE cntrwk_ct_sn=%s", (cntrwk_ct_sn, ))
            query = """INSERT INTO cost({}) VALUES ({})""".format(",".join(sub_query), ",".join(params_query))
            g.curs.execute(query, cost_param)



        for item_type, item_nm, item_dlnt, item_damt, item_total in zip(c['item_type[]'], c['item_name[]'], c['item_dlnt[]'], c['item_damt[]'], c['item_total[]']):
            if item_nm != '':
                if item_type == '':
                    item_type = '0'

                dlnt = int(item_dlnt.replace(",", ""))
                total = int(item_total.replace(",", ""))

                damt = int(item_damt.replace(",", ""))
                query = """INSERT INTO outsrc_item(outsrc_sn, item_nm, item_dlnt, item_damt) VALUES (%s, %s, %s, %s)"""
                g.curs.execute(query, (outsrc_sn, item_nm, dlnt, damt))
                pParams = {}
                for key in ["cntrct_sn", "prjct_sn", "name", "register_id"]:
                    pParams[key] = c[key]
                pParams["model_no"] = item_nm
                pParams["cost_type"] = int(item_type)
                pParams["qy"] = dlnt
                pParams["puchas_amount"] = total / dlnt
                if int(item_type) == 3:
                    isThereDaily.append(pParams)
                    continue
                query = """INSERT INTO cost(cntrct_sn, prjct_sn, cntrct_execut_code, ct_se_code, purchsofc_sn, model_no, qy, puchas_amount, extra_sn, regist_dtm, register_id, cost_type)
                            VALUES (%(cntrct_sn)s, %(prjct_sn)s, 'E', '5', %(name)s, %(model_no)s, %(qy)s, %(puchas_amount)s, 0, NOW(), %(register_id)s, %(cost_type)s)"""
                g.curs.execute(query, pParams)

    if len(isThereDaily) > 0:
        for i, c in enumerate(isThereDaily):
            if i == 0:
                row = g.curs.execute("SELECT outsrc_sn FROM outsrc WHERE cntrct_sn=%(cntrct_sn)s AND outsrc_fo_sn=146", c)
                if row == 0:
                    query = """INSERT INTO outsrc(cntrct_sn, prjct_sn, outsrc_fo_sn, cntrct_de, pymnt_mth, rspnber_nm, rspnber_telno, charger_nm, charger_telno, regist_dtm, register_id)
                                VALUES(%(cntrct_sn)s, %(prjct_sn)s, 146, NULL, NULL, NULL, NULL, NULL, NULL, NOW(), %(register_id)s)"""
                    g.curs.execute(query, c)
                    outsrc_sn = g.curs.lastrowid
                else:
                    outsrc_sn = g.curs.fetchone()['outsrc_sn']
            query = """INSERT INTO cost(cntrct_sn, prjct_sn, cntrct_execut_code, ct_se_code, purchsofc_sn, model_no, qy, puchas_amount, extra_sn, regist_dtm, register_id, cost_type)
                        VALUES (%(cntrct_sn)s, %(prjct_sn)s, 'E', '5', %(name)s, %(model_no)s, %(qy)s, %(puchas_amount)s, 0, NOW(), %(register_id)s, 3)"""
            g.curs.execute(query, c)


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

    equipments_update = [eq for eq in equipments if eq['cnt_dlnt'] <= 0]
    equipments = [eq for eq in equipments if eq['cnt_dlnt'] > 0]

    equipments_other_update = [eq for eq in equipments_other if eq['cnt_dlnt'] <= 0]
    equipments_other = [eq for eq in equipments_other if eq['cnt_dlnt'] > 0]

    query = """INSERT INTO expect_equipment(cntrct_sn, model_no, prdlst_se_code, bcnc_sn, delng_ty_code, cnt_dlnt, dlamt, samt, rm)
                VALUES (%(cntrct_sn)s, %(model_no)s, %(prdlst_se_code)s, %(bcnc_sn)s, %(delng_ty_code)s, %(cnt_dlnt)s, %(dlamt)s, %(samount)s, %(rm)s)"""
    if equipments:
        g.curs.executemany(query, equipments)
    if equipments_other:
        g.curs.executemany(query, equipments_other)
    if equipments_update:
        for eq in equipments_update:
            query = """SELECT * FROM expect_equipment WHERE cntrct_sn=%(cntrct_sn)s AND model_no=%(model_no)s AND dlamt=%(dlamt)s"""
            row = g.curs.execute(query, eq)
            if row:
                before = g.curs.fetchone(transform=False)
                del before['equip_sn']
                del before['reg_time']
                if before['samt'] is None:
                    before['samt'] = 0
                before['samt'] = int(before['samt']*int(eq['cnt_dlnt'])/before['cnt_dlnt'])
                before['cnt_dlnt'] = int(eq['cnt_dlnt'])
                keys = list(before.keys())
                query = """INSERT INTO expect_equipment({0}) VALUES ({1})""".format(",".join(keys), ",".join(["%({})s".format(k) for k in keys]))
                g.curs.execute(query, before)

    if equipments_other_update:
        for eq in equipments_other_update:
            query = """SELECT * FROM expect_equipment WHERE cntrct_sn=%(cntrct_sn)s AND model_no=%(model_no)s"""
            row = g.curs.execute(query, eq)
            if row:
                before = g.curs.fetchone(transform=False)
                del before['equip_sn']
                del before['reg_time']
                if before['samt'] is None:
                    before['samt'] = 0
                before['samt'] = int(before['samt']*int(eq['cnt_dlnt'])/before['cnt_dlnt'])
                before['cnt_dlnt'] = int(eq['cnt_dlnt'])
                keys = list(before.keys())
                query = """INSERT INTO expect_equipment({0}) VALUES ({1})""".format(",".join(keys), ",".join(["%({})s".format(k) for k in keys]))
                g.curs.execute(query, before)

    if "option_bigo" in params and params["option_bigo"].strip() != '':
        query = """SELECT partclr_matter FROM project WHERE prjct_sn=%s"""
        prjct = get_project_by_cntrct_nm(params["cntrct_sn"])
        g.curs.execute(query, (prjct["prjct_sn"],))
        result = g.curs.fetchone()
        if result and result["partclr_matter"]:
            before = result["partclr_matter"]
        else:
            before = ""
        partclr_matter = "{}\n\n{} {}\n{}".format(before, datetime.datetime.now(timezone('Asia/Seoul')).strftime("%Y-%m-%d"),
                                                  "장비현황 및 업체선정", params["option_bigo"])

        query = """UPDATE project SET partclr_matter=%s WHERE prjct_sn=%s"""
        if prjct["prjct_sn"] is not None:
            g.curs.execute(query, (partclr_matter, prjct["prjct_sn"]))
        query = """UPDATE contract SET renewal=0 WHERE cntrct_sn=%s"""
        g.curs.execute(query, (params["cntrct_sn"],))


def insert_equipment_samsung(params):
    row_length = len(params['equip_sn[]'])
    order_de = datetime.datetime.now(timezone('Asia/Seoul')).strftime("%Y-%m-%d")
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

    for r in real_data:
        if r['equip_sn'] == '':
            r['equip_sn'] = None
        if "_type" not in params:
            r['delng_ty_code']=1
            r['bcnc_sn'] = 74
        else:
            r['delng_ty_code']=2
            r['bcnc_sn'] = 100

    query = """INSERT INTO equipment(order_de, cntrct_sn, prdlst_se_code, model_no, dlnt, pamt, samt, bcnc_sn, cnnc_sn, delng_ty_code) 
    VALUES(NOW(), %(cntrct_sn)s, %(prdlst_se_code)s, %(model_no)s, %(dlnt)s, %(dlamt)s, %(samount)s, %(bcnc_sn)s, %(equip_sn)s, %(delng_ty_code)s) """
    g.curs.executemany(query, real_data)

    if "option_bigo" in params and params["option_bigo"].strip() != '':
        query = """SELECT partclr_matter FROM project WHERE prjct_sn=%s"""
        prjct = get_project_by_cntrct_nm(params["cntrct_sn"])
        g.curs.execute(query, (prjct["prjct_sn"],))
        result = g.curs.fetchone()
        if result and result["partclr_matter"]:
            before = result["partclr_matter"]
        else:
            before = ""
        partclr_matter = "{}\n\n{} {}\n{}".format(before, datetime.datetime.now(timezone('Asia/Seoul')).strftime("%Y-%m-%d"),
                                                  "삼성장비" if "_type" not in params else "타사장비", params["option_bigo"])

        query = """UPDATE project SET partclr_matter=%s WHERE prjct_sn=%s"""
        if prjct["prjct_sn"] is not None:
            g.curs.execute(query, (partclr_matter, prjct["prjct_sn"]))


def insert_equipment_BD_samsung(params):
    row_length = len(params['equip_sn[]'])
    order_de = datetime.datetime.now(timezone('Asia/Seoul')).strftime("%Y-%m-%d")
    data = []
    for _ in range(row_length):
        data.append({"cntrct_sn" : params["cntrct_sn"], "order_de" : order_de})

    for key in params:
        if key.endswith("[]"):
            for i, v in enumerate(params[key]):
                k = key.replace("[]", "")
                if k in ("dlnt", "pamount", "cntrct_amount", "dlivy_amt"):
                    value = None if v.replace(",", "") == "" else int(v.replace(",", ""))
                else:
                    value = v
                data[i][k] = value

    real_data = []
    for d in data:
        if d['dlnt'] is not None and d['dlnt'] > 0:
            real_data.append(d)
    query = """INSERT INTO equipment(order_de, cntrct_sn, prdlst_se_code, model_no, dlnt, pamt, samt, bcnc_sn, cnnc_sn, delng_ty_code, dlivy_amt) 
    VALUES(%(order_de)s, %(cntrct_sn)s, %(prdlst_se_code)s, %(model_no)s, %(dlnt)s, %(pamount)s, %(cntrct_amount)s, %(bcnc_sn)s, %(equip_sn)s, 1, %(dlivy_amt)s) """
    g.curs.executemany(query, real_data)

    if "option_bigo" in params and params["option_bigo"].strip() != '':
        query = """SELECT partclr_matter FROM project WHERE prjct_sn=%s"""
        prjct = get_project_by_cntrct_nm(params["cntrct_sn"])
        g.curs.execute(query, (prjct["prjct_sn"],))
        result = g.curs.fetchone()
        if result and result["partclr_matter"]:
            before = result["partclr_matter"]
        else:
            before = ""
        partclr_matter = "{}\n\n{} {}\n{}".format(before, datetime.datetime.now(timezone('Asia/Seoul')).strftime("%Y-%m-%d"),
                                                  "삼성장비", params["option_bigo"])

        query = """UPDATE project SET partclr_matter=%s WHERE prjct_sn=%s"""
        if prjct["prjct_sn"] is not None:
            g.curs.execute(query, (partclr_matter, prjct["prjct_sn"]))


def insert_direct(params):
    if "taxbil_sn" in params:
        taxbil_sns = params["taxbil_sn"].split(",")
        total_data = list()
        for taxbil_sn in taxbil_sns:
            data = dict()
            data["taxbil_sn"] = taxbil_sn
            data["rcppay_de"] = params["rcppay_de"]
            data["amount"] = params["amount"]
            total_data.append(data)
            break
        query = "INSERT INTO direct(taxbil_sn, rcppay_de, amount) VALUES (%(taxbil_sn)s, %(rcppay_de)s, %(amount)s)"
        g.curs.executemany(query, total_data)

def update_direct(params):
    if "taxbil_sn" in params:
        taxbil_sns = params["taxbil_sn"].split(",")
        total_data = list()
        for taxbil_sn in taxbil_sns:
            data = dict()
            data["taxbil_sn"] = taxbil_sn
            data["rcppay_de"] = params["rcppay_de"]
            data["amount"] = params["amount"]
            total_data.append(data)
        query = "UPDATE direct SET amount=%(amount)s WHERE taxbil_sn=%(taxbil_sn)s AND rcppay_de= %(rcppay_de)s"
        g.curs.executemany(query, total_data)


def update_account_expect_de(params):
    g.curs.execute("UPDATE account SET expect_de=%(expect_de)s WHERE cntrct_sn=%(cntrct_sn)s AND bcnc_sn=%(bcnc_sn)s AND expect_de=%(before)s", params)

def insert_general_sales_BD(params):
    total_samount = 0
    cntrct_de = datetime.datetime.now(timezone('Asia/Seoul')).strftime("%Y-%m-%d")
    now_bgn = datetime.datetime.strptime(datetime.datetime.now(timezone('Asia/Seoul')).strftime("%Y-%m-01"), "%Y-%m-%d")
    cntrct_nm_format = now_bgn.strftime("%y년%m월 일반판매")
    cntrct_nm = "{}(빌트인)".format(cntrct_nm_format)
    g.curs.execute("SELECT cntrct_sn FROM contract WHERE cntrct_nm=%s", cntrct_nm)
    general_cntrct_sn = g.curs.fetchone()['cntrct_sn']
    for sale_type, stock_sn, bcnc_sn, ddt_man, dlivy_amt, dlnt, model_no, prdlst_se_code, s_dlamt, etc, dc, rm in zip(params['sale_type[]'], params['stock_sn[]'], params['bcnc_sn[]'], params['ddt_man[]'], params['dlivy_amt[]'], params['dlnt[]'], params['model_no[]'], params['prdlst_se_code[]'], params['s_dlamt[]'], params['etc[]'], params['dc[]'], params['rm[]']):
        s_dlamt = int(s_dlamt.replace(",", "")) if s_dlamt.replace(",", "") != '' else 0

        data = dict()
        data['ctmmny_sn'] = 1
        data['bcnc_sn'] = bcnc_sn
        data['delng_ty_code'] = '1'
        data['cntrct_sn'] = params['cntrct_sn']

        data['prjct_sn'] = get_project_by_cntrct_nm(data['cntrct_sn'])['prjct_sn']
        data['delng_se_code'] = 'P'
        data['dlivy_amt'] = int(dlivy_amt.replace(",", "")) if dlivy_amt.replace(",", "") != '' else 0
        data['dlnt'] = int(dlnt.replace(",", "")) if dlnt.replace(",", "") != '' else 0
        data['dscnt_rt'] = float(dc.replace("%", "")) if dc.replace("%", "") != '' else 0.0
        if stock_sn != '':
            data['ddt_man'] = None
            data['dscnt_rt'] = None
            data['dlivy_amt'] = None
            data['dlamt'] = 0
        else:
            data['ddt_man'] = None
            data['dlamt'] = int(data['dlivy_amt'] * (100 - data['dscnt_rt']) / 100)
        data['model_no'] = model_no
        data['prdlst_se_code'] = prdlst_se_code
        data['regist_dtm'] = datetime.datetime.now(timezone('Asia/Seoul'))
        data['register_id'] = 'nexell'

        keys = list(data.keys())

        query = """INSERT INTO account({}) VALUES ({})""".format(",".join(keys), ",".join(["%({})s".format(k) for k in keys]))
        g.curs.execute(query, data)
        cnnc_sn = g.curs.lastrowid

        if stock_sn != '':
            query = """SELECT MAX(log_sn) AS log_sn FROM stock_log WHERE stock_sn=%s"""
            g.curs.execute(query, stock_sn)
            result = g.curs.fetchall()
            if result and result[0]['log_sn'] is not None:
                log_sn = result[0]['log_sn']
            else:
                log_sn = None
            json_data = {"stock_sn" : stock_sn, "cntrct_sn" : data["cntrct_sn"], "delng_sn" : cnnc_sn, "cnnc_sn" : log_sn, "rm" : rm, "dlnt" : data['dlnt'], "dlamt" : s_dlamt}
            g.curs.execute("INSERT INTO account_temp(delng_sn, sales_type, json_data) VALUES (%s, 1, %s)", (cnnc_sn, json.dumps(json_data)))

            # g.curs.execute("""INSERT INTO stock_log(stock_sn, stock_sttus, cntrct_sn, delng_sn, ddt_man, cnnc_sn) VALUES(%s, 3, %s, %s, %s, %s)""", (stock_sn, data['cntrct_sn'], cnnc_sn, data['ddt_man'], log_sn))


        data['delng_se_code'] = 'S'
        if sale_type == 'T':
            data['delng_ty_code'] = '12'
            data['expect_de'] = params['expect_de']
        else:
            data['delng_ty_code'] = '14'
            if data['prjct_sn'] is not None:
                s_dlamt = data['dlamt']

        prjct = get_contract({"s_cntrct_sn" : data['cntrct_sn']})
        data['bcnc_sn'] = prjct['bcnc_sn']
        etc = int(etc.replace(",", "")) if etc.replace(",", "") != '' else 0

        data['dlamt'] = s_dlamt
        data['dlivy_de'] = None
        data['cnnc_sn'] = cnnc_sn

        keys = list(data.keys())

        query = """INSERT INTO account({}) VALUES ({})""".format(",".join(keys), ",".join(["%({})s".format(k) for k in keys]))
        g.curs.execute(query, data)

        # if rm != '' and stock_sn != '':
        #     query = """INSERT INTO bnd_sales_table_log(delng_sn, sale_type, dlnt, dlamt, ddt_man) VALUES(%s, %s, %s, %s, %s)"""
        #     g.curs.execute(query, (cnnc_sn, rm, data['dlnt'], data['dlamt'], data['ddt_man']))

        if sale_type == 'T' or data['prjct_sn'] is None:
            # data['cntrct_de'] = params['cntrct_de']
            data['cntrct_de'] = cntrct_de

            data['cntrct_sn'] = general_cntrct_sn
            data['prjct_sn'] = 0
            query = """INSERT INTO cost(cntrct_sn, prjct_sn, cntrct_execut_code, ct_se_code, purchsofc_sn, prdlst_se_code, model_no, qy, puchas_amount, salamt, dscnt_rt, cost_date, extra_sn, register_id, regist_dtm)
                                    VALUES(%(cntrct_sn)s, %(prjct_sn)s, 'C', 1, 2, null, %(model_no)s, %(dlnt)s, %(dlivy_amt)s, %(dlamt)s, %(dscnt_rt)s, %(cntrct_de)s, 0, 'nexell', NOW())"""
            g.curs.execute(query, data)
            total_samount += int(s_dlamt) * int(dlnt)
    if total_samount > 0:
        g.curs.execute("INSERT INTO contract_table(cntrct_de, cntrct_sn, cntrct_amount) VALUES (%(cntrct_de)s, %(cntrct_sn)s, %(total_samount)s)", {"cntrct_de": cntrct_de, "cntrct_sn": general_cntrct_sn, "total_samount": total_samount})
def insert_general_sales_NR(params):
    print(params)
    general_cntrct_sn = None
    now = datetime.datetime.now(timezone('Asia/Seoul')).strftime("%Y-%m-%d")
    total_samount = 0
    for sale_type, stock_sn, bcnc_sn, ddt_man, dlamt, dlnt, model_no, prdlst_se_code, s_bcnc_sn, samount, etc in zip(params['sale_type[]'], params['stock_sn[]'], params['bcnc_sn[]'], params['ddt_man[]'], params['dlamt[]'], params['dlnt[]'], params['model_no[]'], params['prdlst_se_code[]'], params['s_bcnc_sn[]'], params['samount[]'], params['etc[]']):
        data = dict()
        if sale_type == '' and bcnc_sn == '' and model_no == '':
            continue
        data['ctmmny_sn'] = 1
        data['bcnc_sn'] = bcnc_sn
        data['delng_ty_code'] = '1'
        data['cntrct_sn'] = params['cntrct_sn']
        data['prjct_sn'] = get_project_by_cntrct_nm(data['cntrct_sn'])['prjct_sn']
        data['ddt_man'] = None
        data['delng_se_code'] = 'P'
        data['dlamt'] = int(dlamt.replace(",", "")) if dlamt.replace(",", "") != '' else 0
        data['dlnt'] = int(dlnt.replace(",", "")) if dlnt.replace(",", "") != '' else 0
        data['model_no'] = model_no
        data['prdlst_se_code'] = prdlst_se_code
        data['regist_dtm'] = datetime.datetime.now(timezone('Asia/Seoul'))
        data['register_id'] = 'nexell'

        keys = list(data.keys())

        query = """INSERT INTO account({}) VALUES ({})""".format(",".join(keys), ",".join(["%({})s".format(k) for k in keys]))
        g.curs.execute(query, data)
        cnnc_sn = g.curs.lastrowid

        if stock_sn != '':
            query = """SELECT MAX(log_sn) AS log_sn FROM stock_log WHERE stock_sn=%s"""
            g.curs.execute(query, stock_sn)
            result = g.curs.fetchall()
            if result and result[0]['log_sn'] is not None:
                log_sn = result[0]['log_sn']
            else:
                log_sn = None
            json_data = {"stock_sn" : stock_sn, "cntrct_sn" : data["cntrct_sn"], "delng_sn" : cnnc_sn, "cnnc_sn" : log_sn}
            g.curs.execute("INSERT INTO account_temp(delng_sn, sales_type, json_data) VALUES (%s, 0, %s)", (cnnc_sn, json.dumps(json_data)))
            # g.curs.execute("""INSERT INTO stock_log(stock_sn, stock_sttus, cntrct_sn, delng_sn, ddt_man, cnnc_sn) VALUES(%s, 3, %s, %s, %s, %s)""", (stock_sn, data['cntrct_sn'], cnnc_sn, data['ddt_man'], log_sn))


        data['delng_se_code'] = 'S'
        if sale_type == 'T':
            data['delng_ty_code'] = '12'
            data['expect_de'] = params['expect_de']
        else:
            data['delng_ty_code'] = '14'
        data['bcnc_sn'] = s_bcnc_sn
        samount = int(samount.replace(",", "")) if samount.replace(",", "") != '' else 0
        etc = int(etc.replace(",", "")) if etc.replace(",", "") != '' else 0

        data['dlamt'] = samount / data['dlnt']
        data['dlivy_de'] = None
        data['cnnc_sn'] = cnnc_sn

        keys = list(data.keys())

        query = """INSERT INTO account({}) VALUES ({})""".format(",".join(keys), ",".join(["%({})s".format(k) for k in keys]))
        g.curs.execute(query, data)

        if samount > 0:
            if general_cntrct_sn is None:
                g.curs.execute("SELECT m.dept_code, c.bcnc_sn FROM contract c LEFT JOIN member m ON c.spt_chrg_sn=m.mber_sn WHERE c.cntrct_sn=%s", params['cntrct_sn'])
                contract = g.curs.fetchone()
                dept_code = contract['dept_code']
                bcnc_sn = contract['bcnc_sn']
                dept_nm = {"TS1" : "공조1", "TS2" : "공조2", "BI" : "빌트인"}[dept_code]
                now_bgn = datetime.datetime.strptime(datetime.datetime.now(timezone('Asia/Seoul')).strftime("%Y-%m-01"), "%Y-%m-%d")
                cntrct_nm_format = now_bgn.strftime("%y년%m월 일반판매")
                cntrct_nm = "{}({})".format(cntrct_nm_format, dept_nm)
                g.curs.execute("SELECT cntrct_sn FROM contract WHERE cntrct_nm=%s", cntrct_nm)
                general_cntrct_sn = g.curs.fetchone()['cntrct_sn']

            query = """INSERT INTO cost(cntrct_sn, prjct_sn, cntrct_execut_code, ct_se_code, purchsofc_sn, qy, salamt, cost_date, extra_sn, cost_type, regist_dtm, register_id)
                            VALUES (%(cntrct_sn)s, 0, 'C', '10', %(bcnc_sn)s, 1, %(samount)s, %(now)s, 0, 4, NOW(), 'nexelll')"""
            data = {"cntrct_sn" : general_cntrct_sn, "bcnc_sn": bcnc_sn, "samount": samount, "now": now}
            g.curs.execute(query, data)
            total_samount += samount
        if total_samount > 0:
            g.curs.execute("INSERT INTO contract_table(cntrct_de, cntrct_sn, cntrct_amount) VALUES (%(cntrct_de)s, %(cntrct_sn)s, %(total_samount)s)", {"cntrct_de": now, "cntrct_sn": general_cntrct_sn, "total_samount": total_samount})

def get_equipment(params):
    row = g.curs.execute("SELECT eq_sn FROM equipment WHERE cntrct_sn=%(cntrct_sn)s AND model_no=%(model_no)s AND pamt*(dlnt-before_dlnt)=%(amount)s AND deleted = 0", params)
    result = g.curs.fetchall()
    return result