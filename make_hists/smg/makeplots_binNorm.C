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
			
			MnvH1D *qe = (MnvH1D*)infile->Get(Form("h___%s___qelike___%s___reconstructed",sample.c_str(),vars1D[i].c_str()));
			MnvH1D *sch = (MnvH1D*)infile->Get(Form("h___%s___1chargedpion___%s___reconstructed",sample.c_str(),vars1D[i].c_str()));
			MnvH1D *snu = (MnvH1D*)infile->Get(Form("h___%s___1neutralpion___%s___reconstructed",sample.c_str(),vars1D[i].c_str()));
			MnvH1D *multi = (MnvH1D*)infile->Get(Form("h___%s___multipion___%s___reconstructed",sample.c_str(),vars1D[i].c_str()));
			MnvH1D *other = (MnvH1D*)infile->Get(Form("h___%s___other___%s___reconstructed",sample.c_str(),vars1D[i].c_str()));
			MnvH1D *data = (MnvH1D*)infile->Get(Form("h___%s___data___%s___reconstructed",sample.c_str(),vars1D[i].c_str()));
			
			qe->SetFillColor(TColor::GetColor(0,133,173));//kMagenta-4);
			sch->SetFillColor(TColor::GetColor(175,39,47));//kBlue-7);
			snu->SetFillColor(TColor::GetColor(76,140,43));//kGreen-3);
			multi->SetFillColor(TColor::GetColor(234,170,0));//kRed-4);
			other->SetFillColor(TColor::GetColor(82,37,6));//kBlack);
			data->SetFillColor(TColor::GetColor(255,255,255));

			qe->SetFillStyle(3001);
			sch->SetFillStyle(3001);
			snu->SetFillStyle(3001);
			multi->SetFillStyle(3001);
			other->SetFillStyle(3001);
			
			qe->SetLineColor(TColor::GetColor(0,133,173));//kMagenta-4);
			sch->SetLineColor(TColor::GetColor(175,39,47));//Blue-7);
			snu->SetLineColor(TColor::GetColor(76,140,43));//kGreen-3);
			multi->SetLineColor(TColor::GetColor(234,170,0));//kRed-4);
			other->SetLineColor(TColor::GetColor(82,37,6));//kBlack);
			data->SetLineColor(TColor::GetColor(255,255,255));
			
			qe->Scale(1.0,"width");
			sch->Scale(1.0,"width");
			snu->Scale(1.0,"width");
			multi->Scale(1.0,"width");
			other->Scale(1.0,"width");
			data->Scale(1.0,"width");
			
			int nbins = qe->GetNbinsX();
			for( int i=0; i<=nbins; i++ ){
			
				double denom = qe->GetBinContent(i) +
				               sch->GetBinContent(i) +
				               snu->GetBinContent(i) +
				               multi->GetBinContent(i) +
				               other->GetBinContent(i);
				if(denom == 0) denom = 1;
				
				double num_qe = qe->GetBinContent(i);
				double num_sch = sch->GetBinContent(i);
				double num_snu = snu->GetBinContent(i);
				double num_multi = multi->GetBinContent(i);
				double num_other = other->GetBinContent(i);
				
				qe->SetBinContent(i,num_qe/denom);
				sch->SetBinContent(i,num_sch/denom);
				snu->SetBinContent(i,num_snu/denom);
				multi->SetBinContent(i,num_multi/denom);
				other->SetBinContent(i,num_other/denom);
				data->SetBinContent(i,0.);
			}
			
			data->GetYaxis()->SetRangeUser(0,1);
			
			THStack *hs = new THStack();
			hs->Add(new TH1D(other->GetCVHistoWithError()));
			hs->Add(new TH1D(multi->GetCVHistoWithError()));
			hs->Add(new TH1D(snu->GetCVHistoWithError()));
			hs->Add(new TH1D(sch->GetCVHistoWithError()));
			hs->Add(new TH1D(qe->GetCVHistoWithError()));
			
			
			data->GetYaxis()->SetTitle("relative contribution per bin");
			data->GetXaxis()->SetTitleOffset(1.2);
			data->GetYaxis()->SetTitleOffset(1);
			data->GetYaxis()->SetMaxDigits(4);
			if (sample == "QElike_Mult1") {
				data->SetTitle("Multiplicity = 1, Traditional Cuts");
			}
			else if (sample == "Mult1TMVA04" ||
			         sample == "Mult1TMVA035"  ) {
				data->SetTitle("Multiplicity = 1, TMVA Gradient BDTs");
			}
			else if (sample == "QElike_Mult2p") {
				data->SetTitle("Multiplicity #geq 2, Traditional Cuts");
			}
			else if (sample == "Mult2pTMVA04" ||
			         sample == "Mult2pTMVA035"  ) {
				data->SetTitle("Multiplicity #geq 2, TMVA Gradient BDTs");
			}
			else if (sample == "Mult1p") {
				data->SetTitle("Multiplicity #geq 1");
			}
			else {
				data->SetTitle(sample.c_str());
			}
			data->SetStats(0);
			applyStyle(data);
			
			TLegend *leg = new TLegend(0.62,0.6,0.89,0.89);
			leg->SetFillColor(kWhite);
			leg->AddEntry(qe,"QELike","F");
			leg->AddEntry(sch,"Single #pi^{+/-} in FS","F");
			leg->AddEntry(snu,"Single #pi^{0} in FS","F");
			leg->AddEntry(multi,"N#pi in FS","F");
			leg->AddEntry(other,"Other","F");
			
			double xmax = data->GetXaxis()->GetBinUpEdge(data->GetNbinsX());
			double xmin = data->GetXaxis()->GetBinLowEdge(1);
			double xdel = xmax-xmin;
			double xtext = xmin+0.35*xdel;
			double ytext = 1;
			
			TLatex *text = new TLatex(xtext,0.98*ytext,"Work in progress");
			text->SetTextAlign(13);
			text->SetTextColor(kRed);
			text->SetTextFont(13);
			text->SetTextSize(20);

			data->Draw("HIST");
			hs->Draw("HISTSAME");
			//dolog[i]?data->GetYaxis()->SetRangeUser(0.1,yscale*data->GetBinContent(data->GetMaximumBin())):data->GetYaxis()->SetRangeUser(0,yscale*data->GetBinContent(data->GetMaximumBin()));
			leg->Draw("SAME");
			text->Draw("SAME");
			//if(dolog[i]) c1->SetLogy(true);
			//if(dolog[i]) c1->SetLogx(true);
			gPad->RedrawAxis();			
			
			//c1->Print(Form("%s/1D/%s_%s.png",rootfolder.c_str(),sample.c_str(),vars1D[i].c_str()));
			c1->Print(Form("binNorm_%s___%s___%s_%s.png",sample.c_str(),vars1D[i].c_str(),base.c_str(),prescale.c_str()));
			
		}
	}
   
	exit(0);
}

