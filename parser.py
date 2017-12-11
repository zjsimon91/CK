__author__ = 'zjsimon'
from scraper import *
import json

if __name__ == "__main__":
    ks = KittyScratcher()
    f = open('data.json','w')
    data = []
    i = 0
    print len(ks.ids)
    for each in ks.ids:
        d = ks.getInfo(each)
        data.append(d)
        json.dump(data,f)
        i = i +1

