from flask import g
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

    g.curs.execute(query, data)
    result['data'] = g.curs.fetchall()
    return result