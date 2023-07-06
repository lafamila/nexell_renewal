import pymysql
import os
import decimal
import datetime
from pytz import timezone
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT', "3306")
DB_SCHEME = os.getenv('DB_SCHEME')

class Cursor:
    def __init__(self, cursor):
        self.cursor = cursor

    def execute(self, query, params=tuple()):
        return self.cursor.execute(query, params)

    def executemany(self, query, params=tuple()):
        return self.cursor.executemany(query, params)

    def fetchone(self):
        result = self.cursor.fetchone()
        if result is None:
            return result
        for key, obj in result.items():

            if isinstance(obj, datetime.datetime):
                result[key] = obj.strftime('%Y-%m-%d')

            if isinstance(obj, datetime.date):
                result[key] = obj.strftime('%Y-%m-%d')

            if isinstance(obj, decimal.Decimal):
                result[key] = float(obj)

            if obj is None:
                result[key] = ""

        return result

    def fetchall(self, transform=True):
        result = self.cursor.fetchall()
        if transform:
            for r in result:
                for key, obj in r.items():
                    if isinstance(obj, decimal.Decimal):
                        r[key] = float(obj)

                    if isinstance(obj, datetime.datetime):
                        r[key] = obj.strftime('%Y-%m-%d')
                    if isinstance(obj, datetime.date):
                        r[key] = obj.strftime('%Y-%m-%d')
                    if obj is None:
                        r[key] = ""
        return result

    @property
    def lastrowid(self):
        return self.cursor.lastrowid

    def close(self):
        self.cursor.close()



class DB:
    def __init__(self):
        self.conn = pymysql.connect(host=DB_HOST, user=DB_USER, password=DB_PASSWORD, db=DB_SCHEME, port=int(DB_PORT))

    def is_connected(self):
        return self.conn.open

    def cursor(self):
        curs = self.conn.cursor(pymysql.cursors.DictCursor)
        return Cursor(curs)

    def reconnect(self):
        if self.is_connected():
            self.conn.close()
        self.conn = pymysql.connect(host=DB_HOST, user=DB_USER, password=DB_PASSWORD, db=DB_SCHEME, port=int(DB_PORT))

    def commit(self):
        self.conn.commit()

    def close(self):
        self.conn.close()