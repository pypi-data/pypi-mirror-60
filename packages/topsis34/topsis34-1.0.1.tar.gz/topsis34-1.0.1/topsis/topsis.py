import numpy as np
import sys
import pandas as pd

#python3 topsis.py data.csv "0.25,0.25,0.25,0.25" "-,+,+,+"
class Topsis:
    data=None
    w = None
    impact = None
    pscore = []
    rank = None
    df = None
    def __init__(self,filename,w,impact):
        self.data = np.loadtxt(filename,delimiter=',')
        self.w = w.split(',' or '"')
        self.impact = impact.split(',' or '"')

    def normalize_with_weights(self):
        for i in range(0,self.data.shape[1]):
            column = self.data[:,i]
            column = [ x/np.sqrt(sum(np.square(column))) for x in column ]
            column = [ x*float(self.w[i]) for x in column ]
            self.data[:,i] = column

    def ideal_best_worst(self):
        p = [] #bests
        n = [] # worst
        for i in range(0,self.data.shape[1]):
            column = self.data[:,i]
            if(self.impact[i]=='+'):
                p.append(np.amax(column,axis=0))
                n.append(np.amin(column,axis=0))
            if(self.impact[i]=='-'):
                p.append(np.amin(column,axis=0))
                n.append(np.amax(column,axis=0))
        return p,n

    def find_pscore(self,p,n):
        dp = [] # euclidean distance from ideal best
        dn = [] # euclidean distance from ideal worst
        for row in self.data:
            num = self.data.shape[1]
            dp.append(np.sqrt(sum( [ (row[i] - p[i])**2 for i in range(0,num) ] )))
            dn.append(np.sqrt(sum( [ (row[i] - n[i])**2 for i in range(0,num) ] )))
            self.pscore.append( dn[-1] / (dp[-1]+dn[-1]) )

    def print_rank(self):
        self.df = pd.DataFrame(self.rank , columns = ["Column Number", "Performance Score", "Rank"])
        print(self.df)

    def calculate_print_rank(self):
        self.normalize_with_weights()
        p,n = self.ideal_best_worst()
        self.find_pscore(p,n)
        sort_p = list( sorted(enumerate(self.pscore,1), key=lambda x:x[1],reverse=True) )
        self.rank = np.array(sort_p)
        num = np.array([[*range(1,self.data.shape[0]+1)]])
        self.rank = np.concatenate((self.rank, num.T), axis=1)
        self.rank = self.rank[self.rank[:,0].argsort()]
        self.print_rank()
