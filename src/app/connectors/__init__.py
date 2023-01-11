import pymysql
import os
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT', "3306")
DB_SCHEME = os.getenv('DB_SCHEME')

class DB:
    def __init__(self):
        self.conn = pymysql.connect(host=DB_HOST, user=DB_USER, password=DB_PASSWORD, db=DB_SCHEME, port=int(DB_PORT))

    def is_connected(self):
        return self.conn.open

    def cursor(self):
        curs = self.conn.cursor(pymysql.cursors.DictCursor)
        return curs

    def reconnect(self):
        if self.is_connected():
            self.conn.close()
        self.conn = pymysql.connect(host=DB_HOST, user=DB_USER, password=DB_PASSWORD, db=DB_SCHEME, port=int(DB_PORT))

    def commit(self):
        self.conn.commit()

    def close(self):
        self.conn.close()