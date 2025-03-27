import sqlite3
import traceback
import os


class Db:
    def __init__(self):
        self.db_name = os.environ["DB_NAME"]
        self.con = None
        self.cur = None

    def newConnection(self):
        con = sqlite3.connect(self.db_name)
        cur = con.cursor()
        self.con = con
        self.cur = cur

    def closeConnection(self):
        self.con.close()

    def createTables(self):
        self.newConnection()
        fd = open('./dataETL/queries/createTable.sql')
        sqlContents = fd.read()
        fd.close()

        createQueries = sqlContents.split(';')

        for query in createQueries:
            try:
                query = query.replace('\n', '')
                self.cur.execute(query)
            except Exception:
                print(traceback.format_exc())
        
        self.closeConnection()

    def insertData(self, queryArr):
        self.newConnection()
        
        for query in queryArr:
            try:
                self.cur.execute(query)
            except Exception:
                print(traceback.format_exc())

        self.closeConnection()
                

    
db = Db()
db.createTables()