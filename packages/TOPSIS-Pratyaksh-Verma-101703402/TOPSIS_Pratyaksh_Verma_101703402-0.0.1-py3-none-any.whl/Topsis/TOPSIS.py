""" Coded by Pratyaksh Verma
    101703402
    3COE - 18
    For Data Analytics and Visualization
    """
import numpy as np
def first(arr):
    sum_1=[]
    n=len(arr)
    m=len(arr[0])
    for i in range(m):
        sum_2=0
        for j in range(n):
            sum_2+=arr[j][i]*arr[j][i]
        sum_1.append(sum_2)
    for i in range(m):
        for j in range(n):
            arr[j][i]=arr[j][i]/sum_1[j]
    return arr

def second(arr,x):
    n=len(arr)
    m=len(arr[0])
    for i in range(n):
        for j in range(m):
            arr[i][j]=arr[i][j]*x[j]
    return arr

#if ch=1, third step and if ch=0, fourth step
def third_fourth(arr,nd,ch):
    n=len(arr)
    m=len(arr[0])
    vg=[]
    maximum=0
    minimum=1e9
    for i in range(m):
        for j in range(n):
            if(nd[i]==ch):
                maximum=max(maximum,arr[j][i])
            else:
                minimum=min(minimum,arr[j][i])
        if(ch==1):
            if(nd[i]==1):
                vg.append(maximum)
            else:
                vg.append(minimum)
        elif(ch==0):
            if(nd[i]==1):
                vg.append(minimum)
            else:
                vg.append(maximum)
    return vg

def fifth(arr,vg):
    n=len(arr)
    m=len(arr[0])
    sg=[]
    for i in range(n):
        sum_1=0
        for j in range(m):
            sum_1+=(vg[i]-arr[i][j])**2
        sg.append(sum_1**0.5)
    return sg

def sixth(arr,vb):
    n=len(arr)
    m=len(arr[0])
    sb=[]
    for i in range(n):
        sum_1=0
        for j in range(m):
            sum_1+=(vb[i]-arr[i][j])**2
        sb.append(sum_1**0.5)
    return sb

def seventh(sg,sb):
    n=len(sg)
    q=[]
    for i in range(n):
        q.append(sb[i]/(sg[i]+sb[i]))
    return q

def eighth(r):
    n=len(r)
    k=r
    k.sort()
    diction={}
    for i in range(0,n):
        diction[k[i]]=n1-i
    for j in range(n):
        r[j]=diction[r[j]]
    return r

#Main TOPSIS Function to be called
def topsis_function(arr,x,need):
    arr=first(arr)
    arr=second(arr,x)
    vg=third_fourth(arr,nd,1)
    #1 is passed for step three
    vb=third_fourth(arr,nd,0)
    #0 is passed for step 4
    sg=fifth(arr,vg)
    sb=sixth(arr,vb)
    p=seventh(sg,sb)
    ranked=eighth(r)
    return ranked
