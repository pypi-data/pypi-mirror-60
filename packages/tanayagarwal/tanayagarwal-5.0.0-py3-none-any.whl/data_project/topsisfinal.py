# -*- coding: utf-8 -*-
"""
Created on Sun Jan 19 22:04:04 2020

@author: tanay
"""
import numpy as np
import pandas as pd
import argparse
import sys

def top(X,weights,impacts):
    #exception handling 
    for i in weights:
        if type(i)!=int:
            print(type(i))
            print('Weights should be in int data type')
            sys.exit(0)
            
    for i in impacts:
        if type(i)!=str:
            print(type(i))
            print('impacts should be in str data type')
            sys.exit(0)
            
    if(type(X)!=np.ndarray):
        print("matrix should be pass as a parameter")
        sys.exit(0)
    
    if(len(impacts)!=np.shape(X)[1]):
        print("length of impact parameter is not proper")
        sys.exit(0)
        
    if(len(weights)!=np.shape(X)[1]):
        print("length of weight parameter is not proper")
        sys.exit(0)

    #calculating square root of sum of squares of each column
    col=np.sqrt(np.sum(np.square(X), axis=0))
    
    #normalizing matrix
    for i,j in enumerate(col):
        X[:,i]=np.divide(X[:,i],j)
        
    #multipying each column with its weight
    for i,j in enumerate(weights):
        X[:,i]=X[:,i]*j
      
    #calculating v matrix acc. to weights
    V=np.zeros((2,np.shape(X)[1]))
    for i,j in enumerate(impacts):
        if j=='+':
            V[0][i]=np.max(X[:,i])
            V[1][i]=np.min(X[:,i])
        else:
            V[0][i]=np.min(X[:,i])
            V[1][i]=np.max(X[:,i])
            
    #calculating S matrix   
    S=np.zeros((np.shape(X)[0],5))
    S[:,0]= np.sqrt(np.sum(np.square(X-V[0]),axis=1))
    S[:,1]= np.sqrt(np.sum(np.square(X-V[1]),axis=1))
    S[:,2]=S[:,0]+S[:,1]
    S[:,3]=np.divide(S[:,1],S[:,2])
    l=sorted(S[:,3],reverse=True)
    rank={}
    j=1
    for i in l:
        rank[i]=j
        j+=1
    ans=np.zeros((np.shape(X)[0],2))
    n_row=0
    for i,j in enumerate(S[:,3]):
        ans[i][0]=rank[j]
        ans[i][1]=i+1
        n_row=n_row+1
    
    print("Rank Model")    
    for i in range(0,n_row):
        print(ans[i][0],ans[i][1])
    
def main():
    #taking argument from cmd using parser
    parser=argparse.ArgumentParser(description='Find out the ranking table')
    parser.add_argument("filename",help='Name of the csv file',type=str)
    parser.add_argument('-t',"--tt",help='Enter the weights'  ,nargs="+", type=int)
    parser.add_argument('-a',"--aa",help='Enter the impacts ',nargs='+',type=str)
    args=parser.parse_args()
    file=args.filename
    impacts=args.aa
    weights=args.tt
    data=pd.read_csv(file)
    X=data.iloc[:,1:].values
    
    #topsis executed
    top(X,weights,impacts)
        
if __name__=='__main__':   
   main()