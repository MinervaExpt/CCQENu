import sys,os

name = sys.argv[1]

print (name)
f = open(name,'r')

g = open(name.replace(".C",".py"),'w')

def convertline(line):
    newline = line
    if "if" in newline: newline = newline.replace(")","):")
    newline = newline.replace("else","else:")
    newline = newline.replace(".c_str()","")
    newline = newline.replace("argc","len(sys.argv)")
    newline = newline.replace("std::string ","")
    newline = newline.replace("std::string(","(")
    newline = newline.replace("int ","")
    newline = newline.replace("bool ","")
    newline = newline.replace("argv","sys.argv")
    newline = newline.replace("exit","sys.exit")
    newline = newline.replace("std::cout << ","print(")
    newline = newline.replace("<< std::endl;",")")
    newline = newline.replace("<< std::endl;",")")
    newline = newline.replace("std::endl;",")")
    newline = newline.replace("<<",",")
    newline = newline.replace("->",".")
    newline = newline.replace("//","#")
    newline = newline.replace("new NuConfig","")
    #newline = newline.replace("TFile","ROOT.TFile")
    if "for" in line:
        newline = newline.replace("for (", "for").replace(")",":")
    if "auto" in line: 
        newline = newline.replace("auto","").replace(" : "," in ")
    newline = newline.replace("}","").replace("{","")
    newline = newline.replace(".Close",".close")
    newline = newline.replace("true","True").replace("false","False")
    newline = newline.replace("std::vector","")
    newline = newline.replace("<double>","")
    newline = newline.replace("<>","")
    newline = newline.replace("const ","")
    newline = newline.replace("delete","#delete")
    newline = newline.replace("double ","")
    newline = newline.replace("main(","# main")
    newline = newline.replace("!","not ")
    newline = newline.replace(";","")
    newline = newline.replace("::",".")
    newline = newline.replace("push_back","append")
    newline = newline.replace("<std.string>","# fixme")
    newline = newline.replace("atoi","int")
    newline = newline.replace("MnvH1D*","MnvH1D")
    newline = newline.replace("MnvH2D*","MnvH2D")
    
    print (newline)
    return newline


lines = f.readlines()
g.write("import os,sys\n")
g.write("from ROOT import *\n")
g.write("from PlotUtils import *\n")
for line in lines:
    g.write(convertline(line))#+"\n"))

f.close()
g.close()