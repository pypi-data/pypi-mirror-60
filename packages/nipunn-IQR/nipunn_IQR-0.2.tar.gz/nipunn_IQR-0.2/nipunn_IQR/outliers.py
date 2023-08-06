# -*- coding: utf-8 -*-
"""
Created on Tue Feb  4 22:47:56 2020

@author: nipunn
"""
def outlying_rows(filename):
    mydataset=pd.read_csv(filename)
    dataset=mydataset.iloc[:,1:]
    shape=np.shape(dataset)
    rows=shape[0]
    coloumns=shape[1]
    lower_bound=[]
    upper_bound=[]
    for i in range(0,coloumns):
      perc25, perc75=np.percentile(sorted(dataset.iloc[:,i]),[25,75])
      iqr=perc75-perc25
      lower_bound.append((perc25-1.5*iqr))
      upper_bound.append((perc75+1.5*iqr))
            
    outlier_rows=[]
    
    for i in range(0,coloumns):
        for j in range(0,rows):
            if dataset.iloc[j,i]<lower_bound[i] or dataset.iloc[j,i]>upper_bound[i]:
                if j not in outlier_rows:
                    outlier_rows.append(j)

    return outlier_rows



def elimrow(filename1,filename2):
    dataset=pd.read_csv(filename1)
    dataset=dataset.iloc[:,1:]
    outlier_rows=outlying_rows(filename1)
    shape=np.shape(dataset)
    rows=shape[0]
    new_dataset=pd.DataFrame()
    for i in range(0,rows):
        if i not in outlier_rows: 
            new_dataset=new_dataset.append(dataset.iloc[i,:])
    new_dataset=new_dataset.iloc[:,1:]
    new_dataset=new_dataset.reset_index(drop=True)
    new_IDs=[]
    for i in range(0,rows-len(outlier_rows)):
        new_IDs.append(i+1)
    new_IDs=pd.Series(new_IDs)
    new_dataset=pd.concat([new_IDs,new_dataset],axis=1)
    
    new_dataset.to_csv(filename2, index=False,)
    
    print(str(len(outlier_rows))+' rows removed')
    print(new_dataset)
    return new_dataset

import pandas as pd
import numpy as np
import sys
if len(sys.argv)>1:
    if len(sys.argv)==3:
        filename1=sys.argv[1]
        filename2=sys.argv[2]
        sa=elimrow(filename1,filename2)
    else:
        print("Enter two arguments: \n 1.INPUT FILE NAME \n 2. OUTPUT FILE NAME" )


