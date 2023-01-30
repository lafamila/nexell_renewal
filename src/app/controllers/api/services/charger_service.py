from flask import session, jsonify, g

def get_charger_list(params):
    query = """SELECT cntrct_sn
				, prjct_sn
				, charger_sn
				, charger_se_code
				, charger_nm
				, charger_telno
				, charger_moblphon
				, regist_dtm
				, register_id
				, update_dtm
				, updater_id
				FROM charger
				WHERE 1=1
				AND cntrct_sn = %(s_cntrct_sn)s
				AND prjct_sn = %(s_prjct_sn)s
"""
    g.curs.execute(query, params)
    result = g.curs.fetchall()
    return result