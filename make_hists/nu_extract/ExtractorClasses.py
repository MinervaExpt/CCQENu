# classes for extracting a cross section from a fit

## note figure out what do_cov_area_norm does.  3-8-2026

import os,sys
from ROOT import TFile,TNamed, TH1D, TCanvas, TMatrixD, TVectorD,TString, gPad
from PlotUtils import MnvH1D, MnvH2D, MnvPlotter
import commentjson
from SyncBands import SyncBands
from UnfoldUtils import MnvUnfold, MnvResponse
from RebinFlux import GetFluxFlat

DEBUG=True
PLOTS=True
POPFITPARAMETERS=True # have to do this for now to keep unfolding happy about match between data and mc. HMS 3-7-2026

print ("have imported common packages")

from MatrixUtils import checktag, ToVectorD, ToMatrixDSym, scaleHist, map2TObjArray, TexFigure3
from GetXSec import GetCrossSection 

from RebinFlux import GetFlux
from plotting_pdf import PlotCVAndError
from GetTarget import GetTarget


def addentry(thing,one,two,three,four,value):
    ''' helper function to add entries to a dictionary 4 deep, and sync the error bands if needed '''
    
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
        self.grabber = grabber
        
    def unfold(self,iterations=4):
        input_stage = "fitted_combined"
        stage = "unfolded"
        for sample in self.allconfigs["Cross"]["Samples"]:
            for variable in self.allconfigs["Cross"]["Variables"]:
                data_cat = self.allconfigs["Cross"]["Data"]
                signal_cat = self.allconfigs["Cross"]["Signal"]
                
                migration = self.allconfigs["Cross"]["Migration"]
                data_hist = self.hists1D[sample][data_cat][variable][input_stage]
                unfolded_name = (data_hist.GetName()) + "_"+stage
                migration = self.hists1D[sample][signal_cat][variable][migration+"_migration"]
                true_sel_hist = self.hists1D[sample][signal_cat][variable]["selected_truth"]
                unfolded_hist= MnvH1D()
                unfolded_hist= MnvH1D((true_sel_hist).GetCVHistoWithStatError())
                unfolded_hist.SetName(unfolded_name)
                unfolded_hist.SetDirectory(0)
                print(" Migration matrix has size " , len(migration.GetErrorBandNames()) )
                print(" Data has  size " , len(data_hist.GetErrorBandNames()) )
                #  make an empty covariance matrix for the unfolding to give back to you
                n = unfolded_hist.GetXaxis().GetNbins()
                covmatrix = TMatrixD(n,n) 
                kBayes = 1
                unfolder = MnvUnfold()
                status  = unfolder.UnfoldHisto(unfolded_hist, covmatrix, migration, data_hist, kBayes, iterations, True, True)

                print ("unfolding returned status",status)

                for i in range(0,  covmatrix.GetNrows()):  
                    covmatrix[i][i] = 0.0

                unfolded_hist.FillSysErrorMatrix("Unfolding", covmatrix)
                SyncBands(unfolded_hist)
                addentry(self.hists1D, sample, data_cat, variable, stage, unfolded_hist)
                unfolded_hist.Print()

                if PLOTS:
                    
                    data_hist.Print("ALL")
                    unfolded_hist.Print("ALL")
                    PlotCVAndError(self.plotter.canvas1D, data_hist,unfolded_hist,"unfolding before and after",True,1)
                    self.plotter.canvas1D.Print(f"pix/{sample}_{variable}_unfoldingeffect.png")
                    data_hist.Print("ALL")
                    unfolded_hist.Print("ALL")
                    PlotCVAndError(self.plotter.canvas1D, unfolded_hist,true_sel_hist,"unfolded data and selected",True,1)
                    self.plotter.canvas1D.Print(f"pix/{sample}_{variable}_{stage}.png")
                    #cE.Print(f"unfolding_{sample}_{variable}.png")

    def efficiency(self):
        input_stage = "unfolded"
        stage="effcorr"
        for sample in self.allconfigs["Cross"]["Samples"]:
            for variable in self.allconfigs["Cross"]["Variables"]:
                data_cat = self.allconfigs["Cross"]["Data"]
                mc_cat = self.allconfigs["Cross"]["Signal"]
                
                unfolded_hist = self.hists1D[sample][data_cat][variable][input_stage]
                true_sel_hist = self.hists1D[sample][mc_cat][variable]["selected_truth"]
                true_all_hist = self.hists1D[sample][mc_cat][variable]["all_truth"]
                efficiency_name = true_sel_hist.GetName().replace("selected_truth","efficiency")
                efficiency_hist = MnvH1D()
                efficiency_hist = true_sel_hist.Clone(efficiency_name)
                efficiency_hist.Divide(efficiency_hist,true_all_hist)

                efficiency_hist.PopVertErrorBand("Flux")

                print("removed Flux Error band from efficiency" )
    
                efficiency_hist.AddMissingErrorBandsAndFillWithCV(unfolded_hist)
                SyncBands(efficiency_hist)
                
                addentry(self.hists1D, sample, mc_cat, variable, "efficiency", efficiency_hist)
                efficiency_hist.Print("ALL")



                corrected_name=unfolded_hist.GetName()+"_"+stage
                corrected_hist = MnvH1D()
                corrected_hist = unfolded_hist.Clone(corrected_name)
                corrected_hist.Divide(corrected_hist,efficiency_hist)
                addentry(self.hists1D, sample, data_cat, variable, stage, corrected_hist)

                if PLOTS:
                    
                    PlotCVAndError(self.plotter.canvas1D, efficiency_hist,efficiency_hist,"efficiency",True,1,False) # remove binwid
                    #self.plotter.canvas1D.Print(f"pix/{sample}_{variable}_efficiency.png")
                    
                    PlotCVAndError(self.plotter.canvas1D, corrected_hist,unfolded_hist,"after and before efficiency correction",True,logscale=1,binwid=True)
                    #self.plotter.canvas1D.Print(f"pix/{sample}_{variable}_effcoreffect.png")

                    PlotCVAndError(self.plotter.canvas1D, corrected_hist,true_all_hist,"effcor compared to selected",True,logscale=1,binwid=True)
                    #self.plotter.canvas1D.Print(f"pix/{sample}_{variable}_effcor.png")


    def flux(self):
        input_stage = "effcorr"
        stage="sigma"
        mcstage="sigmaMC"
        for sample in self.allconfigs["Cross"]["Samples"]:
            for variable in self.allconfigs["Cross"]["Variables"]:
                data_cat = self.allconfigs["Cross"]["Data"]
                mc_cat = self.allconfigs["Cross"]["Signal"]
                
                effcorr_hist = self.hists1D[sample][data_cat][variable][input_stage]
                true_all_hist = self.hists1D[sample][mc_cat][variable]["all_truth"]
                
                sigma_name=effcorr_hist.GetName()+"_"+stage
                sigma_hist = MnvH1D()
                sigma_hist = effcorr_hist.Clone(sigma_name)

                sigmaMC_name=true_all_hist.GetName()+"_"+mcstage
                sigmaMC_hist = MnvH1D()
                sigmaMC_hist = true_all_hist.Clone(sigmaMC_name)
                norm = self.norm(ismc=False)
                normMC = self.norm(ismc=True)
                
                if (not self.allconfigs["Cross"]["FluxNorm"][variable]): 
                    print(" Using flat flux normalization. " )
                    # Returns integrated flux hist in bins input hist
                    print(self.allconfigs.keys())
                    if "main" in self.allconfigs.keys():
                        print (self.allconfigs["main"])
                    theflux_hist = GetFluxFlat(self.allconfigs, sigma_hist)

                    theflux_hist.AddMissingErrorBandsAndFillWithCV(sigma_hist)
                    sigma_hist.AddMissingErrorBandsAndFillWithCV(theflux_hist)
                    sigma_hist.Divide(sigma_hist, theflux_hist)
                    # target normalization
                    sigma_hist.Scale(norm)

                    theflux_hist.AddMissingErrorBandsAndFillWithCV(sigmaMC_hist)
                    sigmaMC_hist.AddMissingErrorBandsAndFillWithCV(theflux_hist)
                    sigmaMC_hist.Divide(sigmaMC_hist, theflux_hist)
                    # target normalization
                    sigmaMC_hist.Scale(normMC)
                else:
                    print("energy dependent flux not implemented yet")
                    pass


                addentry(self.hists1D, sample, data_cat, variable, stage, sigma_hist)

                addentry(self.hists1D, sample, mc_cat, variable, mcstage, sigmaMC_hist)

                if PLOTS:
                    
                    PlotCVAndError(self.plotter.canvas1D, sigma_hist,sigmaMC_hist,"cross sections",True,logscale=1,binwid=True)
                    #self.plotter.canvas1D.Print(f"pix/{sample}_{variable}_effcor.png")


            
                    


    
        # Implement the logic to extract the cross section from the fit result
        # using the provided cross section model
        pass

    def norm(self,ismc):
        f = self.grabber.data_file
        h_pot = TH1D()
        h_pot = f.Get("POT_summary")
        h_pot.Print("ALL")

        dataPOT = h_pot.GetBinContent(1)
        mcPOTprescaled = h_pot.GetBinContent(3)
        POTScale = dataPOT / mcPOTprescaled
        target = GetTarget(type=self.allconfigs["Cross"]["Target"],ismc=ismc)
        norm = 1. / dataPOT / target
        
        self.targetobj = TNamed("targets", "%6e"%target)

        print(" integrated luminosity is " , 1 / norm / 1.E24 , "barns^-1" )

        print(" POT MC " , mcPOTprescaled )
        print(" POT DATA " , dataPOT )

        print(" POT Scale",POTScale)
        return norm

class DataGrabber:
    def __init__(self, config, plotter):
        self.config = config
        self.data_source = config["InputFile"]
        self.data_file = TFile.Open(self.data_source,'READ')
        self.allconfigs = {}
        for key in ["main","varsFile","cutsFile","samplesFile"]:
            self.allconfigs[key] = commentjson.loads(self.data_file.Get(key).GetTitle())
        
        self.allconfigs["Cross"]=config
        self.hists1D = {}
        self.datatypes1D = self.allconfigs["Cross"]["data_types1D"] 
        self.datatypes2D = self.allconfigs["Cross"]["data_types2D"]
        self.plotter = plotter

    

    def grab(self):
        # Implement the logic to grab the necessary data from the data source

        for sample in self.allconfigs["Cross"]["Samples"]:
            for category in self.allconfigs["Cross"]["Categories"]:
                for variable in self.allconfigs["Cross"]["Variables"]:
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
        for sample in self.allconfigs["Cross"]["Samples"]:
            for variable in self.allconfigs["Cross"]["Variables"]:
                data_cat = self.allconfigs["Cross"]["Data"]
                signal_cat = self.allconfigs["Cross"]["Signal"]
                types = self.allconfigs["Cross"]["data_types1D"]
                if DEBUG: print (types)
                data_hist = self.hists1D[sample][data_cat][variable]["fitted_combined"]
                mc_hist = self.hists1D[sample][signal_cat][variable]["reconstructed"]
                
                if PLOTS:
                    PlotCVAndError(self.plotter.canvas1D, data_hist,mc_hist,"subtracted",True,self.plotter.scales[variable])
                    self.plotter.canvas1D.Print(f"pix/{sample}_{variable}_subtracted.png")
        pass

    def write(self, outname):
        out = TFile.Open(outname,"RECREATE")
        out.cd()
        
        for sample in self.hists1D.keys():
            for category in self.hists1D[sample].keys():
                for variable in self.hists1D[sample][category].keys():
                    for data_type in self.hists1D[sample][category][variable].keys():
                        self.hists1D[sample][category][variable][data_type].Write()
        # write out the configs

        for key, config in self.allconfigs.items():
            print (" write out config ", key )
            obj = commentjson.dumps(config)
            print (obj)
            object = TNamed()   
            object.SetName(key)
            object.SetTitle(obj)
            object.Print()
            object.Write()
        
        print ("close output file")
        out.ls()
        out.Close()
        pass

    def delete(self):
        del self.hists1D
        

        pass

                        



class Plotter:

    def __init__(self,config,pdffilename):
        self.pdfname = pdffilename
        self.canvas1D = TCanvas(pdffilename)
        self.canvas1D.SetLeftMargin(0.15)
        self.canvas1D.SetRightMargin(0.15)
        self.canvas1D.SetBottomMargin(0.15)
        self.canvas1D.SetTopMargin(0.15)
        self.canvas1D.Print(pdffilename+"(", "pdf")
        self.logx=0
        self.scales=config["Scales"]

        pass


    
    
    def close(self,pdfname):
        self.canvas1D.Print(self.pdfname+")", "pdf")

    



if __name__ == "__main__":
    configfilename = "XNu.json"
    configfile = open(configfilename,'r')
    config = commentjson.load(configfile)
    configfile.close()
    pdffilename1D= configfilename.replace("json","pdf")
    plotter = Plotter(config,pdffilename1D)

    grabber = DataGrabber(config,plotter)
    grabber.grab()
    cross = CrossSectionExtractor(grabber,plotter)
    cross.unfold(4)
    cross.efficiency()
    cross.flux()

    # close the pdf file
    plotter.canvas1D.Print(pdffilename1D+")", "pdf")
    grabber.write(configfilename.replace(".json",".root"))
    grabber.delete()
