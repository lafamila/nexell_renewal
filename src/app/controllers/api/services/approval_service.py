from flask import session, jsonify, g, render_template
from app.helpers.datatable_helper import dt_query
import json

def get_approval_template(url, init=True):
    return render_template("approvals/{}.html".format(url), init=init)

def get_approval_ty_list(params):
    query = """SELECT code
    , code_nm
    , code_dc
    , estn_code_a as parent_code
    , estn_code_b as template_url
    , estn_code_c AS api_url 
    FROM code
    WHERE use_at='Y'
    AND parnts_code='APPROVAL_TY_CODE'
    ORDER BY code_ordr"""
    g.curs.execute(query)
    rows = g.curs.fetchall()

    result = {}
    for r in rows:
        parent_code = r['parent_code']
        if parent_code not in result:
            result[parent_code] = list()
        result[parent_code].append(r)
    return result

def insert_approval(params):
    params['approval_data'] = json.dumps(params['data'])
    query = "INSERT INTO approval(approval_ty_code, approval_data, approval_title) VALUES (%s, %s, %s)"
    g.curs.execute(query, (params['approval_ty_code'], params['approval_data'], params['approval_title']))
    return g.curs.lastrowid

def insert_approval_member(params):
    approval_list = params['approval_list']
    for row in approval_list:
        row['approval_sn'] = params['approval_sn']
    g.curs.executemany("INSERT INTO approval_member(approval_sn, mber_sn, reg_type, approval_status_code) VALUES (%(approval_sn)s, %(mber_sn)s, %(reg_type)s, 0)", approval_list)

def get_approval(params):
    query = """SELECT a.approval_sn
                , (SELECT estn_code_b FROM code WHERE parnts_code='APPROVAL_TY_CODE' AND code=a.approval_ty_code) AS template_url
                , (SELECT estn_code_c FROM code WHERE parnts_code='APPROVAL_TY_CODE' AND code=a.approval_ty_code) AS api_url
                , a.approval_data
                , a.approval_title
                FROM approval a
                WHERE 1=1
                AND a.approval_sn=%(approval_sn)s"""
    g.curs.execute(query, params)
    result = g.curs.fetchone()
    return result

def get_approval_member(params):
    query = """SELECT am.mber_sn
                , (SELECT mber_nm FROM member WHERE mber_sn=am.mber_sn) AS mber_nm
                , am.reg_type
                , IFNULL(am.update_dtm, '') AS update_dtm
                , am.approval_status_code
                FROM approval_member am
                WHERE 1=1
                AND am.approval_sn=%(approval_sn)s
                ORDER BY am_sn"""
    g.curs.execute(query, params)
    result = g.curs.fetchall()
    return result


def update_approval(params):
    data = [params['approval_status_code']]
    query = """UPDATE approval_member SET approval_status_code=%s, update_dtm=NOW() """
    if "memo" in params and params["memo"]:
        query += ", memo=%s"
        data.append(params['memo'])
    query += " WHERE mber_sn=%s AND approval_sn=%s"
    data.append(session['member']['member_sn'])
    data.append(params['approval_sn'])
    g.curs.execute(query, data)

def get_approval_datatable(params):
    query = """SELECT a.approval_sn
				, a.approval_ty_code
				, (SELECT code_nm FROM code WHERE ctmmny_sn=1 AND parnts_code='APPROVAL_TY_CODE' AND code=a.approval_ty_code) AS approval_ty_nm
				, (SELECT estn_code_a FROM code WHERE parnts_code='APPROVAL_TY_CODE' AND code=a.approval_ty_code) AS approval_se_code
				, (SELECT c.code_nm FROM code c WHERE c.parnts_code='APPROVAL_SE_CODE' AND code=(SELECT estn_code_a FROM code WHERE parnts_code='APPROVAL_TY_CODE' AND code=a.approval_ty_code)) AS approval_se_nm
				, a.approval_title
				, '' AS approval_status
				, DATE_FORMAT(a.reg_dtm, '%%Y-%%m-%%d') AS start_de
				, '' AS end_de
				, '' AS final_mber_nm
				FROM (SELECT * FROM approval_member WHERE mber_sn=%s ) am
				LEFT JOIN approval a 
				ON am.approval_sn=a.approval_sn
				WHERE 1=1
				AND a.reg_dtm BETWEEN '{0} 00:00:00' AND '{1} 23:59:59'
""".format(params['s_start_de_start'], params['s_start_de_end'])

    data = [session['member']['member_sn']]
    return dt_query(query, data, params)

#
#     if "s_cntrct_no" in params and params['s_cntrct_no']:
#         query += " AND c.cntrct_no LIKE %s"
#         data.append('%{}%'.format(params["s_cntrct_no"]))
#
#     if "s_spt_nm" in params and params['s_spt_nm']:
#         query += " AND c.spt_nm LIKE %s"
#         data.append('%{}%'.format(params["s_spt_nm"]))
#
#     if "s_prjct_ty_code" in params and params['s_prjct_ty_code']:
#         query += " AND p.prjct_ty_code=%s"
#         data.append(params["s_prjct_ty_code"])
#
#     if "s_cntrct_se_code" in params and params['s_cntrct_se_code']:
#         query += " AND p.cntrct_se_code=%s"
#         data.append(params["s_cntrct_se_code"])
#
#     if "s_bcnc_sn" in params and params['s_bcnc_sn']:
#         query += " AND c.bcnc_sn=%s"
#         data.append(params["s_bcnc_sn"])
#
#     if "s_dept_code" in params and params['s_dept_code']:
#         if params["s_dept_code"] == "TS":
#             query += " AND m.dept_code LIKE %s"
#             data.append('TS%')
#         else:
#             query += " AND m.dept_code=%s"
#             data.append(params["s_dept_code"])
#
#     if "s_bsn_chrg_sn" in params and params['s_bsn_chrg_sn']:
#         query += " AND c.bsn_chrg_sn=%s"
#         data.append(params["s_bsn_chrg_sn"])
#
#     if "s_spt_chrg_sn" in params and params['s_spt_chrg_sn']:
#         query += " AND c.spt_chrg_sn=%s"
#         data.append(params["s_spt_chrg_sn"])
#
#     if "s_acmslt_sttemnt_at" in params and params['s_acmslt_sttemnt_at']:
#         query += " AND p.acmslt_sttemnt_at LIKE %s"
#         data.append('%{}%'.format(params["s_acmslt_sttemnt_at"]))
#
#     if "s_cntwrk_regstr_ennc" in params and params['s_cntwrk_regstr_ennc']:
#         query += " AND p.cntwrk_regstr_ennc LIKE %s"
#         data.append('%{}%'.format(params["s_cntwrk_regstr_ennc"]))
#
#     if "s_cntrct_nm" in params and params['s_cntrct_nm']:
#         query += " AND c.cntrct_nm LIKE %s"
#         data.append('%{}%'.format(params["s_cntrct_nm"]))
#
#     if "s_progrs_sttus_code" in params and params['s_progrs_sttus_code']:
#         if params["s_progrs_sttus_code"] == "BPSN":
#             query += " AND c.progrs_sttus_code IN ('B', 'P', 'S', 'N')"
#         elif params["s_progrs_sttus_code"] == "BP":
#             query += " AND c.progrs_sttus_code IN ('B', 'P')"
#         else:
#             query += " AND c.progrs_sttus_code=%s"
#             data.append(params["s_progrs_sttus_code"])
#
#     if "s_prjct_creat_at" in params and params['s_prjct_creat_at']:
#         query += " AND c.prjct_creat_at=%s"
#         data.append(params["s_prjct_creat_at"])



    # return dt_query(query, data, params)
