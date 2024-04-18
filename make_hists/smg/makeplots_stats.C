#include <iostream>
#include <string>
#include "PlotUtils/MnvH1D.h"
#include "PlotUtils/MnvH2D.h"
#include "MinervaUnfold/MnvResponse.h"
#include "MinervaUnfold/MnvUnfold.h"
#include "utils/RebinFlux.h"
#include "utils/SyncBands.h"
#include "TH2D.h"
#include "TH1D.h"
#include "TF2.h"
#include "TCanvas.h"
#include "utils/NuConfig.h"
#include "PlotUtils/FluxReweighter.h"
#include <math.h>
#include "TColor.h"
#include "TLatex.h"
//#include <filesystem>

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


void applyStyle(MnvH2D* myhist){

  myhist->GetXaxis()->CenterTitle(true);
  myhist->GetYaxis()->CenterTitle(true);
  myhist->GetZaxis()->CenterTitle(true);
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
  myhist->SetLabelSize(0.05,"z");
  myhist->SetTitleSize(0.04,"z");
  myhist->GetZaxis()->SetTitleOffset(1.05);

  myhist->SetTickLength(0.01, "Y");
  myhist->SetTickLength(0.02, "X");
  
  myhist->SetNdivisions(510, "XYZ");
}


int main(const int argc, const char *argv[]) {
	
	std::string pl = std::string(argv[1]);
	std::string configfilename(pl+".json");
	NuConfig config;
  config.Read(configfilename);
  
  std::string path(pl);
  std::string prescale; 
  //= config.GetDouble("prescale");
  prescale = std::string(argv[2]);
  std::string base = path.substr(path.find_last_of("/\\") + 1);
  std::string rootfilename = Form("%s_%s_%s.root",config.GetString("outRoot").c_str(),base.c_str(),prescale.c_str());
  std::cout << "\nroot file: " << rootfilename << std::endl;
  std::string rootfolder = rootfilename.substr(0, rootfilename.size()-5);
  //std::filesystem::create_directory(rootfolder);
  //std::filesystem::create_directory(Form("%s/1D",rootfolder));
  //std::filesystem::create_directory(Form("%s/2D",rootfolder));
  
  std::vector<std::string> vars1D = config.GetStringVector("AnalyzeVariables");
  std::vector<std::string> vars2D = config.GetStringVector("Analyze2DVariables");
  std::vector<std::string> samples = config.GetStringVector("runsamples");
  
  double yscale = 1.2;
	
	TFile *infile = new TFile(Form(rootfilename.c_str()));
	
	for (auto sample : samples) {
		for ( int i=0; i<vars1D.size(); i++ ) {
		
			TCanvas *c1 = new TCanvas(vars1D[i].c_str(),vars1D[i].c_str());
			c1->SetLeftMargin(0.15);
			c1->SetRightMargin(0.1);
			c1->SetBottomMargin(0.15);
			c1->SetTopMargin(0.1);
			
			std::string ref_sample;
			if (sample == "QElike_Mult1" ||
			    sample == "Mult1TMVA035" ||
			    sample == "Mult1TMVA04"  ||
			    sample == "Mult1"          ) {
				ref_sample = "Mult1";
			}
			else {
				ref_sample = "Mult2p";
			}
			
			MnvH1D *qe_reco = (MnvH1D*)infile->Get(Form("h___%s___qelike___%s___reconstructed",sample.c_str(),vars1D[i].c_str()));
			MnvH1D *qe_true = (MnvH1D*)infile->Get(Form("h___%s___qelike___%s___reconstructed",ref_sample.c_str(),vars1D[i].c_str()));
			MnvH1D *sch = (MnvH1D*)infile->Get(Form("h___%s___1chargedpion___%s___reconstructed",sample.c_str(),vars1D[i].c_str()));
			MnvH1D *snu = (MnvH1D*)infile->Get(Form("h___%s___1neutralpion___%s___reconstructed",sample.c_str(),vars1D[i].c_str()));
			MnvH1D *multi = (MnvH1D*)infile->Get(Form("h___%s___multipion___%s___reconstructed",sample.c_str(),vars1D[i].c_str()));
			MnvH1D *other = (MnvH1D*)infile->Get(Form("h___%s___other___%s___reconstructed",sample.c_str(),vars1D[i].c_str()));		
			
			MnvH1D *h_pur = (MnvH1D*) qe_reco->Clone();
			MnvH1D *h_eff = (MnvH1D*) qe_reco->Clone();
			MnvH1D *h_pureff = (MnvH1D*) qe_reco->Clone();
			
			h_pur->SetLineColor(kBlue+1);
			h_eff->SetLineColor(kGreen+2);
			h_pureff->SetLineColor(kRed+1);
			
			h_eff->SetLineWidth(2);
			h_pureff->SetLineWidth(2);
		
		  int nbins = h_pur->GetNbinsX();
		  // Purity
			for( int i=0; i<=nbins; i++ ){
			
				double denom = qe_reco->GetBinContent(i) +
				               sch->GetBinContent(i) +
				               snu->GetBinContent(i) +
				               multi->GetBinContent(i) +
				               other->GetBinContent(i);				
				double num_qe_reco = qe_reco->GetBinContent(i);
				double num_qe_true = qe_true->GetBinContent(i);
				
				if (denom == 0) denom = 1;
				h_pur->SetBinContent(i,num_qe_reco/denom);
				if (num_qe_true == 0) {
					h_eff->SetBinContent(i,0);
				}
				else {
					h_eff->SetBinContent(i,num_qe_reco/num_qe_true);
				}
				double purity = h_pur->GetBinContent(i);
				double efficiency = h_eff->GetBinContent(i);
				h_pureff->SetBinContent(i,purity*efficiency);
			}
			
			h_pur->GetYaxis()->SetRangeUser(0,1);			
			h_pur->GetXaxis()->SetTitleOffset(1.2);
			if (sample == "QElike_Mult1") {
				h_pur->SetTitle("Multiplicity = 1, Traditional Cuts");
			}
			else if (sample == "Mult1TMVA035") {
				h_pur->SetTitle("Multiplicity = 1, TMVA Gradient BDTs");
			}
			else if (sample == "Mult1TMVA04") {
				h_pur->SetTitle("Multiplicity = 1, TMVA Gradient BDTs");
			}
			else if (sample == "QElike_Mult2p") {
				h_pur->SetTitle("Multiplicity #geq 2, Traditional Cuts");
			}
			else if (sample == "Mult2pTMVA035") {
				h_pur->SetTitle("Multiplicity #geq 2, TMVA Gradient BDTs");
			}
			else if (sample == "Mult2pTMVA04") {
				h_pur->SetTitle("Multiplicity #geq 2, TMVA Gradient BDTs");
			}
			else {
				h_pur->GetYaxis()->SetTitle("Counts/Unit");
			}
			h_pur->SetStats(0);
			applyStyle(h_pur);
			
			
			TLegend *leg = new TLegend(0.65,0.77,0.89,0.89);
			leg->SetFillColor(kWhite);
			leg->AddEntry(h_pur,"Purity","l");
			leg->AddEntry(h_eff,"Efficiency","l");
			leg->AddEntry(h_pureff,"Purity #times Efficiency","l");
			
			double xmax = h_pur->GetXaxis()->GetBinUpEdge(h_pur->GetNbinsX());
			double xmin = h_pur->GetXaxis()->GetBinLowEdge(1);
			double xdel = xmax-xmin;
			double xtext = xmin+0.35*xdel;
			double ytext = h_pur->GetMaximum();
			
			TLatex *text = new TLatex(xtext,0.98,"Work in progress");
			text->SetTextAlign(13);
			text->SetTextColor(kRed);
			text->SetTextFont(13);
			text->SetTextSize(20);
			
			h_pur->Draw("HIST");
			h_eff->Draw("HISTSAME");
			h_pureff->Draw("HISTSAME");
			leg->Draw("SAME");
			text->Draw("SAME");
			gPad->RedrawAxis();
			
			//c1->Print(Form("%s/1D/%s_%s.png",rootfolder.c_str(),sample.c_str(),vars1D[i].c_str()));
			c1->Print(Form("%s_stats___%s___%s_%s.png",sample.c_str(),vars1D[i].c_str(),base.c_str(),prescale.c_str()));
			c1->Print(Form("%s_stats___%s___%s_%s.C",sample.c_str(),vars1D[i].c_str(),base.c_str(),prescale.c_str()));
			
		}
	}
	exit(0);
}

