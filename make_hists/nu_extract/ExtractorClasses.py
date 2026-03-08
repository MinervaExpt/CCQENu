# classes for extracting a cross section from a fit

import os,sys
from ROOT import TFile,TNamed, TH1D, TCanvas, TMatrixD, TVectorD,gPad
from PlotUtils import MnvH1D, MnvH2D, MnvPlotter
import commentjson
from SyncBands import SyncBands
from UnfoldUtils import MnvUnfold, MnvResponse

DEBUG=True
PLOTS=True
POPFITPARAMETERS=True # have to do this for now to keep unfolding happy about match between data and mc. HMS 3-7-2026

print ("have imported common packages")

from MatrixUtils import checktag, ToVectorD, ToMatrixDSym, scaleHist, map2TObjArray, TexFigure3
from GetXSec import GetCrossSection 

from RebinFlux import GetFlux
from plotting_pdf import PlotCVAndError, setLogScale

# helper function to add entries to a dictionary 4 deep, and sync the error bands if needed

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

class CrossSectionExtractor:
    def __init__(self, grabber, plotter):
        self.hists1D = grabber.hists1D
        self.allconfigs = grabber.allconfigs
        self.plotter = plotter
        #self.plotter = MnvPlotter()
        #self.plotter.SetLegendPosition(0.7,0.7,0.9,0.9)

    def unfold(self,iterations=4):

        for sample in self.allconfigs["Fits"]["Samples"]:
            for variable in self.allconfigs["Fits"]["Variables"]:
                bkgsub = self.allconfigs["Fits"]["Data"]
                signal = self.allconfigs["Fits"]["Signal"]
                
                migration = self.allconfigs["Fits"]["Migration"]
                data_hist = self.hists1D[sample][bkgsub][variable]["fitted_combined"]
                unfoldedname = (data_hist.GetName()) + "_unfolded"
                migration = self.hists1D[sample][signal][variable][migration+"_migration"]
                true_sel_hist = self.hists1D[sample][signal][variable]["selected_truth"]
                unfolded = MnvH1D()
                unfolded = MnvH1D((true_sel_hist).GetCVHistoWithStatError())
                unfolded.SetName(unfoldedname)
                unfolded.SetDirectory(0)
                print(" Migration matrix has size " , len(migration.GetErrorBandNames()) )
                print(" Data has  size " , len(data_hist.GetErrorBandNames()) )
                #  make an empty covariance matrix for the unfolding to give back to you
                n = unfolded.GetXaxis().GetNbins()
                covmatrix = TMatrixD(n,n) 
                kBayes = 1
                unfolder = MnvUnfold()
                unfolded_hist = unfolder.UnfoldHisto(unfolded, covmatrix, migration, data_hist, kBayes, iterations, True, True)

                for i in range(0,  covmatrix.GetNrows()):  
                    covmatrix[i][i] = 0.0

                unfolded.FillSysErrorMatrix("Unfolding", covmatrix)
                SyncBands(unfolded)
                addentry(self.hists1D, sample, "bkgsub", variable, "bkgsub_unfolded", unfolded)
                unfolded.Print()

                if PLOTS:
                    
                    data_hist.Print("ALL")
                    unfolded.Print("ALL")
                    PlotCVAndError(self.plotter.canvas1D, data_hist,unfolded,"unfolding before and after",True,1)

                    data_hist.Print("ALL")
                    unfolded.Print("ALL")
                    PlotCVAndError(self.plotter.canvas1D, unfolded,true_sel_hist,"unfolded data and selected",True,1)
                    #cE.Print(f"unfolding_{sample}_{variable}.png")


            
                    


    
        # Implement the logic to extract the cross section from the fit result
        # using the provided cross section model
        pass

class DataGrabber:
    def __init__(self, config, plotter):
        self.config = config
        self.data_source = config["InputFile"]
        self.data_file = TFile.Open(self.data_source,'READ')
        self.allconfigs = {}
        for key in ["main","varsFile","cutsFile","samplesFile"]:
            self.allconfigs[key] = self.data_file.Get(key).GetTitle()
        
        self.allconfigs["Fits"]=config
        self.hists1D = {}
        self.datatypes1D = self.allconfigs["Fits"]["data_types1D"] 
        self.datatypes2D = self.allconfigs["Fits"]["data_types2D"]
        self.plotter = plotter

    

    def grab(self):
        # Implement the logic to grab the necessary data from the data source
        for sample in self.allconfigs["Fits"]["Samples"]:
            for category in self.allconfigs["Fits"]["Categories"]:
                for variable in self.allconfigs["Fits"]["Variables"]:
                    for data_type in self.datatypes1D[category]:
                        
                        hist_name = f"h___{sample}___{category}___{variable}___{data_type}"
                        hist = MnvH1D()
                        hist = self.data_file.Get(hist_name)
                        if hist == None:
                            print ("could not find",hist_name)
                            continue
                        if POPFITPARAMETERS:
                            bands = hist.GetErrorBandNames()
                            if "FitVariations" in bands:
                                hist.PopVertErrorBand("FitVariations")
            
                        addentry(self.hists1D, sample, category, variable, data_type, hist)
                        if DEBUG: print ("grabbed",self.hists1D[sample][category][variable][data_type].GetName(),sample,category,variable,data_type)

                    for data_type in self.datatypes2D[category]:
                        hist_name = f"h___{sample}___{category}___{variable}___{data_type}"
                        hist = MnvH2D()
                        hist = self.data_file.Get(hist_name)
                        if hist == None:
                            print ("could not find",hist_name)
                            continue
                        addentry(self.hists1D, sample, category, variable, data_type, hist)
                        if DEBUG: print ("grabbed",self.hists1D[sample][category][variable][data_type].GetName(),sample,category,variable,data_type)
        for sample in self.allconfigs["Fits"]["Samples"]:
            for variable in self.allconfigs["Fits"]["Variables"]:
                datatype = self.allconfigs["Fits"]["Data"]
                signaltype = self.allconfigs["Fits"]["Signal"]
                types = self.allconfigs["Fits"]["data_types1D"]
                if DEBUG: print (types)
                data_hist = self.hists1D[sample][datatype][variable]["fitted_combined"]
                mc_hist = self.hists1D[sample][signaltype][variable]["reconstructed"]
                
                PlotCVAndError(self.plotter.canvas1D, data_hist,mc_hist,"subtracted",True,1)
        pass

class Plotter:

    def __init__(self,pdffilename):
        self.pdfname = pdffilename
        self.canvas1D = TCanvas(pdffilename)
        self.canvas1D.SetLeftMargin(0.15)
        self.canvas1D.SetRightMargin(0.15)
        self.canvas1D.SetBottomMargin(0.15)
        self.canvas1D.SetTopMargin(0.15)
        self.canvas1D.Print(pdffilename+"(", "pdf")
        self.logx=0

        pass

    def setLogx(self,logx):
        print ("setting Logx",logx)
        self.logx = logx
        self.canvas1D.SetLogx(logx)
    
    def close(self,pdfname):
        self.canvas1D.Print(self.pdfname+")", "pdf")



if __name__ == "__main__":
    configfilename = "XNu.json"
    configfile = open(configfilename,'r')
    config = commentjson.load(configfile)
    configfile.close()
    pdffilename1D= configfilename.replace("json","pdf")
    plotter = Plotter(pdffilename1D)
    plotter.setLogx(1)
    grabber = DataGrabber(config,plotter)
    grabber.grab()
    cross = CrossSectionExtractor(grabber,plotter)
    cross.unfold(4)

    # close the pdf file
    plotter.canvas1D.Print(pdffilename1D+")", "pdf")
