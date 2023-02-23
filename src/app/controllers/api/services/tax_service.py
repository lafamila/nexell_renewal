from flask import session, jsonify, g
from app.helpers.datatable_helper import dt_query
from collections import OrderedDict
import datetime
import calendar

def get_taxbil_datatable(params):
    query = """SELECT t.ctmmny_sn
				, t.cntrct_sn
				, t.prjct_sn
				, t.taxbil_sn
				, t.taxbil_yn
				, t.delng_se_code
				, (SELECT code_nm FROM code WHERE ctmmny_sn=1 AND parnts_code='DELNG_SE_CODE' AND code=t.delng_se_code) AS delng_se_nm
				, t.pblicte_trget_sn
				, (SELECT bcnc_nm FROM bcnc WHERE bcnc_sn=t.pblicte_trget_sn) AS pblicte_trget_nm
				, t.pblicte_de
				, t.splpc_am
				, t.vat
				, (t.splpc_am + IFNULL(t.vat, 0)) AS total
				, t.rm
				, t.regist_dtm
				, t.register_id
				, t.update_dtm
				, t.updater_id
				, c.cntrct_no
				, c.cntrct_nm
				, m.dept_code
				, (SELECT code_nm FROM code WHERE ctmmny_sn=1 AND parnts_code='DEPT_CODE' AND code=m.dept_code) AS dept_nm
				FROM taxbil t
				LEFT JOIN contract c
				ON t.ctmmny_sn=c.ctmmny_sn AND t.cntrct_sn=c.cntrct_sn
				LEFT OUTER JOIN member m
				ON m.mber_sn=c.bsn_chrg_sn
				WHERE 1=1
				AND t.ctmmny_sn = '1'
				AND t.pblicte_de BETWEEN '{0} 00:00:00' AND '{1} 23:59:59' """.format(params['s_pblicte_de_start'], params['s_pblicte_de_end'])

    data = []
    if "s_cntrct_no" in params and params['s_cntrct_no']:
        query += " AND c.cntrct_no LIKE %s"
        data.append('%{}%'.format(params["s_cntrct_no"]))

    if "s_cntrct_nm" in params and params['s_cntrct_nm']:
        query += " AND c.cntrct_nm LIKE %s"
        data.append('%{}%'.format(params["s_cntrct_nm"]))

    if "s_dept_code" in params and params['s_dept_code']:
        query += " AND m.dept_code=%s"
        data.append(params["s_dept_code"])

    if "s_delng_se_code" in params and params['s_delng_se_code']:
        if params['s_delng_se_code'] == 'SS':
            query += " AND t.delng_se_code LIKE %s"
            data.append("S%")
        else:
            query += " AND t.delng_se_code=%s"
            data.append(params["s_delng_se_code"])

    if "s_pblicte_trget_sn" in params and params['s_pblicte_trget_sn']:
        query += " AND t.pblicte_trget_sn=%s"
        data.append(params["s_pblicte_trget_sn"])

    if "s_taxbil_yn" in params and params['s_taxbil_yn']:
        query += " AND t.taxbil_yn=%s"
        data.append(params["s_taxbil_yn"])

    return dt_query(query, data, params)

def get_taxbil_summary(params):
    query = """SELECT IFNULL(COUNT(t.taxbil_sn),0) AS total_count
				, IFNULL(SUM(IFNULL(t.splpc_am, 0)+IFNULL(t.vat, 0)),0) AS total_amount
				FROM taxbil t
				LEFT JOIN contract c
				ON t.ctmmny_sn=c.ctmmny_sn AND t.cntrct_sn=c.cntrct_sn
				LEFT OUTER JOIN member m
				ON m.mber_sn=c.bsn_chrg_sn
				WHERE 1=1
				AND t.ctmmny_sn = '1'
				AND t.pblicte_de BETWEEN '{0} 00:00:00'
				AND '{1} 23:59:59' """.format(params['s_pblicte_de_start'], params['s_pblicte_de_end'])

    data = []
    if "s_cntrct_no" in params and params['s_cntrct_no']:
        query += " AND c.cntrct_no LIKE %s"
        data.append('%{}%'.format(params["s_cntrct_no"]))

    if "s_cntrct_nm" in params and params['s_cntrct_nm']:
        query += " AND c.cntrct_nm LIKE %s"
        data.append('%{}%'.format(params["s_cntrct_nm"]))

    if "s_dept_code" in params and params['s_dept_code']:
        query += " AND m.dept_code=%s"
        data.append(params["s_dept_code"])

    if "s_delng_se_code" in params and params['s_delng_se_code']:
        if params['s_delng_se_code'] == 'SS':
            query += " AND t.delng_se_code LIKE %s"
            data.append("S%")
        else:
            query += " AND t.delng_se_code=%s"
            data.append(params["s_delng_se_code"])

    if "s_pblicte_trget_sn" in params and params['s_pblicte_trget_sn']:
        query += " AND t.pblicte_trget_sn=%s"
        data.append(params["s_pblicte_trget_sn"])

    if "s_taxbil_yn" in params and params['s_taxbil_yn']:
        query += " AND t.taxbil_yn=%s"
        data.append(params["s_taxbil_yn"])

    g.curs.execute(query, data)
    result = g.curs.fetchone()
    return result

def get_taxbil(params):
    query = """SELECT t.ctmmny_sn
				, t.cntrct_sn
				, t.prjct_sn
				, t.taxbil_sn
				, t.taxbil_yn
				, t.delng_se_code
				, (SELECT code_nm FROM code WHERE ctmmny_sn=1 AND parnts_code='DELNG_SE_CODE' AND code=t.delng_se_code) AS delng_se_nm
				, t.pblicte_trget_sn
				, (SELECT bcnc_nm FROM bcnc WHERE bcnc_sn=t.pblicte_trget_sn) AS pblicte_trget_nm
				, t.pblicte_de
				, t.collct_de
				, t.collct_time
				, t.splpc_am
				, t.vat
				, t.rm
				, t.regist_dtm
				, t.register_id
				, t.update_dtm
				, t.updater_id
				, c.cntrct_no
				, c.prjct_creat_at
				FROM taxbil t
				LEFT JOIN contract c
				ON t.ctmmny_sn=c.ctmmny_sn AND t.cntrct_sn=c.cntrct_sn
				WHERE 1=1
				AND t.ctmmny_sn = '1'
				AND t.cntrct_sn = %(s_cntrct_sn)s
				AND taxbil_sn = %(s_taxbil_sn)s """
    g.curs.execute(query, params)
    result = g.curs.fetchone()
    return result

def insert_taxbil(params):
    data = OrderedDict()
    for key in params:
        if key not in (None,):
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

    query = """INSERT INTO taxbil({}) VALUES ({})""".format(",".join(sub_query), ",".join(params_query))
    g.curs.execute(query, data)
    return g.curs.lastrowid

def update_taxbil(params):
    data = OrderedDict()

    for key in params:
        if key not in ("s_taxbil_sn", ):
            if key in ("vat", ):
                if params[key] == '':
                    params[key] = None
                    data[key] = None
                    continue
                data[key] = params[key]
            elif params[key] != '':
                data[key] = params[key]

    if "ctmmny_sn" not in params:
        params["ctmmny_sn"] = 1

    if "update_dtm" not in params:
        params["update_dtm"] = datetime.datetime.now()

    if "updater_id" not in params:
        params["updater_id"] = session["member"]["member_id"]

    sub_query = ["{0}=%({0})s".format(key) for key in data]
    query = """UPDATE taxbil SET {} WHERE taxbil_sn=%(s_taxbil_sn)s""".format(",".join(sub_query))
    g.curs.execute(query, params)

def delete_taxbil(params):
    g.curs.execute("DELETE FROM taxbil WHERE taxbil_sn=%(s_taxbil_sn)s", params)

def get_taxbil_list(params):
    query = """SELECT t.ctmmny_sn
				, t.cntrct_sn
				, t.prjct_sn
				, t.taxbil_sn
				, t.taxbil_yn
				, t.delng_se_code
				, (SELECT code_nm FROM code WHERE ctmmny_sn=1 AND parnts_code='DELNG_SE_CODE' AND code=t.delng_se_code) AS delng_se_nm
				, t.pblicte_trget_sn
				, (SELECT bcnc_nm FROM bcnc WHERE bcnc_sn=t.pblicte_trget_sn) AS pblicte_trget_nm
				, t.pblicte_de
				, t.splpc_am
				, t.vat
				, (t.splpc_am + t.vat) AS total
				, t.rm
				, t.regist_dtm
				, t.register_id
				, t.update_dtm
				, t.updater_id
				, x.amount
				FROM taxbil t LEFT OUTER JOIN (SELECT SUM(r.amount) AS amount, r.cnnc_sn FROM rcppay r WHERE 1 GROUP BY r.cnnc_sn) x ON t.taxbil_sn = x.cnnc_sn
				WHERE 1=1
				AND t.ctmmny_sn = '1' """

    data = []
    if "s_cntrct_sn" in params and params["s_cntrct_sn"]:
        query += " AND t.cntrct_sn = %s "
        data.append(params['s_cntrct_sn'])

    if "s_prvent_sn" in params and params["s_prvent_sn"]:
        query += " AND t.pblicte_trget_sn = %s "
        data.append(params['s_prvent_sn'])

    query += " ORDER BY t.pblicte_de ASC "
    g.curs.execute(query)
    result = g.curs.fetchall()
    return result