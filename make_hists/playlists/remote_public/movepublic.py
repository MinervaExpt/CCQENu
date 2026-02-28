import os,sys,string
oldpath = "root://fndca1.fnal.gov:1095/pnfs/fnal.gov/usr/minerva/persistent/OpenData/MediumEnergy_FHC/Data/"
newpath = "/Volumes/MINERvA_data/minerva/public/Data/"
if "MC" in sys.argv[1]:
    oldpath="root://fndca1.fnal.gov:1095/pnfs/fnal.gov/usr/minerva/persistent/OpenData/MediumEnergy_FHC/MC/StandardMC/"
    newpath = "/Volumes/MINERvA_data/minerva/public/StandardMC/"
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
