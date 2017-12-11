__author__ = 'zjsimon'
from mysqlConn import MySqlConn
import os, pandas as pd, sqlparse
from datetime import datetime


class CatGenome():
    def __init__(self):
        self.qp = "Queries"
        self.conn = MySqlConn()

    def runFile(self, name, **kwargs):
        q = open(os.path.join(self.qp, name), 'r').read().format(**kwargs)
        q = [each for each in sqlparse.split(q) if each]
        for each in q[:-1]: self.conn.safeExecute(each)
        return self.conn.getFrame(q[-1])


def popHeritage():
    gen = CatGenome()
    for i in range(6000):
        s = datetime.now()
        gen.runFile('append_h.txt')
        print datetime.now() - s
        gen.conn.db.commit()


if __name__ == "__main__":
    popHeritage()