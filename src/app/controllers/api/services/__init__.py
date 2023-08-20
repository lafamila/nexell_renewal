from flask import session
from app.connectors import DB
from datetime import datetime
from pytz import timezone
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
                contract_nr_list=get_contract_NR_list(),
                amt_ty_code_list=get_code_list('amt_ty_code'.upper()),
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
    # general sales project - bcnc check

    # bcnc_nm = "{}년{}월일반".format(datetime.now(timezone('Asia/Seoul')).strftime("%y"), int(datetime.now(timezone('Asia/Seoul')).strftime("%m")))
    # row = curs.execute("SELECT bcnc_sn FROM bcnc WHERE bcnc_nm=%s AND bcnc_se_code='S'", bcnc_nm)
    # if not row:
    #     curs.execute("INSERT bcnc(CTMMNY_SN, BCNC_SE_CODE, BCNC_NM, BCNC_TELNO, BCNC_ADRES, RPRSNTV_NM, BIZRNO, BSNM_SE_CODE, ESNTL_DELNG_NO, USE_AT, REGIST_DTM, REGISTER_ID) VALUES (1, 'S', %s, null, null, null, '해당사항없음', 1, null, 'Y', NOW(), 'nexelll')", bcnc_nm)
    #     bcnc_sn = curs.lastrowid
    # else:
    #     bcnc_sn = curs.fetchone()['bcnc_sn']
    #
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

