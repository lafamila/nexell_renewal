from flask import session, jsonify, g
from app.helpers.datatable_helper import dt_query
from collections import OrderedDict
import datetime
from pytz import timezone
import calendar

def get_rcppay_datatable(params):
    query = """SELECT r.ctmmny_sn
				, r.cntrct_sn
				, prjct_sn
				, r.cnnc_sn
				, rcppay_sn
				, prvent_sn
				, (SELECT bcnc_nm FROM bcnc WHERE bcnc_sn=r.prvent_sn) AS prvent_nm
				, rcppay_de
				, acntctgr_code
				, (SELECT code_nm FROM code WHERE ctmmny_sn=1 AND parnts_code='ACNTCTGR_CODE' AND code=r.acntctgr_code) AS acntctgr_nm
				, rcppay_dtls
				, papr_invstmnt_sn
				, GET_MEMBER_NAME(papr_invstmnt_sn, 'M') AS papr_invstmnt_nm
				, dept_code
				, (SELECT code_nm FROM code WHERE ctmmny_sn=1 AND parnts_code='DEPT_CODE' AND code=r.dept_code) AS dept_nm
				, rcppay_se_code
				, (SELECT code_nm FROM code WHERE ctmmny_sn=1 AND parnts_code='RCPPAY_SE_CODE' AND code=r.rcppay_se_code) AS rcppay_se_nm
				, IFNULL(amount, '') AS amount
				, acnut_code
				, (SELECT code_nm FROM code WHERE ctmmny_sn=1 AND parnts_code='ACNUT_CODE' AND code=r.acnut_code) AS acnut_nm
				, r.bil_exprn_de
				, r.regist_dtm
				, r.register_id
				, r.update_dtm
				, r.updater_id
				, c.cntrct_no
				, c.spt_nm
				FROM rcppay r
				LEFT JOIN contract c
				ON r.cntrct_sn=c.cntrct_sn
				WHERE 1=1
				AND r.ctmmny_sn = '1'
				AND r.rcppay_de BETWEEN '{0} 00:00:00'
				AND '{1} 23:59:59' """.format(params['s_rcppay_de_start'], params['s_rcppay_de_end'])

    data = []
    if "s_cntrct_no" in params and params['s_cntrct_no']:
        query += " AND c.cntrct_no LIKE %s"
        data.append('%{}%'.format(params["s_cntrct_no"]))

    if "s_spt_nm" in params and params['s_spt_nm']:
        query += " AND c.spt_nm LIKE %s"
        data.append('%{}%'.format(params["s_spt_nm"]))

    if "s_acntctgr_code" in params and params['s_acntctgr_code']:
        query += " AND r.acntctgr_code=%s"
        data.append(params["s_acntctgr_code"])

    if "s_bil_exprn_de" in params and params['s_bil_exprn_de']:
        query += " AND r.bil_exprn_de=%s"
        data.append(params["s_bil_exprn_de"])

    if "s_rcppay_dtls" in params and params['s_rcppay_dtls']:
        query += " AND r.rcppay_dtls LIKE %s"
        data.append('%{}%'.format(params["s_rcppay_dtls"]))

    if "s_prvent_sn" in params and params['s_prvent_sn']:
        query += " AND r.prvent_sn=%s"
        data.append(params["s_prvent_sn"])

    if "s_papr_invstmnt_sn" in params and params['s_papr_invstmnt_sn']:
        query += " AND r.papr_invstmnt_sn=%s"
        data.append(params["s_papr_invstmnt_sn"])

    if "s_dept_code" in params and params['s_dept_code']:
        query += " AND r.dept_code=%s"
        data.append(params["s_dept_code"])

    if "s_rcppay_se_code" in params and params['s_rcppay_se_code']:
        query += " AND r.rcppay_se_code=%s"
        data.append(params["s_rcppay_se_code"])

    if "s_acnut_code" in params and params['s_acnut_code']:
        if params['s_acnut_code'] == '999':
            query += " AND r.acnut_code IS NULL"

        else:
            query += " AND r.acnut_code=%s"
            data.append(params["s_acnut_code"])

    return dt_query(query, data, params)

def get_rcppay_summary(params, exist=True):
    option = "NOT" if exist else ""
    query = """SELECT SUM(IFNULL(o.amount, 0)) amount
				, COUNT(o.rcppay_sn) AS count
				, 'O' AS rcppay_se_code
				FROM rcppay o
				LEFT JOIN contract c
				ON o.cntrct_sn=c.cntrct_sn
				WHERE 1=1
				AND o.rcppay_se_code IN ('O')
				AND o.rcppay_se_code NOT IN ('B')
				AND (o.acnut_code IS {0} NULL)
				AND o.ctmmny_sn = '1'
				AND o.rcppay_de BETWEEN '{1} 00:00:00'
				AND '{2} 23:59:59' """.format(option, params['s_rcppay_de_start'], params['s_rcppay_de_end'])

    data = []
    if "s_cntrct_no" in params and params['s_cntrct_no']:
        query += " AND c.cntrct_no LIKE %s"
        data.append('%{}%'.format(params["s_cntrct_no"]))

    if "s_spt_nm" in params and params['s_spt_nm']:
        query += " AND c.spt_nm LIKE %s"
        data.append('%{}%'.format(params["s_spt_nm"]))

    if "s_acntctgr_code" in params and params['s_acntctgr_code']:
        query += " AND o.acntctgr_code=%s"
        data.append(params["s_acntctgr_code"])

    if "s_bil_exprn_de" in params and params['s_bil_exprn_de']:
        query += " AND o.bil_exprn_de=%s"
        data.append(params["s_bil_exprn_de"])

    if "s_rcppay_dtls" in params and params['s_rcppay_dtls']:
        query += " AND o.rcppay_dtls LIKE %s"
        data.append('%{}%'.format(params["s_rcppay_dtls"]))

    if "s_prvent_sn" in params and params['s_prvent_sn']:
        query += " AND o.prvent_sn=%s"
        data.append(params["s_prvent_sn"])

    if "s_papr_invstmnt_sn" in params and params['s_papr_invstmnt_sn']:
        query += " AND o.papr_invstmnt_sn=%s"
        data.append(params["s_papr_invstmnt_sn"])

    if "s_dept_code" in params and params['s_dept_code']:
        query += " AND o.dept_code=%s"
        data.append(params["s_dept_code"])

    if "s_rcppay_se_code" in params and params['s_rcppay_se_code']:
        query += " AND o.rcppay_se_code=%s"
        data.append(params["s_rcppay_se_code"])

    if "s_acnut_code" in params and params['s_acnut_code']:
        if params['s_acnut_code'] == '999':
            query += " AND o.acnut_code IS NULL"

        else:
            query += " AND o.acnut_code=%s"
            data.append(params["s_acnut_code"])

    query += """UNION
				SELECT SUM(IFNULL(i.amount, 0)) amount
				, COUNT(i.rcppay_sn) AS count
				, 'I' AS rcppay_se_code
				FROM rcppay i
				LEFT JOIN contract c
				ON i.cntrct_sn=c.cntrct_sn
				WHERE 1=1
				AND i.rcppay_se_code NOT IN ('O')
				AND i.rcppay_se_code NOT IN ('B')
				AND (i.acnut_code IS {0} NULL)
				AND i.ctmmny_sn = '1'
				AND i.rcppay_de BETWEEN '{1} 00:00:00'
				AND '{2} 23:59:59' """.format(option, params['s_rcppay_de_start'], params['s_rcppay_de_end'])

    if "s_cntrct_no" in params and params['s_cntrct_no']:
        query += " AND c.cntrct_no LIKE %s"
        data.append('%{}%'.format(params["s_cntrct_no"]))

    if "s_spt_nm" in params and params['s_spt_nm']:
        query += " AND c.spt_nm LIKE %s"
        data.append('%{}%'.format(params["s_spt_nm"]))

    if "s_acntctgr_code" in params and params['s_acntctgr_code']:
        query += " AND i.acntctgr_code=%s"
        data.append(params["s_acntctgr_code"])

    if "s_bil_exprn_de" in params and params['s_bil_exprn_de']:
        query += " AND i.bil_exprn_de=%s"
        data.append(params["s_bil_exprn_de"])

    if "s_rcppay_dtls" in params and params['s_rcppay_dtls']:
        query += " AND i.rcppay_dtls LIKE %s"
        data.append('%{}%'.format(params["s_rcppay_dtls"]))

    if "s_prvent_sn" in params and params['s_prvent_sn']:
        query += " AND i.prvent_sn=%s"
        data.append(params["s_prvent_sn"])

    if "s_papr_invstmnt_sn" in params and params['s_papr_invstmnt_sn']:
        query += " AND i.papr_invstmnt_sn=%s"
        data.append(params["s_papr_invstmnt_sn"])

    if "s_dept_code" in params and params['s_dept_code']:
        query += " AND i.dept_code=%s"
        data.append(params["s_dept_code"])

    if "s_rcppay_se_code" in params and params['s_rcppay_se_code']:
        query += " AND i.rcppay_se_code=%s"
        data.append(params["s_rcppay_se_code"])

    if "s_acnut_code" in params and params['s_acnut_code']:
        if params['s_acnut_code'] == '999':
            query += " AND i.acnut_code IS NULL"

        else:
            query += " AND i.acnut_code=%s"
            data.append(params["s_acnut_code"])

    query += " ORDER BY rcppay_se_code ASC"
    g.curs.execute(query, data)
    result = g.curs.fetchall()
    return result

def get_rcppay(params):
    query = """SELECT ctmmny_sn
				, cntrct_sn
				, prjct_sn
				, cnnc_sn
				, rcppay_sn
				, prvent_sn
				, rcppay_de
				, acntctgr_code
				, rcppay_dtls
				, papr_invstmnt_sn
				, dept_code
				, rcppay_se_code
				, amount
				, acnut_code
				, bil_exprn_de
				, regist_dtm
				, register_id
				, update_dtm
				, updater_id
				, (SELECT IFNULL(prjct_creat_at, 'N') FROM contract WHERE cntrct_sn = %(s_cntrct_sn)s) AS prjct_creat_at
				FROM rcppay
				WHERE 1=1
				AND ctmmny_sn = '1'
				AND rcppay_sn = %(s_rcppay_sn)s """

    if "s_cntrct_sn" in params and params["s_cntrct_sn"]:
        query += " AND cntrct_sn = %(s_cntrct_sn)s "

    g.curs.execute(query, params)
    result = g.curs.fetchone()
    return result

def insert_rcppay(params):
    data = OrderedDict()
    for key in params:
        if key not in (None,):
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

    query = """INSERT INTO rcppay({}) VALUES ({})""".format(",".join(sub_query), ",".join(params_query))
    g.curs.execute(query, data)
    return g.curs.lastrowid

def update_rcppay(params):
    data = OrderedDict()

    for key in params:
        if key not in ("s_rcppay_sn", ):
            if key in ("cntrct_sn", "prjct_sn", "prvent_sn", "cnnc_sn", "bil_exprn_de", "rcppay_dtls", "papr_invstmnt_sn", ):
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
        params["update_dtm"] = datetime.datetime.now(timezone('Asia/Seoul'))

    if "updater_id" not in params:
        params["updater_id"] = session["member"]["member_id"]

    sub_query = ["{0}=%({0})s".format(key) for key in data]
    query = """UPDATE rcppay SET {} WHERE rcppay_sn=%(s_rcppay_sn)s""".format(",".join(sub_query))
    g.curs.execute(query, params)

def delete_rcppay(params):
    g.curs.execute("DELETE FROM rcppay WHERE rcppay_sn=%(s_rcppay_sn)s", params)

def delete_rcppay_many(params):
    targets = params['rcppay_sns']
    g.curs.execute("DELETE FROM rcppay WHERE rcppay_sn IN ({})".format(",".join(["%s"]*len(targets))), targets)

def copy_rcppays(params):
    query = """SELECT * FROM rcppay WHERE rcppay_sn IN ({})""".format(",".join(["%s"] * len(params['rcppay_sns'])))
    g.curs.execute(query, params['rcppay_sns'])
    rcppays = g.curs.fetchall(transform=False)
    rows = []
    for r in rcppays:
        row = {}
        for key, value in r.items():
            if key.lower() not in ('rcppay_sn', "regist_dtm", "register_id"):
                row[key.lower()] = value

        row['rcppay_de'] = params['rcppay_de']
        row["regist_dtm"] = datetime.datetime.now(timezone('Asia/Seoul'))
        row["register_id"] = session["member"]["member_id"]
        rows.append(row)


    query = "INSERT INTO rcppay({0}) VALUES ({1})".format(",".join(list(rows[0].keys())), ",".join(["%({})s".format(k) for k in list(rows[0].keys())]))
    g.curs.executemany(query, rows)

def get_report(params):
    query = """SELECT r.rcppay_de
				, r.acntctgr_code
				, (SELECT code_nm FROM code WHERE ctmmny_sn=r.ctmmny_sn AND parnts_code='ACNTCTGR_CODE' AND code=r.acntctgr_code) AS acntctgr_nm
				, r.rcppay_dtls
				, r.papr_invstmnt_sn
				, GET_MEMBER_NAME(r.papr_invstmnt_sn, 'M') AS papr_invstmnt_nm
				, r.dept_code
				, (SELECT code_nm FROM code WHERE ctmmny_sn=r.ctmmny_sn AND parnts_code='DEPT_CODE' AND code=r.dept_code) AS dept_nm
				, IF (rcppay_se_code NOT IN ('O'), r.amount, 0) AS i_amount
				, IF (rcppay_se_code IN ('O'), r.amount, 0) AS o_amount
				, r.acnut_code
				, (SELECT code_nm FROM code WHERE ctmmny_sn=r.ctmmny_sn AND parnts_code='ACNUT_CODE' AND code=r.acnut_code) AS acnut_nm
				, c.cntrct_nm
				, (SELECT bcnc_nm FROM bcnc WHERE bcnc_sn=r.prvent_sn) AS bcnc_nm
				FROM rcppay r
				LEFT OUTER JOIN contract c
				ON c.cntrct_sn=r.cntrct_sn
				WHERE 1=1
				AND r.ctmmny_sn = '1'
				AND r.rcppay_de = %(s_rcppay_de)s
				AND r.rcppay_se_code NOT IN ('B') """

    g.curs.execute(query, params)
    result = g.curs.fetchall()
    return result


def get_rcppay_summary1(params):
    query = """SELECT c.code
				, c.estn_code_a
				, GET_ACNUT_RCPPAY_BALANCE(c.code, %(s_rcppay_de)s) AS balance
				, SUM(IF(r.rcppay_se_code NOT IN ('O'), r.amount, 0)) AS i_amount
				, SUM(IF(r.rcppay_se_code IN ('O'), r.amount, 0)) AS o_amount
				FROM code c
				LEFT JOIN rcppay r
				ON c.parnts_code='ACNUT_CODE' AND r.acnut_code=c.code AND r.rcppay_de = %(s_rcppay_de)s AND r.rcppay_se_code NOT IN ('B')
				WHERE c.parnts_code = 'ACNUT_CODE'
				AND c.use_at='Y'
				GROUP BY c.code, c.estn_code_a
				ORDER BY c.code_ordr
"""

    g.curs.execute(query, params)
    result = g.curs.fetchall()
    return result


def get_rcppay_summary11(params):
    query = """SELECT c.code
				, c.code_nm
				, IFNULL(SUM(r.amount),0) AS balance
				, (SELECT IFNULL(SUM(r.amount),0)
				FROM rcppay r
				WHERE r.rcppay_de = %(s_rcppay_de)s
				AND r.rcppay_se_code LIKE 'I%%'
				AND r.acnut_code IS NOT NULL
				AND r.acntctgr_code NOT IN ('103')
				) AS i_amount
				, (SELECT IFNULL(SUM(r.amount),0)
				FROM rcppay r
				WHERE r.rcppay_de = %(s_rcppay_de)s
				AND r.rcppay_se_code = 'O'
				AND r.acnut_code IS NOT NULL
				AND r.acntctgr_code NOT IN ('103')
				) AS o_amount
				FROM code c
				LEFT JOIN (SELECT acnut_code, CASE WHEN rcppay_se_code LIKE 'I%%' THEN 'I' ELSE rcppay_se_code END AS rcppay_se_code, acntctgr_code, rcppay_de, amount FROM rcppay WHERE rcppay_se_code NOT IN ('B')) r
				ON c.code=r.rcppay_se_code AND r.rcppay_de BETWEEN CONCAT(SUBSTRING(%(s_rcppay_de)s,1,7),'-01') AND DATE_ADD(%(s_rcppay_de)s, INTERVAL-1 DAY) AND r.acntctgr_code NOT IN ('103') AND r.acnut_code IS NOT NULL
				WHERE c.parnts_code = 'REPORT_FUND_LABEL1'
				GROUP BY c.code_nm, r.rcppay_se_code
"""

    g.curs.execute(query, params)
    result = g.curs.fetchall()
    return result


def get_rcppay_summary2(params):
    query = """SELECT c.code
				, c.code_nm
				, (SELECT IFNULL(SUM(IF(rcppay_se_code IN ('O'), amount*-1, amount)),0)
				FROM rcppay
				WHERE acntctgr_code = c.code
				AND acnut_code IS NULL
				AND rcppay_de BETWEEN CONCAT(SUBSTRING(%(s_rcppay_de)s,1,4),'-01-01') AND DATE_ADD(%(s_rcppay_de)s, INTERVAL-1 DAY)
				) AS balance
				, SUM(IF(r.rcppay_se_code NOT IN ('O'), r.amount, 0)) AS i_amount
				, SUM(IF(r.rcppay_se_code IN ('O'), r.amount, 0)) AS o_amount
				FROM code c
				LEFT JOIN rcppay r
				ON r.acnut_code IS NULL AND r.acntctgr_code=c.code AND r.rcppay_de = %(s_rcppay_de)s AND r.rcppay_se_code NOT IN ('B')
				WHERE c.parnts_code='ACNTCTGR_CODE_PRT'
				AND c.use_at='Y'				
				GROUP BY c.code, c.code_nm
				ORDER BY c.code_ordr
"""

    g.curs.execute(query, params)
    result = g.curs.fetchall()
    return result

def get_rcppay_summary_s1(params):
    first_day = '{}-01-01'.format(params['s_rcppay_de'].split("-")[0])
    query = """SELECT r.prvent_sn
				, (SELECT bcnc_nm FROM bcnc WHERE bcnc_sn=r.prvent_sn) AS prvent_nm
				, SUM(IF(r.rcppay_se_code IN ('O'), -1*r.amount, r.amount)) AS amount
				FROM rcppay r
				WHERE r.acnut_code IS NULL AND r.acntctgr_code='134' AND r.rcppay_de BETWEEN '{0}' AND %(s_rcppay_de)s
				GROUP BY r.prvent_sn
    """.format(first_day)

    g.curs.execute(query, params)
    result = g.curs.fetchall()
    return result

def get_rcppay_summary_s2(params):
    first_day = '{}-01-01'.format(params['s_rcppay_de'].split("-")[0])
    query = """SELECT r.bil_exprn_de
				, r.prvent_sn
				, (SELECT bcnc_nm FROM bcnc WHERE bcnc_sn=r.prvent_sn) AS prvent_nm
				, SUM(IF(r.rcppay_se_code IN ('O'), -1*r.amount, r.amount)) AS amount
				FROM rcppay r
				WHERE r.acnut_code IS NULL AND r.acntctgr_code='110' AND r.rcppay_de BETWEEN '{0}' AND %(s_rcppay_de)s
				GROUP BY r.prvent_sn, r.bil_exprn_de
				ORDER BY r.bil_exprn_de, prvent_nm""".format(first_day)

    g.curs.execute(query, params)
    result = g.curs.fetchall()
    return result

def get_fund_stat_datatable1(params):
    data = []
    query = """SELECT SUBSTRING(t.rcppay_de,1,7) AS rcppay_de
				, t.acntctgr_code
				, GET_CODE_NAME('ACNTCTGR_CODE', t.acntctgr_code) AS acntctgr_nm
				, SUM(t.i_amount) AS i_amount
				, SUM(t.o_amount) AS o_amount
				FROM (
				SELECT SUBSTRING(r.rcppay_de,1,7) AS rcppay_de
				, r.acntctgr_code
				, GET_CODE_NAME('ACNTCTGR_CODE', r.acntctgr_code) AS acntctgr_nm
				, SUM(IF (r.rcppay_se_code NOT IN ('O'), r.amount, 0)) AS i_amount
				, SUM(IF (r.rcppay_se_code IN ('O'), r.amount, 0)) AS o_amount
				FROM rcppay r
				WHERE r.rcppay_se_code NOT IN ('B')
				AND r.rcppay_de BETWEEN CONCAT(SUBSTRING('{0}',1,7),'-01') AND CONCAT(SUBSTRING('{1}',1,7),'-31') """.format(params['s_rcppay_de1_start'], params['s_rcppay_de1_end'])
    if "s_acntctgr_code" in params and params["s_acntctgr_code"]:
        query += " AND r.acntctgr_code = %s "
        data.append(params['s_acntctgr_code'])

    query += """GROUP BY SUBSTRING(r.rcppay_de,1,7), r.acntctgr_code
				UNION
				SELECT SUBSTRING(c.card_de,1,7) AS rcppay_de
				, c.acntctgr_code
				, GET_CODE_NAME('ACNTCTGR_CODE', c.acntctgr_code) AS acntctgr_nm
				, 0 AS i_amount
				, SUM(IFNULL( c.amount, 0)) AS o_amount
				FROM card c
				WHERE c.card_de BETWEEN CONCAT(SUBSTRING('{0}',1,7),'-01') AND CONCAT(SUBSTRING({1},1,7),'-31') """.format(params['s_rcppay_de1_start'], params['s_rcppay_de1_end'])
    if "s_acntctgr_code" in params and params["s_acntctgr_code"]:
        query += " AND c.acntctgr_code = %s "
        data.append(params['s_acntctgr_code'])

    query += """GROUP BY SUBSTRING(c.card_de,1,7), c.acntctgr_code
				) t
				WHERE 1=1
				GROUP BY SUBSTRING(t.rcppay_de,1,7), t.acntctgr_code """
    g.curs.execute(query, params)
    return dt_query(query, data, params)

def get_fund_stat_summary1(params):
    data = []
    query = """SELECT SUM(t.i_amount) AS i_amount
				, SUM(t.o_amount) AS o_amount
				FROM (
				SELECT SUM(IF (r.rcppay_se_code NOT IN ('O'), r.amount, 0)) AS i_amount
				, SUM(IF (r.rcppay_se_code IN ('O'), r.amount, 0)) AS o_amount
				FROM rcppay r
				WHERE r.rcppay_se_code NOT IN ('B')
				AND r.rcppay_de BETWEEN CONCAT(SUBSTRING('{0}',1,7),'-01') AND CONCAT(SUBSTRING('{1}',1,7),'-31') """.format(params['s_rcppay_de1_start'], params['s_rcppay_de1_end'])

    if "s_acntctgr_code" in params and params["s_acntctgr_code"]:
        query += " AND r.acntctgr_code = %s "
        data.append(params['s_acntctgr_code'])

    query += """UNION
				SELECT 0 AS i_amount
				, SUM(IFNULL( c.amount, 0)) AS o_amount
				FROM card c
				WHERE c.card_de BETWEEN CONCAT(SUBSTRING('{0}',1,7),'-01') AND CONCAT(SUBSTRING('{1}',1,7),'-31') """.format(params['s_rcppay_de1_start'], params['s_rcppay_de1_end'])
    if "s_acntctgr_code" in params and params["s_acntctgr_code"]:
        query += " AND c.acntctgr_code = %s "
        data.append(params['s_acntctgr_code'])

    query += """) t
				WHERE 1=1 
			"""

    g.curs.execute(query, data)
    result = g.curs.fetchone()
    return result

def get_fund_stat_datatable2(params):
    data = []
    query = """SELECT SUBSTRING(t.rcppay_de,1,7) AS rcppay_de
				, t.acntctgr_code
				, GET_CODE_NAME('ACNTCTGR_CODE', t.acntctgr_code) AS acntctgr_nm
				, t.dept_code
				, GET_CODE_NAME('DEPT_CODE', t.dept_code) AS dept_nm
				, SUM(t.i_amount) AS i_amount
				, SUM(t.o_amount) AS o_amount
				, t.types
				FROM (
				SELECT SUBSTRING(r.rcppay_de,1,7) AS rcppay_de
				, r.acntctgr_code
				, GET_CODE_NAME('ACNTCTGR_CODE', r.acntctgr_code) AS acntctgr_nm
				, r.dept_code
				, GET_CODE_NAME('DEPT_CODE', r.dept_code) AS dept_nm
				, SUM(IF (r.rcppay_se_code NOT IN ('O'), r.amount, 0)) AS i_amount
				, SUM(IF (r.rcppay_se_code IN ('O'), r.amount, 0)) AS o_amount
				, 'B' AS types
				FROM rcppay r
				WHERE r.rcppay_se_code NOT IN ('B')
				AND r.rcppay_de BETWEEN CONCAT(SUBSTRING('{0}',1,7),'-01') AND CONCAT(SUBSTRING('{1}',1,7),'-31') """.format(params['s_rcppay_de2_start'], params['s_rcppay_de2_end'])

    if "s_acntctgr_code" in params and params["s_acntctgr_code"]:
        query += " AND r.acntctgr_code = %s "
        data.append(params['s_acntctgr_code'])

    if "s_dept_code" in params and params["s_dept_code"]:
        query += " AND r.dept_code = %s "
        data.append(params['s_dept_code'])

    query += """GROUP BY SUBSTRING(r.rcppay_de,1,7), r.dept_code, r.acntctgr_code
				UNION
				SELECT SUBSTRING(c.card_de,1,7) AS rcppay_de
				, c.acntctgr_code
				, GET_CODE_NAME('ACNTCTGR_CODE', c.acntctgr_code) AS acntctgr_nm
				, c.dept_code
				, GET_CODE_NAME('DEPT_CODE', c.dept_code) AS dept_nm
				, 0 AS i_amount
				, SUM(IFNULL (c.amount, 0)) AS o_amount
				, 'C' AS types
				FROM card c
				WHERE c.card_de BETWEEN CONCAT(SUBSTRING('{0}',1,7),'-01') AND CONCAT(SUBSTRING('{1}',1,7),'-31') """.format(params['s_rcppay_de2_start'], params['s_rcppay_de2_end'])

    if "s_acntctgr_code" in params and params["s_acntctgr_code"]:
        query += " AND c.acntctgr_code = %s "
        data.append(params['s_acntctgr_code'])

    if "s_dept_code" in params and params["s_dept_code"]:
        query += " AND c.dept_code = %s "
        data.append(params['s_dept_code'])

    query += """GROUP BY SUBSTRING(c.card_de,1,7), c.dept_code, c.acntctgr_code
				) t
				WHERE 1=1 """
    if "s_types" in params and params["s_types"]:
        query += " AND types=%s "
        data.append(params["s_types"])
    query += """ GROUP BY SUBSTRING(t.rcppay_de,1,7), t.dept_code, t.acntctgr_code, t.types """


    return dt_query(query, data, params)


def get_fund_stat_summary2(params):
    data = []
    query = """SELECT SUM(t.i_amount) AS i_amount
				, SUM(t.o_amount) AS o_amount
				FROM (
				SELECT SUM(IF (r.rcppay_se_code NOT IN ('O'), r.amount, 0)) AS i_amount
				, SUM(IF (r.rcppay_se_code IN ('O'), r.amount, 0)) AS o_amount
				FROM rcppay r
				WHERE r.rcppay_se_code NOT IN ('B')
				AND r.rcppay_de BETWEEN CONCAT(SUBSTRING('{0}',1,7),'-01') AND CONCAT(SUBSTRING('{1}',1,7),'-31')""".format(params['s_rcppay_de2_start'], params['s_rcppay_de2_end'])

    if "s_acntctgr_code" in params and params["s_acntctgr_code"]:
        query += " AND r.acntctgr_code = %s "
        data.append(params['s_acntctgr_code'])

    if "s_dept_code" in params and params["s_dept_code"]:
        query += " AND r.dept_code = %s "
        data.append(params['s_dept_code'])

    query += """UNION
				SELECT 0 AS i_amount
				, SUM(IFNULL (c.amount, 0)) AS o_amount
				FROM card c
				WHERE c.card_de BETWEEN CONCAT(SUBSTRING('{0}',1,7),'-01') AND CONCAT(SUBSTRING('{1}',1,7),'-31') """.format(params['s_rcppay_de2_start'], params['s_rcppay_de2_end'])


    if "s_acntctgr_code" in params and params["s_acntctgr_code"]:
        query += " AND c.acntctgr_code = %s "
        data.append(params['s_acntctgr_code'])

    if "s_dept_code" in params and params["s_dept_code"]:
        query += " AND c.dept_code = %s "
        data.append(params['s_dept_code'])

    query += """) t
				WHERE 1=1 """

    g.curs.execute(query, data)
    result = g.curs.fetchone()
    return result

def insert_memo(params):
    data = {}
    if "memo_ty" in params and params["memo_ty"]:
        data["memo_ty"] = params["memo_ty"]

    if "memo_id" in params and params["memo_id"]:
        data["memo_id"] = params["memo_id"]

    if "memo_de" in params and params["memo_de"]:
        data["memo_de"] = params["memo_de"]

    if "memo" in params:
        data["memo"] = params["memo"]

    if "regist_dtm" in params and params["regist_dtm"]:
        data["regist_dtm"] = params["regist_dtm"]
    else:
        data["regist_dtm"] = datetime.datetime.now(timezone('Asia/Seoul')).strftime("%Y-%m-%d %H:%M:%S")

    if "register_id" in params and params["register_id"]:
        data["register_id"] = params["register_id"]
    else:
        data["register_id"] = session['member']['member_id']

    columns = list(data.keys())
    query = """INSERT INTO memo({}) VALUES ({})""".format(",".join(columns), ",".join(["%({})s".format(c) for c in columns]))
    g.curs.execute(query, data)


def get_memo_list2(params):
    query = """SELECT memo_ty
				, memo_id
				, memo
				FROM memo m
				WHERE memo_sn IN (SELECT MAX(memo_sn) FROM memo WHERE memo_ty = %(s_memo_ty)s AND memo_de = %(s_memo_de)s GROUP BY memo_ty, memo_id)
				AND memo_id <> ''
				AND memo_de = %(s_memo_de)s"""
    g.curs.execute(query, params)
    result = g.curs.fetchall()
    return result

def get_values(params):
    query = "SELECT * FROM temp WHERE temp_dtm = %(rpt7_ddt_man)s"
    g.curs.execute(query, params)
    result = g.curs.fetchall()
    return result