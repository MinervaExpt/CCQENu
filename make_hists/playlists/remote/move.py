import os,sys,string
oldpath = "root://fndca1.fnal.gov:1094/pnfs/fnal.gov/usr/minerva/persistent/users/drut1186/CCQENu_Anatuples/"
newpath = "/minerva/data/ME/"
f = open(sys.argv[1],'r')
g = open(sys.argv[1].replace(".txt",".sh"),'w')
files = f.readlines()
for file in files:
    newloc = file.replace(oldpath,newpath)
    newline = file.replace("root:","nohup xrdcopy root:")
    newline = newline.replace(".root",".root "+newloc)
    g.write(newline)
    print (newline)
