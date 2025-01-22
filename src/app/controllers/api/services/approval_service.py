from flask import session, jsonify, g, render_template
from app.helpers.datatable_helper import dt_query
import json
from . import refresh_code_list
import datetime
from pytz import timezone

def get_approval_template(url, init=True):
    return render_template("approvals/{}.html".format(url), init=init, **refresh_code_list())


def get_approval_detail(approval_ty_code):
    result = {}
    query = """SELECT code_ordr AS team_ordr
                    , estn_code_a AS parent_code
                    FROM code
                WHERE use_at='Y'
                AND parnts_code='APPROVAL_TY_CODE'
                AND code=%s"""
    g.curs.execute(query, approval_ty_code)
    result.update(g.curs.fetchone())

    query = """SELECT auth_type
                    , coop
                    , conditions
                    FROM approval_auth
                    WHERE approval_ty_code = %s"""
    g.curs.execute(query, approval_ty_code)
    result.update(g.curs.fetchone())


    return result
def get_approval_ty_list(params):
    query = """SELECT code
                    , code_nm
                    , code_dc
                    , estn_code_a AS parent_code
                FROM code
                WHERE use_at='Y'
                AND parnts_code='APPROVAL_TTY_CODE'
                ORDER BY estn_code_a, code_ordr"""

    g.curs.execute(query)
    rows = g.curs.fetchall()

    query = """SELECT c.code
    , c.code_nm
    , c.code_dc
    , (SELECT estn_code_a FROM code WHERE parnts_code='APPROVAL_TTY_CODE' AND code=c.estn_code_a) AS top_parent_code
    , c.estn_code_a as parent_code
    , c.estn_code_b as template_url
    , c.estn_code_c AS api_url 
    , c.code_ordr
    FROM code c
    WHERE c.use_at='Y'
    AND c.parnts_code='APPROVAL_TY_CODE'
    ORDER BY c.code_ordr"""
    g.curs.execute(query)
    d_rows = g.curs.fetchall()

    result = {}
    for r in rows:
        parent_code = r['parent_code']
        if parent_code not in result:
            result[parent_code] = dict()
        if r['code'] not in result[parent_code]:
            result[parent_code][r['code']] = [(r['code_nm'], r['code_dc']), dict()]

    for r in d_rows:
        top_parent_code = r['top_parent_code']
        parent_code = r['parent_code']
        result[top_parent_code][parent_code][-1][r['code_ordr']] = r
    return result

def insert_approval(params):
    params['approval_data'] = json.dumps(params['data'])
    mber_sn = session['member']['member_sn']
    query = "INSERT INTO approval(approval_ty_code, approval_data, approval_title, reg_mber) VALUES (%s, %s, %s, %s)"
    g.curs.execute(query, (params['approval_ty_code'], params['approval_data'], params['approval_title'], mber_sn))
    return g.curs.lastrowid

def delete_approval(params):
    query = "DELETE FROM approval_member WHERE approval_sn=%(approval_sn)s"
    g.curs.execute(query, params)
    query = "DELETE FROM approval WHERE approval_sn=%(approval_sn)s"
    g.curs.execute(query, params)


def insert_approval_member(params):
    approval_list = params['approval_list']
    already_members = []
    for row in approval_list:
        row['approval_sn'] = params['approval_sn']
        already_members.append(row['mber_sn'])
    g.curs.execute("SELECT mber_sn FROM member WHERE author_sn=1 or dept_code='CEO' or mber_sn=63")
    systems = g.curs.fetchall()
    for s in systems:
        if str(s['mber_sn']) not in already_members:
            approval_list.append({"approval_sn" : params['approval_sn'], "mber_sn" : s['mber_sn'], "reg_type" : 2})
    g.curs.execute("SELECT code_ordr FROM code WHERE parnts_code='APPROVAL_TY_CODE' AND code=%s", params['approval_ty_code'])
    code_ordr = int(g.curs.fetchone()['code_ordr'])
    print(code_ordr, already_members)
    if code_ordr in (2, 3):
        if '91' not in already_members:
            approval_list.append({"approval_sn": params['approval_sn'], "mber_sn": '91', "reg_type": 2})
    g.curs.executemany("INSERT INTO approval_member(approval_sn, mber_sn, reg_type, approval_status_code) SELECT %(approval_sn)s, %(mber_sn)s, %(reg_type)s, 0 FROM approval_member WHERE NOT EXISTS (SELECT approval_sn, mber_sn, reg_type FROM approval_member WHERE approval_sn=%(approval_sn)s AND mber_sn=%(mber_sn)s AND reg_type=%(reg_type)s) LIMIT 1", approval_list)

def get_approval(params):
    query = """SELECT a.approval_sn
                , (SELECT estn_code_b FROM code WHERE parnts_code='APPROVAL_TY_CODE' AND code=a.approval_ty_code) AS template_url
                , (SELECT estn_code_c FROM code WHERE parnts_code='APPROVAL_TY_CODE' AND code=a.approval_ty_code) AS api_url
                , (SELECT estn_code_a FROM code WHERE parnts_code='APPROVAL_TTY_CODE' AND code=(SELECT estn_code_a FROM code WHERE parnts_code='APPROVAL_TY_CODE' AND code=a.approval_ty_code)) AS approval_se_code
                , (SELECT code_nm FROM code WHERE parnts_code='APPROVAL_TTY_CODE' AND code=(SELECT estn_code_a FROM code WHERE parnts_code='APPROVAL_TY_CODE' AND code=a.approval_ty_code)) AS approval_template_title                
                , a.approval_ty_code
                , a.approval_data
                , a.approval_title
                , a.reg_mber
                FROM approval a
                WHERE 1=1
                AND a.approval_sn=%(approval_sn)s"""
    g.curs.execute(query, params)
    result = g.curs.fetchone()
    return result

def get_approval_member(params):
    query = """SELECT am.mber_sn
                , m.mber_nm AS mber_nm
                , IF(f.file_path IS NULL, 'signature.jpg', f.file_path) AS sign_path
                , (SELECT code_nm FROM code WHERE parnts_code='OFCPS_CODE' AND code=m.ofcps_code) AS ofcps_nm                
                , am.reg_type
                , IFNULL(am.update_dtm, '') AS update_dtm
                , am.approval_status_code
                , am.memo
                FROM approval_member am
                LEFT JOIN member m
                ON m.mber_sn=am.mber_sn
                LEFT OUTER JOIN files f
                ON m.sign_file_sn=f.f_sn
                WHERE 1=1
                AND am.approval_sn=%(approval_sn)s
                AND (am.mber_sn NOT IN (SELECT mber_sn FROM member WHERE author_sn=1) OR (am.mber_sn IN (SELECT mber_sn FROM member WHERE author_sn=1) AND am.reg_type=1))
                ORDER BY am_sn"""
    g.curs.execute(query, params)
    result = g.curs.fetchall()
    return result


def update_approval(params):
    data = [params['approval_status_code']]
    if int(data[0]) in (1, -1):
        query = """UPDATE approval_member SET approval_status_code=%s, update_dtm=NOW() """
    else:
        query = """UPDATE approval_member SET approval_status_code=%s, update_dtm=%s """
        data.append(None)

    if "memo" in params and params["memo"]:
        query += ", memo=%s"
        data.append(params['memo'])
    if "comment" in params and params["comment"].strip() != '':
        query += ", memo=%s"
        data.append(params['comment'].strip())
    query += " WHERE mber_sn=%s AND approval_sn=%s"
    data.append(session['member']['member_sn'])
    data.append(params['approval_sn'])
    g.curs.execute(query, data)

    if int(data[0]) == 1 and session['member']['member_sn'] in (63, 91):
        member_list = get_approval_member(params)
        member_list = [m for m in member_list if m['reg_type'] in (0, 1)]

        _pass = False
        g.curs.execute("SELECT a.approval_ty_code, m.rspofc_code FROM approval a LEFT JOIN member m ON a.reg_mber=m.mber_sn WHERE a.approval_sn=%s", params['approval_sn'])
        approval = g.curs.fetchone()
        if int(approval['approval_ty_code']) in (2, 34, 41) or (int(approval['approval_ty_code']) in (22, 56, 57) and int(approval['rspofc_code']) in (100, 150)):
            _pass = False

        if _pass:
            _next = False
            for m in member_list:
                if _next and m['mber_sn'] == 4 and int(m['reg_type']) == 1:
                    g.curs.execute("UPDATE approval_member SET approval_status_code=1, update_dtm=NOW() WHERE mber_sn=4 AND approval_sn=%s", params['approval_sn'])
                    break
                if m['mber_sn'] == session['member']['member_sn']:
                    _next = True
                    continue
                else:
                    _next = False



def get_approval_datatable(params):
    query = """SELECT distinct a.approval_sn
				, a.approval_ty_code
				, (SELECT code_nm FROM code WHERE ctmmny_sn=1 AND parnts_code='APPROVAL_TY_CODE' AND code=a.approval_ty_code) AS approval_ty_nm
				, (SELECT estn_code_a FROM code WHERE parnts_code='APPROVAL_TTY_CODE' AND code=(SELECT estn_code_a FROM code WHERE parnts_code='APPROVAL_TY_CODE' AND code=a.approval_ty_code)) AS approval_se_code
				, (SELECT c.code_nm FROM code c WHERE parnts_code='APPROVAL_SE_CODE' AND code=(SELECT estn_code_a FROM code WHERE parnts_code='APPROVAL_TTY_CODE' AND code=(SELECT estn_code_a FROM code WHERE parnts_code='APPROVAL_TY_CODE' AND code=a.approval_ty_code))) AS approval_se_nm
				, a.approval_title
				, CASE 
				WHEN mi.approval_status_code='0' THEN '상신' 
				WHEN m.approval_status_code='1' THEN '완결'
				WHEN (SELECT MIN(approval_status_code) FROM approval_member WHERE approval_sn=a.approval_sn) = '-1' THEN '반려'
				WHEN m.approval_status_code <> '1' AND last.am_sn >= am.am_sn THEN '진행'
				WHEN n.mber_sn=am.mber_sn THEN '미결'
				WHEN am.approval_status_code='0' AND am.reg_type='2' THEN '수신'
				WHEN am.approval_status_code='1' AND am.reg_type<>'2' THEN '완료'
				ELSE ''
				END AS approval_status
				, DATE_FORMAT(a.reg_dtm, '%%Y-%%m-%%d') AS start_de
				, IF(m.approval_status_code <> 0, DATE_FORMAT(m.update_dtm, '%%Y-%%m-%%d'), '') AS end_de
				, (SELECT mber_nm FROM member WHERE mber_sn=last.mber_sn) AS final_mber_nm
				, (SELECT mber_nm FROM member WHERE mber_sn=a.reg_mber) AS start_mber_nm
				, (SELECT dept_code FROM member WHERE mber_sn=a.reg_mber) AS start_dept_code
				, (SELECT code_nm FROM code WHERE parnts_code='DEPT_CODE' AND code=(SELECT dept_code FROM member WHERE mber_sn=a.reg_mber)) AS start_dept_nm
				FROM (SELECT * FROM approval_member WHERE mber_sn=%s ) am
				LEFT JOIN approval a 
				ON am.approval_sn=a.approval_sn
				INNER JOIN 
				(SELECT x.* FROM approval_member x INNER JOIN (SELECT approval_sn, MAX(am_sn) AS m_am_sn FROM approval_member WHERE reg_type=1 GROUP BY approval_sn) y ON x.approval_sn=y.approval_sn AND x.am_sn=y.m_am_sn) m ON a.approval_sn=m.approval_sn
				INNER JOIN 
				(SELECT x.* FROM approval_member x INNER JOIN (SELECT approval_sn, MIN(am_sn) AS m_am_sn FROM approval_member WHERE reg_type=1 GROUP BY approval_sn) y ON x.approval_sn=y.approval_sn AND x.am_sn=y.m_am_sn) mi ON a.approval_sn=mi.approval_sn
				LEFT OUTER JOIN 
				(SELECT x.* FROM approval_member x INNER JOIN (SELECT approval_sn, MIN(am_sn) AS m_am_sn FROM approval_member WHERE reg_type IN (0, 1) AND approval_status_code='0' GROUP BY approval_sn) y ON x.approval_sn=y.approval_sn AND x.am_sn=y.m_am_sn) n ON a.approval_sn=n.approval_sn
				LEFT OUTER JOIN 
				(SELECT x.* FROM approval_member x INNER JOIN (SELECT approval_sn, MAX(am_sn) AS m_am_sn FROM approval_member WHERE reg_type IN (0, 1) AND approval_status_code='1' GROUP BY approval_sn) y ON x.approval_sn=y.approval_sn AND x.am_sn=y.m_am_sn) last ON a.approval_sn=last.approval_sn
				WHERE 1=1				"""

    data = [session['member']['member_sn']]
    if "s_start_de_start" in params and params["s_start_de_start"] and "s_start_de_end" in params and params["s_start_de_end"]:
        query += " AND a.reg_dtm BETWEEN '{0} 00:00:00' AND '{1} 23:59:59'".format(params['s_start_de_start'], params['s_start_de_end'])

    if "s_approval_tty_code" in params and params['s_approval_tty_code']:
        query += " AND (SELECT estn_code_a FROM code WHERE ctmmny_sn=1 AND parnts_code='APPROVAL_TY_CODE' AND code=a.approval_ty_code) = %s"
        data.append(params["s_approval_tty_code"])

    if "s_approval_se_code" in params and params['s_approval_se_code']:
        query += " AND (SELECT estn_code_a FROM code WHERE ctmmny_sn=1 AND parnts_code='APPROVAL_TTY_CODE' AND code=(SELECT estn_code_a FROM code WHERE parnts_code='APPROVAL_TY_CODE' AND code=a.approval_ty_code)) = %s"
        data.append(params["s_approval_se_code"])

    if "s_approval_title" in params and params['s_approval_title']:
        query += " AND a.approval_title LIKE %s"
        data.append('%{}%'.format(params["s_approval_title"]))

    if "s_start_mber_sn" in params and params['s_start_mber_sn']:
        query += " AND a.reg_mber=%s"
        data.append(params["s_start_mber_sn"])

    if "s_start_dept_code" in params and params['s_start_dept_code']:
        query += " AND (SELECT dept_code FROM member WHERE mber_sn=a.reg_mber)=%s"
        data.append(params["s_start_dept_code"])

    if "s_approval_status" in params and params["s_approval_status"]:
        if session["member"]["member_sn"] == 4:
            query += """ AND CASE 
            				WHEN mi.approval_status_code='0' THEN '상신' 
            				WHEN m.approval_status_code='1' THEN '완결'
            				WHEN (SELECT MIN(approval_status_code) FROM approval_member WHERE approval_sn=a.approval_sn) = '-1' THEN '반려'
            				WHEN m.approval_status_code <> '1' AND last.am_sn >= am.am_sn THEN '진행'
            				WHEN n.mber_sn=am.mber_sn THEN '미결'
            				WHEN am.approval_status_code='0' AND am.reg_type='2' THEN '수신'
            				ELSE ''
            				END = %s AND IF('수신' = %s, IF(a.approval_ty_code IN (1, 39, 40, 13, 5, 37, 44), 1, 0), 1) = 1"""
            data.append(params["s_approval_status"])
            data.append(params["s_approval_status"])
        else:
            query += """ AND CASE 
                    WHEN mi.approval_status_code='0' THEN '상신' 
                    WHEN m.approval_status_code='1' THEN '완결'
                    WHEN (SELECT MIN(approval_status_code) FROM approval_member WHERE approval_sn=a.approval_sn) = '-1' THEN '반려'
                    WHEN m.approval_status_code <> '1' AND last.am_sn >= am.am_sn THEN '진행'
                    WHEN n.mber_sn=am.mber_sn THEN '미결'
                    WHEN am.approval_status_code='0' AND am.reg_type='2' THEN '수신'
                    ELSE ''
                    END = %s """
            data.append(params["s_approval_status"])
    params["custom_order"] = ["IF(m.approval_status_code <> 0, DATE_FORMAT(m.update_dtm, '%%Y-%%m-%%d'), '9999-99-99') DESC", "a.approval_sn DESC"]

    return dt_query(query, data, params)



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
