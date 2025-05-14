#!/usr/bin/env python
# coding: utf-8

TEST = False # only does Enu
DEBUG = False # even more printout
STOP1 = False # just does readin
rescale = True # expect a fit of some sort

import os,sys
from ROOT import TFile,TNamed, TH1D, TCanvas, TMatrixDSym, TVectorD
from PlotUtils import MnvH1D, MnvH2D, MnvPlotter
import commentjson
from SyncBands import SyncBands

print ("have imported common packages")

from MatrixUtils import checktag, ToVectorD, ToMatrixDSym, scaleHist, map2TObjArray, TexFigure3
from GetXSec import GetCrossSection 

from RebinFlux import GetFlux
from plotting_pdf import PlotCVAndError

print ("have imported local packages")

from UnfoldUtils import MnvUnfold, MnvResponse

print ("have gotten UnfoldUtils")

print ("got here")


# In[ ]:





# In[ ]:






# In[ ]:


#include <sstream>

# code to split on any delimiter thanks to stackoverflow
#
# # split (s, delimiter) 
#   size_t pos_start = 0, pos_end, delim_len = delimiter.length()
#   token
#   # res
#
#   while ((pos_end = s.find (delimiter, pos_start)) not = std.string.npos) 
#     token = s.substr (pos_start, pos_end - pos_start)
#     pos_start = pos_end + delim_len
#     res.append (token)
#   
#
#   res.append (s.substr (pos_start))
#   return res
# 

# Main  - this will do set up, loop over events and then make some plots

# def checktag(keys, tag) :
#     count = 0
#     for x in keys:
#         if tag in x: count += 1
#     return count
#     #return std.count(keys.begin(), keys.end(), tag) > 0


def addentry(thing,one,two,three,four,value):
    ''' add entries to a dictionary 4 deep '''
    
    if thing == {}:
        thing[one] = {}
    if one not in thing:
        thing[one] = {}
    if thing[one] == {}:
        thing[one][two] = {}
    if two not in thing[one]:
        thing[one][two] = {}
    if thing[one][two] == {}:
        thing[one][two][three] = {}
    if three not in thing[one][two]:
        thing[one][two][three] = {}
    if thing[one][two][three] == {}:
        thing[one][two][three][four] = value
    if four not in thing[one][two][three]:
        thing[one][two][three][four] = value
    names = value.GetErrorBandNames()
    if len(names) > 0:
        SyncBands(value)
    if DEBUG: print ("added",thing[one][two][three][four].GetName(),one,two,three,four,value.GetName())


# In[ ]:


print ("starting main")
# mainlen(sys.sys.argv), char* sys.argv[]) 
#gROOT.ProcessLine("gErrorIgnoreLevel = kWarning")
#++++++++++++++++++=  Initialization +++++++++++++++++++++++++

targets = 3.23478E30  # nucleons - is this the same for MC or different

inputconfig = "FitAnu.json"
prefit = False
if (len(sys.argv) > 1): 
    #rescale = True
    if ("root") in sys.argv[1]:
        inputname = sys.argv[1]
        prefit = True
    # else:
    #     inputconfig = (sys.argv[1])
    #     inputconfigfile = open(inputconfig,'r')
    #     fitconfig = commentjson.load(inputconfigfile)
    #     inputname = fitconfig["InputFile"]
    #     prefit = False
    #rescale = True

else: 
    print(" arguments are:\n readme  a root file from  a fit")
     
    sys.exit(0)
    #sys.exit(0)
    
    # NuConfig config
    # TFile* f
    # inputname
    # configloc
    # singlesample
    # asample = ""
    # hasbkgsub
    # usetune

    #------------get and store the configs from root or disk

allconfigs = {}

# inputconfigfile = open(inputconfig,'r')
# fitconfig = commentjson.load(inputconfigfile)
# inputname = fitconfig["InputFile"]
# if len(sys.argv) > 1: 
#     print("getting config from root input " , sys.argv[1] )
#     inputname = (sys.argv[1])
# else:
#     inputname = "/Users/schellma/Dropbox/ccqe/BDT2/samples.root"
usetune = False
f = TFile.Open(inputname, "READONLY")
g = TFile.Open(inputname.replace(".root","_out.root"),"RECREATE")

mains = f.Get("main").GetTitle()

#print (mains)
if rescale:
    if not prefit:
        allconfigs["Fit"] = fitconfig
    if prefit: 
        allconfigs["Fit"] = commentjson.loads((f.Get("Fit").GetTitle()))

allconfigs["main"] = commentjson.loads(mains)
allconfigs["varsFile"] = commentjson.loads((f.Get("varsFile").GetTitle()))
allconfigs["cutsFile"] = commentjson.loads((f.Get("cutsFile").GetTitle()))
allconfigs["samplesFile"] = commentjson.loads((f.Get("samplesFile").GetTitle()))
#allconfigs["FitFile"] = commentjson.loads((f.Get("FitFile").GetTitle()))
#print(allconfigs)
AnalyzeVariables = allconfigs["main"]["AnalyzeVariables"]
if "AnalyzeVariables2D" in allconfigs["main"]:
    AnalyzeVariables2D = allconfigs["main"]["AnalyzeVariables2D"]
else:
    AnalyzeVariables2D = []
categoryMap = {}
signalMap = {}
count = 0
if rescale:
    for x in allconfigs["Fit"]["Categories"]:
        categoryMap[x] = count
        count += 1
else:
    categoryMap["qelike"] = 0
    categoryMap["qelikenot"] = 1

if rescale:
    for x in allconfigs["Fit"]["Signal"]:
        signalMap[x] = count
        count += 1
else:
    signalMap["qelike"] = 0
    #SignalMap["qelikenot"] = 1

print (categoryMap)

singlesample = False
# see if the root file has already had fits done - these will be used in the cross section fit.
hasbkgsub = f.Get("fitconfig") != 0

if (len(sys.argv) > 2): 
    usetune = (sys.argv[2])

print ("read in config")
 


# In[ ]:
AnalyzeVariables = allconfigs["main"]
#if TEST: AnalyzeVariables=["Q2QE"]
if (not singlesample): 
    SampleRequest = allconfigs["main"]["runsamples"]
print (SampleRequest)
playlist = allconfigs["main"]["playlist"]

m_fluxUniverses = allconfigs["main"]["fluxUniverses"]

print (playlist)


# In[ ]:


#========================================= now get the histograms

h_flux_dewidthed = MnvH1D()
h_flux_dewidthed = GetFlux(allconfigs)

#h_flux_dewidthed.Print("ALL")


flux = h_flux_dewidthed.Integral()
# # make containers for different analysis levels
# std.map<std.string, MnvH1D> h_flux_ebins

# now loop over histograms, unsmear, efficiency correct and normalize

# unfolding setup
#MinervaUnfold.MnvUnfold unfold
unfold = MnvUnfold()
# MnvH2D MigrationMatrix
num_iter = 5

# input 4 D hist-map

# arguments will be sample, variable, thethetype, category
# order in histogram name is sample___category___variable___thetype
# thetype is reconstructed, truth...
# category is qelike, qelikenot ...



# std.map<std.string, std.map<std.string, std.map<std.string, std.map<std.string, MnvH2D> > > > hists2D

# std.map<std.string, std.map<std.string, std.map<std.string, std.map<std.string, MnvH2D> > > > response1D

# std.map<std.string, std.map<std.string, std.map<std.string, std.map<std.string, MnvH2D> > > > response2D

# f.ls()

# keys



# this is the old read in the POT.  They are also in a vector which Amit like having
h_pot = TH1D()
h_pot = f.Get("POT_summary")
h_pot.Print("ALL")

dataPOT = h_pot.GetBinContent(1)
mcPOTprescaled = h_pot.GetBinContent(3)
POTScale = dataPOT / mcPOTprescaled

norm = 1. / dataPOT / targets
targetobj = TNamed("targets", "%6e"%targets)

print(" integrated luminosity is " , 1 / norm / 1.E24 , "barns^-1" )

print(" POT MC " , mcPOTprescaled )
print(" POT DATA " , dataPOT )

print(" POT Scale",POTScale)


# In[ ]:


hists1D={}
hists2D={}
res1D = {}
types1D = {}
response1D={}
response2D={}
parameters={}
covariance={}

null = MnvH1D("null", "empty histogram", 1, 0., 1.)
null2 = MnvH2D("null2", "empty histogram", 1, 0., 1., 1, 0., 1.)

samples = []
variables = []
categories = []
thetypes = []


# In[ ]:



count = 0
DEBUG=1
keys = []
if not os.path.exists("pix"):
    os.mkdir("pix")
if not os.path.exists("csv"):
    os.mkdir("csv")
keylist = open("keylist.txt",'w')

# first pull out the parameters and covariance

# first get the parameters
for k in f.GetListOfKeys():
    key = k.GetName()
    parsekey = k.GetName().split("___")
    if len(parsekey) < 4: 
        #print(" not a " , k.GetName() )

        continue

    hNd = parsekey[0]
    sample = parsekey[1]
    category = parsekey[2]
    variable = parsekey[3]
    thetype = parsekey[4]
     
    if "parameters" in key:
        hist = MnvH1D()
        hist = f.Get(key)
        parameters[sample] = ToVectorD(hist)
        #addentry(parameters,sample,variable,thetype,category,hist.Clone())
        #parameters[sample][variable][thetype][category] = hist.Clone()
        print ("added parameters",sample)
        # parameters = ToVectorD(hist)
        # parameters.Print()
        continue

    if "covariance" in key:
        hist = MnvH2D()
        hist = f.Get(key)
        covariance[sample] = ToMatrixDSym(hist)
        #addentry(covariance,sample,variable,thetype,category,hist.Clone())
        #parameters[sample][variable][thetype][category] = hist.Clone()
        print ("added Covariance")
        # covariance = ToMatrixDSym(hist)
        # covariance.Print()
        continue

# now do some scaling for MC

skip = ["covariance","parameters","correlation"]
noscale = ["data","all","bkg","bkgsub"]

goodhists = {}
for k in f.GetListOfKeys():
    
    count += 1
    key = k.GetName()
    
    for x in skip:
        if x in key:
            continue
    parsekey = k.GetName().split("___")
    if len(parsekey) < 4: 
        #print(" not a " , k.GetName() )

        continue
    if DEBUG: print ("got a key",key)
    hNd = parsekey[0]
    sample = parsekey[1]
    category = parsekey[2]
    variable = parsekey[3]
    thetype = parsekey[4]
    
    dim = 1

    if "migration" in thetype or "h2D" in hNd:
        hist = MnvH2D()
        dim = 2
    else:
        hist = MnvH1D()
        dim = 1

    if "type_" in key or "types_" in key:
        hist = TH1D()
        dim = 0
    
       

    hist = f.Get(key)
    goodhists[key] = hist
    SyncBands(hist)
    print ("the hist is ", hist)
    #hist.Print()
    dim = 0
    if hist.InheritsFrom("MnvH2D"): dim=2
    elif hist.InheritsFrom("MnvH1D"): dim = 1
    else: dim=0

    if DEBUG and dim==1: 
        print ("errorband",hist.GetName(), hist.GetErrorBandNames())
        hist.Print("ALL")
        hist.MnvH1DToCSV(hist.GetName(),"./csv", 1., False, True, True, True)
    if DEBUG and dim==2: 
        print ("errorband",hist.GetName(), hist.GetErrorBandNames())
        #hist.MnvH2DToCSV(hist.GetName(),"./csv", 1., False, True, True, True)


    if category in ["data","bkgsub"]:  # these can't be POT normalized
        continue
    before = hist.Integral()
    hist.Scale(POTScale)
    after = hist.Integral()
    print ("POTscale",before,after,hist.GetName())
    
    if rescale and category not in noscale:
        newtype = thetype + "_scaledmc"
        newname = key.replace(thetype,newtype)
        print ("dim",dim)
        if sample not in parameters:
            print ("sample",sample, "not in parameters")
            continue
        newres = scaleHist(hist,categoryMap[category], parameters[sample],covariance[sample],newname)
        if newres.InheritsFrom("MnvH1D"):
            print ("band", newres.GetName(), newres.GetErrorBandNames())
        #else:
        #    print ("noband", newres.GetName())
        # addentry(response1D,sample,variable,newtype,category,newres)
        # if DEBUG: print ("made ",newname)
        # response1D[sample][variable][thetype][category].SetDirectory(0)
        # keylist.write(newname+"\n")
        afterscale = newres.Integral()
        if DEBUG and dim==1: 
            print ("errorband2",hist.GetName(), hist.GetErrorBandNames())
            hist.MnvH1DToCSV(hist.GetName(),"./csv", 1., False, True, True, True)
        if DEBUG and dim==2: 
            print ("errorband2",hist.GetName(), hist.GetErrorBandNames())
        #hist.MnvH2DToCSV(hist.GetName(),"./csv", 1., False, True, True, True)


        print ("rescale",after,newres,newres.GetName())
        goodhists[newname]=newres

        
# sort into buckets


for key in goodhists.keys():
    # keylist.write(k.GetName()+"\n")
    # #print(k)
    # count += 1
    # #if count > 400: break
    # keys.append(k.GetName())
    
    if "parameters" in key or "covariance" in key: continue
    if "type_" in key or "types_" in key: continue
    #if DEBUG and "Q2QE" not in key: continue

    parsekey = key.split("___")
    if len(parsekey) < 4: 
        #print(" not a " , k.GetName() )

        continue
    print ("got a key",key)
    hNd = parsekey[0]
    sample = parsekey[1]
    category = parsekey[2]
    variable = parsekey[3]
    thetype = parsekey[4]
    if TEST and variable != "Enu": continue
    
    # build lists of tags
    if not checktag(samples, sample):
        samples.append(sample)
        print(" add a sample: " , sample )

    if not checktag(categories, category): 
        categories.append(category)
        print(" add a category: " , category )
    
    if not checktag(variables, variable): 
        variables.append(variable)
        print(" add a variable: " , variable )
    
    if not checktag(thetypes, thetype):
        thetypes.append(thetype)
        print(" add a thetype: " , thetype )
    
    # get the histogram
    #me = TNamed()
    # me = f.GetKey(key)
    
    if "correlation" in key or ("h___" not in key[0:5] and "h2D___" not in key):
        continue
    if "covariance" in key or "parameters" in key: continue

    #noscale = ["data","all","bkg","bkgsub"]
    #skip = ["covariance","parameters","correlation"]
    # 1D hists
    if "h_" in key[0:2]:
        
        # if response in name its a 2D so do a cast to MnvH2D
        
        if "migration" in key:
            # hist = MnvH2D()
            # hist = (f.Get(key))
            hist = goodhists[key]
            #print ("found migration",key,sample,variable,thetype,category)
            if (hist != 0) and hist != None: 
                addentry(response1D,sample,variable,thetype,category,hist.Clone())
                #response1D[sample][variable][thetype][category].Scale(POTScale)
                # response1D[sample][variable][thetype][category].Print()
                response1D[sample][variable][thetype][category].SetDirectory(0)
                SyncBands(response1D[sample][variable][thetype][category])
                #print(" migration " , sample , " " , variable , " " , thetype , " " , category )
                #delete hist
                # if rescale and category not in noscale:
                #     newtype = thetype + "_scaledmc"
                #     newname = key.replace(thetype,newtype)
                #     newres = MnvH2D()
                #     newres = scaleHist(hist,categoryMap[category], parameters[sample],covariance[sample],newname)
                #     addentry(response1D,sample,variable,newtype,category,newres)
                #     if DEBUG: print ("made ",newname)
                #     response1D[sample][variable][thetype][category].SetDirectory(0)
                #     keylist.write(newname+"\n")
                    
            else: 
                #print("could not read " , key )
                response1D[sample][variable][thetype][category] = 0
            
        
        # it's normal so it's a 1D.
        else: 
            hist = MnvH1D()
            hist = goodhists[key]
            if (hist != 0): 
                if DEBUG: print ("found an h1D", sample,variable,thetype,category,hist.GetName())
                #if (category == "all"):
                    # print ("all", key)
                if "_resolution" in variable:
                    addentry(res1D,sample,variable,thetype,category,hist.Clone())
                    #hists1D[sample][variable][thetype][category].Scale(POTScale)
                    #hists1D[sample][variable][thetype][category].Print()
                    res1D[sample][variable][thetype][category].SetDirectory(0)
                    SyncBands(res1D[sample][variable][thetype][category])
                elif "type_" in variable or "types_" in variable:
                    addentry(types1D,sample,variable,thetype,category,hist.Clone())
                    #hists1D[sample][variable][thetype][category].Scale(POTScale)
                    #hists1D[sample][variable][thetype][category].Print()
                    types1D[sample][variable][thetype][category].SetDirectory(0)
                else:
                    addentry(hists1D,sample,variable,thetype,category,hist.Clone())
                    hists1D[sample][variable][thetype][category].SetDirectory(0)
                    # if rescale and category not in noscale:
                    #     newtype = thetype + "_scaledmc"
                    #     newname = hist.GetName().replace(thetype,newtype)

                    #     newhist = scaleHist(hixt,categoryMap[category], parameters[sample],covariance[sample],newname)
                    #     if DEBUG: print ("rescale",newname)
                    #     addentry(hists1D,sample,variable,newtype,category,newhist)
                    #     hists1D[sample][variable][newtype][category].SetDirectory(0)
                    #     keylist.write(newname+"\n")
                        
            else: 
                #print("could not read " , key )
                hists1D[sample][variable][thetype][category] = 0
    



# 2D hists

    if (hNd == "h2D" or "h2D" in key): 
        # partsof2D = split(variable, "_")
        # hist = MnvH2D()
        # hist = (f.Get(key))
        hist = goodhists[key]
        # Check if response is in its name
        if (hist != 0): 
            if ("migration" in key): 
                addentry(response2D,sample,variable,thetype,category,hist)
                #response2D[sample][variable][thetype][category] = hist.Clone()
                #response2D[sample][variable][thetype][category].Print()
                #response2D[sample][variable][thetype][category].Scale(POTScale)
                response2D[sample][variable][thetype][category].SetDirectory(0)
                #print(" 2D migration " , sample , " " , variable , " " , thetype , " " , category )
                #delete hist
            else: 
                addentry(hists2D,sample,variable,thetype,category,hist)
                #hists2D[sample][variable][thetype][category] = hist.Clone()
                #hists2D[sample][variable][thetype][category].Scale(POTScale)
                #hists2D[sample][variable][thetype][category].Print()
                hists2D[sample][variable][thetype][category].SetDirectory(0)
                #print(" hist 2D " , sample , " " , variable , " " , thetype , " " , category )
                #delete hist
            
        else: 
            #print("could not read " , key )
            if ("migration" in "key"): 
                addentry(response2D,sample,variable,thetype,category,0)
                #hists2D[sample][variable][thetype][category].Scale(POTScale)
                #response2D[sample][variable][thetype][category] = None
            else: 
                addentry(hists2D,sample,variable,thetype,category,0)
                #hists2D[sample][variable][thetype][category] = 0
                

print (samples)
#print (hists1D)

keylist.close()

if STOP1: sys.exit(0)

# In[ ]:
# do not POT normalize after scaling

# for sample in hists1D.keys():
#     for variable in hists1D[sample].keys():
#         if variable not in AnalyzeVariables:
#             continue
#         for thetype in hists1D[sample][variable].keys():
#             for category in hists1D[sample][variable][thetype].keys():
#                 if category in ["data","bkgsub"]: continue
#                 if hists1D[sample][variable][thetype][category] != 0:
#                     hists1D[sample][variable][thetype][category].Scale(POTScale)
#                 # if hists2D[sample][variable][thetype][category] is not None:
#                 #     hists2D[sample][variable][thetype][category].Scale(POTScale)
        
# for sample in response1D.keys():
#     for variable in response1D[sample].keys():
#         if variable not in AnalyzeVariables:
#             continue
#         for thetype in response1D[sample][variable].keys():
#             for category in response1D[sample][variable][thetype].keys():        
#                 if response1D[sample][variable][thetype][category] !=0 : 
#                     response1D[sample][variable][thetype][category].Scale(POTScale)
#             # if response2D[sample][variable][thetype][category] is not None:
#             #     response2D[sample][variable][thetype][category].Scale(POTScale)


# In[ ]:


g.cd()


# In[ ]:


# define the output file
#pdfname
#outroot
stune = "_untuned"
if (usetune): stune = "_tuned"
if (rescale): stune += "_scaledmc"
if (singlesample): 
    outname = inputname[:-5] + "_" +  stune + "_analyze"
    outroot = outname + ".root"

    # set up the outputs
    pdfname = outname
else: 
    outname = inputname[:-5] + stune + "_analyze"
    outroot = outname + ".root"

    # set up the outputs
    pdfname = outname  

o = TFile.Open(outroot, "RECREATE")
targetobj.Write()
h_flux_dewidthed.Write()
pdffilename1D = pdfname + "_1D.pdf"
pdfstart1D = pdfname + "_1D.pdf("
pdfend1D = pdfname + "_1D.pdf)"

pdffilename1Dres = pdfname + "_1Dres.pdf"
pdfstart1Dres = pdfname + "_1Dres.pdf("
pdfend1Dres = pdfname + "_1Dres.pdf)"

pdffilename2D = pdfname + "_2D.pdf"
pdfstart2D = pdfname + "_2D.pdf("
pdfend2D = pdfname + "_2D.pdf)"

o.cd()
for s in hists1D: 
    sample = s 
    for v in hists1D[sample]: 
        variable = v 
        for t in hists1D[sample][variable]: 
            thetype = t 
            for c in hists1D[sample][variable][thetype]: 
                category = c 
                #print(" write out " , hists1D[sample][variable][thetype][category].GetName() )
                hists1D[sample][variable][thetype][category].Write()
                


# In[ ]:





# In[ ]:


print ("samples",samples)
print ("categories",categories)
print ("variables",variables)
print ("thetypes",thetypes)

#print (hists1D)

#print ("about to rescale?")



# if rescale:

#     for sample in samples:
#         for variable in variables:
#             if variable not in AnalyzeVariables:
#                 continue
#             for thetype in usetypes:
#                 newtype = thetype + "scaledmc"
#                 for category in categoryMap.keys():
#                     if category == "data": continue
#                     index = categoryMap[category]
#                     if migration not in thetype:
#                         hist = hists1D[sample][variable][thetype][category]
#                         print ("make rescaled version")
#                         #hist.Print()
#                         newname = hist.GetName().replace(thetype,newtype)
                        
#                         newhist = scaleHist(hist,index, parameters,covariance[sample],newname)
#                         #newhist.Print()
#                         newhist.Write()
#                         newhist.MnvH1DToCSV(newhist.GetName(),"./csv/",1.,False)
#                         addentry(hists1D,sample,variable,newtype,category,newhist)
#                         #hists1D[sample][variable][newtype][category].Print()


mnvPlotter = MnvPlotter()
texname = os.path.basename(inputname.replace(".root",".tex"))
texfile = open(texname,'w')
texfile.write("\\input Header.tex\n")
cF = TCanvas()
basetypes = ["reconstructed","migration","selected_truth","response1D","all_truth"]
usetypes = []
for x in basetypes:
    if usetune:
        if "response" not in x:
            x += "_tuned"
        else:
            x = x.replace("response_migration","response_tuned_migration")
            x = x.replace("response_reco","response_tuned_reco")
            x = x.replace("response_truth","response_tuned_truth")
    if rescale:
        x += "_scaledmc"
    usetypes.append(x)

print ("usetypes",usetypes)

print (" about to rescale ", rescale)
component = {}
for sample in samples:
    for variable in variables:
        if variable not in AnalyzeVariables:
            continue
        for thetype in usetypes:
            #if not rescale and thetype == "reconstructed_scaled": continue
            status = 1
            models = {}
            data = hists1D[sample][variable]["reconstructed"]["data"]
            signal = allconfigs["main"]["signal"][sample]
            if "migration" in thetype: 
                typical = response1D[sample][variable][thetype][signal]
                migration = MnvH2D()
                newname = typical.GetName().replace(signal,"tot")
                migration = typical.Clone(newname)
                for category in categoryMap.keys():
                    component[category] = (hists2D[sample][variable][thetype][category])
                    if component[category] is None: 
                        print ("nothing here",sample,variable,thetype,category)
                        status = 0
                        break
                    migration.Add(component[category],1.)
                if status == 0: continue
                addentry(response1D,sample,variable,thetype,signal,total)
                migration.Print()
                migration.Write()
            else:
                typical = hists1D[sample][variable][thetype][signal]
                total = MnvH1D()
                total = typical.Clone()
                total.SetName(data.GetName().replace("data","tot"))
                total.Reset()
                bkg = MnvH1D()
                bkg = typical.Clone()
                bkg.SetName(data.GetName().replace("data","bkg"))
                bkg.Reset()
                
                for category in categoryMap.keys():
                    models[category] = (hists1D[sample][variable][thetype][category])
                    if models[category] is None: 
                        print ("nothing here",sample,variable,thetype,category)
                        status = 0
                        break
                    total.Add(models[category],1.)
                    if rescale and category in allconfigs["Fit"]["Backgrounds"]:
                        bkg.Add(models[category],1.) 
                    elif category == "qelikenot":
                        bkg.Add(models[category],1.)  
                sig = MnvH1D()
                sig = typical.Clone()
                sig.SetName(data.GetName().replace("data","bkg"))
                sig.Reset() 
                for signal in signalMap.keys():
                    models[signal] = (hists1D[sample][variable][thetype][signal])
                    if models[signal] is None: 
                        print ("nothing here",sample,variable,thetype,signal)
                        status = 0
                        break
                    signal.Add(models[signal],1.)
                    if rescale and signal in allconfigs["Fit"]["Signal"]:
                        sig.Add(models[signal],1.) 
                    elif category == "qelike":
                        sig.Add(models[signal],1.)   

                if status == 0: continue
                addentry(hists1D,sample,variable,thetype,"tot",total)
                addentry(hists1D,sample,variable,thetype,"bkg",bkg)
                addentry(hists1D,sample,variable,thetype,"sig",sig)
                total.Print()
                bkg.Print()
                sig.Print()
            #print ("models",models)
                ModelArray = map2TObjArray(models)
                mnvPlotter.DrawDataStackedMC(data,ModelArray,1.0,"TR")
                cF.Print("pix/%s_%s_%s_%s"%(sample,variable,thetype,"stacked.png"))
                mnvPlotter.DrawDataMCRatio(data,total, 1. )
                cF.Print("pix/%s_%s_%s_%s"%(sample,variable,thetype,"ratio.png"))
                mnvPlotter.DrawDataMCWithErrorBand(data,total, 1., "TR");
                cF.Print("pix/%s_%s_%s_%s"%(sample,variable,thetype,"dataMC.png"))
                mnvPlotter.DrawErrorSummary(bkg);
                cF.Print("pix/%s_%s_%s_%s"%(sample,variable,thetype,"bkg_uncertainty.png"))

                s = TexFigure3(name1="pix/%s_%s_%s_%s"%(sample,variable,thetype,"stacked.png"), name2="pix/%s_%s_%s_%s"%(sample,variable,thetype,"ratio.png"),name3="pix/%s_%s_%s_%s"%(sample,variable,thetype,"dataMC.png"),
                name4="pix/%s_%s_%s_%s"%(sample,variable,thetype,"bkg_uncertainty.png"),caption="%s %s %s"%(sample,variable,thetype),label=None)
                
                texfile.write(s)
                bkg.Write()
                total.Write()
texfile.write("\\end{document}\n")
texfile.close()        
            


# In[ ]:



for sample in samples:
    for variable in variables:
        if variable not in AnalyzeVariables:
            continue
        if variable not in hists1D[sample].keys():
            print ("no variable in data for ",variable)
            continue
    
        print (sample,variable)
        
        tot = hists1D[sample][variable]["reconstructed"]["data"].Clone()
        
        totname =  tot.GetName().replace("data","tot")
        tot.Reset()
        tot.SetName(totname)
        for category in categories:  
            if category in ["all","bkg","bkgsub"]: 
                continue
            tmp = MnvH1D()
            tmp = hists1D[sample][variable]["reconstructed"][category].Clone()
            print ("tmp thetype",type(tmp))
            print (tmp.GetName())
            
            if not tmp: continue
            tot.Add(tmp,1.)
        addentry(hists1D,sample,variable,"reconstructed","tot",tmp)
        tmp.Write()
        tmp.Print()
  

o.cd()
for name,config in allconfigs.items(): 
    print(" write out config " , name)
    obj = commentjson.dumps(config)
    object = TNamed()
    object = TNamed(name, obj)
    object.Write()



canvas1D = TCanvas(pdffilename1D)
canvas1D.SetLeftMargin(0.15)
canvas1D.SetRightMargin(0.15)
canvas1D.SetBottomMargin(0.15)
canvas1D.SetTopMargin(0.15)
canvas1D.Print(pdfstart1D, "pdf")




    # binwid = True  # flag you need if MnvPlotter does not do binwid correction.  If it does not, you need to set this to True

print(" just before 1D loop" ,hists1D.keys())

for sample in hists1D.keys(): 
    print(" Sample: " , sample )
    for variable in hists1D[sample].keys():   # only do this for a subset to save output time.
        print ("Variable: ",variable)
        # if variable not in AnalyzeVariables:
        #     print(" don't do this variable for now" , variable )
        #     continue
        if "_resolution" in variable:
            print ("skip resolution for cross section",variable)
            continue
        print("  Variable: " , variable )
        basename = "h_" + sample + "_" + variable
        if (singlesample): 
            basename = "h_" + variable

        if variable not in response1D[sample].keys() or response1D[sample][variable] == 0:
            print ("no response for",sample,variable,hists1D[sample][variable])
            continue
        
        print("basename is " , basename )
        reallyhasbkgsub = True
        if hasbkgsub and "fitted" not in hists1D[sample][variable].keys():
            reallyhasbkgsub = False 

        print ("response",response1D.keys(),response1D[sample].keys())
        print ("hists",hists1D[sample][variable].keys())
        status = GetCrossSection(sample, variable, basename, hists1D[sample][variable], response1D[sample][variable], allconfigs, canvas1D, norm, POTScale, h_flux_dewidthed, unfold, num_iter, DEBUG, reallyhasbkgsub, usetune, rescale, pdfname)

        if (DEBUG): print(status)
    

print(" end of 1D loop" )
# Close pdf for 1D plots.
canvas1D.Print(pdfend1D, "pdf")

canvas1Dres = TCanvas(pdffilename1Dres)
canvas1Dres.SetLeftMargin(0.15)
canvas1Dres.SetRightMargin(0.15)
canvas1Dres.SetBottomMargin(0.15)
canvas1Dres.SetTopMargin(0.15)
canvas1Dres.Print(pdfstart1Dres, "pdf")
# # resolutions = ("resolution"), ("tuned_resolution")

print ("start of 1D res loop")

for sample in res1D: 
    
    print(" Sample: " , sample )
    for variable in res1D[sample].keys():   # only do this for a subset to save output time.

        
        if "_resolution" not in variable: continue
        #if (variable.find("_resolution"): == std.string.npos): continue

        for resthetype in res1D[sample][variable].keys(): 
            
            print("resthetype " , resthetype )
            if "type" in resthetype:
                continue
            for category in res1D[sample][variable][resthetype].keys(): 
                h = MnvH1D()
                h = res1D[sample][variable][resthetype][category].Clone()
                if (h.GetEntries() == 0): continue
                label = ("resolution_")+sample+"_"+variable+"_"+resthetype+"_"+category
                print ("h type",h.GetName(), type(h))
                PlotCVAndError(canvas1Dres, h, h, label, False, 0, True)
            
        
    


canvas1Dres.Print(pdfend1Dres, "pdf")

# Set up pdf for 2D plots.
canvas2D = TCanvas(pdffilename2D)
canvas2D.SetLeftMargin(0.15)
canvas2D.SetRightMargin(0.15)
canvas2D.SetBottomMargin(0.15)
canvas2D.SetTopMargin(0.15)
canvas2D.Print(pdfstart2D, "pdf")

print(" just before 2D loop" )
for sample in hists2D: 

    for variable in hists2D[sample]:   # only do this for a subset to save output time.
        if not checktag(AnalyzeVariables2D, variable):
            print(" don't do this variable for now" , variable )
            continue
        
        basename = "h2D_" + sample + "_" + variable
        if (singlesample): 
            basename = "h_" + variable
        
        sys.exit = GetCrossSection(sample, variable, basename, hists2D[sample][variable], response2D[sample][variable], allconfigs, canvas2D, norm, POTScale, h_flux_dewidthed, unfold, num_iter, DEBUG, hasbkgsub, usetune, pdfname)
        if (DEBUG): print(sys.exit )
    

print(" end of 2D loop" )
canvas2D.Print(pdfend2D, "pdf")
# Close pdf for 2D plots.

o.Close()
sys.exit(0)

    # if len(sys.argv) < 2:
    #     print ("give me a root file to chew on")
    # else:
    #     main()

