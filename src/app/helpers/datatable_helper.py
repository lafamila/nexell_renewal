from flask import g
import datetime
from pytz import timezone
def dt_query(query, data, params={}):
    result = dict()
    result['recordsTotal'] = g.curs.execute(query, data)
    result['recordsFiltered'] = result['recordsTotal']


    order_column = None
    ordered = False
    i = 0
    while True:
        if "order[{}][column]".format(i) in params:
            order_column = params["order[{}][column]".format(i)]
            order_column = params["columns[{}][data]".format(order_column)]
            order_dir = params["order[{}][dir]".format(i)]
            if not ordered :
                query += " ORDER BY {} {}".format(order_column, order_dir)
                ordered = True
            else:
                query += " , {} {}".format(order_column, order_dir)
        else:
            break
        i+=1

    if "order[0][column]" not in params and "custom_order" in params:
        query += " ORDER BY "+ ",".join(params["custom_order"])


    if "length" in params and int(params["length"]) > 0:
        query += " LIMIT {}, {}".format(params['start'], params['length'])

    g.curs.execute(query, data)
    result['data'] = g.curs.fetchall()
    for d in result['data']:

        for key in d:
            if type(d[key]) is datetime.datetime or type(d[key]) is datetime.date:
                d[key] = d[key].strftime("%Y-%m-%d")
    return result