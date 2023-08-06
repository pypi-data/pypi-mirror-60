import pandas as pd

def topsis(data,weights,b):
    import numpy as np
    import pandas as pd
    import math as math
    
    #convert to the Dataframe
    dataset=pd.DataFrame(data)
    #print(dataset)
    
    #get the no ofrows and columns
    row_count=dataset.shape[0]
    column_count=dataset.shape[1]
    #print(row_count)
    #print(column_count)
    #print(dataset)
    
    
    #Get the root of sum of square values
    
    for i in range(0,column_count) :
        sum=0
        for j in range(0,row_count):
            sum=sum + (dataset.iloc[j,i])*(dataset.iloc[j,i])
        sum=math.sqrt(sum)
        #print(sum)
        #Get the column wise values normalized
        
        for  j in range(0,row_count):
            #print(weights[i])
            k=float(weights[i])/(sum)
            dataset.iloc[j,i]=float(dataset.iloc[j,i]*k)
    #print(dataset)
    
    # Get the V+ AND V- values
    Vp=[]
    Vn=[]
    for i in range(0,column_count):
        if(b[i]=='p'):
            Vp.append(max(dataset.iloc[:,i]))
            Vn.append(min(dataset.iloc[:,i]))
        if(b[i]=='n'):
            Vn.append(max(dataset.iloc[:,i]))
            Vp.append(min(dataset.iloc[:,i]))
    #print(Vp)
    #print(Vn)
    
    # Get S+ & S- Values
    Sp=[]
    Sn=[]
    for i in range(0,row_count):
        p=0
        n=0
        for j in range(0,column_count):
            p=p+(dataset.iloc[i,j]-Vp[j])*(dataset.iloc[i,j]-Vp[j])
            n=n+(dataset.iloc[i,j]-Vn[j])*(dataset.iloc[i,j]-Vn[j])
        p=math.sqrt(p)
        n=math.sqrt(n)
        Sp.append(p)
        Sn.append(n)
    #print(Sp)
    #print(Sn)
    
    Sp=np.array(Sp)
    Sn=np.array(Sn)
    #print(Sp.T)
    #Get performance Score Values
    p=[]
    for i in range(0,row_count):
        t=(Sn[i])/(Sn[i]+Sp[i])
        p.append(t)
    #print(p)
    
    p_temp=p.copy()
    rank=[]
    for i in range(0,row_count):
        rank.append(0)
    m=1
    for i in range(0,row_count):
        ff=max(p_temp)
        sj=p_temp.index(ff)
        p_temp[sj]=-1
        rank[sj]=m
        m=m+1
    
    dataset['topsis score']=p;
    dataset['rank']=rank;
    print(dataset)
    
import sys

def main():
    print(sys.argv)
    weights=[float(i) for i in sys.argv[2].split(',')]
    data=pd.read_csv(sys.argv[1]).values
    b=sys.argv[3].split(',')
    topsis(data,weights,b)

if __name__=="__main__":
    main()