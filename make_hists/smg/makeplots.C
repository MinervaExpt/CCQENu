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
#include <filesystem>

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
			data->SetFillColor(TColor::GetColor(0,0,0));

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
			data->SetLineColor(TColor::GetColor(0,0,0));
			
			double data_integral = data->Integral();
			double mc_integral = qe->Integral() + sch->Integral() + snu->Integral() +
			                     multi->Integral() + other->Integral();
			double integral_scale = data_integral/mc_integral;
			
			qe->Scale(integral_scale);
			sch->Scale(integral_scale);
			snu->Scale(integral_scale);
			multi->Scale(integral_scale);
			other->Scale(integral_scale);
			
			qe->Scale(1.0,"width");
			sch->Scale(1.0,"width");
			snu->Scale(1.0,"width");
			multi->Scale(1.0,"width");
			other->Scale(1.0,"width");
			data->Scale(1.0,"width");
			
			THStack *hs = new THStack();
			hs->Add(new TH1D(other->GetCVHistoWithError()));
			hs->Add(new TH1D(multi->GetCVHistoWithError()));
			hs->Add(new TH1D(snu->GetCVHistoWithError()));
			hs->Add(new TH1D(sch->GetCVHistoWithError()));
			hs->Add(new TH1D(qe->GetCVHistoWithError()));
			
			data->GetYaxis()->SetTitle("Counts/Unit");
			data->GetXaxis()->SetTitleOffset(1.2);
			data->GetYaxis()->SetTitleOffset(1.3);
			data->SetTitle(vars1D[i].c_str());
			data->SetStats(0);
			applyStyle(data);
			
			TLegend *leg = new TLegend(0.62,0.6,0.89,0.89);
			leg->SetFillColor(kWhite);
			leg->AddEntry(data,"MINERvA Data","p");
			leg->AddEntry(qe,"QELike","F");
			leg->AddEntry(sch,"Single #pi^{+/-} in FS","F");
			leg->AddEntry(snu,"Single #pi^{0} in FS","F");
			leg->AddEntry(multi,"N#pi in FS","F");
			leg->AddEntry(other,"Other","F");
			
			data->Draw("PE1");
			hs->Draw("HISTSAME");
			data->Draw("PE1SAME");
			//dolog[i]?data->GetYaxis()->SetRangeUser(0.1,yscale*data->GetBinContent(data->GetMaximumBin())):data->GetYaxis()->SetRangeUser(0,yscale*data->GetBinContent(data->GetMaximumBin()));
			leg->Draw("SAME");
			//if(dolog[i]) c1->SetLogy(true);
			//if(dolog[i]) c1->SetLogx(true);
			gPad->RedrawAxis();
			
			//c1->Print(Form("%s/1D/%s_%s.png",rootfolder.c_str(),sample.c_str(),vars1D[i].c_str()));
			c1->Print(Form("%s.png",vars1D[i].c_str()));
			
		}
		
		/*for ( int i=0; i<vars2D.size(); i++ ) {
		
			std::vector<std::string> interactions = {"data","qelike","1chargedpion","1neutralpion","multipion","other"};
			
			for (auto iter : interactions) {
				TCanvas *c1 = new TCanvas(vars2D[i].c_str(),vars2D[i].c_str());
				c1->SetLeftMargin(0.15);
				c1->SetRightMargin(0.1);
				c1->SetBottomMargin(0.15);
				c1->SetTopMargin(0.1);
				
				MnvH2D *h2D = (MnvH2D*)infile->Get(Form("h2D___%s___%s___%s___reconstructed",
				                                        sample.c_str(),iter.c_str(),vars2D[i].c_str()));
				                                        
				c1->Print(Form("%s/2D/%s_%s_%s.png",rootfolder.c_str(),sample.c_str(),iter.c_str(),vars2D[i].c_str()));
			}
		}*/
		
	}
  
  /////////
  //int argument = std::stoi(argv[1]);
	int argument = 100;
	if(argument == 1 || argument == 2) {
		/*std::vector<bool> binwidthnorm = { true,true,true,true,true,true,true,true };
		std::vector<std::string> varnames = {"PrimaryProtonScore1","recoil","PrimaryProtonTrackVtxGap","BlobCount",
                                         "PrimaryProtonFractionVisEnergyInCone","PrimaryProtonTfromdEdx",
                                         "NumClustsPrimaryProtonEnd","ImprovedMichelCount"};
		std::vector<std::string> ytitles = {"Counts","Counts/GeV","Counts/mm","Counts","Counts",
		                                    "Counts/MeV","Counts","Counts"};
		std::vector<bool> dolog = { false,false,false,false,false,false,false,false,false };
		std::string sample;
		std::string title;
		if(argument == 1) {
			sample = "2track";
			title = "2 tracks";
		
		}
		else if(argument == 2) {
			sample = "QElike_noProtonCuts";
			title = "QElike, No Protons Cut, 2+ tracks";
		}
		
		std::string rootfilename = "SB_NuConfig_v8_2track_me1n_1.root";*/
		
		std::vector<bool> binwidthnorm = { true,true,false,false,false,false,false,true,true,false,false,false,false };
		std::vector<std::string> varnames = {"Q2QE","EnuCCQE","bdtg1ChargedPion","bdtg1NeutralPion",
                                         "bdtgMultiPion","bdtgOther","bdtgQELike","ptmu","pzmu",
                                         "PrimaryProtonTrackVtxGap","PrimaryProtonScore1",
                                         "ImprovedMichelCount","BlobCount"};
		std::vector<std::string> ytitles = {"Counts/GeV^s","Counts/GeV","Counts","Counts","Counts",
		                                    "Counts","Counts","Counts/GeV","Counts/GeV","Counts",
		                                    "Counts","Counts","Counts"};
		std::vector<bool> dolog = { true,false,false,false,false,false,false,false,false,false,false,false,false };
		std::string sample;
		std::string title;
		sample = "Mult1p";
		title = "Multiplicity 1+, in fiducial volume, muon in MINOS";
		std::string rootfilename = "SB_NuConfig_mult1pBDTG_me1N_1.root";
		
		double yscale = 1.2;
		
		TFile *infile = new TFile(Form(rootfilename.c_str()));
		
		for ( int i=0; i<varnames.size(); i++ ) {
		 
			TCanvas *c1 = new TCanvas(varnames[i].c_str(),varnames[i].c_str());
			c1->SetLeftMargin(0.15);
			c1->SetRightMargin(0.1);
			c1->SetBottomMargin(0.15);
			c1->SetTopMargin(0.1);
			
			MnvH1D *qe = (MnvH1D*)infile->Get(Form("h___%s___qelike___%s___reconstructed",sample.c_str(),varnames[i].c_str()));
			MnvH1D *sch = (MnvH1D*)infile->Get(Form("h___%s___1chargedpion___%s___reconstructed",sample.c_str(),varnames[i].c_str()));
			MnvH1D *snu = (MnvH1D*)infile->Get(Form("h___%s___1neutralpion___%s___reconstructed",sample.c_str(),varnames[i].c_str()));
			MnvH1D *multi = (MnvH1D*)infile->Get(Form("h___%s___multipion___%s___reconstructed",sample.c_str(),varnames[i].c_str()));
			MnvH1D *other = (MnvH1D*)infile->Get(Form("h___%s___other___%s___reconstructed",sample.c_str(),varnames[i].c_str()));
			MnvH1D *data = (MnvH1D*)infile->Get(Form("h___%s___data___%s___reconstructed",sample.c_str(),varnames[i].c_str()));
			
			qe->SetFillColor(TColor::GetColor(0,133,173));//kMagenta-4);
			sch->SetFillColor(TColor::GetColor(175,39,47));//kBlue-7);
			snu->SetFillColor(TColor::GetColor(76,140,43));//kGreen-3);
			multi->SetFillColor(TColor::GetColor(234,170,0));//kRed-4);
			other->SetFillColor(TColor::GetColor(82,37,6));//kBlack);
			data->SetFillColor(TColor::GetColor(0,0,0));

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
			data->SetLineColor(TColor::GetColor(0,0,0));
			
			/*MnvH1D *h_pot = (MnvH1D*)infile->Get("POT_summary");
			double dataPOT = h_pot->GetBinContent(1);
			double mcPOTprescaled = h_pot->GetBinContent(3);
			double POTScale = dataPOT/mcPOTprescaled;
			delete h_pot;
			
			qe->Scale(POTScale);
			sch->Scale(POTScale);
			snu->Scale(POTScale);
			multi->Scale(POTScale);
			other->Scale(POTScale);*/
			
			double data_integral = data->Integral();
			double mc_integral = qe->Integral() + sch->Integral() + snu->Integral() +
			                     multi->Integral() + other->Integral();
			double integral_scale = data_integral/mc_integral;
			
			qe->Scale(integral_scale);
			sch->Scale(integral_scale);
			snu->Scale(integral_scale);
			multi->Scale(integral_scale);
			other->Scale(integral_scale);
			
			if(binwidthnorm[i]){
				qe->Scale(1.0,"width");
				sch->Scale(1.0,"width");
				snu->Scale(1.0,"width");
				multi->Scale(1.0,"width");
				other->Scale(1.0,"width");
				data->Scale(1.0,"width");
			}
			
			THStack *hs = new THStack();
			hs->Add(new TH1D(other->GetCVHistoWithError()));
			hs->Add(new TH1D(multi->GetCVHistoWithError()));
			hs->Add(new TH1D(snu->GetCVHistoWithError()));
			hs->Add(new TH1D(sch->GetCVHistoWithError()));
			hs->Add(new TH1D(qe->GetCVHistoWithError()));
			
			//data->GetXaxis()->SetTitle(xtitle.c_str());
			data->GetYaxis()->SetTitle(ytitles[i].c_str());
			data->GetXaxis()->SetTitleOffset(1.2);
		  data->GetYaxis()->SetTitleOffset(1.3);
			//data->SetTitle(title.c_str());
			data->SetTitle(varnames[i].c_str());
			data->SetStats(0);
			applyStyle(data);
			
			TLegend *leg = new TLegend(0.62,0.6,0.89,0.89);
			leg->SetFillColor(kWhite);
			leg->AddEntry(data,"MINERvA Data","p");
			leg->AddEntry(qe,"QELike","F");
			leg->AddEntry(sch,"Single #pi^{+/-} in FS","F");
			leg->AddEntry(snu,"Single #pi^{0} in FS","F");
			leg->AddEntry(multi,"N#pi in FS","F");
			leg->AddEntry(other,"Other","F");
			
			data->Draw("PE1");
			hs->Draw("HISTSAME");
			data->Draw("PE1SAME");
			//dolog[i]?data->GetYaxis()->SetRangeUser(0.1,yscale*data->GetBinContent(data->GetMaximumBin())):data->GetYaxis()->SetRangeUser(0,yscale*data->GetBinContent(data->GetMaximumBin()));
			leg->Draw("SAME");
			//if(dolog[i]) c1->SetLogy(true);
			if(dolog[i]) c1->SetLogx(true);
			gPad->RedrawAxis();
			
			c1->Print(Form("%s_%s.png",sample.c_str(),varnames[i].c_str()));
			
		}
	}
	else if(argument == 3 || argument == 4 || argument == 5){
	
		std::vector<std::string> varnames = { "PrimaryProtonScore","NumClustsPrimaryProtonEnd","PrimaryProtonTrackLength",
		                                      "CalibEClustsPrimaryProtonEnd","PrimaryProtonTfromdEdx",
		                                      "TotalPrimaryProtonEnergydEdxAndClusters","PrimaryProtonTrueKE",
		                                      "EnergyDiffTruedEdx","PrimaryProtonFractionEnergyInCone",
		                                      "Q2QE","EnuCCQE","ptmu","pzmu" };
		std::vector<std::string> ytitles = { "Counts","Counts","Counts/mm","Counts/MeV","Counts/MeV","Counts/MeV",
		                                     "Counts/MeV","Counts/MeV","Counts","Counts/GeV^2","Counts/GeV",
		                                     "Counts/GeV","Counts/GeV" };
		std::vector<bool> binwidthnorm = { false,false,true,true,true,true,true,true,false,true,true,true,true };
		std::vector<bool> dolog = { false,true,false,true,false,false,false,false,true,false,false,false,false };
		double yscale = 1.2;
		std::string rootfilename;
		std::vector<std::string> samples;
		std::string rootfilename2;
		std::vector<std::string> samples2;
		std::string title;
		std::string tag;
	
		if(argument == 3){
			rootfilename = "SB_NuConfig_primaryprotonPass_me1N_1.root";
			samples = { "QElike_Pass_NoSec","QElike_PassTrue","QElike_PassPi","QElike" };
			title = "Passes Proton Score Cut, 2+ tracks";
			tag = "Pass";
		}
		else if(argument == 4){
			rootfilename = "SB_NuConfig_primaryprotonFail_me1N_1.root";
			samples = { "QElike_Fail_NoSec","QElike_FailTrue","QElike_FailPi","QElike_FailOther" };
			title = "Fails Proton Score Cut, 2+ tracks";
			tag = "Fails";
		}
		else if(argument == 5){
			rootfilename = "SB_NuConfig_primaryprotonCombined_me1N_1.root";
			samples = { "QElike_noProtonCuts2","QElike_True","QElike_Pi","QElike_Other" };
			title = "No Proton Score Cuts, 2+ tracks";
			tag = "Combined";
		}
		
		TFile *infile = new TFile(Form(rootfilename.c_str()));
		
		for ( int i=0; i<varnames.size(); i++ ) {
		
			std::cout << std::endl << " plotting " << varnames[i];
		 
			TCanvas *c1 = new TCanvas(varnames[i].c_str(),varnames[i].c_str());
			c1->SetLeftMargin(0.15);
			c1->SetRightMargin(0.1);
			c1->SetBottomMargin(0.15);
			c1->SetTopMargin(0.1);
			
			MnvH1D *prot = (MnvH1D*)infile->Get(Form("h___%s___qelike___%s___reconstructed",samples[1].c_str(),varnames[i].c_str()));
			MnvH1D *pion = (MnvH1D*)infile->Get(Form("h___%s___qelike___%s___reconstructed",samples[2].c_str(),varnames[i].c_str()));
			MnvH1D *other = (MnvH1D*)infile->Get(Form("h___%s___qelike___%s___reconstructed",samples[3].c_str(),varnames[i].c_str()));
			MnvH1D *data = (MnvH1D*)infile->Get(Form("h___%s___data___%s___reconstructed",samples[0].c_str(),varnames[i].c_str()));

			prot->SetFillColor(TColor::GetColor(0,133,173));//kBlue-7);
			pion->SetFillColor(TColor::GetColor(234,170,0));//kGreen-3);
			other->SetFillColor(TColor::GetColor(82,37,6));//kOrange);
			
			prot->SetFillStyle(3001);
			pion->SetFillStyle(3001);
			other->SetFillStyle(3001);
			
			prot->SetLineColor(TColor::GetColor(0,133,173));//kBlue-7);
			pion->SetLineColor(TColor::GetColor(234,170,0));//kGreen-3);
			other->SetLineColor(TColor::GetColor(82,37,6));//kOrange);
			
			MnvH1D *h_pot = (MnvH1D*)infile->Get("POT_summary");
			double dataPOT = h_pot->GetBinContent(1);
			double mcPOTprescaled = h_pot->GetBinContent(3);
			double POTScale = dataPOT/mcPOTprescaled;
			delete h_pot;
			
			prot->Scale(POTScale);
			pion->Scale(POTScale);
			other->Scale(POTScale);
			
			if(binwidthnorm[i]){
				prot->Scale(1.0,"width");
				pion->Scale(1.0,"width");
				other->Scale(1.0,"width");
				data->Scale(1.0,"width");
			}
			
			THStack *hs = new THStack();
			hs->Add(new TH1D(other->GetCVHistoWithError()));
			hs->Add(new TH1D(pion->GetCVHistoWithError()));
			hs->Add(new TH1D(prot->GetCVHistoWithError()));
			
			//data->GetXaxis()->SetTitle(xtitle.c_str());
			data->GetYaxis()->SetTitle(ytitles[i].c_str());
			data->GetXaxis()->SetTitleOffset(1.2);
		  data->GetYaxis()->SetTitleOffset(1.3);
			data->SetTitle(title.c_str());
			data->SetStats(0);
			applyStyle(data);
			
			TLegend *leg = new TLegend(0.62,0.6,0.89,0.89);
			leg->SetFillColor(kWhite);
			leg->AddEntry(data,"MINERvA Data","p");
			leg->AddEntry(prot,"proton","F");
			leg->AddEntry(pion,"#pi^{+/-}","F");
			leg->AddEntry(other,"other","F");
			
			data->Draw("PE1");
			hs->Draw("HISTSAME");
			data->Draw("PE1SAME");
			dolog[i]?data->GetYaxis()->SetRangeUser(0.1,yscale*data->GetBinContent(data->GetMaximumBin())):data->GetYaxis()->SetRangeUser(0,yscale*data->GetBinContent(data->GetMaximumBin()));
			leg->Draw("SAME");
			if(dolog[i]) c1->SetLogy(true);
			gPad->RedrawAxis();
			
			c1->Print(Form("%s_%s.png",tag.c_str(),varnames[i].c_str()));
		}
	}/*
	else if(argument == 6 || argument == 7 || argument == 8) {
		
		std::vector<std::string> varnames = { "PrimaryProtonScore_Q2QEsimplebin", "PrimaryProtonScore_ptmu",
		                                      "PrimaryProtonScore_pzmu","PrimaryProtonScore_NumClustsPrimaryProtonEnd",
		                                      "PrimaryProtonScore_EnergyDiffTruedEdx","PrimaryProtonScore_PrimaryProtonTrackLength",
		                                      "PrimaryProtonTrueKE_TotalPrimaryProtonEnergydEdxAndClusters" };
		std::vector<bool> binwidthnorm = { false,false,false,false,false,false,true };
		std::vector<bool> dolog = { false,false,false,false,false,false,false };
		std::vector<std::string> ytitles = { "Counts","Counts","Counts","Counts","Counts","Counts","Counts/MeV" };
		std::string rootfilename;
		std::vector<std::string> samples;
		int yscale = 1.2;
		std::string tag;
		std::string title;
		                                      
		if(argument == 6){
			rootfilename = "SB_NuConfig_primaryprotonPass_me1N_1.root";
			samples = { "QElike_Pass_NoSec","QElike_PassTrue","QElike_PassPi","QElike" };
			title = "Passes Proton Score Cut, 2+ tracks";
			tag = "Pass";
		}
		else if(argument == 7){
			rootfilename = "SB_NuConfig_primaryprotonFail_me1N_1.root";
			samples = { "QElike_Fail_NoSec","QElike_FailTrue","QElike_FailPi","QElike_FailOther" };
			title = "Fails Proton Score Cut, 2+ tracks";
			tag = "Fails";
		}
		else if(argument == 8){
			rootfilename = "SB_NuConfig_primaryprotonCombined_me1N_1.root";
			samples = { "QElike_NoSec","QElike_True","QElike_Pi","QElike_Other" };
			title = "No Proton Score Cuts, 2+ tracks";
			tag = "Combined";
		}
		
		TFile *infile = new TFile(Form(rootfilename.c_str()));
		
		std::cout << "Check 1\n";
		
		for ( int i=0; i<varnames.size(); i++ ) {
		
			MnvH2D *prot2d = (MnvH2D*)infile->Get(Form("h2___%s___qelike___%s___reconstructed",samples[1].c_str(),varnames[i].c_str()));
			std::cout << "Check " << i+2 << "\n";
			int ny = prot2d->GetNbinsY();
			std::cout << "Check " << i+3 << "\n";
			int dy = (int)(floor(ny/10));
			
			std::cout << "Check " << i+4 << "\n";
			
			for( int j=1; j<ny; j++ ) {
			
				int k = j+dy;
				if(k>ny) k = ny;
				
				TCanvas *c1 = new TCanvas(varnames[i].c_str(),varnames[i].c_str());
				c1->SetLeftMargin(0.15);
				c1->SetRightMargin(0.1);
				c1->SetBottomMargin(0.15);
				c1->SetTopMargin(0.1);
			
				MnvH1D *prot = (MnvH1D*)((MnvH2D*)infile->Get(Form("h2___%s___qelike___%s___reconstructed",samples[1].c_str(),varnames[i].c_str())))->ProjectionX("prot",j,k);
				MnvH1D *pion = (MnvH1D*)((MnvH2D*)infile->Get(Form("h2___%s___qelike___%s___reconstructed",samples[2].c_str(),varnames[i].c_str())))->ProjectionX("pion",j,k);
				MnvH1D *other = (MnvH1D*)((MnvH2D*)infile->Get(Form("h2___%s___qelike___%s___reconstructed",samples[3].c_str(),varnames[i].c_str())))->ProjectionX("other",j,k);
				MnvH1D *data = (MnvH1D*)((MnvH2D*)infile->Get(Form("h2___%s___qelike___%s___reconstructed",samples[0].c_str(),varnames[i].c_str())))->ProjectionX("data",j,k);
				
				prot->SetFillColor(kBlue-7);
				pion->SetFillColor(kGreen-3);
				other->SetFillColor(kOrange);
				
				prot->SetFillStyle(3001);
				pion->SetFillStyle(3001);
				other->SetFillStyle(3001);
				
				prot->SetLineColor(kBlue-7);
				pion->SetLineColor(kGreen-3);
				other->SetLineColor(kOrange);
				
				MnvH1D *h_pot = (MnvH1D*)infile->Get("POT_summary");
				double dataPOT = h_pot->GetBinContent(1);
				double mcPOTprescaled = h_pot->GetBinContent(3);
				double POTScale = dataPOT/mcPOTprescaled;
				delete h_pot;
				
				prot->Scale(POTScale);
				pion->Scale(POTScale);
				other->Scale(POTScale);
				
				if(binwidthnorm[i]) {
					prot->Scale(1.0,"width");
					pion->Scale(1.0,"width");
					other->Scale(1.0,"width");
					data->Scale(1.0,"width");
				}
				
				THStack *hs = new THStack();
				hs->Add(new TH1D(other->GetCVHistoWithError()));
				hs->Add(new TH1D(pion->GetCVHistoWithError()));
				hs->Add(new TH1D(prot->GetCVHistoWithError()));
				
				//data->GetXaxis()->SetTitle(xtitle.c_str());
				data->GetYaxis()->SetTitle(ytitles[i].c_str());
				data->GetXaxis()->SetTitleOffset(1.2);
				data->GetYaxis()->SetTitleOffset(1.3);
				//data->SetTitle(title.c_str());
				data->SetStats(0);
				applyStyle(data);
				
				TLegend *leg = new TLegend(0.62,0.6,0.89,0.89);
				leg->SetFillColor(kWhite);
				leg->AddEntry(data,"MINERvA Data","p");
				leg->AddEntry(prot,"proton","F");
				leg->AddEntry(pion,"#pi^{+/-}","F");
				leg->AddEntry(other,"other","F");
				
				data->Draw("PE1");
				hs->Draw("HISTSAME");
				data->Draw("PE1SAME");
				dolog[i]?data->GetYaxis()->SetRangeUser(0.1,yscale*data->GetBinContent(data->GetMaximumBin())):data->GetYaxis()->SetRangeUser(0,yscale*data->GetBinContent(data->GetMaximumBin()));
				leg->Draw("SAME");
				if(dolog[i]) c1->SetLogy(true);
				gPad->RedrawAxis();
				
				c1->Print(Form("%s_%s.png",tag.c_str(),varnames[i].c_str()));
				
			}
		}
		
	}*/
   
	exit(0);
}

