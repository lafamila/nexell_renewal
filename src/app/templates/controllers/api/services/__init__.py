from flask import current_app
from app.connectors import DB

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
                author_list=get_author_list(),
                bcnc_list=get_bcnc_list(),
                member_list=get_member_list(),
                prduct_ty_code_list=get_code_list('prduct_ty_code'.upper()),
                prduct_sse_code_list=get_code_list('prduct_sse_code'.upper()),
                invn_sttus_code_list=get_code_list('invn_sttus_code'.upper()),
                inventory_list=get_inventory_name_list(),
                contract_list=get_contract_list(),
                amt_ty_code_list=get_code_list('amt_ty_code'.upper()))

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
    current_app.jinja_env.globals.update(
        menus=total_menus
    )

