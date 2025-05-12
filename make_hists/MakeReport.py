import sys,os
def makereport(path,out):
    items = ["combined","compare","compare_ratio","errors"]
    for i in items:
        newname = path.replace("combined",i)
        newname = newname.replace("postfit_combined","SlowChi2_postfit_combined")
        out.write("\\includegraphics[width=5 in]{%s}\n\n"%newname)
  
name =  sys.argv[1] 
outname = os.path.basename(name.replace("png","tex"))
out = open(outname,'w')
out.write("\\input Header.tex\n")
makereport(name,out)
postname = name.replace("prefit","postfit")
makereport(postname,out)
out.write("\\end{document}\n")

