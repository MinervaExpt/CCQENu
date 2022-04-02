//File: TMinFitting.cxx
//Info: This script is intended to fit for scale factors (and scale factors only) in whatever distribution.
//
//Usage: TMinFitting <mc_file> <data_file>
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

//ROOT includes
#include "TInterpreter.h"
#include "TROOT.h"
#include "TH1F.h"
#include "TH2F.h"
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


using namespace std;
using namespace PlotUtils;

// convert the vector of hists into something MnvPlotter wants

TObjArray* Vec2TObjArray(std::vector<TH1D*> hists, std::vector<std::string> names){
    TObjArray* newArray = new TObjArray();
    newArray->SetOwner(kTRUE);
    std::cout << " try to make an ObjArray" << hists.size() << std::endl;
    int i = 0;
    if (hists.size() != names.size()){
        std::cout << " problem with objec array names " << std::endl;
    }
    for (int i = 0 ; i != hists.size(); i++){
        MnvH1D* m = new MnvH1D(*hists[i]);
        
        m->SetTitle(names[i].c_str());
        m->Print();
        newArray->Add(m);
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
    string inputFileName=config.GetString("InputFile");
    string outputFileName = config.GetString("OutputFile");
    std::vector<std::string> sidebands = config.GetStringVector("Sidebands");
    std::vector<std::string> categories = config.GetStringVector("Categories");
    
    // use this to exclude or include sidebands in the global fit
    std::vector<std::string> include = config.GetStringVector("IncludeInFit");
    std::map<const std::string, bool> includeInFit;
    for (auto s:sidebands){
        includeInFit[s] = false;
        for (auto i:include){
            if (s == i) includeInFit[s] = true;
        }
    }
    std::string varName = config.GetString("Variable");
 
    
    // read in the data and parse it
  
    TFile* inputFile = new TFile(inputFileName.c_str(),"READ");
    
   // std::vector<TString> tags = {""};
    TH1F* pot_summary = (TH1F*) inputFile->Get("POT_summary");
    std:vector<double > potinfo(2);
    potinfo[0]=pot_summary->GetBinContent(1);
    potinfo[1]=pot_summary->GetBinContent(2);
    TParameter<double>* mcPOT = (TParameter<double>*) &potinfo[1];
    TParameter<double>* dataPOT = (TParameter<double>*) &potinfo[0];
    std::cout << " dataPOT "<< potinfo[0] << " mcPOT " << potinfo[1] << std::endl;
    
    double POTscale = dataPOT->GetVal()/mcPOT->GetVal();
    cout << "POT scale factor: " << POTscale << endl;
    
    // make and fill maps that contain pointers to the histograms you want to fit  uses CCQEMAT template
    
    std::string h_template = "h___%s___%s___%s___reconstructed";
    char cname[1000];
    std::map<const std::string, TH1D*> dataHistCV;
    std::map<const std::string,std::vector<TH1D*>> fitHistsCV;
    std::map<const std::string,std::vector<TH1D*>> unfitHistsCV;
    TString name = varName;
    for (auto side:sidebands){
        std::string cat="data";
        std::sprintf(cname,h_template.c_str(),side.c_str(), cat.c_str(),varName.c_str());
        std::cout << " look for " << cname << std::endl;
        MnvH1D* dataHist = (MnvH1D*)inputFile->Get(cname);
        dataHistCV[side] = (TH1D*)dataHist->GetCVHistoWithStatError().Clone();
        for (auto cat:categories){
            std::sprintf(cname,h_template.c_str(),side.c_str(), cat.c_str(),varName.c_str());
            name = TString(cname);
            MnvH1D* MCHist = (MnvH1D*)inputFile->Get(cname);
            TH1D* NewMCCV = (TH1D*)MCHist->GetCVHistoWithStatError().Clone(TString("new_")+MCHist->GetName());
            TH1D* OldMCCV = (TH1D*)MCHist->GetCVHistoWithStatError().Clone(TString("old_")+MCHist->GetName());
            
            cout << "Testing Fitting for: " << name << endl;
            unfitHistsCV[side].push_back(OldMCCV);
            fitHistsCV[side].push_back(NewMCCV);
        }
    }

    
    // now have made a common map for all histograms
    
    int lowBin = 1;
    int hiBin = dataHistCV[include[0]]->GetXaxis()->GetNbins();
  
    fit::MultiScaleFactors func2(unfitHistsCV,dataHistCV,includeInFit,lowBin,hiBin);
    
    std::cout << "Have made the fitter " << std::endl;
    
    auto* mini2 = new ROOT::Minuit2::Minuit2Minimizer(ROOT::Minuit2::kMigrad);
    
    std::cout << " now set up parameters" << func2.NDim() <<std::endl;
    
    int nextPar = 0;
    for(unsigned int i=0; i < categories.size(); ++i){
        mini2->SetLowerLimitedVariable(nextPar,categories[i],1.0,0.1,0.0);
        nextPar++;
    }
    
    if (nextPar != func2.NDim()){
        cout << "The number of parameters was unexpected for some reason for fitHists1." << endl;
        return 6;
    }
    
    std::cout << "Have set up the parameters " << std::endl;
    
    mini2->SetFunction(func2);
    
    mini2->PrintResults();
    
    cout << "Fitting " << "combination" << endl;
    if(!mini2->Minimize()){
        cout << "Printing Results." << endl;
        mini2->PrintResults();
        printCorrMatrix(*mini2, func2.NDim());
        cout << "FIT FAILED" << endl;
        //return 7;
    }
    else{
        cout << "Printing Results." << endl;
        mini2->PrintResults();
        printCorrMatrix(*mini2, func2.NDim());
        //cout << mini2->X() << endl;
        //cout << mini2->Errors() << endl;
        cout << "FIT SUCCEEDED" << endl;
    }
    
    // have done the fit, now rescale all histograms by the appropriate scale factors
    
    const double* combScaleResults = mini2->X();
    for (auto side:sidebands){
        for (int i = 0; i < categories.size(); i++){
            fitHistsCV[side][i]->Scale(combScaleResults[i]);
            fitHistsCV[side][i]->Print();
        }
    }
    
    std::cout << " Try to write it out " << std::endl;
    TFile* outputfile = TFile::Open(outputFileName.c_str(),"RECREATE");
    outputfile->cd();
    for (auto side:sidebands){
        dataHistCV[side]->Print();
        dataHistCV[side]->Write();
    
        TH1F* tot = (TH1F*)dataHistCV[side]->Clone(TString("AfterFit_"+side));
        tot->Reset();
        for (int i = 0; i < categories.size(); i++){
            fitHistsCV[side][i]->Write();
            tot->Add(tot,fitHistsCV[side][i],1.,1.);
        }
        tot->Print();
        tot->Write();
    }
    std::cout << "wrote the results " << std::endl;
    
    for (auto side:sidebands){
        TH1F* pre = (TH1F*) dataHistCV[side]->Clone(TString("PreFit_"+side));
        pre->Reset();
        for (int i = 0; i < categories.size(); i++){
            unfitHistsCV[side][i]->Write();
            pre->Add(pre,unfitHistsCV[side][i],1.,1.);
        }
        pre->Print();
        pre->Write();
        
    }
    std::cout << "wrote the inputs " << std::endl;
    
    // now make some amusing plots
    
    PlotUtils::MnvPlotter mnvPlotter(PlotUtils::kCCQEAntiNuStyle);
    TCanvas cF("fit","fit");
    TObjArray* combmcin;
    TObjArray* combmcout;
    for (auto side:sidebands){
        combmcin  = Vec2TObjArray(unfitHistsCV[side],categories);
        std::cout << "got an array back " << std::endl;
        combmcout = Vec2TObjArray(fitHistsCV[side],categories);
        std::cout << " before call to DrawStack" << std::endl;
        
        TH1D test = ((MnvH1D*)combmcin->At(0))->GetCVHistoWithError();
        
        //test.Print();
        MnvH1D* data = new MnvH1D(*(dataHistCV[side]));
        data->SetTitle("Data");
        mnvPlotter.DrawDataStackedMC(data,combmcin,1.0,"TR");
        cF.Print(TString(side+"_prefit_combined.png").Data());
        mnvPlotter.DrawDataStackedMC(data,combmcout,1.0,"TR");
        cF.Print(TString(side+"_postfit_combined.png").Data());
    }
    outputfile->Close();
    cout << "Closing Files... Does this solve the issue of seg fault." << endl;
   
    inputFile->Close();

    
    cout << "HEY YOU DID IT!!!" << endl;
    return 0;
}
