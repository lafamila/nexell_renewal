from flask import session, jsonify, g
import onetimepass as otp
import random
import string
import urllib
import datetime
from src.app.helpers.class_helper import Map
from src.app.helpers.datatable_helper import dt_query


def generate_secret_key():
    sck = "".join([random.choice(string.ascii_letters) for i in range(16)])
    return sck

def history_login(view_title, view_action, member_sn, member_id):
    row = g.curs.execute("""INSERT INTO history(client_sn, member_sn, view_title, view_path, view_action, regist_dtm, register_id) VALUES (1, %s, %s, '/', %s, NOW(), %s)""", (member_sn, view_title, view_action, member_id))
    return {"status": True}

def insert_member(params):
    query = """INSERT INTO member(ctmmny_sn, mber_id, mber_password, mber_nm, mber_telno, mber_mob)"""
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
                FROM member m
                WHERE 1=1
                AND ctmmny_sn = 1
                AND mber_sn = %s
                """
    row = g.curs.execute(query, member_sn)
    member = g.curs.fetchone()
    return member
def get_member_info(member_sn):
    row = g.curs.execute("""SELECT m.mber_sn AS member_sn, m.mber_id AS member_id, m.mber_nm AS member_nm, m.author_sn AS auth_cd, m.ctmmny_sn AS client_sn, c.bizrno, (SELECT code_nm FROM code WHERE PARNTS_CODE='OFCPS_CODE' AND code=m.ofcps_code) AS member_level, (SELECT code_nm FROM code WHERE PARNTS_CODE='DEPT_CODE' AND code=m.dept_code) AS dept_nm 
    , (SELECT MAX(regist_dtm) as login_dtm FROM history WHERE member_sn=m.mber_sn AND view_title='로그인' GROUP BY mber_sn, view_title) AS login_dtm
    FROM member m LEFT JOIN ctmmny c ON m.ctmmny_sn = c.ctmmny_sn WHERE m.mber_sn=%s""", (member_sn, ))
    member = g.curs.fetchone()
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
        if secret_key == '':
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
                , login_dtm
                , regist_dtm
                , register_id
                , update_dtm
                , updater_id
                FROM member m
                WHERE 1=1
                AND ctmmny_sn = 1
                """
    data = []


    if "s_mber_id" in params and params['s_mber_id']:
        query += " AND mber_id=%s"
        data.append(params["s_author_sn"])
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
    if "s_mber_sttus_code" in params and params['s_mber_sttus_code']:
        query += " AND mber_sttus_code=%s"
        data.append(params["s_mber_sttus_code"])


    return dt_query(query, data, params)
