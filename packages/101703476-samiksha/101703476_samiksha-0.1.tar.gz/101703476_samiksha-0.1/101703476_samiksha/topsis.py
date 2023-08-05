#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jan 19 18:08:36 2020

@author: samikshakapoor
"""

import pandas as pd
import sys
import numpy as np
def main():
    dataset = pd.read_csv(sys.argv[1]).values  #import the dataset
    weights = [int(i) for i in sys.argv[2].split(',')]    #initalize the weights array entered by user
    impacts = sys.argv[3].split(',')  
    topsis(dataset , weights , impacts)                    #initalize impacts array entered by user
#dataset = [[250,16,12,5],[200,16,8,3],[300,32,16,4],[275,32,8,4],[225,16,16,2]]
#output = pd.DataFrame(dataset)
#w = [.25,.25,.25,.25]
#beni = ['-','+','+','+']


def topsis(dataset,weights,benificiary):
    #importing libraries
    import math
#    print(dataset)
    output=pd.DataFrame(dataset)
    a = (output.shape)
    #print(output)
    rows = a[0]
    columns = a[1]
#    print(a)
    #normalizing the dataset
#    dataset = pd.DataFrame(dataset)
#    dataset.astype('float')
#    dataset.to_numpy()
    dataset=np.array(dataset).astype('float32')
    for i in range(0,columns):
        Fsum=0
        for j in range(0,rows):
            Fsum += dataset[j][i]*dataset[j][i]
        Fsum = math.sqrt(Fsum)
        for j in range(0,rows):
            dataset[j][i] = dataset[j][i]/Fsum
#    print(dataset)
#    print(Fsum) 
    #multipling with weights    
    for x in range(0,columns):
        for y in range(0,rows):
            dataset[y][x] *= weights[x]
    #finding worst and best of each column
    #print(dataset)
    vPlus = []
    vMinus = []
    
    def findMin(x,rows):
        m = 100
        for i in range(0,rows):
            if(dataset[i][x]<m):
                m=dataset[i][x]
        return m
    
    def findMax(x,rows):
        m = -1
        for i in range(0,rows):
            if(dataset[i][x]>m):
                m=dataset[i][x]
        return m
    
    for x in range(0,columns):
        if(benificiary[x]=='+'):
           vPlus.append(findMax(x,rows))
           vMinus.append(findMin(x,rows))
    
        else:
            vPlus.append(findMin(x,rows))
            vMinus.append(findMax(x,rows))        
            
    #calculatind the s+ and s- values 
    #computing the performance score for each row     
    def svalue(a,b):
        sub = a-b
        ans = sub**2
        return ans
    
    p = []
    #print(vPlus)
    #print(vMinus)
    for i in range(0,rows):
        sum1 = 0
        sum2 = 0
        for j in range(0,columns):
            sum1 = sum1+svalue(dataset[i][j],vPlus[j])
            sum2 = sum2+svalue(dataset[i][j],vMinus[j])
        sum1 = math.sqrt(sum1)
        sum2 = math.sqrt(sum2)
#        print(sum1)
#        print(sum2)
#        print("*****")
        p.append(sum2/(sum1+sum2))
        
    output['performance score'] = p
    rank = [0 for x in range(rows)]
    count=1
    q = p.copy()
    for i in range(0,rows):
        maxpos = q.index(max(q))
        rank[maxpos] = count
        count=count+1
        q[maxpos]=-1
    
    output['rank'] = rank
    print(output)
    return output



if __name__=="__main__":
    main()