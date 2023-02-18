from flask import g
import datetime
def dt_query(query, data, params={}):
    result = dict()
    result['recordsTotal'] = g.curs.execute(query, data)
    result['recordsFiltered'] = result['recordsTotal']


    order_column = None
    if "order[0][column]" in params:
        order_column = params["order[0][column]"]
        order_column = params["columns[{}][data]".format(order_column)]
        order_dir = params["order[0][dir]"]

        query += " ORDER BY {} {}".format(order_column, order_dir)

    if "length" in params and int(params["length"]) > 0:
        query += " LIMIT {}, {}".format(params['start'], params['length'])

    print(query, data)
    g.curs.execute(query, data)
    result['data'] = g.curs.fetchall()
    for d in result['data']:

        for key in d:
            if type(d[key]) is datetime.datetime or type(d[key]) is datetime.date:
                d[key] = d[key].strftime("%Y-%m-%d")
    return result