import os,sys,string
oldpath = "root://fndca1.fnal.gov:1094/pnfs/fnal.gov/usr/minerva/persistent/DataPreservation/p6/p6PrimeData/"
newpath = "/minerva/data/ME/p6/p6PrimeData/"
if "MC" in sys.argv[1]:
    oldpath="root://fndca1.fnal.gov:1094/pnfs/fnal.gov/usr/minerva/persistent/DataPreservation/p6/FullDetector/"
    newpath = "/minerva/data/ME/p6/FullDetector/"
f = open(sys.argv[1],'r')
g = open(sys.argv[1].replace(".txt",".sh"),'w')
p = open("../hep01_p6/"+sys.argv[1],'w')
log = sys.argv[1].replace(".txt",".log")
files = f.readlines()
g.write("touch "+log + "\n")
for file in files:
    newloc = file.replace(oldpath,newpath).strip()
    newline = file.replace("root:","xrdcopy root:")
    newline = newline.replace(".root",".root "+newloc+"\n" )
    p.write(newloc+"\n")
    g.write(newline)
    print (newline)

g.close()
p.close()
