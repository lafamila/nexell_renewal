from flask import session, jsonify, g
import onetimepass as otp
import random
import string
import urllib
import datetime
import calendar
from app.helpers.class_helper import Map
from app.helpers.datatable_helper import dt_query
from collections import OrderedDict

def get_biss_summery(params):
    query = """SELECT * FROM (
				SELECT m.mber_sn
				, (SELECT code_ordr FROM code WHERE parnts_code='DEPT_CODE' AND code=m.dept_code) AS code_ordr
				, (SELECT code_nm FROM code WHERE parnts_code='DEPT_CODE' AND code=m.dept_code) AS dept_nm
				, GET_MEMBER_NAME(m.mber_sn, 'M') AS mber_nm
				, m.mber_size AS mber_size
				, IFNULL((SELECT COUNT(cntrct_no) FROM contract WHERE progrs_sttus_code IN ('P') AND spt_chrg_sn=m.mber_sn AND prjct_creat_at = 'Y'),0) AS cntrct_cnt
				, IFNULL((SELECT COUNT(cntrct_no) FROM contract WHERE progrs_sttus_code IN ('S') AND spt_chrg_sn=m.mber_sn AND prjct_creat_at = 'Y'),0) AS s_cnt
				, IFNULL((SELECT SUM(IFNULL(flaw_co,0)) FROM contract WHERE flaw_co>0 AND spt_chrg_sn=m.mber_sn),0) AS flaw_cnt
				, IFNULL((SELECT COUNT(cntrct_no) FROM contract WHERE progrs_sttus_code='B' AND spt_chrg_sn=m.mber_sn AND prjct_creat_at = 'Y'),0) AS ct_cnt
				, IFNULL((SELECT COUNT(cntrct_no) FROM contract WHERE progrs_sttus_code='N' AND spt_chrg_sn=m.mber_sn AND prjct_creat_at = 'Y'),0) AS n_cnt
				, IFNULL((SELECT COUNT(c.cntrct_no) FROM contract c LEFT JOIN (SELECT p.rate, p.cntrct_sn FROM pxcond p WHERE p.cntrct_sn=cntrct_sn AND rate IS NOT NULL ORDER BY p.pxcond_mt DESC LIMIT 1) p ON c.cntrct_sn=p.cntrct_sn WHERE p.rate=0),0) AS k_cnt
				, c.cntrct_no AS cntrct_no
				, c.spt_nm AS spt_nm
				, IFNULL(c.flaw_co, 0) AS flaw_co
				, m.ofcps_code
				, m.dept_code
				, c.bcnc_sn
				, (SELECT bcnc_nm FROM bcnc WHERE bcnc_sn=c.bcnc_sn) AS bcnc_nm
				FROM member m
				LEFT OUTER JOIN (SELECT * FROM contract WHERE flaw_co>0) c
				ON m.mber_sn = c.spt_chrg_sn
				WHERE m.dept_code IN ('PM', 'TS1', 'TS2', 'TS3', 'OS', 'BI')
				AND m.mber_sttus_code = 'H'
				) t ORDER BY t.code_ordr, t.ofcps_code, t.mber_nm"""
    g.curs.execute(query)
    result = g.curs.fetchall()
    return result

def get_all_member_project(params):
    query = """SELECT c.spt_chrg_sn AS mber_sn
				, (SELECT rate FROM pxcond WHERE cntrct_sn=c.cntrct_sn AND rate IS NOT NULL ORDER BY pxcond_mt DESC LIMIT 1) AS rate
				FROM contract c
				WHERE c.progrs_sttus_code IN ('P', 'S')
				AND c.prjct_creat_at = 'Y'
				"""
    g.curs.execute(query)
    result = g.curs.fetchall()
    return result

def get_sales_summery(params):
    ymd = params['s_pxcond_mt']
    year = ymd.split("-")[0]
    query = """SELECT bcnc_nm AS label
				, SUM(p_month01) AS p_month01
				, SUM(p_month02) AS p_month02
				, SUM(p_month03) AS p_month03
				, SUM(p_month04) AS p_month04
				, SUM(p_month05) AS p_month05
				, SUM(p_month06) AS p_month06
				, SUM(p_month07) AS p_month07
				, SUM(p_month08) AS p_month08
				, SUM(p_month09) AS p_month09
				, SUM(p_month10) AS p_month10
				, SUM(p_month11) AS p_month11
				, SUM(p_month12) AS p_month12
				, SUM(p_month99) AS p_month99
				FROM (
				SELECT 'part' AS type
				, b.esntl_delng_no
				, b.bcnc_nm
				, IF (SUBSTRING(a.ddt_man,6,2) = '01', SUM(a.dlnt*a.dlamt), 0) AS p_month01
				, IF (SUBSTRING(a.ddt_man,6,2) = '02', SUM(a.dlnt*a.dlamt), 0) AS p_month02
				, IF (SUBSTRING(a.ddt_man,6,2) = '03', SUM(a.dlnt*a.dlamt), 0) AS p_month03
				, IF (SUBSTRING(a.ddt_man,6,2) = '04', SUM(a.dlnt*a.dlamt), 0) AS p_month04
				, IF (SUBSTRING(a.ddt_man,6,2) = '05', SUM(a.dlnt*a.dlamt), 0) AS p_month05
				, IF (SUBSTRING(a.ddt_man,6,2) = '06', SUM(a.dlnt*a.dlamt), 0) AS p_month06
				, IF (SUBSTRING(a.ddt_man,6,2) = '07', SUM(a.dlnt*a.dlamt), 0) AS p_month07
				, IF (SUBSTRING(a.ddt_man,6,2) = '08', SUM(a.dlnt*a.dlamt), 0) AS p_month08
				, IF (SUBSTRING(a.ddt_man,6,2) = '09', SUM(a.dlnt*a.dlamt), 0) AS p_month09
				, IF (SUBSTRING(a.ddt_man,6,2) = '10', SUM(a.dlnt*a.dlamt), 0) AS p_month10
				, IF (SUBSTRING(a.ddt_man,6,2) = '11', SUM(a.dlnt*a.dlamt), 0) AS p_month11
				, IF (SUBSTRING(a.ddt_man,6,2) = '12', SUM(a.dlnt*a.dlamt), 0) AS p_month12
				, SUM(a.dlnt*a.dlamt) AS p_month99
				FROM account a
				JOIN bcnc b
				ON a.ctmmny_sn=b.ctmmny_sn AND a.bcnc_sn=b.bcnc_sn
				WHERE a.ctmmny_sn = 1
				AND a.ddt_man BETWEEN '{0}-01-01' AND '{0}-12-31'
				AND a.delng_se_code = 'P'
				GROUP BY b.esntl_delng_no, b.bcnc_nm, SUBSTRING(a.ddt_man,1,7)
				UNION ALL
				SELECT 'total' AS type
				, '총계' AS esntl_delng_no
				, '총계' AS bcnc_nm
				, IF (SUBSTRING(a.ddt_man,6,2) = '01', SUM(a.dlnt*a.dlamt), 0) AS p_month01
				, IF (SUBSTRING(a.ddt_man,6,2) = '02', SUM(a.dlnt*a.dlamt), 0) AS p_month02
				, IF (SUBSTRING(a.ddt_man,6,2) = '03', SUM(a.dlnt*a.dlamt), 0) AS p_month03
				, IF (SUBSTRING(a.ddt_man,6,2) = '04', SUM(a.dlnt*a.dlamt), 0) AS p_month04
				, IF (SUBSTRING(a.ddt_man,6,2) = '05', SUM(a.dlnt*a.dlamt), 0) AS p_month05
				, IF (SUBSTRING(a.ddt_man,6,2) = '06', SUM(a.dlnt*a.dlamt), 0) AS p_month06
				, IF (SUBSTRING(a.ddt_man,6,2) = '07', SUM(a.dlnt*a.dlamt), 0) AS p_month07
				, IF (SUBSTRING(a.ddt_man,6,2) = '08', SUM(a.dlnt*a.dlamt), 0) AS p_month08
				, IF (SUBSTRING(a.ddt_man,6,2) = '09', SUM(a.dlnt*a.dlamt), 0) AS p_month09
				, IF (SUBSTRING(a.ddt_man,6,2) = '10', SUM(a.dlnt*a.dlamt), 0) AS p_month10
				, IF (SUBSTRING(a.ddt_man,6,2) = '11', SUM(a.dlnt*a.dlamt), 0) AS p_month11
				, IF (SUBSTRING(a.ddt_man,6,2) = '12', SUM(a.dlnt*a.dlamt), 0) AS p_month12
				, SUM(a.dlnt*a.dlamt) AS p_month99
				FROM account a
				JOIN bcnc b
				ON a.ctmmny_sn=b.ctmmny_sn AND a.bcnc_sn=b.bcnc_sn
				WHERE a.ctmmny_sn = 1
				AND a.ddt_man BETWEEN '{0}-01-01' AND '{0}-12-31'
				AND a.delng_se_code = 'P'
				GROUP BY SUBSTRING(a.ddt_man,6,2)
				) t
				GROUP BY bcnc_nm
				ORDER BY type, p_month99 DESC""".format(year)
    g.curs.execute(query)
    result = g.curs.fetchall()
    return result

def get_sales_one_summery(params):
    ymd = params['s_pxcond_mt']
    y, m, d = ymd.split("-")
    f, l = calendar.monthrange(int(y), int(m))
    first_day = "{}-{}-{}".format(y.zfill(4), m.zfill(2), str(f).zfill(2))
    last_day = "{}-{}-{}".format(y.zfill(4), m.zfill(2), str(l).zfill(2))
    query = """SELECT IF(b.bcnc_sn IN (3, 74, 79, 100), bcnc_nm, '타사자재') AS label
				, IFNULL(SUM(IFNULL(a.dlnt,0)*IFNULL(a.dlamt, 0)),0) AS p_month
				, IFNULL(m.dept_code, 999) AS dept_code
				, IFNULL((SELECT code_nm FROM code WHERE parnts_code='DEPT_CODE' AND code=dept_code),'기타') AS bsn_dept_nm
				, IFNULL((SELECT cd.code_ordr FROM code cd WHERE cd.parnts_code='DEPT_CODE' AND code = dept_code),999) AS code_order
				FROM account a
				LEFT JOIN bcnc b
				ON a.ctmmny_sn=b.ctmmny_sn AND a.bcnc_sn=b.bcnc_sn
				LEFT JOIN contract c
				ON a.cntrct_sn=c.cntrct_sn
				LEFT JOIN member m
				ON c.bsn_chrg_sn = m.mber_sn
				WHERE a.ctmmny_sn = 1
				AND a.ddt_man BETWEEN '{0} 00:00:00' AND '{1} 23:59:59'
				AND a.delng_se_code = 'P'
				AND a.cntrct_sn IS NOT NULL
				GROUP BY b.esntl_delng_no, b.bcnc_nm, dept_code
				UNION
				SELECT IF(b.bcnc_sn IN (3, 74, 79, 100), bcnc_nm, '타사자재') AS label
				, IFNULL(SUM(IFNULL(a.dlnt,0)*IFNULL(a.dlamt, 0)),0) AS p_month
				, 999 AS dept_code
				, '기타' AS bsn_dept_nm
				, 999 AS code_order
				FROM account a
				LEFT JOIN bcnc b
				ON a.ctmmny_sn=b.ctmmny_sn AND a.bcnc_sn=b.bcnc_sn
				WHERE a.ctmmny_sn = 1
				AND a.ddt_man BETWEEN '{0} 00:00:00' AND '{1} 23:59:59'
				AND a.delng_se_code = 'P'
				AND a.cntrct_sn IS NULL
				GROUP BY b.esntl_delng_no, b.bcnc_nm, dept_code
				ORDER BY code_order ASC, dept_code ASC, p_month DESC""".format(first_day, last_day)
    g.curs.execute(query)
    result = g.curs.fetchall()
    return result