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
#include "utils/SyncBands.h"

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
    std::string outputFileNameraw = config.GetString("OutputFile");
    std::string outputFileName = (outputDir + "/" + outputFileNameraw).c_str();
    bool logPlot = config.GetBool("LogPlot");
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
    std::string fitvarName = config.GetString("FitVariable");
    std::string projvarName = config.GetString("ProjectionVariable");
    std::string varName2d = config.GetString("Variable2D");
    std::string fitType = config.GetString("FitType");
    std::string h_template = config.GetString("Template");
    std::string f_template = config.GetString("FitTemplate");

    // read in the data and parse it

    TFile* inputFile = TFile::Open(inputFileName.c_str(), "READ");
    TFile* outputFile = TFile::Open(outputFileName.c_str(), "RECREATE");
    // loop on all entries of this directory

    outputFile->cd();
    CopyDir(inputFile, outputFile);

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

    // TODO: Loop over Q^2QE bins, project recoil in each, run fitter for them


     
    // make and fill maps that contain pointers to the histograms you want to fit  uses CCQEMAT template

    int n_fitbins = 0;
    bool firstdata = true; // dummy hacky way of just grabbing xbins once

    // TODO: Figure out how to make cname and fname work with and h2D
    // std::string h_template = "h___%s___%s___%s___reconstructed";
    char cname[1000];
    char fname[1000];
    std::map<const std::string, PlotUtils::MnvH2D*> dataHist2D;
    std::map<const std::string, std::vector<PlotUtils::MnvH2D*>> fitHists2D;
    std::map<const std::string, std::vector<PlotUtils::MnvH2D*>> unfitHists2D; 
    TString name = varName2d;
    for (auto const side : sidebands) {
        std::string cat = "data";
        std::snprintf(cname, sizeof(cname), h_template.c_str(), side.c_str(), cat.c_str(), varName2d.c_str());  // This is the data hist name
        // std::snprintf(fname, f_template.c_str(), side.c_str(), cat.c_str(), varName.c_str()); // This is the fitted hist name
        std::cout << " look for " << cname << std::endl;
        dataHist2D[side] = (PlotUtils::MnvH2D*)inputFile->Get(cname)->Clone();
        if (firstdata) {
            n_fitbins = dataHist2D[side]->GetXaxis()->GetNbins();
            firstdata=false;
        }
        // dataHist[side]->SetNormBinWidth(1.0);
        // dataHist[sidename] = (TH1D*)dataHist->GetCVHistoWithStatError().Clone();
        for (auto cat : categories) {
            std::snprintf(cname, sizeof(cname), h_template.c_str(), side.c_str(), cat.c_str(), varName2d.c_str()); // unfit hist name
            std::snprintf(fname, sizeof(fname), f_template.c_str(), side.c_str(), cat.c_str(), varName2d.c_str());  // fitted hist name
            name = TString(cname);
            std::cout << " look for " << cname << std::endl;
            MnvH2D* newhist = (PlotUtils::MnvH2D*)inputFile->Get(cname)->Clone();
            if (!newhist) {
                std::cout << " no " << cname << std::endl;
            }
            newhist->Print();
            newhist->Scale(POTscale);
            newhist->Print();
            unfitHists2D[side].push_back(newhist);
            fitHists2D[side].push_back((PlotUtils::MnvH2D*)newhist->Clone(TString(fname)));
        }
        /*for (int i = 0; i < categories.size(); i++){
            unfitHists[side][i]->SetNormBinWidth(1.0);
            fitHists[side][i]->SetNormBinWidth(1.0);
        }*/
    }

    std::vector<std::map<const std::string, PlotUtils::MnvH1D*>> dataHist1D;
    std::vector<std::map<const std::string, std::vector<PlotUtils::MnvH1D*>>> fitHists1D;
    std::vector<std::map<const std::string, std::vector<PlotUtils::MnvH1D*>>> unfitHists1D;
    PlotUtils::MnvH1D* dummy_xproj_hist;
    firstdata = true;

    std::string h1d_template = "h___%s___%s___%s_%02d___reconstructed";
    std::string fh1d_template = "h___%s___%s___%s_%02d___reconstructed_fitted";
    char cname1d[1000];
    char fname1d[1000];
    for (int fitbin = 1; fitbin < n_fitbins + 1; fitbin++) {
        std::map<const std::string, PlotUtils::MnvH1D*> tmp_dataMap1d;
        std::map<const std::string, std::vector<PlotUtils::MnvH1D*>> tmp_fitMap1d;
        std::map<const std::string, std::vector<PlotUtils::MnvH1D*>> tmp_unfitMap1d;
        for (auto const side : sidebands) {
            // std::string dataname1d = ("h___" + side.c_str() + "___data___" + varName.c_str() + "_" + std::to_string(fitbin) + "___reconstructed").c_str();
            // MnvH1D* tmp_data1d = (MnvH1D*)dataHist2D[side]->ProjectionY(dataname1d, fitbin, fitbin, "e");
            std::string cat = "data";
            std::snprintf(cname1d, sizeof(cname1d), h1d_template.c_str(), side.c_str(), cat.c_str(), fitvarName.c_str(), fitbin);  // This is the data hist name
            MnvH1D* tmp_data1d = (MnvH1D*)dataHist2D[side]->ProjectionY(cname1d, fitbin, fitbin, "e");
            if (firstdata) {
                dummy_xproj_hist = (MnvH1D*)dataHist2D[side]->ProjectionX("dummy_xproj", fitbin, fitbin, "e");
                firstdata = false;
            }
            tmp_dataMap1d[side] = tmp_data1d;

            std::vector<MnvH1D*> tmp_unfitcatlist1d;
            std::vector<MnvH1D*> tmp_fitcatlist1d;
            for (int cat = 0; cat < categories.size(); cat++) {
                // std::string fitcatname1d = ("h___" + side.c_str() + "___" + cat.c_str() + "___" + varName.c_str() + "_" + std::to_string(fitbin) + "___reconstructed").c_str();
                // std::string unfitcatname1d = ("h___" + side.c_str() + "___" + cat.c_str() + "___" + varName.c_str() + "_" + std::to_string(fitbin) + "___reconstructed_fitted").c_str();
                // MnvH1D* tmp_unfitcat1d = (MnvH1D*)unfitHists2D[side][cat]->ProjectionY(catname1d, fitbin, fitbin, "e");
                // MnvH1D* tmp_fitcat1d = (MnvH1D*)fitHists2D[side][cat]->ProjectionY(catname1d, fitbin, fitbin, "e");
                std::snprintf(cname1d, sizeof(cname1d), h1d_template.c_str(), side.c_str(), categories[cat].c_str(), fitvarName.c_str(), fitbin);  // This is the data hist name
                std::snprintf(fname1d, sizeof(fname1d), fh1d_template.c_str(), side.c_str(), categories[cat].c_str(), fitvarName.c_str(), fitbin);  // This is the data hist name

                MnvH1D* tmp_unfitcat1d = (MnvH1D*)unfitHists2D[side][cat]->ProjectionY(cname1d, fitbin, fitbin, "e");
                MnvH1D* tmp_fitcat1d = (MnvH1D*)fitHists2D[side][cat]->ProjectionY(fname1d, fitbin, fitbin, "e");
                tmp_unfitcatlist1d.push_back(tmp_unfitcat1d);
                tmp_fitcatlist1d.push_back(tmp_fitcat1d);
            }
            tmp_unfitMap1d[side] = tmp_unfitcatlist1d;
            tmp_fitMap1d[side] = tmp_fitcatlist1d;
        }
        dataHist1D.push_back(tmp_dataMap1d);
        fitHists1D.push_back(tmp_fitMap1d);
        unfitHists1D.push_back(tmp_unfitMap1d);
    }

    std::cout << "have extracted the inputs" << std::endl;
    outputFile->cd();

    std::vector<MnvH1D*> parameters_list;

    // for (auto dataHist : dataHist1D) {
    for (int fitbin = 0; fitbin < n_fitbins; fitbin++) {
        std::map<const std::string, PlotUtils::MnvH1D*> dataHist = dataHist1D[fitbin];
        std::map<const std::string, std::vector<PlotUtils::MnvH1D*>> fitHists = fitHists1D[fitbin];
        std::map<const std::string, std::vector<PlotUtils::MnvH1D*>> unfitHists = unfitHists1D[fitbin];
        
        // now have made a common map for all histograms
        bool binbybin = false;
        int lowBin = 1;
        int hiBin = dataHist[include[0]]->GetXaxis()->GetNbins();  // TODO: how to deal with this
        fit::fit_type type;
        type = fit::kFastChi2;
        if (fitType == "FastChi2") type = fit::kFastChi2;
        if (fitType == "SlowChi2") type = fit::kSlowChi2;
        if (fitType == "ML") type = fit::kML;
        std::cout << " Try to write it out " << std::endl;
        char paramname[1000];
        std::snprintf(paramname, sizeof(paramname), h1d_template.c_str(), "QElike", "fit_paramters", fitvarName.c_str(), fitbin + 1);  // This is the data hist name
        PlotUtils::MnvH1D* parameters = new PlotUtils::MnvH1D(paramname, "fit parameters", categories.size(), 0.0, double(categories.size()));
        int ret = fit::DoTheFit(fitHists, parameters, unfitHists, dataHist, includeInFit, categories, type, lowBin, hiBin, binbybin, outputDir, fitbin + 1);
        parameters_list.push_back(parameters);
        // int ret = fit::DoTheFit(fitHists, unfitHists, dataHist, includeInFit, categories, type, lowBin, hiBin, binbybin, outputDir, fitbin+1);

        // set up for plots

        // PlotUtils::MnvPlotter mnvPlotter(PlotUtils::kCCQEAntiNuStyle);
        // mnvPlotter.draw_normalized_to_bin_width = false;
        // TCanvas cF("fit", "fit");
        // if (logPlot) gPad->SetLogy(1);
        // std::map<const std::string, MnvH1D*> tot;
        // std::map<const std::string, MnvH1D*> pre;
        // std::map<const std::string, MnvH1D*> bkg;
        // std::map<const std::string, MnvH1D*> sig;
        // std::map<const std::string, MnvH1D*> bkgsub;

        // for (auto side : sidebands) {
        //     dataHist[side]->Print();

        //     // dataHist[side]->Write();

        //     for (int i = 0; i < categories.size(); i++) {
        //         fitHists[side][i]->Write();
        //         std::snprintf(fname1d, sizeof(fname1d), fh1d_template.c_str(), side.c_str(), "all", fitvarName.c_str(), fitbin + 1);
        //         if (i == 0) {
        //             tot[side] = (MnvH1D*)fitHists[side][i]->Clone(TString(fname1d));
        //         } else {
        //             tot[side]->Add(fitHists[side][i]);
        //         }
        //     }
        //     tot[side]->MnvH1DToCSV(tot[side]->GetName(), outputDir + "/csv/", 1., false);
        //     tot[side]->Print();
        //     tot[side]->Write();
        // }
        // std::cout << "wrote the results " << std::endl;

        // for (auto side : sidebands) {
        //     for (int i = 0; i < categories.size(); i++) {
        //         std::snprintf(cname1d, sizeof(cname1d), h1d_template.c_str(), side.c_str(), "all", fitvarName.c_str(), fitbin + 1);
        //         if (i == 0) {
        //             pre[side] = (MnvH1D*)unfitHists[side][i]->Clone(TString(cname1d));
        //         } else {
        //             pre[side]->Add(unfitHists[side][i]);
        //         }
        //     }
        //     pre[side]->Print();
        //     pre[side]->Write();
        //     pre[side]->MnvH1DToCSV(pre[side]->GetName(), outputDir + "/csv/", 1., false);
        // }
        // // this loops over, finds the categories that are in the backgrounds and sums those to get a background
        // // uses this whole counter thing to avoid having to figure out how to do string searches in a list in C++

        // for (auto side : sidebands) {
        //     int count = 0;
        //     for (int i = 0; i < categories.size(); i++) {
        //         for (int j = 0; j < backgrounds.size(); j++) {
        //             // std::cout << "match " << categories[i] << " " << backgrounds[j] << " " << count << std::endl;
        //             if (categories[i] == backgrounds[j]) {
        //                 std::snprintf(fname1d, sizeof(fname1d), fh1d_template.c_str(), side.c_str(), "bkg", fitvarName.c_str(), fitbin + 1);
        //                 if (count == 0) {
        //                     bkg[side] = (MnvH1D*)fitHists[side][i]->Clone(TString(fname1d));
        //                     count += 1;
        //                 } else {
        //                     bkg[side]->Add(fitHists[side][i]);
        //                 }
        //             }
        //         }
        //         if (count > 0) {
        //             bkg[side]->Print();
        //             bkg[side]->Write();
        //             bkg[side]->MnvH1DToCSV(bkg[side]->GetName(), outputDir + "/csv/", 1., false);
        //         }
        //     }
        // }
        // for (auto side : sidebands) {
        //     std::snprintf(fname, sizeof(fname), fh1d_template.c_str(), side.c_str(), "bkgsub", fitvarName.c_str(), fitbin + 1);
        //     bkgsub[side] = (MnvH1D*)dataHist[side]->Clone(fname1d);
        //     bkgsub[side]->AddMissingErrorBandsAndFillWithCV(*(fitHists[side][0]));
        //     bkgsub[side]->Add(bkg[side], -1);
        //     bkgsub[side]->Write();
        //     dataHist[side]->MnvH1DToCSV(dataHist[side]->GetName(), outputDir + "/csv/", 1., false);
        //     bkgsub[side]->MnvH1DToCSV(bkgsub[side]->GetName(), outputDir + "/csv/", 1., false);
        // }
        // std::cout << "wrote the inputs and outputs " << std::endl;

        // for (auto side : sidebands) {
        //     // dataHist[side]->Print("ALL");
        //     dataHist[side]->Scale(1., "width");
        //     // dataHist[side]->Print("ALL");
        //     tot[side]->Scale(1., "width");
        //     pre[side]->Scale(1., "width");
        //     bkg[side]->Scale(1., "width");
        //     bkgsub[side]->Scale(1., "width");
        //     for (int i = 0; i < categories.size(); i++) {
        //         unfitHists[side][i]->Scale(1., "width");
        //         fitHists[side][i]->Scale(1., "width");
        //     }
        // }

        // for (auto side : sidebands) {
        //     mnvPlotter.DrawDataMCWithErrorBand(dataHist[side], tot[side], 1., "TR");
        //     cF.Print(TString(outputDir + "/png/" + side + "_postfit_compare.png").Data());

        //     mnvPlotter.DrawDataMCWithErrorBand(dataHist[side], pre[side], 1., "TR");
        //     cF.Print(TString(outputDir + "/png/" + side + "_prefit_compare.png").Data());

        //     mnvPlotter.DrawDataMCWithErrorBand(bkgsub[side], fitHists[side][0], 1., "TR");
        //     cF.Print(TString(outputDir + "/png/" + side + "_bkgsub_compare.png").Data());
        // }

        // TObjArray* combmcin;
        // TObjArray* combmcout;

        // for (auto side : sidebands) {
        //     std::string label;
        //     label = side + " " + fitvarName;
        //     combmcin = Vec2TObjArray(unfitHists[side], categories);
        //     combmcout = Vec2TObjArray(fitHists[side], categories);
        //     std::cout << " before call to DrawStack" << std::endl;
        //     PlotUtils::MnvH1D* data = new PlotUtils::MnvH1D(*(dataHist[side]));
        //     data->SetTitle("Data");
        //     label = side + " " + fitvarName + " Before fit";
        //     TText t(.3, .95, label.c_str());
        //     t.SetTitle(label.c_str());
        //     t.SetNDC(1);
        //     t.SetTextSize(.03);

        //     mnvPlotter.DrawDataStackedMC(data, combmcin, 1.0, "TR");
        //     t.Draw("same");
        //     cF.Print(TString(outputDir + "/png/" + side + "_prefit_combined.png").Data());
        //     label = side + " " + fitvarName + " After fit";
        //     TText t2(.3, .95, label.c_str());
        //     t2.SetTitle(label.c_str());
        //     t2.SetNDC(1);
        //     t2.SetTextSize(.03);
        //     t2.SetTitle(label.c_str());
        //     mnvPlotter.DrawDataStackedMC(data, combmcout, 1.0, "TR");
        //     cF.Print(TString(outputDir + "/png/" + side + "_" + fitType + "_postfit_combined.png").Data());
        //     label = side + " " + fitvarName + "Background Subtracted";

        //     t2.SetTitle(label.c_str());
        //     t2.SetNDC(1);
        //     t2.SetTextSize(.03);
        //     t2.SetTitle(label.c_str());
        //     bkgsub[side]->SetTitle("bkgsub");
        //     mnvPlotter.DrawDataStackedMC(bkgsub[side], combmcout, 1.0, "TR");
        //     cF.Print(TString(outputDir + "/png/" + side + "_" + fitType + "_bkgsub_combined.png").Data());
        // }
        std::cout << " > after drawstack loop, before closign files" << std::endl;
    }

    // Now put all the parameters into a file with scale factors
    std::vector<std::string> universes = parameters_list[0]->GetVertErrorBandNames();
    universes.push_back("CV");
    std::string scalefileName = (outputDir + "/scales_" + outputFileNameraw).c_str();
    TFile* scalefile = TFile::Open(scalefileName.c_str(), "RECREATE");
    scalefile->cd();
    for (int cat = 0; cat < categories.size(); cat++) {
        std::string catname = categories[cat];
        char sname[1000];
        std::string s1d_template = "h___Background___%s___%s___scale";
        std::snprintf(sname, sizeof(sname), s1d_template.c_str(), catname.c_str(), projvarName.c_str());
        PlotUtils::MnvH1D* catscales = dummy_xproj_hist->Clone(sname);
        catscales->ClearAllErrorBands();
        catscales->Reset("ICES");
        for (int fitbin = 1; fitbin < n_fitbins+1; fitbin++) {
            PlotUtils::MnvH1D* param_mnvh = parameters_list[fitbin - 1];
            // param_mnvh->Print();
            // Now get the content for that cat, put it in the bin for the scales
            for (auto univ : universes) {
                int nunivs = 1;
                if (univ != "CV") {
                    // std::cout << univ << std::endl;
                    nunivs = param_mnvh->GetVertErrorBand(univ)->GetNHists();
                    if (fitbin == 1)
                        catscales->AddVertErrorBandAndFillWithCV(univ, nunivs);
                }
                for (int iuniv = 0; iuniv < nunivs; iuniv++) {
                    if (univ == "CV") {
                        std::cout << "bin content being set " << param_mnvh->GetBinContent(cat + 1) << std::endl;
                        std::cout << "bin error being set   " << param_mnvh->GetBinError(cat + 1) << std::endl;
                        catscales->SetBinContent(fitbin, param_mnvh->GetBinContent(cat + 1));
                        catscales->SetBinError(fitbin, param_mnvh->GetBinError(cat + 1));
                    } else {
                        // std::cout << " before catscales getHist" << std::endl;
                        TH1D* catscales_hist = catscales->GetVertErrorBand(univ)->GetHist(iuniv);
                        // std::cout << " before param_mnvh getHist" << std::endl;
                        TH1D* param_hist = param_mnvh->GetVertErrorBand(univ)->GetHist(iuniv);
                        catscales_hist->SetBinContent(fitbin, param_hist->GetBinContent(cat + 1));
                    }
                }
            }
        }
        SyncBands(catscales);
        catscales->SetTitle(("scales for "+catname).c_str());
        catscales->Print();
        catscales->MnvH1DToCSV((outputDir + "/csv/").c_str());
        catscales->Write();
    }

    std::cout << "before closing files" << std::endl;
    inputFile->cd();
    inputFile->Close();
    std::cout << "after close input" << std::endl;
    outputFile->cd();
    // outputFile->Close();
    std::cout << "Closing Output File... Does this solve the issue of seg fault." << std::endl;

    std::cout << "HEY YOU DID IT!!!" << std::endl;
    return 0;
}