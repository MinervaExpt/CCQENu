//File: MnvFitDriver.cxx
//Info: This script is intended to fit for scale factors (and scale factors only) in whatever distribution.
//
//Usage: MnvFitDriver json file. 
//
//IGNORE FOR THE TIME BEING <outdir> <do fits in bins of muon momentum (only 0 means no)> optional: <lowFitBinNum> <hiFitBinNum> TODO: Save the information beyond just printing it out
//
//Author: David Last dlast@sas.upenn.edu/lastd44@gmail.com
// reconfigured to use json configuration - Schellman

//C++ includes
#include <iostream>
#include <iomanip>
#include <stdlib.h>
#include <string>
#include <sstream>
#include <fstream>
#include <vector>
#include <numeric>
#include <algorithm>
#include <unordered_map>
#include <bitset>
#include <time.h>
#include <sys/stat.h>
#include <filesystem>

//ROOT includes
#include "MnvH1D.h"
#include "TInterpreter.h"
#include "TROOT.h"
#include "TH1F.h"
#include "TH2F.h"
#include "TPad.h"
#include "THStack.h"
#include "TFile.h"
#include "TTree.h"
#include "TKey.h"
#include "TDirectory.h"
#include "TSystemDirectory.h"
#include "TCanvas.h"
#include "TStyle.h"
#include "TString.h"
#include "TLorentzVector.h"
#include "TVector3.h"
#include "TLegend.h"
#include "TMath.h"
#include "TColor.h"
#include "TParameter.h"
#include "TFractionFitter.h"
#include "TText.h"
#include "Math/IFunction.h"
#include "Math/Minimizer.h"
#include "Math/Factory.h"
#include "Minuit2/Minuit2Minimizer.h"
#include "TMinuitMinimizer.h"

//Analysis includes
#include "fits/ScaleFactors.h"
#include "fits/MultiScaleFactors.h"

//PlotUtils includes??? Trying anything at this point...
#include "PlotUtils/MnvH1D.h"
#include "PlotUtils/MnvPlotter.h"
#include "utils/NuConfig.h"
#include "utils/SyncBands.h"
#include "fits/DoTheFit.h"


using namespace std;
using namespace PlotUtils;

// convert the vector of hists into something MnvPlotter wants

TObjArray* Vec2TObjArray(std::vector<MnvH1D*> hists, std::vector<std::string> names){
    TObjArray* newArray = new TObjArray();
    newArray->SetOwner(kTRUE);
    //std::cout << " try to make an ObjArray" << hists.size() << std::endl;
    int i = 0;
    if (hists.size() != names.size()){
        std::cout << " problem with objec array names " << std::endl;
    }
    for (int i = 0 ; i != hists.size(); i++){
        
        hists[i]->SetTitle(names[i].c_str());
       
        newArray->Add(hists[i]);
    }
    return newArray;
}

//Borrowed Directly from Andrew.
void printCorrMatrix(const ROOT::Math::Minimizer& minim, const int nPars)
{
    std::vector<double> covMatrix(nPars * nPars, 0);
    minim.GetCovMatrix(covMatrix.data());
    const double* errors = minim.Errors();
    
    for(int xPar = 0; xPar < nPars; ++xPar){
        std::cout << "[";
        for(int yPar = 0; yPar < nPars-1; ++yPar){
            std::cout << std::fixed << std::setprecision(2) << std::setw(5) << covMatrix[xPar * nPars + yPar]/errors[xPar]/errors[yPar] << ", ";
        }
        std::cout << std::fixed << std::setprecision(2) << std::setw(5) << covMatrix[xPar * nPars + nPars-1]/errors[xPar]/errors[nPars-1] << "]\n";
    }
}
// direct from Rene Brun and the tutorials
void CopyDir(TDirectory *source, TDirectory *adir) {
   //copy all objects and subdirs of directory source as a subdir of the current directory
   //source->ls();
   adir->cd();
   //loop on all entries of this directory
   TKey *key;
   TIter nextkey(source->GetListOfKeys());
   
   while ((key = (TKey*)nextkey())) {
      const char *classname = key->GetClassName();
      TClass *cl = gROOT->GetClass(classname);
      if (!cl) continue;
      if (cl->InheritsFrom(TDirectory::Class())) {
         source->cd(key->GetName());
         TDirectory *subdir = gDirectory;
         adir->cd();
         CopyDir(subdir,adir);
         adir->cd();
      } else if (cl->InheritsFrom(TTree::Class())) {
         TTree *T = (TTree*)source->Get(key->GetName());
         adir->cd();
         TTree *newT = T->CloneTree(-1,"fast");
         newT->Write();
      } else {
         source->cd();
         TObject *obj = key->ReadObj();
         adir->cd();
         obj->Write();
         //delete obj;
     }
  }
  //adir->SaveSelf(kTRUE);
  //  std::cout <<  adir->GetName()<< std::endl;
}

int main(int argc, char* argv[]) {
    
    gStyle->SetOptStat(0);
    
    //  #ifndef NCINTEX
    //  ROOT::Cintex::Cintex::Enable();
    //  #endif
    string ConfigName="test.json";
    //Pass an input file name to this script now
    if (argc == 1) {
        cout << "using default" <<  ConfigName << endl;
    }
    if (argc == 2) {
        ConfigName = argv[1];
        cout << "using" << ConfigName <<  endl;
    }
    
    // read in the configuration
    NuConfig config;
    config.Read(ConfigName);
    config.Print();
    std::string inputFileName=config.GetString("InputFile");
    std::string outputFileName = config.GetString("OutputFile2D");
    bool logPlot = config.GetBool("LogPlot");
    bool logX = config.GetBool("LogX");
    double logMinimum = config.GetDouble("LogMinimum");
    double logXMinimum = config.GetDouble("LogXMinimum");
    std::vector<std::string> sidebands = config.GetStringVector("Sidebands");
    std::vector<std::string> categories = config.GetStringVector("Categories");
    std::string pixdirectory = config.GetString("PixDir");
    
    // use this to exclude or include sidebands in the global fit
    std::vector<std::string> include = config.GetStringVector("IncludeInFit");
    std::vector<std::string> backgrounds = config.GetStringVector("Backgrounds");
    std::map<const std::string, bool> includeInFit;
    for (auto s:sidebands){
        includeInFit[s] = false;
        for (auto i:include){
            if (s == i) includeInFit[s] = true;
        }
    }
    std::string varName = config.GetString("Variable");
	std::string varUnit = config.GetString("VariableUnits");
	int lowVarBinCut = config.GetInt("LowestVariableBinCut");
	std::string binVarName = config.GetString("BinningVariable");
	std::string binVarUnit = config.GetString("BinningVariableUnits");
	std::vector<int> lowBin = config.GetIntVector("LowBin");
	std::vector<int> highBin = config.GetIntVector("HighBin");
    std::string fitType = config.GetString("FitType");
    std::string h_template = config.GetString("Template");
    std::string f_template = config.GetString("FitTemplate");
    std::string h_template2D = config.GetString("Template2D");
    std::string f_template2D = config.GetString("FitTemplate2D");
    
    std::vector<int> binSliceMap;
    std::cout << std::endl << std::endl << "{ ";
    for (int i=0; i<lowBin.size(); i++) {
    	int bins = highBin[i]-lowBin[i]+1;
    	for(int j=0; j<bins; j++) {
    		binSliceMap.push_back(i);
    		std::cout << i << " ";
    	}
    }
    std::cout << "}" << std::endl << std::endl;
    
    pixdirectory = pixdirectory+"_"+binVarName;
    std::filesystem::create_directory(pixdirectory.c_str());

    int rebin=1;
    if (config.CheckMember("Rebin")){
        rebin = config.GetInt("Rebin");
    }

	std::cout << "\nReading in and parsing data.\n";
    // read in the data and parse it
    TFile* inputFile = TFile::Open(inputFileName.c_str(),"READ");
    TFile* outputfile = TFile::Open(outputFileName.c_str(),"RECREATE");
    //loop on all entries of this directory
    
    outputfile->cd();
    CopyDir(inputFile,outputfile);
    
    // std::vector<TString> tags = {""};
    TH1F* pot_summary = (TH1F*) inputFile->Get("POT_summary");
    std:vector<double > potinfo(2);
    potinfo[0]=pot_summary->GetBinContent(1);
    potinfo[1]=pot_summary->GetBinContent(3); // this includes any prescale
    pot_summary->Print("ALL");
    TParameter<double>* mcPOT = (TParameter<double>*) &potinfo[1];
    TParameter<double>* dataPOT = (TParameter<double>*) &potinfo[0];
    std::cout << " dataPOT "<< potinfo[0] << " mcPOT " << potinfo[1] << std::endl;
    
    //double POTscale = dataPOT->GetVal()/mcPOT->GetVal();
    double POTscale = potinfo[0]/potinfo[1];
  
    cout << "POT scale factor: " << POTscale << endl;
    
    // make and fill maps that contain pointers to the histograms you want to fit  uses CCQEMAT template
    
    //std::string h_template = "h___%s___%s___%s___reconstructed";
	char cname[1000];
	char fname[1000];
	char cname_slice[1000];
	char fname_slice[1000];
	char cname_combined[1000];
	char fname_combined[1000];
	int nbinsy;
	std::vector<double> sliceLow;
	std::vector<double> sliceHigh;
	bool sliceboundariesfilled = 0;
	std::string h_template_slice = h_template + "_%s_%02d";
	std::string f_template_slice = f_template + "_%s_%02d";
	std::string h_template_combined = h_template + "_combined";
	std::string f_template_combined = f_template + "_combined";
	std::map<const std::string, PlotUtils::MnvH2D*> dataHist2D;
	std::map<const std::string, std::vector<PlotUtils::MnvH2D*>> fitHists2D;
	std::map<const std::string, std::vector<PlotUtils::MnvH2D*>> unfitHists2D;
	std::map<const int, std::map<const std::string, PlotUtils::MnvH1D*>> dataHist_slices;
	std::map<const int, std::map<const std::string, std::vector<PlotUtils::MnvH1D*>>> fitHists_slices;
	std::map<const int, std::map<const std::string, std::vector<PlotUtils::MnvH1D*>>> unfitHists_slices;
	std::map<const std::string, PlotUtils::MnvH1D*> dataHist_combined;
	std::map<const std::string, std::vector<PlotUtils::MnvH1D*>> fitHists_combined;
	std::map<const std::string, std::vector<PlotUtils::MnvH1D*>> unfitHists_combined;
	TString name = varName;
    for (auto const side:sidebands){
        std::string cat = "data";
        std::snprintf(cname,1000,h_template2D.c_str(),side.c_str(),cat.c_str(),varName.c_str(),binVarName.c_str());
        std::snprintf(fname,1000,f_template2D.c_str(),side.c_str(),cat.c_str(),varName.c_str(),binVarName.c_str());
        std::cout << " look for " << cname << std::endl;
        dataHist2D[side] = (PlotUtils::MnvH2D*)inputFile->Get(cname);
        
        //dataHist2D[side]->Rebin(rebin);
        std::cout << " nbins " << cname << " " << dataHist2D[side]->GetXaxis()->GetNbins() << std::endl;
        nbinsy = dataHist2D[side]->GetYaxis()->GetNbins();
        if (logPlot) dataHist2D[side]->SetMinimum(logMinimum);
        
        /*for (int i=1; i<=nbinsy; i++){
        	std::snprintf(cname_slice,1000,h_template_slice.c_str(),side.c_str(),cat.c_str(),varName.c_str(),binVarName.c_str(),i);
        	PlotUtils::MnvH1D* newhist_data_slice = (PlotUtils::MnvH1D*)dataHist2D[side]->ProjectionX(cname_slice,i,i);
        	newhist_data_slice->Rebin(rebin);
        	dataHist_slices[i][side] = newhist_data_slice;
        	if (!sliceboundariesfilled) {
        		sliceLow.push_back(dataHist2D[side]->GetYaxis()->GetBinLowEdge(i));
        		sliceHigh.push_back(dataHist2D[side]->GetYaxis()->GetBinUpEdge(i));
        	}
        }*/
        for (int i=0; i<lowBin.size(); i++){
        	std::snprintf(cname_slice,1000,h_template_slice.c_str(),side.c_str(),cat.c_str(),varName.c_str(),binVarName.c_str(),i);
        	PlotUtils::MnvH1D* newhist_data_slice = (PlotUtils::MnvH1D*)dataHist2D[side]->ProjectionX(cname_slice,lowBin[i],highBin[i]);
        	//newhist_data_slice->Rebin(rebin);
        	dataHist_slices[i][side] = newhist_data_slice;
        	if (!sliceboundariesfilled) {
        		sliceLow.push_back(dataHist2D[side]->GetYaxis()->GetBinLowEdge(lowBin[i]));
        		sliceHigh.push_back(dataHist2D[side]->GetYaxis()->GetBinUpEdge(highBin[i]));
        	}
        }
        sliceboundariesfilled = 1;
        
        // Binning variable 1D Hist
        std::snprintf(cname_combined,1000,h_template_combined.c_str(),side.c_str(),cat.c_str(),binVarName.c_str());
        std::snprintf(fname,1000,f_template.c_str(),side.c_str(),cat.c_str(),binVarName.c_str());
        std::cout << " look for " << cname << std::endl;
        dataHist_combined[side] = (PlotUtils::MnvH1D*)dataHist2D[side]->ProjectionY(cname_combined,lowVarBinCut,20);
        
        //dataHist[side]->SetNormBinWidth(1.0);
        //dataHist[sidename] = (TH1D*)dataHist->GetCVHistoWithStatError().Clone();
        for (auto cat:categories){
            std::snprintf(cname,1000,h_template2D.c_str(),side.c_str(),cat.c_str(),varName.c_str(),binVarName.c_str());
            std::snprintf(fname,1000,f_template2D.c_str(),side.c_str(),cat.c_str(),varName.c_str(),binVarName.c_str());
            name = TString(cname);
			std::cout << " look for " << cname << std::endl;
			PlotUtils::MnvH2D* newhist = (PlotUtils::MnvH2D*)inputFile->Get(cname);
			if (!newhist){
				std::cout << " no " << cname << std::endl;
			}
			//newhist->RebinX(rebin);
			if (logPlot) newhist->SetMinimum(logMinimum);
			std::cout << "nbins " << cname << " " << newhist->GetXaxis()->GetNbins() << std::endl;
			SyncBands(newhist);
			newhist->Print();
			newhist->Scale(POTscale);
			newhist->Print();
			newhist->MnvH2DToCSV(std::string(cname)+"_unfit", "./csv/", 1.0, false);
			unfitHists2D[side].push_back(newhist);
			fitHists2D[side].push_back((PlotUtils::MnvH2D*)newhist->Clone(TString(fname)));
			
			// Binning variable 1D Hist
			std::snprintf(cname_combined,1000,h_template_combined.c_str(),side.c_str(),cat.c_str(),binVarName.c_str());
            std::snprintf(fname_combined,1000,f_template.c_str(),side.c_str(),cat.c_str(),binVarName.c_str());
            name = TString(cname);
			//std::cout << " look for " << cname << std::endl;
			//PlotUtils::MnvH1D* newhist_combined = (PlotUtils::MnvH1D*)inputFile->Get(cname);
			std::cout << " projecting " << cname << " to get " << cname_combined << std::endl;
			PlotUtils::MnvH1D* newhist_combined = (PlotUtils::MnvH1D*)newhist->ProjectionY(cname_combined,lowVarBinCut,20);
			SyncBands(newhist_combined);
			if (!newhist_combined){
				std::cout << " no " << cname_combined << std::endl;
			}
			//newhist->RebinX(rebin);
			if (logPlot) newhist_combined->SetMinimum(logMinimum);
			std::cout << "nbins " << cname_combined << " " << newhist_combined->GetXaxis()->GetNbins() << std::endl;
			newhist_combined->Print();
			//newhist_combined->Scale(POTscale);
			newhist_combined->Print();
			unfitHists_combined[side].push_back(newhist_combined);
			newhist_combined->MnvH1DToCSV(std::string(cname_combined)+"_unfit", "./csv/");
			fitHists_combined[side].push_back((PlotUtils::MnvH1D*)newhist_combined->Clone(TString(fname_combined)));
			
			// Slices
			/*for (int i=1; i<=nbinsy; i++){
				std::snprintf(cname_slice,1000,h_template_slice.c_str(),side.c_str(),cat.c_str(),varName.c_str(),binVarName.c_str(),i);
				std::snprintf(fname_slice,1000,f_template_slice.c_str(),side.c_str(),cat.c_str(),varName.c_str(),binVarName.c_str(),i);
				name = TString(cname_combined);
				PlotUtils::MnvH1D* newhist_slice = (PlotUtils::MnvH1D*)newhist->ProjectionX(cname_slice,i,i);
				newhist_slice->Rebin(rebin);
				SyncBands(newhist_slice);
				std::string cname_slice_num = std::string(cname_slice)+"_unfit_"+std::to_string(i);
				newhist_slice->MnvH1DToCSV(cname_slice_num, "./csv/");
				unfitHists_slices[i][side].push_back(newhist_slice);
				fitHists_slices[i][side].push_back((PlotUtils::MnvH1D*)newhist_slice->Clone(TString(fname_slice)));
			}*/
			for (int i=0; i<lowBin.size(); i++){
				std::snprintf(cname_slice,1000,h_template_slice.c_str(),side.c_str(),cat.c_str(),varName.c_str(),binVarName.c_str(),i);
				std::snprintf(fname_slice,1000,f_template_slice.c_str(),side.c_str(),cat.c_str(),varName.c_str(),binVarName.c_str(),i);
				name = TString(cname_combined);
				PlotUtils::MnvH1D* newhist_slice = (PlotUtils::MnvH1D*)newhist->ProjectionX(cname_slice,lowBin[i],highBin[i]);
				newhist_slice->Rebin(rebin);
				SyncBands(newhist_slice);
				std::string cname_slice_num = std::string(cname_slice)+"_unfit_"+std::to_string(i);
				newhist_slice->MnvH1DToCSV(cname_slice_num, "./csv/");
				unfitHists_slices[i][side].push_back(newhist_slice);
				fitHists_slices[i][side].push_back((PlotUtils::MnvH1D*)newhist_slice->Clone(TString(fname_slice)));
			}
		}
    }
    
    std::cout << "have extracted the inputs" << std::endl;
    
    // now have made a common map for all histograms
    int lowXbin = 1;
    int highXbin = dataHist2D[include[0]]->GetXaxis()->GetNbins();

    fit::fit_type type;
    type = fit::kFastChi2;
    if (fitType == "FastChi2")type = fit::kFastChi2;
    if (fitType == "SlowChi2")type = fit::kSlowChi2;
    if (fitType == "ML")type = fit::kML;
    //std::cout << " Fit type: " << type.name() << std::endl;
    std::cout << " Try to write it out " << std::endl;
    
    outputfile->cd();
	int ret = fit::DoTheFitSlices(fitHists_slices, unfitHists_slices, dataHist_slices, 
	                              fitHists_combined, unfitHists_combined, dataHist_combined, 
	                              includeInFit, categories, type, lowXbin, highXbin, binSliceMap);
    
    // set up for plots
    
    PlotUtils::MnvPlotter mnvPlotter(PlotUtils::kCCQEAntiNuStyle);
    mnvPlotter.draw_normalized_to_bin_width = false;
    TCanvas cF("fit","fit");
    if (logPlot) gPad->SetLogy(1);
    if (logX) gPad->SetLogx(1);
    std::map<const std::string, MnvH1D*> tot_combined;
    std::map<const std::string, MnvH1D*> pre_combined;
    std::map<const std::string, MnvH1D*> bkg_combined;
    std::map<const std::string, MnvH1D*> sig_combined;
    std::map<const std::string, MnvH1D*> bkgsub_combined;
    
    /*std::map<const std::string, MnvH1D*> tot_bin_combined;
    std::map<const std::string, MnvH1D*> pre_bin_combined;
    std::map<const std::string, MnvH1D*> bkg_bin_combined;
    std::map<const std::string, MnvH1D*> sig_bin_combined;
    std::map<const std::string, MnvH1D*> bkgsub_bin_combined;*/
    
    std::map<const std::string, std::map<const int, MnvH1D*>> tot_slices;
    std::map<const std::string, std::map<const int, MnvH1D*>> pre_slices;
    std::map<const std::string, std::map<const int, MnvH1D*>> bkg_slices;
    std::map<const std::string, std::map<const int, MnvH1D*>> sig_slices;
    std::map<const std::string, std::map<const int, MnvH1D*>> bkgsub_slices;
    
    for (auto side:sidebands){
    	
    }
    
    for (auto side:sidebands){
		for (int i=0; i<lowBin.size(); i++){
		    for (int j=0; j<categories.size(); j++){
		        fitHists_slices[i][side][j]->Write();
		        std::snprintf(fname_slice,1000,f_template_slice.c_str(),side.c_str(),"all",varName.c_str(),binVarName.c_str(),i);
		        if (j == 0){
		            tot_slices[side][i] = (MnvH1D*)fitHists_slices[i][side][j]->Clone(TString(fname_slice));
		        }
		        else{
		            tot_slices[side][i]->Add(fitHists_slices[i][side][j]);
		        }
		    }
		    tot_slices[side][i]->MnvH1DToCSV(tot_slices[side][i]->GetName(),"./csv/",1.,false);
		    tot_slices[side][i]->Print();
		    tot_slices[side][i]->Write();
		    //if (i == 1) {
		    //	tot_slices[side][i] = (MnvH1D*)fitHists_slices[i][side][j]->Clone(TString(fname_slice));
		    //}
        }
        for (int j=0; j<categories.size(); j++){
        	fitHists_combined[side][j]->Write();
        	std::snprintf(fname,1000,f_template_combined.c_str(),side.c_str(),"all",binVarName.c_str());
        	if (j == 0){
	            tot_combined[side] = (MnvH1D*)fitHists_combined[side][j]->Clone(TString(fname));
	        }
	        else{
	            tot_combined[side]->Add(fitHists_combined[side][j]);
	        }
        }
        tot_combined[side]->MnvH1DToCSV(tot_combined[side]->GetName(),"./csv/",1.,false);
	    tot_combined[side]->Print();
	    tot_combined[side]->Write();
    }
    std::cout << "wrote the results " << std::endl;
    
    
    for (auto side:sidebands){
    	for (int i=0; i<lowBin.size(); i++){
		    for (int j=0; j<categories.size(); j++){
		        std::snprintf(cname,1000, h_template_slice.c_str(),side.c_str(),"all",varName.c_str(),binVarName.c_str(),i);
		        if (j == 0){
		            pre_slices[side][i] = (MnvH1D*)unfitHists_slices[i][side][j]->Clone(TString(cname));
		        }
		        else{
		            pre_slices[side][i]->Add(unfitHists_slices[i][side][j]);
		        }
		    }
		    pre_slices[side][i]->Print();
		    pre_slices[side][i]->Write();
		    pre_slices[side][i]->MnvH1DToCSV(pre_slices[side][i]->GetName(),"./csv/",1.,false);
        }
        for (int j=0; j<categories.size(); j++){
	        std::snprintf(cname,1000, h_template_combined.c_str(),side.c_str(),"all",binVarName.c_str());
	        if (j == 0){
	            pre_combined[side] = (MnvH1D*)unfitHists_combined[side][j]->Clone(TString(cname));
	        }
	        else{
	            pre_combined[side]->Add(unfitHists_combined[side][j]);
	        }
	    }
	    pre_combined[side]->Print();
	    pre_combined[side]->Write();
	    pre_combined[side]->MnvH1DToCSV(pre_combined[side]->GetName(),"./csv/",1.,false);
    }
    // this loops over, finds the categories that are in the backgrounds and sums those to get a background
    // uses this whole counter thing to avoid having to figure out how to do string searches in a list in C++
    
    for (auto side:sidebands){
    	for (int i=0; i<lowBin.size(); i++){
		    int count = 0;
		    for (int j=0; j<categories.size(); j++){
		        for (int k=0; k<backgrounds.size(); k++){
		            //std::cout << "match " << categories[i] << " " << backgrounds[j] << " " << count << std::endl;
		            if (categories[j] == backgrounds[k]){
		                 std::snprintf(fname_slice,1000,f_template_slice.c_str(),side.c_str(), "bkg",varName.c_str(),binVarName.c_str(),i);
		                if (count == 0){
		                    bkg_slices[side][i] = (MnvH1D*)fitHists_slices[i][side][j]->Clone(TString(fname_slice));
		                    count +=1;
		                }
		                else{
		                    bkg_slices[side][i]->Add(fitHists_slices[i][side][j]);
		                }
		            }
		        }
		        if (count > 0){
		            bkg_slices[side][i]->Print();
		            bkg_slices[side][i]->Write();
		            bkg_slices[side][i]->MnvH1DToCSV(bkg_slices[side][i]->GetName(),"./csv/",1.,false);
		        }
		    }
        }
        int count = 0;
        for (int j=0; j<categories.size(); j++){
	        for (int k=0; k<backgrounds.size(); k++){
	            //std::cout << "match " << categories[i] << " " << backgrounds[j] << " " << count << std::endl;
	            if (categories[j] == backgrounds[k]){
	                 std::snprintf(fname_combined,1000,f_template_combined.c_str(),side.c_str(),"bkg",binVarName.c_str());
	                if (count == 0){
	                    bkg_combined[side] = (MnvH1D*)fitHists_combined[side][j]->Clone(TString(fname_combined));
	                    count +=1;
	                }
	                else{
	                    bkg_combined[side]->Add(fitHists_combined[side][j]);
	                }
	            }
	        }
	        if (count > 0){
	            bkg_combined[side]->Print();
	            bkg_combined[side]->Write();
	            bkg_combined[side]->MnvH1DToCSV(bkg_combined[side]->GetName(),"./csv/",1.,false);
	        }
	    }
    }
    for (auto side:sidebands){
    	for (int i=0; i<lowBin.size(); i++){
		    std::snprintf(fname_slice,1000,f_template_slice.c_str(),side.c_str(),"bkgsub",varName.c_str(),binVarName.c_str(),i);
		    bkgsub_slices[side][i]=(MnvH1D*)dataHist_slices[i][side]->Clone(fname_slice);
		    bkgsub_slices[side][i]->AddMissingErrorBandsAndFillWithCV(*(fitHists_slices[i][side][0]));
		    bkgsub_slices[side][i]->Add(bkg_slices[side][i],-1);
		    bkgsub_slices[side][i]->Write();
		    dataHist_slices[i][side]->MnvH1DToCSV(dataHist_slices[i][side]->GetName(),"./csv/",1.,false);
		    bkgsub_slices[side][i]->MnvH1DToCSV(bkgsub_slices[side][i]->GetName(),"./csv/",1.,false);
        }
        std::snprintf(fname_combined,1000,f_template_combined.c_str(),side.c_str(),"bkgsub",binVarName.c_str());
	    bkgsub_combined[side]=(MnvH1D*)dataHist_combined[side]->Clone(fname_combined);
	    bkgsub_combined[side]->AddMissingErrorBandsAndFillWithCV(*(fitHists_combined[side][0]));
	    bkgsub_combined[side]->Add(bkg_combined[side],-1);
	    bkgsub_combined[side]->Write();
	    dataHist_combined[side]->MnvH1DToCSV(dataHist_combined[side]->GetName(),"./csv/",1.,false);
	    bkgsub_combined[side]->MnvH1DToCSV(bkgsub_combined[side]->GetName(),"./csv/",1.,false);
    }
    std::cout << "wrote the inputs and outputs " << std::endl;
    
    for (auto side:sidebands){
    	for (int i=0; i<lowBin.size(); i++){
		    //dataHist[side]->Print("ALL");
		    dataHist_slices[i][side]->Scale(1.,"width");
		    //dataHist[side]->Print("ALL");
		    tot_slices[side][i]->Scale(1.,"width");
		    pre_slices[side][i]->Scale(1.,"width");
		    bkg_slices[side][i]->Scale(1.,"width");
		    bkgsub_slices[side][i]->Scale(1.,"width");
		    for (int j=0; j<categories.size(); j++){
		        unfitHists_slices[i][side][j]->Scale(1.,"width");
		        fitHists_slices[i][side][j]->Scale(1.,"width");
		    }
        }
        //dataHist[side]->Print("ALL");
	    dataHist_combined[side]->Scale(1.,"width");
	    //dataHist[side]->Print("ALL");
	    tot_combined[side]->Scale(1.,"width");
	    pre_combined[side]->Scale(1.,"width");
	    bkg_combined[side]->Scale(1.,"width");
	    bkgsub_combined[side]->Scale(1.,"width");
	    for (int j=0; j<categories.size(); j++){
	        unfitHists_combined[side][j]->Scale(1.,"width");
	        fitHists_combined[side][j]->Scale(1.,"width");
	    }
    }
    
    mnvPlotter.error_color_map["FitVariations"] = kBlue + 2;
    mnvPlotter.error_color_map["Normalization"] = kAlpine;
    mnvPlotter.error_color_map["GEANT"] = kGreen + 2;
    
    for (auto side:sidebands){
    	for (int i=0; i<lowBin.size(); i++){
			int nbinsX = dataHist_slices[i][side]->GetXaxis()->GetNbins();
			double xMin = dataHist_slices[i][side]->GetXaxis()->GetBinLowEdge(1);
			double xMax = dataHist_slices[i][side]->GetXaxis()->GetBinUpEdge(nbinsX);
			if (logX) {
				std::cout << "Setting log minimum for X axis." << std::endl;
				gPad->SetLogx(1);
				dataHist_slices[i][side]->GetXaxis()->SetRangeUser(logXMinimum,xMax);
				tot_slices[side][i]->GetXaxis()->SetRangeUser(logXMinimum,xMax);
				pre_slices[side][i]->GetXaxis()->SetRangeUser(logXMinimum,xMax);
				//dataHist_slices[i][side]->SetAxisRange(logXMinimum,xMax,"X");
				//tot_slices[side][i]->SetAxisRange(logXMinimum,xMax,"X");
				//pre_slices[side][i]->SetAxisRange(logXMinimum,xMax,"X");
			}
			else {
				gPad->SetLogx(0);
				dataHist_slices[i][side]->GetXaxis()->SetRangeUser(xMin,xMax);
				tot_slices[side][i]->GetXaxis()->SetRangeUser(xMin,xMax);
				pre_slices[side][i]->GetXaxis()->SetRangeUser(xMin,xMax);
				//dataHist_slices[i][side]->SetAxisRange(xMin,xMax,"X");
				//tot_slices[side][i]->SetAxisRange(xMin,xMax,"X");
				//pre_slices[side][i]->SetAxisRange(xMin,xMax,"X");
			}
		    dataHist_slices[i][side]->SetTitle(dataHist_slices[i][side]->GetName());
		    TString pixheader = TString(pixdirectory+ "/" + side + "_" + varName+"_");
		    
		    std::string ytitle;
			if (varUnit == "") ytitle = "Counts per bin";
			else ytitle = "Counts per "+varUnit;
			TText ty(0.05,0.3,ytitle.c_str());
			ty.SetTitle(ytitle.c_str());
		    ty.SetNDC(1);
		    ty.SetTextSize(.06);
		    ty.SetTextAngle(90);
			
		    mnvPlotter.DrawDataMCWithErrorBand(dataHist_slices[i][side], tot_slices[side][i], 1., "TR");
			//std::string label1;
			//label1 = side+" compare after fit, "+sliceLow[i-1]+" < Q2QE < "+sliceHigh[i-1];
			char label1[1000];
			std::snprintf(label1,1000,"%s compare after fit, %g < %s <= %g",side.c_str(),sliceLow[i],binVarName.c_str(),sliceHigh[i]);
			TText t1(.5,.95,label1);
			t1.SetTitle(label1);
			t1.SetTextAlign(22);
			t1.SetNDC(1);
			t1.SetTextSize(.03);
			t1.Draw("same");
			ty.Draw("same");
		    cF.Print(TString(pixheader + "_postfit_compare_"+binVarName+"_slice"+i+".png").Data());

		    mnvPlotter.DrawDataMCWithErrorBand(dataHist_slices[i][side], pre_slices[side][i], 1., "TR", false , NULL, NULL, false, true);
			char label2[1000];
			std::snprintf(label2,1000,"%s compare before fit, %g < %s <= %g",side.c_str(),sliceLow[i],binVarName.c_str(),sliceHigh[i]);
		    TText t2(.5,.95,label2);
			t2.SetTitle(label2);
			t2.SetTextAlign(22);
			t2.SetNDC(1);
			t2.SetTextSize(.03);
			t2.Draw("same");
			ty.Draw("same");
		    cF.Print(TString(pixheader + "_prefit_compare_"+binVarName+"_slice"+i+".png").Data());
		    
		    mnvPlotter.DrawDataMCRatio(dataHist_slices[i][side], tot_slices[side][i], 1. ); //, true, true, "TL");// false , NULL, NULL, false, true);
			char label3[1000];
			std::snprintf(label3,1000,"%s ratio after fit, %g < %s <= %g",side.c_str(),sliceLow[i],binVarName.c_str(),sliceHigh[i]);
		    TText t3(.5,.95,label3);
			t3.SetTitle(label3);
			t3.SetTextAlign(22);
			t3.SetNDC(1);
			t3.SetTextSize(.03);
			t3.Draw("same");
		    cF.Print(TString(pixheader + "_postfit_compare_ratio_"+binVarName+"_slice"+i+".png").Data());

		    mnvPlotter.DrawDataMCRatio(dataHist_slices[i][side], pre_slices[side][i], 1. ); //, true, true, "TL");// false , NULL, NULL, false, true);
			char label4[1000];
			std::snprintf(label4,1000,"%s ratio before fit, %g < %s <= %g",side.c_str(),sliceLow[i],binVarName.c_str(),sliceHigh[i]);
		    TText t4(.5,.95,label4);
			t4.SetTitle(label4);
			t4.SetTextAlign(22);
			t4.SetNDC(1);
			t4.SetTextSize(.03);
			t4.Draw("same");
		    cF.Print(TString(pixheader + "_prefit_compare_ratio_"+binVarName+"_slice"+i+".png").Data());

		    mnvPlotter.DrawErrorSummary(pre_slices[side][i]);
			char label5[1000];
			std::snprintf(label5,1000,"%s errors before fit, %g < %s <= %g",side.c_str(),sliceLow[i],binVarName.c_str(),sliceHigh[i]);
		    TText t5(.5,.95,label5);
			t5.SetTitle(label5);
			t5.SetTextAlign(22);
			t5.SetNDC(1);
			t5.SetTextSize(.03);
			t5.Draw("same");
		    cF.Print(TString(pixheader + "_prefit_errors_"+binVarName+"_slice"+i+".png").Data());

		    mnvPlotter.DrawErrorSummary(tot_slices[side][i]);
			char label6[1000];
			std::snprintf(label6,1000,"%s errors after fit, %g < %s <= %g",side.c_str(),sliceLow[i],binVarName.c_str(),sliceHigh[i]);
		    TText t6(.5,.95,label6);
			t6.SetTitle(label6);
			t6.SetTextAlign(22);
			t6.SetNDC(1);
			t6.SetTextSize(.03);
			t6.Draw("same");
		    cF.Print(TString(pixheader + "_postfit_errors_"+binVarName+"_slice"+i+".png").Data());

        }
        int nbinsX = dataHist_combined[side]->GetXaxis()->GetNbins();
		double xMin = dataHist_combined[side]->GetXaxis()->GetBinLowEdge(1);
		double xMax = dataHist_combined[side]->GetXaxis()->GetBinUpEdge(nbinsX);
		if (binVarName=="Q2QE") {
			std::cout << "Setting log minimum for X axis." << std::endl;
			gPad->SetLogx(1);
			dataHist_combined[side]->GetXaxis()->SetRangeUser(logXMinimum,xMax);
			tot_combined[side]->GetXaxis()->SetRangeUser(logXMinimum,xMax);
			pre_combined[side]->GetXaxis()->SetRangeUser(logXMinimum,xMax);
			//dataHist_slices[i][side]->SetAxisRange(logXMinimum,xMax,"X");
			//tot_slices[side][i]->SetAxisRange(logXMinimum,xMax,"X");
			//pre_slices[side][i]->SetAxisRange(logXMinimum,xMax,"X");
		}
		else {
			gPad->SetLogx(0);
			dataHist_combined[side]->GetXaxis()->SetRangeUser(xMin,xMax);
			tot_combined[side]->GetXaxis()->SetRangeUser(xMin,xMax);
			pre_combined[side]->GetXaxis()->SetRangeUser(xMin,xMax);
			//dataHist_slices[i][side]->SetAxisRange(xMin,xMax,"X");
			//tot_slices[side][i]->SetAxisRange(xMin,xMax,"X");
			//pre_slices[side][i]->SetAxisRange(xMin,xMax,"X");
		}
		// Combined Slices
	    dataHist_combined[side]->SetTitle(dataHist_combined[side]->GetName());
	    TString pixheader_combined = TString(pixdirectory + "/" + side + "_" + binVarName+"_");
	    
	    std::string ytitle;
		if (binVarUnit == "") ytitle = "Counts per bin";
		else ytitle = "Counts per "+binVarUnit;
		TText ty(0.05,0.3,ytitle.c_str());
		ty.SetTitle(ytitle.c_str());
	    ty.SetNDC(1);
	    ty.SetTextSize(.06);
	    ty.SetTextAngle(90);
		
	    mnvPlotter.DrawDataMCWithErrorBand(dataHist_combined[side], tot_combined[side], 1., "TR");
		char label1[1000];
		std::snprintf(label1,1000,"%s compare after fit",side.c_str());
		TText t1(.5,.95,label1);
		t1.SetTitle(label1);
		t1.SetTextAlign(22);
		t1.SetNDC(1);
		t1.SetTextSize(.03);
		t1.Draw("same");
		ty.Draw("same");
	    cF.Print(TString(pixheader_combined + "_postfit_compare_combined.png").Data());

	    mnvPlotter.DrawDataMCWithErrorBand(dataHist_combined[side], pre_combined[side], 1., "TR", false , NULL, NULL, false, true);
		char label2[1000];
		std::snprintf(label2,1000,"%s compare before fit",side.c_str());
	    TText t2(.5,.95,label2);
		t2.SetTitle(label2);
		t2.SetTextAlign(22);
		t2.SetNDC(1);
		t2.SetTextSize(.03);
		t2.Draw("same");
		ty.Draw("same");
	    cF.Print(TString(pixheader_combined + "_prefit_compare_combined.png").Data());
	    
	    mnvPlotter.DrawDataMCRatio(dataHist_combined[side], tot_combined[side], 1. ); //, true, true, "TL");// false , NULL, NULL, false, true);
		char label3[1000];
		std::snprintf(label3,1000,"%s ratio after fit",side.c_str());
	    TText t3(.5,.95,label3);
		t3.SetTitle(label3);
		t3.SetTextAlign(22);
		t3.SetNDC(1);
		t3.SetTextSize(.03);
		t3.Draw("same");
	    cF.Print(TString(pixheader_combined + "_postfit_compare_ratio_combined.png").Data());

	    mnvPlotter.DrawDataMCRatio(dataHist_combined[side], pre_combined[side], 1. ); //, true, true, "TL");// false , NULL, NULL, false, true);
		char label4[1000];
		std::snprintf(label4,1000,"%s ratio before fit",side.c_str());
	    TText t4(.5,.95,label4);
		t4.SetTitle(label4);
		t4.SetTextAlign(22);
		t4.SetNDC(1);
		t4.SetTextSize(.03);
		t4.Draw("same");
	    cF.Print(TString(pixheader_combined + "_prefit_compare_ratio_combined.png").Data());

	    mnvPlotter.DrawErrorSummary(pre_combined[side]);
		char label5[1000];
		std::snprintf(label5,1000,"%s errors before fit",side.c_str());
	    TText t5(.5,.95,label5);
		t5.SetTitle(label5);
		t5.SetTextAlign(22);
		t5.SetNDC(1);
		t5.SetTextSize(.03);
		t5.Draw("same");
	    cF.Print(TString(pixheader_combined + "_prefit_errors_combined.png").Data());

	    mnvPlotter.DrawErrorSummary(tot_combined[side]);
		char label6[1000];
		std::snprintf(label6,1000,"%s errors after fit",side.c_str());
	    TText t6(.5,.95,label6);
		t6.SetTitle(label6);
		t6.SetTextAlign(22);
		t6.SetNDC(1);
		t6.SetTextSize(.03);
		t6.Draw("same");
	    cF.Print(TString(pixheader_combined + "_postfit_errors_combined.png").Data());

	    //mnvPlotter.DrawDataMCWithErrorBand(bkgsub_slices[side][i], fitHists_slices[i][side][0], 1., "TR");
	    //cF.Print(TString(side+"_bkgsub_compare_slice"+i+".png").Data());
    }
    
    TObjArray* combmcin;
    TObjArray* combmcout;
    
    for (auto side:sidebands){
        TString pixheader = TString(pixdirectory + "/" + side + "_" + varName + "_");
        for (int i=0; i<lowBin.size(); i++){
		    int nbinsX = dataHist_slices[i][side]->GetXaxis()->GetNbins();
			double xMin = dataHist_slices[i][side]->GetXaxis()->GetBinLowEdge(1);
			double xMax = dataHist_slices[i][side]->GetXaxis()->GetBinUpEdge(nbinsX);
			if (logX) {
				std::cout << "Setting log minimum for X axis." << std::endl;
				gPad->SetLogx(1);
				dataHist_slices[i][side]->GetXaxis()->SetRangeUser(logXMinimum,xMax);
				bkgsub_slices[side][i]->GetXaxis()->SetRangeUser(logXMinimum,xMax);
				//dataHist[side]->SetAxisRange(logXMinimum,xMax,"X");
				//bkgsub[side]->SetAxisRange(logXMinimum,xMax,"X");
				for (int j=0; j<categories.size(); j++) {
					unfitHists_slices[i][side][j]->GetXaxis()->SetRangeUser(logXMinimum,xMax);
					fitHists_slices[i][side][j]->GetXaxis()->SetRangeUser(logXMinimum,xMax);
					//unfitHists[side][i]->SetAxisRange(logXMinimum,xMax,"X");
					//fitHists[side][i]->SetAxisRange(logXMinimum,xMax,"X");
				}
			}
			else {
				gPad->SetLogx(0);
				dataHist_slices[i][side]->GetXaxis()->SetRangeUser(xMin,xMax);
				bkgsub_slices[side][i]->GetXaxis()->SetRangeUser(xMin,xMax);
				//dataHist[side]->SetAxisRange(xMin,xMax,"X");
				//bkgsub[side]->SetAxisRange(xMin,xMax,"X");
				for (int j=0; j<categories.size(); j++) {
					unfitHists_slices[i][side][j]->GetXaxis()->SetRangeUser(xMin,xMax);
					fitHists_slices[i][side][j]->GetXaxis()->SetRangeUser(xMin,xMax);
					//unfitHists[side][i]->SetAxisRange(xMin,xMax,"X");
					//fitHists[side][i]->SetAxisRange(xMin,xMax,"X");
				}
			}

		    std::string label;
		    label = side+" "+varName;
		    combmcin  = Vec2TObjArray(unfitHists_slices[i][side],categories);
		    combmcout = Vec2TObjArray(fitHists_slices[i][side],categories);
		    std::cout << " before call to DrawStack" << std::endl;
		    PlotUtils::MnvH1D* data = new PlotUtils::MnvH1D(*(dataHist_slices[i][side]));
		    data->SetTitle("Data");
		    
		    std::string ytitle;
		    double ybottom;
			if (varUnit == "") ytitle = "Counts per bin";
			else ytitle = "Counts per "+varUnit;
			TText ty(0.05,0.3,ytitle.c_str());
			ty.SetTitle(ytitle.c_str());
		    ty.SetNDC(1);
		    ty.SetTextSize(.06);
		    ty.SetTextAngle(90);
		    
			char label1[1000];
			std::snprintf(label1,1000,"%s %s before fit, %g < %s <= %g",side.c_str(),varName.c_str(),sliceLow[i],binVarName.c_str(),sliceHigh[i]);
		    TText t(.5,.95,label1);
		    t.SetTitle(label1);
		    t.SetTextAlign(22);
		    t.SetNDC(1);
		    t.SetTextSize(.03);
		    if (logPlot) data->SetMinimum(logMinimum);
		    mnvPlotter.DrawDataStackedMC(data,combmcin,1.0,"TR");
		    t.Draw("same");
		    ty.Draw("same");
		    cF.Print(TString(pixheader + "_prefit_combined_"+binVarName+"_slice"+i+".png").Data());
		    
			char label2[1000];
			std::snprintf(label2,1000,"%s %s after fit, %g < %s <= %g",side.c_str(),varName.c_str(),sliceLow[i],binVarName.c_str(),sliceHigh[i]);
		    TText t2(.5,.95,label2);
		    t2.SetTitle(label2);
		    t2.SetTextAlign(22);
		    t2.SetNDC(1);
		    t2.SetTextSize(.03);
		    mnvPlotter.DrawDataStackedMC(data,combmcout,1.0,"TR");
		    t2.Draw("same");
		    ty.Draw("same");
		    cF.Print(TString(pixheader + "_" + fitType + "_postfit_combined_"+binVarName+"_slice"+i+".png").Data());
		    
			char label3[1000];
			std::snprintf(label3,1000,"%s %s Background Subtracted, %g < %s <= %g",side.c_str(),varName.c_str(),sliceLow[i],binVarName.c_str(),sliceHigh[i]);
		    TText t3(.5,.95,label3);
		    t3.SetTitle(label3);
		    t3.SetTextAlign(22);
		    t3.SetNDC(1);
		    t3.SetTextSize(.03);
		    bkgsub_slices[side][i]->SetTitle("bkgsub");
		    mnvPlotter.DrawDataMCWithErrorBand(bkgsub_slices[side][i],(MnvH1D*)fitHists_slices[i][side][0], 1.0, "TR");
		    t3.Draw("same");
		    ty.Draw("same");
		    cF.Print(TString(pixheader + "_" + fitType + "_bkgsub_combined_"+binVarName+"_slice"+i+".png").Data());
		    
		   /* mnvPlotter.DrawDataMCRatio(dataHist_slices[i][side], tot_slices[side][i], 1. ); //, true, true, "TL");// false , NULL, NULL, false, true);
		    label = side+" ratio after fit, slice "+i;
		    TText t4(.5,.95,label.c_str());
			t4.SetTitle(label.c_str());
			t4.SetTextAlign(22);
			t4.SetNDC(1);
			t4.SetTextSize(.03);
			t4.Draw("same");
		    cF.Print(TString(pixheader + "_bkgsub_compare_ratio_slice"+i+".png").Data());*/
		    
			char label5[1000];
			std::snprintf(label5,1000,"%s %s errors after Background Subtracted, %g < %s <= %g",side.c_str(),varName.c_str(),sliceLow[i],binVarName.c_str(),sliceHigh[i]);
		    TText t5(.5,.95,label5);
		    t5.SetTitle(label5);
		    t5.SetTextAlign(22);
		    t5.SetNDC(1);
		    t5.SetTextSize(.03);
		    mnvPlotter.DrawErrorSummary(bkgsub_slices[side][i]);
		    std::string label6;
			t5.Draw("same");
		    cF.Print(TString(pixheader + "_bkgsub_errors_"+binVarName+"_slice"+i+".png").Data());
        }
        TString pixheader_combined = TString(pixdirectory + "/" + side + "_" + binVarName + "_");
        int nbinsX = dataHist_combined[side]->GetXaxis()->GetNbins();
		double xMin = dataHist_combined[side]->GetXaxis()->GetBinLowEdge(1);
		double xMax = dataHist_combined[side]->GetXaxis()->GetBinUpEdge(nbinsX);
		if (binVarName=="Q2QE") {
			std::cout << "Setting log minimum for X axis." << std::endl;
			gPad->SetLogx(1);
			dataHist_combined[side]->GetXaxis()->SetRangeUser(logXMinimum,xMax);
			bkgsub_combined[side]->GetXaxis()->SetRangeUser(logXMinimum,xMax);
			//dataHist[side]->SetAxisRange(logXMinimum,xMax,"X");
			//bkgsub[side]->SetAxisRange(logXMinimum,xMax,"X");
			for (int j=0; j<categories.size(); j++) {
				unfitHists_combined[side][j]->GetXaxis()->SetRangeUser(logXMinimum,xMax);
				fitHists_combined[side][j]->GetXaxis()->SetRangeUser(logXMinimum,xMax);
				//unfitHists[side][i]->SetAxisRange(logXMinimum,xMax,"X");
				//fitHists[side][i]->SetAxisRange(logXMinimum,xMax,"X");
			}
		}
		else {
			gPad->SetLogx(0);
			dataHist_combined[side]->GetXaxis()->SetRangeUser(xMin,xMax);
			bkgsub_combined[side]->GetXaxis()->SetRangeUser(xMin,xMax);
			//dataHist[side]->SetAxisRange(xMin,xMax,"X");
			//bkgsub[side]->SetAxisRange(xMin,xMax,"X");
			for (int j=0; j<categories.size(); j++) {
				unfitHists_combined[side][j]->GetXaxis()->SetRangeUser(xMin,xMax);
				fitHists_combined[side][j]->GetXaxis()->SetRangeUser(xMin,xMax);
				//unfitHists[side][i]->SetAxisRange(xMin,xMax,"X");
				//fitHists[side][i]->SetAxisRange(xMin,xMax,"X");
			}
		}

	    std::string label;
	    label = side+" "+binVarName;
	    combmcin  = Vec2TObjArray(unfitHists_combined[side],categories);
	    combmcout = Vec2TObjArray(fitHists_combined[side],categories);
	    std::cout << " before call to DrawStack" << std::endl;
	    PlotUtils::MnvH1D* data = new PlotUtils::MnvH1D(*(dataHist_combined[side]));
	    data->SetTitle("Data");
	    
	    std::string ytitle;
	    double ybottom;
		if (binVarUnit == "") ytitle = "Counts per bin";
		else ytitle = "Counts per "+binVarUnit;
		TText ty(0.05,0.3,ytitle.c_str());
		ty.SetTitle(ytitle.c_str());
	    ty.SetNDC(1);
	    ty.SetTextSize(.06);
	    ty.SetTextAngle(90);
	     
		char label1[1000];
		std::snprintf(label1,1000,"%s %s before fit",side.c_str(),binVarName.c_str());
	    TText t(.5,.95,label1);
	    t.SetTitle(label1);
	    t.SetTextAlign(22);
	    t.SetNDC(1);
	    t.SetTextSize(.03);
	    if (logPlot) data->SetMinimum(logMinimum);
	    mnvPlotter.DrawDataStackedMC(data,combmcin,1.0,"TR");
	    t.Draw("same");
	    ty.Draw("same");
	    cF.Print(TString(pixheader_combined + "_prefit_combined_combined.png").Data());
	    
		char label2[1000];
		std::snprintf(label2,1000,"%s %s after fit",side.c_str(),binVarName.c_str());
	    TText t2(.5,.95,label2);
	    t2.SetTitle(label2);
	    t2.SetTextAlign(22);
	    t2.SetNDC(1);
	    t2.SetTextSize(.03);
	    mnvPlotter.DrawDataStackedMC(data,combmcout,1.0,"TR");
	    t2.Draw("same");
	    ty.Draw("same");
	    cF.Print(TString(pixheader_combined + "_" + fitType + "_postfit_combined_combined.png").Data());
	    
		char label3[1000];
		std::snprintf(label3,1000,"%s %s Background Subtracted",side.c_str(),binVarName.c_str());
	    TText t3(.5,.95,label3);
	    t3.SetTitle(label3);
	    t3.SetTextAlign(22);
	    t3.SetNDC(1);
	    t3.SetTextSize(.03);
	    bkgsub_combined[side]->SetTitle("bkgsub");
	    mnvPlotter.DrawDataMCWithErrorBand(bkgsub_combined[side],(MnvH1D*)fitHists_combined[side][0], 1.0, "TR");
	    t3.Draw("same");
	    ty.Draw("same");
	    cF.Print(TString(pixheader_combined + "_" + fitType + "_bkgsub_combined_combined.png").Data());
	    
	   /* mnvPlotter.DrawDataMCRatio(dataHist_slices[i][side], tot_slices[side][i], 1. ); //, true, true, "TL");// false , NULL, NULL, false, true);
	    label = side+" ratio after fit, slice "+i;
	    TText t4(.5,.95,label.c_str());
		t4.SetTitle(label.c_str());
		t4.SetTextAlign(22);
		t4.SetNDC(1);
		t4.SetTextSize(.03);
		t4.Draw("same");
	    cF.Print(TString(pixheader_combined + "_bkgsub_compare_ratio_combined.png").Data());*/
	    
		char label5[1000];
		std::snprintf(label5,1000,"%s %s errors after Background Subtracted",side.c_str(),binVarName.c_str());
	    TText t5(.5,.95,label5);
	    t5.SetTitle(label5);
	    t5.SetTextAlign(22);
	    t5.SetNDC(1);
	    t5.SetTextSize(.03);
	    mnvPlotter.DrawErrorSummary(bkgsub_combined[side]);
	    std::string label6;
		t5.Draw("same");
	    cF.Print(TString(pixheader_combined + "_bkgsub_errors_combined.png").Data());
    }
    
    //inputFile->Close();
    outputfile->Close();
    cout << "Closing Output File... Does this solve the issue of seg fault." << endl;
   
    
    cout << "HEY YOU DID IT!!!" << endl;
    return 0;
}
