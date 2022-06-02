#include <iostream>
#include <string>
#include "PlotUtils/MnvH1D.h"
#include "PlotUtils/MnvH2D.h"
#include "MinervaUnfold/MnvResponse.h"
#include "MinervaUnfold/MnvUnfold.h"
#include "utils/RebinFlux.h"
#include "utils/SyncBands.h"
#include "TH2D.h"
#include "TF2.h"
#include "TCanvas.h"
#include "utils/NuConfig.h"
#include "PlotUtils/FluxReweighter.h"

#ifndef __CINT__
#include "include/plotting_pdf.h"
#endif

void applyStyle(MnvH1D* myhist){

  myhist->GetXaxis()->CenterTitle(true);
  myhist->GetYaxis()->CenterTitle(true);

  myhist->SetMarkerStyle(8);
  myhist->SetLineWidth(2);
  myhist->SetLabelFont(42);
  myhist->SetTitleFont(42);

  myhist->GetYaxis()->SetTitleFont(42);
  myhist->GetXaxis()->SetTitleFont(42);

  myhist->SetLabelSize(0.05,"x");
  myhist->SetTitleSize(0.05,"x");
  myhist->SetLabelSize(0.05,"y");
  myhist->SetTitleSize(0.05,"y");

  myhist->SetTickLength(0.01, "Y");
  myhist->SetTickLength(0.02, "X");

  myhist->SetNdivisions(510, "XYZ");

}


template<class MnvHistoType>
  int drawStacked(std::string sample, std::string variable, std::string basename,
                  std::map<std::string,MnvHistoType*> hists1D,
                  NuConfig config, NuConfig variables1DConfig, NuConfig samplesConfig,
                  std::string pdffilename1D, double POTScale, 
                  bool DEBUG, bool binwid, TCanvas & canvas) {
                  
    int logscale = 0;
    
    // Read in signal, background, and data names and colors
    NuConfig sigkey = config.GetConfig("signal");
    std::cout << std::endl << "   Signal key:" << std::endl;
    sigkey.Print();
    std::string sig = sigkey.GetString(sample);
    NuConfig bkgkey = config.GetConfig("background");
    std::vector<std::string> bkg = bkgkey.GetStringVector(sample);
    std::cout << std::endl << "   Background key:" << std::endl;
    bkgkey.Print();
    NuConfig datkey = config.GetConfig("data");
    std::string dat = datkey.GetString(sample);
    std::cout << std::endl << "   Data key:" << std::endl;
    datkey.Print();
    
    
    NuConfig sampleConfig = samplesConfig.GetConfig(sample);
    NuConfig colorFillConfig = sampleConfig.GetConfig("fill_colors");
    NuConfig colorLineConfig = sampleConfig.GetConfig("line_colors");
    NuConfig legendEntries = sampleConfig.GetConfig("legend_entries");
    
    
    // Set colors
    hists1D[sig]->SetFillColor(colorFillConfig.GetInt(sig));
    hists1D[sig]->SetLineColor(colorFillConfig.GetInt(sig));
    for(int i = 0; i <= bkg.size()-1; i++){
      hists1D[bkg[i]]->SetFillColor(colorFillConfig.GetInt(bkg[i]));
      hists1D[bkg[i]]->SetLineColor(colorFillConfig.GetInt(bkg[i]));
    }
    
    // Bin width normalization
    if(binwid){
      hists1D[dat]->Scale(1.0,"width");
      hists1D[sig]->Scale(1.0,"width");
      for(int i = 0; i <= bkg.size()-1; i++){
        hists1D[bkg[i]]->Scale(1.0,"width");
      }
    }
    
    // POT normalize
    hists1D[sig]->Scale(POTScale);
    for(int i = 0; i <= bkg.size()-1; i++){
      hists1D[bkg[i]]->Scale(POTScale);
    }
    
    // Stack hists
    THStack *hs = new THStack();
    for(int i = bkg.size()-1; i >= 0; i--){
      hs->Add(new TH1D(hists1D[bkg[i]]->GetCVHistoWithError()));
    }
    hs->Add(new TH1D(hists1D[sig]->GetCVHistoWithError()));
    
    // Make legend
    auto *leg = new TLegend(0.62,0.6,0.89,0.89);
    leg->SetFillColor(kWhite);
    //leg->SetLineColor(0);
    leg->AddEntry(hists1D[dat],legendEntries.GetString(dat).c_str(),"p");
    double maxEntryLength = legendEntries.GetString(dat).length();
    leg->AddEntry(hists1D[sig],legendEntries.GetString(sig).c_str(),"F");
    if(legendEntries.GetString(sig).length() > maxEntryLength){
      maxEntryLength =legendEntries.GetString(sig).length();
    }
    for(int i = 0; i <= bkg.size()-1; i++){
      leg->AddEntry(hists1D[bkg[i]],legendEntries.GetString(bkg[i]).c_str(),"F");
      if(legendEntries.GetString(bkg[i]).length() > maxEntryLength){
        maxEntryLength =legendEntries.GetString(bkg[i]).length();
      }
    }
    std::cout << std::endl << "   Max Legend Entry Length = " << maxEntryLength << std::endl;

	// Get variable titles
	std::string title = sample + "_" + variable;
	NuConfig variableConfig = variables1DConfig.GetConfig(variable);
	std::string xtitle = variableConfig.GetString("title");
	std::string ytitle;
	if(binwid) ytitle = "Events per " + variableConfig.GetString("units");
	else ytitle = "Events";

    hists1D[dat]->GetXaxis()->SetTitle(xtitle.c_str());
    hists1D[dat]->GetYaxis()->SetTitle(ytitle.c_str());
    hists1D[dat]->GetXaxis()->SetTitleOffset(1.2);
    hists1D[dat]->GetYaxis()->SetTitleOffset(1.3);
    hists1D[dat]->SetTitle(title.c_str());
    hists1D[dat]->SetStats(0);
    applyStyle(hists1D[dat]);
    
    // Draw hists
    hists1D[dat]->Draw("PE1");
    hs->Draw("HISTSAME");
    hists1D[dat]->Draw("PE1SAME");
    hists1D[dat]->GetYaxis()->SetRangeUser(0,1.2*hists1D[dat]->GetBinContent(hists1D[dat]->GetMaximumBin()));
    leg->Draw("SAME");
    gPad->RedrawAxis();
    
    canvas.Print(pdffilename1D.c_str());
    
    return 0;
    
  }
    
    
    
    
    
    
    
    
    
    
    
    
