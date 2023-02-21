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

def get_completed_suju_b(params):
    query = """SELECT co.code_nm
				, co.code_ordr
				, 1 AS ordr
				, c.cntrct_nm
				, c.cntrct_de AS cntrct_de
				, 0 AS price_1
				, SUM(
				    IF(c.prjct_ty_code <> 'BF',
				      IF(cst.cntrct_execut_code = 'B', IFNULL(cst.salamt,0)*cst.qy, 0),
				      IF(cst.cntrct_execut_code = 'B', IFNULL(cst.QY, 0)*IFNULL(cst.puchas_amount,0)*0.01*(100.0-IFNULL(cst.dscnt_rt, 0))*IFNULL(cst.fee_rt, 0)*0.01, 0)
				    )
			    ) AS price_2
				, 1 AS count
				, m.dept_code
				, (SELECT bcnc_nm FROM bcnc b WHERE b.bcnc_sn = c.bcnc_sn) AS bcnc_nm
				, CONCAT(c.cntrwk_bgnde,' ~ ',c.cntrwk_endde) AS cntrwk_period
				FROM cost cst
                    LEFT JOIN contract c
                    ON c.cntrct_sn = cst.cntrct_sn
                    LEFT JOIN member m
                    ON c.bsn_chrg_sn = m.mber_sn
                    LEFT JOIN code co
                    ON co.parnts_code = 'DEPT_CODE' AND co.code = m.dept_code
				WHERE 1=1
                    AND (m.dept_code LIKE 'TS%%' OR m.dept_code = 'BI')
                    AND m.mber_sttus_code = 'H'
                    AND cst.cntrct_execut_code IN ('B', 'C')
                    AND c.PROGRS_STTUS_CODE IN ('B')
				GROUP BY m.dept_code, c.bcnc_sn, cst.cntrct_sn
				ORDER BY code_ordr, dept_code, ordr, bcnc_nm, cntrct_de
				"""
    g.curs.execute(query)
    result = g.curs.fetchall()
    return result

def get_kisung_suju(params):
    query = """SELECT sj.*
				, cd.code_nm AS dept_nm
				FROM (
				SELECT 1 AS sort
				, mb.dept_code AS dept
				, SUM(IFNULL(1m,0)) AS m01
				, SUM(IFNULL(2m,0)) AS m02
				, SUM(IFNULL(3m,0)) AS m03
				, SUM(IFNULL(4m,0)) AS m04
				, SUM(IFNULL(5m,0)) AS m05
				, SUM(IFNULL(6m,0)) AS m06
				, SUM(IFNULL(7m,0)) AS m07
				, SUM(IFNULL(8m,0)) AS m08
				, SUM(IFNULL(9m,0)) AS m09
				, SUM(IFNULL(10m,0)) AS m10
				, SUM(IFNULL(11m,0)) AS m11
				, IFNULL(SUM(IFNULL(12m,0)), 0) AS m12
				, IFNULL(SUM(IFNULL(1m,0)),0)
				+ IFNULL(SUM(IFNULL(2m,0)),0)
				+ IFNULL(SUM(IFNULL(3m,0)),0)
				+ IFNULL(SUM(IFNULL(4m,0)),0)
				+ IFNULL(SUM(IFNULL(5m,0)),0)
				+ IFNULL(SUM(IFNULL(6m,0)),0)
				+ IFNULL(SUM(IFNULL(7m,0)),0)
				+ IFNULL(SUM(IFNULL(8m,0)),0)
				+ IFNULL(SUM(IFNULL(9m,0)),0)
				+ IFNULL(SUM(IFNULL(10m,0)),0)
				+ IFNULL(SUM(IFNULL(11m,0)),0)
				+ IFNULL(SUM(IFNULL(12m,0)),0) AS total
				FROM goal go
				JOIN member mb
				ON go.mber_sn = mb.mber_sn
				WHERE go.stdyy = SUBSTRING(NOW(),1,4)
				AND go.amt_ty_code = '2'
				AND mb.dept_code <> 'PM'
				GROUP BY mb.dept_code
				UNION
				SELECT 2 AS sort
				, t.dept
				, SUM(IFNULL(t.m01,0)) AS m01
				, SUM(IFNULL(t.m02,0)) AS m02
				, SUM(IFNULL(t.m03,0)) AS m03
				, SUM(IFNULL(t.m04,0)) AS m04
				, SUM(IFNULL(t.m05,0)) AS m05
				, SUM(IFNULL(t.m06,0)) AS m06
				, SUM(IFNULL(t.m07,0)) AS m07
				, SUM(IFNULL(t.m08,0)) AS m08
				, SUM(IFNULL(t.m09,0)) AS m09
				, SUM(IFNULL(t.m10,0)) AS m10
				, SUM(IFNULL(t.m11,0)) AS m11
				, SUM(IFNULL(t.m12,0)) AS m12
				, IFNULL(SUM(t.m01),0)+IFNULL(SUM(t.m02),0)+IFNULL(SUM(t.m03),0)+IFNULL(SUM(t.m04),0)+IFNULL(SUM(t.m05),0)+IFNULL(SUM(t.m06),0)+IFNULL(SUM(t.m07),0)+IFNULL(SUM(t.m08),0)+IFNULL(SUM(t.m09),0)+IFNULL(SUM(t.m10),0)+IFNULL(SUM(t.m11),0)+IFNULL(SUM(t.m12),0) AS total
				FROM (
				SELECT mb.dept_code AS dept
				, GET_SUJU_AMOUNT(CONCAT(SUBSTRING(NOW(),1,4),'-01-01'), mb.mber_sn, 'M') AS m01
				, GET_SUJU_AMOUNT(CONCAT(SUBSTRING(NOW(),1,4),'-02-01'), mb.mber_sn, 'M') AS m02
				, GET_SUJU_AMOUNT(CONCAT(SUBSTRING(NOW(),1,4),'-03-01'), mb.mber_sn, 'M') AS m03
				, GET_SUJU_AMOUNT(CONCAT(SUBSTRING(NOW(),1,4),'-04-01'), mb.mber_sn, 'M') AS m04
				, GET_SUJU_AMOUNT(CONCAT(SUBSTRING(NOW(),1,4),'-05-01'), mb.mber_sn, 'M') AS m05
				, GET_SUJU_AMOUNT(CONCAT(SUBSTRING(NOW(),1,4),'-06-01'), mb.mber_sn, 'M') AS m06
				, GET_SUJU_AMOUNT(CONCAT(SUBSTRING(NOW(),1,4),'-07-01'), mb.mber_sn, 'M') AS m07
				, GET_SUJU_AMOUNT(CONCAT(SUBSTRING(NOW(),1,4),'-08-01'), mb.mber_sn, 'M') AS m08
				, GET_SUJU_AMOUNT(CONCAT(SUBSTRING(NOW(),1,4),'-09-01'), mb.mber_sn, 'M') AS m09
				, GET_SUJU_AMOUNT(CONCAT(SUBSTRING(NOW(),1,4),'-10-01'), mb.mber_sn, 'M') AS m10
				, GET_SUJU_AMOUNT(CONCAT(SUBSTRING(NOW(),1,4),'-11-01'), mb.mber_sn, 'M') AS m11
				, GET_SUJU_AMOUNT(CONCAT(SUBSTRING(NOW(),1,4),'-12-01'), mb.mber_sn, 'M') AS m12
				, GET_SUJU_AMOUNT(CONCAT(SUBSTRING(NOW(),1,4),'-12-01'), mb.mber_sn, 'A') AS total
				FROM member mb
				WHERE 1
				AND (mb.dept_code LIKE 'TS%%' OR mb.dept_code LIKE 'BI%%' OR mb.dept_code IN ('ST', 'EL', 'CT', 'MA'))
				) t
				GROUP BY t.dept
				) sj
				JOIN code cd
				ON cd.parnts_code='GOAL_DEPT_CODE' AND cd.code=sj.dept
				ORDER BY cd.code_ordr, sj.sort"""
    g.curs.execute(query)
    result = g.curs.fetchall()
    return result

def get_kisung_sales(params):
    query = """SELECT sj.*
				, cd.code_nm AS dept_nm
				FROM (
				SELECT 1 AS sort
				, mb.dept_code AS dept
				, SUM(IFNULL(1m,0)) AS m01
				, SUM(IFNULL(2m,0)) AS m02
				, SUM(IFNULL(3m,0)) AS m03
				, SUM(IFNULL(4m,0)) AS m04
				, SUM(IFNULL(5m,0)) AS m05
				, SUM(IFNULL(6m,0)) AS m06
				, SUM(IFNULL(7m,0)) AS m07
				, SUM(IFNULL(8m,0)) AS m08
				, SUM(IFNULL(9m,0)) AS m09
				, SUM(IFNULL(10m,0)) AS m10
				, SUM(IFNULL(11m,0)) AS m11
				, IFNULL(SUM(IFNULL(12m,0)), 0) AS m12
				, IFNULL(SUM(1m),0)+IFNULL(SUM(2m),0)+IFNULL(SUM(3m),0)+IFNULL(SUM(4m),0)+IFNULL(SUM(5m),0)+IFNULL(SUM(6m),0)+IFNULL(SUM(7m),0)+IFNULL(SUM(8m),0)+IFNULL(SUM(9m),0)+IFNULL(SUM(10m),0)+IFNULL(SUM(11m),0)+IFNULL(SUM(12m),0) AS total
				FROM goal go
				JOIN member mb
				ON go.mber_sn = mb.mber_sn
				WHERE go.stdyy = SUBSTRING(NOW(),1,4)
				AND go.amt_ty_code IN ('3','8')
				AND mb.dept_code <> 'PM'
				GROUP BY mb.dept_code
				UNION
				SELECT 2 AS sort
				, t.dept
				, IFNULL(SUM(t.m01),0) AS m01
				, IFNULL(SUM(t.m02),0) AS m02
				, IFNULL(SUM(t.m03),0) AS m03
				, IFNULL(SUM(t.m04),0) AS m04
				, IFNULL(SUM(t.m05),0) AS m05
				, IFNULL(SUM(t.m06),0) AS m06
				, IFNULL(SUM(t.m07),0) AS m07
				, IFNULL(SUM(t.m08),0) AS m08
				, IFNULL(SUM(t.m09),0) AS m09
				, IFNULL(SUM(t.m10),0) AS m10
				, IFNULL(SUM(t.m11),0) AS m11
				, IFNULL(SUM(t.m12),0) AS m12
				, IFNULL(SUM(t.m01),0)+IFNULL(SUM(t.m02),0)+IFNULL(SUM(t.m03),0)+IFNULL(SUM(t.m04),0)+IFNULL(SUM(t.m05),0)+IFNULL(SUM(t.m06),0)+IFNULL(SUM(t.m07),0)+IFNULL(SUM(t.m08),0)+IFNULL(SUM(t.m09),0)+IFNULL(SUM(t.m10),0)+IFNULL(SUM(t.m11),0)+IFNULL(SUM(t.m12),0) AS total
				FROM (
				SELECT mb.dept_code AS dept
				, IFNULL(GET_PXCOND_MONTH_AMOUNT('C',CONCAT(SUBSTRING(NOW(),1,4),'-01-01'), mb.mber_sn),0) AS m01
				, IFNULL(GET_PXCOND_MONTH_AMOUNT('C',CONCAT(SUBSTRING(NOW(),1,4),'-02-01'), mb.mber_sn),0) AS m02
				, IFNULL(GET_PXCOND_MONTH_AMOUNT('C',CONCAT(SUBSTRING(NOW(),1,4),'-03-01'), mb.mber_sn),0) AS m03
				, IFNULL(GET_PXCOND_MONTH_AMOUNT('C',CONCAT(SUBSTRING(NOW(),1,4),'-04-01'), mb.mber_sn),0) AS m04
				, IFNULL(GET_PXCOND_MONTH_AMOUNT('C',CONCAT(SUBSTRING(NOW(),1,4),'-05-01'), mb.mber_sn),0) AS m05
				, IFNULL(GET_PXCOND_MONTH_AMOUNT('C',CONCAT(SUBSTRING(NOW(),1,4),'-06-01'), mb.mber_sn),0) AS m06
				, IFNULL(GET_PXCOND_MONTH_AMOUNT('C',CONCAT(SUBSTRING(NOW(),1,4),'-07-01'), mb.mber_sn),0) AS m07
				, IFNULL(GET_PXCOND_MONTH_AMOUNT('C',CONCAT(SUBSTRING(NOW(),1,4),'-08-01'), mb.mber_sn),0) AS m08
				, IFNULL(GET_PXCOND_MONTH_AMOUNT('C',CONCAT(SUBSTRING(NOW(),1,4),'-09-01'), mb.mber_sn),0) AS m09
				, IFNULL(GET_PXCOND_MONTH_AMOUNT('C',CONCAT(SUBSTRING(NOW(),1,4),'-10-01'), mb.mber_sn),0) AS m10
				, IFNULL(GET_PXCOND_MONTH_AMOUNT('C',CONCAT(SUBSTRING(NOW(),1,4),'-11-01'), mb.mber_sn),0) AS m11
				, IFNULL(GET_PXCOND_MONTH_AMOUNT('C',CONCAT(SUBSTRING(NOW(),1,4),'-12-01'), mb.mber_sn),0) AS m12
				, GET_PXCOND_TOTAL_AMOUNT('C',CONCAT(SUBSTRING(NOW(),1,4),'-12'), mb.mber_sn) AS total
				FROM member mb
				WHERE 1
				AND (mb.dept_code LIKE 'TS%%' OR mb.dept_code LIKE 'BI%%' OR mb.dept_code IN ('EL', 'CT', 'MA'))
				UNION
				SELECT mb.dept_code AS dept
				, IFNULL(SUM(1m),0) AS m01
				, IFNULL(SUM(2m),0) AS m02
				, IFNULL(SUM(3m),0) AS m03
				, IFNULL(SUM(4m),0) AS m04
				, IFNULL(SUM(5m),0) AS m05
				, IFNULL(SUM(6m),0) AS m06
				, IFNULL(SUM(7m),0) AS m07
				, IFNULL(SUM(8m),0) AS m08
				, IFNULL(SUM(9m),0) AS m09
				, IFNULL(SUM(10m),0) AS m10
				, IFNULL(SUM(11m),0) AS m11
				, IFNULL(SUM(12m), 0) AS m12
				, IFNULL(SUM(1m),0)+IFNULL(SUM(2m),0)+IFNULL(SUM(3m),0)+IFNULL(SUM(4m),0)+IFNULL(SUM(5m),0)+IFNULL(SUM(6m),0)+IFNULL(SUM(7m),0)+IFNULL(SUM(8m),0)+IFNULL(SUM(9m),0)+IFNULL(SUM(10m),0)+IFNULL(SUM(11m),0)+IFNULL(SUM(12m),0) AS total
				FROM goal go
				JOIN member mb
				ON go.mber_sn = mb.mber_sn
				WHERE go.stdyy = SUBSTRING(NOW(),1,4)
				AND go.amt_ty_code = '9'
				AND mb.dept_code <> 'PM'
				GROUP BY mb.dept_code
				) t
				GROUP BY t.dept
				) sj
				JOIN code cd
				ON cd.parnts_code='GOAL_DEPT_CODE' AND cd.code=sj.dept
				ORDER BY cd.code_ordr, sj.sort"""
    g.curs.execute(query)
    result = g.curs.fetchall()
    return result
def get_kisung_va(params):
    query = """SELECT sj.*
				, cd.code_nm AS dept_nm
				FROM (
				SELECT 1 AS sort
				, mb.dept_code AS dept
				, SUM(IFNULL(1m, 0)) AS m01
				, SUM(IFNULL(2m, 0)) AS m02
				, SUM(IFNULL(3m, 0)) AS m03
				, SUM(IFNULL(4m, 0)) AS m04
				, SUM(IFNULL(5m, 0)) AS m05
				, SUM(IFNULL(6m, 0)) AS m06
				, SUM(IFNULL(7m, 0)) AS m07
				, SUM(IFNULL(8m, 0)) AS m08
				, SUM(IFNULL(9m, 0)) AS m09
				, SUM(IFNULL(10m, 0)) AS m10
				, SUM(IFNULL(11m, 0)) AS m11
				, IFNULL(SUM(IFNULL(12m, 0)), 0) AS m12
				, IFNULL(SUM(1m),0)+IFNULL(SUM(2m),0)+IFNULL(SUM(3m),0)+IFNULL(SUM(4m),0)+IFNULL(SUM(5m),0)+IFNULL(SUM(6m),0)+IFNULL(SUM(7m),0)+IFNULL(SUM(8m),0)+IFNULL(SUM(9m),0)+IFNULL(SUM(10m),0)+IFNULL(SUM(11m),0)+IFNULL(SUM(12m),0) AS total
				FROM goal go
				JOIN member mb
				ON go.mber_sn = mb.mber_sn
				WHERE go.stdyy = SUBSTRING(NOW(),1,4)
				AND go.amt_ty_code IN ('5','8')
				AND mb.dept_code <> 'PM'
				GROUP BY mb.dept_code
				UNION
				SELECT 2 AS sort
				, t.dept
				, SUM(t.m01) AS m01
				, SUM(t.m02) AS m02
				, SUM(t.m03) AS m03
				, SUM(t.m04) AS m04
				, SUM(t.m05) AS m05
				, SUM(t.m06) AS m06
				, SUM(t.m07) AS m07
				, SUM(t.m08) AS m08
				, SUM(t.m09) AS m09
				, SUM(t.m10) AS m10
				, SUM(t.m11) AS m11
				, SUM(t.m12) AS m12
				, SUM(t.total) AS total
				FROM (
				SELECT mb.dept_code AS dept
				, SUM(GET_VA_MONTH_AMOUNT(CONCAT(SUBSTRING(NOW(),1,4),'-01'), mb.mber_sn)) AS m01
				, SUM(GET_VA_MONTH_AMOUNT(CONCAT(SUBSTRING(NOW(),1,4),'-02'), mb.mber_sn)) AS m02
				, SUM(GET_VA_MONTH_AMOUNT(CONCAT(SUBSTRING(NOW(),1,4),'-03'), mb.mber_sn)) AS m03
				, SUM(GET_VA_MONTH_AMOUNT(CONCAT(SUBSTRING(NOW(),1,4),'-04'), mb.mber_sn)) AS m04
				, SUM(GET_VA_MONTH_AMOUNT(CONCAT(SUBSTRING(NOW(),1,4),'-05'), mb.mber_sn)) AS m05
				, SUM(GET_VA_MONTH_AMOUNT(CONCAT(SUBSTRING(NOW(),1,4),'-06'), mb.mber_sn)) AS m06
				, SUM(GET_VA_MONTH_AMOUNT(CONCAT(SUBSTRING(NOW(),1,4),'-07'), mb.mber_sn)) AS m07
				, SUM(GET_VA_MONTH_AMOUNT(CONCAT(SUBSTRING(NOW(),1,4),'-08'), mb.mber_sn)) AS m08
				, SUM(GET_VA_MONTH_AMOUNT(CONCAT(SUBSTRING(NOW(),1,4),'-09'), mb.mber_sn)) AS m09
				, SUM(GET_VA_MONTH_AMOUNT(CONCAT(SUBSTRING(NOW(),1,4),'-10'), mb.mber_sn)) AS m10
				, SUM(GET_VA_MONTH_AMOUNT(CONCAT(SUBSTRING(NOW(),1,4),'-11'), mb.mber_sn)) AS m11
				, SUM(GET_VA_MONTH_AMOUNT(CONCAT(SUBSTRING(NOW(),1,4),'-12'), mb.mber_sn)) AS m12
				, SUM(GET_VA_TOTAL_AMOUNT(CONCAT(SUBSTRING(NOW(),1,4),'-12'), mb.mber_sn)) AS total
				FROM member mb
				WHERE (mb.dept_code LIKE 'TS%%' OR mb.dept_code LIKE 'BI%%' OR mb.dept_code IN ('EL', 'CT', 'MA'))
				GROUP BY mb.dept_code
				UNION
				SELECT mb.dept_code AS dept
				, SUM(1m) AS m01
				, SUM(2m) AS m02
				, SUM(3m) AS m03
				, SUM(4m) AS m04
				, SUM(5m) AS m05s
				, SUM(6m) AS m06
				, SUM(7m) AS m07
				, SUM(8m) AS m08
				, SUM(9m) AS m09
				, SUM(10m) AS m10
				, SUM(11m) AS m11
				, IFNULL(SUM(12m), 0) AS m12
				, IFNULL(SUM(1m),0)+IFNULL(SUM(2m),0)+IFNULL(SUM(3m),0)+IFNULL(SUM(4m),0)+IFNULL(SUM(5m),0)+IFNULL(SUM(6m),0)+IFNULL(SUM(7m),0)+IFNULL(SUM(8m),0)+IFNULL(SUM(9m),0)+IFNULL(SUM(10m),0)+IFNULL(SUM(11m),0)+IFNULL(SUM(12m),0) AS total
				FROM goal go
				JOIN member mb
				ON go.mber_sn = mb.mber_sn
				WHERE go.stdyy = SUBSTRING(NOW(),1,4)
				AND go.amt_ty_code = '9'
				AND mb.dept_code <> 'PM'
				GROUP BY mb.dept_code
				) t
				GROUP BY t.dept
				) sj
				JOIN code cd
				ON cd.parnts_code='GOAL_DEPT_CODE' AND cd.code=sj.dept
				ORDER BY cd.code_ordr, sj.sort"""
    g.curs.execute(query)
    result = g.curs.fetchall()
    return result

def get_projects_by_dept_member(params):
    if "s_pxcond_mt" in params and params["s_pxcond_mt"]:
        s_pxcond_mt = params["s_pxcond_mt"]
    else:
        s_pxcond_mt = datetime.datetime.now().strftime("%Y-%m")

    data = dict()
    data["s_pxcond_mt"] = s_pxcond_mt
    data["s_dept_code"] = params["s_dept_code"]
    if "s_mber_sn" in params:
        data["s_mber_sn"] = params["s_mber_sn"]
    query = """SELECT c.progrs_sttus_code
				, (SELECT co.code_nm FROM code co WHERE co.parnts_code='PROGRS_STTUS_CODE' AND co.code=c.progrs_sttus_code) AS sttus_nm
				, c.bcnc_sn
				, (SELECT bcnc_nm FROM bcnc WHERE bcnc_sn=c.bcnc_sn) AS bcnc_nm
				, c.spt_nm
				, cntrwk_bgnde
				, cntrwk_endde
				, prjct_ty_code
				, (SELECT code_nm FROM code WHERE ctmmny_sn=1 AND parnts_code='PRJCT_TY_CODE' AND code=c.prjct_ty_code) AS prjct_ty_nm
				, CONCAT(DATE_FORMAT(cntrwk_bgnde, '%%Y-%%m'),'~',DATE_FORMAT(cntrwk_endde, '%%Y-%%m')) AS cntrwk_period
				, (SELECT rate FROM pxcond WHERE cntrct_sn=c.cntrct_sn AND rate IS NOT NULL ORDER BY pxcond_mt DESC LIMIT 1) AS rate
				, (SELECT SUM(IFNULL(co.qy*co.puchas_amount, 0)) FROM cost co WHERE co.cntrct_sn=c.cntrct_sn AND co.cntrct_execut_code='E' AND co.ct_se_code NOT IN ('61','62', '63','7', '8', '10')) AS exec_sum
				, (SELECT SUM(CASE WHEN co.ct_se_code IN ('1','2','4') THEN GET_ACCOUNT_COMPLETE_AMOUNT(c.cntrct_sn, co.purchsofc_sn, 'P', %(s_pxcond_mt)s)
				WHEN co.ct_se_code IN ('3') THEN GET_ACCOUNT_COMPLETE_AMOUNT(c.cntrct_sn, co.purchsofc_sn, 'S', %(s_pxcond_mt)s)
				WHEN co.ct_se_code IN ('8') THEN GET_PXCOND_COMPLETE_AMOUNT(c.cntrct_sn, co.purchsofc_sn, 'S', %(s_pxcond_mt)s)
				ELSE GET_TAXBIL_COMPLETE_AMOUNT(c.cntrct_sn, co.purchsofc_sn, co.cntrct_execut_code, %(s_pxcond_mt)s)
				END) FROM cost co WHERE co.cntrct_sn=c.cntrct_sn AND co.cntrct_execut_code='E' AND co.ct_se_code NOT IN ('61','62', '63','7', '8', '10')) AS complete_sum
				, (SELECT SUM(CASE WHEN co.ct_se_code IN ('1','2','4') THEN GET_ACCOUNT_EXCUT_AMOUNT(c.cntrct_sn, co.purchsofc_sn, 'P', %(s_pxcond_mt)s)
				WHEN co.ct_se_code IN ('3') THEN GET_ACCOUNT_EXCUT_AMOUNT(c.cntrct_sn, co.purchsofc_sn, 'S', %(s_pxcond_mt)s)
				WHEN co.ct_se_code IN ('8') THEN GET_PXCOND_EXCUT_AMOUNT(c.cntrct_sn, co.purchsofc_sn, co.cntrct_execut_code, %(s_pxcond_mt)s)
				ELSE GET_TAXBIL_EXCUT_AMOUNT(c.cntrct_sn, co.purchsofc_sn, co.cntrct_execut_code, %(s_pxcond_mt)s)
				END) FROM cost co WHERE co.cntrct_sn=c.cntrct_sn AND co.cntrct_execut_code='E' AND co.ct_se_code NOT IN ('61','62', '63','7', '8', '10')) AS now_sum
				, CASE WHEN progrs_sttus_code = 'P' THEN 1
				WHEN progrs_sttus_code = 'N' THEN 3
				WHEN progrs_sttus_code = 'B' THEN 2
				WHEN progrs_sttus_code = 'S' THEN 1
				END AS ordr
				, (SELECT IFNULL(SUM(IF(c.prjct_ty_code <> 'BF',IF(c.progrs_sttus_code <> 'B', IF(cst.cntrct_execut_code = 'B',0, IFNULL(cst.salamt,0)*cst.qy), 0),IF(cst.cntrct_execut_code = 'C', IFNULL(cst.QY, 0)*IFNULL(cst.puchas_amount,0)*0.01*(100.0-IFNULL(cst.dscnt_rt, 0))*IFNULL(cst.fee_rt, 0)*0.01, 0))),0) FROM cost cst WHERE cst.cntrct_sn = c.cntrct_sn AND cst.cntrct_execut_code <> 'B') AS cntrct_amount
				FROM contract c
				LEFT JOIN member m
				ON c.spt_chrg_sn=m.mber_sn
				WHERE 1=1
				AND c.progrs_sttus_code IN ('P', 'B', 'N', 'S')
				AND c.prjct_creat_at = 'Y'
				AND m.dept_code = %(s_dept_code)s
				"""
    if "s_mber_sn" in data:
        query += " AND c.spt_chrg_sn = %(s_mber_sn)s "
    """ ORDER BY ordr, bcnc_nm, c.spt_nm"""
    g.curs.execute(query, data)
    result = g.curs.fetchall()
    return result

def get_goal_contract(params):
    query = """SELECT g.stdyy AS stdyy
                    , g.amt_ty_code AS amt_ty_code
                    , m.dept_code AS dept_code
                    , `{0}m` AS value
                    , g.cntrct_sn AS cntrct_sn
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
                    FROM goal g
                    LEFT JOIN member m
                    ON g.mber_sn=m.mber_sn
                    LEFT JOIN contract c
                    ON g.cntrct_sn=c.cntrct_sn
                    WHERE 1=1
                    AND `{0}m` IS NOT NULL
                    AND amt_ty_code IN ('2', '3')
                    AND stdyy={1}""".format(params['s_month'], params['s_stdyy'])
    g.curs.execute(query)
    result = g.curs.fetchall()
    return result