import os, sys

for subdir, dirs, files in os.walk(os.getenv("PWD")):
    for file in files:
        if ".C" in file and "_fix.C" not in file:
            f = open(file,'r')
            lines = f.readlines()
            g = open(file.replace(".C","_fix.C"),'w')
            for line in lines:

                if "void" in line: 
                    line = line.replace("()","_fix()")
                if "SetMinimum(0)" not in line:
                    g.write(line)
            f.close()
            g.close()