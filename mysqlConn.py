# -*- coding: UTF-8 -*-
#!/usr/bin/python
import MySQLdb
import MySQLdb.cursors
import pandas as pd,json



class MySqlConn:
    def __init__(self,db='temp'):
        self.db = MySQLdb.connect(user="root", passwd="",db="mysql",cursorclass=MySQLdb.cursors.DictCursor)
        self.cursor = self.db.cursor()
        self.db.set_character_set('utf8')
        self.cursor.execute("set names utf8;")

    def getFrame(self,q):
        return pd.read_sql(q, con=self.db)

    def insertDF(self,df,table,ins="INSERT"):
        headers = df.columns
        cols = ", ".join(["`{0}`".format(each) for each in df.columns])

        vals=[]
        for each in df.to_dict('records'):
            vals.append("({0})".format( ",".join(["'{0}'".format(each[k]) for k in headers])))

        vals = ",\n".join(vals)



        q = """
        {ins} INTO {table}
        ({cols})
        Values
        {data};
        """.format(table=table,cols=cols,data=vals,ins = ins)
        self.safeExecute(q)

    def safeExecute(self,q):
        try:
            return self.cursor.execute(q)
        except Exception, e:
            print q
            raise e

if __name__ == "__main__":
    conn = MySqlConn()
    print conn.getFrame('show databases;')
    df = pd.DataFrame(json.load(open('data.json')))

    print conn.insertDF(df,'crypto.cats')

