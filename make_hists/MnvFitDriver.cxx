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
    std::string outputFileName = config.GetString("OutputFile");
    bool logPlot = config.GetBool("LogPlot");
    bool logX = config.GetBool("LogX");
    NuConfig addLogX = config.GetConfig("AdditionalLogX");
    double logMinimum = config.GetDouble("LogMinimum");
    double logXMinimum = config.GetDouble("LogXMinimum");
    std::vector<std::string> sidebands = config.GetStringVector("Sidebands");
    std::vector<std::string> categories = config.GetStringVector("Categories");
    std::string pixdirectory = config.GetString("PixDir");
    
    std::filesystem::create_directory(pixdirectory.c_str());
    
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
	std::vector<std::string> addVarNames = config.GetStringVector("AdditionalVariables");
	std::string varUnit = config.GetString("VariableUnits");
	NuConfig addVarUnits = config.GetConfig("AdditionalVariablesUnits");
    std::string fitType = config.GetString("FitType");
    std::string h_template = config.GetString("Template");
    std::string f_template = config.GetString("FitTemplate");

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
	std::map<const std::string, PlotUtils::MnvH1D*> dataHist;
	std::map<const std::string, std::vector<PlotUtils::MnvH1D*>> fitHists;
	std::map<const std::string, std::vector<PlotUtils::MnvH1D*>> unfitHists;
	std::map<const std::string, std::map<const std::string, PlotUtils::MnvH1D*>> addDataHist;
	std::map<const std::string, std::map<const std::string, std::vector<PlotUtils::MnvH1D*>>> addFitHists;
	std::map<const std::string, std::map<const std::string, std::vector<PlotUtils::MnvH1D*>>> addUnfitHists;
	TString name = varName;
    for (auto const side:sidebands){
        std::string cat = "data";
        std::snprintf(cname,1000,h_template.c_str(),side.c_str(), cat.c_str(),varName.c_str());
        std::snprintf(fname,1000,f_template.c_str(),side.c_str(), cat.c_str(),varName.c_str());
        std::cout << " look for " << cname << std::endl;
        dataHist[side] = (PlotUtils::MnvH1D*)inputFile->Get(cname);
        
        dataHist[side]->Rebin(rebin);
        std::cout << " nbins " << cname << " " << dataHist[side]->GetXaxis()->GetNbins() << std::endl;
        if (logPlot) dataHist[side]->SetMinimum(logMinimum);
        
        for (auto addVarName:addVarNames) {
        	std::snprintf(cname,1000,h_template.c_str(),side.c_str(), cat.c_str(),addVarName.c_str());
		    std::snprintf(fname,1000,f_template.c_str(),side.c_str(), cat.c_str(),addVarName.c_str());
		    std::cout << " look for " << cname << std::endl;
		    addDataHist[side][addVarName] = (PlotUtils::MnvH1D*)inputFile->Get(cname);
		    
		    addDataHist[side][addVarName]->Rebin(rebin);
		    std::cout << " nbins " << cname << " " << addDataHist[side][addVarName]->GetXaxis()->GetNbins() << std::endl;
		    if (logPlot) addDataHist[side][addVarName]->SetMinimum(logMinimum);
        }
        
        //dataHist[side]->SetNormBinWidth(1.0);
        //dataHist[sidename] = (TH1D*)dataHist->GetCVHistoWithStatError().Clone();
        for (auto cat:categories){
            std::snprintf(cname,1000,h_template.c_str(),side.c_str(), cat.c_str(),varName.c_str());
            std::snprintf(fname,1000,f_template.c_str(),side.c_str(), cat.c_str(),varName.c_str());
            name = TString(cname);
			std::cout << " look for " << cname << std::endl;
			MnvH1D* newhist = (PlotUtils::MnvH1D*)inputFile->Get(cname);
			if (!newhist){
				std::cout << " no " << cname << std::endl;
			}
			newhist->Rebin(rebin);
			if (logPlot) newhist->SetMinimum(logMinimum);
			std::cout << "nbins " << cname << " " << newhist->GetXaxis()->GetNbins() << std::endl;
			newhist->Print();
			newhist->Scale(POTscale);
			newhist->Print();
			unfitHists[side].push_back(newhist);
			fitHists[side].push_back((PlotUtils::MnvH1D*)newhist->Clone(TString(fname)));
		}
		for (auto addVarName:addVarNames) {
			for (auto cat:categories){
		        std::snprintf(cname,1000,h_template.c_str(),side.c_str(), cat.c_str(),addVarName.c_str());
		        std::snprintf(fname,1000,f_template.c_str(),side.c_str(), cat.c_str(),addVarName.c_str());
		        name = TString(cname);
				std::cout << " look for " << cname << std::endl;
				MnvH1D* newhist = (PlotUtils::MnvH1D*)inputFile->Get(cname);
				if (!newhist){
					std::cout << " no " << cname << std::endl;
				}
				newhist->Rebin(rebin);
				if (logPlot) newhist->SetMinimum(logMinimum);
				std::cout << "nbins " << cname << " " << newhist->GetXaxis()->GetNbins() << std::endl;
				newhist->Print();
				newhist->Scale(POTscale);
				newhist->Print();
				addUnfitHists[side][addVarName].push_back(newhist);
				addFitHists[side][addVarName].push_back((PlotUtils::MnvH1D*)newhist->Clone(TString(fname)));
			}
		}
        /*for (int i = 0; i < categories.size(); i++){
            unfitHists[side][i]->SetNormBinWidth(1.0);
            fitHists[side][i]->SetNormBinWidth(1.0);
        }*/
    }
    
    std::cout << "have extracted the inputs" << std::endl;
    
    // now have made a common map for all histograms
    int lowBin = 1;
    int hiBin = dataHist[include[0]]->GetXaxis()->GetNbins();
    std::map<const std::string, int> addHiBin;
    /*for (auto addVarName:addVarNames) {
    	addHiBin[addVarName] = dataHist[include[0]][addVarName]->GetXaxis()->GetNbins();
    }*/
    fit::fit_type type;
    type = fit::kFastChi2;
    if (fitType == "FastChi2")type = fit::kFastChi2;
    if (fitType == "SlowChi2")type = fit::kSlowChi2;
    if (fitType == "ML")type = fit::kML;
    //std::cout << " Fit type: " << type.name() << std::endl;
    std::cout << " Try to write it out " << std::endl;
    
    outputfile->cd();
    int ret = fit::DoTheFit(fitHists, unfitHists, dataHist, 
                            addFitHists, addUnfitHists, addDataHist,
                            includeInFit, categories,  type, lowBin, hiBin, addHiBin);
    
    // set up for plots
    
    PlotUtils::MnvPlotter mnvPlotter(PlotUtils::kCCQEAntiNuStyle);
    mnvPlotter.draw_normalized_to_bin_width = false;
    TCanvas cF("fit","fit");
    if (logPlot) gPad->SetLogy(1);
    if (logX) gPad->SetLogx(1);
    std::map<const std::string, MnvH1D*> tot;
    std::map<const std::string, MnvH1D*> pre;
    std::map<const std::string, MnvH1D*> bkg;
    std::map<const std::string, MnvH1D*> sig;
    std::map<const std::string, MnvH1D*> bkgsub;
    
    std::map<const std::string, std::map<const std::string, MnvH1D*>> addTot;
    std::map<const std::string, std::map<const std::string, MnvH1D*>> addPre;
    std::map<const std::string, std::map<const std::string, MnvH1D*>> addBkg;
    std::map<const std::string, std::map<const std::string, MnvH1D*>> addSig;
    std::map<const std::string, std::map<const std::string, MnvH1D*>> addBkgsub;
    
    for (auto side:sidebands){
        //dataHist[side]->Print();
        

        //dataHist[side]->Write();
        
       
        
        for (int i = 0; i < categories.size(); i++){
            fitHists[side][i]->Write();
            //std::sprintf(fname,f_template.c_str(),side.c_str(), "all",varName.c_str());
            std::snprintf(fname, 1000, f_template.c_str(), side.c_str(), "all", varName.c_str());
            if (i == 0){
                tot[side] = (MnvH1D*)fitHists[side][i]->Clone(TString(fname));
            }
            else{
                tot[side]->Add(fitHists[side][i]);
            }
        }
        tot[side]->MnvH1DToCSV(tot[side]->GetName(),"./csv/",1.,false);
        tot[side]->Print();
        tot[side]->Write();
        
        for (auto addVarName:addVarNames) {
        	for (int i = 0; i < categories.size(); i++){
        		addFitHists[side][addVarName][i]->Write();
        		std::snprintf(fname, 1000, f_template.c_str(), side.c_str(), "all", addVarName.c_str());
		        if (i == 0){
		            addTot[side][addVarName] = (MnvH1D*)addFitHists[side][addVarName][i]->Clone(TString(fname));
		        }
		        else{
		            addTot[side][addVarName]->Add(addFitHists[side][addVarName][i]);
		        }
        	}
        }
    }
    std::cout << "wrote the results " << std::endl;
    
    for (auto side:sidebands){
        for (int i = 0; i < categories.size(); i++){
            std::snprintf(cname,1000, h_template.c_str(),side.c_str(), "all",varName.c_str());
            if (i == 0){
                pre[side] = (MnvH1D*)unfitHists[side][i]->Clone(TString(cname));
            }
            else{
                pre[side]->Add(unfitHists[side][i]);
            }
        }
        pre[side]->Print();
        pre[side]->Write();
        pre[side]->MnvH1DToCSV(pre[side]->GetName(),"./csv/",1.,false);
        
        for (auto addVarName:addVarNames) {
        	for (int i = 0; i < categories.size(); i++){
		        std::snprintf(cname,1000, h_template.c_str(),side.c_str(), "all",addVarName.c_str());
		        if (i == 0){
		            addPre[side][addVarName] = (MnvH1D*)addUnfitHists[side][addVarName][i]->Clone(TString(cname));
		        }
		        else{
		            addPre[side][addVarName]->Add(addUnfitHists[side][addVarName][i]);
		        }
		    }
		    addPre[side][addVarName]->Print();
		    addPre[side][addVarName]->Write();
		    addPre[side][addVarName]->MnvH1DToCSV(pre[side]->GetName(),"./csv/",1.,false);
        }
    }
    // this loops over, finds the categories that are in the backgrounds and sums those to get a background
    // uses this whole counter thing to avoid having to figure out how to do string searches in a list in C++
    
    for (auto side:sidebands){
        int count = 0;
        for (int i = 0; i < categories.size(); i++){
            for (int j = 0; j < backgrounds.size(); j++){
                //std::cout << "match " << categories[i] << " " << backgrounds[j] << " " << count << std::endl;
                if (categories[i] == backgrounds[j]){
                     std::snprintf(fname,1000, f_template.c_str(),side.c_str(), "bkg",varName.c_str());
                    if (count == 0){
                        bkg[side] = (MnvH1D*)fitHists[side][i]->Clone(TString(fname));
                        count +=1;
                    }
                    else{
                        bkg[side]->Add(fitHists[side][i]);
                    }
                }
            }
            if (count > 0){
                bkg[side]->Print();
                bkg[side]->Write();
                bkg[side]->MnvH1DToCSV(bkg[side]->GetName(),"./csv/",1.,false);
            }
        }
        
        for (auto addVarName:addVarNames) {
        	int count = 0;
        	for (int i = 0; i < categories.size(); i++){
		        for (int j = 0; j < backgrounds.size(); j++){
		            //std::cout << "match " << categories[i] << " " << backgrounds[j] << " " << count << std::endl;
		            if (categories[i] == backgrounds[j]){
		            	std::snprintf(fname,1000, f_template.c_str(),side.c_str(),"bkg",addVarName.c_str());
		                if (count == 0){
		                    addBkg[side][addVarName] = (MnvH1D*)addFitHists[side][addVarName][i]->Clone(TString(fname));
		                    count +=1;
		                }
		                else{
		                    addBkg[side][addVarName]->Add(addFitHists[side][addVarName][i]);
		                }
		            }
		        }
		        if (count > 0){
		            addBkg[side][addVarName]->Print();
		            addBkg[side][addVarName]->Write();
		            addBkg[side][addVarName]->MnvH1DToCSV(addBkg[side][addVarName]->GetName(),"./csv/",1.,false);
		        }
		    }
        }
    }
    for (auto side:sidebands){
        std::snprintf(fname,1000,f_template.c_str(),side.c_str(), "bkgsub",varName.c_str());
        bkgsub[side]=(MnvH1D*)dataHist[side]->Clone(fname);
        bkgsub[side]->AddMissingErrorBandsAndFillWithCV(*(fitHists[side][0]));
        bkgsub[side]->Add(bkg[side],-1);
        bkgsub[side]->Write();
        dataHist[side]->MnvH1DToCSV(dataHist[side]->GetName(),"./csv/",1.,false);
        bkgsub[side]->MnvH1DToCSV(bkgsub[side]->GetName(),"./csv/",1.,false);
        for (auto addVarName:addVarNames) {
		    std::snprintf(fname,1000,f_template.c_str(),side.c_str(), "bkgsub",addVarName.c_str());
		    addBkgsub[side][addVarName]=(MnvH1D*)addDataHist[side][addVarName]->Clone(fname);
		    addBkgsub[side][addVarName]->AddMissingErrorBandsAndFillWithCV(*(addFitHists[side][addVarName][0]));
		    addBkgsub[side][addVarName]->Add(addBkg[side][addVarName],-1);
		    addBkgsub[side][addVarName]->Write();
		    addDataHist[side][addVarName]->MnvH1DToCSV(addDataHist[side][addVarName]->GetName(),"./csv/",1.,false);
		    addBkgsub[side][addVarName]->MnvH1DToCSV(addBkgsub[side][addVarName]->GetName(),"./csv/",1.,false);
        }
    }
    std::cout << "wrote the inputs and outputs " << std::endl;
    
    for (auto side:sidebands){
        //dataHist[side]->Print("ALL");
        dataHist[side]->Scale(1.,"width");
        //dataHist[side]->Print("ALL");
        tot[side]->Scale(1.,"width");
        pre[side]->Scale(1.,"width");
        bkg[side]->Scale(1.,"width");
        bkgsub[side]->Scale(1.,"width");
        for (int i = 0; i < categories.size(); i++){
            unfitHists[side][i]->Scale(1.,"width");
            fitHists[side][i]->Scale(1.,"width");
        }
        for (auto addVarName:addVarNames) {
		    addDataHist[side][addVarName]->Scale(1.,"width");
		    addTot[side][addVarName]->Scale(1.,"width");
		    addPre[side][addVarName]->Scale(1.,"width");
		    addBkg[side][addVarName]->Scale(1.,"width");
		    addBkgsub[side][addVarName]->Scale(1.,"width");
		    for (int i = 0; i < categories.size(); i++){
		        addUnfitHists[side][addVarName][i]->Scale(1.,"width");
		        addFitHists[side][addVarName][i]->Scale(1.,"width");
		    }
        }
    }
    
    mnvPlotter.error_color_map["FitVariations"] = kBlue + 2;
    mnvPlotter.error_color_map["Normalization"] = kAlpine;
    mnvPlotter.error_color_map["GEANT"] = kGreen + 2;
    
    for (auto side:sidebands){
    	int nbinsX = dataHist[side]->GetXaxis()->GetNbins();
    	double xMin = dataHist[side]->GetXaxis()->GetBinLowEdge(1);
    	double xMax = dataHist[side]->GetXaxis()->GetBinUpEdge(nbinsX);
    	if (logX) {
    		std::cout << "Setting log minimum for X axis." << std::endl;
    		gPad->SetLogx(1);
    		dataHist[side]->GetXaxis()->SetRangeUser(logXMinimum,xMax);
    		tot[side]->GetXaxis()->SetRangeUser(logXMinimum,xMax);
    		pre[side]->GetXaxis()->SetRangeUser(logXMinimum,xMax);
    		//dataHist[side]->SetAxisRange(logXMinimum,xMax,"X");
    		//tot[side]->SetAxisRange(logXMinimum,xMax,"X");
    		//pre[side]->SetAxisRange(logXMinimum,xMax,"X");
    	}
    	else {
    		gPad->SetLogx(0);
    		dataHist[side]->GetXaxis()->SetRangeUser(xMin,xMax);
    		tot[side]->GetXaxis()->SetRangeUser(xMin,xMax);
    		pre[side]->GetXaxis()->SetRangeUser(xMin,xMax);
    		//dataHist[side]->SetAxisRange(xMin,xMax,"X");
    		//tot[side]->SetAxisRange(xMin,xMax,"X");
    		//pre[side]->SetAxisRange(xMin,xMax,"X");
    	}
        dataHist[side]->SetTitle(dataHist[side]->GetName());
        TString pixheader = TString(pixdirectory + "/" + side + "_" + varName+"_");
        
        std::string ytitle;
    	if (varUnit == "") ytitle = "Counts per bin";
    	else ytitle = "Counts per "+varUnit;
    	TText ty(0.05,0.3,ytitle.c_str());
    	ty.SetTitle(ytitle.c_str());
        ty.SetNDC(1);
        ty.SetTextSize(.06);
        ty.SetTextAngle(90);
		
        mnvPlotter.DrawDataMCWithErrorBand(dataHist[side], tot[side], 1., "TR");
		std::string label1;
		label1 = side+" compare after fit";
		TText t1(.3,.95,label1.c_str());
	    t1.SetTitle(label1.c_str());
	    t1.SetNDC(1);
	    t1.SetTextSize(.03);
	    t1.Draw("same");
	    ty.Draw("same");
        cF.Print(TString(pixheader + "_postfit_compare.png").Data());

        mnvPlotter.DrawDataMCWithErrorBand(dataHist[side], pre[side], 1., "TR", false , NULL, NULL, false, true);
        std::string label2;
        label2 = side+" compare before fit";
        TText t2(.3,.95,label2.c_str());
	    t2.SetTitle(label2.c_str());
	    t2.SetNDC(1);
	    t2.SetTextSize(.03);
	    t2.Draw("same");
	    ty.Draw("same");
        cF.Print(TString(pixheader + "_prefit_compare.png").Data());

        mnvPlotter.DrawDataMCRatio(dataHist[side], tot[side], 1. ); //, true, true, "TL");// false , NULL, NULL, false, true);
        std::string label3;
        label3 = side+" ratio after fit";
        TText t3(.3,.95,label3.c_str());
	    t3.SetTitle(label3.c_str());
	    t3.SetNDC(1);
	    t3.SetTextSize(.03);
	    t3.Draw("same");
        cF.Print(TString(pixheader + "_postfit_compare_ratio.png").Data());

        mnvPlotter.DrawDataMCRatio(dataHist[side], pre[side], 1. ); //, true, true, "TL");// false , NULL, NULL, false, true);
        std::string label4;
        label4 = side+" ratio before fit";
        TText t4(.3,.95,label4.c_str());
	    t4.SetTitle(label4.c_str());
	    t4.SetNDC(1);
	    t4.SetTextSize(.03);
	    t4.Draw("same");
        cF.Print(TString(pixheader + "_prefit_compare_ratio.png").Data());

        mnvPlotter.DrawErrorSummary(pre[side]);
        std::string label5;
        label5 = side+" errors before fit";
        TText t5(.3,.95,label5.c_str());
	    t5.SetTitle(label5.c_str());
	    t5.SetNDC(1);
	    t5.SetTextSize(.03);
	    t5.Draw("same");
        cF.Print(TString(pixheader + "_prefit_errors.png").Data());

        mnvPlotter.DrawErrorSummary(tot[side]);
        std::string label6;
        label6 = side+" errors after fit";
        TText t6(.3,.95,label6.c_str());
	    t6.SetTitle(label6.c_str());
	    t6.SetNDC(1);
	    t6.SetTextSize(.03);
	    t6.Draw("same");
        cF.Print(TString(pixheader + "_postfit_errors.png").Data());

        //mnvPlotter.DrawDataMCWithErrorBand(bkgsub[side], fitHists[side][0], 1., "TR");
        //cF.Print(TString(side+"_bkgsub_compare.png").Data());
        
        for (auto addVarName:addVarNames) {
        	addDataHist[side][addVarName]->SetTitle(addDataHist[side][addVarName]->GetName());
		    TString pixheader = TString(pixdirectory + "/" + side + "_" + addVarName+"_");
		    
		    int nbinsX = addDataHist[side][addVarName]->GetXaxis()->GetNbins();
    		double xMin = addDataHist[side][addVarName]->GetXaxis()->GetBinLowEdge(1);
    		double xMax = addDataHist[side][addVarName]->GetXaxis()->GetBinUpEdge(nbinsX);
    		if (addLogX.GetBool(addVarName)) {
    			std::cout << "Setting log minimum for X axis." << std::endl;
				gPad->SetLogx(1);
				addDataHist[side][addVarName]->GetXaxis()->SetRangeUser(logXMinimum,xMax);
				addTot[side][addVarName]->GetXaxis()->SetRangeUser(logXMinimum,xMax);
				addPre[side][addVarName]->GetXaxis()->SetRangeUser(logXMinimum,xMax);
				//addDataHist[side][addVarName]->SetAxisRange(logXMinimum,xMax,"X");
				//addTot[side][addVarName]->SetAxisRange(logXMinimum,xMax,"X");
				//addPre[side][addVarName]->SetAxisRange(logXMinimum,xMax,"X");
			}
			else {
				gPad->SetLogx(0);
				addDataHist[side][addVarName]->GetXaxis()->SetRangeUser(xMin,xMax);
				addTot[side][addVarName]->GetXaxis()->SetRangeUser(xMin,xMax);
				addPre[side][addVarName]->GetXaxis()->SetRangeUser(xMin,xMax);
				//addDataHist[side][addVarName]->SetAxisRange(xMin,xMax,"X");
				//addTot[side][addVarName]->SetAxisRange(xMin,xMax,"X");
				//addPre[side][addVarName]->SetAxisRange(xMin,xMax,"X");
			}
		    
		    std::string addVarUnit = addVarUnits.GetString(addVarName);
        	std::string ytitle;
			if (addVarUnit == "") ytitle = "Counts per bin";
			else ytitle = "Counts per "+addVarUnit;
			TText ty(0.05,0.3,ytitle.c_str());
			ty.SetTitle(ytitle.c_str());
		    ty.SetNDC(1);
		    ty.SetTextSize(.06);
		    ty.SetTextAngle(90);
        	
		    mnvPlotter.DrawDataMCWithErrorBand(addDataHist[side][addVarName], addTot[side][addVarName], 1., "TR");
			t1.Draw("same");
	    	ty.Draw("same");
		    cF.Print(TString(pixheader + "_postfit_compare.png").Data());

		    mnvPlotter.DrawDataMCWithErrorBand(addDataHist[side][addVarName], addPre[side][addVarName], 1., "TR", false , NULL, NULL, false, true);
		    t2.Draw("same");
	    	ty.Draw("same");
		    cF.Print(TString(pixheader + "_prefit_compare.png").Data());

		    mnvPlotter.DrawDataMCRatio(addDataHist[side][addVarName], addTot[side][addVarName], 1. ); //, true, true, "TL");// false , NULL, NULL, false, true);
		    t3.Draw("same");
		    cF.Print(TString(pixheader + "_postfit_compare_ratio.png").Data());

		    mnvPlotter.DrawDataMCRatio(addDataHist[side][addVarName], addPre[side][addVarName], 1. ); //, true, true, "TL");// false , NULL, NULL, false, true);
		    t4.Draw("same");
		    cF.Print(TString(pixheader + "_prefit_compare_ratio.png").Data());

		    mnvPlotter.DrawErrorSummary(addPre[side][addVarName]);
		    t5.Draw("same");
		    cF.Print(TString(pixheader + "_prefit_errors.png").Data());

		    mnvPlotter.DrawErrorSummary(addTot[side][addVarName]);
		    t6.Draw("same");
		    cF.Print(TString(pixheader + "_postfit_errors.png").Data());
        }
    }
    
    TObjArray* combmcin;
    TObjArray* combmcout;
    
    for (auto side:sidebands){
        TString pixheader = TString(pixdirectory + "/" + side + "_" + varName + "_");
        
        int nbinsX = dataHist[side]->GetXaxis()->GetNbins();
    	double xMin = dataHist[side]->GetXaxis()->GetBinLowEdge(1);
    	double xMax = dataHist[side]->GetXaxis()->GetBinUpEdge(nbinsX);
    	if (logX) {
    		std::cout << "Setting log minimum for X axis." << std::endl;
    		gPad->SetLogx(1);
    		dataHist[side]->GetXaxis()->SetRangeUser(logXMinimum,xMax);
    		bkgsub[side]->GetXaxis()->SetRangeUser(logXMinimum,xMax);
    		//dataHist[side]->SetAxisRange(logXMinimum,xMax,"X");
    		//bkgsub[side]->SetAxisRange(logXMinimum,xMax,"X");
    		for (int i = 0; i < categories.size(); i++) {
    			unfitHists[side][i]->GetXaxis()->SetRangeUser(logXMinimum,xMax);
    			fitHists[side][i]->GetXaxis()->SetRangeUser(logXMinimum,xMax);
    			//unfitHists[side][i]->SetAxisRange(logXMinimum,xMax,"X");
    			//fitHists[side][i]->SetAxisRange(logXMinimum,xMax,"X");
    		}
    	}
    	else {
    		gPad->SetLogx(0);
    		dataHist[side]->GetXaxis()->SetRangeUser(xMin,xMax);
    		bkgsub[side]->GetXaxis()->SetRangeUser(xMin,xMax);
    		//dataHist[side]->SetAxisRange(xMin,xMax,"X");
    		//bkgsub[side]->SetAxisRange(xMin,xMax,"X");
    		for (int i = 0; i < categories.size(); i++) {
				unfitHists[side][i]->GetXaxis()->SetRangeUser(xMin,xMax);
				fitHists[side][i]->GetXaxis()->SetRangeUser(xMin,xMax);
				//unfitHists[side][i]->SetAxisRange(xMin,xMax,"X");
				//fitHists[side][i]->SetAxisRange(xMin,xMax,"X");
    		}
    	}

        std::string label;
        label = side+" "+varName;
        combmcin  = Vec2TObjArray(unfitHists[side],categories);
        combmcout = Vec2TObjArray(fitHists[side],categories);
        std::cout << " before call to DrawStack" << std::endl;
        PlotUtils::MnvH1D* data = new PlotUtils::MnvH1D(*(dataHist[side]));
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
        
        label = side+" "+varName + " Before fit";
        TText t(.3,.95,label.c_str());
        t.SetTitle(label.c_str());
        t.SetNDC(1);
        t.SetTextSize(.03);
        if (logPlot) data->SetMinimum(logMinimum);
        mnvPlotter.DrawDataStackedMC(data,combmcin,1.0,"TR");
        t.Draw("same");
        ty.Draw("same");
        cF.Print(TString(pixheader + "_prefit_combined.png").Data());
        
        label = side+" "+varName + " After fit";
        TText t2(.3,.95,label.c_str());
        t2.SetTitle(label.c_str());
        t2.SetNDC(1);
        t2.SetTextSize(.03);
        mnvPlotter.DrawDataStackedMC(data,combmcout,1.0,"TR");
        t2.Draw("same");
        ty.Draw("same");
        cF.Print(TString(pixheader + "_" + fitType + "_postfit_combined.png").Data());
        
        label = side+" "+varName + " Background Subtracted";
        TText t3(.3,.95,label.c_str());
        t3.SetTitle(label.c_str());
        t3.SetNDC(1);
        t3.SetTextSize(.03);
        bkgsub[side]->SetTitle("bkgsub");
        mnvPlotter.DrawDataMCWithErrorBand(bkgsub[side],(MnvH1D*)fitHists[side][0], 1.0, "TR");
        t3.Draw("same");
        ty.Draw("same");
        cF.Print(TString(pixheader + "_" + fitType + "_bkgsub_combined.png").Data());
        
        label = side + "errors after background subtraction";
        TText t4(.2,.95,label.c_str());
        t4.SetTitle(label.c_str());
        t4.SetNDC(1);
        t4.SetTextSize(.03);
        mnvPlotter.DrawErrorSummary(bkgsub[side]);
        std::string label6;
	    t4.Draw("same");
        cF.Print(TString(pixheader + "_bkgsub_errors.png").Data());
        
        for (auto addVarName:addVarNames) {
		    TString pixheader = TString(pixdirectory + "/" + side + "_" + addVarName + "_");
		    
		    int nbinsX = addDataHist[side][addVarName]->GetXaxis()->GetNbins();
    		double xMin = addDataHist[side][addVarName]->GetXaxis()->GetBinLowEdge(1);
    		double xMax = addDataHist[side][addVarName]->GetXaxis()->GetBinUpEdge(nbinsX);
    		if (addLogX.GetBool(addVarName)) {
    			std::cout << "Setting log minimum for X axis." << std::endl;
				gPad->SetLogx(1);
				addDataHist[side][addVarName]->GetXaxis()->SetRangeUser(logXMinimum,xMax);
				addBkgsub[side][addVarName]->GetXaxis()->SetRangeUser(logXMinimum,xMax);
				//addDataHist[side][addVarName]->SetAxisRange(logXMinimum,xMax,"X");
				//addBkgsub[side][addVarName]->SetAxisRange(logXMinimum,xMax,"X");
				for (int i = 0; i < categories.size(); i++) {
					addUnfitHists[side][addVarName][i]->GetXaxis()->SetRangeUser(logXMinimum,xMax);
					addFitHists[side][addVarName][i]->GetXaxis()->SetRangeUser(logXMinimum,xMax);
					//addUnfitHists[side][addVarName][i]->SetAxisRange(logXMinimum,xMax,"X");
					//addFitHists[side][addVarName][i]->SetAxisRange(logXMinimum,xMax,"X");
				}
			}
			else {
				gPad->SetLogx(0);
				addDataHist[side][addVarName]->GetXaxis()->SetRangeUser(xMin,xMax);
				addBkgsub[side][addVarName]->GetXaxis()->SetRangeUser(xMin,xMax);
				//addDataHist[side][addVarName]->SetAxisRange(xMin,xMax,"X");
				//addBkgsub[side][addVarName]->SetAxisRange(xMin,xMax,"X");
				for (int i = 0; i < categories.size(); i++) {
					addUnfitHists[side][addVarName][i]->GetXaxis()->SetRangeUser(xMin,xMax);
					addFitHists[side][addVarName][i]->GetXaxis()->SetRangeUser(xMin,xMax);
					//addUnfitHists[side][addVarName][i]->SetAxisRange(xMin,xMax,"X");
					//addFitHists[side][addVarName][i]->SetAxisRange(xMin,xMax,"X");
				}
			}

		    std::string label;
		    label = side+" "+varName;
		    combmcin  = Vec2TObjArray(addUnfitHists[side][addVarName],categories);
		    combmcout = Vec2TObjArray(addFitHists[side][addVarName],categories);
		    std::cout << " before call to DrawStack" << std::endl;
		    PlotUtils::MnvH1D* data = new PlotUtils::MnvH1D(*(addDataHist[side][addVarName]));
		    data->SetTitle("Data");
		    
			std::string addVarUnit = addVarUnits.GetString(addVarName);
		    std::string ytitle;
		    double ybottom;
        	if (addVarUnit == "") ytitle = "Counts per bin";
        	else ytitle = "Counts per "+addVarUnit;
        	TText ty(0.05,0.3,ytitle.c_str());
        	ty.SetTitle(ytitle.c_str());
		    ty.SetNDC(1);
		    ty.SetTextSize(.06);
		    ty.SetTextAngle(90);    
		    
		    label = side+" "+addVarName + " Before fit";
		    TText t(.3,.95,label.c_str());
		    t.SetTitle(label.c_str());
		    t.SetNDC(1);
		    t.SetTextSize(.03);
		    if (logPlot) data->SetMinimum(logMinimum);
		    
		    mnvPlotter.DrawDataStackedMC(data,combmcin,1.0,"TR");
		    t.Draw("same");
		    ty.Draw("same");
		    cF.Print(TString(pixheader + "_prefit_combined.png").Data());
		    
		    label = side+" "+addVarName + " After fit";
		    TText t2(.3,.95,label.c_str());
		    t2.SetTitle(label.c_str());
		    t2.SetNDC(1);
		    t2.SetTextSize(.03);
		    t2.SetTitle(label.c_str());
		    mnvPlotter.DrawDataStackedMC(data,combmcout,1.0,"TR");
		    t2.Draw("same");
		    ty.Draw("same");
		    cF.Print(TString(pixheader + "_" + fitType + "_postfit_combined.png").Data());
		    
		    label = side+" "+addVarName + " Background Subtracted";
		    TText t3(.3,.95,label.c_str());
		    t3.SetTitle(label.c_str());
		    t3.SetNDC(1);
		    t3.SetTextSize(.03);
		    t3.SetTitle(label.c_str());
		    addBkgsub[side][addVarName]->SetTitle("bkgsub");
		    mnvPlotter.DrawDataMCWithErrorBand(addBkgsub[side][addVarName],(MnvH1D*)addFitHists[side][addVarName][0], 1.0, "TR");
		    t3.Draw("same");
		    ty.Draw("same");
		    cF.Print(TString(pixheader + "_" + fitType + "_bkgsub_combined.png").Data());
		    
		    label = side+" "+addVarName+" errors after background subtraction";
		    TText t4(.2,.95,label.c_str());
		    t4.SetTitle(label.c_str());
		    t4.SetNDC(1);
		    t4.SetTextSize(.03);
		    mnvPlotter.DrawErrorSummary(addBkgsub[side][addVarName]);
		    std::string label6;
			t4.Draw("same");
		    cF.Print(TString(pixheader + "_" + fitType + "_postbkgdsubtraction_errors.png").Data());
        }
    }
    
    //inputFile->Close();
    outputfile->Close();
    cout << "Closing Output File... Does this solve the issue of seg fault." << endl;
   
    
    cout << "HEY YOU DID IT!!!" << endl;
    return 0;
}
