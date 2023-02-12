from flask import session, jsonify, g
from app.helpers.datatable_helper import dt_query
from collections import OrderedDict

def get_stock_datatable(params, use_type):
    query = """SELECT '1' AS ctmmny_sn
				# , GROUP_CONCAT(s.stock_sn) AS stock_sn
				# , COUNT(*) AS qy
				, s.stock_sn				
				, prduct_se_code
				, (SELECT code_nm FROM code WHERE parnts_code='PRDUCT_SSE_CODE' AND code=s.prduct_se_code) AS prduct_se_nm
				, prduct_ty_code
				, (SELECT code_nm FROM code WHERE parnts_code='PRDUCT_TY_CODE' AND code=s.prduct_ty_code) AS prduct_ty_nm
				, s.model_no AS modl_nm
				, m.delng_sn AS delng_sn
				, m.cntrct_sn AS cntrct_sn
				, p.ddt_man AS puchas_de
				, s.use_flag as puchas_se_code
				, IF(p.delng_ty_code <> '61', IFNULL(p.dlamt, 0), IFNULL(p.dlivy_amt, 0) * (100 - IFNULL(p.dscnt_rt,0) - IFNULL(p.add_dscnt_rt, 0))/100) AS puchas_amount_one
				, IFNULL((SELECT spt_nm FROM contract ct WHERE ct.cntrct_sn=m.cntrct_sn), '') AS cntrct_nm
				, IFNULL((SELECT b.bcnc_nm FROM bcnc b JOIN contract ct ON b.bcnc_sn=ct.bcnc_sn WHERE ct.cntrct_sn=m.cntrct_sn), '') AS bcnc_nm
				, CASE WHEN m.stock_sttus IN (2, 3) THEN sa.dlivy_de ELSE '' END AS instl_de
				, m.ddt_man AS wrhousng_de
				, s.rm
				, s.etc_flag AS bigo
				, m.stock_sttus AS invn_sttus_code
				, CASE WHEN m.stock_sttus=1 AND (s.rm LIKE %s) IS NOT TRUE THEN (SELECT code_nm FROM code WHERE parnts_code='INVN_STTUS_CODE' AND code=m.cntrct_sn)
				WHEN m.stock_sttus=1 AND m.cntrct_sn = 2 AND s.rm LIKE %s THEN '이현/예약'
				WHEN m.stock_sttus=1 AND m.cntrct_sn = 3 AND s.rm LIKE %s THEN '기타/예약'
				WHEN m.stock_sttus IN (2,3) THEN (SELECT code_nm FROM code WHERE parnts_code='INVN_STTUS_CODE' AND code=(m.stock_sttus-2))
				ELSE (SELECT code_nm FROM code WHERE parnts_code='INVN_STTUS_CODE' AND code=m.stock_sttus)
				END AS invn_sttus_nm
				FROM stock s 
				LEFT JOIN 
				(SELECT * FROM stock_log WHERE log_sn IN (SELECT MAX(log_sn) FROM stock_log GROUP BY log_sn)) m ON s.stock_sn=m.stock_sn
				LEFT JOIN
				(SELECT * FROM stock_log WHERE log_sn IN (SELECT MIN(log_sn) FROM stock_log GROUP BY log_sn)) mi ON s.stock_sn=mi.stock_sn
				LEFT JOIN
				account p ON mi.delng_sn=p.delng_sn
				LEFT JOIN
				account sa ON sa.cnnc_sn=p.delng_sn
				WHERE s.use_type = %s
				AND m.ddt_man BETWEEN '{0}' AND '{1}'
""".format(params['s_ddt_man_start'], params['s_ddt_man_end'])
    # query += "GROUP BY prduct_se_nm, prduct_ty_nm, modl_nm, bigo, puchas_de, puchas_se_code, puchas_amount_one, bcnc_nm, cntrct_nm, instl_de, wrhousng_de, invn_sttus_nm, rm "
    data = ["%예약%", "%예약%", "%예약%", use_type]

    if "s_prduct_ty_code" in params and params['s_prduct_ty_code']:
        if int(params["s_prduct_ty_code"]) == 0:
            query += " AND s.prduct_ty_code IN (1, 2) "
        else:
            query += " AND s.prduct_ty_code=%s"
            data.append(params["s_prduct_ty_code"])

    if "s_modl_nm" in params and params['s_modl_nm']:
        query += " AND s.model_no LIKE %s"
        data.append('%{}%'.format(params["s_modl_nm"]))

    if "s_rm" in params and params['s_rm']:
        query += " AND s.rm LIKE %s"
        data.append('%{}%'.format(params["s_rm"]))

    if "s_cntrct_nm" in params and params['s_cntrct_nm']:
        query += " AND m.stock_sttus IN (2, 3) AND (SELECT spt_nm FROM contract ct WHERE ct.cntrct_sn=m.cntrct_sn) LIKE %s"
        data.append('%{}%'.format(params["s_cntrct_nm"]))

    if "s_bcnc_sn" in params and params['s_bcnc_sn']:
        query += " AND m.stock_sttus IN (2,3) AND (SELECT bcnc_sn FROM contract ct WHERE ct.cntrct_sn=m.cntrct_sn) = %s"
        data.append(params["s_bcnc_sn"])

    if "s_puchas_se_code" in params and params['s_puchas_se_code']:
        query += " AND s.use_flag=%s"
        data.append(params['s_puchas_se_code'])

    if "s_bigo" in params and params['s_bigo']:
        query += " AND s.etc_flag=%s"
        data.append(params['s_bigo'])

    if "s_invn_sttus_code" in params and params['s_invn_sttus_code']:
        sttus_code = params['s_invn_sttus_code']
        if sttus_code == '2S':
            query += " AND (m.stock_sttus=1 AND m.cntrct_sn=2 AND s.rm LIKE %s)"
            data.append("%예약%")

        elif sttus_code == '3S':
            query += " AND (m.stock_sttus=1 AND m.cntrct_sn=3 AND s.rm LIKE %s)"
            data.append("%예약%")

        elif sttus_code == "0":
            query += " AND m.stock_sttus = 2"

        elif sttus_code == "1":
            query += " AND m.stock_sttus = 3"

        elif sttus_code == "4":
            query += " AND m.stock_sttus = 4"

        elif sttus_code == "100":
            query += " AND m.stock_sttus = 1 AND m.cntrct_sn IN (2, 3)"

        else:
            query += " AND m.stock_sttus = 1 AND m.cntrct_sn=%s"
            data.append(sttus_code)


    return dt_query(query, data, params)

def get_stock_summary(params, use_type):
    query = """SELECT '1' AS ctmmny_sn
                , count(*) as cnt
                , m.stock_sttus
                , count(distinct m.cntrct_sn) AS cntrct_count
                , sum(IF(p.delng_ty_code <> '61', IFNULL(p.dlamt, 0), IFNULL(p.dlivy_amt, 0) * (100 - IFNULL(p.dscnt_rt,0) - IFNULL(p.add_dscnt_rt, 0))/100)) as amount
                , IF(m.stock_sttus=1, m.cntrct_sn, 0) AS cntrct_sn
				FROM stock s 
				LEFT JOIN 
				(SELECT * FROM stock_log WHERE log_sn IN (SELECT MAX(log_sn) FROM stock_log GROUP BY log_sn)) m ON s.stock_sn=m.stock_sn
				LEFT JOIN
				(SELECT * FROM stock_log WHERE log_sn IN (SELECT MIN(log_sn) FROM stock_log GROUP BY log_sn)) mi ON s.stock_sn=mi.stock_sn
				LEFT JOIN
				account p ON mi.delng_sn=p.delng_sn
				LEFT JOIN
				account sa ON sa.cnnc_sn=p.delng_sn
				WHERE s.use_type = %s
				AND m.ddt_man BETWEEN '{0}' AND '{1}'
""".format(params['s_ddt_man_start'], params['s_ddt_man_end'])
    # query += "GROUP BY prduct_se_nm, prduct_ty_nm, modl_nm, bigo, puchas_de, puchas_se_code, puchas_amount_one, bcnc_nm, cntrct_nm, instl_de, wrhousng_de, invn_sttus_nm, rm "
    data = [use_type]

    if "s_prduct_ty_code" in params and params['s_prduct_ty_code']:
        if int(params["s_prduct_ty_code"]) == 0:
            query += " AND s.prduct_ty_code IN (1, 2) "
        else:
            query += " AND s.prduct_ty_code=%s"
            data.append(params["s_prduct_ty_code"])

    if "s_modl_nm" in params and params['s_modl_nm']:
        query += " AND s.model_no LIKE %s"
        data.append('%{}%'.format(params["s_modl_nm"]))

    if "s_rm" in params and params['s_rm']:
        query += " AND s.rm LIKE %s"
        data.append('%{}%'.format(params["s_rm"]))

    if "s_cntrct_nm" in params and params['s_cntrct_nm']:
        query += " AND m.stock_sttus IN (2, 3) AND (SELECT spt_nm FROM contract ct WHERE ct.cntrct_sn=m.cntrct_sn) LIKE %s"
        data.append('%{}%'.format(params["s_cntrct_nm"]))

    if "s_bcnc_sn" in params and params['s_bcnc_sn']:
        query += " AND m.stock_sttus IN (2,3) AND (SELECT bcnc_sn FROM contract ct WHERE ct.cntrct_sn=m.cntrct_sn) = %s"
        data.append(params["s_bcnc_sn"])

    if "s_puchas_se_code" in params and params['s_puchas_se_code']:
        query += " AND s.use_flag=%s"
        data.append(params['s_puchas_se_code'])

    if "s_bigo" in params and params['s_bigo']:
        query += " AND s.etc_flag=%s"
        data.append(params['s_bigo'])

    if "s_invn_sttus_code" in params and params['s_invn_sttus_code']:
        sttus_code = params['s_invn_sttus_code']
        if sttus_code == '2S':
            query += " AND (m.stock_sttus=1 AND m.cntrct_sn=2 AND s.rm LIKE %s)"
            data.append("%예약%")

        elif sttus_code == '3S':
            query += " AND (m.stock_sttus=1 AND m.cntrct_sn=3 AND s.rm LIKE %s)"
            data.append("%예약%")

        elif sttus_code == "0":
            query += " AND m.stock_sttus = 2"

        elif sttus_code == "1":
            query += " AND m.stock_sttus = 3"

        elif sttus_code == "4":
            query += " AND m.stock_sttus = 4"

        elif sttus_code == "100":
            query += " AND m.stock_sttus = 1 AND m.cntrct_sn IN (2, 3)"

        else:
            query += " AND m.stock_sttus = 1 AND m.cntrct_sn=%s"
            data.append(sttus_code)

    query += " GROUP BY m.stock_sttus, IF(m.stock_sttus=1, m.cntrct_sn, 0)"
    g.curs.execute(query, data)
    result = g.curs.fetchall()
    return result
