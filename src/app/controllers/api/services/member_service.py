from flask import session, jsonify, g
import onetimepass as otp
import random
import string
import urllib
from src.app.helpers.class_helper import Map


def generate_secret_key():
    sck = "".join([random.choice(string.ascii_letters) for i in range(16)])
    return sck

def get_member_info(member_sn):
    row = g.curs.execute("SELECT m.mber_sn AS member_sn, m.mber_id AS member_id, m.mber_nm AS member_nm, m.author_sn AS auth_cd, m.ctmmny_sn AS client_sn, c.bizrno FROM member m LEFT JOIN ctmmny c ON m.ctmmny_sn = c.ctmmny_sn WHERE m.mber_sn=%s", (member_sn, ))
    member = g.curs.fetchone()
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
