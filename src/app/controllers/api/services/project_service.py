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
				AND r.acntctgr_code NOT IN ('108', '638', '110') 
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
				AND c.acntctgr_code NOT IN ('108', '638', '110') 
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
				FROM outsrc o
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
				, (SELECT bcnc_nm FROM bcnc WHERE ctmmny_sn=t.ctmmny_sn AND bcnc_sn=t.pblicte_trget_sn) AS pblicte_trget_nm
				FROM taxbil t
				WHERE t.ctmmny_sn = 1
				AND t.cntrct_sn = %(s_cntrct_sn)s
				AND t.prjct_sn = %(s_prjct_sn)s
				AND t.delng_se_code = 'S2'
				ORDER BY t.pblicte_de, t.pblicte_trget_sn
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
				FROM rcppay r
				WHERE r.ctmmny_sn = 1
				AND r.cntrct_sn = %(s_cntrct_sn)s
				AND r.prjct_sn = %(s_prjct_sn)s
				AND r.rcppay_se_code = 'I2'
				ORDER BY r.rcppay_de
"""
    g.curs.execute(query, params)
    result = g.curs.fetchall()
    return result

def get_s3_taxbil_report_list(params):
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
				AND p.delng_ty_code IN ('61', '62')
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




