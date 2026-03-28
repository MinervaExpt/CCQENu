# classes for extracting a cross section from a fit

## note figure out what do_cov_area_norm does.  3-8-2026

#TODO: store normalization information
#TODO: need to be able to use scaled MC distributions in unfolding/efficiency.  

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
##from GetXSec import GetCrossSection 

from RebinFlux import GetFlux
from plotting_pdf import PlotCVAndError,PlotErrorSummary
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
    elif four not in thing[one][two][three]:
        thing[one][two][three][four] = value
        names = value.GetErrorBandNames()
        if len(names) > 0:
            SyncBands(value)
        if DEBUG: print ("added",thing[one][two][three][four].GetName(),one,two,three,four,value.GetName())
    else:
        print ("Found a duplicate item",one,two,three,four)
    pass

def fractionator(hist1, hist2,newname):
    ''' get the fraction of hist1 in hist1+hist2 without double counting errors'''
    den = hist1.Clone("temp")
    den.Add(hist2)
    num = hist1.Clone(newname)
    num.Divide(num,den, 1., 1., "B")
    del den
    return num
    
    
    

class CrossSectionExtractor:

    ''' Class that does cross section extraction after data grab '''
    def __init__(self, grabber, plotter):
        self.hists1D = grabber.hists1D
        self.allconfigs = grabber.allconfigs
        self.plotter = plotter
        self.grabber = grabber

    def background(self):
        input_stage = self.grabber.allconfigs["Cross"]["Stages"]["Background"]["In"]
        output_stage = self.grabber.allconfigs["Cross"]["Stages"]["Background"]["Out"]
        for sample in self.allconfigs["Cross"]["Samples"]:
            for variable in self.allconfigs["Cross"]["Variables"]:

                data_cat = self.allconfigs["Cross"]["Data_Cat"]            
                bkg_cat = "bkgtot"
                sig_cat = self.allconfigs["Cross"]["Signal_Cat"]
                
                sig_type = self.allconfigs["Cross"]["Signal_Type"]
                bkg_hist = self.hists1D[sample][bkg_cat][variable][sig_type]
                sig_hist = self.hists1D[sample][sig_cat][variable][sig_type]
                new_name = self.hists1D[sample][data_cat][variable][input_stage].GetName()+"_"+input_stage
                
                bkgsub_hist = self.hists1D[sample][data_cat][variable][input_stage].Clone(new_name)
                bkgsub_hist.AddMissingErrorBandsAndFillWithCV(sig_hist)
                

                signal_fraction = fractionator(sig_hist,bkg_hist,newname=sample+"_"+variable+"_signal_fraction")
                bkgsub_hist.Multiply(bkgsub_hist,signal_fraction)
                addentry(self.hists1D, sample, data_cat, variable, output_stage, bkgsub_hist)
                
                if PLOTS:
                    logscale = self.allconfigs["Cross"]["Scales"][variable]

                    PlotCVAndError(self.plotter.canvas1D, signal_fraction,signal_fraction,sample+": Signal Fraction",True,1,False) # remove binwid                   
                    PlotErrorSummary(self.plotter.canvas1D, signal_fraction, sample + ": Signal Fraction Systematics", logscale%2)

                    PlotCVAndError(self.plotter.canvas1D,bkgsub_hist,sig_hist,sample+": Background Subtracted Data",True,logscale)
                    PlotErrorSummary(self.plotter.canvas1D, bkgsub_hist, sample + ": Background Subtracted Data Systematics", logscale%2)
                                   
                

        
    def unfold(self,iterations=4):
        ''' method that unfolds background subtracted data '''

        input_stage = self.grabber.allconfigs["Cross"]["Stages"]["Unfold"]["In"]
        output_stage = self.grabber.allconfigs["Cross"]["Stages"]["Unfold"]["Out"]
        
        for sample in self.allconfigs["Cross"]["Samples"]:
            for variable in self.allconfigs["Cross"]["Variables"]:
                logscale = self.allconfigs["Cross"]["Scales"][variable]
                data_cat = self.allconfigs["Cross"]["Data_Cat"]
                signal_cat = self.allconfigs["Cross"]["Signal_Cat"]
                
                migration_type = self.allconfigs["Cross"]["Migration_Type"]
                selected_type = self.allconfigs["Cross"]["Selected_Type"]
                data_hist = self.hists1D[sample][data_cat][variable][input_stage]
                unfolded_name = (data_hist.GetName()) + "_"+output_stage
                migration = self.hists1D[sample][signal_cat][variable][migration_type+"_migration"]
                true_sel_hist = self.hists1D[sample][signal_cat][variable][selected_type]

                unfolded_hist= MnvH1D()
                unfolded_hist= MnvH1D((true_sel_hist).GetCVHistoWithStatError())
                unfolded_hist.SetName(unfolded_name)
                unfolded_hist.SetDirectory(0)
                if DEBUG: print(" Migration matrix has size " , len(migration.GetErrorBandNames()) )
                if DEBUG: print(" Data has  size " , len(data_hist.GetErrorBandNames()) )
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
                addentry(self.hists1D, sample, data_cat, variable, output_stage, unfolded_hist)
                unfolded_hist.Print()

                if PLOTS:
                    
                    #data_hist.Print("ALL")
                    #unfolded_hist.Print("ALL")
                    PlotCVAndError(self.plotter.canvas1D, data_hist,unfolded_hist,sample+": unfolding before and after",True,logscale)
                    

                   
                    PlotCVAndError(self.plotter.canvas1D, unfolded_hist,true_sel_hist,sample+": Unfolded data",True,logscale)
                    PlotErrorSummary(self.plotter.canvas1D, unfolded_hist, sample+": Unfolded Systematics", logscale%2)
                    #self.plotter.canvas1D.Print(f"pix/{sample}_{variable}_{stage}.png")
                    #cE.Print(f"unfolding_{sample}_{variable}.png")

    def efficiency(self,thesamples):
        input_stage = self.grabber.allconfigs["Cross"]["Stages"]["Efficiency"]["In"]
        output_stage = self.grabber.allconfigs["Cross"]["Stages"]["Efficiency"]["Out"]
        for sample in self.grabber.hists1D.keys():
            print ("efficiency correcting",sample)
            if sample not in thesamples: continue
            for variable in self.allconfigs["Cross"]["Variables"]:
                logscale = self.allconfigs["Cross"]["Scales"][variable]
                data_cat = self.allconfigs["Cross"]["Data_Cat"]
                mc_cat = self.allconfigs["Cross"]["Signal_Cat"]
                selected_type = self.allconfigs["Cross"]["Selected_Type"]
                truth_type = self.allconfigs["Cross"]["Truth_Type"]
                unfolded_hist = self.hists1D[sample][data_cat][variable][input_stage]
                
                true_sel_hist = self.hists1D[sample][mc_cat][variable][selected_type]
                true_all_hist = self.hists1D[sample][mc_cat][variable][truth_type]
                efficiency_name = true_sel_hist.GetName().replace(selected_type,"efficiency")
                efficiency_hist = MnvH1D()
                efficiency_hist = true_sel_hist.Clone(efficiency_name)
                efficiency_hist.Divide(efficiency_hist,true_all_hist,1.,1.,"B")

                efficiency_hist.PopVertErrorBand("Flux")

                print("removed Flux Error band from efficiency" )
    
                efficiency_hist.AddMissingErrorBandsAndFillWithCV(unfolded_hist)
                SyncBands(efficiency_hist)
                
                addentry(self.hists1D, sample, mc_cat, variable, "efficiency", efficiency_hist)
                #efficiency_hist.Print("ALL")



                corrected_name=unfolded_hist.GetName()+"_"+output_stage
                corrected_hist = MnvH1D()
                corrected_hist = unfolded_hist.Clone(corrected_name)
                corrected_hist.Divide(corrected_hist,efficiency_hist)
                SyncBands(corrected_hist)
                addentry(self.hists1D, sample, data_cat, variable, output_stage, corrected_hist)

                if PLOTS:
                    if sample == "merged":
                        PlotCVAndError(self.plotter.canvas1D, unfolded_hist,true_sel_hist,sample+": Merged Unfolded Data",True,logscale=1,binwid=True)
                        PlotErrorSummary(self.plotter.canvas1D, unfolded_hist, sample+": Merged Unfolded Systematics", logscale%2)

                    PlotCVAndError(self.plotter.canvas1D, efficiency_hist,efficiency_hist,sample+": Efficiency Correction",True,1,False) # remove binwid                   
                    PlotErrorSummary(self.plotter.canvas1D, efficiency_hist, sample + ": Efficiency Systematics", logscale%2)

                    PlotCVAndError(self.plotter.canvas1D, corrected_hist,true_all_hist,sample+": Efficiency Corrected Data",True,logscale=1,binwid=True)
                    PlotErrorSummary(self.plotter.canvas1D, corrected_hist, sample+": Efficiency Corrected Systematics", logscale%2)
                    


    def flux(self,thesamples):
        '''Method that does a flux/target correction to corrected counts to make a cross section'''

        input_stage = self.grabber.allconfigs["Cross"]["Stages"]["Flux"]["In"]
        output_stage = self.grabber.allconfigs["Cross"]["Stages"]["Flux"]["Out"]

        mcoutput_stage=output_stage+"MC"
        for sample in self.grabber.hists1D.keys():
            if sample not in thesamples: continue
            for variable in self.allconfigs["Cross"]["Variables"]:
                logscale = self.allconfigs["Cross"]["Scales"][variable]
                data_cat = self.allconfigs["Cross"]["Data_Cat"]
                mc_cat = self.allconfigs["Cross"]["Signal_Cat"]
                truth_type = self.allconfigs["Cross"]["Truth_Type"]
                effcorr_hist = self.hists1D[sample][data_cat][variable][input_stage]
                true_all_hist = self.hists1D[sample][mc_cat][variable][truth_type]
                
                sigma_name=effcorr_hist.GetName()+"_"+output_stage
                sigma_hist = MnvH1D()
                sigma_hist = effcorr_hist.Clone(sigma_name)

                sigmaMC_name=true_all_hist.GetName()+"_"+ mcoutput_stage
                sigmaMC_hist = MnvH1D()
                sigmaMC_hist = true_all_hist.Clone(sigmaMC_name)

                # get the target and POT normalizations

                norm = self.norm(ismc=False)
                normMC = self.norm(ismc=True)
                
                if (not self.allconfigs["Cross"]["FluxNorm"][variable]): 
                    print(" Using flat flux normalization. " )
                    # Returns integrated flux hist in bins input hist
                    
                    theflux_hist = GetFluxFlat(self.allconfigs, sigma_hist)

                    theflux_hist.AddMissingErrorBandsAndFillWithCV(sigma_hist)

                    sigma_hist.AddMissingErrorBandsAndFillWithCV(theflux_hist)

                    sigma_hist.Divide(sigma_hist, theflux_hist)

                    # target/POT normalization
                    sigma_hist.Scale(norm)

                    theflux_hist.AddMissingErrorBandsAndFillWithCV(sigmaMC_hist)

                    sigmaMC_hist.AddMissingErrorBandsAndFillWithCV(theflux_hist)

                    sigmaMC_hist.Divide(sigmaMC_hist, theflux_hist)

                    # target/POT normalization
                    sigmaMC_hist.Scale(normMC)
                else:
                    print("energy dependent flux not implemented yet")
                    pass


                addentry(self.hists1D, sample, data_cat, variable, output_stage, sigma_hist)

                addentry(self.hists1D, sample, mc_cat, variable, mcoutput_stage, sigmaMC_hist)

                if PLOTS:
                    
                    PlotCVAndError(self.plotter.canvas1D, sigma_hist,sigmaMC_hist,sample+": Cross Section "+self.grabber.model,True,logscale,binwid=True)
                    PlotErrorSummary(self.plotter.canvas1D, sigma_hist, sample+": Cross Section Systematics", logscale%2)
        pass

    def norm(self,ismc):
        ''' method to get POT and target information for normalization'''
        f = self.grabber.data_files[self.grabber.reference_sample]
        h_pot = TH1D()
        h_pot = f.Get("POT_summary")
        h_pot.Print("ALL")

        dataPOT = h_pot.GetBinContent(1)
        mcPOTprescaled = h_pot.GetBinContent(3)
        POTScale = dataPOT / mcPOTprescaled
        target = GetTarget(type=self.allconfigs["Cross"]["Target"],ismc=ismc)
        norm = 1. / dataPOT / target
        
        #self.targetobj = TNamed("targets", "%6e"%target)

        print(" integrated luminosity is " , 1 / norm / 1.E24 , "barns^-1" )

        print(" POT MC " , mcPOTprescaled )
        print(" POT DATA " , dataPOT )

        print(" POT Scale",POTScale)

        

        return norm

class DataGrabber:
    ''' class to grab data from a fit file '''

    def __init__(self, config, plotter):
        '''  store the config and input data file'''
        self.config = config
        self.data_source = config["InputFiles"]

        self.samples = config["Samples"]
        self.data_files = {}
        self.samples_pot = {}
        count = 0
        self.reference_sample = ""
        for sample in self.samples:
            self.data_files[sample] = TFile.Open(self.data_source[sample],'READ')
            h_pot = TH1D()
            h_pot = self.data_files[sample].Get("POT_summary")
            self.samples_pot[sample]=h_pot
            h_pot.Print("ALL")
            if count == 0:
                self.reference_sample = sample
                count += 1

        self.allconfigs = {}
        for key in ["main","varsFile","cutsFile","samplesFile"]:
            self.allconfigs[key] = commentjson.loads(self.data_files[self.reference_sample].Get(key).GetTitle())
        
        self.allconfigs["Cross"]=config
        self.hists1D = {}
        self.datatypes1D = self.allconfigs["Cross"]["data_types1D"] 
        self.datatypes2D = self.allconfigs["Cross"]["data_types2D"]
        self.plotter = plotter
        self.model = self.allconfigs["main"]["MinervaModel"]

    def grab(self):
        ''' Implement the logic to grab the necessary data from the data source 
        This filters out intermediate information 
        '''

        for sample in self.allconfigs["Cross"]["Samples"]:
            for category in self.allconfigs["Cross"]["Categories"]:
                for variable in self.allconfigs["Cross"]["Variables"]:
                    for data_type in self.datatypes1D[category]:
                        
                        hist_name = f"h___{sample}___{category}___{variable}___{data_type}"
                        hist = MnvH1D()
                        hist = self.data_files[sample].Get(hist_name)
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
                        hist = self.data_files[sample].Get(hist_name)
                        if hist == None:
                            print ("could not find",hist_name)
                            continue
                        addentry(self.hists1D, sample, category, variable, data_type, hist)
                        if DEBUG: print ("grabbed",self.hists1D[sample][category][variable][data_type].GetName(),sample,category,variable,data_type)

# make an MCTOT and plot if request
        
        for sample in self.allconfigs["Cross"]["Samples"]:
            for variable in self.allconfigs["Cross"]["Variables"]:
                
                data_cat = self.allconfigs["Cross"]["Data_Cat"]
                signal_cat = self.allconfigs["Cross"]["Signal_Cat"]
                background_cats = self.allconfigs["Cross"]["Background_Cat"]
                data_type = self.allconfigs["Cross"]["Data_Type"]
                signal_type = self.allconfigs["Cross"]["Signal_Type"]
                background_type = self.allconfigs["Cross"]["Background_Type"]
                data_hist = self.hists1D[sample][data_cat][variable][data_type]
                mc_hist = self.hists1D[sample][signal_cat][variable][signal_type]
                mctot_hist = mc_hist.Clone(mc_hist.GetName()+"_mctot")
                bkgtot_hist = mc_hist.Clone(mc_hist.GetName()+"_bkgtot")
                bkgtot_hist.Reset()
                for bkg_cat in background_cats:
                    bkg_hist = self.hists1D[sample][bkg_cat][variable][background_type]
                    mctot_hist.Add(bkg_hist)
                    bkgtot_hist.Add(bkg_hist)
                
                addentry(self.hists1D,sample,"mctot",variable,signal_type,mctot_hist)
                addentry(self.hists1D,sample,"bkgtot",variable,signal_type,bkgtot_hist)

                if DEBUG: print ("created",self.hists1D[sample]["mctot"][variable][signal_type].GetName(),sample,category,variable,signal_type) 
                if DEBUG: print ("created",self.hists1D[sample]["bkgtot"][variable][background_type].GetName(),sample,category,variable,background_type)   


            
                if PLOTS:
                    logscale = self.allconfigs["Cross"]["Scales"][variable]
                    PlotCVAndError(self.plotter.canvas1D, data_hist,mctot_hist,sample + ": data compared to "+self.model,True,self.plotter.scales[variable])
                    PlotErrorSummary(self.plotter.canvas1D, data_hist, sample + ": Data", logscale%2)
                   
        pass

    def merge(self, mergesamples=[]):
        ''' method to merge disjoint samples
        it does not merge the total truth as that has no 
        selection applied
        '''
        newsample = "merged"
        for sampleindex in range(0,len(mergesamples)):
            sample = mergesamples[sampleindex]  
                       
            for category in self.hists1D[sample].keys():
                for variable in self.hists1D[sample][category].keys():
                    for data_type in self.hists1D[sample][category][variable].keys():
                        if sampleindex == 0:
                            newname = self.hists1D[sample][category][variable][data_type].GetName().replace(sample,newsample)
                            hist = self.hists1D[sample][category][variable][data_type].Clone(newname)
                            addentry(self.hists1D, newsample, category, variable, data_type, hist)
                        else:
                            if "all_truth" in data_type: 
                                print ("should not merge the truth")
                                continue
                            self.hists1D[newsample][category][variable][data_type].Add(self.hists1D[sample][category][variable][data_type])
        
        pass

    def print(self,types=[],option=""):
        for sample in self.hists1D.keys():
            for category in self.hists1D[sample].keys():
                for variable in self.hists1D[sample][category].keys():
                    for data_type in self.hists1D[sample][category][variable].keys():
                        if types != [] and data_type not in types: continue
                        count = self.hists1D[sample][category][variable][data_type].Integral()
                        print (f"Totals: {sample} {category} {variable} {data_type} {count}")
        pass

    def write(self, outname):
        ''' method to write root file with hists and configuration'''
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
            #print (obj)
            object = TNamed()   
            object.SetName(key)
            object.SetTitle(obj)
            #object.Print()
            object.Write()
        
        print ("close output file")

        out.Close()
        pass

    def store(self, outdir):
        ''' method to write tables and config files to outdir'''
    
        if not os.path.exists(outdir):
            print ("making output directory",outdir)
            os.mkdir(outdir)
        
        for sample in self.hists1D.keys():
            for category in self.hists1D[sample].keys():
                for variable in self.hists1D[sample][category].keys():
                    for data_type in self.hists1D[sample][category][variable].keys():
                        if "sigma" in data_type:
                            print ("dump the numbers")
                            hist = self.hists1D[sample][category][variable][data_type]
                            #void MnvH1DToCSV(std::string name, std::string directory="", double scale=1.0, bool fullprecision=true, bool errors=true, bool percentage = true, bool binwidth = true);
                            hist.MnvH1DToCSV(name=hist.GetName(),directory=outdir, scale=1.E41, fullprecision=False,errors= True,  percentage=True, binwidth=True)
        # write out the configs

        for key, config in self.allconfigs.items():
            print (" Store config ", key )
            obj = commentjson.dumps(config)
            f = open(os.path.join(outdir,key+".json"),'w')
            f.write(obj)
            f.close()
            
        
        print ("close output file")
        
        pass

    def delete(self):
        ''' method to delete the histograms, needs work '''
        del self.hists1D
        

        pass

                        



class Plotter:
    ''' class that holds plotter configurations'''

    def __init__(self,config,pdffilename):
        self.pdfname = pdffilename
        self.canvas1D = TCanvas(pdffilename)
        self.canvas1D.SetLeftMargin(0.15)
        self.canvas1D.SetRightMargin(0.15)
        self.canvas1D.SetBottomMargin(0.15)
        self.canvas1D.SetTopMargin(0.10)
        self.canvas1D.Print(pdffilename+"(", "pdf")
        self.logx=0
        self.scales=config["Scales"]

        pass


    
    
    def close(self):
        ''' method to close a pdf file '''
        self.canvas1D.Print(self.pdfname+")", "pdf")
        pass
    



if __name__ == "__main__":
    
    ## read in a config file
    configfilename = "AntiNu.json"
    if len(sys.argv) > 1:
        configfilename = sys.argv[1]
    configfile = open(configfilename,'r')
    config = commentjson.load(configfile)
    configfile.close()

    # set up the plotter
    pdffilename1D= configfilename.replace("json","pdf")
    plotter = Plotter(config,pdffilename1D)

    # set up and grab the data

    grabber = DataGrabber(config,plotter)
    grabber.grab()

    cross = CrossSectionExtractor(grabber,plotter)

    if "Background" in config["Stages"]:
        cross.background()

    

    #grabber.print(["fitted_combined","reconstructed"])
    
    # set up and do the cross section extraction

    
    cross.unfold(iterations=4)
    
    grabber.merge(config["Samples"])
    

    # efficiency correction 

    cross.efficiency(["merged"])

    # flux normalization for just the merged sample

    cross.flux("merged")


    # close the pdf file
    plotter.close()

    # write to root file and csv directory
    
    grabber.write(configfilename.replace(".json",".root"))
    grabber.store(os.path.join("csv",configfilename.replace(".json","")))
    grabber.delete()
