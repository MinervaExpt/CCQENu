#!/usr/bin/env python
# coding: utf-8

TEST = False # only does Enu
DEBUG = False # even more printout
STOP1 = False # just does readin
#rescale = True # expect a fit of some sort

import os,sys
from ROOT import TFile,TNamed, TH1D, TCanvas, TMatrixDSym, TVectorD
from PlotUtils import MnvH1D, MnvH2D, MnvPlotter
import commentjson
from SyncBands import SyncBands

print ("have imported common packages")

from MatrixUtils import checktag, ToVectorD, ToMatrixDSym, scaleHist, map2TObjArray, TexFigure3
from MakeXSec import GetCrossSection 

from RebinFlux import GetFlux
from plotting_pdf import PlotCVAndError

print ("have imported local packages")

from UnfoldUtils import MnvUnfold, MnvResponse

print ("have gotten UnfoldUtils")

print ("got here")

null = MnvH1D("null", "empty histogram", 1, 0., 1.)
null2 = MnvH2D("null2", "empty histogram", 1, 0., 1., 1, 0., 1.)


def mergeCategories(mapofstuff,listofcats,newtag):
    ''' merge stuff and give it a new name'''
    if DEBUG: print ("merge",newtag,listofcats,mapofstuff.keys())
    if newtag in mapofstuff:
        print ("merge has already happened",newtag)
        return
    first = listofcats[0]
    if first not in mapofstuff.keys():
        print ("mergeCategories error can't find",first,"in",mapofstuff.keys())
        return
    if mapofstuff[first].InheritsFrom("MnvH1D"):
        newhist = MnvH1D()
    
    if mapofstuff[first].InheritsFrom("MnvH2D"):
        newhist=MnvH2D()
    # use the first entry in the inputs as a template
    newname = mapofstuff[first].GetName().replace(first,newtag)          
    newhist = mapofstuff[first].Clone(newname)
    newhist.Reset()
    if DEBUG: print ("mapofstuff",newtag,mapofstuff.keys())
    for cats in listofcats:
        if cats in mapofstuff:
            mapofstuff[cats].Print()
            newhist.Add(mapofstuff[cats])
        else:
            print ("could not add",cats,"to",newname)
    mapofstuff[newtag] = newhist
    return newhist

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



#------------get and store the configs from root or disk

class AnalysisDriver():

    def __init__(self):
        ''' initialyze the analysis driver'''
        self.commandLine()
        self.f = TFile.Open(self.inputname, "READONLY")
        self.g = TFile.Open(self.inputname.replace(".root","_out.root"),"RECREATE")
        
        self.allconfigs = {}
        
        self.allconfigs["main"] = commentjson.loads(self.f.Get("main").GetTitle())
        self.allconfigs["varsFile"] = commentjson.loads((self.f.Get("varsFile").GetTitle()))
        self.allconfigs["cutsFile"] = commentjson.loads((self.f.Get("cutsFile").GetTitle()))
        self.allconfigs["samplesFile"] = commentjson.loads((self.f.Get("samplesFile").GetTitle()))

        self.rescale = self.f.Get("Fit")
        self.hasbkgsub =  False
        if self.rescale:
            self.allconfigs["Fit"] = commentjson.loads((self.f.Get("Fit").GetTitle()))
        else:
            definitions = open("SignalDef.json",'r')
            fitconfig = commentjson.load(definitions)
            self.allconfigs["Fit"] = fitconfig
            self. AnalyzeVariables = self.allconfigs["main"]["AnalyzeVariables"]

        if "AnalyzeVariables2D" in self.allconfigs["main"]:
            self.AnalyzeVariables2D = self.allconfigs["main"]["AnalyzeVariables2D"]
        else:
            self.AnalyzeVariables2D = []

        self.SampleRequest = self.allconfigs["main"]["runsamples"]
        self.singlesample=len(self.SampleRequest)-1
        self.playlist = self.allconfigs["main"]["playlist"]
        self.m_fluxUniverses = self.allconfigs["main"]["fluxUniverses"]

        self.categoryMap = {}
        ## data members

        self.hists1D={}
        self.hists2D={}
        self.res1D = {}
        self.types1D = {}
        self.response1D={}
        self.response2D={}
        self.parameters={}
        self.covariance={}
                
        self.samples = []
        self.variables = []
        self.categories = []
        self.thetypes = []

        self.h_pot = TH1D()
        self.POTScale = 0.0
        self.targets = 3.23478E30 
        self.h_flux_dewidthed = MnvH1D()
        # these don't work to well 
        self.skipVariables=["RecoTrueEnuRatio","TrueEnuDiffGeV","TrueEnuRatio"]

    def commandLine(self):
        print ("starting main")

        #++++++++++++++++++=  Initialization +++++++++++++++++++++++++

         # nucleons - is this the same for MC or different
        self.usetune = 0

        if (len(sys.argv) > 2): 
            self.usetune = (sys.argv[2])

        if (len(sys.argv) > 1) and ("root") in sys.argv[1]: 
            self.inputname = sys.argv[1]
        else: 
            print(" arguments are:\n readme  a root file to analyze")     
            sys.exit(0)


# def GetConfig
# self.allconfigs = {}

# usetune = False
# f = TFile.Open(inputname, "READONLY")
# g = TFile.Open(inputname.replace(".root","_out.root"),"RECREATE")

# mains =  self.f.Get("main").GetTitle()
# rescale =  self.f.Get("Fit")

# # get the info from the fit if available, otherwise need to read it in. 

# if rescale:
#     self.allconfigs["Fit"] = commentjson.loads((f.Get("Fit").GetTitle()))
# else:
#     definitions = open("SignalDef.json",'r')
#     fitconfig = commentjson.load(definitions)
#     self.allconfigs["Fit"] = fitconfig

# self.allconfigs["main"] = commentjson.loads(mains)
# self.allconfigs["varsFile"] = commentjson.loads((f.Get("varsFile").GetTitle()))
# self.allconfigs["cutsFile"] = commentjson.loads((f.Get("cutsFile").GetTitle()))
# self.allconfigs["samplesFile"] = commentjson.loads((f.Get("samplesFile").GetTitle()))




#categoryMap = {}
#signalMap = {}
#count = 0

    def categorymaps(self):
        ''' translate the list of categories into parameter numbers'''
        count = 0
        if self.rescale:
            for x in self.allconfigs["Fit"]["Categories"]:
                self.categoryMap[x] = count
                count += 1
        else:
            self.categoryMap["qelike"] = 0
            self.categoryMap["qelikenot"] = 1
    
        print (self.categoryMap)

#singlesample = False

# see if the root file has already had fits done - these will be used in the cross section fit.

# hasbkgsub =  self.f.Get("fitconfig") != 0

# if (len(sys.argv) > 2): 
#     usetune = (sys.argv[2])

# print ("read in config")




#========================================= now get the histograms

    def loadFlux(self):
        self.h_flux_dewidthed = GetFlux(self.allconfigs)
        self.flux = self.h_flux_dewidthed.Integral()

# # make containers for different analysis levels

# now loop over histograms, unsmear, efficiency correct and normalize

# unfolding setup

    def setUnfold(self):

        self.unfold = MnvUnfold()
        self.num_iter = 5

# input 4 D hist-map

# arguments will be sample, variable, thethetype, category
# order in histogram name is sample___category___variable___thetype
# thetype is reconstructed, truth...
# category is qelike, qelikenot ...

# this is the old read in the POT.  They are also in a vector which Amit like having

    def POTInfo(self):
        
        self.h_pot =  self.f.Get("POT_summary")
        if DEBUG: 
            self.h_pot.Print("ALL")

        dataPOT =  self.h_pot.GetBinContent(1)
        mcPOTprescaled =  self.h_pot.GetBinContent(3)
        self.POTScale = dataPOT / mcPOTprescaled
        self.norm = 1. / dataPOT / self.targets
        self.targetobj = TNamed("targets", "%6e"%self.targets)

        print(" integrated luminosity is " , 1 / self.norm / 1.E24 , "barns^-1" )

        print(" POT MC " , mcPOTprescaled )
        print(" POT DATA " , dataPOT )

        print(" POT Scale",self.POTScale)

# self.hists1D={}
# hists2D={}
#  self.res1D = {}
# types1D = {}
# response1D={}
# response2D={}
# parameters={}
# covariance={}

# null = MnvH1D("null", "empty histogram", 1, 0., 1.)
# null2 = MnvH2D("null2", "empty histogram", 1, 0., 1., 1, 0., 1.)

# samples = []
# variables = []
# categories = []
# thetypes = []

# count = 0
# DEBUG=False
# keys = []

    def mkdirs(self):
        if not os.path.exists("pix"):
            os.mkdir("pix")
        if not os.path.exists("csv"):
            os.mkdir("csv")

    def parsekeys(self):
        ''' go through the data and figure out what is in it'''
        self.keylist = open("keylist.txt",'w')

        for k in self.f.GetListOfKeys():
            key = k.GetName()
            parsekey = k.GetName().split("___")
            if len(parsekey) < 4: 
                print(" not a " , k.GetName() )
                continue
            if TEST: print ("check a key",key)
            hNd = parsekey[0]
            sample = parsekey[1]
            category = parsekey[2]
            variable = parsekey[3]
            thetype = parsekey[4]
    
            
            if "parameters" in key:
                hist = MnvH1D()
                hist =  self.f.Get(key)
                self.parameters[sample] = ToVectorD(hist)
                print ("added parameters",sample)
                continue

            if "covariance" in key:
                hist = MnvH2D()
                hist =  self.f.Get(key)
                self.covariance[sample] = ToMatrixDSym(hist)
                print ("added Covariance")
                continue

# now read in the histograms and POT scale them

    def scaleMC(self):
        ''' read in hists, POT scale and then scale by parameters - put in goodhists list'''
        skip = ["covariance","parameters","correlation"]
        noscale = ["data","all","bkg","bkgsub"]
        count = 0
        self.goodhists = {}
        for k in self.f.GetListOfKeys():           
            count += 1
            key = k.GetName()
            
            for x in skip:
                if x in key:
                    continue
            parsekey = k.GetName().split("___")
            if len(parsekey) < 4: 
                #print(" not a " , k.GetName() )

                continue
            #if DEBUG: print ("got a key",key)
            hNd = parsekey[0]
            sample = parsekey[1]
            category = parsekey[2]
            variable = parsekey[3]
            thetype = parsekey[4]

            if variable in self.skipVariables or "resolution" in variable:
                print ("skipping",variable)
                continue

            if TEST and variable != "Enu": continue
            if self.rescale and sample not in self.parameters:
                    print ("sample",sample, "not in parameters")
                    continue
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
            
            hist = self.f.Get(key)
            self.goodhists[key] = hist
            SyncBands(hist)
            #print ("the hist is ", hist)

            dim = 0
            if hist.InheritsFrom("MnvH2D"): 
                dim = 2
            elif hist.InheritsFrom("MnvH1D"): 
                dim = 1
            else: 
                dim=0

            if DEBUG and dim==1: 
                print ("errorband",hist.GetName(), hist.GetErrorBandNames())
                hist.Print("ALL")
                hist.MnvH1DToCSV(hist.GetName(),"./csv", 1., False, True, True, True)
            if DEBUG and dim==2: 
                print ("errorband",hist.GetName(), hist.GetErrorBandNames())
                hist.MnvH2DToCSV(hist.GetName(),"./csv", 1., False, True, True, True)

            if category in ["data","bkgsub"]:  # these can't be POT normalized
                continue
            before = hist.Integral()
            hist.Scale(self.POTScale)
            after = hist.Integral()
            print ("POTscale",before,after,hist.GetName())

            if "scaledmc" in thetype:
                print("already rescaled",hist.GetName())
                self.goodhists[newname]=hist.GetName()
                continue

            if self.rescale and category not in noscale:
                newtype = thetype + "_scaledmc"
                newname = key.replace(thetype,newtype)
                #print ("dim",dim)
                
                newres = scaleHist(hist,self.categoryMap[category], self.parameters[sample],self.covariance[sample],newname)
                
                #addentry(hists1D,sample,category,variable,thetype,newres)

                if DEBUG and newres.InheritsFrom("MnvH1D"):
                    print ("band", newres.GetName(), newres.GetErrorBandNames())

                afterscale = newres.Integral()
                if DEBUG and dim==1: 
                    print ("errorband1",hist.GetName(), hist.GetErrorBandNames())
                    hist.MnvH1DToCSV(hist.GetName(),"./csv", 1., False, True, True, True)
                if DEBUG and dim==2: 
                    print ("errorband2",hist.GetName(), hist.GetErrorBandNames())
                    hist.MnvH2DToCSV(hist.GetName(),"./csv", 1., False, True, True, True)
                

                print ("rescaled",after,newres,newres.GetName())
                self.goodhists[newname]=newres

    def zeroPOT(self):
        self.POTScale = 1.0
        
# sort into buckets

    def mapHists(self):
        ''' sort the histograms and put into a map'''

        for key in self.goodhists.keys():          
            if "parameters" in key or "covariance" in key: continue
            if "type_" in key or "types_" in key: continue
            parsekey = key.split("___")
            if len(parsekey) < 4: 
                continue

            hNd = parsekey[0]
            sample = parsekey[1]
            category = parsekey[2]
            variable = parsekey[3]
            thetype = parsekey[4]
            
            
            # build lists of tags
            if not checktag(self.samples, sample):
                self.samples.append(sample)
                #print(" add a sample: " , sample )

            if not checktag(self.categories, category): 
                self.categories.append(category)
                #print(" add a category: " , category )
            
            if not checktag(self.variables, variable): 
                self.variables.append(variable)
                #print(" add a variable: " , variable )
            
            if not checktag(self.thetypes, thetype):
                self.thetypes.append(thetype)
                #print(" add a thetype: " , thetype )
            
            if "correlation" in key or ("h___" not in key[0:5] and "h2D___" not in key):
                continue
            if "covariance" in key or "parameters" in key: 
                continue


            # 1D hists
            if "h_" in key[0:2]:
                
                # if response in name its a 2D so do a cast to MnvH2D
                
                if "migration" in key:
                    
                    hist = self.goodhists[key]
                    print ("found migration",key,sample,variable,thetype,category)
                    if (hist != 0) and hist != None: 
                        addentry(self.response1D,sample,variable,thetype,category,hist.Clone())
                
                        self.response1D[sample][variable][thetype][category].SetDirectory(0)
                        SyncBands(self.response1D[sample][variable][thetype][category])
                            
                    else: 
                        print("could not read " , key )
                        self.response1D[sample][variable][thetype][category] = 0
                    
                
                # it's normal so it's a 1D.
                else: 
                    hist = MnvH1D()
                    hist = self.goodhists[key]
                    if (hist != 0): 
                        if DEBUG: print ("found an h1D", sample,variable,thetype,category,hist.GetName())
                        
                        if "_resolution" in variable:
                            addentry(self.res1D,sample,variable,thetype,category,hist.Clone())
                            
                            self.res1D[sample][variable][thetype][category].SetDirectory(0)
                            SyncBands(self.res1D[sample][variable][thetype][category])
                        elif "type_" in variable or "types_" in variable:
                            addentry(self.types1D,sample,variable,thetype,category,hist.Clone())
                        
                            self.types1D[sample][variable][thetype][category].SetDirectory(0)
                        else:
                            addentry(self.hists1D,sample,variable,thetype,category,hist.Clone())
                            self.hists1D[sample][variable][thetype][category].SetDirectory(0)
                                
                    else: 
                        #print("could not read " , key )
                        self.hists1D[sample][variable][thetype][category] = 0
            



        # 2D hists

            if (hNd == "h2D" or "h2D" in key): 
                
                hist = self.goodhists[key]
                # Check if response is in its name
                if (hist != 0): 
                    if ("migration" in key): 
                        addentry(self.response2D,sample,variable,thetype,category,hist)
                        
                        self.response2D[sample][variable][thetype][category].SetDirectory(0)
                        
                    else: 
                        addentry(self.hists2D,sample,variable,thetype,category,hist)
            
                        self.hists2D[sample][variable][thetype][category].SetDirectory(0)
                
                    
                else: 
                    #print("could not read " , key )
                    if ("migration" in "key"): 
                        addentry(self.response2D,sample,variable,thetype,category,0)
                        
                    else: 
                        addentry(self.hists2D,sample,variable,thetype,category,0)
                        
                    
        self.keylist.close()

#if STOP1: sys.exit(0)



    def makeoutfile(self):
        self.g.cd()

        stune = "_untuned"
        if (self.usetune): stune = "_tuned"
        if (self.rescale): stune += "_scaledmc"
        if (self.singlesample): 
            self.outname = self.inputname[:-5] + "_" +  stune + "_analyze"
            self.outroot = self.outname + ".root"

            # set up the outputs
            self.pdfname = self.outname
        else: 
            self.outname = self.inputname[:-5] + stune + "_analyze"
            self.outroot = self.outname + ".root"

            # set up the outputs
            self.pdfname = self.outname  

        self.o = TFile.Open(self.outroot, "RECREATE")
        self.targetobj.Write()
        self.h_flux_dewidthed.Write()
        

        

        

        self.o.cd()
        for s in self.hists1D: 
            sample = s 
            for v in self.hists1D[sample]: 
                variable = v 
                for t in self.hists1D[sample][variable]: 
                    thetype = t 
                    for c in self.hists1D[sample][variable][thetype]: 
                        category = c 
                        self.hists1D[sample][variable][thetype][category].Write()
                        

# print ("samples",samples)
# print ("categories",categories)
# print ("variables",variables)
# print ("thetypes",thetypes)


        self.mnvPlotter = MnvPlotter()
        self.texname = os.path.basename(self.inputname.replace(".root",".tex"))
        self.texfile = open(self.texname,'w')
        self.texfile.write("\\input Header.tex\n")
        self.cF = TCanvas()

    def combine(self):
        ''' merge types to make signal and background samples'''
        basetypes = ["reconstructed","response_migration","selected_truth","response1D","all_truth","response_reco","response_truth"]
        self.usetypes = []
        for x in basetypes:
            if self.usetune:
                if "response" not in x:
                    x += "_tuned"
                else:
                    x = x.replace("response_migration","response_tuned_migration")
                    x = x.replace("response_reco","response_tuned_reco")
                    x = x.replace("response_truth","response_tuned_truth")
            if self.rescale:
                x += "_scaledmc"
            self.usetypes.append(x)

        print ("usetypes",self.usetypes)

        print (" about to combine samples ", self.rescale)
        component = {}
        for sample in self.samples:
            print ("sample",sample)
            for variable in self.variables:
                print ("variable",variable)
                for thetype in self.usetypes:
                    print ("merging",sample,variable,thetype)
                    status = 1
                    models = {}
                    if self.hists2D and variable in self.hists2D[sample]:
                        continue
                    data = self.hists1D[sample][variable]["reconstructed"]["data"]
                    #signal = self.allconfigs["main"]["signal"][sample]
                    signals =  self.allconfigs["Fit"]["Signal"]
                    categories = self.allconfigs["Fit"]["Categories"]
                    backs = []
                    for x in categories:
                        if x not in signals:
                            backs.append(x)
                    print ("sorting",signals,categories,backs)
                    if "migration" in thetype: 
                        if thetype in self.response1D[sample][variable]:
                            mergeCategories(self.response1D[sample][variable][thetype],signals,"sig")
                        else:
                            print (thetype,"not there for",sample,variable,self.response1D[sample][variable].keys())
                            continue
                    else:
                        
                        if thetype not in self.hists1D[sample][variable]:
                            print (thetype,"not there for",sample,variable,self.hists1D[sample][variable].keys())
                            continue

                        sig = mergeCategories(self.hists1D[sample][variable][thetype],signals,"sig")
                        if "reconstructed" in thetype:
                            total = mergeCategories(self.hists1D[sample][variable][thetype],categories,"tot")
                            bkg = mergeCategories(self.hists1D[sample][variable][thetype],backs,"bkg")
                        else:
                            total = 0
                            bkg = 0
                        
                        
                        for category in categories:
                            if thetype in self.hists1D[sample][variable].keys() and category in self.hists1D[sample][variable][thetype]:
                                models[category] = (self.hists1D[sample][variable][thetype][category])

                        
                        print ("check",sample,variable,thetype)
                        if "reconstructed" in thetype: 
                            bkg.Print()
                            total.Print()
                        else:
                            bkg=null
                            total=sig
                        sig.Print()
                        sig.Write()
                #print ("models",models)
                        if("reconstructed" in thetype):
                            self.ModelArray = map2TObjArray(models)
                            #mnvPlotter.DrawDataStackedMC(data,ModelArray,1.0,"TR")
                            # cF.Print("pix/%s_%s_%s_%s"%(sample,variable,thetype,"stacked.png"))
                            # mnvPlotter.DrawDataMCRatio(data,total, 1. )
                            # cF.Print("pix/%s_%s_%s_%s"%(sample,variable,thetype,"ratio.png"))
                            # mnvPlotter.DrawDataMCWithErrorBand(data,total, 1., "TR");
                            # cF.Print("pix/%s_%s_%s_%s"%(sample,variable,thetype,"dataMC.png"))
                            
                            # mnvPlotter.DrawErrorSummary(bkg);
                            # cF.Print("pix/%s_%s_%s_%s"%(sample,variable,thetype,"bkg_uncertainty.png"))

                            # s = TexFigure3(name1="pix/%s_%s_%s_%s"%(sample,variable,thetype,"stacked.png"), name2="pix/%s_%s_%s_%s"%(sample,variable,thetype,"ratio.png"),name3="pix/%s_%s_%s_%s"%(sample,variable,thetype,"dataMC.png"),
                            # name4="pix/%s_%s_%s_%s"%(sample,variable,thetype,"bkg_uncertainty.png"),caption="%s %s %s"%(sample,variable,thetype),label=None)
                            
                            # texfile.write(s)
                            bkg.Write()
                            total.Write()
        # texfile.write("\\end{document}\n")
        # texfile.close()        
            

# for sample in samples:
#     for variable in variables:
#         if variable not in AnalyzeVariables:
#             continue
#         if variable not in self.hists1D[sample].keys():
#             print ("no variable in data for ",variable)
#             continue
    
#         print (sample,variable)
        
#         tot = self.hists1D[sample][variable]["reconstructed"]["data"].Clone()
        
#         totname =  tot.GetName().replace("data","tot")
#         tot.Reset()
#         tot.SetName(totname)
#         for category in categories:  
#             if category in ["all","bkg","bkgsub"]: 
#                 continue
#             tmp = MnvH1D()
#             tmp = self.hists1D[sample][variable]["reconstructed"][category].Clone()
#             print ("tmp thetype",type(tmp))
#             print (tmp.GetName())
            
#             if not tmp: continue
#             tot.Add(tmp,1.)
#         addentry(hists1D,sample,variable,"reconstructed","tot",tmp)
#         tmp.Write()
#         tmp.Print()
  
    def writeConfigs(self):
        self.o.cd()
        for name,config in self.allconfigs.items(): 
            print(" write out config " , name)
            obj = commentjson.dumps(config)
            object = TNamed()
            object = TNamed(name, obj)
            object.Write()


    def opencanvas1D(self):
        self.pdffilename1D = self.pdfname + "_1D.pdf"
        pdfstart1D = self.pdffilename1D+"("
        pdfend1D = self.pdffilename1D+")"
        self.canvas1D = TCanvas(self.pdffilename1D)
        self.canvas1D.SetLeftMargin(0.15)
        self.canvas1D.SetRightMargin(0.15)
        self.canvas1D.SetBottomMargin(0.15)
        self.canvas1D.SetTopMargin(0.15)
        self.canvas1D.Print(pdfstart1D, "pdf")




     #it does not, you need to set this to True

    def Loop1D(self):
        print(" just before 1D loop" ,self.hists1D.keys())

        #if TEST: sys.exit(1)

        for sample in self.hists1D.keys(): 
            print(" Sample: " , sample )
            for variable in self.hists1D[sample].keys():   # only do this for a subset to save output time.
                print ("Variable: ",variable)
                # if variable not in AnalyzeVariables:
                #     print(" don't do this variable for now" , variable )
                #     continue
                if "_resolution" in variable:
                    print ("skip resolution for cross section",variable)
                    continue
                print("  Variable: " , variable )
                basename = "h_" + sample + "_" + variable
                if (self.singlesample): 
                    basename = "h_" + variable

                if variable not in self.response1D[sample].keys() or self.response1D[sample][variable] == 0:
                    print ("no response for",sample,variable,self.hists1D[sample][variable])
                    continue
                
                print("basename is " , basename )
                self.reallyhasbkgsub = True
                if self.hasbkgsub and "fitted" not in self.hists1D[sample][variable].keys():
                    self.reallyhasbkgsub = False 

                print ("response",self.response1D.keys(),self.response1D[sample].keys())
                print ("hists",self.hists1D[sample][variable].keys())
                status = GetCrossSection(sample, variable, basename, self.hists1D[sample][variable], self.response1D[sample][variable], self.allconfigs, self.canvas1D,  self.norm, self.POTScale, self.h_flux_dewidthed, self.unfold, self.num_iter, DEBUG, self.reallyhasbkgsub, self.usetune, self.rescale, self.pdfname)

                if (DEBUG): print(status)
            

        print(" end of 1D loop" )
# Close pdf for 1D plots.

    def close1DCanvas(self):
        pdfend1D = self.pdffilename1D+")"
        self.canvas1D.Print(pdfend1D, "pdf")

        
# # resolutions = ("resolution"), ("tuned_resolution")

    def plotRes(self):
        self.pdffilename1Dres = self.pdfname + "_1Dres.pdf"
        pdfstart1Dres = self.pdffilename1Dres+"("
        pdfend1Dres = self.pdffilename1Dres+")"
        self.canvas1Dres = TCanvas(self.pdffilename1Dres)
        self.canvas1Dres.SetLeftMargin(0.15)
        self.canvas1Dres.SetRightMargin(0.15)
        self.canvas1Dres.SetBottomMargin(0.15)
        self.canvas1Dres.SetTopMargin(0.15)
        self.canvas1Dres.Print(pdfstart1Dres, "pdf")
        print ("start of 1D res loop")

        for sample in self.res1D: 
            
            print(" Sample: " , sample )
            for variable in self.res1D[sample].keys():   # only do this for a subset to save output time.

                
                if "_resolution" not in variable: continue
                #if (variable.find("_resolution"): == std.string.npos): continue

                for resthetype in self.res1D[sample][variable].keys(): 
                    
                    print("resthetype " , resthetype )
                    if "type" in resthetype:
                        continue
                    for category in  self.res1D[sample][variable][resthetype].keys(): 
                        h = MnvH1D()
                        h =  self.res1D[sample][variable][resthetype][category].Clone()
                        if (h.GetEntries() == 0): continue
                        label = ("resolution_")+sample+"_"+variable+"_"+resthetype+"_"+category
                        print ("h type",h.GetName(), type(h))
                        PlotCVAndError(self.canvas1Dres, h, h, label, False, 0, True)
                    
                
            


        self.canvas1Dres.Print(pdfend1Dres, "pdf")

    def plot2D(self):
        # Set up pdf for 2D plots.
        self.pdffilename2D = self.pdfname + "_2D.pdf"
        pdfstart2D = self.pdfname + "_2D.pdf("
        pdfend2D = self.pdfname + "_2D.pdf)"
        canvas2D = TCanvas(self.pdffilename2D)
        canvas2D.SetLeftMargin(0.15)
        canvas2D.SetRightMargin(0.15)
        canvas2D.SetBottomMargin(0.15)
        canvas2D.SetTopMargin(0.15)
        canvas2D.Print(pdfstart2D, "pdf")

        print(" just before 2D loop" )
        for sample in self.hists2D: 

            for variable in self.hists2D[sample]:   # only do this for a subset to save output time.
                if not checktag(self.AnalyzeVariables2D, variable):
                    print(" don't do this variable for now" , variable )
                    continue
                
                basename = "h2D_" + sample + "_" + variable
                if (self.singlesample): 
                    basename = "h_" + variable
                
                sys.exit = GetCrossSection(sample, variable, basename, self.hists2D[sample][variable], self.response2D[sample][variable], self.allconfigs, canvas2D,  self.norm, self.POTScale, self.h_flux_dewidthed, self.unfold, self.num_iter, DEBUG, self.hasbkgsub, self.usetune, self.pdfname)
                if (DEBUG): print(sys.exit )
            

        print(" end of 2D loop" )
        canvas2D.Print(pdfend2D, "pdf")
        # Close pdf for 2D plots.

    def end(self):
        self.o.Close()
        sys.exit(0)

    # if len(sys.argv) < 2:
    #     print ("give me a root file to chew on")
    # else:
    #     main()

# actually do it

driver = AnalysisDriver()
driver.categorymaps()
driver.loadFlux()
driver.setUnfold()
driver.POTInfo()
driver.mkdirs()
driver.parsekeys()
driver.scaleMC()
driver.zeroPOT()
driver.mapHists()
driver.makeoutfile()
driver.combine()
driver.writeConfigs()
driver.opencanvas1D()
driver.Loop1D()
driver.close1DCanvas()
driver.plotRes()
driver.plot2D()
driver.end()