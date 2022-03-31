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

//PlotUtils includes??? Trying anything at this point...
#include "PlotUtils/MnvH1D.h"
#include "PlotUtils/MnvPlotter.h"
#include "utils/NuConfig.h"


using namespace std;
using namespace PlotUtils;


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
    
    NuConfig config;
    config.Read(ConfigName);
    config.Print();
    string InputFileName=config.GetString("InputFile");
    string OutputFileName = config.GetString("OutputFile");
    string MCfileName = InputFileName;
    string DATAfileName = InputFileName;
    
    std::vector<std::string> sidebands = config.GetStringVector("Sidebands");
    std::vector<std::string> categories = config.GetStringVector("Categories");
    std::string varName = config.GetString("Variable");
    
    /*
     int lowBin1 = 6;
     int hiBin1 = 25;
     */
    
    //int lowBin = 26;
    //int hiBin = 50;
    
    string rootExt = ".root";
    string slash = "/";
    string token;
    string fileNameStub = MCfileName;
    size_t pos=0;
    
    //cout << sigNameStub << endl;
    while ((pos = fileNameStub.find(slash)) != string::npos){
        //cout << sigNameStub << endl;
        token = fileNameStub.substr(0, pos);
        //cout << token << endl;
        fileNameStub.erase(0, pos+slash.length());
    }
    //cout << sigNameStub << endl;
    if ((pos=fileNameStub.find(rootExt)) == string::npos){
        cout << "MC Input need be .root file." << endl;
        return 4;
    }
    
    cout << "Input MC file name parsed to: " << fileNameStub << endl;
    
    rootExt = ".root";
    slash = "/";
    token = "";
    fileNameStub = DATAfileName;
    pos=0;
    
    //cout << sigNameStub << endl;
    while ((pos = fileNameStub.find(slash)) != string::npos){
        //cout << sigNameStub << endl;
        token = fileNameStub.substr(0, pos);
        //cout << token << endl;
        fileNameStub.erase(0, pos+slash.length());
    }
    //cout << sigNameStub << endl;
    if ((pos=fileNameStub.find(rootExt)) == string::npos){
        cout << "DATA Input need be .root file." << endl;
        return 5;
    }
    
    cout << "Input Data file name parsed to: " << fileNameStub << endl;
    
    //TFile* mcFile = new TFile(MCfileName.c_str(),"READ");
    TFile* dataFile = new TFile(DATAfileName.c_str(),"READ");
    
    std::vector<TString> tags = {""};
    TH1F* pot_summary = (TH1F*) dataFile->Get("POT_summary");
    std:vector<double > potinfo(2);
    potinfo[0]=pot_summary->GetBinContent(1);
    potinfo[1]=pot_summary->GetBinContent(2);
    TParameter<double>* mcPOT = (TParameter<double>*) &potinfo[1];
    TParameter<double>* dataPOT = (TParameter<double>*) &potinfo[0];
    std::cout << " dataPOT "<< potinfo[0] << " mcPOT " << potinfo[1] << std::endl;
    
    double POTscale = dataPOT->GetVal()/mcPOT->GetVal();
    cout << "POT scale factor: " << POTscale << endl;
    
    std::string h_template = "h___%s___%s___%s___reconstructed";
    char cname[1000];
    
    
    std::map<std::string, TH1D*> dataHistCV1;
    std::map<std::string,std::vector<TH1D*>> fitHistsCV1;
    std::map<std::string,std::vector<TH1D*>> unfitHistsCV1;
    TString name = varName;
    for (auto side:sidebands){
        std::string cat="data";
        std::sprintf(cname,h_template.c_str(),side.c_str(), cat.c_str(),varName.c_str());
        std::cout << " look for " << cname << std::endl;
        MnvH1D* dataHist = (MnvH1D*)dataFile->Get(cname);
        dataHistCV1[side] = (TH1D*)dataHist->GetCVHistoWithStatError().Clone();
        
        
        for (auto cat:categories){
            std::sprintf(cname,h_template.c_str(),side.c_str(), cat.c_str(),varName.c_str());
            name = TString(cname);
            MnvH1D* MCHist = (MnvH1D*)dataFile->Get(cname);
            TH1D* NewMCCV1 = (TH1D*)MCHist->GetCVHistoWithStatError().Clone(TString("new_")+MCHist->GetName());
            TH1D* OldMCCV1 = (TH1D*)MCHist->GetCVHistoWithStatError().Clone(TString("old_")+MCHist->GetName());
            
            cout << "Testing Fitting for: " << name << endl;
            unfitHistsCV1[side].push_back(NewMCCV1);
            fitHistsCV1[side].push_back(OldMCCV1);
        }
    }
    
    TFile* outputfile = TFile::Open(OutputFileName.c_str(),"RECREATE");
    for (auto side:sidebands){
        int lowBin = 1;
        int hiBin = dataHistCV1[side]->GetXaxis()->GetNbins();
        fit::ScaleFactors func1(fitHistsCV1[side],unfitHistsCV1[side],dataHistCV1[side],lowBin,hiBin);
        
        
        auto* mini1 = new ROOT::Minuit2::Minuit2Minimizer(ROOT::Minuit2::kMigrad);
        
        
        int nextPar = 0;
        for(unsigned int i=0; i < fitHistsCV1[side].size(); ++i){
            string var = "par"+to_string(i);
            mini1->SetLowerLimitedVariable(nextPar,categories[i],1.0,0.1,0.0);
            nextPar++;
        }
        
        if (nextPar != func1.NDim()){
            cout << "The number of parameters was unexpected for some reason for fitHists1." << endl;
            return 6;
        }
        
        
        
        mini1->SetFunction(func1);
        
        
        cout << "Fitting " << side << endl;
        if(!mini1->Minimize()){
            cout << "Printing Results." << endl;
            mini1->PrintResults();
            printCorrMatrix(*mini1, func1.NDim());
            cout << "FIT FAILED" << endl;
            //return 7;
        }
        else{
            cout << "Printing Results." << endl;
            mini1->PrintResults();
            printCorrMatrix(*mini1, func1.NDim());
            //cout << mini->X() << endl;
            //cout << mini->Errors() << endl;
            cout << "FIT SUCCEEDED" << endl;
        }
        outputfile->cd();
        dataHistCV1[side]->Write();
        TH1F* tot = (TH1F*)dataHistCV1[side]->Clone(TString("AfterFit_"+side));
        tot->Reset();
        for (auto h:fitHistsCV1[side]){
            h->Write();
            tot->Add(tot,h,1.,1.);
        }
        tot->Write();
        TH1F* pre = (TH1F*) dataHistCV1[side]->Clone(TString("PreFit_"+side));
        pre->Reset();
        for (auto h:unfitHistsCV1[side]){
            h->Write();
            pre->Add(pre,h,1.,1.);
        }
        pre->Write();
        
    }
    outputfile->Close();
    cout << "Closing Files... Does this solve the issue of seg fault." << endl;
   
    dataFile->Close();
    
    cout << "HEY YOU DID IT!!!" << endl;
    return 0;
}
