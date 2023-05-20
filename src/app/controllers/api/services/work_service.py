from flask import session, jsonify, g
from app.helpers.datatable_helper import dt_query
from collections import OrderedDict
import datetime
import calendar

def get_work_datatable(params):
    last_years = int(params["s_stdyy"].split("-")[0])-1
    last = "{}-{}-{}".format(last_years, params["s_stdyy"].split("-")[1], params["s_stdyy"].split("-")[2])
    query = """SELECT '{0}' AS stdyy
                    , m.mber_sn
                    , m.mber_nm
                    , m.dept_code
                    , (SELECT code_nm FROM code WHERE ctmmny_sn=1 AND parnts_code='DEPT_CODE' AND code=m.dept_code) AS dept_nm
                    , m.mber_sttus_code
                    , (SELECT code_nm FROM code WHERE ctmmny_sn=1 AND parnts_code='MBER_STTUS_CODE' AND code=m.mber_sttus_code) AS mber_sttus_nm
                    , m.enter_de
                    , IF(m.mber_sttus_code = 'R', DATE_FORMAT(m.out_de, %s), '') AS out_dtm
                    , IFNULL((SELECT work_data FROM work WHERE work_year='{3}' AND work_row=m.mber_sn AND work_month='tot'), (15 + FLOOR(DATEDIFF('{1}', m.enter_de)/730))) AS last_tot
                    , IFNULL((SELECT work_data FROM work WHERE work_year='{2}' AND work_row=m.mber_sn AND work_month='tot'), (15 + FLOOR(DATEDIFF('{0}', m.enter_de)/730))) AS tot
                    , IFNULL((SELECT work_data FROM work WHERE work_year='{3}' AND work_row=m.mber_sn AND work_month='mod'), 0) AS last_mod
                    , IFNULL((SELECT work_data FROM work WHERE work_year='{2}' AND work_row=m.mber_sn AND work_month='mod'), 0) AS `mod`
                    , IFNULL((SELECT work_data FROM work WHERE work_year='{3}' AND work_row=m.mber_sn AND work_month='use'), IFNULL((SELECT SUM(IF(vacation_type IN (2, 3, 5, 6), 0.5, 1)) FROM vacation WHERE mber_sn=m.mber_sn AND YEAR(vacation_de)='{3}' AND vacation_type IN (1, 2, 3, 4, 5, 6, 7)), 0)) AS last_use
                    , IFNULL((SELECT work_data FROM work WHERE work_year='{2}' AND work_row=m.mber_sn AND work_month='use'), IFNULL((SELECT SUM(IF(vacation_type IN (2, 3, 5, 6), 0.5, 1)) FROM vacation WHERE mber_sn=m.mber_sn AND YEAR(vacation_de)='{2}' AND vacation_type IN (1, 2, 3, 4, 5, 6, 7)), 0)) AS `use`
                    , IFNULL((SELECT work_data FROM work WHERE work_year='{2}' AND work_row=m.mber_sn AND work_month='rm'), '') AS rm
    				, (SELECT code_ordr FROM code WHERE parnts_code='DEPT_CODE' AND code=m.dept_code) AS code_ordr
    				, IFNULL((SELECT COUNT(*) FROM vacation WHERE mber_sn=m.mber_sn AND YEAR(vacation_de)='{2}' AND vacation_type IN (8, 9)), 0) AS `out`
                    FROM member m
                    WHERE m.enter_de <= '{0}'
                    AND m.dept_code <> ''
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

    query += " ORDER BY code_ordr, mber_sttus_code, mber_nm"
    return dt_query(query, data, params)

def get_work_time(params):
    y, m, d = params["calendar"].split("-")
    query = """SELECT workdate AS work_date
                    , WSTime AS start_time
                    , WCTime AS end_time 
                FROM T_SECOM_WORKHISTORY
                WHERE WorkDate LIKE %s AND Name=%s AND WSTime <> ''"""
    data = ['{0}{1}%'.format(y, m), params['s_mber_nm']]
    g.curs.execute(query, data)
    result = g.curs.fetchall()
    return result

def get_vacation_member(params):
    query = """SELECT mber_sn
                , vacation_type
                , vacation_de
                , (SELECT code_nm FROM code WHERE parnts_code='VACATION_TYPE_CODE' AND code=vacation_type) AS vacation_type_nm
                , rm
                FROM vacation WHERE mber_sn=%(s_mber_sn)s"""
    g.curs.execute(query, params)
    result = g.curs.fetchall()
    return result

def get_work_daily_summary(params, limit):
    query = """SELECT COUNT(*) AS total_count
                    , SUM(IF((w.WSTime IS NOT NULL AND w.WSTime > %s),1, 0)) AS rate_count
                    , SUM(IF((v.vacation_type IN (1,4,7)), 1, 0)) AS off_count
                    , SUM(IF((v.vacation_type IN (8, 9)), 1, 0)) AS out_count
                FROM member m
                LEFT OUTER JOIN (SELECT * FROM T_SECOM_WORKHISTORY WHERE workdate=%s) w 
                ON m.mber_nm=w.Name
                LEFT OUTER JOIN (SELECT * FROM vacation WHERE vacation_de=%s AND vacation_type In (1, 4, 7, 8, 9)) v
                ON m.mber_sn=v.mber_sn
                WHERE 1=1
                AND m.mber_sttus_code='H'
                AND m.dept_code <> ''
            """
    data = [params['s_calendar'].replace("-", "")+limit+"00", params['s_calendar'].replace("-", ""), params['s_calendar']]
    if "s_mber_nm" in params and params["s_mber_nm"]:
        query += " AND m.mber_nm LIKE %s"
        data.append("%{}%".format(params['s_mber_nm']))

    if "s_dept_code" in params and params["s_dept_code"]:
        query += " AND m.dept_code = %s"
        data.append(params['s_dept_code'])

    if "s_ofcps_code" in params and params["s_ofcps_code"]:
        query += " AND m.ofcps_code = %s"
        data.append(params['s_ofcps_code'])

    g.curs.execute(query, data)
    result = g.curs.fetchone()
    return result

def get_vacation(params):
    query = """SELECT mber_sn
                , vacation_type
                , (SELECT code_nm FROM code WHERE parnts_code='VACATION_TYPE_CODE' AND code=vacation_type) AS vacation_type_nm
                , rm
                FROM vacation WHERE vacation_de=%(s_calendar)s"""
    g.curs.execute(query, params)
    result = g.curs.fetchall()
    return result
def get_work_daily_datatable(params):
    query = """SELECT '1' AS ctmmny_sn
                    , m.mber_sn
                    , m.mber_nm
                    , m.ofcps_code
                    , (SELECT code_nm FROM code WHERE parnts_code='OFCPS_CODE' AND code=m.ofcps_code) AS ofcps_nm
                    , m.dept_code
                    , (SELECT code_nm FROM code WHERE parnts_code='DEPT_CODE' AND code=m.dept_code) AS dept_nm
                    , w.WSTime AS status
                    , w.WSTime AS start_time
                    , w.WCTime AS end_time
                FROM member m
                LEFT OUTER JOIN (SELECT * FROM T_SECOM_WORKHISTORY WHERE workdate=%s) w 
                ON m.mber_nm=w.Name
                WHERE 1=1
                AND m.mber_sttus_code='H'
                AND m.dept_code <> ''
            """
    data = [params['s_calendar'].replace("-", "")]
    if "s_mber_nm" in params and params["s_mber_nm"]:
        query += " AND m.mber_nm LIKE %s"
        data.append("%{}%".format(params['s_mber_nm']))

    if "s_dept_code" in params and params["s_dept_code"]:
        query += " AND m.dept_code = %s"
        data.append(params['s_dept_code'])

    if "s_ofcps_code" in params and params["s_ofcps_code"]:
        query += " AND m.ofcps_code = %s"
        data.append(params['s_ofcps_code'])


    return dt_query(query, data, params)


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

def get_work_data(params):
    g.curs.execute("SELECT work_sn, work_year, work_row, work_month, work_data, work_class FROM work WHERE work_year=%s", params['work_date'].split("-")[0])
    result = g.curs.fetchall()
    return result


def get_work(params):
    work_date = params['work_date']
    work_year = work_date.split("-")[0]
    query = """SELECT '1' AS ctmmny_sn
                    , m.mber_sn
                    , m.mber_nm
                    , m.ofcps_code
                    , (SELECT code_nm FROM code WHERE parnts_code='OFCPS_CODE' AND code=m.ofcps_code) AS ofcps_nm
                    , m.dept_code
                    , (SELECT code_nm FROM code WHERE parnts_code='DEPT_CODE' AND code=m.dept_code) AS dept_nm
                    , IF(m.check_rate='1', IFNULL(wt.rate_tot, 0), 0) AS rate_count
                    , IFNULL((SELECT work_data FROM work WHERE work_year='{1}' AND work_row=m.mber_sn AND work_month='tot2'), (15 + FLOOR(DATEDIFF('{0}', m.enter_de)/730))) AS tot
                    , (SELECT COUNT(*) FROM vacation WHERE mber_sn=m.mber_sn AND YEAR(vacation_de)='{1}' AND vacation_type IN (1, 4, 7)) AS `use`
                    , (SELECT COUNT(*) FROM vacation WHERE mber_sn=m.mber_sn AND YEAR(vacation_de)='{1}' AND vacation_type IN (2, 3, 5, 6)) AS `half`
                    , IFNULL((SELECT work_data FROM work WHERE work_year='{1}' AND work_row=m.mber_sn AND work_month='rm2'), '') AS rm
                    , IF(w.WSTime IS NULL OR w.WSTime='', 0,
                    CASE DAYOFWEEK(STR_TO_DATE(w.WorkDate, %s))-1
                        WHEN 0 THEN 0
                        WHEN 6 THEN 0
                        WHEN 1 THEN IF(SUBSTRING(w.WSTime, 9, 4) > '0900', 1, 0)
                        ELSE IF(SUBSTRING(w.WSTime, 9, 4) > '0840', 1, 0)
                    END) AS today_rate
                    , (SELECT GROUP_CONCAT(DATE_FORMAT(vacation_de, '%%m/%%d')) FROM vacation WHERE mber_sn=m.mber_sn AND YEAR(vacation_de)='{1}' AND vacation_type IN (1, 4, 7)) AS use_dates
                    , (SELECT GROUP_CONCAT(DATE_FORMAT(vacation_de, '%%m/%%d')) FROM vacation WHERE mber_sn=m.mber_sn AND YEAR(vacation_de)='{1}' AND vacation_type IN (2,3,5,6)) AS half_dates
    				, (SELECT code_ordr FROM code WHERE parnts_code='DEPT_CODE' AND code=m.dept_code) AS code_ordr
    				, (SELECT code_ordr FROM code WHERE parnts_code='OFCPS_CODE' AND code=m.ofcps_code) AS ofcps_ordr
                FROM (SELECT mber_sn, mber_nm, ofcps_code, dept_code, enter_de, check_rate FROM member WHERE check_work='1' AND mber_sttus_code='H' AND dept_code <> '') m
                LEFT OUTER JOIN 
                (SELECT SUM(IF(WSTime IS NULL OR WSTime='', 0,
                    CASE DAYOFWEEK(STR_TO_DATE(WorkDate, %s))-1
                        WHEN 0 THEN 0
                        WHEN 6 THEN 0
                        WHEN 1 THEN IF(SUBSTRING(WSTime, 9, 4) > '0900', 1, 0)
                        ELSE IF(SUBSTRING(WSTime, 9, 4) > '0840', 1, 0)
                    END)) AS rate_tot
                    , Name AS name 
                    FROM T_SECOM_WORKHISTORY WHERE 1=1 AND WorkDate LIKE %s GROUP BY Name, Sabun) wt
                ON m.mber_nm=wt.name
                LEFT OUTER JOIN (SELECT * FROM T_SECOM_WORKHISTORY WHERE workdate=%s) w 
                ON m.mber_nm=w.Name
                WHERE 1=1
                ORDER BY code_ordr ASC, ofcps_ordr ASC
                    """.format(work_date, work_year)

    data = ['%Y%m%d', '%Y%m%d', '{}%'.format(work_year), work_date.replace("-", "")]
    g.curs.execute(query, data)
    result = g.curs.fetchall()
    return result


def set_work_data(params):
    row = g.curs.execute("SELECT work_sn FROM work WHERE work_year=%(work_year)s AND work_row=%(work_row)s AND work_month=%(work_month)s", params)
    if row:
        result = g.curs.fetchone()
        params['work_sn'] = result['work_sn']

        g.curs.execute("UPDATE work SET {} WHERE work_sn=%(work_sn)s".format(",".join(["{0}=%({0})s".format(t) for t in ["work_data", "work_class"] if t in params])), params)

    else:
        if "work_data" not in params:
            params["work_data"] = ""
        if "work_class" not in params:
            params["work_class"] = 0
        g.curs.execute("INSERT INTO work(work_year, work_row, work_month, work_data, work_class) VALUES(%(work_year)s, %(work_row)s, %(work_month)s, %(work_data)s, %(work_class)s)", params)

def get_today(params):
    work_date = params['s_today']
    work_year = work_date.split("-")[0]
    query = """SELECT '1' AS ctmmny_sn
                    , IF(w.WSTime IS NULL OR w.WSTime='', 0,
                    CASE DAYOFWEEK(STR_TO_DATE(w.WorkDate, %s))-1
                        WHEN 0 THEN 0
                        WHEN 6 THEN 0
                        WHEN 1 THEN IF(SUBSTRING(w.WSTime, 9, 4) > '0900', 1, 0)
                        ELSE IF(SUBSTRING(w.WSTime, 9, 4) > '0840', 1, 0)
                    END) AS today_rate
    				, w.WSTime AS start_time
    				, w.WCTime AS end_time
                FROM member m
                LEFT OUTER JOIN (SELECT * FROM T_SECOM_WORKHISTORY WHERE workdate=%s) w 
                ON m.mber_nm=w.Name
                WHERE 1=1
                AND m.mber_sn=%s"""
    data = ['%Y%m%d', work_date.replace("-", ""), params['mber_sn']]
    g.curs.execute(query, data)
    result = g.curs.fetchone()
    return result