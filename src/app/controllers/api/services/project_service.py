from flask import session, jsonify, g
from app.helpers.datatable_helper import dt_query
from collections import OrderedDict
from datetime import datetime

def get_project_datatable(params):
    query = """SELECT c.ctmmny_sn
				, c.cntrct_sn
				, c.cntrct_nm
				, p.prjct_sn
				, p.prjct_ty_code
				, (SELECT code_nm FROM code WHERE ctmmny_sn=1 AND parnts_code='PRJCT_TY_CODE' AND code=p.prjct_ty_code) AS prjct_ty_nm
				, cntrct_se_code
				, (SELECT code_nm FROM code WHERE ctmmny_sn=1 AND parnts_code='CNTRCT_SE_CODE' AND code=p.cntrct_se_code) AS cntrct_se_nm
				, mngr_sn
				, (SELECT mber_nm FROM member WHERE mber_sn=p.mngr_sn) AS mngr_nm
				, manage_no
				, eqpmn_dtls
				, cntrwk_dtls
				, cntrct_dscnt_rt
				, cnsul_dscnt_rt
				, drw_opertor_sn
				, (SELECT mber_nm FROM member WHERE mber_sn=p.drw_opertor_sn) AS drw_opertor_nm
				, acmslt_sttemnt_at
				, cntwrk_regstr_ennc
				, p.partclr_matter
				, enty
				, enty_de
				, enty_rm
				, prtpay
				, prtpay_de
				, prtpay_rm
				, surlus
				, surlus_de
				, surlus_rm
				, setle_mth
				, p.register_id
				, p.update_dtm
				, p.updater_id
				, c.cntrct_no
				, c.cntrct_de
				, c.cntrct_nm
				, CASE WHEN c.prjct_ty_code IN ('NR') THEN
				(SELECT IFNULL(SUM(IFNULL(co.QY, 0)*IFNULL(co.SALAMT,0)),0) FROM cost co WHERE co.cntrct_sn = c.cntrct_sn AND co.cntrct_execut_code IN ('A', 'C'))
				WHEN c.prjct_ty_code IN ('BF') AND c.progrs_sttus_code <> 'B' THEN
				(SELECT IFNULL(SUM(ROUND(IFNULL(co.QY, 0)*IFNULL(co.puchas_amount,0)*0.01*(100.0-IFNULL(co.dscnt_rt, 0))*IFNULL(co.fee_rt, 0)*0.01)),0) FROM cost co WHERE co.cntrct_sn = c.cntrct_sn AND co.cntrct_execut_code IN ('C'))
				WHEN c.prjct_ty_code IN ('BD') AND c.progrs_sttus_code <> 'B' THEN
				(SELECT IFNULL(SUM(IFNULL(co.QY, 0)*IFNULL(co.SALAMT,0)),0) FROM cost co WHERE co.cntrct_sn = c.cntrct_sn AND co.cntrct_execut_code IN ('A', 'C'))
				WHEN c.prjct_ty_code IN ('BD') AND c.progrs_sttus_code = 'B' THEN
				(SELECT IFNULL(SUM(IFNULL(co.QY, 0)*IFNULL(co.SALAMT,0)),0) FROM cost co WHERE co.cntrct_sn = c.cntrct_sn AND (co.cost_date > '0000-00-00') AND co.cntrct_execut_code IN ('C'))
				ELSE 0
				END AS cntrct_amount
				, CASE WHEN c.prjct_ty_code IN ('NR') THEN
				(SELECT IFNULL(SUM(IFNULL(co.QY, 0)*IFNULL(co.SALAMT,0)),0) FROM cost co WHERE co.cntrct_sn = c.cntrct_sn AND co.cntrct_execut_code IN ('A', 'C') AND co.cost_date BETWEEN '{0} 00:00:00' AND '{1} 23:59:59')
				WHEN c.prjct_ty_code IN ('BF') AND c.progrs_sttus_code <> 'B' THEN
				(SELECT IFNULL(SUM(ROUND(IFNULL(co.QY, 0)*IFNULL(co.puchas_amount,0)*0.01*(100.0-IFNULL(co.dscnt_rt, 0))*IFNULL(co.fee_rt, 0)*0.01)),0) FROM cost co WHERE co.cntrct_sn = c.cntrct_sn AND co.cntrct_execut_code IN ('C') AND co.cost_date BETWEEN '{0} 00:00:00' AND '{1} 23:59:59')
				WHEN c.prjct_ty_code IN ('BD') AND c.progrs_sttus_code <> 'B' THEN
				(SELECT IFNULL(SUM(IFNULL(co.QY, 0)*IFNULL(co.SALAMT,0)),0) FROM cost co WHERE co.cntrct_sn = c.cntrct_sn AND co.cntrct_execut_code IN ('A', 'C') AND co.cost_date BETWEEN '{0} 00:00:00' AND '{1} 23:59:59')
				WHEN c.prjct_ty_code IN ('BD') AND c.progrs_sttus_code = 'B' THEN
				(SELECT IFNULL(SUM(IFNULL(co.QY, 0)*IFNULL(co.SALAMT,0)),0) FROM cost co WHERE co.cntrct_sn = c.cntrct_sn AND co.cntrct_execut_code IN ('C') AND co.cost_date BETWEEN '{0} 00:00:00' AND '{1} 23:59:59')
				ELSE 0
				END AS amount
				, c.bcnc_sn
				, (SELECT bcnc_nm FROM bcnc WHERE bcnc_sn=c.bcnc_sn) AS bcnc_nm
				, c.spt_nm
				, c.spt_adres
				, c.cntrwk_bgnde
				, c.cntrwk_endde
				, c.etc_sttus
				, m.dept_code
				, (SELECT code_nm FROM code WHERE ctmmny_sn=1 AND parnts_code='DEPT_CODE' AND code=m.dept_code) AS dept_nm
				, c.bsn_chrg_sn
				, GET_MEMBER_NAME(c.bsn_chrg_sn, 'M') AS bsn_chrg_nm
				, c.spt_chrg_sn
				, GET_MEMBER_NAME(c.spt_chrg_sn, 'M') AS spt_chrg_nm
				, c.prjct_creat_at
				, c.progrs_sttus_code
				, (SELECT code_nm FROM code WHERE ctmmny_sn=1 AND parnts_code='PROGRS_STTUS_CODE' AND code=c.progrs_sttus_code) AS progrs_sttus_nm
				, (SELECT code_nm FROM code WHERE ctmmny_sn=1 AND parnts_code='PRJCT_CREAT_AT' AND code=c.prjct_creat_at) AS prjct_sttus_nm
				, c.flaw_co
				, c.regist_dtm
				, c.register_id
				, c.update_dtm
				, c.updater_id
				FROM contract c
				LEFT OUTER JOIN member m
				ON m.mber_sn=c.bsn_chrg_sn
				LEFT OUTER JOIN project p
				ON p.cntrct_sn=c.cntrct_sn
				WHERE 1=1
				AND ((c.cntrct_de BETWEEN '{0} 00:00:00'
				AND '{1} 23:59:59') OR ((SELECT COUNT(co.cntrwk_ct_sn) FROM cost co WHERE 1=1 AND co.cntrct_execut_code IN ('A', 'C') AND co.cost_date BETWEEN '{0} 00:00:00' AND '{1} 23:59:59' AND co.cntrct_sn = c.cntrct_sn GROUP BY co.cntrct_sn) > 0))
""".format(params['s_cntrct_de_start'], params['s_cntrct_de_end'])

    data = []


    if "s_cntrct_no" in params and params['s_cntrct_no']:
        query += " AND c.cntrct_no LIKE %s"
        data.append('%{}%'.format(params["s_cntrct_no"]))

    if "s_spt_nm" in params and params['s_spt_nm']:
        query += " AND c.spt_nm LIKE %s"
        data.append('%{}%'.format(params["s_spt_nm"]))

    if "s_prjct_ty_code" in params and params['s_prjct_ty_code']:
        query += " AND p.prjct_ty_code=%s"
        data.append(params["s_prjct_ty_code"])

    if "s_cntrct_se_code" in params and params['s_cntrct_se_code']:
        query += " AND p.cntrct_se_code=%s"
        data.append(params["s_cntrct_se_code"])

    if "s_bcnc_sn" in params and params['s_bcnc_sn']:
        query += " AND c.bcnc_sn=%s"
        data.append(params["s_bcnc_sn"])

    if "s_dept_code" in params and params['s_dept_code']:
        if params["s_dept_code"] == "TS":
            query += " AND m.dept_code LIKE %s"
            data.append('TS%')
        else:
            query += " AND m.dept_code=%s"
            data.append(params["s_dept_code"])

    if "s_bsn_chrg_sn" in params and params['s_bsn_chrg_sn']:
        query += " AND c.bsn_chrg_sn=%s"
        data.append(params["s_bsn_chrg_sn"])

    if "s_spt_chrg_sn" in params and params['s_spt_chrg_sn']:
        query += " AND c.spt_chrg_sn=%s"
        data.append(params["s_spt_chrg_sn"])

    if "s_acmslt_sttemnt_at" in params and params['s_acmslt_sttemnt_at']:
        query += " AND p.acmslt_sttemnt_at LIKE %s"
        data.append('%{}%'.format(params["s_acmslt_sttemnt_at"]))

    if "s_cntwrk_regstr_ennc" in params and params['s_cntwrk_regstr_ennc']:
        query += " AND p.cntwrk_regstr_ennc LIKE %s"
        data.append('%{}%'.format(params["s_cntwrk_regstr_ennc"]))

    if "s_cntrct_nm" in params and params['s_cntrct_nm']:
        query += " AND c.cntrct_nm LIKE %s"
        data.append('%{}%'.format(params["s_cntrct_nm"]))

    if "s_progrs_sttus_code" in params and params['s_progrs_sttus_code']:
        if params["s_progrs_sttus_code"] == "BPSN":
            query += " AND c.progrs_sttus_code IN ('B', 'P', 'S', 'N')"
        elif params["s_progrs_sttus_code"] == "BP":
            query += " AND c.progrs_sttus_code IN ('B', 'P')"
        else:
            query += " AND c.progrs_sttus_code=%s"
            data.append(params["s_progrs_sttus_code"])

    if "s_prjct_creat_at" in params and params['s_prjct_creat_at']:
        query += " AND c.prjct_creat_at=%s"
        data.append(params["s_prjct_creat_at"])



    return dt_query(query, data, params)


def get_contract_summary(params):
    query = """SELECT IFNULL(COUNT(c.cntrct_sn),0) AS total_count
				, SUM(CASE WHEN c.prjct_ty_code IN ('NR') THEN
				IFNULL(IFNULL(co.QY, 0)*IFNULL(co.SALAMT,0),0)
				WHEN c.prjct_ty_code IN ('BF') AND c.progrs_sttus_code <> 'B' THEN
				IFNULL(ROUND(IFNULL(co.QY, 0)*IFNULL(co.puchas_amount,0)*0.01*(100.0-IFNULL(co.dscnt_rt, 0))*IFNULL(co.fee_rt, 0)*0.01),0)
				WHEN c.prjct_ty_code IN ('BD') AND c.progrs_sttus_code <> 'B' THEN
				IFNULL(IFNULL(co.QY, 0)*IFNULL(co.SALAMT,0),0)
				WHEN c.prjct_ty_code IN ('BD') AND c.progrs_sttus_code = 'B' THEN
				IFNULL(IF(co.cost_date <> '0000-00-00', IFNULL(co.QY, 0)*IFNULL(co.SALAMT,0), 0),0)
				ELSE 0
				END) AS total_amount
				, SUM(CASE WHEN c.prjct_ty_code IN ('NR') THEN
				IFNULL(IF(co.cost_date BETWEEN '{0} 00:00:00' AND '{1} 23:59:59', IFNULL(co.QY, 0)*IFNULL(co.SALAMT,0), 0),0)
				WHEN c.prjct_ty_code IN ('BF') AND c.progrs_sttus_code <> 'B' THEN
				IFNULL(IF(co.cost_date BETWEEN '{0} 00:00:00' AND '{1} 23:59:59', ROUND(IFNULL(co.QY, 0)*IFNULL(co.puchas_amount,0)*0.01*(100.0-IFNULL(co.dscnt_rt, 0))*IFNULL(co.fee_rt, 0)*0.01), 0),0)
				WHEN c.prjct_ty_code IN ('BD') AND c.progrs_sttus_code <> 'B' THEN
				IFNULL(IF(co.cost_date BETWEEN '{0} 00:00:00' AND '{1} 23:59:59', IFNULL(co.QY, 0)*IFNULL(co.SALAMT,0), 0),0)
				WHEN c.prjct_ty_code IN ('BD') AND c.progrs_sttus_code = 'B' THEN
				IFNULL(IF(co.cost_date BETWEEN '{0} 00:00:00' AND '{1} 23:59:59', IFNULL(co.QY, 0)*IFNULL(co.SALAMT,0), 0),0)
				ELSE 0
				END) AS amount
				FROM contract c
				LEFT OUTER JOIN project p
				ON c.cntrct_sn = p.cntrct_sn
				LEFT OUTER JOIN member m
				ON m.mber_sn=c.bsn_chrg_sn
				LEFT OUTER JOIN cost co
				ON c.cntrct_sn=co.cntrct_sn
				AND co.cntrct_execut_code IN ('C')
				WHERE 1=1
				AND c.ctmmny_sn = 1
				AND ((c.cntrct_de BETWEEN '{0} 00:00:00'
				AND '{1} 23:59:59') OR ((SELECT COUNT(co.cntrwk_ct_sn) FROM cost co WHERE 1=1 AND co.cntrct_execut_code IN ('A', 'C') AND co.cost_date BETWEEN '{0} 00:00:00' AND '{1} 23:59:59' AND co.cntrct_sn = c.cntrct_sn GROUP BY co.cntrct_sn) > 0))""".format(params['s_cntrct_de_start'], params['s_cntrct_de_end'])


    data = []


    if "s_cntrct_no" in params and params['s_cntrct_no']:
        query += " AND c.cntrct_no LIKE %s"
        data.append('%{}%'.format(params["s_cntrct_no"]))

    if "s_spt_nm" in params and params['s_spt_nm']:
        query += " AND c.spt_nm LIKE %s"
        data.append('%{}%'.format(params["s_spt_nm"]))

    if "s_prjct_ty_code" in params and params['s_prjct_ty_code']:
        query += " AND p.prjct_ty_code=%s"
        data.append(params["s_prjct_ty_code"])

    if "s_cntrct_se_code" in params and params['s_cntrct_se_code']:
        query += " AND p.cntrct_se_code=%s"
        data.append(params["s_cntrct_se_code"])

    if "s_bcnc_sn" in params and params['s_bcnc_sn']:
        query += " AND c.bcnc_sn=%s"
        data.append(params["s_bcnc_sn"])

    if "s_dept_code" in params and params['s_dept_code']:
        if params["s_dept_code"] == "TS":
            query += " AND m.dept_code LIKE %s"
            data.append('TS%')
        else:
            query += " AND m.dept_code=%s"
            data.append(params["s_dept_code"])

    if "s_bsn_chrg_sn" in params and params['s_bsn_chrg_sn']:
        query += " AND c.bsn_chrg_sn=%s"
        data.append(params["s_bsn_chrg_sn"])

    if "s_spt_chrg_sn" in params and params['s_spt_chrg_sn']:
        query += " AND c.spt_chrg_sn=%s"
        data.append(params["s_spt_chrg_sn"])

    if "s_acmslt_sttemnt_at" in params and params['s_acmslt_sttemnt_at']:
        query += " AND p.acmslt_sttemnt_at LIKE %s"
        data.append('%{}%'.format(params["s_acmslt_sttemnt_at"]))

    if "s_cntwrk_regstr_ennc" in params and params['s_cntwrk_regstr_ennc']:
        query += " AND p.cntwrk_regstr_ennc LIKE %s"
        data.append('%{}%'.format(params["s_cntwrk_regstr_ennc"]))

    if "s_cntrct_nm" in params and params['s_cntrct_nm']:
        query += " AND c.cntrct_nm LIKE %s"
        data.append('%{}%'.format(params["s_cntrct_nm"]))

    if "s_progrs_sttus_code" in params and params['s_progrs_sttus_code']:
        if params["s_progrs_sttus_code"] == "BPSN":
            query += " AND c.progrs_sttus_code IN ('B', 'P', 'S', 'N')"
        elif params["s_progrs_sttus_code"] == "BP":
            query += " AND c.progrs_sttus_code IN ('B', 'P')"
        else:
            query += " AND c.progrs_sttus_code=%s"
            data.append(params["s_progrs_sttus_code"])

    if "s_prjct_creat_at" in params and params['s_prjct_creat_at']:
        query += " AND c.prjct_creat_at=%s"
        data.append(params["s_prjct_creat_at"])

    g.curs.execute(query, data)
    result = g.curs.fetchone()
    return result

def get_contract_count_summary(params):
    query = """SELECT IFNULL(COUNT(c.cntrct_sn),0) AS total_count
				FROM contract c
				LEFT OUTER JOIN member m
				ON m.mber_sn=c.bsn_chrg_sn
				LEFT OUTER JOIN project p
				ON p.cntrct_sn=c.cntrct_sn
				WHERE 1=1
				AND c.ctmmny_sn = 1
				AND ((c.cntrct_de BETWEEN '{0} 00:00:00'
				AND '{1} 23:59:59') OR ((SELECT COUNT(co.cntrwk_ct_sn) FROM cost co WHERE 1=1 AND co.cntrct_execut_code IN ('A', 'C') AND co.cost_date BETWEEN '{0} 00:00:00' AND '{1} 23:59:59' AND co.cntrct_sn = c.cntrct_sn GROUP BY co.cntrct_sn) > 0))""".format(params['s_cntrct_de_start'], params['s_cntrct_de_end'])



    data = []


    if "s_cntrct_no" in params and params['s_cntrct_no']:
        query += " AND c.cntrct_no LIKE %s"
        data.append('%{}%'.format(params["s_cntrct_no"]))

    if "s_spt_nm" in params and params['s_spt_nm']:
        query += " AND c.spt_nm LIKE %s"
        data.append('%{}%'.format(params["s_spt_nm"]))

    if "s_prjct_ty_code" in params and params['s_prjct_ty_code']:
        query += " AND p.prjct_ty_code=%s"
        data.append(params["s_prjct_ty_code"])

    if "s_cntrct_se_code" in params and params['s_cntrct_se_code']:
        query += " AND p.cntrct_se_code=%s"
        data.append(params["s_cntrct_se_code"])

    if "s_bcnc_sn" in params and params['s_bcnc_sn']:
        query += " AND c.bcnc_sn=%s"
        data.append(params["s_bcnc_sn"])

    if "s_dept_code" in params and params['s_dept_code']:
        if params["s_dept_code"] == "TS":
            query += " AND m.dept_code LIKE %s"
            data.append('TS%')
        else:
            query += " AND m.dept_code=%s"
            data.append(params["s_dept_code"])

    if "s_bsn_chrg_sn" in params and params['s_bsn_chrg_sn']:
        query += " AND c.bsn_chrg_sn=%s"
        data.append(params["s_bsn_chrg_sn"])

    if "s_spt_chrg_sn" in params and params['s_spt_chrg_sn']:
        query += " AND c.spt_chrg_sn=%s"
        data.append(params["s_spt_chrg_sn"])

    if "s_acmslt_sttemnt_at" in params and params['s_acmslt_sttemnt_at']:
        query += " AND p.acmslt_sttemnt_at LIKE %s"
        data.append('%{}%'.format(params["s_acmslt_sttemnt_at"]))

    if "s_cntwrk_regstr_ennc" in params and params['s_cntwrk_regstr_ennc']:
        query += " AND p.cntwrk_regstr_ennc LIKE %s"
        data.append('%{}%'.format(params["s_cntwrk_regstr_ennc"]))

    if "s_cntrct_nm" in params and params['s_cntrct_nm']:
        query += " AND c.cntrct_nm LIKE %s"
        data.append('%{}%'.format(params["s_cntrct_nm"]))

    if "s_progrs_sttus_code" in params and params['s_progrs_sttus_code']:
        if params["s_progrs_sttus_code"] == "BPSN":
            query += " AND c.progrs_sttus_code IN ('B', 'P', 'S', 'N')"
        elif params["s_progrs_sttus_code"] == "BP":
            query += " AND c.progrs_sttus_code IN ('B', 'P')"
        else:
            query += " AND c.progrs_sttus_code=%s"
            data.append(params["s_progrs_sttus_code"])

    if "s_prjct_creat_at" in params and params['s_prjct_creat_at']:
        query += " AND c.prjct_creat_at=%s"
        data.append(params["s_prjct_creat_at"])

    g.curs.execute(query, data)
    result = g.curs.fetchone()
    return result

def get_construct(params):
    query = """SELECT construct_sn
    				, construct_name
    				, construct_count
    				, construct_amt
    				, construct_tax
    				, cntrct_sn
    				FROM construct
    				WHERE 1=1
    				AND cntrct_sn = %s
    """
    g.curs.execute(query, params['s_cntrct_sn'])
    result = g.curs.fetchall()
    return result

def get_contract(params):
    query = """SELECT ctmmny_sn
				, cntrct_sn
				, cntrct_no
				, cntrct_nm
				, cntrct_de
				, cntrct_amount
				, prjct_ty_code
				, bcnc_sn
				, author
				, (SELECT bcnc_nm FROM bcnc WHERE bcnc_sn=c.bcnc_sn) AS bcnc_nm
				, spt_nm
				, spt_adres
				, cntrwk_bgnde
				, cntrwk_endde
				, CONCAT(cntrwk_bgnde,' ~ ',cntrwk_endde) AS cntrwk_period
				, etc_sttus
				, bsn_chrg_sn
				, (SELECT mber_nm FROM member WHERE mber_sn=c.bsn_chrg_sn) AS bsn_chrg_nm
				, spt_chrg_sn
				, (SELECT mber_nm FROM member WHERE mber_sn=c.spt_chrg_sn) AS spt_chrg_nm
				, partclr_matter
				, prjct_creat_at
				, (SELECT code_nm FROM code WHERE ctmmny_sn=1 AND parnts_code='PRJCT_CREAT_AT' AND code=c.prjct_creat_at) AS prjct_creat_nm
				, progrs_sttus_code
				, flaw_co
				, regist_dtm
				, register_id
				, update_dtm
				, updater_id
				, biss_a
				, biss_b
				, biss_c
				, biss_d
				, biss_e
				, biss_f
				, biss_g
				, biss_h
				, biss_i
				, biss_j
				, home_count
				, home_region
				FROM contract c
				WHERE 1=1
				AND ctmmny_sn = 1
				AND cntrct_sn = %s
"""
    g.curs.execute(query, params['s_cntrct_sn'])
    result = g.curs.fetchone()
    return result

def get_project_list(params):
    query = """SELECT p.ctmmny_sn
    				, p.cntrct_sn
    				, c.cntrct_nm
    				, prjct_sn
    				, p.prjct_ty_code
    				, (SELECT code_nm FROM code WHERE ctmmny_sn=1 AND parnts_code='PRJCT_TY_CODE' AND code=p.prjct_ty_code) AS prjct_ty_nm
    				, cntrct_se_code
    				, (SELECT code_nm FROM code WHERE ctmmny_sn=1 AND parnts_code='CNTRCT_SE_CODE' AND code=p.cntrct_se_code) AS cntrct_se_nm
    				, mngr_sn
    				, (SELECT mber_nm FROM member WHERE mber_sn=p.mngr_sn) AS mngr_nm
    				, manage_no
    				, eqpmn_dtls
    				, cntrwk_dtls
    				, cntrct_dscnt_rt
    				, cnsul_dscnt_rt
    				, drw_opertor_sn
    				, (SELECT mber_nm FROM member WHERE mber_sn=p.drw_opertor_sn) AS drw_opertor_nm
    				, acmslt_sttemnt_at
    				, cntwrk_regstr_ennc
    				, p.partclr_matter
    				, enty
    				, enty_de
    				, enty_rm
    				, prtpay
    				, prtpay_de
    				, prtpay_rm
    				, surlus
    				, surlus_de
    				, surlus_rm
    				, setle_mth
    				, p.regist_dtm
    				, p.register_id
    				, p.update_dtm
    				, p.updater_id
    				, c.cntrct_no
    				, c.cntrct_de
    				, c.cntrct_nm
    				, c.cntrct_amount
    				, c.bcnc_sn
    				, (SELECT bcnc_nm FROM bcnc WHERE bcnc_sn=c.bcnc_sn) AS bcnc_nm
    				, c.spt_nm
    				, c.cntrwk_bgnde
    				, c.cntrwk_endde
    				, CONCAT(c.cntrwk_endde, '~', c.cntrwk_endde) AS cntrwk_prod
    				, c.bsn_chrg_sn
    				, (SELECT mber_nm FROM member WHERE mber_sn=c.bsn_chrg_sn) AS bsn_chrg_nm
    				, c.spt_chrg_sn
    				, (SELECT mber_nm FROM member WHERE mber_sn=c.spt_chrg_sn) AS spt_chrg_nm
    				, c.prjct_creat_at
    				, (SELECT code_nm FROM code WHERE ctmmny_sn=1 AND parnts_code='PRJCT_CREAT_AT' AND code=c.prjct_creat_at) AS prjct_sttus_nm
    				FROM project p
    				LEFT JOIN contract c
    				ON p.ctmmny_sn=c.ctmmny_sn AND p.cntrct_sn=c.cntrct_sn
    				WHERE 1=1
    				AND p.ctmmny_sn = 1
    				AND p.cntrct_sn = %(s_cntrct_sn)s
    """
    g.curs.execute(query, params)
    result = g.curs.fetchall()
    return result


def get_project(params):
    query = """SELECT ctmmny_sn
				, cntrct_sn
				, prjct_sn
				, prjct_ty_code
				, (SELECT code_nm FROM code WHERE ctmmny_sn=1 AND parnts_code='PRJCT_TY_CODE' AND code=p.prjct_ty_code) AS prjct_ty_nm
				, cntrct_se_code
				, (SELECT code_nm FROM code WHERE ctmmny_sn=1 AND parnts_code='CNTRCT_SE_CODE' AND code=p.cntrct_se_code) AS cntrct_se_nm
				, mngr_sn
				, (SELECT mber_nm FROM member WHERE mber_sn=p.mngr_sn) AS mngr_nm
				, manage_no
				, eqpmn_dtls
				, cntrwk_dtls
				, IFNULL(cntrct_dscnt_rt, '') AS cntrct_dscnt_rt
				, IFNULL(cnsul_dscnt_rt, '') AS cnsul_dscnt_rt
				, drw_opertor_sn
				, (SELECT mber_nm FROM member WHERE mber_sn=p.drw_opertor_sn) AS drw_opertor_nm
				, acmslt_sttemnt_at
				, cntwrk_regstr_ennc
				, REPLACE(partclr_matter, '\r\n', '<br>') AS partclr_matter
				, IFNULL(enty, '') AS enty
				, IFNULL(enty_de, '') AS enty_de
				, IFNULL(enty_rm, '') AS enty_rm
				, IFNULL(prtpay, '') AS prtpay
				, IFNULL(prtpay_de, '') AS prtpay_de
				, IFNULL(prtpay_rm, '') AS prtpay_rm
				, IFNULL(surlus, '') AS surlus
				, IFNULL(surlus_de, '') AS surlus_de
				, IFNULL(surlus_rm, '') AS surlus_rm
				, IFNULL(setle_mth, '') AS setle_mth
				, regist_dtm
				, register_id
				, update_dtm
				, updater_id
				FROM project p
				WHERE 1=1
				AND ctmmny_sn = 1
				AND cntrct_sn = %(s_cntrct_sn)s
				AND prjct_sn = %(s_prjct_sn)s
"""
    g.curs.execute(query, params)
    result = g.curs.fetchone()
    return result


def get_a_cost_list(params):
    query = """SELECT cntrct_execut_code
				, ct_se_code
				, CASE cntrct_execut_code
				WHEN 'E' THEN SUM(puchas_amount * qy)
				WHEN 'C' THEN SUM(salamt*qy)
				END AS amount
				FROM cost
				WHERE 1=1
				AND cntrct_sn = %(s_cntrct_sn)s
				AND prjct_sn = %(s_prjct_sn)s
				AND extra_sn = 0
				GROUP BY cntrct_execut_code, ct_se_code
				ORDER BY cntrct_execut_code, ct_se_code
"""
    g.curs.execute(query, params)
    result = g.curs.fetchall()
    return result

def get_b_cost_list(params):
    query = """SELECT cntrct_execut_code
				, ct_se_code
				, CASE cntrct_execut_code
				WHEN 'D' THEN SUM(puchas_amount * qy)
				WHEN 'B' THEN SUM(salamt*qy)
				END AS amount
				FROM cost
				WHERE 1=1
				AND cntrct_sn = %(s_cntrct_sn)s
				AND prjct_sn = %(s_prjct_sn)s
				AND extra_sn = 0
				GROUP BY cntrct_execut_code, ct_se_code
				ORDER BY cntrct_execut_code, ct_se_code
"""
    g.curs.execute(query, params)
    result = g.curs.fetchall()
    return result

def get_max_extra_cost_list(params):
    query = """SELECT cntrct_execut_code
				, ct_se_code
				, extra_sn
				, CASE cntrct_execut_code
				WHEN 'E' THEN SUM(puchas_amount * qy)
				WHEN 'C' THEN SUM(salamt*qy)
				END AS amount
				FROM cost
				WHERE 1=1
				AND cntrct_sn = %(s_cntrct_sn)s
				AND prjct_sn = %(s_prjct_sn)s
				AND extra_sn > 0
				GROUP BY extra_sn, cntrct_execut_code, ct_se_code
				ORDER BY extra_sn, cntrct_execut_code, ct_se_code"""
    g.curs.execute(query, params)
    result = g.curs.fetchall()
    return result

def get_c_cost_list_extra(params):
    query = """SELECT c.cntrct_sn
				, c.prjct_sn
				, c.cntrwk_ct_sn
				, c.cntrct_execut_code
				, (SELECT code_nm FROM code WHERE ctmmny_sn=1 AND parnts_code='CNTRCT_EXECUT_CODE' AND code=c.cntrct_execut_code) AS cntrct_execut_nm
				, c.ct_se_code
				, (SELECT code_nm FROM code WHERE ctmmny_sn=1 AND parnts_code='CT_SE_CODE' AND code=c.ct_se_code) AS ct_se_nm
				, c.purchsofc_sn
				, c.prdlst_se_code
				, (SELECT code_nm FROM code WHERE ctmmny_sn=1 AND parnts_code='PRDLST_SE_CODE' AND code=c.prdlst_se_code) AS prdlst_se_nm
				, c.model_no
				, c.qy
				, c.puchas_amount
				, c.salamt
				, c.dscnt_rt
				, c.add_dscnt_rt
				, c.extra_sn
				, c.fee_rt
				, c.dspy_se_code
				, (SELECT code_nm FROM code WHERE ctmmny_sn=1 AND parnts_code='DSPY_SE_CODE' AND code=c.dspy_se_code) AS dspy_se_nm
				, c.dspy_de
				, c.regist_dtm
				, c.register_id
				, c.update_dtm
				, c.updater_id
				FROM cost c
				WHERE 1=1
				AND cntrct_sn = %(s_cntrct_sn)s
				AND prjct_sn = %(s_prjct_sn)s
				AND cntrct_execut_code = 'B'
				ORDER BY c.regist_dtm
"""
    g.curs.execute(query, params)
    result = g.curs.fetchall()
    return result


def get_e_cost_list_extra(params):
    query = """SELECT c.cntrct_sn
				, c.prjct_sn
				, c.cntrwk_ct_sn
				, c.cntrct_execut_code
				, (SELECT code_nm FROM code WHERE ctmmny_sn=1 AND parnts_code='CNTRCT_EXECUT_CODE' AND code=c.cntrct_execut_code) AS cntrct_execut_nm
				, c.ct_se_code
				, (SELECT code_nm FROM code WHERE ctmmny_sn=1 AND parnts_code='CT_SE_CODE' AND code=c.ct_se_code) AS ct_se_nm
				, c.purchsofc_sn
				, c.prdlst_se_code
				, (SELECT code_nm FROM code WHERE ctmmny_sn=1 AND parnts_code='PRDLST_SE_CODE' AND code=c.prdlst_se_code) AS prdlst_se_nm
				, c.model_no
				, c.qy
				, c.puchas_amount
				, c.salamt
				, c.dscnt_rt
				, c.add_dscnt_rt
				, c.fee_rt
				, c.dspy_se_code
				, (SELECT code_nm FROM code WHERE ctmmny_sn=1 AND parnts_code='DSPY_SE_CODE' AND code=c.dspy_se_code) AS dspy_se_nm
				, c.dspy_de
				, c.regist_dtm
				, c.register_id
				, c.update_dtm
				, c.updater_id
				FROM cost c
				WHERE 1=1
				AND cntrct_sn = %(s_cntrct_sn)s
				AND prjct_sn = %(s_prjct_sn)s
				AND cntrct_execut_code = 'D'
				ORDER BY c.dspy_de
"""
    g.curs.execute(query, params)
    result = g.curs.fetchall()
    return result

def get_g_cost_list_extra(params):
    query = """SELECT c.cntrct_sn
				, c.prjct_sn
				, c.cntrwk_ct_sn
				, c.cntrct_execut_code
				, (SELECT code_nm FROM code WHERE ctmmny_sn=1 AND parnts_code='CNTRCT_EXECUT_CODE' AND code=c.cntrct_execut_code) AS cntrct_execut_nm
				, c.ct_se_code
				, (SELECT code_nm FROM code WHERE ctmmny_sn=1 AND parnts_code='CT_SE_CODE' AND code=c.ct_se_code) AS ct_se_nm
				, c.purchsofc_sn
				, c.prdlst_se_code
				, (SELECT code_nm FROM code WHERE ctmmny_sn=1 AND parnts_code='PRDLST_SE_CODE' AND code=c.prdlst_se_code) AS prdlst_se_nm
				, c.model_no
				, c.qy
				, c.puchas_amount
				, c.salamt
				, c.dscnt_rt
				, c.add_dscnt_rt
				, c.fee_rt
				, c.dspy_se_code
				, (SELECT code_nm FROM code WHERE ctmmny_sn=1 AND parnts_code='DSPY_SE_CODE' AND code=c.dspy_se_code) AS dspy_se_nm
				, c.dspy_de
				, c.regist_dtm
				, c.register_id
				, c.update_dtm
				, c.updater_id
				FROM cost c
				WHERE 1=1
				AND cntrct_sn = %(s_cntrct_sn)s
				AND prjct_sn = %(s_prjct_sn)s
				AND cntrct_execut_code = 'G'
				ORDER BY c.dspy_de
"""
    g.curs.execute(query, params)
    result = g.curs.fetchall()
    return result


def get_c_cost_list(params):
    query = """SELECT c.cntrct_sn
				, c.prjct_sn
				, c.cntrwk_ct_sn
				, c.cntrct_execut_code
				, (SELECT code_nm FROM code WHERE ctmmny_sn=1 AND parnts_code='CNTRCT_EXECUT_CODE' AND code=c.cntrct_execut_code) AS cntrct_execut_nm
				, c.ct_se_code
				, (SELECT code_nm FROM code WHERE ctmmny_sn=1 AND parnts_code='CT_SE_CODE' AND code=c.ct_se_code) AS ct_se_nm
				, c.purchsofc_sn
				, c.prdlst_se_code
				, (SELECT code_nm FROM code WHERE ctmmny_sn=1 AND parnts_code='PRDLST_SE_CODE' AND code=c.prdlst_se_code) AS prdlst_se_nm
				, c.model_no
				, c.qy
				, c.puchas_amount
				, c.salamt
				, c.dscnt_rt
				, c.add_dscnt_rt
				, c.extra_sn
				, c.fee_rt
				, c.dspy_se_code
				, (SELECT code_nm FROM code WHERE ctmmny_sn=1 AND parnts_code='DSPY_SE_CODE' AND code=c.dspy_se_code) AS dspy_se_nm
				, c.dspy_de
				, c.regist_dtm
				, c.register_id
				, c.update_dtm
				, c.updater_id
				FROM cost c
				WHERE 1=1
				AND cntrct_sn = %(s_cntrct_sn)s
				AND prjct_sn = %(s_prjct_sn)s
				AND cntrct_execut_code = 'C'
				ORDER BY c.regist_dtm
"""
    g.curs.execute(query, params)
    result = g.curs.fetchall()
    return result

def get_e_cost_list(params):
    query = """SELECT c.cntrct_sn
				, c.prjct_sn
				, c.cntrwk_ct_sn
				, c.cntrct_execut_code
				, (SELECT code_nm FROM code WHERE ctmmny_sn=1 AND parnts_code='CNTRCT_EXECUT_CODE' AND code=c.cntrct_execut_code) AS cntrct_execut_nm
				, c.ct_se_code
				, (SELECT code_nm FROM code WHERE ctmmny_sn=1 AND parnts_code='CT_SE_CODE' AND code=c.ct_se_code) AS ct_se_nm
				, c.purchsofc_sn
				, c.prdlst_se_code
				, (SELECT code_nm FROM code WHERE ctmmny_sn=1 AND parnts_code='PRDLST_SE_CODE' AND code=c.prdlst_se_code) AS prdlst_se_nm
				, c.model_no
				, c.qy
				, c.puchas_amount
				, c.salamt
				, c.dscnt_rt
				, c.add_dscnt_rt
				, c.fee_rt
				, c.dspy_se_code
				, (SELECT code_nm FROM code WHERE ctmmny_sn=1 AND parnts_code='DSPY_SE_CODE' AND code=c.dspy_se_code) AS dspy_se_nm
				, c.dspy_de
				, c.regist_dtm
				, c.register_id
				, c.update_dtm
				, c.updater_id
				FROM cost c
				WHERE 1=1
				AND cntrct_sn = %(s_cntrct_sn)s
				AND prjct_sn = %(s_prjct_sn)s
				AND cntrct_execut_code = 'E'
				ORDER BY c.dspy_de
"""
    g.curs.execute(query, params)
    result = g.curs.fetchall()
    return result

def get_g_cost_list(params):
    query = """SELECT c.cntrct_sn
				, c.prjct_sn
				, c.cntrwk_ct_sn
				, c.cntrct_execut_code
				, (SELECT code_nm FROM code WHERE ctmmny_sn=1 AND parnts_code='CNTRCT_EXECUT_CODE' AND code=c.cntrct_execut_code) AS cntrct_execut_nm
				, c.ct_se_code
				, (SELECT code_nm FROM code WHERE ctmmny_sn=1 AND parnts_code='CT_SE_CODE' AND code=c.ct_se_code) AS ct_se_nm
				, c.purchsofc_sn
				, c.prdlst_se_code
				, (SELECT code_nm FROM code WHERE ctmmny_sn=1 AND parnts_code='PRDLST_SE_CODE' AND code=c.prdlst_se_code) AS prdlst_se_nm
				, c.model_no
				, c.qy
				, c.puchas_amount
				, c.salamt
				, c.dscnt_rt
				, c.add_dscnt_rt
				, c.fee_rt
				, c.dspy_se_code
				, (SELECT code_nm FROM code WHERE ctmmny_sn=1 AND parnts_code='DSPY_SE_CODE' AND code=c.dspy_se_code) AS dspy_se_nm
				, c.dspy_de
				, c.regist_dtm
				, c.register_id
				, c.update_dtm
				, c.updater_id
				FROM cost c
				WHERE 1=1
				AND cntrct_sn = %(s_cntrct_sn)s
				AND prjct_sn = %(s_prjct_sn)s
				AND cntrct_execut_code = 'G'
				ORDER BY c.dspy_de
"""
    g.curs.execute(query, params)
    result = g.curs.fetchall()
    return result







def get_extra_cost_list(params):
    query = """SELECT cntrct_execut_code
				, 99 AS ct_se_code
				, SUM(CASE cntrct_execut_code
				WHEN 'E' THEN puchas_amount * qy
				WHEN 'C' THEN salamt*qy
				END) AS amount
				FROM cost
				WHERE 1=1
				AND cntrct_sn = %(s_cntrct_sn)s
				AND prjct_sn = %(s_prjct_sn)s
				AND extra_sn <> 0
				GROUP BY cntrct_execut_code
				ORDER BY cntrct_execut_code
"""
    g.curs.execute(query, params)
    result = g.curs.fetchall()
    return result

def get_c5_cost_list(params):
    query = """SELECT purchsofc_sn
				, cntrct_execut_code
				, ct_se_code
				, CASE cntrct_execut_code
				WHEN 'E' THEN puchas_amount
				WHEN 'C' THEN salamt
				END AS amount
				, qy AS qy
				, model_no
				FROM cost
				WHERE 1=1
				AND cntrct_sn = %(s_cntrct_sn)s
				AND prjct_sn = %(s_prjct_sn)s
				AND cntrct_execut_code = 'C'
				AND ct_se_code IN ('5')
"""
    g.curs.execute(query, params)
    result = g.curs.fetchall()
    return result

def get_e5_cost_list(params):
    query = """SELECT purchsofc_sn
				, cntrct_execut_code
				, ct_se_code
				, CASE cntrct_execut_code
				WHEN 'E' THEN puchas_amount
				WHEN 'C' THEN salamt
				END AS amount
				, qy AS qy
				, model_no
				FROM cost
				WHERE 1=1
				AND cntrct_sn = %(s_cntrct_sn)s
				AND prjct_sn = %(s_prjct_sn)s
				AND cntrct_execut_code = 'E'
				AND ct_se_code IN ('5')
"""
    g.curs.execute(query, params)
    result = g.curs.fetchall()
    return result

def get_rcppay_report_list(params):
    query = """SELECT co.purchsofc_sn
				FROM cost co
				WHERE co.cntrct_execut_code = 'C'
				AND co.cntrct_sn = %(s_cntrct_sn)s
				GROUP BY co.purchsofc_sn
"""
    g.curs.execute(query, params)
    result = g.curs.fetchall()

    for i, r in enumerate(result):
        pParams = {"s_cntrct_sn" : params['s_cntrct_sn'], "s_pblicte_trget_sn" : r['purchsofc_sn']}
        result[i]['sTaxbilList'] = get_s_taxbil_report_list(pParams)

        pParams = {"s_cntrct_sn": params['s_cntrct_sn'], "s_prvent_sn": r['purchsofc_sn']}
        result[i]['iRcppayList'] = get_i_rcppay_report_list(pParams)
    return result

def get_etc_rcppay_report_list(params):
    query = """SELECT r.rcppay_de AS rcppay_de
				, r.acntctgr_code
				, (SELECT code_nm FROM code WHERE parnts_code='ACNTCTGR_CODE' AND code=r.acntctgr_code) AS acntctgr_nm
				, IFNULL(r.rcppay_dtls, '') AS rcppay_dtls
				, r.papr_invstmnt_sn
				, (SELECT mber_nm FROM member WHERE mber_sn=r.papr_invstmnt_sn) AS papr_invstmnt_nm
				, IFNULL(r.amount, 0) AS amount
				, r.acnut_code
				, (SELECT code_nm FROM code WHERE parnts_code='ACNUT_CODE' AND code=r.acnut_code) AS acnut_nm
				, r.prvent_sn
				, (SELECT bcnc_nm FROM bcnc WHERE ctmmny_sn=r.ctmmny_sn AND bcnc_sn=r.prvent_sn) AS prvent_nm
				FROM rcppay r
				WHERE r.ctmmny_sn = 1
				AND r.cntrct_sn = %(s_cntrct_sn)s
				AND r.prjct_sn = %(s_prjct_sn)s
				AND r.rcppay_se_code = 'O'
				AND r.acntctgr_code NOT IN ('108', '638', '110', '504') 
				UNION ALL
				SELECT c.card_de AS rcppay_de
				, c.acntctgr_code
				, (SELECT code_nm FROM code WHERE parnts_code='ACNTCTGR_CODE' AND code=c.acntctgr_code) AS acntctgr_nm
				, IFNULL(c.card_dtls, '') AS rcppay_dtls
				, c.papr_invstmnt_sn
				, (SELECT mber_nm FROM member WHERE mber_sn=c.papr_invstmnt_sn) AS papr_invstmnt_nm
				, IFNULL(c.amount, 0) AS amount
				, '' AS acnut_code
				, '' AS acnut_nm
				, '' AS prvent_sn
				, '' AS prvent_nm
				FROM card c
				WHERE c.ctmmny_sn = 1
				AND c.cntrct_sn = %(s_cntrct_sn)s
				AND c.acntctgr_code NOT IN ('108', '638', '110', '504') 
				UNION ALL
				SELECT s.dlivy_de AS rcppay_de
				, '' AS acntctgr_code
				, '현장지원' AS acntctgr_nm
				, s.model_no AS rcppay_dtls
				, '' AS papr_invstmnt_sn
				, '' AS papr_invstmnt_nm
				, IFNULL((s.dlnt * s.dlamt), 0) AS amount
				, '' AS acnut_code
				, '' AS acnut_nm
				, '' AS prvent_sn
				, '' AS prvent_nm
				FROM account s
				LEFT JOIN account p
				ON s.ctmmny_sn=p.ctmmny_sn AND s.cntrct_sn=p.cntrct_sn AND s.prjct_sn=p.prjct_sn AND s.cnnc_sn=p.delng_sn
				WHERE s.ctmmny_sn = 1
				AND s.cntrct_sn = %(s_cntrct_sn)s
				AND s.delng_se_code = 'S'
				AND p.delng_ty_code IN ('1', '2')
				AND s.delng_ty_code = 14
				ORDER BY rcppay_de
"""
    g.curs.execute(query, params)
    result = g.curs.fetchall()
    return result



def get_s1_account_report_list(params):
    query = """SELECT s.dlivy_de AS s_dlivy_de
				, s.model_no AS s_model_no
				, IF (s.prdlst_se_code = '1', s.dlnt, '') AS dlnt1
				, IF (s.prdlst_se_code = '2', s.dlnt, '') AS dlnt2
				, IF (s.prdlst_se_code = '3', s.dlnt, '') AS dlnt3
				, IF (s.prdlst_se_code = '4', s.dlnt, '') AS dlnt4
				, IF (s.prdlst_se_code = '9', s.dlnt, '') AS dlnt9
				, p.dlamt AS p_dlamt
				, (s.dlnt * p.dlamt) AS p_total
				, p.bcnc_sn AS p_bcnc_sn
				, (SELECT bcnc_nm FROM bcnc WHERE ctmmny_sn=p.ctmmny_sn AND bcnc_sn=p.bcnc_sn) AS p_bcnc_nm
				, s.dlamt AS s_dlamt
				, (s.dlnt * s.dlamt) AS s_total
				, s.bcnc_sn AS s_bcnc_sn
				, (SELECT bcnc_nm FROM bcnc WHERE ctmmny_sn=s.ctmmny_sn AND bcnc_sn=s.bcnc_sn) AS s_bcnc_nm
				FROM account s
				LEFT JOIN account p
				ON s.ctmmny_sn=p.ctmmny_sn AND s.cntrct_sn=p.cntrct_sn AND s.prjct_sn=p.prjct_sn AND s.cnnc_sn=p.delng_sn
				WHERE s.ctmmny_sn = 1
				AND s.cntrct_sn = %(s_cntrct_sn)s
				AND s.prjct_sn = %(s_prjct_sn)s
				AND s.delng_se_code = 'S'
				AND p.delng_ty_code IN ('1')
				AND s.delng_ty_code <> 14
"""
    g.curs.execute(query, params)
    result = g.curs.fetchall()
    return result

def get_s2_account_report_list(params):
    query = """SELECT a.dlivy_de
				, a.prdlst_se_code
				, (SELECT code_nm FROM code WHERE ctmmny_sn=a.ctmmny_sn AND parnts_code='PRDLST_SE_CODE' AND code=a.prdlst_se_code) AS prdlst_se_nm
				, a.model_no
				, a.dlnt
				, ac.dlamt AS p_dlamt
				, (a.dlnt * ac.dlamt) AS p_total
				, ac.bcnc_sn AS p_bcnc_sn
				, (SELECT bcnc_nm FROM bcnc WHERE ctmmny_sn=ac.ctmmny_sn AND bcnc_sn=ac.bcnc_sn) AS p_bcnc_nm
				, a.dlamt AS s_dlamt
				, (a.dlnt * a.dlamt) AS s_total
				, a.bcnc_sn AS s_bcnc_sn
				, (SELECT bcnc_nm FROM bcnc WHERE ctmmny_sn=a.ctmmny_sn AND bcnc_sn=a.bcnc_sn) AS s_bcnc_nm
				FROM account a
				LEFT JOIN account ac
				ON a.ctmmny_sn=ac.ctmmny_sn AND a.cntrct_sn=ac.cntrct_sn AND a.prjct_sn=ac.prjct_sn AND a.cnnc_sn=ac.delng_sn
				WHERE a.ctmmny_sn = 1
				AND a.cntrct_sn = %(s_cntrct_sn)s
				AND a.prjct_sn = %(s_prjct_sn)s
				AND a.delng_se_code = 'S'
				AND ac.delng_ty_code = '2'
				AND a.delng_ty_code <> 14
				ORDER BY a.dlivy_de
"""
    g.curs.execute(query, params)
    result = g.curs.fetchall()
    return result

def get_s3_account_report_list(params):
    query = """SELECT a.dlivy_de
				, a.prdlst_se_code
				, (SELECT code_nm FROM code WHERE ctmmny_sn=a.ctmmny_sn AND parnts_code='PRDLST_SE_CODE' AND code=a.prdlst_se_code) AS prdlst_se_nm
				, a.model_no
				, a.dlnt
				, ac.dlamt AS p_dlamt
				, (a.dlnt * ac.dlamt) AS p_total
				, ac.bcnc_sn AS p_bcnc_sn
				, (SELECT bcnc_nm FROM bcnc WHERE ctmmny_sn=ac.ctmmny_sn AND bcnc_sn=ac.bcnc_sn) AS p_bcnc_nm
				, a.dlamt AS s_dlamt
				, (a.dlnt * a.dlamt) AS s_total
				, (ac.dlnt * ac.dlamt) AS p_total
				, a.bcnc_sn AS s_bcnc_sn
				, (SELECT bcnc_nm FROM bcnc WHERE ctmmny_sn=a.ctmmny_sn AND bcnc_sn=a.bcnc_sn) AS s_bcnc_nm
				, a.rm
				FROM account a
				LEFT JOIN account ac
				ON a.ctmmny_sn=ac.ctmmny_sn AND a.cntrct_sn=ac.cntrct_sn AND a.prjct_sn=ac.prjct_sn AND a.cnnc_sn=ac.delng_sn
				WHERE a.ctmmny_sn = 1
				AND a.cntrct_sn = %(s_cntrct_sn)s
				AND a.prjct_sn = %(s_prjct_sn)s
				AND a.delng_se_code = 'S'
				AND ac.delng_ty_code = '3'
				ORDER BY a.dlivy_de
"""
    g.curs.execute(query, params)
    result = g.curs.fetchall()
    return result

def get_s4_account_report_list(params):
    query = """SELECT a.dlivy_de
    				, a.prdlst_se_code
    				, (SELECT code_nm FROM code WHERE ctmmny_sn=a.ctmmny_sn AND parnts_code='PRDLST_SE_CODE' AND code=a.prdlst_se_code) AS prdlst_se_nm
    				, a.model_no
    				, a.dlnt
    				, ac.dlamt AS p_dlamt
    				, (a.dlnt * ac.dlamt) AS p_total
    				, ac.bcnc_sn AS p_bcnc_sn
    				, (SELECT bcnc_nm FROM bcnc WHERE ctmmny_sn=ac.ctmmny_sn AND bcnc_sn=ac.bcnc_sn) AS p_bcnc_nm
    				, a.dlamt AS s_dlamt
    				, (a.dlnt * a.dlamt) AS s_total
    				, (ac.dlnt * ac.dlamt) AS p_total
    				, a.bcnc_sn AS s_bcnc_sn
    				, (SELECT bcnc_nm FROM bcnc WHERE ctmmny_sn=a.ctmmny_sn AND bcnc_sn=a.bcnc_sn) AS s_bcnc_nm
    				, a.rm
    				, ac.model_no AS model_where
    				FROM account a
    				LEFT JOIN account ac
    				ON a.ctmmny_sn=ac.ctmmny_sn AND a.cntrct_sn=ac.cntrct_sn AND a.prjct_sn=ac.prjct_sn AND a.cnnc_sn=ac.delng_sn
    				WHERE a.ctmmny_sn = 1
    				AND a.cntrct_sn = %(s_cntrct_sn)s
    				AND a.prjct_sn = %(s_prjct_sn)s
    				AND a.delng_se_code = 'S'
    				AND ac.delng_ty_code = '4'
    				ORDER BY a.dlivy_de
    """
    g.curs.execute(query, params)
    result = g.curs.fetchall()
    return result

def get_sale_model_list(params):
    query = """SELECT IFNULL(s.dlivy_de, '') AS dlivy_de
                    , p.model_no AS model_no
                    , p.prdlst_se_code AS prdlst_se_code
                    , (SELECT code_nm FROM code WHERE parnts_code='PRDLST_SE_CODE' AND code=p.prdlst_se_code) AS prdlst_se_nm
                    , s.dlamt AS dlamt
                    , s.dlnt AS dlnt
                    , p.bcnc_sn AS bcnc_sn
                    , (SELECT bcnc_nm FROM bcnc WHERE bcnc_sn=p.bcnc_sn) AS bcnc_nm
                    , p.wrhousng_de AS expect_de
                    , p.delng_sn AS delng_sn
                    , p.model_no
                FROM (SELECT * FROM account WHERE delng_se_code='P' AND delng_ty_code IN ('63', '66')) p
                LEFT OUTER JOIN account s
                ON s.cnnc_sn=p.delng_sn
                WHERE 1=1
				AND p.cntrct_sn = %(s_cntrct_sn)s
				AND p.prjct_sn = %(s_prjct_sn)s
            """
    g.curs.execute(query, params)
    result = g.curs.fetchall()
    return result

def get_model_cost_list(params):
    query = """SELECT IFNULL(s.dlivy_de, '') AS dlivy_de
                    , p.model_no AS model_no
                    , p.prdlst_se_code AS prdlst_se_code
                    , (SELECT code_nm FROM code WHERE parnts_code='PRDLST_SE_CODE' AND code=p.prdlst_se_code) AS prdlst_se_nm
                    , p.dlamt AS dlamt
                    , p.dlnt AS dlnt
                    , p.bcnc_sn AS bcnc_sn
                    , (SELECT bcnc_nm FROM bcnc WHERE bcnc_sn=p.bcnc_sn) AS bcnc_nm
                    , p.wrhousng_de AS expect_de
                    , p.delng_sn AS delng_sn
                FROM (SELECT * FROM account WHERE delng_se_code='P' AND delng_ty_code IN ('61', '62')) p
                LEFT OUTER JOIN account s
                ON s.cnnc_sn=p.delng_sn
                WHERE 1=1
				AND p.cntrct_sn = %(s_cntrct_sn)s
				AND p.prjct_sn = %(s_prjct_sn)s
            """
    g.curs.execute(query, params)
    result = g.curs.fetchall()
    return result

def get_s61_account_report_list(params):
    query = """SELECT s.dlivy_de AS s_dlivy_de
				, s.model_no AS s_model_no
				, IF (s.prdlst_se_code = '1', s.dlnt, '') AS dlnt1
				, IF (s.prdlst_se_code = '2', s.dlnt, '') AS dlnt2
				, IF (s.prdlst_se_code = '3', s.dlnt, '') AS dlnt3
				, IF (s.prdlst_se_code = '4', s.dlnt, '') AS dlnt4
				, IF (s.prdlst_se_code = '9', s.dlnt, '') AS dlnt9
				, p.dlamt AS p_dlamt
				, (s.dlnt * p.dlamt) AS p_total
				, p.bcnc_sn AS p_bcnc_sn
				, (SELECT bcnc_nm FROM bcnc WHERE ctmmny_sn=p.ctmmny_sn AND bcnc_sn=p.bcnc_sn) AS p_bcnc_nm
				, s.dlamt AS s_dlamt
				, (s.dlnt * s.dlamt) AS s_total
				, s.bcnc_sn AS s_bcnc_sn
				, s.rm AS rm
				, (SELECT bcnc_nm FROM bcnc WHERE ctmmny_sn=s.ctmmny_sn AND bcnc_sn=s.bcnc_sn) AS s_bcnc_nm
				FROM account s
				LEFT JOIN account p
				ON s.ctmmny_sn=p.ctmmny_sn AND s.cntrct_sn=p.cntrct_sn AND s.prjct_sn=p.prjct_sn AND s.cnnc_sn=p.delng_sn
				WHERE s.ctmmny_sn = 1
				AND s.cntrct_sn = %(s_cntrct_sn)s
				AND s.prjct_sn = %(s_prjct_sn)s
				AND s.delng_se_code = 'S'
				AND p.delng_ty_code IN ('61', '62')
				UNION
				SELECT t.pblicte_de AS s_dlivy_de
				, IF(t.delng_se_code = 'S2', '모델하우스 정산금액' ,'설치비') AS s_model_no
				, '' AS dlnt1
				, '' AS dlnt2
				, '' AS dlnt3
				, '' AS dlnt4
				, 1 AS dlnt9
				, IF(t.delng_se_code = 'S2', -1*(t.splpc_am + t.vat), (t.splpc_am + t.vat)) AS p_dlamt
				, IF(t.delng_se_code = 'S2', -1*(t.splpc_am + t.vat), (t.splpc_am + t.vat)) AS p_total
				, t.pblicte_trget_sn AS p_bcnc_sn
				, (SELECT bcnc_nm FROM bcnc WHERE ctmmny_sn=1 AND bcnc_sn=t.pblicte_trget_sn) AS p_bcnc_nm
				, IF(t.delng_se_code = 'S2', -1*(t.splpc_am + t.vat), (t.splpc_am + t.vat)) AS s_dlamt
				, IF(t.delng_se_code = 'S2', -1*(t.splpc_am + t.vat), (t.splpc_am + t.vat)) AS s_total
				, t.pblicte_trget_sn AS s_bcnc_sn
				, '' AS rm
				, (SELECT bcnc_nm FROM bcnc WHERE ctmmny_sn=1 AND bcnc_sn=t.pblicte_trget_sn) AS s_bcnc_nm
				FROM taxbil t
				LEFT JOIN contract c
				ON t.cntrct_sn = c.cntrct_sn
				WHERE t.ctmmny_sn = 1
				AND t.cntrct_sn = %(s_cntrct_sn)s
				AND t.prjct_sn = %(s_prjct_sn)s
				AND c.prjct_ty_code = 'NR'
				AND t.delng_se_code IN ('S2', 'P1')
				ORDER BY s_dlivy_de
"""
    g.curs.execute(query, params)
    result = g.curs.fetchall()
    return result

def get_outsrc_list(params):
    query = """SELECT o.cntrct_sn
    				, o.prjct_sn
    				, o.outsrc_fo_sn
    				, (SELECT bcnc_nm FROM bcnc WHERE ctmmny_sn=1 AND bcnc_sn=o.outsrc_fo_sn) AS outsrc_fo_nm
    				, o.cntrct_de
    				, o.outsrc_sn
    				, rspnber_nm
    				, rspnber_telno
    				, charger_nm
    				, charger_telno
    				, pymnt_mth
    				, outsrc_dtls
    				FROM outsrc o
    				WHERE o.cntrct_sn = %(s_cntrct_sn)s
    				AND o.prjct_sn = %(s_prjct_sn)s
    """
    g.curs.execute(query, params)
    result = g.curs.fetchall()
    return result

def get_outsrc_detail(params):
    result = dict()
    query = """SELECT o.cntrct_sn
				, o.prjct_sn
				, o.outsrc_fo_sn
				, (SELECT bcnc_nm FROM bcnc WHERE ctmmny_sn=1 AND bcnc_sn=o.outsrc_fo_sn) AS outsrc_fo_nm
				, o.cntrct_de
				, o.outsrc_sn
				, rspnber_nm
				, rspnber_telno
				, charger_nm
				, charger_telno
				, pymnt_mth
				, outsrc_dtls
				FROM outsrc o
				WHERE o.cntrct_sn = %(s_cntrct_sn)s
				AND o.prjct_sn = %(s_prjct_sn)s
				AND o.outsrc_fo_sn = %(s_outsrc_fo_sn)s """
    g.curs.execute(query, params)
    result['outsrc'] = g.curs.fetchone()
    params['s_outsrc_sn'] = result['outsrc']['outsrc_sn']

    query = """SELECT item_sn
                , item_damt AS amount
                , item_dlnt AS qy
                , item_nm AS model_no
                , (SELECT SUM(item_damt*item_dlnt) FROM outsrc_item WHERE outsrc_sn=o.outsrc_sn) AS total
                FROM outsrc_item oi
                LEFT JOIN outsrc o ON oi.outsrc_sn=o.outsrc_sn
                WHERE 1=1
                AND o.outsrc_sn = %(s_outsrc_sn)s"""
    g.curs.execute(query, params)
    result['e5CostList'] = g.curs.fetchall()

    query = """SELECT t.pblicte_de
    				, t.splpc_am
    				, t.vat
    				, (t.splpc_am + t.vat) AS total
    				, t.pblicte_trget_sn
    				, (SELECT bcnc_nm FROM bcnc WHERE ctmmny_sn=t.ctmmny_sn AND bcnc_sn=t.pblicte_trget_sn) AS pblicte_trget_nm
    				, t.rm
    				FROM taxbil t
    				WHERE t.ctmmny_sn = 1
    				AND t.cntrct_sn = %(s_cntrct_sn)s
    				AND t.prjct_sn = %(s_prjct_sn)s
    				AND t.delng_se_code = 'P' 
    				AND t.pblicte_trget_sn = %(s_outsrc_fo_sn)s 
    				ORDER BY t.pblicte_de, t.pblicte_trget_sn"""
    g.curs.execute(query, params)
    result["taxbilList"] = g.curs.fetchall()

    query = """SELECT r.rcppay_de
    				, r.amount
    				, r.acnut_code
    				, (SELECT code_nm FROM code WHERE parnts_code='ACNUT_CODE' AND code=r.acnut_code) AS acnut_nm
    				, r.prvent_sn
    				, (SELECT bcnc_nm FROM bcnc WHERE ctmmny_sn=r.ctmmny_sn AND bcnc_sn=r.prvent_sn) AS prvent_nm
    				, r.rcppay_dtls
    				FROM rcppay r
    				WHERE r.ctmmny_sn = 1
    				AND r.cntrct_sn = %(s_cntrct_sn)s
    				AND r.prjct_sn = %(s_prjct_sn)s
    				AND r.rcppay_se_code = 'O' 
    				AND r.acntctgr_code = '638' 
    				AND r.prvent_sn = %(s_outsrc_fo_sn)s
    				ORDER BY r.rcppay_de"""
    g.curs.execute(query, params)
    result['rcppayList'] = g.curs.fetchall()

    return result
def get_outsrc_report_list(params):
    query = """SELECT o.cntrct_sn
				, o.prjct_sn
				, o.outsrc_fo_sn
				, (SELECT bcnc_nm FROM bcnc WHERE ctmmny_sn=1 AND bcnc_sn=o.outsrc_fo_sn) AS outsrc_fo_nm
				, o.cntrct_de
				, rspnber_nm
				, rspnber_telno
				, charger_nm
				, charger_telno
				, pymnt_mth
				, outsrc_dtls
			    , r.r_dt_bg
			    , r.r_dt_ed
			    , r.r_dt_reg
			    , r.rm
				FROM outsrc o
				LEFT OUTER JOIN reserved r
				ON o.outsrc_fo_sn=r.outsrc_fo_sn AND o.cntrct_sn=r.cntrct_sn
				WHERE o.cntrct_sn = %(s_cntrct_sn)s
				AND o.prjct_sn = %(s_prjct_sn)s
"""
    g.curs.execute(query, params)
    result = g.curs.fetchall()

    for i, r in enumerate(result):
        pParams = {k:v for k, v in params.items()}
        pParams['outsrc_fo_sn'] = r['outsrc_fo_sn']
        query = """SELECT purchsofc_sn
                    , cntrct_execut_code
                    , ct_se_code
                    , CASE cntrct_execut_code
                    WHEN 'E' THEN puchas_amount
                    WHEN 'C' THEN salamt
                    END AS amount
                    , qy AS qy
                    , model_no
                    , (SELECT SUM(puchas_amount*qy)
                    FROM cost
                    WHERE cntrct_sn=c.cntrct_sn
                    AND prjct_sn=c.prjct_sn
                    AND cntrct_execut_code=c.cntrct_execut_code
                    AND ct_se_code=c.ct_se_code
                    AND purchsofc_sn=c.purchsofc_sn
                    ) AS total
                    FROM cost c
                    WHERE 1=1
                    AND cntrct_sn = %(s_cntrct_sn)s
                    AND prjct_sn = %(s_prjct_sn)s
                    AND cntrct_execut_code = 'E'
                    AND ct_se_code IN ('5')
                    AND purchsofc_sn = %(outsrc_fo_sn)s"""
        g.curs.execute(query, pParams)
        result[i]['e5CostList'] = g.curs.fetchall()

        query = """SELECT t.pblicte_de
				, t.splpc_am
				, t.vat
				, (t.splpc_am + t.vat) AS total
				, t.pblicte_trget_sn
				, (SELECT bcnc_nm FROM bcnc WHERE ctmmny_sn=t.ctmmny_sn AND bcnc_sn=t.pblicte_trget_sn) AS pblicte_trget_nm
				, t.rm
				FROM taxbil t
				WHERE t.ctmmny_sn = 1
				AND t.cntrct_sn = %(s_cntrct_sn)s
				AND t.prjct_sn = %(s_prjct_sn)s
				AND t.delng_se_code = 'P' 
				AND t.pblicte_trget_sn = %(outsrc_fo_sn)s 
				ORDER BY t.pblicte_de, t.pblicte_trget_sn"""
        g.curs.execute(query, pParams)
        result[i]["taxbilList"] = g.curs.fetchall()

        query = """SELECT r.rcppay_de
				, r.amount
				, r.acnut_code
				, (SELECT code_nm FROM code WHERE parnts_code='ACNUT_CODE' AND code=r.acnut_code) AS acnut_nm
				, r.prvent_sn
				, (SELECT bcnc_nm FROM bcnc WHERE ctmmny_sn=r.ctmmny_sn AND bcnc_sn=r.prvent_sn) AS prvent_nm
				, r.rcppay_dtls
				FROM rcppay r
				WHERE r.ctmmny_sn = 1
				AND r.cntrct_sn = %(s_cntrct_sn)s
				AND r.prjct_sn = %(s_prjct_sn)s
				AND r.rcppay_se_code = 'O' 
				AND r.acntctgr_code = '638' 
				AND r.prvent_sn = %(outsrc_fo_sn)s
				ORDER BY r.rcppay_de"""
        g.curs.execute(query, pParams)
        result[i]['rcppayList'] = g.curs.fetchall()

    return result

def get_s_taxbil_report_list(params):
    query = """SELECT t.pblicte_de
				, t.splpc_am
				, IFNULL(t.vat,0) AS vat
				, (t.splpc_am + IFNULL(t.vat,0)) AS total
				, t.pblicte_trget_sn
				, (SELECT bcnc_nm FROM bcnc WHERE ctmmny_sn=t.ctmmny_sn AND bcnc_sn=t.pblicte_trget_sn) AS pblicte_trget_nm
				FROM taxbil t
				WHERE t.ctmmny_sn = 1
				AND t.cntrct_sn = %(s_cntrct_sn)s
"""
    if "s_pblicte_trget_sn" in params and params["s_pblicte_trget_sn"]:
        query += " AND t.pblicte_trget_sn = %(s_pblicte_trget_sn)s "
    query += """ AND t.delng_se_code = 'S' 
				ORDER BY t.pblicte_trget_sn, t.pblicte_de
"""
    g.curs.execute(query, params)
    result = g.curs.fetchall()
    return result

def get_i_rcppay_report_list(params):
    query = """SELECT r.rcppay_de
				, r.amount
				, r.acnut_code
				, (SELECT code_nm FROM code WHERE parnts_code='ACNUT_CODE' AND code=r.acnut_code) AS acnut_nm
				, r.prvent_sn
				, (SELECT bcnc_nm FROM bcnc WHERE ctmmny_sn=r.ctmmny_sn AND bcnc_sn=r.prvent_sn) AS prvent_nm
				, r.rcppay_dtls
				, (SELECT SUM(co.salamt*co.qy) AS amount FROM cost co WHERE co.cntrct_sn=r.cntrct_sn AND co.purchsofc_sn=r.prvent_sn AND co.cntrct_execut_code='C') AS cntrct_amount
				FROM rcppay r
				WHERE r.ctmmny_sn = 1
				AND r.cntrct_sn = %(s_cntrct_sn)s
"""
    if "s_prvent_sn" in params and params["s_prvent_sn"]:
        query += " AND r.prvent_sn = %(s_prvent_sn)s "

    query += """ AND r.rcppay_se_code = 'I' 
                 ORDER BY r.rcppay_de
    """

    g.curs.execute(query, params)
    result = g.curs.fetchall()
    return result


def get_s2_taxbil_report_list(params):
    query = """SELECT t.pblicte_de
				, t.splpc_am
				, t.vat
				, (t.splpc_am + t.vat) AS total
				, t.pblicte_trget_sn
				, t.delng_se_code
				, (SELECT bcnc_nm FROM bcnc WHERE ctmmny_sn=t.ctmmny_sn AND bcnc_sn=t.pblicte_trget_sn) AS pblicte_trget_nm
				FROM taxbil t
				WHERE t.ctmmny_sn = 1
				AND t.cntrct_sn = %(s_cntrct_sn)s
				AND t.prjct_sn = %(s_prjct_sn)s
				AND t.delng_se_code IN ('S2', 'S4')
				ORDER BY t.delng_se_code, t.pblicte_de, t.pblicte_trget_sn
"""
    g.curs.execute(query, params)
    result = g.curs.fetchall()
    return result

def get_i2_rcppay_report_list(params):
    query = """SELECT r.rcppay_de
				, r.amount
				, r.acnut_code
				, (SELECT code_nm FROM code WHERE parnts_code='ACNUT_CODE' AND code=r.acnut_code) AS acnut_nm
				, r.prvent_sn
				, (SELECT bcnc_nm FROM bcnc WHERE ctmmny_sn=r.ctmmny_sn AND bcnc_sn=r.prvent_sn) AS prvent_nm
				, r.rcppay_dtls
				, rcppay_se_code
				FROM rcppay r
				WHERE r.ctmmny_sn = 1
				AND r.cntrct_sn = %(s_cntrct_sn)s
				AND r.prjct_sn = %(s_prjct_sn)s
				AND r.rcppay_se_code IN ('I2', 'I4')
				ORDER BY r.rcppay_de
"""
    g.curs.execute(query, params)
    result = g.curs.fetchall()
    return result

def get_s3_taxbil_report_list(params):
    query = """SELECT t.pblicte_de
				, t.splpc_am
				, IFNULL(t.vat, 0) AS vat
				, (t.splpc_am + IFNULL(t.vat, 0)) AS total
				, t.pblicte_trget_sn
				, t.taxbil_sn
				, (SELECT bcnc_nm FROM bcnc WHERE ctmmny_sn=t.ctmmny_sn AND bcnc_sn=t.pblicte_trget_sn) AS pblicte_trget_nm
				FROM taxbil t
				WHERE t.ctmmny_sn = 1
				AND t.cntrct_sn = %(s_cntrct_sn)s
				AND t.prjct_sn = %(s_prjct_sn)s
				AND t.delng_se_code = 'S3'
				ORDER BY t.pblicte_de, t.pblicte_trget_sn
"""
    g.curs.execute(query, params)
    result = g.curs.fetchall()
    return result

def get_i3_rcppay_report_list(params):
    query = """SELECT r.rcppay_de
				, r.amount
				, r.acnut_code
				, (SELECT code_nm FROM code WHERE parnts_code='ACNUT_CODE' AND code=r.acnut_code) AS acnut_nm
				, r.prvent_sn
				, (SELECT bcnc_nm FROM bcnc WHERE ctmmny_sn=r.ctmmny_sn AND bcnc_sn=r.prvent_sn) AS prvent_nm
				, r.rcppay_dtls
				, r.cnnc_sn
				FROM rcppay r
				WHERE r.ctmmny_sn = 1
				AND r.cntrct_sn = %(s_cntrct_sn)s
				AND r.prjct_sn = %(s_prjct_sn)s
				AND r.rcppay_se_code = 'I3' 
				ORDER BY r.rcppay_de
"""
    g.curs.execute(query, params)
    result = g.curs.fetchall()
    return result

def get_s12_account_report_list(params):
    query = """SELECT s.dlivy_de AS s_dlivy_de
				, s.model_no AS s_model_no
				, s.dlnt AS s_dlnt
				, s.dlamt AS s_dlamt
				, s.wrhousng_de AS s_wrhousng_de
				, s.rm AS s_rm
				, p.dlivy_amt AS p_dlivy_amt
				, p.dscnt_rt AS p_dscnt_rt
				, p.add_dscnt_rt AS p_add_dscnt_rt
				, p.dlamt AS p_dlamt
				, p.bcnc_sn AS p_bcnc_sn
				, (SELECT bcnc_nm FROM bcnc WHERE ctmmny_sn=p.ctmmny_sn AND bcnc_sn=p.bcnc_sn) AS p_bcnc_nm
				, p.delng_ty_code AS p_delng_ty_code
				, p.delng_sn AS p_delng_sn
				FROM account s
				LEFT JOIN account p
				ON s.ctmmny_sn=p.ctmmny_sn AND s.cntrct_sn=p.cntrct_sn AND s.prjct_sn=p.prjct_sn AND s.cnnc_sn=p.delng_sn
				WHERE s.ctmmny_sn = 1
				AND s.cntrct_sn = %(s_cntrct_sn)s
				AND s.prjct_sn = %(s_prjct_sn)s
				AND s.delng_se_code = 'S'
				AND s.delng_ty_code NOT IN ('14')
				AND p.delng_ty_code IN ('1', '2')
				ORDER BY s.dlivy_de
"""
    g.curs.execute(query, params)
    result = g.curs.fetchall()
    return result

def get_s6_account_report_list(params):
    query = """SELECT s.dlivy_de AS s_dlivy_de
				, s.model_no AS s_model_no
				, s.dlnt AS s_dlnt
				, s.dlamt AS s_dlamt
				, s.wrhousng_de AS s_wrhousng_de
				, s.rm AS s_rm
				, p.dlivy_amt AS p_dlivy_amt
				, p.dscnt_rt AS p_dscnt_rt
				, p.add_dscnt_rt AS p_add_dscnt_rt
				, p.dlamt AS p_dlamt
				, p.bcnc_sn AS p_bcnc_sn
				, (SELECT bcnc_nm FROM bcnc WHERE ctmmny_sn=p.ctmmny_sn AND bcnc_sn=p.bcnc_sn) AS p_bcnc_nm
				, p.delng_ty_code AS p_delng_ty_code
				, p.delng_sn AS p_delng_sn
				FROM account s
				LEFT JOIN account p
				ON s.ctmmny_sn=p.ctmmny_sn AND s.cntrct_sn=p.cntrct_sn AND s.prjct_sn=p.prjct_sn AND s.cnnc_sn=p.delng_sn
				WHERE s.ctmmny_sn = 1
				AND s.cntrct_sn = %(s_cntrct_sn)s
				AND s.prjct_sn = %(s_prjct_sn)s
				AND s.delng_se_code = 'S'
				AND p.delng_ty_code IN ('61', '62', '64', '65')
				ORDER BY s.dlivy_de
"""
    g.curs.execute(query, params)
    result = g.curs.fetchall()
    return result

def get_s7_account_report_list(params):
    query = """SELECT s.dlivy_de AS s_dlivy_de
				, s.model_no AS s_model_no
				, s.dlnt AS s_dlnt
				, s.dlamt AS s_dlamt
				, s.wrhousng_de AS s_wrhousng_de
				, s.rm AS s_rm
				, p.dlivy_amt AS p_dlivy_amt
				, p.dscnt_rt AS p_dscnt_rt
				, p.add_dscnt_rt AS p_add_dscnt_rt
				, p.dlamt AS p_dlamt
				, p.bcnc_sn AS p_bcnc_sn
				, (SELECT bcnc_nm FROM bcnc WHERE ctmmny_sn=p.ctmmny_sn AND bcnc_sn=p.bcnc_sn) AS p_bcnc_nm
				, p.delng_ty_code AS p_delng_ty_code
				, p.delng_sn AS p_delng_sn
				FROM account s
				LEFT JOIN account p
				ON s.ctmmny_sn=p.ctmmny_sn AND s.cntrct_sn=p.cntrct_sn AND s.prjct_sn=p.prjct_sn AND s.cnnc_sn=p.delng_sn
				WHERE s.ctmmny_sn = 1
				AND s.cntrct_sn = %(s_cntrct_sn)s
				AND s.prjct_sn = %(s_prjct_sn)s
				AND s.delng_se_code = 'S'
				AND p.delng_ty_code IN ('7')
				ORDER BY s.dlivy_de
"""
    g.curs.execute(query, params)
    result = g.curs.fetchall()
    return result

def get_s1_taxbil_report_list(params):
    query = """SELECT t.pblicte_de
				, t.splpc_am
				, t.vat
				, (t.splpc_am + t.vat) AS total
				, t.pblicte_trget_sn
				, (SELECT bcnc_nm FROM bcnc WHERE ctmmny_sn=t.ctmmny_sn AND bcnc_sn=t.pblicte_trget_sn) AS pblicte_trget_nm
				FROM taxbil t
				WHERE t.ctmmny_sn = 1
				AND t.cntrct_sn = %(s_cntrct_sn)s
				AND t.prjct_sn = %(s_prjct_sn)s
				AND t.delng_se_code = 'S1'
				ORDER BY t.pblicte_de, t.pblicte_trget_sn
"""
    g.curs.execute(query, params)
    result = g.curs.fetchall()
    return result

def get_i1_rcppay_report_list(params):
    query = """SELECT r.rcppay_de
				, r.amount
				, r.acnut_code
				, (SELECT code_nm FROM code WHERE parnts_code='ACNUT_CODE' AND code=r.acnut_code) AS acnut_nm
				, r.prvent_sn
				, (SELECT bcnc_nm FROM bcnc WHERE ctmmny_sn=r.ctmmny_sn AND bcnc_sn=r.prvent_sn) AS prvent_nm
				, r.rcppay_dtls
				FROM rcppay r
				WHERE r.ctmmny_sn = 1
				AND r.cntrct_sn = %(s_cntrct_sn)s
				AND r.prjct_sn = %(s_prjct_sn)s
				AND r.rcppay_se_code = 'I1'
				ORDER BY r.rcppay_de
"""
    g.curs.execute(query, params)
    result = g.curs.fetchall()
    return result


def get_finals(params):
    query = """SELECT c.ctmmny_sn
				, m.dept_code
				, (SELECT code_nm FROM code WHERE ctmmny_sn=1 AND parnts_code='DEPT_CODE' AND code=k.dept_code) AS dept_nm
				, c.cntrct_sn
				, c.cntrct_de
				, c.bcnc_sn
				, (SELECT bcnc_nm FROM bcnc WHERE bcnc_sn=c.bcnc_sn) AS bcnc_nm
				, c.spt_nm
				, c.spt_chrg_sn
				, GET_MEMBER_NAME(c.spt_chrg_sn, 'S') AS spt_chrg_nm
				, (SELECT code_nm FROM code WHERE ctmmny_sn=1 AND parnts_code='PRJCT_TY_CODE' AND code=p.prjct_ty_code) AS prjct_ty_nm
				, f.finals_amt1
				, f.finals_amt2
				, f.finals_amt3
				, f.finals_amt4
				, f.finals_amt5
				, f.finals_amt6
				, f.finals_sn
				FROM contract c
				LEFT OUTER JOIN member m
				ON m.mber_sn=c.spt_chrg_sn
				LEFT OUTER JOIN member k
				ON k.mber_sn=c.bsn_chrg_sn
				LEFT OUTER JOIN project p
				ON p.cntrct_sn=c.cntrct_sn
				LEFT OUTER JOIN finals f
				ON f.cntrct_sn=c.cntrct_sn
				WHERE 1=1
				AND (c.cntrct_de BETWEEN '{0} 00:00:00'
				AND '{1} 23:59:59')
				AND c.progrs_sttus_code IN ('B', 'P', 'S')
				AND IFNULL(f.finals_done, 'P')='P'
				AND c.prjct_creat_at = 'Y'""".format(params['s_cntrct_de_start'], params['s_cntrct_de_end'])

    data = []



    if "s_spt_nm" in params and params['s_spt_nm']:
        query += " AND c.spt_nm LIKE %s"
        data.append('%{}%'.format(params["s_spt_nm"]))

    if "s_prjct_ty_code" in params and params['s_prjct_ty_code']:
        query += " AND p.prjct_ty_code=%s"
        data.append(params["s_prjct_ty_code"])


    if "s_bcnc_sn" in params and params['s_bcnc_sn']:
        query += " AND c.bcnc_sn=%s"
        data.append(params["s_bcnc_sn"])

    if "s_dept_code" in params and params['s_dept_code']:
        if params["s_dept_code"] == "TS":
            query += " AND m.dept_code LIKE %s"
            data.append('TS%')
        else:
            query += " AND m.dept_code=%s"
            data.append(params["s_dept_code"])

    if "s_spt_chrg_sn" in params and params['s_spt_chrg_sn']:
        query += " AND c.spt_chrg_sn=%s"
        data.append(params["s_spt_chrg_sn"])


    return dt_query(query, data, params)

def get_finals_summary(params):
    query = """SELECT IFNULL(COUNT(c.cntrct_sn),0) AS total_count
				, IFNULL(COUNT(IF(c.progrs_sttus_code='B', c.cntrct_sn, null)),0) AS count1
				, SUM(IFNULL(f.finals_amt1, 0)) AS amt1
				, SUM(IFNULL(f.finals_amt2, 0)) AS amt2
				, SUM(IFNULL(f.finals_amt3, 0)) AS amt3
				, SUM(IFNULL(f.finals_amt4, 0)) AS amt4
				, IFNULL(COUNT(IF(c.progrs_sttus_code IN ('P', 'S'), c.cntrct_sn, null)),0) AS count2
				, IFNULL(COUNT(IF(c.progrs_sttus_code='C', c.cntrct_sn, null)),0) AS count3
				, SUM(IF(c.progrs_sttus_code='C', IFNULL(f.finals_amt5, 0), 0)) AS amt5
				, SUM(IF(c.progrs_sttus_code='C', IFNULL(f.finals_amt6, 0), 0)) AS amt6
				FROM contract c
				LEFT OUTER JOIN member m
				ON m.mber_sn=c.spt_chrg_sn
				LEFT OUTER JOIN project p
				ON p.cntrct_sn=c.cntrct_sn
				LEFT OUTER JOIN finals f
				ON f.cntrct_sn=c.cntrct_sn
				WHERE 1=1
				AND (c.cntrct_de BETWEEN '{0} 00:00:00'
				AND '{1} 23:59:59')
				AND c.progrs_sttus_code IN ('B', 'P', 'S')
				AND IFNULL(f.finals_done, 'P')='P'
				AND c.prjct_creat_at = 'Y' """.format(params['s_cntrct_de_start'], params['s_cntrct_de_end'])
    data = []



    if "s_spt_nm" in params and params['s_spt_nm']:
        query += " AND c.spt_nm LIKE %s"
        data.append('%{}%'.format(params["s_spt_nm"]))

    if "s_prjct_ty_code" in params and params['s_prjct_ty_code']:
        query += " AND p.prjct_ty_code=%s"
        data.append(params["s_prjct_ty_code"])


    if "s_bcnc_sn" in params and params['s_bcnc_sn']:
        query += " AND c.bcnc_sn=%s"
        data.append(params["s_bcnc_sn"])

    if "s_dept_code" in params and params['s_dept_code']:
        if params["s_dept_code"] == "TS":
            query += " AND m.dept_code LIKE %s"
            data.append('TS%')
        else:
            query += " AND m.dept_code=%s"
            data.append(params["s_dept_code"])

    if "s_spt_chrg_sn" in params and params['s_spt_chrg_sn']:
        query += " AND c.spt_chrg_sn=%s"
        data.append(params["s_spt_chrg_sn"])


    g.curs.execute(query, data)
    result = g.curs.fetchone()
    return result

def insert_finals(params):
    data = OrderedDict()
    for key in params:
        data[key] = params[key]

    for i in range(1, 7):
        key = "finals_amt{}".format(i)
        if key not in data:
            data[key] = None


    data['finals_done'] = 'P'

    sub_query = [key for key in data]
    params_query = ["%({})s".format(key) for key in data]

    query = """INSERT INTO finals({}) VALUES ({})""".format(",".join(sub_query), ",".join(params_query))
    g.curs.execute(query, data)


def update_finals(params):
    finals_sn = params["finals_sn"]

    data = OrderedDict()
    for key in params:
        if key not in ("finals_sn"):
            data[key] = params[key]
    sub_query = ["{0}=%({0})s".format(key) for key in data]
    query = """UPDATE finals SET {} WHERE finals_sn=%(finals_sn)s""".format(",".join(sub_query))
    g.curs.execute(query, params)

def delete_finals(params):
    query = """UPDATE finals SET finals_done='F' WHERE finals_sn=%(finals_sn)s"""
    g.curs.execute(query, params)

def get_contract_no(params):
    query = """SELECT * FROM contract WHERE cntrct_no LIKE %s"""
    data = []
    data.append("{}-{}-%".format(datetime.strptime(params['today'], "%Y-%m-%d").strftime("%y%m%d"), session['member']['dept_nm'].replace("팀", "")))
    row = g.curs.execute(query, data)
    return "{}-{}-{}".format(datetime.strptime(params['today'], "%Y-%m-%d").strftime("%y%m%d"), session['member']['dept_nm'].replace("팀", ""), row)

def insert_project(params):
    g.curs.execute("SHOW COLUMNS FROM contract")
    result = g.curs.fetchall()
    total_columns = []
    required = []
    for r in result:
        key = r['Field'].lower()
        if r['Null'] == 'NO' and r['Default'] is None and r['Extra'] != 'auto_increment':
            required.append(key)
        if r['Extra'] != 'auto_increment':
            total_columns.append(key)

    data = OrderedDict()
    for key, value in params.items():
        if value != '' and key in total_columns:
            data[key] = value
        elif value != '':
            # 다른 테이블에 저장해야할 값
            continue
        elif key in required:
            raise AssertionError(key)

    if "ctmmny_sn" not in data:
        data["ctmmny_sn"] = 1

    if "regist_dtm" not in data:
        if "reg_dtm" not in params:
            data["regist_dtm"] = datetime.now()
        else:
            data["regist_dtm"] = datetime.strptime(params["reg_dtm"], "%Y-%m-%d")
    if "spt_nm" not in data:
        data["spt_nm"] = params['cntrct_nm']

    if "register_id" not in data:
        data["register_id"] = session["member"]["member_id"]

    assert len(set(required) - set(data.keys())) == 0, str(set(required) - set(data.keys()))

    sub_query = [key for key in data]
    params_query = ["%({})s".format(key) for key in data]

    query = """INSERT INTO contract({}) VALUES ({})""".format(",".join(sub_query), ",".join(params_query))
    g.curs.execute(query, data)
    cntrct_sn = g.curs.lastrowid
    if data["prjct_creat_at"] == 'Y':
        g.curs.execute("SHOW COLUMNS FROM project")
        result = g.curs.fetchall()
        total_columns = []
        required = []
        for r in result:
            key = r['Field'].lower()
            if r['Null'] == 'NO' and r['Default'] is None and r['Extra'] != 'auto_increment':
                required.append(key)
            if r['Extra'] != 'auto_increment':
                total_columns.append(key)

        data = OrderedDict()
        for key, value in params.items():
            if value != '' and key in total_columns:
                data[key] = value
            elif value != '':
                # 다른 테이블에 저장해야할 값
                continue
            elif key in required:
                raise AssertionError(key)

        if "ctmmny_sn" not in data:
            data["ctmmny_sn"] = 1

        if "register_id" not in data:
            data["register_id"] = session["member"]["member_id"]

        if "regist_dtm" not in data:
            if "reg_dtm" not in params:
                data["regist_dtm"] = datetime.now()
            else:
                data["regist_dtm"] = datetime.strptime(params["reg_dtm"], "%Y-%m-%d")

        if "cntrct_sn" not in data:
            data["cntrct_sn"] = cntrct_sn


        assert len(set(required) - set(data.keys())) == 0, str(set(required) - set(data.keys()))

        sub_query = [key for key in data]
        params_query = ["%({})s".format(key) for key in data]

        query = """INSERT INTO project({}) VALUES ({})""".format(",".join(sub_query), ",".join(params_query))
        g.curs.execute(query, data)
        prjct_sn = g.curs.lastrowid

        query = """INSERT INTO charger(cntrct_sn, prjct_sn, charger_se_code, charger_nm, charger_moblphon, charger_telno, regist_dtm, register_id) VALUES (%s, %s, %s, %s, %s, '', NOW(), %s)"""
        g.curs.execute(query, (cntrct_sn, prjct_sn, 1, params["charger_nm1"], params["charger_moblphon1"], session["member"]["member_id"]))
        g.curs.execute(query, (cntrct_sn, prjct_sn, 2, params["charger_nm2"], params["charger_moblphon2"], session["member"]["member_id"]))
        if params['prjct_ty_code'] in ('BD', 'BF'):
            g.curs.execute(query, (cntrct_sn, prjct_sn, 6, params["charger_nm6"], params["charger_moblphon6"], session["member"]["member_id"]))

def get_b_projects(params):
    query = """SELECT cntrct_sn
                    , cntrct_no
                    , spt_nm
                    , CONCAT(cntrwk_bgnde,' ~ ',cntrwk_endde) AS cntrwk_period
                    , home_count
                    , home_region
                    , mh_count
                    , mh_place
                    , mh_period
                    , mh_approval_step
                FROM contract 
                WHERE progrs_sttus_code='B'
                AND prjct_creat_at='Y'
                """

    g.curs.execute(query)
    result = g.curs.fetchall()
    return result
def get_p_projects(params):
    query = """SELECT cntrct_sn
                    , cntrct_no
                    , spt_nm
                    , CONCAT(cntrwk_bgnde,' ~ ',cntrwk_endde) AS cntrwk_period
                    , home_count
                    , home_region
                    , mh_count
                    , mh_place
                    , mh_period
                    , mh_approval_step
                FROM contract 
                WHERE progrs_sttus_code='P'
                AND prjct_creat_at='Y'
                """

    g.curs.execute(query)
    result = g.curs.fetchall()
    return result
def get_all_projects(params):
    query = """SELECT cntrct_sn
                    , cntrct_no
                    , spt_nm
                    , CONCAT(cntrwk_bgnde,' ~ ',cntrwk_endde) AS cntrwk_period
                    , home_count
                    , home_region
                    , mh_count
                    , mh_place
                    , mh_period
                    , mh_approval_step
                FROM contract 
                WHERE progrs_sttus_code IN ('P', 'B')
                AND prjct_creat_at='Y'
                """

    g.curs.execute(query)
    result = g.curs.fetchall()
    return result

def get_project_by_cntrct_nm(cntrct_sn):
    g.curs.execute("SELECT prjct_sn FROM project WHERE cntrct_sn=%s", (cntrct_sn, ))
    prjct = g.curs.fetchone()
    return prjct


def insert_BF_c_project(params):
    prjct = get_project_by_cntrct_nm(params["cntrct_sn"])
    params['prjct_sn'] = prjct['prjct_sn']
    params['regist_dtm'] = datetime.now()
    params['register_id'] = session['member']['member_id']

    query = """INSERT INTO cost(cntrct_sn, prjct_sn, cntrct_execut_code, ct_se_code, model_no, qy, puchas_amount, cost_date, extra_sn, regist_dtm, register_id)
                VALUES (%(cntrct_sn)s, %(prjct_sn)s, 'E', '10', '기타비용', 1, %(b10)s, '0000-00-00', 0, %(regist_dtm)s, %(register_id)s)"""
    params['b10'] = int(params['E_10'].replace(",", ""))
    g.curs.execute(query, params)

    query = """INSERT INTO cost(cntrct_sn, prjct_sn, cntrct_execut_code, ct_se_code, model_no, qy, puchas_amount, cost_date, extra_sn, regist_dtm, register_id)
                VALUES (%(cntrct_sn)s, %(prjct_sn)s, 'E', '7', '옵션행사비', 1, %(b7)s, '0000-00-00', 0, %(regist_dtm)s, %(register_id)s)"""
    params['b7'] = int(params['E_7'].replace(",", ""))
    g.curs.execute(query, params)

    g.curs.execute("UPDATE contract SET PROGRS_STTUS_CODE='P', cntrct_de=%(cost_date)s WHERE cntrct_sn=%(cntrct_sn)s", params)
def update_BF_c_project(params):
    prjct = get_project_by_cntrct_nm(params["cntrct_sn"])
    params['prjct_sn'] = prjct['prjct_sn']
    params['regist_dtm'] = datetime.now()
    params['register_id'] = session['member']['member_id']
    g.curs.execute("SELECT IFNULL(max(extra_sn), 0) as m_extra_sn FROM cost WHERE cntrct_execut_code = 'E' and cntrct_sn=%s", params['cntrct_sn'])
    extra_sn = g.curs.fetchone()['m_extra_sn'] + 1
    params["extra_sn"] = extra_sn
    query = """INSERT INTO cost(cntrct_sn, prjct_sn, cntrct_execut_code, ct_se_code, model_no, qy, puchas_amount, cost_date, extra_sn, regist_dtm, register_id)
                VALUES (%(cntrct_sn)s, %(prjct_sn)s, 'E', '10', '기타비용', 1, %(b10)s, '0000-00-00', %(extra_sn)s, %(regist_dtm)s, %(register_id)s)"""
    params['b10'] = int(params['Z_10'].replace(",", "")) - int(params['E_10'].replace(",", ""))
    g.curs.execute(query, params)

    query = """INSERT INTO cost(cntrct_sn, prjct_sn, cntrct_execut_code, ct_se_code, model_no, qy, puchas_amount, cost_date, extra_sn, regist_dtm, register_id)
                VALUES (%(cntrct_sn)s, %(prjct_sn)s, 'E', '7', '옵션행사비', 1, %(b7)s, '0000-00-00', %(extra_sn)s, %(regist_dtm)s, %(register_id)s)"""
    params['b7'] = int(params['Z_7'].replace(",", "")) - int(params['E_7'].replace(",", ""))
    g.curs.execute(query, params)

    g.curs.execute("UPDATE contract SET PROGRS_STTUS_CODE='P', cntrct_de=%(cost_date)s WHERE cntrct_sn=%(cntrct_sn)s", params)


def insert_c_project(params):
    cost_data = []
    prjct = get_project_by_cntrct_nm(params["cntrct_sn"])
    for key in params:
        if key.endswith("[]"):
            continue
        elif key.startswith("C_"):
            cntrct_execut_code, ct_se_code  = key.split("_")
            value = params[key].replace(",", "")
            if value == '':
                continue
            column = "puchas_amount" if cntrct_execut_code == 'E' else "salamt"
            cost_data.append({"cntrct_sn" : params["cntrct_sn"], "prjct_sn" : prjct["prjct_sn"], "cntrct_execut_code" : cntrct_execut_code, "ct_se_code" : ct_se_code, "qy" : 1, column : int(value), "extra_sn" : 0, "regist_dtm" : datetime.now(), "register_id" : session["member"]["member_id"]})
            # 간접비 실행
            if ct_se_code == '8':
                cntrct_execut_code = 'E'
                column = "puchas_amount" if cntrct_execut_code == 'E' else "salamt"
                cost_data.append({"cntrct_sn": params["cntrct_sn"], "prjct_sn": prjct["prjct_sn"],
                                  "cntrct_execut_code": cntrct_execut_code, "ct_se_code": ct_se_code, "qy": 1,
                                  column: int(value), "extra_sn": 0, "regist_dtm": datetime.now(),
                                  "register_id": session["member"]["member_id"]})

    # M,S/H 와 옵션행사비 사전입찰 내역
    g.curs.execute("SELECT * FROM cost WHERE cntrct_execut_code='D' AND ct_se_code IN ('7', '61') AND cntrct_sn=%s AND prjct_sn=%s", (params['cntrct_sn'], prjct['prjct_sn']))
    costs = g.curs.fetchall(transform=False)
    g.curs.execute("SHOW COLUMNS FROM cost")
    result = g.curs.fetchall()
    no_required = []
    for r in result:
        key = r['Field'].lower()
        if r['Extra'] == 'auto_increment':
            no_required.append(key)

    for cost in costs:
        raw_data = {}
        for key in cost:
            if key.lower() not in no_required:
                raw_data[key.lower()] = cost[key]
        raw_data['cntrct_execut_code'] = 'E'
        cost_data.append(raw_data)

    # 기타 실행
    total = 0
    for data in cost_data:
        if data['cntrct_execut_code'] == 'C':
            total += data["salamt"]
    cost_data.append({"cntrct_sn": params["cntrct_sn"], "prjct_sn": prjct["prjct_sn"],
                                  "cntrct_execut_code": 'E', "ct_se_code": '10', "qy": 1,
                                  "puchas_amount": int(total*0.005), "extra_sn": 0, "regist_dtm": datetime.now(),
                                  "register_id": session["member"]["member_id"]})


    for data in cost_data:
        sub_query = [key for key in data]
        params_query = ["%({})s".format(key) for key in data]

        query = """INSERT INTO cost({}) VALUES ({})""".format(",".join(sub_query), ",".join(params_query))
        g.curs.execute(query, data)

    params["cost_date"] = datetime.now().strftime("%Y-%m-%d")
    g.curs.execute("UPDATE contract SET PROGRS_STTUS_CODE='P', cntrct_de=%(cost_date)s WHERE cntrct_sn=%(cntrct_sn)s", params)
def insert_c_extra_project(params):
    cost_data = []
    g.curs.execute("SELECT IFNULL(max(extra_sn), 0) as m_extra_sn FROM cost WHERE cntrct_execut_code IN ('C', 'E') and cntrct_sn=%s", params['cntrct_sn'])
    extra_sn = g.curs.fetchone()['m_extra_sn'] + 1
    prjct = get_project_by_cntrct_nm(params["cntrct_sn"])
    for key in params:
        if key.endswith("[]"):
            continue
        elif (key.startswith("C_") or key.startswith("E_")) and key.endswith("_alpha"):
            cntrct_execut_code, ct_se_code, _  = key.split("_")
            value = params[key].replace(",", "")
            if value == '':
                continue
            column = "puchas_amount" if cntrct_execut_code == 'E' else "salamt"
            cost_data.append({"cntrct_sn" : params["cntrct_sn"], "prjct_sn" : prjct["prjct_sn"], "cntrct_execut_code" : cntrct_execut_code, "ct_se_code" : ct_se_code, "qy" : 1, column : int(value), "extra_sn" : extra_sn, "regist_dtm" : datetime.now(), "register_id" : session["member"]["member_id"]})

    for data in cost_data:
        sub_query = [key for key in data]
        params_query = ["%({})s".format(key) for key in data]

        query = """INSERT INTO cost({}) VALUES ({})""".format(",".join(sub_query), ",".join(params_query))
        g.curs.execute(query, data)

def delete_option_bf_project(params):
    prjct = get_project_by_cntrct_nm(params["cntrct_sn"])
    params['prjct_sn'] = prjct['prjct_sn']
    g.curs.execute("DELETE FROM cost WHERE cntrct_sn=%(cntrct_sn)s AND prjct_sn=%(prjct_sn)s AND cntrct_execut_code='C' AND ct_se_code='9' AND purchsofc_sn='2'", params)

def delete_option_bd_project(params):
    prjct = get_project_by_cntrct_nm(params["cntrct_sn"])
    params['prjct_sn'] = prjct['prjct_sn']
    g.curs.execute("DELETE FROM cost WHERE cntrct_sn=%(cntrct_sn)s AND prjct_sn=%(prjct_sn)s AND cntrct_execut_code='C' AND ct_se_code='1' AND purchsofc_sn='2'", params)
def insert_b_option_bf_project(params):
    prjct = get_project_by_cntrct_nm(params["cntrct_sn"])
    params['prjct_sn'] = prjct['prjct_sn']
    params['regist_dtm'] = datetime.now()
    params['register_id'] = session['member']['member_id']
    if "Z_10" in params:
        g.curs.execute(
            "SELECT IFNULL(max(extra_sn), 0) as m_extra_sn FROM cost WHERE cntrct_execut_code = 'C' and cntrct_sn=%s",params['cntrct_sn'])
        extra_sn = g.curs.fetchone()['m_extra_sn'] + 1
        params["extra_sn"] = extra_sn
    else:
        params["extra_sn"] = 0

    for model_no, qy, puchas_amount, dscnt_rt, fee_rt, amount in zip(params['model_no[]'], params['qy[]'], params['puchas_amount[]'], params['dc_rate[]'], params['rate[]'], params['amount[]']):
        if model_no == '' and qy == '' and puchas_amount == '' and dscnt_rt == '' and fee_rt == '':
            continue
        qy = int(qy.replace(",", ""))
        amount = int(amount.replace(",", ""))
        puchas_amount = int(puchas_amount.replace(",", ""))
        dscnt_rt = (100.0 - (amount / puchas_amount)*100.0)
        fee_rt = float(fee_rt.replace("%", ""))
        pParams = {key : value for key, value in params.items() if not key.endswith("[]")}
        pParams["qy"] = qy
        pParams["puchas_amount"] = puchas_amount
        pParams["dscnt_rt"] = dscnt_rt
        pParams["fee_rt"] = fee_rt
        pParams['model_no'] = model_no
        if "cost_date" in params:
            pParams["cost_date"] = params["cost_date"]
            query = """INSERT INTO cost(cntrct_sn, prjct_sn, cntrct_execut_code, ct_se_code, purchsofc_sn, model_no, qy, puchas_amount, dscnt_rt, fee_rt, cost_date, extra_sn, regist_dtm, register_id)
                        VALUES (%(cntrct_sn)s, %(prjct_sn)s, 'C', '9', '2', %(model_no)s, %(qy)s, %(puchas_amount)s, %(dscnt_rt)s, %(fee_rt)s, %(cost_date)s, %(extra_sn)s, %(regist_dtm)s, %(register_id)s)"""
        else:
            query = """INSERT INTO cost(cntrct_sn, prjct_sn, cntrct_execut_code, ct_se_code, purchsofc_sn, model_no, qy, puchas_amount, dscnt_rt, fee_rt, cost_date, extra_sn, regist_dtm, register_id)
                        VALUES (%(cntrct_sn)s, %(prjct_sn)s, 'C', '9', '2', %(model_no)s, %(qy)s, %(puchas_amount)s, %(dscnt_rt)s, %(fee_rt)s, '0000-00-00', %(extra_sn)s, %(regist_dtm)s, %(register_id)s)"""
        g.curs.execute(query, pParams)

def insert_bd_expect_equipment(params):
    for model_no, qy, puchas_amount, dlamt, salamt, dlivy_amt in zip(params['model_no[]'], params['qy[]'], params['dlivy_amt[]'], params['dlamt[]'], params['cntrct_dlamt[]'], params['dlivy_amt[]']):
        if model_no == '' and qy == '' and puchas_amount == '' and dscnt_rt == '':
            continue
        qy = int(qy.replace(",", ""))
        puchas_amount = int(puchas_amount.replace(",", ""))
        dlamt = int(dlamt.replace(",", ""))
        dscnt_rt = float((1.0-(dlamt/puchas_amount))*100.0)
        salamt = int(salamt.replace(",", ""))
        dlivy_amt = int(dlivy_amt.replace(",", ""))
        query = """INSERT INTO expect_equipment(cntrct_sn, model_no, prdlst_se_code, bcnc_sn, delng_ty_code, cnt_dlnt, dlamt, samt, rm, dlivy_amt)
                    VALUES (%(cntrct_sn)s, %(model_no)s, '9', 74, 1, %(qy)s, %(dlamt)s, %(salamt)s, '', %(dlivy_amt)s)"""
        pParams = {key : value for key, value in params.items() if not key.endswith("[]")}
        pParams["qy"] = qy
        pParams["dlamt"] = dlamt
        pParams["salamt"] = salamt
        pParams['model_no'] = model_no
        pParams["dlivy_amt"] = dlivy_amt
        g.curs.execute(query, pParams)

def insert_b_option_bd_project(params):
    prjct = get_project_by_cntrct_nm(params["cntrct_sn"])
    params['prjct_sn'] = prjct['prjct_sn']
    params['regist_dtm'] = datetime.now()
    params['register_id'] = session['member']['member_id']
    if "Z_10" in params:
        g.curs.execute(
            "SELECT IFNULL(max(extra_sn), 0) as m_extra_sn FROM cost WHERE cntrct_execut_code = 'C' and cntrct_sn=%s",params['cntrct_sn'])
        extra_sn = g.curs.fetchone()['m_extra_sn'] + 1
        params["extra_sn"] = extra_sn
    else:
        params["extra_sn"] = 0

    for model_no, qy, puchas_amount, dlamt, salamt in zip(params['model_no[]'], params['qy[]'], params['dlivy_amt[]'], params['dlamt[]'], params['cntrct_dlamt[]']):
        if model_no == '' and qy == '' and puchas_amount == '' and dscnt_rt == '':
            continue
        qy = int(qy.replace(",", ""))
        puchas_amount = int(puchas_amount.replace(",", ""))
        dlamt = int(dlamt.replace(",", ""))
        dscnt_rt = float((1.0-(dlamt/puchas_amount))*100.0)
        salamt = int(salamt.replace(",", ""))
        pParams = {key : value for key, value in params.items() if not key.endswith("[]")}
        pParams["qy"] = qy
        pParams["puchas_amount"] = puchas_amount
        pParams["dscnt_rt"] = dscnt_rt
        pParams["salamt"] = salamt
        pParams['model_no'] = model_no
        if "cost_date" in params:
            pParams["cost_date"] = params["cost_date"]
            query = """INSERT INTO cost(cntrct_sn, prjct_sn, cntrct_execut_code, ct_se_code, purchsofc_sn, model_no, qy, puchas_amount, salamt, dscnt_rt, cost_date, extra_sn, regist_dtm, register_id)
                        VALUES (%(cntrct_sn)s, %(prjct_sn)s, 'C', '1', '2', %(model_no)s, %(qy)s, %(puchas_amount)s, %(salamt)s, %(dscnt_rt)s, %(cost_date)s, %(extra_sn)s, %(regist_dtm)s, %(register_id)s)"""
        else:
            query = """INSERT INTO cost(cntrct_sn, prjct_sn, cntrct_execut_code, ct_se_code, purchsofc_sn, model_no, qy, puchas_amount, salamt, dscnt_rt, cost_date, extra_sn, regist_dtm, register_id)
                        VALUES (%(cntrct_sn)s, %(prjct_sn)s, 'C', '1', '2', %(model_no)s, %(qy)s, %(puchas_amount)s, %(salamt)s, %(dscnt_rt)s, '0000-00-00', %(extra_sn)s, %(regist_dtm)s, %(register_id)s)"""
        g.curs.execute(query, pParams)


def insert_b_bd_project(params):
    prjct = get_project_by_cntrct_nm(params["cntrct_sn"])
    params['prjct_sn'] = prjct['prjct_sn']
    params['regist_dtm'] = datetime.now()
    params['register_id'] = session['member']['member_id']
    for model_no, qy, puchas_amount, dlamt, salamt in zip(params['model_no[]'], params['qy[]'], params['dlivy_amt[]'], params['dlamt[]'], params['cntrct_dlamt[]']):
        if model_no == '' and qy == '' and puchas_amount == '' and dscnt_rt == '':
            continue
        qy = int(qy.replace(",", ""))
        puchas_amount = int(puchas_amount.replace(",", ""))
        dlamt = int(dlamt.replace(",", ""))
        dscnt_rt = float((1.0-(dlamt/puchas_amount))*100.0)
        salamt = int(salamt.replace(",", ""))
        query = """INSERT INTO cost(cntrct_sn, prjct_sn, cntrct_execut_code, ct_se_code, purchsofc_sn, model_no, qy, puchas_amount, salamt, dscnt_rt, cost_date, extra_sn, regist_dtm, register_id)
                    VALUES (%(cntrct_sn)s, %(prjct_sn)s, 'B', '1', '2', %(model_no)s, %(qy)s, %(puchas_amount)s, %(salamt)s, %(dscnt_rt)s, '0000-00-00', 0, %(regist_dtm)s, %(register_id)s)"""
        pParams = {key : value for key, value in params.items() if not key.endswith("[]")}
        pParams["qy"] = qy
        pParams["puchas_amount"] = puchas_amount
        pParams["dscnt_rt"] = dscnt_rt
        pParams["salamt"] = salamt
        pParams['model_no'] = model_no
        g.curs.execute(query, pParams)
    query = """INSERT INTO cost(cntrct_sn, prjct_sn, cntrct_execut_code, ct_se_code, purchsofc_sn, model_no, qy, puchas_amount, dscnt_rt, add_dscnt_rt, cost_date, extra_sn, regist_dtm, register_id, dspy_se_code)
                VALUES (%(cntrct_sn)s, %(prjct_sn)s, 'D', '61', '74', '(예상)', 1, %(b61)s, 0.0, %(b61rate)s ,'0000-00-00', 0, %(regist_dtm)s, %(register_id)s, 1)"""
    params['b61'] = int(params['D_61'].replace(",", ""))
    params['b61rate'] = (int(params['D_61_DC'].replace(",", ""))*100/int(params['D_61'].replace(",", ""))) if int(params['D_61'].replace(",", "")) != 0 else 0.0
    g.curs.execute(query, params)

    query = """INSERT INTO cost(cntrct_sn, prjct_sn, cntrct_execut_code, ct_se_code, model_no, qy, salamt, cost_date, extra_sn, regist_dtm, register_id)
                VALUES (%(cntrct_sn)s, %(prjct_sn)s, 'G', '63', '판매금액', 1, %(b63)s, '0000-00-00', 0, %(regist_dtm)s, %(register_id)s)"""
    params['b63'] = int(params['D_63'].replace(",", ""))
    g.curs.execute(query, params)

    query = """INSERT INTO cost(cntrct_sn, prjct_sn, cntrct_execut_code, ct_se_code, model_no, qy, puchas_amount, cost_date, extra_sn, regist_dtm, register_id)
                VALUES (%(cntrct_sn)s, %(prjct_sn)s, 'D', '10', '기타비용', 1, %(b10)s, '0000-00-00', 0, %(regist_dtm)s, %(register_id)s)"""
    params['b10'] = int(params['D_10'].replace(",", ""))
    g.curs.execute(query, params)

    query = """INSERT INTO cost(cntrct_sn, prjct_sn, cntrct_execut_code, ct_se_code, model_no, qy, puchas_amount, cost_date, extra_sn, regist_dtm, register_id)
                VALUES (%(cntrct_sn)s, %(prjct_sn)s, 'D', '7', '옵션행사비', 1, %(b7)s, '0000-00-00', 0, %(regist_dtm)s, %(register_id)s)"""
    params['b7'] = int(params['D_7'].replace(",", ""))
    g.curs.execute(query, params)
def insert_b_bf_project(params):
    prjct = get_project_by_cntrct_nm(params["cntrct_sn"])
    params['prjct_sn'] = prjct['prjct_sn']
    params['regist_dtm'] = datetime.now()
    params['register_id'] = session['member']['member_id']
    for model_no, qy, puchas_amount, dscnt_rt, fee_rt, amount in zip(params['model_no[]'], params['qy[]'], params['puchas_amount[]'], params['dc_rate[]'], params['rate[]'], params['amount[]']):
        if model_no == '' and qy == '' and puchas_amount == '' and dscnt_rt == '' and fee_rt == '':
            continue
        qy = int(qy.replace(",", ""))
        amount = int(amount.replace(",", ""))
        puchas_amount = int(puchas_amount.replace(",", ""))
        dscnt_rt = (100.0 - (amount / puchas_amount)*100.0)
        fee_rt = float(fee_rt.replace("%", ""))
        query = """INSERT INTO cost(cntrct_sn, prjct_sn, cntrct_execut_code, ct_se_code, purchsofc_sn, model_no, qy, puchas_amount, dscnt_rt, fee_rt, cost_date, extra_sn, regist_dtm, register_id)
                    VALUES (%(cntrct_sn)s, %(prjct_sn)s, 'B', '9', '2', %(model_no)s, %(qy)s, %(puchas_amount)s, %(dscnt_rt)s, %(fee_rt)s, '0000-00-00', 0, %(regist_dtm)s, %(register_id)s)"""
        pParams = {key : value for key, value in params.items() if not key.endswith("[]")}
        pParams["qy"] = qy
        pParams["puchas_amount"] = puchas_amount
        pParams["dscnt_rt"] = dscnt_rt
        pParams["fee_rt"] = fee_rt
        pParams['model_no'] = model_no
        g.curs.execute(query, pParams)
    query = """INSERT INTO cost(cntrct_sn, prjct_sn, cntrct_execut_code, ct_se_code, purchsofc_sn, model_no, qy, puchas_amount, dscnt_rt, add_dscnt_rt, cost_date, extra_sn, regist_dtm, register_id, dspy_se_code)
                VALUES (%(cntrct_sn)s, %(prjct_sn)s, 'D', '61', '74', '(예상)', 1, %(b61)s, 0.0, %(b61rate)s ,'0000-00-00', 0, %(regist_dtm)s, %(register_id)s, 1)"""
    params['b61'] = int(params['D_61'].replace(",", ""))
    params['b61rate'] = (int(params['D_61_DC'].replace(",", ""))*100/int(params['D_61'].replace(",", ""))) if int(params['D_61'].replace(",", "")) != 0 else 0.0
    g.curs.execute(query, params)

    query = """INSERT INTO cost(cntrct_sn, prjct_sn, cntrct_execut_code, ct_se_code, model_no, qy, salamt, cost_date, extra_sn, regist_dtm, register_id)
                VALUES (%(cntrct_sn)s, %(prjct_sn)s, 'G', '63', '판매금액', 1, %(b63)s, '0000-00-00', 0, %(regist_dtm)s, %(register_id)s)"""
    params['b63'] = int(params['D_63'].replace(",", ""))
    g.curs.execute(query, params)

    query = """INSERT INTO cost(cntrct_sn, prjct_sn, cntrct_execut_code, ct_se_code, model_no, qy, puchas_amount, cost_date, extra_sn, regist_dtm, register_id)
                VALUES (%(cntrct_sn)s, %(prjct_sn)s, 'D', '10', '기타비용', 1, %(b10)s, '0000-00-00', 0, %(regist_dtm)s, %(register_id)s)"""
    params['b10'] = int(params['D_10'].replace(",", ""))
    g.curs.execute(query, params)

    query = """INSERT INTO cost(cntrct_sn, prjct_sn, cntrct_execut_code, ct_se_code, model_no, qy, puchas_amount, cost_date, extra_sn, regist_dtm, register_id)
                VALUES (%(cntrct_sn)s, %(prjct_sn)s, 'D', '7', '옵션행사비', 1, %(b7)s, '0000-00-00', 0, %(regist_dtm)s, %(register_id)s)"""
    params['b7'] = int(params['D_7'].replace(",", ""))
    g.curs.execute(query, params)




def insert_b_project(params):
    n_params = {}
    cost_data = []
    prjct = get_project_by_cntrct_nm(params["cntrct_sn"])
    for key in params:
        if key.endswith("[]"):
            if key == "construct_name[]":
                n_params[key.replace("[]", "")] = params[key]
            else:
                n_params[key.replace("[]", "")] = [int(d.replace(",", "")) for d in params[key]]
        elif key.startswith("B_") or key.startswith("D_"):
            cntrct_execut_code, ct_se_code  = key.split("_")
            value = params[key].replace(",", "")
            if value == '':
                continue
            column = "puchas_amount" if cntrct_execut_code == 'D' else "salamt"
            cost_data.append({"cntrct_sn" : params["cntrct_sn"], "prjct_sn" : prjct["prjct_sn"], "cntrct_execut_code" : cntrct_execut_code, "ct_se_code" : ct_se_code, "qy" : 1, column : int(value), "extra_sn" : 0, "regist_dtm" : datetime.now(), "register_id" : session["member"]["member_id"]})

    construct_data = []
    for n, c, a, t in zip(n_params["construct_name"], n_params["construct_count"], n_params["construct_amt"], n_params["construct_tax"]):
        construct_data.append({"cntrct_sn" : params["cntrct_sn"], "construct_name" : n, "construct_count" : c, "construct_amt" : a, "construct_tax" : t})

    if construct_data:
        sub_query = [key for key in construct_data[0]]
        params_query = ["%({})s".format(key) for key in construct_data[0]]

        query = """INSERT INTO construct({}) VALUES ({})""".format(",".join(sub_query), ",".join(params_query))
        g.curs.executemany(query, construct_data)

    for data in cost_data:
        sub_query = [key for key in data]
        params_query = ["%({})s".format(key) for key in data]

        query = """INSERT INTO cost({}) VALUES ({})""".format(",".join(sub_query), ",".join(params_query))
        g.curs.execute(query, data)



def insert_option_cost(params):
    prefix = "e_" if params['opt_approval_type'] == 'S' else "c_"
    opt_type = "E" if params["opt_approval_type"] == "S" else "C"

    params["{}opt_period".format(prefix)] = params["{}opt_period_start".format(prefix)] + " ~ " + params["{}opt_period_end".format(prefix)]
    del params["{}opt_period_start".format(prefix)]
    del params["{}opt_period_end".format(prefix)]
    data = OrderedDict()
    g.curs.execute("SHOW COLUMNS FROM dspy_option")
    result = g.curs.fetchall()
    total_columns = []
    required = []
    for r in result:
        key = r['Field'].lower()
        if r['Null'] == 'NO' and r['Default'] is None and r['Extra'] != 'auto_increment':
            required.append(key)
        if r['Extra'] != 'auto_increment':
            total_columns.append(key)

    for key in params:
        if key.startswith(prefix):
            data[key.replace(prefix, "")] = params[key]
        elif key in required:
            data[key] = params[key]
        elif key in total_columns and params[key]:
            data[key] = params[key]

    data["opt_type"] = opt_type

    for key in data:
        if key in ("opt_amount", "opt_helper"):
            data[key] = data[key].replace(",", "")
            if data[key] == '':
                data[key] = 0
            else:
                data[key] = int(data[key])
        elif key in ('opt_dtm', 'opt_pay_dtm'):
            if data[key] == '':
                data[key] = None

    row = g.curs.execute("SELECT opt_sn FROM dspy_option WHERE cntrct_sn=%s AND opt_type=%s", (params["cntrct_sn"], opt_type))
    if row:
        opt_sn = g.curs.fetchone()['opt_sn']
        sub_query = ["{0}=%({0})s".format(key) for key in data]
        query = """UPDATE dspy_option SET {} WHERE opt_sn=%(opt_sn)s""".format(",".join(sub_query))
        data["opt_sn"] = opt_sn
        g.curs.execute(query, data)

    else:
        sub_query = [key for key in data]
        params_query = ["%({})s".format(key) for key in data]

        query = """INSERT INTO dspy_option({}) VALUES ({})""".format(",".join(sub_query), ",".join(params_query))
        g.curs.execute(query, data)


def get_option_cost_list(params):
    query = """SELECT c.opt_period AS c_opt_period
                    , substring_index(c.opt_period, ' ~ ',1)  AS c_opt_period_start
                    , substring_index(c.opt_period, ' ~ ',-1)  AS c_opt_period_end
                    , c.opt_dtm AS c_opt_dtm
                    , c.opt_helper AS c_opt_helper
                    , c.opt_rate AS c_opt_rate
                    , c.opt_amount AS c_opt_amount
                    , c.opt_pay_dtm AS c_opt_pay_dtm
                    , c.opt_rm AS c_opt_rm
                    , e.opt_period AS e_opt_period
                    , substring_index(e.opt_period, ' ~ ',1)  AS e_opt_period_start
                    , substring_index(e.opt_period, ' ~ ',-1)  AS e_opt_period_end
                    , e.opt_dtm AS e_opt_dtm
                    , e.opt_helper AS e_opt_helper
                    , e.opt_rate AS e_opt_rate
                    , e.opt_amount AS e_opt_amount
                    , e.opt_pay_dtm AS e_opt_pay_dtm
                    , e.opt_rm AS e_opt_rm
                FROM (SELECT * FROM dspy_option WHERE opt_type='C') c 
                LEFT OUTER JOIN (SELECT * FROM dspy_option WHERE opt_type='E') e
                ON c.cntrct_sn=e.cntrct_sn
                WHERE 1=1
                AND c.cntrct_sn=%(s_cntrct_sn)s
                 
                 UNION
                SELECT c.opt_period AS c_opt_period
                    , substring_index(c.opt_period, ' ~ ',1)  AS c_opt_period_start
                    , substring_index(c.opt_period, ' ~ ',-1)  AS c_opt_period_end
                    , c.opt_dtm AS c_opt_dtm
                    , c.opt_helper AS c_opt_helper
                    , c.opt_rate AS c_opt_rate
                    , c.opt_amount AS c_opt_amount
                    , c.opt_pay_dtm AS c_opt_pay_dtm
                    , c.opt_rm AS c_opt_rm
                    , e.opt_period AS e_opt_period
                    , substring_index(e.opt_period, ' ~ ',1)  AS e_opt_period_start
                    , substring_index(e.opt_period, ' ~ ',-1)  AS e_opt_period_end
                    , e.opt_dtm AS e_opt_dtm
                    , e.opt_helper AS e_opt_helper
                    , e.opt_rate AS e_opt_rate
                    , e.opt_amount AS e_opt_amount
                    , e.opt_pay_dtm AS e_opt_pay_dtm
                    , e.opt_rm AS e_opt_rm
                FROM (SELECT * FROM dspy_option WHERE opt_type='C') c 
                RIGHT OUTER JOIN (SELECT * FROM dspy_option WHERE opt_type='E') e
                ON c.cntrct_sn=e.cntrct_sn
                WHERE 1=1
                AND e.cntrct_sn=%(s_cntrct_sn)s
                 """
    g.curs.execute(query, params)
    result = g.curs.fetchone()
    return result

def get_expect_equip_list(params):
    query = """SELECT e.equip_sn
                    , e.model_no
                    , e.prdlst_se_code
                    , e.bcnc_sn
                    , e.delng_ty_code
                    , e.cnt_dlnt
                    , e.dlamt
                    , e.samt AS samount
                    , e.rm
                    , e.dlivy_amt
                    , IF(q.dlivy_de='0000-00-00', '', IFNULL(q.dlivy_de, '')) AS dlivy_de
                    , IFNULL(q.dlnt, 0) AS sdlnt
                FROM expect_equipment e
                LEFT OUTER JOIN (SELECT cnnc_sn, MAX(IFNULL(dlivy_de, '0000-00-00')) as dlivy_de, SUM(dlnt) as dlnt FROM equipment WHERE cnnc_sn IS NOT NULL GROUP BY cnnc_sn) q
                ON e.equip_sn=q.cnnc_sn
                WHERE 1=1
                AND e.delng_ty_code='1'
                AND cntrct_sn = %(s_cntrct_sn)s"""
    g.curs.execute(query, params)
    result = g.curs.fetchall()
    return result

def get_expect_equip_other_list(params):
    query = """SELECT e.equip_sn
                    , e.model_no
                    , e.prdlst_se_code
                    , e.bcnc_sn
                    , e.delng_ty_code
                    , e.cnt_dlnt
                    , e.dlamt
                    , e.samt AS samount
                    , e.rm
                    , IF(q.dlivy_de='0000-00-00', '', IFNULL(q.dlivy_de, '')) AS dlivy_de
                    , IFNULL(q.dlnt, 0) AS sdlnt
                FROM expect_equipment e
                LEFT OUTER JOIN (SELECT cnnc_sn, MAX(IFNULL(dlivy_de, '0000-00-00')) as dlivy_de, SUM(dlnt) as dlnt FROM equipment WHERE cnnc_sn IS NOT NULL GROUP BY cnnc_sn) q
                ON e.equip_sn=q.cnnc_sn
                WHERE 1=1
                AND e.delng_ty_code='2'
                AND cntrct_sn = %(s_cntrct_sn)s"""
    g.curs.execute(query, params)
    result = g.curs.fetchall()
    return result

def update_c_project(params):
    cntrct_sn1 = params['cntrct_sn_1']
    cntrct_sn2 = params['cntrct_sn_2']
    prjct_1 = get_project_by_cntrct_nm(cntrct_sn1)
    prjct_2 = get_project_by_cntrct_nm(cntrct_sn2)
    column = {"E" : "puchas_amount", "C" : "salamt"}
    cost_data = []
    c_99_1 = int(params['C_99_1'].replace(",", "")) if params['C_99_1'].replace(",", "") != '' else 0
    c_99_2 = int(params['C_99_2'].replace(",", "")) if params['C_99_2'].replace(",", "") != '' else 0
    e_99_1 = int(params['E_99_1'].replace(",", "")) if params['E_99_1'].replace(",", "") != '' else 0
    e_99_2 = int(params['E_99_2'].replace(",", "")) if params['E_99_2'].replace(",", "") != '' else 0
    cost_data.append(
        {"cntrct_sn": cntrct_sn1, "prjct_sn": prjct_1["prjct_sn"], "cntrct_execut_code": 'C',
         "ct_se_code": '99', "qy": 1, column['C']: c_99_1, "extra_sn": 0, "regist_dtm": datetime.now(),
         "register_id": session["member"]["member_id"]})
    cost_data.append(
        {"cntrct_sn": cntrct_sn1, "prjct_sn": prjct_1["prjct_sn"], "cntrct_execut_code": 'E',
         "ct_se_code": '99', "qy": 1, column['E']: e_99_1, "extra_sn": 0, "regist_dtm": datetime.now(),
         "register_id": session["member"]["member_id"]})
    cost_data.append(
        {"cntrct_sn": cntrct_sn2, "prjct_sn": prjct_2["prjct_sn"], "cntrct_execut_code": 'C',
         "ct_se_code": '99', "qy": 1, column['C']: c_99_2, "extra_sn": 0, "regist_dtm": datetime.now(),
         "register_id": session["member"]["member_id"]})
    cost_data.append(
        {"cntrct_sn": cntrct_sn2, "prjct_sn": prjct_2["prjct_sn"], "cntrct_execut_code": 'E',
         "ct_se_code": '99', "qy": 1, column['E']: e_99_2, "extra_sn": 0, "regist_dtm": datetime.now(),
         "register_id": session["member"]["member_id"]})

    for data in cost_data:
        sub_query = [key for key in data]
        params_query = ["%({})s".format(key) for key in data]

        query = """INSERT INTO cost({}) VALUES ({})""".format(",".join(sub_query), ",".join(params_query))
        g.curs.execute(query, data)

def get_reserved_project_list(params):
    query = """SELECT c.cntrct_sn
                    , p.prjct_sn
                    , c.bcnc_sn
                    , (SELECT bcnc_nm FROM bcnc WHERE bcnc_sn=c.bcnc_sn) AS bcnc_nm
                    , c.spt_nm
                    FROM contract c
                    LEFT OUTER JOIN project p ON c.cntrct_sn=p.cntrct_sn
                    WHERE c.progrs_sttus_code IN ('C', 'N')"""
    data = []
    if "s_bcnc_sn" in params and params['s_bcnc_sn']:
        query += " AND c.bcnc_sn=%s"
        data.append(params["s_bcnc_sn"])
    g.curs.execute(query, data)
    projects = g.curs.fetchall()
    result = []
    for r in projects:

        pParams = {"s_cntrct_sn" : r['cntrct_sn'], "s_prjct_sn" : r["prjct_sn"]}
        outsrcs = get_outsrc_report_list(pParams)
        for outsrc in outsrcs:
            if "s_resrv_bcnc" in params and params['s_resrv_bcnc']:
                if int(params["s_resrv_bcnc"]) != int(outsrc['outsrc_fo_sn']):
                    continue
            row = dict()
            row['r_dt_bg'] = outsrc['r_dt_bg']
            row['r_dt_ed'] = outsrc['r_dt_ed']
            row['r_dt_reg'] = outsrc['r_dt_reg']
            row['rm'] = outsrc['rm']
            row['cntrct_sn'] = r['cntrct_sn']
            row['bcnc_nm'] = r['bcnc_nm']
            row['spt_nm'] = r['spt_nm']
            row['outsrc_fo_sn'] = outsrc['outsrc_fo_sn']
            row['outsrc_fo_nm'] = outsrc['outsrc_fo_nm']
            taxbilList = outsrc['taxbilList']
            row['cntrct_amount'] = sum([t['splpc_am']+(t['vat'] if t['vat'] != '' else 0) for t in taxbilList])
            rcppayList = outsrc['rcppayList']
            row['rcppay_amount'] = sum([t['amount'] for t in rcppayList])
            if row['cntrct_amount'] > row['rcppay_amount']:
                row['diff'] = row['cntrct_amount'] - row['rcppay_amount']
                result.append(row)
    return result

def update_biss(params):
    data = dict()
    for i in range(10):
        key = "biss_{}".format(chr(ord('a')+i))
        data[key] = params[key]
    keys = list(data.keys())
    query = """UPDATE contract SET {} WHERE cntrct_sn=%(cntrct_sn)s""".format(",".join(["{0}=%({0})s".format(k) for k in keys]))
    g.curs.execute(query, params)
def update_flaw_co(params):
    query = """UPDATE contract SET flaw_co=%(biss)s WHERE cntrct_sn=%(cntrct_sn)s"""
    g.curs.execute(query, params)