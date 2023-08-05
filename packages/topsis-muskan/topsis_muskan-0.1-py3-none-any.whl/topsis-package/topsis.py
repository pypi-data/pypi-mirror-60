# -*- coding: utf-8 -*-
"""
Created on Wed Jan 22 13:21:13 2020

@author: MY LAPPY
"""
import sys
import numpy as np
import pandas as pd
import math
from sys import argv
def main():

	s1=argv[1]
	s2=argv[2]
	s3=argv[3]
	s4=s2.split(",")
	s5=s3.split(",")
	mobile=pd.read_csv(s1)
	x=mobile.iloc[:,1:5]
	x=mobile.iloc[:,1:5].values
	x=x.astype(float)
	m=len(x)#no of rows
	n=len(x[0])#no of columns
	a=np.array(float)
	a=np.zeros(shape=(n))
	for i in range(n):
	    for j in range(m):
	        a[i]=a[i]+(x[j][i]*x[j][i])
	    a[i]=a[i]**0.5      
	#print(a)
	for i in range(m):
	    for j in range(n):
	        x[i][j]=x[i][j]*float(s4[j])/a[j]
	        
	#print(x)
	b=np.array(float)
	b=np.zeros(shape=(n))
	#print(b)
	c=np.array(float)
	c=np.zeros(shape=(n))
	#print(c)
	for i in range(n):
	    print(max(x[:,i]))
	    if(s5[i]=='+'):
	        b[i]=max(x[:,i])
	        c[i]=min(x[:,i])
	    else :
	        b[i]=min(x[:,i])
	        c[i]=max(x[:,i])
	#print(b)
	#print(c)
	sp=np.array(float)
	sp=np.zeros(shape=(m))
	sn=np.array(float)
	sn=np.zeros(shape=(m))
	p=np.array(float)
	p=np.zeros(shape=(m))
	for i in range(m):
	    for j in range(n):
	        sp[i]=sp[i]+(x[i][j]-b[j])**2
	        sn[i]=sn[i]+(x[i][j]-c[j])**2
	    sp[i]=math.sqrt(sp[i])
	    sn[i]=math.sqrt(sn[i])
	    p[i]=sn[i]/(sp[i]+sn[i])
	max=p[0]
	mobile["performance"]=p
	mobile["rank"]=mobile["performance"].rank(ascending=False)
	print(mobile)


