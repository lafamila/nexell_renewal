from flask import session, jsonify, g
import onetimepass as otp
import random
import string
import urllib
from src.app.connectors import DB

def generate_secret_key():
    sck = "".join([random.choice(string.ascii_letters) for i in range(16)])
    return sck

def member_check(member_id, member_pw):
    row = g.curs.execute("SELECT mber_sn, mber_qr, mber_otp FROM member WHERE mber_id=%s AND mber_password=PASSWORD(%s)", (member_id, member_pw))
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
