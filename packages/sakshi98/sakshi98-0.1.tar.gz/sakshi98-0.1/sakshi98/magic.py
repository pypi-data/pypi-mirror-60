#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jan 26 16:25:39 2020

@author: sakshi
"""

import pandas as pd
import math
import sys
import scipy.stats as ss
from sklearn.preprocessing import LabelEncoder
#dataset = [[250,16,12,5],[200,16,8,3],[300,32,16,4],[275,32,8,4],[225,16,16,2]]
#w = [.25,.25,.25,.25]
#impact = ['-','+','+','+']
def main():
    dataset = pd.read_csv(sys.argv[1]).values            
#    decision_matrix = dataset[:,1:]
    weights = [float(i) for i in sys.argv[2].split(',')]
    impacts = sys.argv[3].split(',')
    topsis(dataset , weights , impacts)
    
def topsis(dataset,weights,impacts):
    best=[]
    worst=[]
    eubest=[]
    euworst=[]
    rows=None
    columns=None
    array=pd.DataFrame(dataset)
    output=pd.DataFrame(dataset)
    x=(array.shape)
    array=array.astype(dtype=float)
    rows=x[0]
    columns=len(weights)
    array = array.as_matrix()
    for i in range(0,columns):
        sum=0
        max=0
        min=1
        for j in range(0,rows):
            sum=sum+(array[j][i]*array[j][i])
        sum=math.sqrt(sum)
        for k in range(0,rows):
            array[k][i]=array[k][i]/sum
            array[k][i]=array[k][i]*weights[i]
            if array[k][i]>max:
                max=array[k][i]
            if array[k][i]<min:
                min=array[k][i]
        if impacts[i]=="+":
            best.append(max)
            worst.append(min)
        else:
            best.append(min)
            worst.append(max)
    for z in range(0,rows):
        sum=0
        sum2=0
        for t in range(0,columns):
            temp=array[z][t]-best[t]
            temp2=array[z][t]-worst[t]
            temp=temp*temp
            sum=sum+temp
            sum2=sum2+temp2*temp2
        sum=math.sqrt(sum)
        sum2=math.sqrt(sum2)
        eubest.append(sum)
        euworst.append(sum2)    
    result=[]
    
    for g in range(0,rows):
        r=euworst[g]/(euworst[g]+eubest[g])
       
        result.append(r)
    rank = ss.rankdata(result)
    rank = len(rank) - rank +1
    output["performance score"] = result
    output["rank"] = rank
    print(output)
if __name__=="__main__" :
       main()

    
