// File: MnvFitDriver.cxx
// Info: This script is intended to fit for scale factors (and scale factors only) in whatever distribution.
//
// Usage: MnvFitDriver json file.
//
// IGNORE FOR THE TIME BEING <outdir> <do fits in bins of muon momentum (only 0 means no)> optional: <lowFitBinNum> <hiFitBinNum> TODO: Save the information beyond just printing it out
//
// Author: David Last dlast@sas.upenn.edu/lastd44@gmail.com
//  reconfigured to use json configuration - Schellman

// C++ includes
#include <stdlib.h>
#include <sys/stat.h>
#include <time.h>

#include <algorithm>
#include <bitset>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <numeric>
#include <sstream>
#include <string>
#include <unordered_map>
#include <vector>

// ROOT includes
#include "Math/Factory.h"
#include "Math/IFunction.h"
#include "Math/Minimizer.h"
#include "Minuit2/Minuit2Minimizer.h"
#include "MnvH1D.h"
#include "TCanvas.h"
#include "TColor.h"
#include "TDirectory.h"
#include "TFile.h"
#include "TFractionFitter.h"
#include "TH1F.h"
#include "TH2F.h"
#include "THStack.h"
#include "TInterpreter.h"
#include "TKey.h"
#include "TLegend.h"
#include "TLorentzVector.h"
#include "TMath.h"
#include "TMinuitMinimizer.h"
#include "TPad.h"
#include "TParameter.h"
#include "TROOT.h"
#include "TString.h"
#include "TStyle.h"
#include "TSystemDirectory.h"
#include "TText.h"
#include "TTree.h"
#include "TVector3.h"

// Analysis includes
#include "fits/MultiScaleFactors.h"
#include "fits/ScaleFactors.h"

// PlotUtils includes??? Trying anything at this point...
#include "PlotUtils/MnvH1D.h"
#include "PlotUtils/MnvPlotter.h"
#include "fits/DoTheFit.h"
#include "utils/NuConfig.h"

using namespace std;
using namespace PlotUtils;

// convert the vector of hists into something MnvPlotter wants

TObjArray* Vec2TObjArray(std::vector<MnvH1D*> hists, std::vector<std::string> names) {
    TObjArray* newArray = new TObjArray();
    newArray->SetOwner(kTRUE);
    // std::cout << " try to make an ObjArray" << hists.size() << std::endl;
    int i = 0;
    if (hists.size() != names.size()) {
        std::cout << " problem with objec array names " << std::endl;
    }
    for (int i = 0; i != hists.size(); i++) {
        hists[i]->SetTitle(names[i].c_str());

        newArray->Add(hists[i]);
    }
    return newArray;
}

// Borrowed Directly from Andrew.
void printCorrMatrix(const ROOT::Math::Minimizer& minim, const int nPars) {
    std::vector<double> covMatrix(nPars * nPars, 0);
    minim.GetCovMatrix(covMatrix.data());
    const double* errors = minim.Errors();

    for (int xPar = 0; xPar < nPars; ++xPar) {
        std::cout << "[";
        for (int yPar = 0; yPar < nPars - 1; ++yPar) {
            std::cout << std::fixed << std::setprecision(2) << std::setw(5) << covMatrix[xPar * nPars + yPar] / errors[xPar] / errors[yPar] << ", ";
        }
        std::cout << std::fixed << std::setprecision(2) << std::setw(5) << covMatrix[xPar * nPars + nPars - 1] / errors[xPar] / errors[nPars - 1] << "]\n";
    }
}
// direct from Rene Brun and the tutorials
void CopyDir(TDirectory* source, TDirectory* adir) {
    // copy all objects and subdirs of directory source as a subdir of the current directory
    source->ls();
    adir->cd();
    // loop on all entries of this directory
    TKey* key;
    TIter nextkey(source->GetListOfKeys());

    while ((key = (TKey*)nextkey())) {
        const char* classname = key->GetClassName();
        TClass* cl = gROOT->GetClass(classname);
        if (!cl) continue;
        if (cl->InheritsFrom(TDirectory::Class())) {
            source->cd(key->GetName());
            TDirectory* subdir = gDirectory;
            adir->cd();
            CopyDir(subdir, adir);
            adir->cd();
        } else if (cl->InheritsFrom(TTree::Class())) {
            TTree* T = (TTree*)source->Get(key->GetName());
            adir->cd();
            TTree* newT = T->CloneTree(-1, "fast");
            newT->Write();
        } else {
            source->cd();
            TObject* obj = key->ReadObj();
            adir->cd();
            obj->Write();
            // delete obj;
        }
    }
    // adir->SaveSelf(kTRUE);
    //   std::cout <<  adir->GetName()<< std::endl;
}

int main(int argc, char* argv[]) {
    gStyle->SetOptStat(0);

    //  #ifndef NCINTEX
    //  ROOT::Cintex::Cintex::Enable();
    //  #endif
    string ConfigName = "test.json";
    // Pass an input file name to this script now
    if (argc == 1) {
        std::cout << "using default" << ConfigName << std::endl;
    }
    if (argc == 2) {
        ConfigName = argv[1];
        std::cout << "using" << ConfigName << std::endl;
    }

    // read in the configuration
    NuConfig config;
    config.Read(ConfigName);
    config.Print();
    std::string inputFileName = config.GetString("InputFile");
    std::string outputDir = config.GetString("OutputDir");
    std::string outputFileName = config.GetString("OutputFile");
    outputFileName=(outputDir+"/"+outputFileName).c_str();
    bool logPlot = config.GetBool("LogPlot");
    double logMinimum = config.GetDouble("LogMinimum");
    std::vector<std::string> sidebands = config.GetStringVector("Sidebands");
    std::vector<std::string> categories = config.GetStringVector("Categories");

    // use this to exclude or include sidebands in the global fit
    std::vector<std::string> include = config.GetStringVector("IncludeInFit");
    std::vector<std::string> backgrounds = config.GetStringVector("Backgrounds");
    std::map<const std::string, bool> includeInFit;
    for (auto s : sidebands) {
        includeInFit[s] = false;
        for (auto i : include) {
            if (s == i) includeInFit[s] = true;
        }
    }
    std::string varName = config.GetString("Variable");
    std::string fitType = config.GetString("FitType");
    std::string h_template = config.GetString("Template");
    std::string f_template = config.GetString("FitTemplate");

    // read in the data and parse it

    TFile* inputFile = TFile::Open(inputFileName.c_str(), "READ");
    TFile* outputfile = TFile::Open(outputFileName.c_str(), "RECREATE");
    // loop on all entries of this directory

    outputfile->cd();
    CopyDir(inputFile, outputfile);

    // std::vector<TString> tags = {""};
    TH1F* pot_summary = (TH1F*)inputFile->Get("POT_summary");
    std::vector<double> potinfo(2);
    potinfo[0] = pot_summary->GetBinContent(1);
    potinfo[1] = pot_summary->GetBinContent(3);  // this includes any prescale
    pot_summary->Print("ALL");
    TParameter<double>* mcPOT = (TParameter<double>*)&potinfo[1];
    TParameter<double>* dataPOT = (TParameter<double>*)&potinfo[0];
    std::cout << " dataPOT " << potinfo[0] << " mcPOT " << potinfo[1] << std::endl;

    // double POTscale = dataPOT->GetVal()/mcPOT->GetVal();
    double POTscale = potinfo[0] / potinfo[1];

    std::cout << "POT scale factor: " << POTscale << std::endl;

    // make and fill maps that contain pointers to the histograms you want to fit  uses CCQEMAT template

    // std::string h_template = "h___%s___%s___%s___reconstructed";
    char cname[1000];
    char fname[1000];
    std::map<const std::string, PlotUtils::MnvH1D*> dataHist;
    std::map<const std::string, std::vector<PlotUtils::MnvH1D*>> fitHists;
    std::map<const std::string, std::vector<PlotUtils::MnvH1D*>> unfitHists;
    TString name = varName;
    for (auto const side : sidebands) {
        std::string cat = "data";
        std::sprintf(cname, h_template.c_str(), side.c_str(), cat.c_str(), varName.c_str());
        std::sprintf(fname, f_template.c_str(), side.c_str(), cat.c_str(), varName.c_str());
        std::cout << " look for " << cname << std::endl;
        dataHist[side] = (PlotUtils::MnvH1D*)inputFile->Get(cname);
        // dataHist[side]->SetNormBinWidth(1.0);
        // dataHist[sidename] = (TH1D*)dataHist->GetCVHistoWithStatError().Clone();
        for (auto cat : categories) {
            std::sprintf(cname, h_template.c_str(), side.c_str(), cat.c_str(), varName.c_str());
            std::sprintf(fname, f_template.c_str(), side.c_str(), cat.c_str(), varName.c_str());
            name = TString(cname);
            std::cout << " look for " << cname << std::endl;
            MnvH1D* newhist = (PlotUtils::MnvH1D*)inputFile->Get(cname);
            if (!newhist) {
                std::cout << " no " << cname << std::endl;
            }
            newhist->Print();
            newhist->Scale(POTscale);
            newhist->Print();
            unfitHists[side].push_back(newhist);
            fitHists[side].push_back((PlotUtils::MnvH1D*)newhist->Clone(TString(fname)));
        }
        /*for (int i = 0; i < categories.size(); i++){
            unfitHists[side][i]->SetNormBinWidth(1.0);
            fitHists[side][i]->SetNormBinWidth(1.0);
        }*/
    }
    // inputFile->Close(); // this didn't work

    std::cout << "have extracted the inputs" << std::endl;

    // now have made a common map for all histograms
    bool binbybin = false;
    int lowBin = 1;
    int hiBin = dataHist[include[0]]->GetXaxis()->GetNbins();
    fit::fit_type type;
    type = fit::kFastChi2;
    if (fitType == "FastChi2") type = fit::kFastChi2;
    if (fitType == "SlowChi2") type = fit::kSlowChi2;
    if (fitType == "ML") type = fit::kML;
    std::cout << " Try to write it out " << std::endl;

    outputfile->cd();
    int ret = fit::DoTheFit(fitHists, unfitHists, dataHist, includeInFit, categories, type, lowBin, hiBin, binbybin, outputDir);

    // set up for plots

    PlotUtils::MnvPlotter mnvPlotter(PlotUtils::kCCQEAntiNuStyle);
    mnvPlotter.error_color_map["FitVariations"] = kBlue + 2;
    mnvPlotter.draw_normalized_to_bin_width = false;
    TCanvas cF("fit", "fit");
    if (logPlot) gPad->SetLogy(1);
    std::map<const std::string, MnvH1D*> tot;
    std::map<const std::string, MnvH1D*> pre;
    std::map<const std::string, MnvH1D*> bkg;
    std::map<const std::string, MnvH1D*> sig;
    std::map<const std::string, MnvH1D*> bkgsub;

    for (auto side : sidebands) {
        dataHist[side]->Print();

        // dataHist[side]->Write();

        for (int i = 0; i < categories.size(); i++) {
            fitHists[side][i]->Write();
            std::sprintf(fname, f_template.c_str(), side.c_str(), "all", varName.c_str());
            if (i == 0) {
                tot[side] = (MnvH1D*)fitHists[side][i]->Clone(TString(fname));
            } else {
                tot[side]->Add(fitHists[side][i]);
            }
        }
        tot[side]->MnvH1DToCSV(tot[side]->GetName(), outputDir + "/csv/", 1., false);
        tot[side]->Print();
        tot[side]->Write();
    }
    std::cout << "wrote the results " << std::endl;

    for (auto side : sidebands) {
        for (int i = 0; i < categories.size(); i++) {
            std::sprintf(cname, h_template.c_str(), side.c_str(), "all", varName.c_str());
            if (i == 0) {
                pre[side] = (MnvH1D*)unfitHists[side][i]->Clone(TString(cname));
            } else {
                pre[side]->Add(unfitHists[side][i]);
            }
        }
        pre[side]->Print();
        pre[side]->Write();
        pre[side]->MnvH1DToCSV(pre[side]->GetName(), outputDir + "/csv/", 1., false);
    }
    // this loops over, finds the categories that are in the backgrounds and sums those to get a background
    // uses this whole counter thing to avoid having to figure out how to do string searches in a list in C++

    for (auto side : sidebands) {
        int count = 0;
        for (int i = 0; i < categories.size(); i++) {
            for (int j = 0; j < backgrounds.size(); j++) {
                // std::cout << "match " << categories[i] << " " << backgrounds[j] << " " << count << std::endl;
                if (categories[i] == backgrounds[j]) {
                    std::sprintf(fname, f_template.c_str(), side.c_str(), "bkg", varName.c_str());
                    if (count == 0) {
                        bkg[side] = (MnvH1D*)fitHists[side][i]->Clone(TString(fname));
                        count += 1;
                    } else {
                        bkg[side]->Add(fitHists[side][i]);
                    }
                }
            }
            if (count > 0) {
                bkg[side]->Print();
                bkg[side]->Write();
                bkg[side]->MnvH1DToCSV(bkg[side]->GetName(), outputDir + "/csv/", 1., false);
            }
        }
    }
    for (auto side : sidebands) {
        std::sprintf(fname, f_template.c_str(), side.c_str(), "bkgsub", varName.c_str());
        bkgsub[side] = (MnvH1D*)dataHist[side]->Clone(fname);
        bkgsub[side]->AddMissingErrorBandsAndFillWithCV(*(fitHists[side][0]));
        bkgsub[side]->Add(bkg[side], -1);
        bkgsub[side]->Write();
        dataHist[side]->MnvH1DToCSV(dataHist[side]->GetName(),  outputDir + "/csv/", 1., false);
        bkgsub[side]->MnvH1DToCSV(bkgsub[side]->GetName(),  outputDir + "/csv/", 1., false);
    }
    std::cout << "wrote the inputs and outputs " << std::endl;

    for (auto side : sidebands) {
        // dataHist[side]->Print("ALL");
        dataHist[side]->Scale(1., "width");
        // dataHist[side]->Print("ALL");
        tot[side]->Scale(1., "width");
        pre[side]->Scale(1., "width");
        bkg[side]->Scale(1., "width");
        bkgsub[side]->Scale(1., "width");
        for (int i = 0; i < categories.size(); i++) {
            unfitHists[side][i]->Scale(1., "width");
            fitHists[side][i]->Scale(1., "width");
        }
    }

    for (auto side : sidebands) {
        mnvPlotter.DrawDataMCWithErrorBand(dataHist[side], tot[side], 1., "TR");
        cF.Print(TString(outputDir + "/png/" + side + "_postfit_compare.png").Data());

        mnvPlotter.DrawDataMCWithErrorBand(dataHist[side], pre[side], 1., "TR");
        cF.Print(TString(outputDir + "/png/" + side + "_prefit_compare.png").Data());

        mnvPlotter.DrawDataMCWithErrorBand(bkgsub[side], fitHists[side][0], 1., "TR");
        cF.Print(TString(outputDir + "/png/" + side + "_bkgsub_compare.png").Data());
    }

    TObjArray* combmcin;
    TObjArray* combmcout;

    for (auto side : sidebands) {
        std::string label;
        label = side + " " + varName;
        combmcin = Vec2TObjArray(unfitHists[side], categories);
        combmcout = Vec2TObjArray(fitHists[side], categories);
        std::cout << " before call to DrawStack" << std::endl;
        PlotUtils::MnvH1D* data = new PlotUtils::MnvH1D(*(dataHist[side]));
        data->SetTitle("Data");
        label = side + " " + varName + " Before fit";
        TText t(.3, .95, label.c_str());
        t.SetTitle(label.c_str());
        t.SetNDC(1);
        t.SetTextSize(.03);

        mnvPlotter.DrawDataStackedMC(data, combmcin, 1.0, "TR");
        t.Draw("same");
        cF.Print(TString(outputDir + "/png/" + side + "_prefit_combined.png").Data());
        label = side + " " + varName + " After fit";
        TText t2(.3, .95, label.c_str());
        t2.SetTitle(label.c_str());
        t2.SetNDC(1);
        t2.SetTextSize(.03);
        t2.SetTitle(label.c_str());
        mnvPlotter.DrawDataStackedMC(data, combmcout, 1.0, "TR");
        cF.Print(TString(outputDir + "/png/" + side + "_" + fitType + "_postfit_combined.png").Data());
        label = side + " " + varName + "Background Subtracted";

        t2.SetTitle(label.c_str());
        t2.SetNDC(1);
        t2.SetTextSize(.03);
        t2.SetTitle(label.c_str());
        bkgsub[side]->SetTitle("bkgsub");
        mnvPlotter.DrawDataStackedMC(bkgsub[side], combmcout, 1.0, "TR");
        cF.Print(TString(outputDir + "/png/" + side + "_" + fitType + "_bkgsub_combined.png").Data());
    }
    std::cout << " > after drawstack loop, before closign files" << std::endl;
    inputFile->Close();
    outputfile->Close();
    std::cout << "Closing Output File... Does this solve the issue of seg fault." << std::endl;

    std::cout << "HEY YOU DID IT!!!" << std::endl;
    return 0;
}
