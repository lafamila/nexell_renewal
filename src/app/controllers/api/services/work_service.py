from flask import session, jsonify, g
from app.helpers.datatable_helper import dt_query
from collections import OrderedDict
import datetime
import calendar

def get_work_datatable(params):
    last_years = int(params["s_stdyy"].split("-")[0])-1
    last = "{}-{}-{}".format(last_years, params["s_stdyy"].split("-")[1], params["s_stdyy"].split("-")[2])
    # TODO : use, last_use를 휴가 결재 내역에서 가져올것
    query = """SELECT '{0}' AS stdyy
                    , m.mber_sn
                    , m.mber_nm
                    , m.dept_code
                    , (SELECT code_nm FROM code WHERE ctmmny_sn=1 AND parnts_code='DEPT_CODE' AND code=m.dept_code) AS dept_nm
                    , m.mber_sttus_code
                    , (SELECT code_nm FROM code WHERE ctmmny_sn=1 AND parnts_code='MBER_STTUS_CODE' AND code=m.mber_sttus_code) AS mber_sttus_nm
                    , m.enter_de
                    , IF(m.mber_sttus_code = 'R', DATE_FORMAT(m.update_dtm, %s), '') AS out_dtm
                    , IFNULL((SELECT work_data FROM work WHERE work_year='{3}' AND work_row=m.mber_sn AND work_month='tot'), (15 + FLOOR(DATEDIFF('{1}', m.enter_de)/730))) AS last_tot
                    , IFNULL((SELECT work_data FROM work WHERE work_year='{2}' AND work_row=m.mber_sn AND work_month='tot'), (15 + FLOOR(DATEDIFF('{0}', m.enter_de)/730))) AS tot
                    , IFNULL((SELECT work_data FROM work WHERE work_year='{3}' AND work_row=m.mber_sn AND work_month='mod'), 0) AS last_mod
                    , IFNULL((SELECT work_data FROM work WHERE work_year='{2}' AND work_row=m.mber_sn AND work_month='mod'), 0) AS `mod`
                    , IFNULL((SELECT work_data FROM work WHERE work_year='{3}' AND work_row=m.mber_sn AND work_month='use'), 0) AS last_use
                    , IFNULL((SELECT work_data FROM work WHERE work_year='{2}' AND work_row=m.mber_sn AND work_month='use'), 0) AS `use`
                    , IFNULL((SELECT work_data FROM work WHERE work_year='{2}' AND work_row=m.mber_sn AND work_month='rm'), '') AS rm
    				, (SELECT code_ordr FROM code WHERE parnts_code='DEPT_CODE' AND code=m.dept_code) AS code_ordr
                    FROM member m
                    WHERE m.enter_de <= '{0}'
            """.format(params["s_stdyy"], last, last_years+1, last_years)
    data = ['%Y-%m-%d']
    if "s_dept_code" in params and params["s_dept_code"]:
        query += " and m.dept_code=%s"
        data.append(params["s_dept_code"])

    if "s_mber_sn" in params and params["s_mber_sn"]:
        query += " and m.mber_sn=%s"
        data.append(params["s_mber_sn"])

    if "s_mber_sttus_code" in params and params["s_mber_sttus_code"]:
        query += " and m.mber_sttus_code=%s"
        data.append(params["s_mber_sttus_code"])

    if "s_cal_year" in params and params["s_cal_year"]:
        query += " and FLOOR(DATEDIFF('{0}', m.enter_de)/365)=%s".format(params["s_stdyy"])
        data.append(int(params["s_cal_year"])-1)

    query += " ORDER BY code_ordr, mber_nm"
    return dt_query(query, data, params)

def get_work_time(params):
    y, m, d = params["calendar"].split("-")
    query = """SELECT workdate AS work_date
                    , WSTime AS start_time
                    , WCTime AS end_time 
                FROM t_secom_workhistory 
                WHERE WorkDate LIKE %s AND Name=%s AND WSTime <> ''"""
    data = ['{0}{1}%'.format(y, m), params['s_mber_nm']]
    g.curs.execute(query, data)
    result = g.curs.fetchall()
    return result

def get_work_calendar(params):
    cal = calendar.TextCalendar()
    cal.setfirstweekday(calendar.SUNDAY)
    y, m, d = params["calendar"].split("-")
    text = cal.formatmonth(int(y), int(m)).strip()
    title = text.split("\n")[0]
    result = []
    for row in text.split("\n")[2:]:
        rowlist = list()
        for i in range(len(row)//3+1):
            cell = row[3*i:3*i+2]
            if cell.strip() != '':
                cell = int(cell)
            else:
                cell = ''
            rowlist.append(cell)
        result.append(rowlist)
    return {"title" : title, "rows" : result}

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


def set_work_data(params):
    row = g.curs.execute("SELECT work_sn FROM work WHERE work_year=%(work_year)s AND work_row=%(work_row)s AND work_month=%(work_month)s", params)
    if row:
        result = g.curs.fetchone()
        params['work_sn'] = result['work_sn']
        g.curs.execute("UPDATE work SET work_data=%(work_data)s WHERE work_sn=%(work_sn)s", params)

    else:
        g.curs.execute("INSERT INTO work(work_year, work_row, work_month, work_data) VALUES(%(work_year)s, %(work_row)s, %(work_month)s, %(work_data)s)", params)
