from flask import session, jsonify, g
from app.helpers.datatable_helper import dt_query

def get_approval_datatable(params):
#     query = """SELECT c.ctmmny_sn
# 				, c.cntrct_sn
# 				, c.cntrct_nm
# 				, p.prjct_sn
# 				, p.prjct_ty_code
# 				, (SELECT code_nm FROM code WHERE ctmmny_sn=1 AND parnts_code='PRJCT_TY_CODE' AND code=p.prjct_ty_code) AS prjct_ty_nm
# 				, cntrct_se_code
# 				, (SELECT code_nm FROM code WHERE ctmmny_sn=1 AND parnts_code='CNTRCT_SE_CODE' AND code=p.cntrct_se_code) AS cntrct_se_nm
# 				, mngr_sn
# 				, (SELECT mber_nm FROM member WHERE mber_sn=p.mngr_sn) AS mngr_nm
# 				, manage_no
# 				, eqpmn_dtls
# 				, cntrwk_dtls
# 				, cntrct_dscnt_rt
# 				, cnsul_dscnt_rt
# 				, drw_opertor_sn
# 				, (SELECT mber_nm FROM member WHERE mber_sn=p.drw_opertor_sn) AS drw_opertor_nm
# 				, acmslt_sttemnt_at
# 				, cntwrk_regstr_ennc
# 				, p.partclr_matter
# 				, enty
# 				, enty_de
# 				, enty_rm
# 				, prtpay
# 				, prtpay_de
# 				, prtpay_rm
# 				, surlus
# 				, surlus_de
# 				, surlus_rm
# 				, setle_mth
# 				, p.register_id
# 				, p.update_dtm
# 				, p.updater_id
# 				, c.cntrct_no
# 				, c.cntrct_de
# 				, c.cntrct_nm
# 				, CASE WHEN c.prjct_ty_code IN ('NR') THEN
# 				(SELECT IFNULL(SUM(IFNULL(co.QY, 0)*IFNULL(co.SALAMT,0)),0) FROM cost co WHERE co.cntrct_sn = c.cntrct_sn AND co.cntrct_execut_code IN ('A', 'C'))
# 				WHEN c.prjct_ty_code IN ('BF') AND c.progrs_sttus_code <> 'B' THEN
# 				(SELECT IFNULL(SUM(ROUND(IFNULL(co.QY, 0)*IFNULL(co.puchas_amount,0)*0.01*(100.0-IFNULL(co.dscnt_rt, 0))*IFNULL(co.fee_rt, 0)*0.01)),0) FROM cost co WHERE co.cntrct_sn = c.cntrct_sn AND co.cntrct_execut_code IN ('C'))
# 				WHEN c.prjct_ty_code IN ('BD') AND c.progrs_sttus_code <> 'B' THEN
# 				(SELECT IFNULL(SUM(IFNULL(co.QY, 0)*IFNULL(co.SALAMT,0)),0) FROM cost co WHERE co.cntrct_sn = c.cntrct_sn AND co.cntrct_execut_code IN ('A', 'C'))
# 				WHEN c.prjct_ty_code IN ('BD') AND c.progrs_sttus_code = 'B' THEN
# 				(SELECT IFNULL(SUM(IFNULL(co.QY, 0)*IFNULL(co.SALAMT,0)),0) FROM cost co WHERE co.cntrct_sn = c.cntrct_sn AND (co.cost_date > '0000-00-00') AND co.cntrct_execut_code IN ('C'))
# 				ELSE 0
# 				END AS cntrct_amount
# 				, CASE WHEN c.prjct_ty_code IN ('NR') THEN
# 				(SELECT IFNULL(SUM(IFNULL(co.QY, 0)*IFNULL(co.SALAMT,0)),0) FROM cost co WHERE co.cntrct_sn = c.cntrct_sn AND co.cntrct_execut_code IN ('A', 'C') AND co.cost_date BETWEEN '{0} 00:00:00' AND '{1} 23:59:59')
# 				WHEN c.prjct_ty_code IN ('BF') AND c.progrs_sttus_code <> 'B' THEN
# 				(SELECT IFNULL(SUM(ROUND(IFNULL(co.QY, 0)*IFNULL(co.puchas_amount,0)*0.01*(100.0-IFNULL(co.dscnt_rt, 0))*IFNULL(co.fee_rt, 0)*0.01)),0) FROM cost co WHERE co.cntrct_sn = c.cntrct_sn AND co.cntrct_execut_code IN ('C') AND co.cost_date BETWEEN '{0} 00:00:00' AND '{1} 23:59:59')
# 				WHEN c.prjct_ty_code IN ('BD') AND c.progrs_sttus_code <> 'B' THEN
# 				(SELECT IFNULL(SUM(IFNULL(co.QY, 0)*IFNULL(co.SALAMT,0)),0) FROM cost co WHERE co.cntrct_sn = c.cntrct_sn AND co.cntrct_execut_code IN ('A', 'C') AND co.cost_date BETWEEN '{0} 00:00:00' AND '{1} 23:59:59')
# 				WHEN c.prjct_ty_code IN ('BD') AND c.progrs_sttus_code = 'B' THEN
# 				(SELECT IFNULL(SUM(IFNULL(co.QY, 0)*IFNULL(co.SALAMT,0)),0) FROM cost co WHERE co.cntrct_sn = c.cntrct_sn AND co.cntrct_execut_code IN ('C') AND co.cost_date BETWEEN '{0} 00:00:00' AND '{1} 23:59:59')
# 				ELSE 0
# 				END AS amount
# 				, c.bcnc_sn
# 				, (SELECT bcnc_nm FROM bcnc WHERE bcnc_sn=c.bcnc_sn) AS bcnc_nm
# 				, c.spt_nm
# 				, c.spt_adres
# 				, c.cntrwk_bgnde
# 				, c.cntrwk_endde
# 				, c.etc_sttus
# 				, m.dept_code
# 				, (SELECT code_nm FROM code WHERE ctmmny_sn=1 AND parnts_code='DEPT_CODE' AND code=m.dept_code) AS dept_nm
# 				, c.bsn_chrg_sn
# 				, GET_MEMBER_NAME(c.bsn_chrg_sn, 'M') AS bsn_chrg_nm
# 				, c.spt_chrg_sn
# 				, GET_MEMBER_NAME(c.spt_chrg_sn, 'M') AS spt_chrg_nm
# 				, c.prjct_creat_at
# 				, c.progrs_sttus_code
# 				, (SELECT code_nm FROM code WHERE ctmmny_sn=1 AND parnts_code='PROGRS_STTUS_CODE' AND code=c.progrs_sttus_code) AS progrs_sttus_nm
# 				, (SELECT code_nm FROM code WHERE ctmmny_sn=1 AND parnts_code='PRJCT_CREAT_AT' AND code=c.prjct_creat_at) AS prjct_sttus_nm
# 				, c.flaw_co
# 				, c.regist_dtm
# 				, c.register_id
# 				, c.update_dtm
# 				, c.updater_id
# 				FROM contract c
# 				LEFT OUTER JOIN member m
# 				ON m.mber_sn=c.bsn_chrg_sn
# 				LEFT OUTER JOIN project p
# 				ON p.cntrct_sn=c.cntrct_sn
# 				WHERE 1=1
# 				AND ((c.cntrct_de BETWEEN '{0} 00:00:00'
# 				AND '{1} 23:59:59') OR ((SELECT COUNT(co.cntrwk_ct_sn) FROM cost co WHERE 1=1 AND co.cntrct_execut_code IN ('A', 'C') AND co.cost_date BETWEEN '{0} 00:00:00' AND '{1} 23:59:59' AND co.cntrct_sn = c.cntrct_sn GROUP BY co.cntrct_sn) > 0))
# """.format(params['s_cntrct_de_start'], params['s_cntrct_de_end'])
#
#     data = []
#
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
    result = dict()
    result['recordsTotal'] = 1
    result['recordsFiltered'] = result['recordsTotal']
    result['data'] = [{"approval_se_nm" : "공사", "approval_ty_nm" : "수주계약서", "cntrct_nm" : "현장명현장명 현장명", "approval_status" : "완료", "start_de" : "2023-01-01", "end_de" : "2023-01-15", "final_mber_nm" : "이경민"}]
    return result
