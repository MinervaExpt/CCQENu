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
    
    NuConfig config;
    config.Read(ConfigName);
    config.Print();
    string InputFileName=config.GetString("InputFile");
    string OutputFileName = config.GetString("OutputFile");
    string MCfileName = InputFileName;
    string DATAfileName = InputFileName;
    
    std::vector<std::string> sidebands = config.GetStringVector("Sidebands");
    std::vector<std::string> categories = config.GetStringVector("Categories");
    std::string signal = config.GetString("Signal");
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
    
    
    std::map<std::string, TH1D*> dataHistCV;
    std::map<std::string,std::vector<TH1D*>> fitHistsCV;
    
    std::map<std::string,std::vector<TH1D*>> unfitHistsCV;
    TString name = varName;
    for (auto side:sidebands){
        std::string cat="data";
        std::sprintf(cname,h_template.c_str(),side.c_str(), cat.c_str(),varName.c_str());
        std::cout << " look for " << cname << std::endl;
        MnvH1D* dataHist = (MnvH1D*)dataFile->Get(cname);
        dataHistCV[side] = (TH1D*)dataHist->GetCVHistoWithStatError().Clone();
        
        
        for (auto cat:categories){
            std::sprintf(cname,h_template.c_str(),side.c_str(), cat.c_str(),varName.c_str());
            name = TString(cname);
            MnvH1D* MCHist = (MnvH1D*)dataFile->Get(cname);
            TH1D* NewMCCV = (TH1D*)MCHist->GetCVHistoWithStatError().Clone(TString("new_")+MCHist->GetName());
            TH1D* OldMCCV = (TH1D*)MCHist->GetCVHistoWithStatError().Clone(TString("old_")+MCHist->GetName());
            
            cout << "Testing Fitting for: " << name << endl;
            unfitHistsCV[side].push_back(OldMCCV);
            fitHistsCV[side].push_back(NewMCCV);
        }
    }
    
    
    for (auto side:sidebands){
        int lowBin = 1;
        int hiBin = dataHistCV[side]->GetXaxis()->GetNbins();
        fit::ScaleFactors func1(fitHistsCV[side],unfitHistsCV[side],dataHistCV[side],lowBin,hiBin);
        
        
        auto* mini = new ROOT::Minuit2::Minuit2Minimizer(ROOT::Minuit2::kMigrad);
        
        
        int nextPar = 0;
        for(unsigned int i=0; i < fitHistsCV[side].size(); ++i){
            string var = "par"+to_string(i);
            mini->SetLowerLimitedVariable(nextPar,categories[i],1.0,0.1,0.0);
            nextPar++;
        }
        
        if (nextPar != func1.NDim()){
            cout << "The number of parameters was unexpected for some reason for fitHists1." << endl;
            return 6;
        }
        
        
        
        mini->SetFunction(func1);
        
        
        cout << "Fitting " << side << endl;
        if(!mini->Minimize()){
            cout << "Printing Results." << endl;
            mini->PrintResults();
            printCorrMatrix(*mini, func1.NDim());
            cout << "FIT FAILED" << endl;
            //return 7;
        }
        else{
            cout << "Printing Results." << endl;
            mini->PrintResults();
            printCorrMatrix(*mini, func1.NDim());
            //cout << mini->X() << endl;
            //cout << mini->Errors() << endl;
            cout << "FIT SUCCEEDED" << endl;
        }
        const double* scaleResults = mini->X();
        for (int i = 0; i < fitHistsCV[side].size(); i++){
            fitHistsCV[side][i]->Scale(scaleResults[i]);
        }
        
    }
    // now try a combined fit
    std::vector<std::vector<TH1D*>> combFitHistsCV;
    std::vector<std::vector<TH1D*>> combUnfitHistsCV;
    std::vector<TH1D*> combDataHistCV;
    
    
    /// put the combo into the list of sidebands just for fun.
 

     
    
    
    TFile* outputfile = TFile::Open(OutputFileName.c_str(),"RECREATE");
    for (auto side:sidebands){
        outputfile->cd();
        dataHistCV[side]->Write();
        TH1F* tot = (TH1F*)dataHistCV[side]->Clone(TString("AfterFit_"+side));
        tot->Reset();
        for (auto h:fitHistsCV[side]){
            h->Write();
            tot->Add(tot,h,1.,1.);
        }
        tot->Write();
        TH1F* pre = (TH1F*) dataHistCV[side]->Clone(TString("PreFit_"+side));
        pre->Reset();
        for (auto h:unfitHistsCV[side]){
            h->Write();
            pre->Add(pre,h,1.,1.);
        }
        pre->Write();
        
    }
    PlotUtils::MnvPlotter mnvPlotter(PlotUtils::kCCQEAntiNuStyle);
    TCanvas cF("fit","fit");
    std::map<std::string, TObjArray*> newmcin;
    std::map<std::string, TObjArray*> newmcout;
    for (auto side:sidebands){
        
        newmcin[side] = Vec2TObjArray(unfitHistsCV[side],categories);
        newmcout[side] = Vec2TObjArray(fitHistsCV[side],categories);
        std::cout << " before call to DrawStack" << std::endl;
        
        TH1D test = ((MnvH1D*)newmcin[side]->At(0))->GetCVHistoWithError();
        
        //test.Print();
        MnvH1D* newdata = new MnvH1D(*(dataHistCV[side]));
        newdata->SetTitle("Data");
        mnvPlotter.DrawDataStackedMC(newdata,newmcin[side],1.0,"TR");
        cF.Print(TString(side+"_prefit.png").Data());
        mnvPlotter.DrawDataStackedMC(newdata,newmcout[side],1.0,"TR");
        cF.Print(TString(side+"_postfit.png").Data());
    }
    
     
    // same for combined fit results
    
    // make a common list for all histos
    
    std::cout << "Start combined fit " << std::endl;
    for (int i = 0 ; i < sidebands.size(); i++){
        std::string side = sidebands[i];
        if (side == signal) continue;
        combDataHistCV.push_back(dataHistCV[side]);
        combUnfitHistsCV.push_back(unfitHistsCV[side]);
        combFitHistsCV.push_back(fitHistsCV[side]);
    }
    
    std::cout << "Have made the arrays " << std::endl;
    int lowBin = 1;
    int hiBin = dataHistCV["QElike"]->GetXaxis()->GetNbins();
    std::cout << "Have made the arrays " << std::endl;
  
    fit::MultiScaleFactors func2(combFitHistsCV,combUnfitHistsCV,combDataHistCV,lowBin,hiBin);
    
    std::cout << "Have made the fitter " << std::endl;
    
    auto* mini2 = new ROOT::Minuit2::Minuit2Minimizer(ROOT::Minuit2::kMigrad);
    
    std::cout << " now set up another set of parameters" << std::endl;
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
    // put the signal back in
    
    combDataHistCV.push_back(dataHistCV[signal]);
    combUnfitHistsCV.push_back(unfitHistsCV[signal]);
    combFitHistsCV.push_back(fitHistsCV[signal]);
    
    
    
    const double* combScaleResults = mini2->X();
    for (int side = 0 ; side < sidebands.size(); side++){
        for (int i = 0; i < categories.size(); i++){
            combFitHistsCV[side][i] = (TH1D*)combUnfitHistsCV[side][i]->Clone();
            combFitHistsCV[side][i]->Scale(combScaleResults[i]);
            combFitHistsCV[side][i]->Print();
        }
    }
    
    std::cout << " Try to write it out " << std::endl;
    
    outputfile->cd();
    for (int side = 0 ; side < sidebands.size(); side++){
        combDataHistCV[side]->Print();
        combDataHistCV[side]->Write();
    
        TH1F* tot = (TH1F*)combDataHistCV[side]->Clone(TString("AfterFit_"+sidebands[side]));
        tot->Reset();
        for (int i = 0; i < categories.size(); i++){
            combFitHistsCV[side][i]->Write();
            tot->Add(tot,combFitHistsCV[side][i],1.,1.);
        }
        tot->Print();
        tot->Write();
    }
    std::cout << "wrote the results " << std::endl;
    
    for (int side = 0 ; side < sidebands.size(); side++){
        TH1F* pre = (TH1F*) combDataHistCV[side]->Clone(TString("PreFit_"+sidebands[side]));
        pre->Reset();
        for (int i = 0; i < categories.size(); i++){
            combUnfitHistsCV[side][i]->Write();
            pre->Add(pre,combUnfitHistsCV[side][i],1.,1.);
        }
        pre->Print();
        pre->Write();
        
    }
    std::cout << "wrote the inputs " << std::endl;
    //PlotUtils::MnvPlotter mnvPlotter(PlotUtils::kCCQEAntiNuStyle);
    //TCanvas cF("fit","fit");
    TObjArray* combmcin;
    TObjArray* combmcout;
    for (int side = 0 ; side < sidebands.size(); side++){
        
        combmcin  = Vec2TObjArray(combUnfitHistsCV[side],categories);
        std::cout << "got an array back " << std::endl;
        combmcout = Vec2TObjArray(combFitHistsCV[side],categories);
        std::cout << " before call to DrawStack" << std::endl;
        
        TH1D test = ((MnvH1D*)combmcin->At(0))->GetCVHistoWithError();
        
        //test.Print();
        MnvH1D* data = new MnvH1D(*(combDataHistCV[side]));
        data->SetTitle("Data");
        mnvPlotter.DrawDataStackedMC(data,combmcin,1.0,"TR");
        cF.Print(TString(sidebands[side]+"_prefit_combined.png").Data());
        mnvPlotter.DrawDataStackedMC(data,combmcout,1.0,"TR");
        cF.Print(TString(sidebands[side]+"_postfit_combined.png").Data());
    }
    
    
    outputfile->Close();
    cout << "Closing Files... Does this solve the issue of seg fault." << endl;
   
    dataFile->Close();

    
    cout << "HEY YOU DID IT!!!" << endl;
    return 0;
}
