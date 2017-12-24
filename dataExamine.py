__author__ = 'zjsimon'
from CatGenome import *
import pandas as pd

if __name__ == "__main__":
    gen = CatGenome()
    traits = gen.runFile('tagBits.txt')
    prices = gen.conn.getFrame("SELECT * FROM crypto.marketplace m;")
    potCats = gen.runFile('marketplaceGenetics.txt')
    probs = gen.runFile('genProb.txt').fillna(0)
    print probs

    d = {"traits": traits,
         "prices": prices,
         "cats":potCats,
         "prob": probs}

    for k,v in d.iteritems():
        v.to_csv('JuliaData/{0}.csv'.format(k),index=False)
