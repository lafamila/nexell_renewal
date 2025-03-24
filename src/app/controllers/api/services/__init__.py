from flask import session
from app.connectors import DB
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from pytz import timezone
import requests


def refresh_code_list():
    def wrapper(**params):
        return params

    return wrapper(selng_ty_code_list=get_code_list('selng_ty_code'.upper()),
                prdlst_se_code_list=get_code_list('prdlst_se_code'.upper()),
                dept_code_list=get_code_list('dept_code'.upper()),
                card_code_list=get_code_list('card_code'.upper()),
                puchas_ty_code_list=get_code_list('ct_se_code'.upper()),
                delng_se_code_list=get_code_list('delng_se_code'.upper()),
                ofcps_code_list=get_code_list('ofcps_code'.upper()),
                rspofc_code_list=get_code_list('rspofc_code'.upper()),
                prjct_ty_code_list=get_code_list('prjct_ty_code'.upper()),
                progrs_sttus_code_list=get_code_list('progrs_sttus_code'.upper()),
                approval_se_code_list=get_code_list('approval_se_code'.upper()),
                approval_ty_code_list=get_code_list('approval_ty_code'.upper()),
                approval_tty_code_list=get_code_list('approval_tty_code'.upper()),
                mber_sttus_code_list=get_code_list('mber_sttus_code'.upper()),
                acntctgr_code_list=get_code_list('acntctgr_code'.upper()),
                rcppay_se_code_list=get_code_list('rcppay_se_code'.upper()),
                acnut_code_list=get_code_list('acnut_code'.upper()),
                bsnm_se_code_list=get_code_list('bsnm_se_code'.upper()),
                bcnc_se_code_list=get_code_list('bcnc_se_code'.upper()),
                ct_se_code_list=get_code_list('ct_se_code'.upper()),
                cntrct_execut_code_list=get_code_list('cntrct_execut_code'.upper()),
                dspy_se_code_list=get_code_list('dspy_se_code'.upper()),
                author_list=get_author_list(),
                bcnc_list=get_bcnc_list(),
                member_list=get_member_list(),
                member_all_list=get_member_all_list(),
                prduct_ty_code_list=get_code_list('prduct_ty_code'.upper()),
                prduct_sse_code_list=get_code_list('prduct_sse_code'.upper()),
                invn_sttus_code_list=get_code_list('invn_sttus_code'.upper()),
                inventory_list=get_inventory_name_list(),
                contract_list=get_contract_list(),
                contract_all_list=get_contract_all_list(),
                contract_nr_list=get_contract_NR_list(),
                amt_ty_code_list=get_code_list('amt_ty_code'.upper()),
                exp_se_code_list=get_code_list('exp_se_code'.upper()),
                exp_ty_code_list=get_code_list('exp_ty_code'.upper()),
                menu_total_list=get_menu_total_list(),
                menus=set_menu(session['member']['auth_cd']) if 'member' in session else None)


def get_menu_total_list():
    db = DB()
    curs = db.cursor()
    curs.execute("""SELECT menu_sn
                        , menu_nm
                        , parnts_menu_sn
                        , menu_icon
                        , menu_level
                        , menu_ordr
                        FROM menu WHERE use_at='Y'
                        ORDER BY menu_level, parnts_menu_sn, menu_ordr""")

    result = curs.fetchall()
    total_menus = {}
    for r in result:
        if int(r['parnts_menu_sn']) == 0:
            total_menus[int(r['menu_sn'])] = [r, []]
        else:
            total_menus[int(r['parnts_menu_sn'])][1].append(r)
    curs.close()
    db.close()
    return total_menus

def get_approval_ty_code_by_sn(params):
    db = DB()
    curs = db.cursor()
    curs.execute("""SELECT approval_sn
                        , approval_ty_code
                        , approval_title
                        , approval_data
                        FROM approval WHERE approval_sn=%(approval_sn)s""", params)
    result = curs.fetchone()
    curs.close()
    db.close()
    return result

def get_approval_by_sn(params):
    db = DB()
    curs = db.cursor()
    curs.execute("""SELECT code_nm AS title
                        , estn_code_b AS url
                        , estn_code_c AS ajax_url
                        , code AS approval_ty_code
                        FROM code WHERE parnts_code='APPROVAL_TY_CODE' AND code=%(approval_ty_code)s""", params)
    result = curs.fetchone()
    curs.close()
    db.close()
    return result

def get_member_list_by_sn():
    db = DB()
    curs = db.cursor()
    curs.execute("""SELECT m.mber_sn AS mber_sn
                    , m.mber_nm AS mber_nm
                    , (SELECT code_nm FROM code WHERE parnts_code='OFCPS_CODE' AND code=m.ofcps_code) AS ofcps_nm                
                    , IF(f.file_path IS NULL, 'signature.jpg', f.file_path) AS sign_path
                    FROM member m
                    LEFT OUTER JOIN files f
                    ON f.f_sn=m.sign_file_sn
                    WHERE 1=1 """)
    result = curs.fetchall()
    curs.close()
    db.close()
    return {r['mber_sn'] : r for r in result}

def get_contract_all_list():
    db = DB()
    curs = db.cursor()
    curs.execute("""SELECT cntrct_sn AS value
    				, cntrct_nm AS label
    				, cntrct_no AS etc1
    				, cntrct_de AS etc2
    				, CONCAT(
    				cntrct_no, '.',
    				cntrct_nm, '.',
    				cntrct_de
    				) AS etc3
    				, (SELECT bcnc_nm FROM bcnc WHERE bcnc_sn=c.bcnc_sn) AS bcnc_nm
    				, biss_a
    				, prjct_creat_at
    				, (SELECT COUNT(prjct_sn) FROM project WHERE cntrct_sn=c.cntrct_sn) AS prjct_cnt
    				, c.spt_chrg_sn
    				, c.bsn_chrg_sn
    				FROM contract c
    				WHERE 1=1
    				AND ctmmny_sn = 1
                    """)
    result = curs.fetchall()
    curs.close()
    db.close()
    return result


def get_contract_list():
    db = DB()
    curs = db.cursor()
    curs.execute("""SELECT cntrct_sn AS value
				, cntrct_nm AS label
				, cntrct_no AS etc1
				, cntrct_de AS etc2
				, CONCAT(
				cntrct_no, '.',
				cntrct_nm, '.',
				cntrct_de
				) AS etc3
				, (SELECT bcnc_nm FROM bcnc WHERE bcnc_sn=c.bcnc_sn) AS bcnc_nm
				, biss_a
				, prjct_creat_at
				, (SELECT COUNT(prjct_sn) FROM project WHERE cntrct_sn=c.cntrct_sn) AS prjct_cnt
				, c.spt_chrg_sn
				, c.bsn_chrg_sn
				FROM contract c
				WHERE 1=1
				AND ctmmny_sn = 1
				AND progrs_sttus_code IN ('B', 'P', 'N', 'S')
                """)
    result = curs.fetchall()
    curs.close()
    db.close()
    return result

def get_contract_NR_list():
    db = DB()
    curs = db.cursor()
    curs.execute("""SELECT cntrct_sn AS value
				, cntrct_nm AS label
				, cntrct_no AS etc1
				, cntrct_de AS etc2
				, CONCAT(
				cntrct_no, '.',
				cntrct_nm, '.',
				cntrct_de
				) AS etc3
				, (SELECT bcnc_nm FROM bcnc WHERE bcnc_sn=c.bcnc_sn) AS bcnc_nm
				, prjct_creat_at
				, (SELECT COUNT(prjct_sn) FROM project WHERE cntrct_sn=c.cntrct_sn) AS prjct_cnt
				, c.spt_chrg_sn
				, c.bsn_chrg_sn
				FROM contract c
				WHERE 1=1
				AND c.prjct_ty_code='NR'
				AND ctmmny_sn = 1
				AND progrs_sttus_code IN ('B', 'P', 'N', 'S')
                """)
    result = curs.fetchall()
    curs.close()
    db.close()
    return result

def get_inventory_name_list():
    db = DB()
    curs = db.cursor()
    curs.execute("""SELECT code AS value
                    , code_nm AS label
                    FROM code
                    WHERE 1=1
                    AND ctmmny_sn=1
                    AND use_at = 'Y'
                    AND parnts_code = 'INVN_STTUS_CODE'
                    AND code > '1'
                    AND code <> '4'
                    """)
    result = curs.fetchall()
    curs.close()
    db.close()
    return result

def get_member_list():
    db = DB()
    curs = db.cursor()
    curs.execute("""SELECT m.mber_sn AS value
				, m.mber_nm AS label
				, (SELECT code_nm FROM code WHERE parnts_code='OFCPS_CODE' AND code=m.ofcps_code) AS etc1
				, (SELECT code_nm FROM code WHERE parnts_code='DEPT_CODE' AND code=m.dept_code) AS etc2
				, m.dept_code AS dept_code
				, CONCAT( IFNULL((SELECT code_nm FROM code WHERE parnts_code='DEPT_CODE' AND code=m.dept_code),''), ' '
				, m.mber_nm, ' '
				, IFNULL((SELECT code_nm FROM code WHERE parnts_code='OFCPS_CODE' AND code=m.ofcps_code),'')
				) AS etc3
				FROM member m
				WHERE 1=1
				AND ctmmny_sn = 1
				AND mber_sttus_code = 'H'
				AND dept_code != ''
				ORDER BY mber_nm""")
    result = curs.fetchall()
    # 				AND mber_sn NOT IN (74, 81, 82, 44, 27, 54)
    curs.close()
    db.close()
    return result

def get_member_all_list():
    db = DB()
    curs = db.cursor()
    curs.execute("""SELECT m.mber_sn AS value
				, m.mber_nm AS label
				, (SELECT code_nm FROM code WHERE parnts_code='OFCPS_CODE' AND code=m.ofcps_code) AS etc1
				, (SELECT code_nm FROM code WHERE parnts_code='DEPT_CODE' AND code=m.dept_code) AS etc2
				, CONCAT( IFNULL((SELECT code_nm FROM code WHERE parnts_code='DEPT_CODE' AND code=m.dept_code),''), ' '
				, m.mber_nm, ' '
				, IFNULL((SELECT code_nm FROM code WHERE parnts_code='OFCPS_CODE' AND code=m.ofcps_code),'')
				) AS etc3
				FROM member m
				WHERE 1=1
				AND ctmmny_sn = 1
				AND mber_sttus_code = 'H'
				AND dept_code != ''
				ORDER BY mber_nm""")
    result = curs.fetchall()
    curs.close()
    db.close()
    return result


def get_bcnc_list():
    db = DB()
    curs = db.cursor()
    curs.execute("""SELECT bcnc_sn AS value
				, bcnc_nm AS label
				, bizrno AS et1
				FROM bcnc
				WHERE 1=1
				AND ctmmny_sn = 1
				AND use_at = 'Y'
                """)
    result = curs.fetchall()
    curs.close()
    db.close()
    return result


def get_author_list():
    db = DB()
    curs = db.cursor()
    curs.execute("""SELECT author_sn AS value
				, author_nm AS label
				FROM author
				WHERE 1=1
				AND ctmmny_sn = 1
				AND use_at = 'Y'    
				ORDER BY ORDR ASC
                """)
    result = curs.fetchall()
    curs.close()
    db.close()
    return result


def get_code_list(parnts_code):
    db = DB()
    curs = db.cursor()
    curs.execute("""SELECT c.parnts_code
                        , c.code AS value
                        , c.code_nm AS label
                        , c.estn_code_a AS etc1
                        , c.estn_code_b AS etc2
                        , c.estn_code_c AS etc3
                        , c.code_ordr
                        FROM code c
                        WHERE 1=1
                        AND ctmmny_sn = 1
                        AND c.parnts_code = %s
                        AND c.use_at = 'Y'
                        ORDER BY c.code_ordr, c.code_nm
                """, parnts_code)
    result = curs.fetchall()
    curs.close()
    db.close()
    return result

def set_menu(auth_cd):
    db = DB()
    curs = db.cursor()

    #########################
    # auto handler check    #
    #########################
    now = datetime.now(timezone('Asia/Seoul')) - relativedelta(months=1)
    before = datetime.now(timezone('Asia/Seoul')) - relativedelta(months=2)
    last_day = datetime.strptime(datetime.now(timezone('Asia/Seoul')).strftime("%Y-%m-01"), "%Y-%m-%d") + timedelta(days=-1)

    y, m = now.strftime("%Y-%m").split("-")
    st, ed = now.strftime("%Y-%m-01"), now.strftime("%Y-%m-31")
    before_y, before_m = before.strftime("%Y-%m").split("-")
    row = curs.execute("SELECT * FROM bnd_table WHERE stdyy=%s AND stdmm=%s", (y, m))
    if not row:
        query = "SELECT IFNULL(count(distinct c.cntrct_sn), 0) as cnt FROM account s LEFT JOIN contract c ON s.cntrct_sn=c.cntrct_sn LEFT JOIN member m ON c.bsn_chrg_sn=m.mber_sn WHERE 1=1 AND m.dept_code='BI' AND s.delng_se_code='S' AND s.delng_ty_code='13' AND ddt_man BETWEEN '{} 00:00:00' AND '{} 23:59:59'".format(st, ed)
        curs.execute(query)
        result = curs.fetchone()
        cnt_new = result['cnt']
        query = """SELECT distinct c.spt_nm FROM stock_log x INNER JOIN (SELECT stock_sn, MAX(log_sn) AS m_log_sn FROM stock_log GROUP BY stock_sn) y ON x.stock_sn=y.stock_sn AND x.log_sn=y.m_log_sn LEFT JOIN stock s ON x.stock_sn=s.stock_sn LEFT OUTER JOIN contract c ON x.cntrct_sn=c.cntrct_sn
                LEFT OUTER JOIN
				(SELECT * FROM account WHERE delng_se_code='P') p_last ON x.delng_sn=p_last.delng_sn
				LEFT OUTER JOIN
				(SELECT * FROM account WHERE delng_se_code='S') sa_last ON sa_last.cnnc_sn=p_last.delng_sn
WHERE 1=1 AND prduct_se_code='2' AND x.stock_sttus=2 AND IF(x.stock_sttus IN (1, 4), x.ddt_man, sa_last.dlivy_de) IS NOT NULL"""
        curs.execute(query)
        result = curs.fetchall()
        cnt_out_all = len(result)
        query = "SELECT COUNT(distinct c.cntrct_sn) AS cnt FROM taxbil t LEFT JOIN contract c ON t.cntrct_sn=c.cntrct_sn LEFT JOIN member m ON c.BSN_CHRG_SN=m.mber_sn WHERE m.dept_code='BI' AND  t.delng_se_code IN ('S2', 'S4') AND t.PBLICTE_DE BETWEEN %(st)s AND %(ed)s"
        curs.execute(query, {"st": st, "ed": ed})
        result = curs.fetchone()
        cnt_in_1 = result['cnt']
        query = "SELECT COUNT(distinct c.cntrct_sn) AS cnt FROM taxbil t LEFT JOIN contract c ON t.cntrct_sn=c.cntrct_sn LEFT JOIN member m ON c.BSN_CHRG_SN=m.mber_sn WHERE m.dept_code='BI' AND c.PRJCT_CREAT_AT='Y' AND t.delng_se_code IN ('S', 'S1') AND t.PBLICTE_DE BETWEEN %(st)s AND %(ed)s"
        curs.execute(query, {"st": st, "ed": ed})
        result = curs.fetchone()
        cnt_in_2 = result['cnt']


        params = {'bnd_year': last_day.year, 'm_dlivy_de_start': '', 'm_dlivy_de_end': '', 'm_pblict_de_start': '', 'm_pblict_de_end': '', 's_dlivy_de_start': '', 's_dlivy_de_end': '', 's_pblict_de_start': '', 's_pblict_de_end': '', 't_pblict_de_start': '', 't_pblict_de_end': ''}
        res = requests.get("http://localhost:5001/api/bnd/ajax_get_bnd",
                           params=params)
        result = res.json()
        cnt_1 = 0
        remain_1 = 0
        cnt_2 = 0
        remain_2 = 0
        expect = {str(_['cntrct_sn']): (datetime.strptime(_['expect_de'], "%y/%m/%d"), _['progrs_order'] in (1, 3)) for
                  _ in result['data'] if _['expect_de'] != ''}
        for cntrct_sn, pRow in result['taxbill'].items():
            mTotal = sum([_[1] for _ in pRow['M']])
            sTotal = sum([_[1] for _ in pRow['S']])
            tTotal = sum([_[1] for _ in pRow['T']])
            rcppay = result['rcppay'].get(cntrct_sn, {'M': 0, 'S': 0, 'T': 0})
            mRemain, sRemain = round((int(rcppay['M']) - int(mTotal)) / 1000), round(
                (int(rcppay['S']) - int(sTotal)) / 1000)
            if mRemain >= 10 or sRemain >= 10:
                cnt_1 += 1
                remain_1 += mRemain if mRemain >= 10 else 0
                remain_1 += sRemain if sRemain >= 10 else 0

            tRemain = round((int(rcppay['T']) - int(tTotal)) / 1000)
            if cntrct_sn in expect:
                if last_day >= expect[cntrct_sn][0] and expect[cntrct_sn][1] and tRemain > 0:
                    cnt_2 += 1
                    remain_2 += tRemain
        for cntrct_sn, pRow in result['rcppay'].items():
            if cntrct_sn not in result['taxbill']:
                mRemain, sRemain = round(int(pRow['M']) / 1000), round(int(pRow['S']) / 1000)
                if mRemain >= 10 or sRemain >= 10:
                    cnt_1 += 1
                    remain_1 += mRemain if mRemain >= 10 else 0
                    remain_1 += sRemain if sRemain >= 10 else 0
                tRemain = round(int(rcppay['T']) / 1000)
                if last_day >= expect[cntrct_sn][0] and expect[cntrct_sn][1] and tRemain > 0:
                    cnt_2 += 1
                    remain_2 += tRemain

        # TODO: cnt_not_in_1, cnt_remain_1, cnt_not_in_2, cnt_remain_2
        # TODO: insert
        curs.execute(
            "INSERT INTO bnd_table(stdyy, stdmm, cnt_new, cnt_out_all, cnt_in_1, cnt_not_in_1, cnt_remain_1, cnt_in_2, cnt_not_in_2, cnt_remain_2) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
            (last_day.year, last_day.month, cnt_new, cnt_out_all, cnt_in_1, cnt_1, remain_1, cnt_in_2, cnt_2, remain_2))
        db.commit()

    row = curs.execute("SELECT * FROM bnd_stock_table WHERE stdyy=%s AND stdmm=%s", (y, m))
    if not row:
        queries = """SELECT IFNULL(COUNT(*), 0) AS cnt FROM stock_log ss LEFT JOIN stock s ON ss.stock_sn=s.stock_sn WHERE ss.stock_sttus='1' AND s.PRDUCT_SE_CODE='2' AND ddt_man BETWEEN %(st)s AND %(ed)s
    SELECT IFNULL(COUNT(*), 0) AS cnt  FROM stock_log ss LEFT JOIN stock s ON ss.stock_sn=s.stock_sn WHERE ss.stock_sttus='2' AND s.PRDUCT_SE_CODE='2' AND ss.CNNC_SN IS NOT NULL AND ddt_man BETWEEN %(st)s AND %(ed)s
    SELECT IFNULL(COUNT(*), 0) AS cnt  FROM stock_log ss LEFT JOIN stock s ON ss.stock_sn=s.stock_sn WHERE ss.stock_sttus='3' AND s.PRDUCT_SE_CODE='2' AND ddt_man BETWEEN %(st)s AND %(ed)s
    SELECT IFNULL(COUNT(*), 0) AS cnt  FROM stock_log ss LEFT JOIN stock s ON ss.stock_sn=s.stock_sn WHERE ss.stock_sttus='4' AND s.PRDUCT_SE_CODE='2' AND ddt_man BETWEEN %(st)s AND %(ed)s""".split("\n")
        results = dict()
        for i, query in enumerate(queries):
            curs.execute(query.strip(), {"st": st, "ed": ed})
            result = curs.fetchone()
            cnt = result['cnt']
            results[f"cnt{i}"] = cnt
        curs.execute("SELECT IFNULL(s.use_type, '') AS use_type, count(*) AS cnt FROM stock_log x INNER JOIN (SELECT stock_sn, MAX(log_sn) AS m_log_sn FROM stock_log GROUP BY stock_sn) y ON x.stock_sn=y.stock_sn AND x.log_sn=y.m_log_sn  LEFT JOIN stock s ON x.stock_sn=s.stock_sn WHERE x.stock_sttus='1' AND s.PRDUCT_SE_CODE='2' GROUP BY s.use_type")
        result = curs.fetchall()
        for r in result:
            if r['use_type'] != '':
                results[r['use_type']] = r['cnt']

        for t in ("빌트인", "일반", "자재"):
            if t not in results:
                results[t] = 0
        curs.execute("INSERT INTO bnd_stock_table(stdyy, stdmm, invn_type, cnt1, cnt2, cnt3, cnt4, cnt5, cnt6, cnt7) VALUES (%s, %s, 0, %s, %s, %s, %s, %s, %s, %s)", (y, m, results["cnt0"], results["cnt1"], results["cnt2"], results["cnt3"], results["빌트인"], results["일반"], results["자재"]))

        curs.execute("SELECT * FROM bnd_stock_table WHERE stdyy=%s AND stdmm=%s AND invn_type IN (1, 2)", (before_y, before_m))
        result = curs.fetchall()
        result_before = {int(r['invn_type']):r for r in result}

        query = """SELECT ss.cntrct_sn, IF(s.prduct_ty_code IN (1, 2), s.prduct_ty_code, 3) AS prduct_ty_code, COUNT(*) AS cnt FROM stock_log ss LEFT OUTER JOIN stock_log ls ON ls.cnnc_sn=ss.log_sn LEFT JOIN stock s ON ss.stock_sn=s.stock_sn WHERE ss.stock_sttus='1' AND s.PRDUCT_SE_CODE='1' AND (ls.LOG_SN IS NULL OR ls.STOCK_STTUS <> '4') AND ss.ddt_man BETWEEN %(st)s AND %(ed)s GROUP BY ss.cntrct_sn, IF(s.prduct_ty_code IN (1, 2), s.prduct_ty_code, 3)"""
        curs.execute(query.strip(), {"st": st, "ed" : ed})
        result = curs.fetchall()
        data_in = {2: 0, 3: 0}
        for r in result:
            data_in[int(r['cntrct_sn'])] += r['cnt']
            result_before[int(r['cntrct_sn'])-1]['cnt{}'.format(int(r['prduct_ty_code'])+4)] += r['cnt']

        query = """SELECT ss.stock_sttus, IF(s.prduct_ty_code IN (1, 2), s.prduct_ty_code, 3) AS prduct_ty_code, ls.cntrct_sn, COUNT(*) AS cnt FROM stock_log ss LEFT OUTER JOIN stock_log ls ON ls.log_sn=ss.cnnc_sn LEFT JOIN stock s ON ss.stock_sn=s.stock_sn WHERE ss.stock_sttus IN ('2', '3') AND s.PRDUCT_SE_CODE='1' AND ls.cntrct_sn IS NOT NULL AND ss.ddt_man BETWEEN %(st)s AND %(ed)s GROUP BY ls.cntrct_sn, ss.STOCK_STTUS, IF(s.prduct_ty_code IN (1, 2), s.prduct_ty_code, 3)"""
        curs.execute(query.strip(), {"st": st, "ed" : ed})
        result = curs.fetchall()
        data_out = {2: {2: 0, 3: 0, 4: 0}, 3: {2: 0, 3: 0, 4: 0}}
        for r in result:
            data_out[int(r['cntrct_sn'])][int(r['stock_sttus'])] += r['cnt']
            result_before[int(r['cntrct_sn']) - 1]['cnt{}'.format(int(r['prduct_ty_code']) + 4)] -= r['cnt']
        for invn_type in data_in:
            curs.execute("INSERT INTO bnd_stock_table(stdyy, stdmm, invn_type, cnt1, cnt2, cnt3, cnt4, cnt5, cnt6, cnt7) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (y, m, invn_type-1, data_in[invn_type], data_out[invn_type][2], data_out[invn_type][3], data_out[invn_type][4], result_before[invn_type-1]['cnt5'], result_before[invn_type-1]['cnt6'], result_before[invn_type-1]['cnt7']))

        db.commit()


    row = curs.execute("""SELECT  s.stock_sn AS stock_sn
				FROM (SELECT * FROM stock WHERE prduct_se_code=2) s
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
                AND p.ddt_man < DATE_SUB(NOW(), INTERVAL 2 YEAR)
                AND (s.rm NOT LIKE %s or s.rm IS NULL)""", ('%장기%', ))
    if row:
        stocks = curs.fetchall()
        curs.executemany("""UPDATE stock SET rm=concat('장기 ', IFNULL(rm, '')) WHERE stock_sn=%(stock_sn)s""", stocks)
        db.commit()
    # general sales project - bcnc check

    bcnc_nm = "{}년{}월일반".format(datetime.now(timezone('Asia/Seoul')).strftime("%y"), int(datetime.now(timezone('Asia/Seoul')).strftime("%m")))
    row = curs.execute("SELECT bcnc_sn FROM bcnc WHERE bcnc_nm=%s AND bcnc_se_code='S'", bcnc_nm)
    if not row:
        curs.execute("INSERT bcnc(CTMMNY_SN, BCNC_SE_CODE, BCNC_NM, BCNC_TELNO, BCNC_ADRES, RPRSNTV_NM, BIZRNO, BSNM_SE_CODE, ESNTL_DELNG_NO, USE_AT, REGIST_DTM, REGISTER_ID) VALUES (1, 'S', %s, null, null, null, '해당사항없음', 1, null, 'Y', NOW(), 'nexelll')", bcnc_nm)
        bcnc_sn = curs.lastrowid
    else:
        bcnc_sn = curs.fetchone()['bcnc_sn']

    dept_codes = {("공조1", "TS1"): "NR", ("공조2", "TS2"): "NR", ("빌트인", "BI"): "BD"}
    now_bgn = datetime.strptime(datetime.now(timezone('Asia/Seoul')).strftime("%Y-%m-01"), "%Y-%m-%d")
    now_end = now_bgn + relativedelta(months=1) + relativedelta(days=-1)
    cntrct_nm_format = now_bgn.strftime("%y년%m월 일반판매")
    for dept_nm, dept_code in dept_codes:
        raw = curs.execute(
            "SELECT mber_sn FROM member  WHERE dept_code=%s AND mber_sttus_code='H' ORDER BY ofcps_code ASC, rspofc_code ASC",
            dept_code)
        if not raw:
            mber_sn = 66
        else:
            mber_sn = curs.fetchone()['mber_sn']

        cntrct_data = {"cntrct_nm": "{}({})".format(cntrct_nm_format, dept_nm),
                       "bgn_de": now_bgn.strftime("%Y-%m-%d"), "end_de": now_end.strftime("%Y-%m-%d"),
                       "prjct_ty_code": dept_codes[(dept_nm, dept_code)], "mber_sn": mber_sn, "bcnc_sn" : bcnc_sn}

        raw = curs.execute("SELECT * FROM contract WHERE cntrct_nm=%(cntrct_nm)s", cntrct_data)
        if not raw:
            query = """INSERT INTO contract (ctmmny_sn, cntrct_no, cntrct_nm, 
                                cntrct_de, prjct_ty_code, bcnc_sn, spt_nm, 
                                spt_adres, cntrwk_bgnde, cntrwk_endde, bsn_chrg_sn, spt_chrg_sn, prjct_creat_at,
                                progrs_sttus_code, home_count, home_region, regist_dtm, register_id)
                        values (1, '', %(cntrct_nm)s,
                                %(bgn_de)s, %(prjct_ty_code)s, %(bcnc_sn)s, %(cntrct_nm)s,
                                ' ', %(bgn_de)s, %(end_de)s, %(mber_sn)s, %(mber_sn)s, 'N',
                                'P', '1', '서울권', NOW(), 'nexelll')"""
            curs.execute(query, cntrct_data)
    db.commit()

    # # general sales project - contract & project check
    # curs.execute("SHOW COLUMNS FROM contract")
    # result = curs.fetchall()
    # total_columns = []
    # required = []
    # for r in result:
    #     key = r['Field'].lower()
    #     if r['Default'] == '' and r['Extra'] != 'auto_increment':
    #         required.append(key)
    #     if r['Extra'] != 'auto_increment':
    #         total_columns.append(key)
    #
    # data = {r.lower():None for r in required}
    #
    # data["ctmmny_sn"] = 1
    # data["regist_dtm"] = datetime.now(timezone('Asia/Seoul'))
    # data["register_id"] = 'nexell'
    # data['progrs_sttus_code'] = 'P'
    # dept_codes = ["TS1", "TS2", "BI"]
    # curs.execute("SELECT code, code_nm FROM code WHERE parnts_code='DEPT_CODE' AND code IN ({})".format(",".join(["'{}'".format(d) for d in dept_codes])))
    # code_nms = curs.fetchall()
    # DEPT_CODES = {r['code']: r['code_nm'] for r in code_nms}
    # for dept_code in dept_codes:
    #     dept_nm = DEPT_CODES[dept_code].replace("팀", "")
    #     row = curs.execute("SELECT mber_sn FROM member WHERE dept_code=%s AND mber_sttus_code='H' AND RSPOFC_CODE=150", dept_code)
    #     if not row:
    #         data['bsn_chrg_sn'] = 73
    #         data['spt_chrg_sn'] = 73
    #     else:
    #         team_leader = curs.fetchone()
    #         data['bsn_chrg_sn'] = team_leader['mber_sn']
    #         data['spt_chrg_sn'] = team_leader['mber_sn']
    #     data['cntrct_nm'] = "{}년{}월 {} 일반판매".format(datetime.now(timezone('Asia/Seoul')).strftime("%y"), int(datetime.now(timezone('Asia/Seoul')).strftime("%m")), dept_nm)
    #     data['spt_nm'] = data['cntrct_nm']
    #     data['cntrct_de'] = datetime.now(timezone('Asia/Seoul')).strftime("%Y-%m-01")
    #     data['prjct_ty_code'] = "NR" if dept_nm.startswith("공조") else "BD"
    #     data['bcnc_sn'] = bcnc_sn
    #     data['cntrct_no'] = ''
    #     data['prjct_creat_at'] = 'Y'
    #     row = curs.execute("SELECT cntrct_sn FROM contract WHERE bcnc_sn=%(bcnc_sn)s AND cntrct_no='' AND cntrct_nm=%(cntrct_nm)s", data)
    #     if not row:
    #         keys = list(data.keys())
    #         sub_query = keys
    #         params_query = ["%({})s".format(key) for key in keys]
    #
    #         query = """INSERT INTO contract({}) VALUES ({})""".format(",".join(sub_query), ",".join(params_query))
    #         curs.execute(query, data)
    #         cntrct_sn = curs.lastrowid
    #
    #         query = """INSERT INTO project(ctmmny_sn, cntrct_sn, prjct_ty_code, regist_dtm, register_id) VALUES (1, %s, %s, NOW(), 'nexell')"""
    #         curs.execute(query, (cntrct_sn, data['prjct_ty_code']))
    #
    # db.commit()

    curs.execute("""SELECT m.parnts_menu_sn
                , m.menu_sn
                , m.menu_nm
                , m.menu_icon
                , m.menu_adres
                , m.menu_level
                , a.write_at
                , a.use_at
                FROM author_menu a
                LEFT JOIN menu m
                ON a.ctmmny_sn = m.ctmmny_sn AND a.menu_sn = m.menu_sn
                WHERE a.author_sn = %s
                AND m.use_at = 'Y'
                ORDER BY m.menu_level, m.menu_ordr
                """, (auth_cd, ))
    result = curs.fetchall()
    curs.close()
    db.close()
    menus = {}
    total_menus = {"main_menu" : []}
    for r in result:
        if r['menu_level'] == 1:
            menus[r['menu_sn']] = []
            total_menus["main_menu"].append(r)
        else:
            menus[r['parnts_menu_sn']].append(r)
    total_menus["sub_menu"] = menus
    return total_menus

