import os, sys

if len(sys.argv) < 2:
    print ("need to give me a playlist - I will try 1A if you don't")
    playlist = "minervame1A"
else:
    playlist = sys.argv[1]

print ("playlist is",playlist)

split = 4
data = open("%s_Data.txt"%playlist,'r')
mc = open("%s_MC.txt"%playlist,'r')

datafiles = data.readlines()
mcfiles = mc.readlines()

datacount = len(datafiles)
mccount = len(mcfiles)

datalist = {}
mclist = {}

for x in range(0,split):
    datalist[x]=[]
    mclist[x]=[]

for i in range(0,datacount):
    list = i%split
    datalist[list].append(datafiles[i])

for i in range(0,mccount):
    list = i%split
    mclist[list].append(mcfiles[i])

for x in range(0,split):
    dname = "split/%s_%d_Data.txt"%(playlist,x)
    mname = "split/%s_%d_MC.txt"%(playlist,x)
    d = open(dname,'w')
    m = open(mname,'w')
    for i in range(0,len(datalist[x])):
        d.write(datalist[x][i])
    for i in range(0,len(mclist[x])):
        m.write(mclist[x][i])
    d.close()
    m.close()
    
    
    

    
