from flask import session, jsonify, g
from app.helpers.datatable_helper import dt_query
from collections import OrderedDict

def get_stock_dp_datatable_search(params):
    query = """SELECT '1' AS ctmmny_sn
    				, s.stock_sn AS stock_sn
    				, prduct_se_code AS prduct_se_code
    				, (SELECT code_nm FROM code WHERE parnts_code='PRDUCT_SSE_CODE' AND code=s.prduct_se_code) AS prduct_se_nm
    				, prduct_ty_code as prduct_ty_code
    				, (SELECT code_nm FROM code WHERE parnts_code='PRDUCT_TY_CODE' AND code=s.prduct_ty_code) AS prduct_ty_nm
    				, s.model_no AS modl_nm
    				, m.delng_sn AS delng_sn
    				, m.cntrct_sn AS cntrct_sn
    				, p.ddt_man AS puchas_de
    				, s.use_flag as puchas_se_code
    				, CASE WHEN mi.stock_sttus = 1 THEN IF(p.dlivy_amt IS NULL, p.dlamt, IFNULL(p.dlivy_amt, 0) * (100 - IFNULL(p.dscnt_rt,0) - IFNULL(p.add_dscnt_rt, 0))/100)
                        WHEN mi.stock_sttus = 2 THEN IF(p.dlivy_amt IS NULL, IFNULL(p.dlamt, 0), IFNULL(p.dlivy_amt, 0) * (100 - IFNULL(p.dscnt_rt,0) - IFNULL(p.add_dscnt_rt, 0))/100)
                        ELSE 0
                        END AS puchas_amount_one
    				, CASE WHEN m.stock_sttus IN (2, 3) THEN IFNULL((SELECT spt_nm FROM contract ct WHERE ct.cntrct_sn=m.cntrct_sn), '')
    				  ELSE IFNULL((SELECT spt_nm FROM contract ct WHERE ct.cntrct_sn=(SELECT cntrct_sn FROM stock_log WHERE log_sn=m.cnnc_sn)), '') END AS cntrct_nm
    				, CASE WHEN m.stock_sttus IN (2, 3) THEN IFNULL((SELECT b.bcnc_nm FROM bcnc b JOIN contract ct ON b.bcnc_sn=ct.bcnc_sn WHERE ct.cntrct_sn=m.cntrct_sn), '')
    				  ELSE IFNULL((SELECT b.bcnc_nm FROM bcnc b JOIN contract ct ON b.bcnc_sn=ct.bcnc_sn WHERE ct.cntrct_sn=(SELECT cntrct_sn FROM stock_log WHERE log_sn=m.cnnc_sn)), '') END AS bcnc_nm
    				, CASE WHEN m.stock_sttus IN (2, 3) THEN sa.dlivy_de ELSE '' END AS instl_de
    				, m.ddt_man AS wrhousng_de
    				, s.rm AS rm
    				, s.use_type AS bigo
    				, m.stock_sttus AS invn_sttus_code
    				, (SELECT code_nm FROM code WHERE parnts_code='INVN_STTUS_CODE' AND code=(m.stock_sttus-2)) AS invn_sttus_nm
    				FROM (SELECT * FROM stock WHERE 1=1) s
    				INNER JOIN
    				(SELECT x.* FROM stock_log x INNER JOIN (SELECT stock_sn, MAX(log_sn) AS m_log_sn FROM stock_log GROUP BY stock_sn) y ON x.stock_sn=y.stock_sn AND x.log_sn=y.m_log_sn) m ON s.stock_sn=m.stock_sn
    				INNER JOIN
    				(SELECT x.* FROM stock_log x INNER JOIN (SELECT stock_sn, MIN(log_sn) AS m_log_sn FROM stock_log GROUP BY stock_sn) y ON x.stock_sn=y.stock_sn AND x.log_sn=y.m_log_sn) mi ON s.stock_sn=mi.stock_sn
    				INNER JOIN
    				(SELECT * FROM account WHERE delng_se_code='P') p ON mi.delng_sn=p.delng_sn
    				INNER JOIN
    				(SELECT * FROM account WHERE delng_se_code='S') sa ON sa.cnnc_sn=p.delng_sn
    				WHERE 1=1 AND m.cntrct_sn=%s AND m.stock_sttus=2"""
    data = [params["cntrct_sn"]]
    if "before" in params and params["before"]:
        befores = params["before"].split(",")
        query += " AND s.stock_sn NOT IN ({})".format(",".join(["%s"]*len(befores)))
        data += befores

    return dt_query(query, data, params)

def get_stock_datatable_search(params):
    query = """SELECT '1' AS ctmmny_sn
    				, s.stock_sn AS stock_sn				
    				, prduct_se_code AS prduct_se_code
    				, (SELECT code_nm FROM code WHERE parnts_code='PRDUCT_SSE_CODE' AND code=s.prduct_se_code) AS prduct_se_nm
    				, prduct_ty_code as prduct_ty_code
    				, (SELECT code_nm FROM code WHERE parnts_code='PRDUCT_TY_CODE' AND code=s.prduct_ty_code) AS prduct_ty_nm
    				, s.model_no AS modl_nm
    				, m.delng_sn AS delng_sn
    				, m.cntrct_sn AS cntrct_sn
    				, p.ddt_man AS puchas_de
    				, s.use_flag as puchas_se_code
    				, CASE WHEN mi.stock_sttus = 1 THEN IF(p.dlivy_amt IS NULL, p.dlamt, IFNULL(p.dlivy_amt, 0) * (100 - IFNULL(p.dscnt_rt,0) - IFNULL(p.add_dscnt_rt, 0))/100)
                        WHEN mi.stock_sttus = 2 THEN IF(p.dlivy_amt IS NULL, IFNULL(p.dlamt, 0), IFNULL(p.dlivy_amt, 0) * (100 - IFNULL(p.dscnt_rt,0) - IFNULL(p.add_dscnt_rt, 0))/100)
                        ELSE 0
                        END AS puchas_amount_one
    				, CASE WHEN m.stock_sttus IN (2, 3) THEN IFNULL((SELECT spt_nm FROM contract ct WHERE ct.cntrct_sn=m.cntrct_sn), '')
    				  ELSE IFNULL((SELECT spt_nm FROM contract ct WHERE ct.cntrct_sn=(SELECT cntrct_sn FROM stock_log WHERE log_sn=m.cnnc_sn)), '') END AS cntrct_nm
    				, CASE WHEN m.stock_sttus IN (2, 3) THEN IFNULL((SELECT b.bcnc_nm FROM bcnc b JOIN contract ct ON b.bcnc_sn=ct.bcnc_sn WHERE ct.cntrct_sn=m.cntrct_sn), '')
    				  ELSE IFNULL((SELECT b.bcnc_nm FROM bcnc b JOIN contract ct ON b.bcnc_sn=ct.bcnc_sn WHERE ct.cntrct_sn=(SELECT cntrct_sn FROM stock_log WHERE log_sn=m.cnnc_sn)), '') END AS bcnc_nm
    				, CASE WHEN m.stock_sttus IN (2, 3) THEN sa.dlivy_de ELSE '' END AS instl_de
    				, m.ddt_man AS wrhousng_de
    				, s.rm AS rm
    				, s.use_type AS bigo
    				, m.stock_sttus AS invn_sttus_code
    				, CASE WHEN m.stock_sttus=1 AND (s.rm LIKE %s) IS NOT TRUE THEN (SELECT code_nm FROM code WHERE parnts_code='INVN_STTUS_CODE' AND code=m.cntrct_sn)
    				WHEN m.stock_sttus=1 AND m.cntrct_sn = 2 AND s.rm LIKE %s THEN '이현/예약'
    				WHEN m.stock_sttus=1 AND m.cntrct_sn = 3 AND s.rm LIKE %s THEN '기타/예약'
    				WHEN m.stock_sttus IN (2,3) THEN (SELECT code_nm FROM code WHERE parnts_code='INVN_STTUS_CODE' AND code=(m.stock_sttus-2))
    				ELSE (SELECT code_nm FROM code WHERE parnts_code='INVN_STTUS_CODE' AND code=m.stock_sttus)
    				END AS invn_sttus_nm
    				FROM (SELECT * FROM stock WHERE 1=1) s 
    				INNER JOIN 
    				(SELECT x.* FROM stock_log x INNER JOIN (SELECT stock_sn, MAX(log_sn) AS m_log_sn FROM stock_log GROUP BY stock_sn) y ON x.stock_sn=y.stock_sn AND x.log_sn=y.m_log_sn) m ON s.stock_sn=m.stock_sn
    				INNER JOIN
    				(SELECT x.* FROM stock_log x INNER JOIN (SELECT stock_sn, MIN(log_sn) AS m_log_sn FROM stock_log GROUP BY stock_sn) y ON x.stock_sn=y.stock_sn AND x.log_sn=y.m_log_sn) mi ON s.stock_sn=mi.stock_sn
    				INNER JOIN
    				(SELECT * FROM account WHERE delng_se_code='P') p ON mi.delng_sn=p.delng_sn
    				LEFT OUTER JOIN
    				(SELECT * FROM account WHERE delng_se_code='S') sa ON sa.cnnc_sn=p.delng_sn
    				WHERE 1=1
    				AND m.ddt_man BETWEEN '{0}' AND '{1}'
    """.format(params['s_ddt_man_start'], params['s_ddt_man_end'])
    # query += "GROUP BY prduct_se_nm, prduct_ty_nm, modl_nm, bigo, puchas_de, puchas_se_code, puchas_amount_one, bcnc_nm, cntrct_nm, instl_de, wrhousng_de, invn_sttus_nm, rm "
    data = ["%예약%", "%예약%", "%예약%"]
    if "after" in params and params["after"]:
        afters = params["after"].split(",")
        if "before" in params and params["before"]:
            befores = params["before"].split(",")
            afters = [a for a in afters if a not in befores]
        if len(afters)>0:
            query += " AND ( s.stock_sn IN ({}) OR ( 1=1 ".format(",".join(["%s"]*len(afters)))
            data += afters
    if "before" in params and params["before"]:
        befores = params["before"].split(",")
        query += " AND s.stock_sn NOT IN ({})".format(",".join(["%s"]*len(befores)))
        data += befores
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
        query += " AND m.stock_sttus=1 AND IFNULL((SELECT spt_nm FROM contract ct WHERE ct.cntrct_sn=(SELECT cntrct_sn FROM stock_log WHERE log_sn=m.cnnc_sn)), '') LIKE %s"
        data.append('%{}%'.format(params["s_cntrct_nm"]))

    if "s_bcnc_sn" in params and params['s_bcnc_sn']:
        query += " AND m.stock_sttus=1 AND (SELECT bcnc_sn FROM contract ct WHERE ct.cntrct_sn=m.cntrct_sn) = %s"
        data.append(params["s_bcnc_sn"])

    if "s_puchas_se_code" in params and params['s_puchas_se_code']:
        query += " AND s.use_flag=%s"
        data.append(params['s_puchas_se_code'])

    if "s_bigo" in params and params['s_bigo']:
        query += " AND s.use_type=%s"
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
    if "after" in params and params["after"]:
        afters = params["after"].split(",")
        if "before" in params and params["before"]:
            befores = params["before"].split(",")
            afters = [a for a in afters if a not in befores]
        if len(afters) > 0:
            query += ") )"

    print(query, data)
    return dt_query(query, data, params)
def get_stock_datatable(params, prduct_se_code):
    query = """SELECT '1' AS ctmmny_sn
				, s.stock_sn AS stock_sn				
				, prduct_se_code AS prduct_se_code
				, (SELECT code_nm FROM code WHERE parnts_code='PRDUCT_SSE_CODE' AND code=s.prduct_se_code) AS prduct_se_nm
				, prduct_ty_code as prduct_ty_code
				, (SELECT code_nm FROM code WHERE parnts_code='PRDUCT_TY_CODE' AND code=s.prduct_ty_code) AS prduct_ty_nm
				, s.model_no AS modl_nm
				, m.delng_sn AS delng_sn
				, m.cntrct_sn AS cntrct_sn
				, p.ddt_man AS puchas_de
				, s.use_flag as puchas_se_code
				, CASE WHEN mi.stock_sttus = 1 THEN IF(p.dlivy_amt IS NULL, p.dlamt, IFNULL(p.dlivy_amt, 0) * (100 - IFNULL(p.dscnt_rt,0) - IFNULL(p.add_dscnt_rt, 0))/100)
                    WHEN mi.stock_sttus = 2 THEN IF(p.dlivy_amt IS NULL, IFNULL(p.dlamt, 0), IFNULL(p.dlivy_amt, 0) * (100 - IFNULL(p.dscnt_rt,0) - IFNULL(p.add_dscnt_rt, 0))/100)
                    WHEN mi.stock_sttus = 3 THEN IFNULL(p.dlamt, 0)
                    ELSE 0
                    END AS puchas_amount_one
				, CASE WHEN m.stock_sttus IN (2, 3) THEN IFNULL((SELECT spt_nm FROM contract ct WHERE ct.cntrct_sn=m.cntrct_sn), '')
				  ELSE IFNULL((SELECT spt_nm FROM contract ct WHERE ct.cntrct_sn=(SELECT cntrct_sn FROM stock_log WHERE log_sn=m.cnnc_sn)), '') END AS cntrct_nm
				, CASE WHEN m.stock_sttus IN (2, 3) THEN IFNULL((SELECT b.bcnc_nm FROM bcnc b JOIN contract ct ON b.bcnc_sn=ct.bcnc_sn WHERE ct.cntrct_sn=m.cntrct_sn), '')
				  ELSE IFNULL((SELECT b.bcnc_nm FROM bcnc b JOIN contract ct ON b.bcnc_sn=ct.bcnc_sn WHERE ct.cntrct_sn=(SELECT cntrct_sn FROM stock_log WHERE log_sn=m.cnnc_sn)), '') END AS bcnc_nm
				, CASE WHEN m.stock_sttus IN (2, 3) THEN sa_last.dlivy_de ELSE '' END AS instl_de
				, IF(m.stock_sttus IN (1, 4), m.ddt_man, '') AS wrhousng_de
				, s.rm AS rm
				, s.use_type AS bigo
				, m.stock_sttus AS invn_sttus_code
				, CASE WHEN m.stock_sttus=1 AND (s.rm LIKE %s) IS NOT TRUE THEN (SELECT code_nm FROM code WHERE parnts_code='INVN_STTUS_CODE' AND code=m.cntrct_sn)
				WHEN m.stock_sttus=1 AND m.cntrct_sn = 2 AND s.rm LIKE %s THEN '이현/예약'
				WHEN m.stock_sttus=1 AND m.cntrct_sn = 3 AND s.rm LIKE %s THEN '기타/예약'
				WHEN m.stock_sttus IN (2,3) THEN (SELECT code_nm FROM code WHERE parnts_code='INVN_STTUS_CODE' AND code=(m.stock_sttus-2))
				ELSE (SELECT code_nm FROM code WHERE parnts_code='INVN_STTUS_CODE' AND code=m.stock_sttus)
				END AS invn_sttus_nm
				FROM (SELECT * FROM stock WHERE prduct_se_code=%s) s 
				INNER JOIN 
				(SELECT x.* FROM stock_log x INNER JOIN (SELECT stock_sn, MAX(log_sn) AS m_log_sn FROM stock_log GROUP BY stock_sn) y ON x.stock_sn=y.stock_sn AND x.log_sn=y.m_log_sn) m ON s.stock_sn=m.stock_sn
				INNER JOIN
				(SELECT x.* FROM stock_log x INNER JOIN (SELECT stock_sn, MIN(log_sn) AS m_log_sn FROM stock_log GROUP BY stock_sn) y ON x.stock_sn=y.stock_sn AND x.log_sn=y.m_log_sn) mi ON s.stock_sn=mi.stock_sn
				INNER JOIN
				(SELECT * FROM account WHERE delng_se_code='P') p ON mi.delng_sn=p.delng_sn
				LEFT OUTER JOIN
				(SELECT * FROM account WHERE delng_se_code='S') sa ON sa.cnnc_sn=p.delng_sn
				LEFT OUTER JOIN
				(SELECT * FROM account WHERE delng_se_code='P') p_last ON m.delng_sn=p_last.delng_sn
				LEFT OUTER JOIN
				(SELECT * FROM account WHERE delng_se_code='S') sa_last ON sa_last.cnnc_sn=p_last.delng_sn
				WHERE 1=1
				AND IF(m.stock_sttus IN (1, 4), m.ddt_man, sa_last.dlivy_de) BETWEEN '{0}' AND '{1}'
""".format(params['s_ddt_man_start'], params['s_ddt_man_end'])
    # query += "GROUP BY prduct_se_nm, prduct_ty_nm, modl_nm, bigo, puchas_de, puchas_se_code, puchas_amount_one, bcnc_nm, cntrct_nm, instl_de, wrhousng_de, invn_sttus_nm, rm "
    data = ["%예약%", "%예약%", "%예약%", prduct_se_code]

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
        query += " AND ((m.stock_sttus IN (2, 3) AND (SELECT spt_nm FROM contract ct WHERE ct.cntrct_sn=m.cntrct_sn) LIKE %s) OR (m.stock_sttus = 1 AND (SELECT spt_nm FROM contract ct WHERE ct.cntrct_sn=(SELECT cntrct_sn FROM stock_log WHERE log_sn=m.cnnc_sn)) LIKE %s))"
        data.append('%{}%'.format(params["s_cntrct_nm"]))
        data.append('%{}%'.format(params["s_cntrct_nm"]))

    if "s_bcnc_sn" in params and params['s_bcnc_sn']:
        query += " AND m.stock_sttus IN (2,3) AND (SELECT bcnc_sn FROM contract ct WHERE ct.cntrct_sn=m.cntrct_sn) = %s"
        data.append(params["s_bcnc_sn"])

    if "s_puchas_se_code" in params and params['s_puchas_se_code']:
        query += " AND s.use_flag=%s"
        data.append(params['s_puchas_se_code'])

    if "s_bigo" in params and params['s_bigo']:
        query += " AND s.use_type=%s"
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

    params["custom_order"] = ["IF(instl_de <> '', instl_de, IF(m.stock_sttus IN (1, 4), m.ddt_man, '')) DESC, invn_sttus_nm"]
    return dt_query(query, data, params)

def get_stock_summary(params, prduct_se_code):
    query = """SELECT '1' AS ctmmny_sn
                , count(*) as cnt
                , m.stock_sttus
                , count(distinct m.cntrct_sn) AS cntrct_count
                , sum(CASE WHEN m.stock_sttus = 3 THEN IFNULL(sa_last.dlamt, 0)
                    WHEN mi.stock_sttus = 1 THEN IF(p.dlivy_amt IS NULL, IFNULL(p.dlamt, 0), IFNULL(p.dlivy_amt, 0) * (100 - IFNULL(p.dscnt_rt,0) - IFNULL(p.add_dscnt_rt, 0))/100)
                    WHEN mi.stock_sttus = 2 THEN IF(p.dlivy_amt IS NULL, IFNULL(p.dlamt, 0), IFNULL(p.dlivy_amt, 0) * (100 - IFNULL(p.dscnt_rt,0) - IFNULL(p.add_dscnt_rt, 0))/100)
                    ELSE 0
                    END) as amount
                , IF(m.stock_sttus=1, m.cntrct_sn, 0) AS cntrct_sn
				FROM stock s 
				INNER JOIN 
				(SELECT x.* FROM stock_log x INNER JOIN (SELECT stock_sn, MAX(log_sn) AS m_log_sn FROM stock_log GROUP BY stock_sn) y ON x.stock_sn=y.stock_sn AND x.log_sn=y.m_log_sn) m ON s.stock_sn=m.stock_sn
				INNER JOIN
				(SELECT x.* FROM stock_log x INNER JOIN (SELECT stock_sn, MIN(log_sn) AS m_log_sn FROM stock_log GROUP BY stock_sn) y ON x.stock_sn=y.stock_sn AND x.log_sn=y.m_log_sn) mi ON s.stock_sn=mi.stock_sn
				INNER JOIN
				(SELECT * FROM account WHERE delng_se_code='P') p ON mi.delng_sn=p.delng_sn
				LEFT OUTER JOIN
				(SELECT * FROM account WHERE delng_se_code='S') sa ON sa.cnnc_sn=p.delng_sn
				LEFT OUTER JOIN
				(SELECT * FROM account WHERE delng_se_code='P') p_last ON m.delng_sn=p_last.delng_sn
				LEFT OUTER JOIN
				(SELECT * FROM account WHERE delng_se_code='S') sa_last ON sa_last.cnnc_sn=p_last.delng_sn
				WHERE s.prduct_se_code = %s
				AND IF(m.stock_sttus IN (1, 4), m.ddt_man, sa_last.dlivy_de) BETWEEN '{0}' AND '{1}'
""".format(params['s_ddt_man_start'], params['s_ddt_man_end'])
    # query += "GROUP BY prduct_se_nm, prduct_ty_nm, modl_nm, bigo, puchas_de, puchas_se_code, puchas_amount_one, bcnc_nm, cntrct_nm, instl_de, wrhousng_de, invn_sttus_nm, rm "
    data = [prduct_se_code]

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
        query += " AND ((m.stock_sttus IN (2, 3) AND (SELECT spt_nm FROM contract ct WHERE ct.cntrct_sn=m.cntrct_sn) LIKE %s) OR (m.stock_sttus = 1 AND (SELECT spt_nm FROM contract ct WHERE ct.cntrct_sn=(SELECT cntrct_sn FROM stock_log WHERE log_sn=m.cnnc_sn)) LIKE %s))"
        data.append('%{}%'.format(params["s_cntrct_nm"]))
        data.append('%{}%'.format(params["s_cntrct_nm"]))

    if "s_bcnc_sn" in params and params['s_bcnc_sn']:
        query += " AND m.stock_sttus IN (2,3) AND (SELECT bcnc_sn FROM contract ct WHERE ct.cntrct_sn=m.cntrct_sn) = %s"
        data.append(params["s_bcnc_sn"])

    if "s_puchas_se_code" in params and params['s_puchas_se_code']:
        query += " AND s.use_flag=%s"
        data.append(params['s_puchas_se_code'])

    if "s_bigo" in params and params['s_bigo']:
        query += " AND s.use_type=%s"
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


def get_stock(params):
    query = """SELECT s.stock_sn 
                , m.stock_sttus AS stock_sttus
                , prduct_se_code
				, (SELECT code_nm FROM code WHERE parnts_code='PRDUCT_SSE_CODE' AND code=s.prduct_se_code) AS prduct_se_nm
				, prduct_ty_code
				, (SELECT code_nm FROM code WHERE parnts_code='PRDUCT_TY_CODE' AND code=s.prduct_ty_code) AS prduct_ty_nm
                , CASE WHEN m.stock_sttus=1 AND (s.rm LIKE %(reserv)s) IS NOT TRUE THEN (SELECT code_nm FROM code WHERE parnts_code='INVN_STTUS_CODE' AND code=m.cntrct_sn)
				WHEN m.stock_sttus=1 AND m.cntrct_sn = 2 AND s.rm LIKE %(reserv)s THEN '이현/예약'
				WHEN m.stock_sttus=1 AND m.cntrct_sn = 3 AND s.rm LIKE %(reserv)s THEN '기타/예약'
				WHEN m.stock_sttus IN (2,3) THEN (SELECT spt_nm FROM contract WHERE cntrct_sn=m.cntrct_sn)
				ELSE (SELECT code_nm FROM code WHERE parnts_code='INVN_STTUS_CODE' AND code=m.stock_sttus)
				END AS invn_sttus_nm
				, p.ddt_man AS puchas_de
				, CASE WHEN mi.stock_sttus = 1 THEN IFNULL(p.dlivy_amt, 0) 
                    WHEN mi.stock_sttus = 2 THEN IFNULL(p.dlivy_amt, 0)
                    ELSE 0
                    END AS dlivy_amt
				, CASE WHEN mi.stock_sttus = 1 THEN IFNULL(p.dscnt_rt,0) + IFNULL(p.add_dscnt_rt, 0)
                    WHEN mi.stock_sttus = 2 THEN IFNULL(p.dscnt_rt,0) + IFNULL(p.add_dscnt_rt, 0)
                    ELSE 0
                    END AS dc
				, CASE WHEN mi.stock_sttus = 1 THEN IF(p.dlivy_amt IS NULL, p.dlamt, IFNULL(p.dlivy_amt, 0) * (100 - IFNULL(p.dscnt_rt,0) - IFNULL(p.add_dscnt_rt, 0))/100)
                    WHEN mi.stock_sttus = 2 THEN IF(p.dlivy_amt IS NULL, IFNULL(p.dlamt, 0), IFNULL(p.dlivy_amt, 0) * (100 - IFNULL(p.dscnt_rt,0) - IFNULL(p.add_dscnt_rt, 0))/100)
                    ELSE 0
                    END AS puchas_amount_one
				, CASE WHEN m.stock_sttus IN (2, 3) THEN IFNULL((SELECT spt_nm FROM contract ct WHERE ct.cntrct_sn=m.cntrct_sn), '')
				  ELSE IFNULL((SELECT spt_nm FROM contract ct WHERE ct.cntrct_sn=(SELECT cntrct_sn FROM stock_log WHERE log_sn=m.cnnc_sn)), '') END AS cntrct_nm
				, IFNULL((SELECT b.bcnc_nm FROM bcnc b JOIN contract ct ON b.bcnc_sn=ct.bcnc_sn WHERE ct.cntrct_sn=m.cntrct_sn), '') AS bcnc_nm
				, 1 AS qy
				, s.model_no AS modl_nm
				, m.stock_sttus AS item_sttus
				FROM stock s 
				INNER JOIN 
				(SELECT x.* FROM stock_log x INNER JOIN (SELECT stock_sn, MAX(log_sn) AS m_log_sn FROM stock_log GROUP BY stock_sn) y ON x.stock_sn=y.stock_sn AND x.log_sn=y.m_log_sn) m ON s.stock_sn=m.stock_sn
				INNER JOIN
				(SELECT x.* FROM stock_log x INNER JOIN (SELECT stock_sn, MIN(log_sn) AS m_log_sn FROM stock_log GROUP BY stock_sn) y ON x.stock_sn=y.stock_sn AND x.log_sn=y.m_log_sn) mi ON s.stock_sn=mi.stock_sn
				INNER JOIN
				(SELECT * FROM account WHERE delng_se_code='P') p ON mi.delng_sn=p.delng_sn
				WHERE s.stock_sn=%(s_stock_sn)s"""
    params['reserv'] = "%예약%"
    g.curs.execute(query, params)
    result = g.curs.fetchone()
    return result

def get_stock_log(params):
    query = """SELECT log_sn
                , stock_sttus
                , l.cntrct_sn
                , l.ddt_man
                , CASE WHEN stock_sttus IN (2, 3) THEN (SELECT spt_nm FROM contract WHERE cntrct_sn=l.cntrct_sn)
                WHEN stock_sttus = 1 THEN (SELECT code_nm FROM code WHERE parnts_code='INVN_STTUS_CODE' AND code=l.cntrct_sn)
                ELSE '' END AS cntrct_nm
                , IF(p.delng_ty_code <> '61', IFNULL(p.dlamt, 0), IFNULL(p.dlivy_amt, 0) * (100 - IFNULL(p.dscnt_rt,0) - IFNULL(p.add_dscnt_rt, 0))/100) AS amount
                , CASE WHEN l.stock_sttus = 1 THEN IF(p.dlivy_amt IS NULL, p.dlamt, IFNULL(p.dlivy_amt, 0) * (100 - IFNULL(p.dscnt_rt,0) - IFNULL(p.add_dscnt_rt, 0))/100)
				WHEN l.stock_sttus = 2 THEN IF(p.dlivy_amt IS NULL, IFNULL(p.dlamt, 0), IFNULL(p.dlivy_amt, 0) * (100 - IFNULL(p.dscnt_rt,0) - IFNULL(p.add_dscnt_rt, 0))/100)
				ELSE 0
				END AS damt
				, CASE WHEN l.stock_sttus = 3 THEN IFNULL(s.dlamt, 0)
				ELSE 0
				END AS samt
				FROM stock_log l
				LEFT OUTER JOIN
				(SELECT * FROM account WHERE delng_se_code='P') p ON l.delng_sn=p.delng_sn
				LEFT OUTER JOIN
				(SELECT * FROM account WHERE delng_se_code='S') s ON s.cnnc_sn=p.delng_sn
				WHERE l.stock_sn=%(s_stock_sn)s    """
    if "approval_sn" in params:
        query += """ AND l.reg_dtm < (SELECT IFNULL(MAX(update_dtm), (SELECT reg_dtm FROM approval WHERE approval_sn=%(approval_sn)s)) FROM approval_member WHERE approval_sn=%(approval_sn)s GROUP BY approval_sn) """
    query += """				
				ORDER BY l.ddt_man ASC, l.log_sn ASC
    """
    g.curs.execute(query, params)
    result = g.curs.fetchall()
    return result

def get_stock_by_account(delng_sn, isReturn=True, isOut=False):
    query = """SELECT x.stock_sn, x.log_sn
                FROM stock_log x """
    if isOut:
        query += """ INNER JOIN (SELECT stock_sn, MAX(log_sn) AS m_log_sn FROM stock_log GROUP BY stock_sn) y ON x.stock_sn=y.stock_sn AND x.log_sn=y.m_log_sn"""
    query += " WHERE x.delng_sn=%s"
    if isReturn:
        query += """ AND x.stock_sttus=2 """
    g.curs.execute(query, delng_sn)
    result = g.curs.fetchall()
    return result
def get_stock_list(params, prduct_se_code, reserved=False):
    query = """SELECT '1' AS ctmmny_sn
                , m.stock_sttus AS etc2
                , s.stock_sn AS value
                , s.model_no AS name
                , s.prduct_se_code AS se
                , s.prduct_ty_code AS ty
                , s.use_type AS use_type
                , m.cntrct_sn AS item_sttus_code
                , IF(m.stock_sttus=1, mi.ddt_man, '') AS dlivy_de
                , (SELECT code_nm FROM code WHERE parnts_code='INVN_STTUS_CODE' AND code=m.cntrct_sn) AS etc3
                , IF(m.stock_sttus=1, (SELECT ct.spt_nm FROM contract ct WHERE ct.cntrct_sn=mi.cntrct_sn), '') AS etc4
                FROM stock s
				LEFT OUTER JOIN 
				(SELECT x.* FROM stock_log x INNER JOIN (SELECT stock_sn, MAX(log_sn) AS m_log_sn FROM stock_log GROUP BY stock_sn) y ON x.stock_sn=y.stock_sn AND x.log_sn=y.m_log_sn) m ON s.stock_sn=m.stock_sn
				LEFT OUTER JOIN
				stock_log mi ON m.cnnc_sn=mi.log_sn
				WHERE 1=1
				AND m.stock_sttus=1
			"""
    if prduct_se_code is not None:
        query += " AND s.prduct_se_code=%s "
        data = [prduct_se_code]
    else:
        data = []

    if reserved:
        query += "AND (s.rm LIKE %s) IS NOT TRUE"
        data.append("%예약%")
    query +="""
				ORDER BY name, etc4, dlivy_de
            """
    g.curs.execute(query, data)
    result = g.curs.fetchall()
    return result

def get_out_list(params):
    query = """SELECT s.stock_sn AS item_sn
                , s.model_no
                , sa.dlivy_de AS ddt_man
                , s.prduct_se_code AS prduct_se_code
                , (SELECT code_nm FROM code WHERE parnts_code='PRDUCT_SSE_CODE' AND code=s.prduct_se_code) AS prduct_se_nm 
                , s.prduct_ty_code AS prduct_ty_code
                , (SELECT code_nm FROM code WHERE parnts_code='PRDUCT_TY_CODE' AND code=s.prduct_ty_code) AS prduct_ty_nm 
                FROM stock s 
				INNER JOIN 
				(SELECT x.* FROM stock_log x INNER JOIN (SELECT stock_sn, MAX(log_sn) AS m_log_sn FROM stock_log GROUP BY stock_sn) y ON x.stock_sn=y.stock_sn AND x.log_sn=y.m_log_sn) m ON s.stock_sn=m.stock_sn
                LEFT OUTER JOIN
				(SELECT * FROM account WHERE delng_se_code='P') p ON m.delng_sn=p.delng_sn
                LEFT OUTER JOIN
				(SELECT * FROM account WHERE delng_se_code='S') sa ON p.delng_sn=sa.cnnc_sn
				WHERE 1=1
				AND m.cntrct_sn = %(s_cntrct_sn)s
				AND m.stock_sttus = 2
				AND p.ddt_man IS NOT NULL 
				ORDER BY sa.dlivy_de
            """
    g.curs.execute(query, params)
    result = g.curs.fetchall()
    return result

def insert_stock(params, use_flag):
    if params['use_type'] == '':
        params['use_type'] = None
    if "rm" not in params:
        params["rm"] = None
    elif params["rm"] == "":
        params["rm"] = None
    params["use_flag"] = use_flag
    query = "INSERT INTO stock(prduct_se_code, prduct_ty_code, model_no, use_type, use_flag, rm) VALUES (%(prduct_se_code)s, %(prduct_ty_code)s, %(model_no)s, %(use_type)s, %(use_flag)s, %(rm)s)"
    g.curs.execute(query, params)
    return g.curs.lastrowid


def insert_log(stock_sn, stock_sttus, cntrct_sn, delng_sn, ddt_man):
    query = "SELECT x.log_sn AS log_sn FROM stock_log x INNER JOIN (SELECT stock_sn, MAX(log_sn) AS m_log_sn FROM stock_log GROUP BY stock_sn) y ON x.stock_sn=y.stock_sn AND x.log_sn=y.m_log_sn WHERE x.stock_sn=%s"
    g.curs.execute(query, stock_sn)
    row = g.curs.fetchone()
    if row:
        cnnc_sn = row['log_sn']
    else:
        cnnc_sn = None
    g.curs.execute("INSERT INTO stock_log(stock_sn, stock_sttus, cntrct_sn, delng_sn, ddt_man, cnnc_sn) VALUES (%s, %s, %s, %s, %s, %s)", (stock_sn, stock_sttus, cntrct_sn, delng_sn, ddt_man, cnnc_sn))

def update_stock_rm(stock_sn, rm):
    g.curs.execute("UPDATE stock SET rm=%s WHERE stock_sn=%s", (rm, stock_sn))

def update_stock_type(stock_sn, type):
    g.curs.execute("UPDATE stock SET use_type=%s WHERE stock_sn=%s", (type, stock_sn))

def get_stock_report_list(params):
    query = """SELECT prduct_se_code
                    , prduct_se_nm
                    , prduct_ty_code
                    , prduct_ty_nm
                    , SUM(IF(invn_sttus_nm='전시', 1, 0)) AS cnt1
                    , SUM(IF(invn_sttus_nm='이현창고', 1, 0)) AS cnt2
                    , SUM(IF(invn_sttus_nm='기타창고', 1, 0)) AS cnt3
                    FROM
                    (SELECT prduct_se_code AS prduct_se_code
    				, (SELECT code_nm FROM code WHERE parnts_code='PRDUCT_SSE_CODE' AND code=s.prduct_se_code) AS prduct_se_nm
    				, prduct_ty_code AS prduct_ty_code
    				, (SELECT code_nm FROM code WHERE parnts_code='PRDUCT_TY_CODE' AND code=s.prduct_ty_code) AS prduct_ty_nm
    				, CASE WHEN m.stock_sttus=1 THEN (SELECT code_nm FROM code WHERE parnts_code='INVN_STTUS_CODE' AND code=m.cntrct_sn)
    				WHEN m.stock_sttus IN (2,3) THEN (SELECT code_nm FROM code WHERE parnts_code='INVN_STTUS_CODE' AND code=(m.stock_sttus-2))
    				ELSE (SELECT code_nm FROM code WHERE parnts_code='INVN_STTUS_CODE' AND code=m.stock_sttus)
    				END AS invn_sttus_nm
    				FROM (SELECT * FROM stock WHERE 1=1) s 
    				INNER JOIN 
    				(SELECT x.* FROM stock_log x INNER JOIN (SELECT stock_sn, MAX(log_sn) AS m_log_sn FROM stock_log GROUP BY stock_sn) y ON x.stock_sn=y.stock_sn AND x.log_sn=y.m_log_sn) m ON s.stock_sn=m.stock_sn
    				INNER JOIN
    				(SELECT x.* FROM stock_log x INNER JOIN (SELECT stock_sn, MIN(log_sn) AS m_log_sn FROM stock_log GROUP BY stock_sn) y ON x.stock_sn=y.stock_sn AND x.log_sn=y.m_log_sn) mi ON s.stock_sn=mi.stock_sn
    				INNER JOIN
    				(SELECT * FROM account WHERE delng_se_code='P') p ON mi.delng_sn=p.delng_sn
    				INNER JOIN
    				(SELECT * FROM account WHERE delng_se_code='S') sa ON sa.cnnc_sn=p.delng_sn
    				WHERE 1=1) t
    				GROUP BY prduct_se_code, prduct_ty_code
    				ORDER BY prduct_se_code, prduct_ty_code
    				"""
    g.curs.execute(query)
    result = g.curs.fetchall()
    return result
def get_stock_report(params):
    query = """SELECT prduct_se_code
                    , prduct_se_nm
                    , SUM(puchas_amount_one) AS puchas_amount
                    , SUM(qy) AS qy_total
                    , invn_sttus_nm
                    FROM
                    (SELECT prduct_se_code AS prduct_se_code
    				, (SELECT code_nm FROM code WHERE parnts_code='PRDUCT_SSE_CODE' AND code=s.prduct_se_code) AS prduct_se_nm
    				, CASE WHEN mi.stock_sttus = 1 THEN IF(p.dlivy_amt IS NULL, p.dlamt, IFNULL(p.dlivy_amt, 0) * (100 - IFNULL(p.dscnt_rt,0) - IFNULL(p.add_dscnt_rt, 0))/100)
                        WHEN mi.stock_sttus = 2 THEN IF(p.dlivy_amt IS NULL, IFNULL(p.dlamt, 0), IFNULL(p.dlivy_amt, 0) * (100 - IFNULL(p.dscnt_rt,0) - IFNULL(p.add_dscnt_rt, 0))/100)
                        ELSE 0
                        END AS puchas_amount_one
                    , 1 AS qy
    				, CASE WHEN m.stock_sttus=1 THEN (SELECT code_nm FROM code WHERE parnts_code='INVN_STTUS_CODE' AND code=m.cntrct_sn)
    				WHEN m.stock_sttus IN (2,3) THEN (SELECT code_nm FROM code WHERE parnts_code='INVN_STTUS_CODE' AND code=(m.stock_sttus-2))
    				ELSE (SELECT code_nm FROM code WHERE parnts_code='INVN_STTUS_CODE' AND code=m.stock_sttus)
    				END AS invn_sttus_nm
    				FROM (SELECT * FROM stock WHERE 1=1) s 
    				INNER JOIN 
    				(SELECT x.* FROM stock_log x INNER JOIN (SELECT stock_sn, MAX(log_sn) AS m_log_sn FROM stock_log GROUP BY stock_sn) y ON x.stock_sn=y.stock_sn AND x.log_sn=y.m_log_sn) m ON s.stock_sn=m.stock_sn
    				INNER JOIN
    				(SELECT x.* FROM stock_log x INNER JOIN (SELECT stock_sn, MIN(log_sn) AS m_log_sn FROM stock_log GROUP BY stock_sn) y ON x.stock_sn=y.stock_sn AND x.log_sn=y.m_log_sn) mi ON s.stock_sn=mi.stock_sn
    				INNER JOIN
    				(SELECT * FROM account WHERE delng_se_code='P') p ON mi.delng_sn=p.delng_sn
    				INNER JOIN
    				(SELECT * FROM account WHERE delng_se_code='S') sa ON sa.cnnc_sn=p.delng_sn
    				WHERE 1=1) t
    				WHERE t.invn_sttus_nm IN ('전시', '이현창고', '기타창고')
    				GROUP BY prduct_se_code, prduct_se_nm, invn_sttus_nm
    				"""
    g.curs.execute(query)
    result = g.curs.fetchall()
    return result

def get_built_month(params):
    params['stdyy'] = params['s_ddt_man'].split("-")[0]
    query = """SELECT stdyy
                    , stdmm
                    , cnt_new
                    , cnt_out_all
                    , cnt_in_1
                    , cnt_not_in_1
                    , cnt_remain_1
                    , cnt_in_2
                    , cnt_not_in_2
                    , cnt_remain_2
                    FROM bnd_table
                    WHERE stdyy=%(stdyy)s
                    ORDER BY stdmm ASC"""
    g.curs.execute(query, params)
    result = g.curs.fetchall()
    return result
def get_built_month_sales(params):
    params['stdyy'] = params['s_ddt_man'].split("-")[0]
    query = """SELECT YEAR(ddt_man) AS stdyy
                    , MONTH(ddt_man) AS stdmm
                    , SUM(IF(sale_type = 0, dlnt, 0)) AS cnt1
                    , ROUND(SUM(IF(sale_type = 0, dlnt*dlamt, 0))) AS amt1
                    , SUM(IF(sale_type = 1, dlnt, 0)) AS cnt2
                    , ROUND(SUM(IF(sale_type = 1, dlnt*dlamt, 0))) AS amt2
                    , SUM(IF(sale_type = 2, dlnt, 0)) AS cnt3
                    , ROUND(SUM(IF(sale_type = 2, dlnt*dlamt, 0))) AS amt3
                    , SUM(IF(sale_type = 3, dlnt, 0)) AS cnt4
                    , ROUND(SUM(IF(sale_type = 3, dlnt*dlamt, 0))) AS amt4
                    , SUM(IF(sale_type = 4, dlnt, 0)) AS cnt5
                    , ROUND(SUM(IF(sale_type = 4, dlnt*dlamt, 0))) AS amt5
                    FROM bnd_sales_table_log
                    WHERE YEAR(ddt_man)=%(stdyy)s
                    GROUP BY YEAR(ddt_man), MONTH(ddt_man)
                    ORDER BY stdmm ASC"""
    g.curs.execute(query, params)
    result = g.curs.fetchall()
    return result
def get_stock_month(params):
    params['stdyy'] = params['s_ddt_man'].split("-")[0]
    params['last'] = int(params['s_ddt_man'].split("-")[0]) - 1
    query = """SELECT stdyy
                    , IF(stdyy=%(last)s, 0, stdmm) AS stdmm """

    for i in range(1, 8):
        query += " , cnt{} ".format(i)

    query +=    """ FROM bnd_stock_table
                    WHERE (stdyy=%(stdyy)s OR (stdyy=%(last)s AND stdmm=12))
                    AND invn_type=%(invn_type)s """

    query +=    """ ORDER BY stdmm ASC"""
    g.curs.execute(query, params)
    result = g.curs.fetchall()
    return result

def delete_stock_log(params):
    query = """SELECT log_sn, cnnc_sn FROM stock_log WHERE stock_sn=%(s_stock_sn)s ORDER BY log_sn DESC"""
    g.curs.execute(query, params)
    result = g.curs.fetchall(transform=False)
    if result:
        log_sn = result[0]['log_sn']
        cnnc_sn = result[0]['cnnc_sn']
        if cnnc_sn is None:
            g.curs.execute("DELETE FROM stock WHERE stock_sn=%(s_stock_sn)s", params)
        g.curs.execute("DELETE FROM stock_log WHERE log_sn=%s", log_sn)
