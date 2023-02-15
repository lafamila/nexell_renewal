from flask import session, jsonify, g
from app.helpers.datatable_helper import dt_query
from collections import OrderedDict
import datetime

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
