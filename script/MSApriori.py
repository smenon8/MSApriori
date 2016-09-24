
# coding: utf-8
# Authors : Sreejith Menon, Rajan Bhandari
# Email address (smenon8,rbhand4)@uic.edu


from collections import Counter,OrderedDict
import re
import sys

# Method for generating all length subsets of elements in l
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


# Method to parse input files and the parameter file. 
def fileParser(transFileName,paramFileName):
    with open(paramFileName,'r') as param:
        data = [row for row in param]
    minSupDict = {}
    
    # logic for parsing all MIS values
    i = 0
    for i in range(len(data)-3):
        items = list(map(lambda x:x.strip(),data[i].split("=")))
        reSearch = re.search(r'MIS\(?(\w+)\)?',items[0])
        key = reSearch.group(1)
        minSupDict[tuple([key])] = float(items[1])

    items = list(map(lambda x:x.strip(),data[i+1].split("=")))
    sdc = float(items[1])

    items = list(map(lambda x:x.strip(),data[i+2].split(":")))
    cannot_be_together = list(map(lambda x : str(x),list(eval(items[1]))))

    items = list(map(lambda x:x.strip(),data[i+3].split(":")))
    must_have = items[1].split(" or ")

    with open(transFileName,'r') as trans:
        data = [row for row in trans]

    inpData = [list(map(lambda x : str(x),list(eval(line)))) for line in data]  
    return inpData,minSupDict,sdc,cannot_be_together,must_have


def searchInT(t,candid): # t here is a single transaction
    found = True
    for eachCandid in candid:
        if eachCandid[0] not in t:
            found = False

    return found


# Logic for initial pass
def initpass(MS,M,T):   
    cntr =  OrderedDict()

    # Get counts for all individual items
    for item in M:
    	for tx in T:
    		if item[0] in tx:
        		cntr[item] = cntr.get(item,0) + 1
    i = 0
    while M[i] in cntr.keys() and cntr[M[i]]/len(T) < MS[M[i]]:
        i += 1
    
    L = OrderedDict()
    for j in range(i,len(M)):
        if M[j] in cntr.keys() and cntr[M[j]] >= MS[M[i]]:
            L[M[j]] = cntr[M[j]]

    return L

# candidate generation for k = 2
def level2_candidate_gen(L,psi,MS,M,T):
    C = []

    for i in range(0,len(M)-1):
        if M[i] in L.keys() and L[M[i]]/len(T) >= MS[M[i]]:
            for j in range(i+1,len(M)):
                if M[j] in L.keys() and L[M[j]]/len(T)>=MS[M[i]] and abs(L[M[j]]/len(T) - L[M[i]]/len(T)) <= psi:
                    freqitems = []
                    freqitems.append(M[i])
                    freqitems.append(M[j])
                    C.append(tuple(freqitems))
    return C



# Candidate generation for k > 2
def MS_genCandidate(Fk1,psi,count,T,MS): #Fk1 indicates F(k-1), it is a list of lists
    Ck = []
    k1  = len(Fk1[0])

    # print(Fk1)
    # COMBINE STEP
    for i in range(len(Fk1)-1):
        for j in range(i+1,len(Fk1)):
            f1,f2 = Fk1[i],Fk1[j]
            
            if f1[:len(f1)-1] == f2[:len(f2)-1] and MS[f1[-1]] <= MS[f2[-1]] and abs(count[f1[-1]]/len(T) - count[f2[-1]]/len(T)) <= psi:
                tempC = f1 + tuple([f2[-1]])

                # PRUNING STEP
                subset = genSubsets(tempC)
                subset = list(filter(lambda x: len(x) == k1,subset))
                appendSts = True
                for item in subset:
                    if tempC[0] in item or (MS[tempC[0]] == MS[tempC[1]]):
                        if tuple(item) not in Fk1:
                            appendSts = False
                if appendSts:
                    Ck.append(tempC)              
    return Ck


def MS_Apriori(T,MS,psi):
    M = sorted(MS.keys(),key = lambda x:(MS[x],x)) # M is the list of all items in the transaction table sorted by their Min-Support values
    L = initpass(MS,M,T)

    finalSet = []
    count = {}
    tailCount = {}
    
    F = [item for item in L.keys() if L[item]/len(T) >= MS[item]]

    for item in L.keys():
        count[item] = L[item]
        tailCount[item] = 0

    for item in F:
        finalSet.append(item)

    k = 2
    while len(F) != 0:
        tempCount = {}
        F = []
        if k == 2:
            Ck = level2_candidate_gen(L,psi,MS,M,T)
        else:
            Ck = MS_genCandidate(Fk1,psi,count,T,MS)
        
        for t in T:
            for c in Ck:
                if searchInT(t,c):
                    count[tuple(c)] = count.get(tuple(c),0) + 1
                    tempCount[tuple(c)] = tempCount.get(tuple(c),0) + 1
                if searchInT(t,c[1:]):
                    tailCount[tuple(c)] = tailCount.get(tuple(c),0) + 1

        for c in Ck:
            if c in count.keys() and count[tuple(c)]/len(T) >= MS[c[0]]:
                F.append(c)

        for item in F:
            finalSet.append(item)

        Fk1 = F 

        k += 1

    return finalSet,count,tailCount



def applySplConditions(a,cannot_be_together,must_have):
    ss = genSubsets(cannot_be_together)
    ss = list(filter(lambda x : len(x)==2,ss))

    ssTups = []
    for row in ss:
        temp = []
        for item in row:
            temp.append(tuple([item]))
        ssTups.append(tuple(temp))

    filtPatt = []
    for sel in a:
        appendFlag = True
        for sub in ssTups:
            if sub[0] in sel and sub[1] in sel:
                appendFlag = False
        if appendFlag:
            filtPatt.append(sel)

    mustHavTups = []
    for item in must_have:
        mustHavTups.append(tuple([item]))

    finalAns = []
    for item in filtPatt:
        appendFlag = False
        for musts in mustHavTups:
            if len(item) == 1 and item == musts:
                appendFlag = True
            else:
                if musts in item:
                    appendFlag = True
        if appendFlag:
            finalAns.append(item)
            
    return finalAns



def __main__(argv):
    tFile = argv[1]
    pFile = argv[2]
    oFile = argv[3]

    T,MS,psi,cannot_be_together,must_have =  fileParser(tFile,pFile)
    result,count,tailCount= MS_Apriori(T,MS,psi)

    finalAns = applySplConditions(result,cannot_be_together,must_have)


    summary = OrderedDict()
    for ele in finalAns:
        summary[len(ele)] = summary.get(len(ele),0) + 1
        
    with open(oFile,"w") as fl:
        lineNum = 0
        for k in summary.keys():
            print("Frequent %d-itemsets\n" %k)
            fl.write("Frequent %d-itemsets\n\n" %k)
            
            for i in range(summary[k]):
                if len(finalAns[lineNum+i]) > 1:
                    flatList = [item for block in finalAns[lineNum+i] for item in block]
                    eleStr = ",".join(flatList)
                else:
                    eleStr = finalAns[lineNum+i][0]
                
                print("\t" + str(count[finalAns[lineNum+i]]) + " : {%s}"%eleStr)
                fl.write("\t" + str(count[finalAns[lineNum+i]]) + " : {%s}\n"%eleStr)
                
                if len(finalAns[lineNum+i]) > 1:
                    print("Tail Count = %d" %tailCount[finalAns[lineNum+i]])
                    fl.write("Tail Count = %d\n" %tailCount[finalAns[lineNum+i]])
            lineNum += (i+1)  
            print("\n\tTotal number of Frequent %d-itemsets = %d\n" %(k,summary[k]))
            fl.write("\n\tTotal number of Frequent %d-itemsets = %d\n" %(k,summary[k]))
            print()
            fl.write("\n")


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Please provide all parameters, positional parameter #1 - Transactional File, #2 - parameter file, #3 - output file name")
        print(len(sys.argv))
        sys.exit(2)


    __main__(sys.argv)


