# -*- coding: utf-8 -*-
"""
Created on Sun Jan 19 20:22:17 2020

@author: Sumit 
"""

import pandas as pd
import numpy as np
import scipy.stats as st
import math
from sys import argv


def main():
    if (len(argv[2].split(",")) != len(argv[3].split(","))):
        print("Please Enter Valid Command Line Arguments!!")
        exit(0)
    else:
        file = open(argv[1], 'rb')
        ws = argv[2]
        ws1 = ws.split(",")
        wt = list(map(int, ws1))
        op = argv[3].split(",")
        sqrs = []

        dataset = pd.read_csv(file)
        names = dataset.iloc[:, 0]
        data = dataset.iloc[:, 1:].values
        r = data.shape[0]
        c = data.shape[1]

        for i in range(0, c):
            s1 = 0
            for j in range(0, r):
                s1 = s1 + math.pow(data[j][i], 2)
            s1 = math.sqrt(s1)
            sqrs.append(s1)

        s2 = 0
        for k in range(0, c):
            s2 = s2 + wt[k]

        for k in range(0, c):
            wt[k] = wt[k] / s2

        for i in range(0, c):
            for j in range(0, r):
                data[j][i] = (data[j][i] / sqrs[i]) * wt[i]

        mx1 = []
        mn1 = []
        bst = []
        wrst = []
        l1 = []
        for i in range(0, c):
            l1 = data[:, i]
            mx1 = max(l1)
            mn1 = min(l1)
            if (op[i] == '+'):
                bst.append(mx1)
                wrst.append(mn1)
            elif (op[i] == '-'):
                bst.append(mn1)
                wrst.append(mx1)

        sp = []
        sn = []
        for i in range(0, r):
            sump = 0
            sumn = 0
            for j in range(0, c):
                sump = sump + math.pow((data[i][j] - bst[j]), 2)
                sumn = sumn + math.pow((data[i][j] - wrst[j]), 2)
            sp.append(math.sqrt(sump))
            sn.append(math.sqrt(sumn))
        prfm = []
        for i in range(0, r):
            prfm.append(sn[i] / (sp[i] + sn[i]))

        print("The Preferential order(Rank) is : ")
        rl = list(map(int, len(prfm) - st.rankdata(prfm) + 1))
        for i in range(len(rl)):
            print(names[i], "-->", rl[i])

        res = max(prfm)

        for i in range(0, len(prfm)):
            if prfm[i] == res:
                index = i
        print("Best Option is  : ", names[index])


if __name__ == '__main__':
    main()





