__author__ = 'zjsimon'
from CatGenome import *
import pandas as pd

if __name__ == "__main__":
    gen = CatGenome()
    df = gen.runFile('genProb.txt')
    df['parents'] = df.apply(lambda x:(int(x['x']),int(x['y'])),axis=1)
    piv = df.set_index(['digit','parents'])['prob'].unstack()

    tags = gen.runFile('tagBits.txt').set_index(['digit','tag'])['value'].unstack()
    data = piv.join(tags)

    data.to_csv('probabilities.csv')