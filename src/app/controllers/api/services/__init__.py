from flask import current_app
from src.app.connectors import DB

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

