# -*- coding: utf-8 -*-
"""
Created on Thu Jan 30 19:19:54 2020

@author: hp
"""

# -*- coding: utf-8 -*-
"""
Created on Thu Jan 30 14:29:17 2020

@author: hp
"""

import pandas as pd
class Dupamb:
    def __init__(self,filename,header=None):
        self.data = pd.read_csv('da.csv',header=header)
        self.d = self.data.iloc[:,:].values
        self.head = self.d[0,:]
        self.d = self.d[1:,:]
    def removeDupAmb(self,outfilename="out.csv"):
        lst = []
        for i in range(0,len(self.d)):
            st = ""
            for j in range(0,len(self.d[i])):
                st = st + str(self.d[i,j]) + " "
            lst.append(st)
        l = set(lst)
        diction = {}
        for i in l:
            if i[i.index(" "):] in diction.keys():
                if diction[i[i.index(" "):]]!=i[0:i.index(" ")]:
                    diction[i[i.index(" "):]]=-1
            else:
                diction[i[i.index(" "):]]=i[0:i.index(" ")]
        k = []
        for i in diction.keys():
            if diction[i]==-1:
                k.append(i)
        for i in k:
            del(diction[i])
        f = open(outfilename,"w")
        f.write(",".join(self.head)+"\n")
        for i in diction.keys():
            f.write(diction[i]+i.rstrip().replace(" ",",")+"\n")
        f.close()