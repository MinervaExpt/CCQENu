import sys,os,string
from ROOT import *
from  PlotUtils import *

scale = 1.E40
binwidth=True
fullprecision = True
syserrors = False
fractionalErrors = True

    

def texheader():
    stex = "\\documentclass[10pt]{article}\n"
    stex += "\\usepackage{rotating, graphicx}"
    stex += "\\begin{document}\n"
    return stex
    
def texender():
    stex = "\\end{document}\n"
    return stex


def read2d(fname):
    f = open(fname,'r')
    print ("reading ",fname)
    cvs = f.read()
    #print (cvs)
    cvs = cvs.split("\n")
    #print (cvs[0],cvs[2])
    if not ("vertdump" in fname or "bins" in fname):
        cv = []
        for i in range(0,len(cvs)-1):
            cvs[i]=cvs[i].strip()
            cv.append(cvs[i].split(","))
            for j in range(0,len(cv[i])):
                cv[i][j] = atof(cv[i][j].strip())
                
    else:
        cv = {}
        for i in range(0,len(cvs)-1):
            #print ("check",cvs[i])
            cvs[i] = cvs[i].strip().split(",")
            name = cvs[i][0]
            if name not in cv:
                cv[name] = []
            row = []
            for j in range(1,len(cvs[i])):
                row.append(atof(cvs[i][j]))
            cv[name].append(row)
                
    #print (fname,cv)
    f.close()
    return cv

def readbins(fname):
    # returns list of name:values
    f = open(fname,'r')
    cvs = f.read()
    #print (cvs)
    cvs = cvs.split("\n")
    #print (cvs[0],cvs[2])
    
    cv = []
    for i in range(0,len(cvs)-1):
        
        cvs[i] = cvs[i].strip().split(",")
        name = cvs[i][0]
        entry = {}
        row = []
        for j in range(1,len(cvs[i])):
            row.append(atof(cvs[i][j]))
        entry["name"] = name
        entry["values"] = row
        cv.append(entry)
                
    # (fname,cv)
    f.close()
    return cv
    
def read1d(fname):
    f = open(fname,'r')
    print ("reading 1d",fname)
    cvs = f.read()
    #print (cvs)
    cvs = cvs.split(",")
    # (cvs[0],cvs[2])
    cv = []
    for i in range(0,len(cvs)):
        cv.append(atof(cvs[i]))
        
    #print (cv)
    f.close()
    return cv

def table2d(xbins,xname,ybins,yname,type,table,caption):
    stex = ""
    nxbins = len(xbins)-1
    nybins = len(ybins)-1
    stex += "\\begin{sidewaystable}\n"
    stex += "\\caption{"+caption+"}\n"
    stex += "\\begin{tabular}{r|"
    for i in range(0,nxbins):
        stex += "r "
    stex += "}\n"
    stex += "\\hline\\hline\n"
    stex += yname.replace("\"","$")
    #print (xbins)
    for j in range(0,nybins):
        stex += "&$%6.3f-$"%(ybins[j])
    stex+="\\\\\n"
    for j in range(0,nybins):
        stex += "&$%6.3f$"%(ybins[j+1])
    stex+="\\\\\n"
    #stex+="\\\\\n"
    stex += xname.replace("\"","$")+"\\quad"
    #for j in range(0,nybins):
    #    stex += "&$%6.3f$"%(ybins[j+1])
    stex+="\\\\\n"
    
    stex+="\\hline"
    corr = 1.0
    if type in ["Stat.","Syst.","Err."] and fractionalErrors:
        corr = 100.
    for i in range(0,nxbins):
        stex+= "$%6.2f-%6.2f$"%(xbins[i],xbins[i+1])
        for j in range(0,nybins):
            #print (len(cv), nxbins,i,len(cv[0]),nybins,j)
            stex += "& %10.2f"%(table[i][j]*corr)
        stex+="\\\\\n"
    stex += "\\end{tabular}\n"
    stex += "\\end{sidewaystable}\n"
    #print (stex)
    return stex

def table1d(xbins,xname,type,table,caption):
    stex = ""
    nxbins = len(xbins)-1
    if type == "End":
        stex += "\\end{tabular}\n"
        stex += "\\end{sidewaystable}\n"
        return stex
    if type == "Start":
        stex += "\\begin{sidewaystable}\n"
        stex += "\\caption{"+caption+"}\n"
        stex += "\\begin{tabular}{r|"
        for i in range(0,nxbins):
            stex += "r "
        stex += "}\n"
        stex += "\\hline\\hline\n"
        stex += xname.replace("\"","$")
    #print (xbins)
    
        for j in range(0,nxbins):
            stex += "&$%6.3f-$"%(xbins[j])
        stex+="\\\\\n"
        for j in range(0,nxbins):
            stex += "&$%6.3f$"%(xbins[j+1])
        stex+="\\\\\n"
        return stex
    
    stex+="\\hline\n"

    #for i in range(0,nxbins):
    #    stex+= "$%6.2f-%6.2f$"%(xbins[i],xbins[i+1])
    stex += type
    for j in range(0,nxbins):
        #print (len(cv), nxbins,i,len(cv[0]),nybins,j)
        stex += "& %10.2f"%(table[j])
    stex+="\\\\\n"
    
    #print (stex)
    return stex
    
def Make1D(hname,outdir,scale,fullprecision,syserrors,fractionalErrors,binwidth):
    
    stex = ""
    
    #stex += texheader()
    oname =  os.path.join(outdir,hname+"_values_1d.csv")
     
    cv = read1d(oname)
    bins = readbins(oname.replace("_values","_bins"))
    #print (bins)
    xname = bins[0]["name"]
    
    xbins = bins[0]["values"]
    
    # (xbins)
    #print (ybins)
    #stex += table1d(xbins,xname,"Start", cv,"Rates $\\times%.2e$"%scale)
    #stex += table1d(xbins,xname,"Rate",cv,"Central values $\\times%.2e$"%scale)
    # (stex)
    covariance = read2d(oname.replace("_values","_covariance"))
    #correlation = read2d(oname.replace("values.csv","_correlation.csv"))
    #vertdump = read2d(oname.replace(".csv","_vertdump.csv"))
    #cv = read2d(oname)
    sname = oname.replace("_values","_staterrors")
    stat = read1d(sname)
  
    #stex += table1d(xbins,xname,"Stat.",stat,"Statistical uncertainties $\\times%.2e$"%scale)
    syst = read1d(oname.replace("_values","_syserrors"))
    #stex += table1d(xbins,xname,"Syst.",syst,"Systematic uncertainties $\\times%.2e$"%scale)
    err = read1d(oname.replace("_values","_errors"))
    #stex += table1d(xbins,xname,"Comb.", err,"Combined systematic and statistical uncertainties $\\times%.2e$"%scale)
    #stex += table1d(xbins,xname,"End", err,"Combined systematic and statistical uncertainties $\\times%.2e$"%scale)
    #print (covariance[0][0],error[0][0]*error[0][0])
    
    stex += table1dr(xbins,xname,cv,stat,syst,err,"Cross section $\\times%.2e$"%scale)
    stex += texender()
    s = open(hname+".tex",'w')
    if "pzmu" in hname or "ptmu" in hname:
        stex = stex.replace("Muon","")
        stex = stex.replace("p_{Z}","p_{||}")
        stex = stex.replace("p_{T}","p_{\\perp}")
        stex = stex.replace("(GeV)$","$(GeV/c)")
    s.write(stex)
    return stex
    
def table1dr(xbins,xname,cv,stat,syst,err,caption):
    stex = ""
    nxbins = len(xbins)-1
    
        
    
    stex += "\\begin{table}\n"
    stex += "\\caption{"+caption+"}\n"
    stex += "\\begin{tabular}{c|r r r r}\n"
    
    stex += "\\hline\n"
    stex += xname.replace("\"","$")
    stex += "&Value&Stat.(\\%)&Syst.(\\%)&Error(\\%)\\\\\n"
    stex += "\\hline\n"
    stex += "\\hline\n"
    for j in range(0,nxbins):
        stex += "$%7.5f-%7.5f$"%(xbins[j],xbins[j+1])
        stex += "&%6.2f"%cv[j]
        stex += "&%6.1f"%(stat[j]*100)
        stex += "&%6.1f"%(syst[j]*100)
        stex += "&%6.1f"%(err[j]*100)
        stex+="\\\\\n"
    stex += "\\hline\n"
    
    stex += "\\end{tabular}\n"
    stex += "\\end{table}\n"
    return stex

if len(sys.argv) < 3:
    print ("arguments are: filename 2Dhistname [significant digits]")
    sys.exit(1)
fname = sys.argv[1]
if not os.path.exists(fname):
    print (fname, "not found")
    sys.exit(1)
    
    
f = TFile.Open(fname,'READONLY')
hname = sys.argv[2]
h = MnvH2D()
h = f.Get(hname)
if h == None:
    print("could not find",hname,"in",fname)
    sys.exit(1)
outdir = (os.path.basename(fname)+"_dump").replace(".root","")
if not os.path.exists(outdir):
    os.makedirs(outdir)
h.SetTitle(h.GetTitle().replace("\nu","\\nu"))

h.GetXaxis().SetTitle(h.GetXaxis().GetTitle().replace("\nu","\\nu"))
h.GetYaxis().SetTitle(h.GetYaxis().GetTitle().replace("\nu","\\nu"))
h.Scale(scale)

if h.InheritsFrom("TH2"):
    

    h.MnvH2DToCSV(hname,outdir,1.0,fullprecision,syserrors,fractionalErrors,binwidth)
    
    

    stex = ""
    stex += texheader()
    oname =  os.path.join(outdir,hname+"_values_2d.csv")
     
    cv = read2d(oname)


    bins = readbins(oname.replace("_values","_bins"))
    #print (bins)
    xname = bins[0]["name"]
    yname = bins[1]["name"]
    xbins = bins[0]["values"]
    ybins = bins[1]["values"]
    # (xbins)
    #print (ybins)
    stex += table2d(xbins,xname,ybins,yname,"CV",cv,"Central values $\\times%.2e$"%scale)
    # (stex)
    covariance = read2d(oname.replace("_values","_covariance"))
    #correlation = read2d(oname.replace("values.csv","_correlation.csv"))
    #vertdump = read2d(oname.replace(".csv","_vertdump.csv"))
    #cv = read2d(oname)
    sname = oname.replace("_values","_staterrors")
    stat = read2d(sname)
    syst = read2d(oname.replace("_values","_syserrors"))
    err = read2d(oname.replace("_values","_errors"))
     
    if fractionalErrors:
        stex += table2d(xbins,xname,ybins,yname,"Stat.",stat,"Statistical uncertainties (\\%)" )
    
        stex += table2d(xbins,xname,ybins,yname,"Syst.",syst,"Systematic uncertainties (\\%)" )
    
        stex += table2d(xbins,xname,ybins,yname,"Err.",err,"Combined systematic and statistical uncertainties (\\%)" )
    else:
        stex += table2d(xbins,xname,ybins,yname,"Stat.",stat,"Statistical uncertainties $\\times%.2e$"%scale)
    
        stex += table2d(xbins,xname,ybins,yname,"Syst.",syst,"Systematic uncertainties $\\times%.2e$"%scale)
    
        stex += table2d(xbins,xname,ybins,yname,"Err.",err,"Combined systematic and statistical uncertainties $\\times%.2e$"%scale)
    #print (covariance[0][0],error[0][0]*error[0][0])
    #stex += texender()
    s = open(hname+".tex",'w')
    if "pzmu" in hname:
        stex = stex.replace("Muon","")
        stex = stex.replace("p_{Z}","p_{||}")
        stex = stex.replace("p_{T}","p_{\\perp}")
        stex = stex.replace("(GeV)$","$(GeV/c)")
    
    
    hx = h.ProjectionX()
    hx.MnvH1DToCSV(hx.GetName(),outdir,1.0,fullprecision,syserrors,fractionalErrors,binwidth)
    hy = h.ProjectionY()
    hy.MnvH1DToCSV(hy.GetName(),outdir,1.0,fullprecision,syserrors,fractionalErrors,binwidth)
    stex+=Make1D(hx.GetName(),outdir,scale,fullprecision,syserrors,fractionalErrors,binwidth)
    stex+=Make1D(hy.GetName(),outdir,scale,fullprecision,syserrors,fractionalErrors,binwidth)
    if "pzmu" in hname:
        stex = stex.replace("Muon","")
        stex = stex.replace("p_{Z}","p_{||}")
        stex = stex.replace("p_{T}","p_{\\perp}")
        stex = stex.replace("(GeV)$","$(GeV/c)")
    stex = stex.replace("#mu","\\mu")
    s.write(stex)
    s.close()
else:
    h.MnvH1DToCSV(h.GetName(),outdir,1.0,fullprecision,syserrors,fractionalErrors,binwidth)
    stex += Make1D(h.GetName(),outdir,1.0,fullprecision,syserrors,fractionalErrors,binwidth)

#    stex = ""
#    stex += texheader()
#    oname =  os.path.join(outdir,hname+"_values_1d.csv")
#
#    cv = read1d(oname)
#    bins = readbins(oname.replace("_values","_bins"))
#    #print (bins)
#    xname = bins[0]["name"]
#
#    xbins = bins[0]["values"]
#
#    # (xbins)
#    #print (ybins)
#    stex += table1d(xbins,xname,"Start", cv,"Rates $\\times%.2e$"%scale)
#    stex += table1d(xbins,xname,"Rate",cv,"Central values $\\times%.2e$"%scale)
#    # (stex)
#    covariance = read2d(oname.replace("_values","_covariance"))
#    #correlation = read2d(oname.replace("values.csv","_correlation.csv"))
#    #vertdump = read2d(oname.replace(".csv","_vertdump.csv"))
#    #cv = read2d(oname)
#    sname = oname.replace("_values","_staterrors")
#    stat = read1d(sname)
#
#    stex += table1d(xbins,xname,"Stat.",stat,"Statistical uncertainties $\\times%.2e$"%scale)
#    syst = read1d(oname.replace("_values","_syserrors"))
#    stex += table1d(xbins,xname,"Syst.",syst,"Systematic uncertainties $\\times%.2e$"%scale)
#    err = read1d(oname.replace("_values","_errors"))
#    stex += table1d(xbins,xname,"Comb.", err,"Combined systematic and statistical uncertainties $\\times%.2e$"%scale)
#    stex += table1d(xbins,xname,"End", err,"Combined systematic and statistical uncertainties $\\times%.2e$"%scale)
#    #print (covariance[0][0],error[0][0]*error[0][0])
#
#    stex += table1dr(xbins,xname,cv,stat,syst,err,"Cross section $\\times%.2e$"%scale)
    #stex += tabender()
    s = open(hname+".tex",'w')
    if "pzmu" in hname or "ptmu" in hname:
        stex = stex.replace("Muon","")
        stex = stex.replace("p_{Z}","p_{||}")
        stex = stex.replace("p_{T}","p_{\\perp}")
        stex = stex.replace("(GeV)$","$(GeV/c)")
    stex.replace("#mu","\\mu")
   
    stex += texender()
    s.write(stex)
    s.close()

