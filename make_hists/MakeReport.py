import sys,os
def makereport(path,out):
    samples = [
        "2track_MultiPionCut"]
    items = ["combined","compare","compare_ratio","errors"]
    timing = ["prefit","postfit"]
    count = 0
    
    for sample in samples:
        for item in items:
            for time in timing:
                newname = path.replace("combined",item)
                newname = newname.replace("QElike_",sample+"_")
                newname = newname.replace("prefit",time)
                if "postfit" in newname:
                    newname = newname.replace("postfit_combined","SlowChi2_postfit_combined")
                print ("newname",item,time,path,newname)
                out.write("\\includegraphics[width=4 in]{%s}\n"%newname)
                if count !=0 and count%2 == 1:
                    out.write("\n")
                    count +=1
  
name =  sys.argv[1] 
outname = os.path.basename(name.replace("png","tex"))
out = open(outname,'w')
out.write("\\input Header.tex\n")
makereport(name,out)
out.write("\\pagebreak\n")
#postname = name.replace("prefit","postfit")
#makereport(postname,out)
out.write("\\end{document}\n")

