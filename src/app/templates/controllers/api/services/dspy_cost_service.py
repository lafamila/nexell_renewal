from flask import session, jsonify, g

def get_dspy_cost_list(params):
    query = """SELECT d.ctmmny_sn
				, d.cntrct_sn
				, d.prjct_sn
				, d.dspy_ct_sn
				, d.inpt_de
				, IFNULL(d.eqpmn_inpt_ct,0) AS eqpmn_inpt_ct
				, IFNULL(d.eqpmn_rtrvl_ct,0) AS eqpmn_rtrvl_ct
				, IFNULL(d.instl_inpt_ct,0) AS instl_inpt_ct
				, IFNULL(d.instl_excclc_ct,0) AS instl_excclc_ct
				, IFNULL(d.optn_event_ct,0) AS optn_event_ct
				, d.regist_dtm
				, d.register_id
				, d.update_dtm
				, d.updater_id
				FROM dspy_cost d
				WHERE 1=1
				AND d.ctmmny_sn = 1
				AND d.cntrct_sn = %(s_cntrct_sn)s
				AND d.prjct_sn = %(s_prjct_sn)s
				ORDER BY d.inpt_de
"""
    g.curs.execute(query, params)
    result = g.curs.fetchall()
    return result