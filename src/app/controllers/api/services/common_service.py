from flask import session, jsonify, g
from app.helpers.datatable_helper import dt_query
from collections import OrderedDict
import datetime

def get_work(params):
    query = """SELECT t.*, IFNULL(s.memo_sn, -1) AS memo_sn, IFNULL(s.memo_state, -1) AS memo_state FROM
				(SELECT e.work_row
				, e.work_month
				, e.work_data
				FROM work e
				WHERE 1=1
				AND e.work_year=%(work_year)s
				AND e.work_sn IN (SELECT MAX(ex.work_sn) FROM work ex WHERE ex.work_year=%(work_year)s GROUP BY ex.work_row, ex.work_month)
				) t LEFT OUTER JOIN (SELECT * FROM work_memo WHERE work_date=DATE_FORMAT(now(), %(format)s)) s ON t.work_row=s.work_row"""
    params['format'] = '%Y-%m-%d'
    g.curs.execute(query, params)
    result = g.curs.fetchall()
    return result