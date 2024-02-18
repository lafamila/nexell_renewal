from flask import session, jsonify, g
import onetimepass as otp
import random
import string
import urllib
import datetime
from pytz import timezone
from app.helpers.class_helper import Map
from app.helpers.datatable_helper import dt_query
from collections import OrderedDict

def generate_secret_key():
    sck = "".join([random.choice(string.ascii_letters) for i in range(16)])
    return sck

def history_login(view_title, view_action, member_sn, member_id):
    row = g.curs.execute("""INSERT INTO history(client_sn, member_sn, view_title, view_path, view_action, regist_dtm, register_id) VALUES (1, %s, %s, '/', %s, NOW(), %s)""", (member_sn, view_title, view_action, member_id))
    return {"status": True}

def update_image(params):
    if int(params["purpose"]) == 0:
        query = """UPDATE member SET sign_file_sn=%(file_sn)s WHERE mber_sn=%(mber_sn)s"""
    else:
        query = """UPDATE member SET prof_file_sn=%(file_sn)s WHERE mber_sn=%(mber_sn)s"""
    g.curs.execute(query, params)


def update_member(params):
    required = ("mber_password", )
    mber_sn = params["mber_sn"]

    data = OrderedDict()
    for key in params:
        if key not in ("mber_sn"):
            if key in ("out_de", "enter_de"):
                if params[key] == '':
                    params[key] = None
                data[key] = params[key]
            elif key in required:
                if params[key] != '':
                    data[key] = key
            else:
                data[key] = params[key]
    sub_query = ["{0}=%({0})s".format(key) if key != "mber_password" else "{0}=password(%({0})s)".format(key) for key in data]
    query = """UPDATE member SET {}, UPDATE_DTM=NOW() WHERE mber_sn=%(mber_sn)s""".format(",".join(sub_query))
    g.curs.execute(query, params)

def insert_member(params):
    data = OrderedDict()
    for key in params:
        if key not in ("mber_sn"):
            data[key] = params[key]
    if "ctmmny_sn" not in data:
        data["ctmmny_sn"] = 1

    if "regist_dtm" not in data:
        data["regist_dtm"] = datetime.datetime.now(timezone('Asia/Seoul'))

    if "register_id" not in data:
        data["register_id"] = session["member"]["member_id"]

    if "out_de" in data and data["out_de"] == "":
        data["out_de"] = None

    sub_query = [key for key in data]
    params_query = ["%({})s".format(key) for key in data]

    query = """INSERT INTO member({}) VALUES ({})""".format(",".join(sub_query), ",".join(params_query))
    g.curs.execute(query, data)

def get_team_leader(dept_code):
    row = g.curs.execute("SELECT mber_sn FROM member WHERE dept_code=%s AND mber_sttus_code='H' AND RSPOFC_CODE=150",
                       dept_code)
    if not row:
        return 73
    else:
        team_leader = g.curs.fetchone()
        return int(team_leader['mber_sn'])


def get_member(member_sn):
    query = """SELECT ctmmny_sn
                , mber_sn
                , mber_id
                , mber_password
                , mber_nm
                , mber_telno
                , mber_moblphon
                , mber_email
                , mber_size
                , enter_de
                , out_de
                , dept_code
                , team_code
                , ofcps_code
                , rspofc_code
                , mber_sttus_code
                , author_sn
                , login_dtm
                , regist_dtm
                , register_id
                , update_dtm
                , updater_id
                , check_rate
                , check_work
                , check_todo
                , (SELECT file_path FROM files WHERE f_sn=m.prof_file_sn) AS mber_profile
                FROM member m
                WHERE 1=1
                AND ctmmny_sn = 1
                AND mber_sn = %s
                """
    row = g.curs.execute(query, member_sn)
    member = g.curs.fetchone()
    return member
def get_member_info(member_sn):
    row = g.curs.execute("""SELECT 
                                m.mber_sn AS member_sn
                                , m.dept_code AS dept_code
                                , m.mber_id AS member_id
                                , m.mber_nm AS member_nm
                                , m.author_sn AS auth_cd
                                , m.ctmmny_sn AS client_sn
                                , c.bizrno
                                , (SELECT code_nm FROM code WHERE PARNTS_CODE='OFCPS_CODE' AND code=m.ofcps_code) AS member_level
                                , (SELECT code_nm FROM code WHERE PARNTS_CODE='DEPT_CODE' AND code=m.dept_code) AS dept_nm
                                , (SELECT MAX(regist_dtm) as login_dtm FROM history WHERE member_sn=m.mber_sn AND view_title='로그인' GROUP BY mber_sn, view_title) AS login_dtm
                                , (IF(f.file_path IS NULL, 'profile.png', f.file_path)) as profile_path
    FROM member m LEFT JOIN ctmmny c ON m.ctmmny_sn = c.ctmmny_sn LEFT OUTER JOIN files f ON f.f_sn=m.prof_file_sn WHERE m.mber_sn=%s""", (member_sn, ))
    member = g.curs.fetchone()
    ...
    for key in member:
        if type(member[key]) is datetime.datetime:
            member[key] = member[key].strftime("%Y-%m-%d %H:%M:%S")
    return Map(member)

def update_member_password(member_sn, old_pwd, new_pwd):
    row = g.curs.execute("SELECT * FROM member WHERE mber_sn=%s AND mber_password=PASSWORD(%s) AND mber_sttus_code='H'", (member_sn, old_pwd))
    member = g.curs.fetchone()
    if member:
        g.curs.execute("UPDATE member SET mber_password=PASSWORD(%s) WHERE mber_sn=%s", (new_pwd, member_sn))
        return {"status": True, "message": "성공적으로 변경되었습니다. 재로그인이 필요합니다."}
    else:
        return {"status": False, "message": "현재 비밀번호가 올바르지 않습니다."}

def member_check(member_id, member_pw):
    row = g.curs.execute("SELECT mber_sn, mber_qr, mber_otp FROM member WHERE mber_id=%s AND mber_password=PASSWORD(%s) AND mber_sttus_code='H'", (member_id, member_pw))
    member = g.curs.fetchone()

    if member:
        secret_key = member['mber_otp']
        member_sn = member['mber_sn']
        member_qr = member['mber_qr']
        if secret_key == '' or secret_key is None:
            secret_key = generate_secret_key()
            g.curs.execute("UPDATE member SET mber_otp=%s WHERE mber_sn=%s", (secret_key, member_sn))

        params = urllib.parse.urlencode({"chl" : 'otpauth://totp/nexellsystem?secret={}&issuer=lafamila'.format(secret_key)})
        qrCodeUrl = 'http://chart.googleapis.com/chart?chs=200x200&chld=M|0&cht=qr&' + params

        return {"status": True, "qrCodeUrl" : urllib.parse.unquote(qrCodeUrl), "secret" : secret_key, "mber_qr" : member_qr, "mber_sn" : member_sn}
    else:
        return {"status": False}

def qrcode_check(member_sn, member_qr):
    row = g.curs.execute("SELECT mber_sn, mber_qr, mber_otp FROM member WHERE mber_sn=%s", (member_sn, ))
    member = g.curs.fetchone()
    secret_key = member['mber_otp']
    oneCode = str(otp.get_totp(secret_key)).zfill(6)
    if member_qr == oneCode:
        g.curs.execute("UPDATE member SET mber_qr=0 WHERE mber_sn=%s", (member_sn, ))
        return {"status": True}
    else:
        return {"status": False}


def get_datatable(params):
    query = """SELECT ctmmny_sn
                , mber_sn
                , mber_id
                , mber_password
                , mber_nm
                , mber_telno
                , mber_moblphon
                , mber_email
                , mber_size
                , dept_code
                , (SELECT code_nm FROM code WHERE ctmmny_sn=1 AND parnts_code='DEPT_CODE' AND code=m.dept_code) AS dept_nm
                , team_code
                , (SELECT code_nm FROM code WHERE ctmmny_sn=1 AND parnts_code='TEAM_CODE' AND code=m.team_code) AS team_nm
                , ofcps_code
                , (SELECT code_nm FROM code WHERE ctmmny_sn=1 AND parnts_code='OFCPS_CODE' AND code=m.ofcps_code) AS ofcps_nm
                , rspofc_code
                , (SELECT code_nm FROM code WHERE ctmmny_sn=1 AND parnts_code='RSPOFC_CODE' AND code=m.rspofc_code) AS rspofc_nm
                , mber_sttus_code
                , (SELECT code_nm FROM code WHERE ctmmny_sn=1 AND parnts_code='MBER_STTUS_CODE' AND code=m.mber_sttus_code) AS mber_sttus_nm
                , author_sn
                , (SELECT author_nm FROM author WHERE ctmmny_sn=1 AND author_sn=m.author_sn) AS author_nm
                , enter_de
                , out_de
                , m.regist_dtm
                , register_id
                , update_dtm
                , updater_id
                , IFNULL(h.regist_dtm, '') AS login_dtm
                FROM member m
				LEFT OUTER JOIN 
				(SELECT x.regist_dtm, x.member_sn FROM history x INNER JOIN (SELECT member_sn, MAX(history_sn) AS h_sn FROM history WHERE view_action='login' GROUP BY member_sn) y ON x.member_sn=y.member_sn AND x.history_sn=y.h_sn) h ON h.member_sn=m.mber_sn
                WHERE 1=1
                AND ctmmny_sn = 1
                """
    data = []


    if "s_mber_id" in params and params['s_mber_id']:
        query += " AND mber_id=%s"
        data.append(params["s_mber_id"])
    if "s_mber_nm" in params and params['s_mber_nm']:
        query += " AND mber_nm LIKE %s"
        data.append('%{}%'.format(params["s_mber_nm"]))
    if "s_dept_code" in params and params['s_dept_code']:
        query += " AND dept_code=%s"
        data.append(params["s_dept_code"])
    if "s_team_code" in params and params['s_team_code']:
        query += " AND team_code=%s"
        data.append(params["s_team_code"])
    if "s_ofcps_code" in params and params['s_ofcps_code']:
        query += " AND ofcps_code=%s"
        data.append(params["s_ofcps_code"])
    if "s_rspofc_code" in params and params['s_rspofc_code']:
        query += " AND rspofc_code=%s"
        data.append(params["s_rspofc_code"])
    if "s_author_sn" in params and params['s_author_sn']:
        query += " AND author_sn=%s"
        data.append(params["s_author_sn"])

    if "s_mber_sttus_code" in params and params["s_mber_sttus_code"]:
        if params["s_mber_sttus_code"] == 'NR':
            query += " and m.mber_sttus_code NOT IN ('R') "
        else:
            query += " and m.mber_sttus_code=%s"
            data.append(params["s_mber_sttus_code"])


    return dt_query(query, data, params)


def get_member_todo(params):
    if int(params["s_mber_type"]) == 0:
        sub_query = """ AND (m.mber_sn = 91 OR m.dept_code <> 'ST')"""
    else:
        sub_query = """ AND (m.mber_sn <> 91 AND m.dept_code = 'ST')"""

    query = """				SELECT m.mber_nm
				, (SELECT code_nm FROM code WHERE parnts_code='DEPT_CODE' AND code=m.dept_code) AS dept_nm
				, m.mber_sn
                , (SELECT code_nm FROM code WHERE parnts_code='OFCPS_CODE' AND code=m.ofcps_code) AS ofcps_nm                
				, IF(m.dept_code = 'MA', 999, (SELECT code_ordr FROM code WHERE parnts_code='DEPT_CODE' AND code=m.dept_code)) AS code_ordr
				, (SELECT t.todo_text FROM todo t WHERE t.mber_sn=m.mber_sn AND t.todo_time=0 AND t.todo_de=%(s_ddt_man)s AND t.todo_sn IN (SELECT MAX(todo_sn) FROM todo WHERE todo_de=%(s_ddt_man)s GROUP BY todo_time, mber_sn)) AS text_m
				, IFNULL((SELECT t.todo_sn FROM todo t WHERE t.mber_sn=m.mber_sn AND t.todo_time=0 AND t.todo_de=%(s_ddt_man)s AND t.todo_sn IN (SELECT MAX(todo_sn) FROM todo WHERE todo_de=%(s_ddt_man)s GROUP BY todo_time, mber_sn)), 0) AS sn_m
				, (SELECT t.todo_text FROM todo t WHERE t.mber_sn=m.mber_sn AND t.todo_time=1 AND t.todo_de=%(s_ddt_man)s AND t.todo_sn IN (SELECT MAX(todo_sn) FROM todo WHERE todo_de=%(s_ddt_man)s GROUP BY todo_time, mber_sn)) AS text_a
				, IFNULL((SELECT t.todo_sn FROM todo t WHERE t.mber_sn=m.mber_sn AND t.todo_time=1 AND t.todo_de=%(s_ddt_man)s AND t.todo_sn IN (SELECT MAX(todo_sn) FROM todo WHERE todo_de=%(s_ddt_man)s GROUP BY todo_time, mber_sn)), 0) AS sn_a
				, IF(m.mber_sn=30, 1, 0) AS ordr
				FROM member m
				WHERE m.mber_sttus_code <> 'R'
				AND m.dept_code IS NOT NULL
				AND m.dept_code <> ''
				AND m.check_todo = 1
				{0}
				ORDER BY code_ordr, m.ofcps_code, rspofc_code, ordr""".format(sub_query)
    g.curs.execute(query, params)
    result = g.curs.fetchall()
    return result

def get_extra_todo(params):
    query = """(SELECT  (SELECT t.todo_text FROM todo t WHERE t.mber_sn=-1 AND t.todo_time=0 AND t.todo_de=%(s_ddt_man)s AND t.todo_sn IN (SELECT MAX(todo_sn) FROM todo WHERE todo_de=%(s_ddt_man)s GROUP BY todo_time, mber_sn)) AS text_m
				, IFNULL((SELECT t.todo_sn FROM todo t WHERE t.mber_sn=-1 AND t.todo_time=0 AND t.todo_de=%(s_ddt_man)s AND t.todo_sn IN (SELECT MAX(todo_sn) FROM todo WHERE todo_de=%(s_ddt_man)s GROUP BY todo_time, mber_sn)), 0) AS sn_m
				, (SELECT t.todo_text FROM todo t WHERE t.mber_sn=-1 AND t.todo_time=1 AND t.todo_de=%(s_ddt_man)s AND t.todo_sn IN (SELECT MAX(todo_sn) FROM todo WHERE todo_de=%(s_ddt_man)s GROUP BY todo_time, mber_sn)) AS text_a
				, IFNULL((SELECT t.todo_sn FROM todo t WHERE t.mber_sn=-1 AND t.todo_time=1 AND t.todo_de=%(s_ddt_man)s AND t.todo_sn IN (SELECT MAX(todo_sn) FROM todo WHERE todo_de=%(s_ddt_man)s GROUP BY todo_time, mber_sn)), 0) AS sn_a
				, -1 AS ordr)
				UNION
				(SELECT  (SELECT t.todo_text FROM todo t WHERE t.mber_sn=-2 AND t.todo_time=0 AND t.todo_de=%(s_ddt_man)s AND t.todo_sn IN (SELECT MAX(todo_sn) FROM todo WHERE todo_de=%(s_ddt_man)s GROUP BY todo_time, mber_sn)) AS text_m
				, IFNULL((SELECT t.todo_sn FROM todo t WHERE t.mber_sn=-2 AND t.todo_time=0 AND t.todo_de=%(s_ddt_man)s AND t.todo_sn IN (SELECT MAX(todo_sn) FROM todo WHERE todo_de=%(s_ddt_man)s GROUP BY todo_time, mber_sn)), 0) AS sn_m
				, (SELECT t.todo_text FROM todo t WHERE t.mber_sn=-2 AND t.todo_time=1 AND t.todo_de=%(s_ddt_man)s AND t.todo_sn IN (SELECT MAX(todo_sn) FROM todo WHERE todo_de=%(s_ddt_man)s GROUP BY todo_time, mber_sn)) AS text_a
				, IFNULL((SELECT t.todo_sn FROM todo t WHERE t.mber_sn=-2 AND t.todo_time=1 AND t.todo_de=%(s_ddt_man)s AND t.todo_sn IN (SELECT MAX(todo_sn) FROM todo WHERE todo_de=%(s_ddt_man)s GROUP BY todo_time, mber_sn)), 0) AS sn_a
				, -2 AS ordr)"""
    g.curs.execute(query, params)
    result = g.curs.fetchall()
    return result

def insert_todo(params):
    query = """INSERT INTO todo(mber_sn, todo_time, todo_text, todo_de, regist_dtm, regist_sn) VALUES(%(mber_sn)s, %(todo_time)s, %(todo_text)s, %(todo_de)s, NOW(), %(regist_sn)s)"""

    params["regist_sn"] = session['member']['member_sn']
    g.curs.execute(query, params)

def update_todo(params):
    query = """UPDATE todo SET todo_text=%(todo_text)s WHERE todo_sn=%(todo_sn)s"""
    g.curs.execute(query, params)

def delete_member(params):
    query = "DELETE FROM member WHERE mber_sn=%(mber_sn)s"
    g.curs.execute(query, params)

def get_vacation_list(params):
    query = """SELECT vacation_sn
                    , vacation_de
                    , vacation_type
                    , rm
                    , etc1
                    , etc2
                    FROM vacation
                    WHERE 1=1
                    AND mber_sn=%(mber_sn)s
                    ORDER BY vacation_de DESC"""
    g.curs.execute(query, params)
    result = g.curs.fetchall()
    return result

def delete_vacation(params):
    g.curs.execute("DELETE FROM vacation WHERE vacation_sn=%(vacation_sn)s", params)

def insert_vacation(params):
    data = OrderedDict()
    data['mber_sn'] = params["mber_sn"]
    st_de = datetime.datetime.strptime(params['s_de_start'], "%Y-%m-%d")
    ed_de = datetime.datetime.strptime(params['s_de_end'], "%Y-%m-%d")
    if params['vacation_type'] == 'y':
        if params['vacation_type_detail'] == 'h1':
            data['vacation_type'] = 2
        elif params['vacation_type_detail'] == 'h2':
            data['vacation_type'] = 3
        else:
            data['vacation_type'] = 1


    elif params['vacation_type'] == 'b':
        if params['vacation_type_detail'] == 'h1':
            data['vacation_type'] = 5
        elif params['vacation_type_detail'] == 'h2':
            data['vacation_type'] = 6
        else:
            data['vacation_type'] = 4

    else:
        data['vacation_type'] = 7
    data['rm'] = params['to_go']
    data['etc1'] = params['rm']
    data['etc2'] = params['tel_no']
    for d in range((ed_de - st_de).days + 1):
        data['vacation_de'] = (st_de + datetime.timedelta(days=d)).strftime("%Y-%m-%d")
        g.curs.execute(
            "INSERT INTO vacation({}) VALUES ({})".format(",".join(["{}".format(key) for key in data.keys()]),
                                                          ",".join(["%({})s".format(key) for key in data.keys()])),
            data)


