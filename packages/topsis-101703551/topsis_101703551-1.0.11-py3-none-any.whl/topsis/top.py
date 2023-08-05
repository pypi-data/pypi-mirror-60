# -*- coding: utf-8 -*-
"""
Created on Sun Jan 19 23:30:59 2020

@author: Brar
"""
import pandas as pd
import sys
import math

def normalise(data):
    n,m=data.shape
    x=data.iloc[0:n,1:m]
    x=x.values.tolist()
    for j in range(0,len(x[0])):
        sumsq=0
        for i in range(0,n):
            sumsq+=x[i][j]*x[i][j]
        for i in range(0,len(x)):
            x[i][j]/=sumsq
    return x
def weighting(x,weight):
    for i in range(0,len(x)):
        for j in range(0,len(x[0])):
            x[i][j]*=weight[j]
    return x
def ideal(x,req):
    li=[]
    for j in range(0,len(x[0])):
        if(req[j]>0):
            can=-1e9
        else:
            can=1e9
        for i in range(0,len(x)):
            if(req[j]>0):
                can=max(can,x[i][j])
            else:
                can=min(can,x[i][j])
        li.append(can)
    return li
def distance(x,req):
    li=[]
    for i in range(0,len(x)):
        dist=0
        for j in range(0,len(x[0])):
            dist+=(x[i][j]-req[j])*(x[i][j]-req[j])
        dist=math.sqrt(dist)
        li.append(dist)
    return li
def performance(spos,sneg):
    li=[]
    for i in range(0,len(spos)):
        tot=(sneg[i]/(spos[i]+sneg[i]))
        li.append([i+1,tot])
    li=sorted(li, key = lambda x: x[1])
    for i in range(0,len(li)):
        li[i][1]=i+1
    return li

def main():
    data=pd.read_csv(sys.argv[1])
    weight=[eval(x) for x in sys.argv[2].split(',')]
    reqstr=[sys.argv[3].split(',')]
    reqpos=[]
    reqneg=[]
    for i in reqstr[0]:
        if(i=='+'):
            reqpos.append(1)
            reqneg.append(-1)
        else:
            reqpos.append(-1)
            reqneg.append(1)
    x=normalise(data)
    x=weighting(x,weight)
    posideal=ideal(x,reqpos)
    negideal=ideal(x,reqneg)
    spos=distance(x,posideal)
    sneg=distance(x,negideal)
    li=performance(spos,sneg)
    
    for i in range(len(li)):
        print("Model "+str(li[i][0])+" ranks "+str(li[i][1]))

main()