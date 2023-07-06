from flask import session, jsonify, g
from app.helpers.datatable_helper import dt_query
from collections import OrderedDict
import datetime
import calendar
from pytz import timezone

def get_cardbil_datatable(params):
    query = """SELECT ca.ctmmny_sn
				, ca.cntrct_sn
				, card_sn
				, card_de
				, card_time
				, acntctgr_code
				, card_code
				, (SELECT code_nm FROM code WHERE ctmmny_sn=1 AND parnts_code='CARD_CODE' AND code=ca.card_code) AS card_nm
				, (SELECT code_nm FROM code WHERE ctmmny_sn=1 AND parnts_code='ACNTCTGR_CODE' AND code=ca.acntctgr_code) AS acntctgr_nm
				, frch_nm
				, region
				, card_dtls
				, papr_invstmnt_sn
				, GET_MEMBER_NAME(papr_invstmnt_sn, 'M') AS papr_invstmnt_nm
				, dept_code
				, (SELECT code_nm FROM code WHERE ctmmny_sn=1 AND parnts_code='DEPT_CODE' AND code=ca.dept_code) AS dept_nm
				, IFNULL(amount, '') AS amount
				, ca.regist_dtm
				, ca.register_id
				, ca.update_dtm
				, ca.updater_id
				, c.cntrct_no
				, c.spt_nm
				FROM card ca
				LEFT OUTER JOIN contract c
				ON ca.cntrct_sn=c.cntrct_sn
				WHERE 1=1
				AND ca.ctmmny_sn = '1'
				AND ca.card_de BETWEEN '{0} 00:00:00'
				AND '{1} 23:59:59' """.format(params['s_card_de_start'], params['s_card_de_end'])

    data = []
    if "s_card_code" in params and params['s_card_code']:
        query += " AND ca.card_code=%s"
        data.append(params["s_card_code"])

    if "s_spt_nm" in params and params['s_spt_nm']:
        query += " AND c.spt_nm LIKE %s"
        data.append('%{}%'.format(params["s_spt_nm"]))

    if "s_card_dtls" in params and params['s_card_dtls']:
        query += " AND ca.card_dtls LIKE %s"
        data.append('%{}%'.format(params["s_card_dtls"]))

    if "s_region" in params and params['s_region']:
        query += " AND ca.region LIKE %s"
        data.append('%{}%'.format(params["s_region"]))

    if "s_frch_nm" in params and params['s_frch_nm']:
        query += " AND ca.frch_nm LIKE %s"
        data.append('%{}%'.format(params["s_frch_nm"]))

    if "s_acntctgr_code" in params and params['s_acntctgr_code']:
        query += " AND ca.acntctgr_code=%s"
        data.append(params["s_acntctgr_code"])

    if "s_papr_invstmnt_sn" in params and params['s_papr_invstmnt_sn']:
        query += " AND ca.papr_invstmnt_sn=%s"
        data.append(params["s_papr_invstmnt_sn"])

    if "s_dept_code" in params and params['s_dept_code']:
        query += " AND ca.dept_code=%s"
        data.append(params["s_dept_code"])

    params["custom_order"] = ["card_de DESC", "card_time DESC"]

    return dt_query(query, data, params)

def get_cardbil_summary(params):
    query = """SELECT IFNULL(COUNT(ca.card_sn),0) AS total_count
				, IFNULL(SUM(ca.amount),0) AS total_amount
				FROM card ca
				LEFT OUTER JOIN contract c
				ON ca.cntrct_sn=c.cntrct_sn
				WHERE 1=1
				AND ca.ctmmny_sn = '1'
				AND ca.card_de BETWEEN '{0} 00:00:00'
				AND '{1} 23:59:59' """.format(params['s_card_de_start'], params['s_card_de_end'])

    data = []
    if "s_card_code" in params and params['s_card_code']:
        query += " AND ca.card_code=%s"
        data.append(params["s_card_code"])

    if "s_spt_nm" in params and params['s_spt_nm']:
        query += " AND c.spt_nm LIKE %s"
        data.append('%{}%'.format(params["s_spt_nm"]))

    if "s_card_dtls" in params and params['s_card_dtls']:
        query += " AND ca.card_dtls LIKE %s"
        data.append('%{}%'.format(params["s_card_dtls"]))

    if "s_region" in params and params['s_region']:
        query += " AND ca.region LIKE %s"
        data.append('%{}%'.format(params["s_region"]))

    if "s_frch_nm" in params and params['s_frch_nm']:
        query += " AND ca.frch_nm LIKE %s"
        data.append('%{}%'.format(params["s_frch_nm"]))

    if "s_acntctgr_code" in params and params['s_acntctgr_code']:
        query += " AND ca.acntctgr_code=%s"
        data.append(params["s_acntctgr_code"])

    if "s_papr_invstmnt_sn" in params and params['s_papr_invstmnt_sn']:
        query += " AND ca.papr_invstmnt_sn=%s"
        data.append(params["s_papr_invstmnt_sn"])

    if "s_dept_code" in params and params['s_dept_code']:
        query += " AND ca.dept_code=%s"
        data.append(params["s_dept_code"])

    g.curs.execute(query, data)
    result = g.curs.fetchone()
    return result

def get_cardbil(params):
    query = """SELECT ctmmny_sn
				, cntrct_sn
				, card_code
				, card_sn
				, card_de
				, card_time
				, frch_nm
				, region
				, acntctgr_code
				, card_dtls
				, papr_invstmnt_sn
				, dept_code
				, amount
				, regist_dtm
				, register_id
				, update_dtm
				, updater_id
				FROM card
				WHERE 1=1
				AND ctmmny_sn = '1'
				AND card_sn = %(s_card_sn)s """
    g.curs.execute(query, params)
    result = g.curs.fetchone()
    return result


def insert_cardbil(params):
    data = OrderedDict()
    for key in params:
        if key not in ("cntrct_sn", "papr_invstmnt_sn", "dept_code"):
            if params[key] != '':
                data[key] = params[key]
        else:
            if params[key] == '':
                data[key] = 0
            else:
                data[key] = params[key]

    if "ctmmny_sn" not in data:
        data["ctmmny_sn"] = 1

    if "regist_dtm" not in data:
        data["regist_dtm"] = datetime.datetime.now(timezone('Asia/Seoul'))

    if "update_dtm" not in data:
        data["update_dtm"] = datetime.datetime.now(timezone('Asia/Seoul'))

    if "register_id" not in data:
        data["register_id"] = session["member"]["member_id"]

    if "updater_id" not in params:
        data["updater_id"] = session["member"]["member_id"]

    if "card_dtls" not in data:
        data["card_dtls"] = ""


    sub_query = [key for key in data]
    params_query = ["%({})s".format(key) for key in data]

    query = """INSERT INTO card({}) VALUES ({})""".format(",".join(sub_query), ",".join(params_query))
    g.curs.execute(query, data)
    return g.curs.lastrowid

def update_cardbil(params):
    data = OrderedDict()

    for key in params:
        if key not in ("s_card_sn", ):
            if key in ("cntrct_sn", "card_dtls",'papr_invstmnt_sn'):
                if params[key] == '':
                    if key in ('cntrct_sn','papr_invstmnt_sn') :
                        params[key] = 0
                        data[key] = 0
                    elif key in ('card_dtls', ):
                        params[key] = ''
                        data[key] = ''
                    else:
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
    query = """UPDATE card SET {} WHERE card_sn=%(s_card_sn)s""".format(",".join(sub_query))
    g.curs.execute(query, params)

def delete_cardbil(params):
    g.curs.execute("DELETE FROM card WHERE card_sn=%(s_card_sn)s", params)

def get_card_dashboard(params):
    query = """SELECT SUM(IF (SUBSTRING(r.card_de,6,2) = '01', r.amount, 0)) AS m01
				, SUM(IF (SUBSTRING(r.card_de,6,2) = '02', r.amount, 0)) AS m02
				, SUM(IF (SUBSTRING(r.card_de,6,2) = '03', r.amount, 0)) AS m03
				, SUM(IF (SUBSTRING(r.card_de,6,2) = '04', r.amount, 0)) AS m04
				, SUM(IF (SUBSTRING(r.card_de,6,2) = '05', r.amount, 0)) AS m05
				, SUM(IF (SUBSTRING(r.card_de,6,2) = '06', r.amount, 0)) AS m06
				, SUM(IF (SUBSTRING(r.card_de,6,2) = '07', r.amount, 0)) AS m07
				, SUM(IF (SUBSTRING(r.card_de,6,2) = '08', r.amount, 0)) AS m08
				, SUM(IF (SUBSTRING(r.card_de,6,2) = '09', r.amount, 0)) AS m09
				, SUM(IF (SUBSTRING(r.card_de,6,2) = '10', r.amount, 0)) AS m10
				, SUM(IF (SUBSTRING(r.card_de,6,2) = '11', r.amount, 0)) AS m11
				, SUM(IF (SUBSTRING(r.card_de,6,2) = '12', r.amount, 0)) AS m12
				, SUM(IF (SUBSTRING(r.card_de,6,2) = '01', 1, 0)) AS c01
				, SUM(IF (SUBSTRING(r.card_de,6,2) = '02', 1, 0)) AS c02
				, SUM(IF (SUBSTRING(r.card_de,6,2) = '03', 1, 0)) AS c03
				, SUM(IF (SUBSTRING(r.card_de,6,2) = '04', 1, 0)) AS c04
				, SUM(IF (SUBSTRING(r.card_de,6,2) = '05', 1, 0)) AS c05
				, SUM(IF (SUBSTRING(r.card_de,6,2) = '06', 1, 0)) AS c06
				, SUM(IF (SUBSTRING(r.card_de,6,2) = '07', 1, 0)) AS c07
				, SUM(IF (SUBSTRING(r.card_de,6,2) = '08', 1, 0)) AS c08
				, SUM(IF (SUBSTRING(r.card_de,6,2) = '09', 1, 0)) AS c09
				, SUM(IF (SUBSTRING(r.card_de,6,2) = '10', 1, 0)) AS c10
				, SUM(IF (SUBSTRING(r.card_de,6,2) = '11', 1, 0)) AS c11
				, SUM(IF (SUBSTRING(r.card_de,6,2) = '12', 1, 0)) AS c12
				FROM card r
				WHERE 1=1
				AND r.ctmmny_sn = '1'
				AND r.card_de BETWEEN '{0} 00:00:00' AND '{1} 23:59:59' """.format("{}-01-01".format(params['card_de'].split("-")[0]), "{}-12-31".format(params['card_de'].split("-")[0]))
    g.curs.execute(query)
    result = g.curs.fetchall()
    return result

def get_report(params, card_code):
    ymd = params['card_de']
    y, m, d = ymd.split("-")
    _, l = calendar.monthrange(int(y), int(m))
    f = 1
    first_day = "{}-{}-{}".format(y.zfill(4), m.zfill(2), str(f).zfill(2))
    last_day = "{}-{}-{}".format(y.zfill(4), m.zfill(2), str(l).zfill(2))

    query = """SELECT r.card_de
				, r.card_time
				, r.frch_nm
				, r.region
				, r.amount
				, r.papr_invstmnt_sn
				, (SELECT mber_nm FROM member WHERE mber_sn=r.papr_invstmnt_sn) AS papr_invstmnt_nm
				, r.dept_code
				, (SELECT co.code_ordr FROM code co WHERE co.parnts_code='DEPT_CODE' AND code=r.dept_code) AS code_order
				, (SELECT code_nm FROM code WHERE ctmmny_sn=r.ctmmny_sn AND parnts_code='DEPT_CODE' AND code=r.dept_code) AS dept_nm
				, (SELECT code_nm FROM code WHERE ctmmny_sn=r.ctmmny_sn AND parnts_code='ACNTCTGR_CODE' AND code=r.acntctgr_code) AS acntctgr_nm
				, r.card_dtls
				, c.spt_nm
				FROM card r
				LEFT OUTER JOIN contract c
				ON c.cntrct_sn=r.cntrct_sn
				WHERE 1=1
				AND r.ctmmny_sn = '1'
				AND r.card_de BETWEEN '{0} 00:00:00' AND '{1} 23:59:59'
				AND r.card_code = '{2}'
				ORDER BY r.card_de DESC, if(r.card_time = '' or ISNULL(r.card_time),1,0) ASC, r.card_time desc """.format(first_day, last_day, card_code)

    g.curs.execute(query)
    result = g.curs.fetchall()
    return result


def get_total(params, card_code):
    ymd = params['card_de']
    y, m, d = ymd.split("-")
    _, l = calendar.monthrange(int(y), int(m))
    f = 1
    first_day = "{}-{}-{}".format(y.zfill(4), m.zfill(2), str(f).zfill(2))
    last_day = "{}-{}-{}".format(y.zfill(4), m.zfill(2), str(l).zfill(2))

    query = """SELECT SUM(r.amount) AS total
				FROM card r
				WHERE 1=1
				AND r.ctmmny_sn = '1'
				AND r.card_de BETWEEN '{0} 00:00:00' AND '{1} 23:59:59'
				AND r.card_code = '{2}' """.format(first_day, last_day, card_code)
    g.curs.execute(query)
    result = g.curs.fetchall()
    return result

def get_card_dashboard_year(params):
    query = """SELECT r.dept_code
				, (SELECT code_nm FROM code WHERE code=r.dept_code AND parnts_code='DEPT_CODE') AS dept_nm
				, (SELECT code_ordr FROM code WHERE code=r.dept_code AND parnts_code='DEPT_CODE') AS ordr
				, SUM(IF (SUBSTRING(r.card_de,6,2) = '01', r.amount, 0)) AS m01
				, SUM(IF (SUBSTRING(r.card_de,6,2) = '02', r.amount, 0)) AS m02
				, SUM(IF (SUBSTRING(r.card_de,6,2) = '03', r.amount, 0)) AS m03
				, SUM(IF (SUBSTRING(r.card_de,6,2) = '04', r.amount, 0)) AS m04
				, SUM(IF (SUBSTRING(r.card_de,6,2) = '05', r.amount, 0)) AS m05
				, SUM(IF (SUBSTRING(r.card_de,6,2) = '06', r.amount, 0)) AS m06
				, SUM(IF (SUBSTRING(r.card_de,6,2) = '07', r.amount, 0)) AS m07
				, SUM(IF (SUBSTRING(r.card_de,6,2) = '08', r.amount, 0)) AS m08
				, SUM(IF (SUBSTRING(r.card_de,6,2) = '09', r.amount, 0)) AS m09
				, SUM(IF (SUBSTRING(r.card_de,6,2) = '10', r.amount, 0)) AS m10
				, SUM(IF (SUBSTRING(r.card_de,6,2) = '11', r.amount, 0)) AS m11
				, SUM(IF (SUBSTRING(r.card_de,6,2) = '12', r.amount, 0)) AS m12
				, SUM(r.amount) AS mtotal
				FROM card r
				WHERE 1=1
				AND r.ctmmny_sn = '1'
				AND r.card_de BETWEEN '{0} 00:00:00' AND '{1} 23:59:59'
				GROUP BY r.dept_code
				ORDER BY ordr """.format("{}-01-01".format(params["card_de"].split("-")[0]), "{}-12-31".format(params["card_de"].split("-")[0]))

    g.curs.execute(query)
    result = g.curs.fetchall()
    return result