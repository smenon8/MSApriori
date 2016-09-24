# -*- coding: utf-8 -*-
"""
Created on Sun Sep  4 21:00:16 2016

@author: sreejithmenon
"""
from collections import Counter,OrderedDict

def genSubsets(l):
    powerSetSize = 2 ** len(l)
    powerSet = []
    for i in range(1,powerSetSize):
        tempEle = []
        for j in range(len(l)):
            binFlagInd = i & (1 << j)
            if binFlagInd:
                tempEle.append(l[j])
        powerSet.append(tempEle)
    return powerSet


# Apriori Algorithm Implementation
def genCandidate(Fk1): #Fk1 indicates F(k-1), it is a list of lists
    Ck = []
    k1  = len(Fk1[0])

    # COMBINE STEP
    for i in range(len(Fk1)-1):
        for j in range(i+1,len(Fk1)):
            f1,f2 = Fk1[i],Fk1[j]

            if f1[:len(f1)-1] == f2[:len(f2)-1] and f1[-1] < f2[-1]:
                tempC = f1 + [f2[-1]]

                # PRUNING STEP
                subset = genSubsets(tempC)
                subset = list(filter(lambda x: len(x) == k1,subset))
                appendSts = True
                for item in subset:
                    if item not in Fk1:
                        appendSts = False
                if appendSts:
                    Ck.append(tempC)              
    return Ck
    
def initPass(txList): # list of transactions, most possibly a dict
    allTx = [item for tx in txList for item in tx]
    allTx.sort()
    cntr =  OrderedDict()
    for tx in allTx:
        cntr[tx] = cntr.get(tx,0) + 1

    return cntr

def searchInT(t,candid): # t here is a single transaction
    found = True
    for eachCandid in candid:
        if eachCandid not in t:
            found = False

    return found

def apriori(T,minSup):
    finalSet = []
    c1 = initPass(T)
    f = [[item] for item in c1.keys() if c1[item]/len(T) >= minSup] # f1
    
    for item in f:
        finalSet.append(item)

    while len(f) != 0:
        Ck = genCandidate(f)
        # print("Ck")
        # print(Ck)
        freqDict = {}
        for t in T:
            for candidate in Ck:
                if searchInT(t,candidate):
                    freqDict[tuple(candidate)] = freqDict.get(tuple(candidate),0) + 1
        # print("freqDict")
        print(freqDict)
        f = []
        for c in freqDict.keys():
            if freqDict[c]/len(T)>= minSup:
                f.append(list(c))

        # print("f")
        # print(f)
        if len(f) != 0:
            f = sorted(f,key=lambda x : (len(x),*x))
            for item in f:
                finalSet.append(item)
    # print(finalSet)
    return finalSet


T = [
    ['1', '3', '4'],
    ['2', '3', '5'],
    ['1', '2', '3', '5'],
    ['1','2','5']
    ] 

print(apriori(T,0.5))