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

using namespace PlotUtils;

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
  
  std::string rootfilename = std::string(argv[1]);
  //std::string sample = std::string(argv[2]);
  std::string sample = "2track";
  
  double yscale = 1.2;
	
	std::cout << std::endl << "Opening file " << rootfilename;
	TFile *infile = new TFile(Form(rootfilename.c_str()));
	
	std::cout << std::endl << "Opening 2D histograms:";
	std::cout << std::endl << Form("  h2D___%s___qelike___bdtgQELike_Q2QE___reconstructed",sample.c_str());
	std::cout << std::endl << Form("  h2D___%s___1chargedpion___bdtgQELike_Q2QE___reconstructed",sample.c_str());
	std::cout << std::endl << Form("  h2D___%s___multipion___bdtgQELike_Q2QE___reconstructed",sample.c_str());
	std::cout << std::endl << Form("  h2D___%s___other1neutralpion___bdtgQELike_Q2QE___reconstructed",sample.c_str());
	std::cout << std::endl << Form("  h2D___%s___data___bdtgQELike_Q2QE___reconstructed",sample.c_str());
	
	MnvH2D *h2D_qe = (MnvH2D*)infile->Get(Form("h2D___%s___qelike___bdtgQELike_Q2QE___reconstructed",sample.c_str()));
	MnvH2D *h2D_sch = (MnvH2D*)infile->Get(Form("h2D___%s___1chargedpion___bdtgQELike_Q2QE___reconstructed",sample.c_str()));
	MnvH2D *h2D_multi = (MnvH2D*)infile->Get(Form("h2D___%s___multipion___bdtgQELike_Q2QE___reconstructed",sample.c_str()));
	MnvH2D *h2D_other = (MnvH2D*)infile->Get(Form("h2D___%s___other1neutralpion___bdtgQELike_Q2QE___reconstructed",sample.c_str()));
	MnvH2D *h2D_data = (MnvH2D*)infile->Get(Form("h2D___%s___data___bdtgQELike_Q2QE___reconstructed",sample.c_str()));
	//MnvH1D *h2D_snu = (MnvH1D*)infile->Get(Form("h2D___%s___1neutralpion___%s___reconstructed",sample.c_str(),vars1D[i].c_str()));

	nbins = h2D_data->GetNbinsY();
	
	std::cout << std::endl << "Begin looping over Q2QE bins";

	int i=1;
	//for (int i=1; i<=nbins; i++) {

	std::cout << std::endl << "Projecting bin " << i;
	TH2D h_qe = h2D_qe->GetCVHistoWithError();
	TH2D h_sch = h2D_sch->GetCVHistoWithError();
	TH2D h_multi = h2D_multi->GetCVHistoWithError();
	TH2D h_other = h2D_other->GetCVHistoWithError();
	TH2D h_dat = h2D_data->GetCVHistoWithError();
	
	TH1D *qe = h_qe.ProjectionX("",i,i,"");
	TH1D *sch = h_sch.ProjectionX("",i,i,"");
	TH1D *multi = h_multi.ProjectionX("",i,i,"");
	TH1D *other = h_other.ProjectionX("",i,i,"");
	TH1D *dat = h_dat.ProjectionX("",i,i,"");
	
	/*TH1D *qe = h2D_qe->GetCVHistoWithError()->Projection("",1,i,i,"");
	TH1D *sch = h2D_sch->GetCVHistoWithError()->Projection("",1,i,i,"");
	TH1D *multi = h2D_multi->GetCVHistoWithError()->Projection("",1,i,i,"");
	TH1D *other = h2D_other->GetCVHistoWithError()->Projection("",1,i,i,"");
	TH1D *dat = h2D_data->GetCVHistoWithError()->Projection("",1,i,i,"");
	*/
	double low = dat->GetXaxis()->GetBinLowEdge(i);
	double high = dat->GetXaxis()->GetBinLowEdge(i+1);
	
	std::cout << std::endl << "Creating Canvas";
	TCanvas *c1 = new TCanvas("bdtgQELike","bdtgQELike");
	c1->SetLeftMargin(0.15);
	c1->SetRightMargin(0.1);
	c1->SetBottomMargin(0.15);
	c1->SetTopMargin(0.1);
	
	std::cout << std::endl << "Setting fill colors";
	qe->SetFillColor(TColor::GetColor(0,133,173));//kMagenta-4);
	sch->SetFillColor(TColor::GetColor(175,39,47));//kBlue-7);
	multi->SetFillColor(TColor::GetColor(234,170,0));//kRed-4);
	other->SetFillColor(TColor::GetColor(76,140,43));//kGreen-3);
	dat->SetFillColor(TColor::GetColor(255,255,255));
	//snu->SetFillColor(TColor::GetColor(76,140,43));//kGreen-3);
	//other->SetFillColor(TColor::GetColor(82,37,6));//kBlack);

	std::cout << std::endl << "Setting fill styles";
	qe->SetFillStyle(3001);
	sch->SetFillStyle(3001);
	multi->SetFillStyle(3001);
	other->SetFillStyle(3001);
	//snu->SetFillStyle(3001);
	
	std::cout << std::endl << "Setting line colors";
	qe->SetLineColor(TColor::GetColor(0,133,173));//kMagenta-4);
	sch->SetLineColor(TColor::GetColor(175,39,47));//Blue-7);
	other->SetLineColor(TColor::GetColor(76,140,43));//kGreen-3);
	multi->SetLineColor(TColor::GetColor(234,170,0));//kRed-4);
	dat->SetLineColor(TColor::GetColor(255,255,255));
	//snu->SetLineColor(TColor::GetColor(76,140,43));//kGreen-3);
	//other->SetLineColor(TColor::GetColor(82,37,6));//kBlack);
	/*
	double data_integral = data->Integral();
	double mc_integral = qe->Integral() + sch->Integral() + snu->Integral() +
		                   multi->Integral() + other->Integral();
	double integral_scale = data_integral/mc_integral;
	
	qe->Scale(integral_scale);
	sch->Scale(integral_scale);
	snu->Scale(integral_scale);
	multi->Scale(integral_scale);
	other->Scale(integral_scale);
	*/
	/*
	qe->Scale(1.0,"width");
	sch->Scale(1.0,"width");
	//snu->Scale(1.0,"width");
	multi->Scale(1.0,"width");
	other->Scale(1.0,"width");
	data->Scale(1.0,"width");
	*/
	
	int nbinsX = h2D_data->GetNbinsX();
	for( int i=0; i<=nbinsX; i++ ){
		dat->SetBinContent(i,0.);
	}
	
	std::cout << std::endl << "Stacking hists";
	THStack *hs = new THStack();
	/*
	std::cout << std::endl << " Adding other";
	hs->Add(new TH1D(other->GetCVHistoWithError()));
	std::cout << std::endl << " Adding multipion";
	hs->Add(new TH1D(multi->GetCVHistoWithError()));
	std::cout << std::endl << " Adding 1chargedpion";
	//hs->Add(new TH1D(snu->GetCVHistoWithError()));
	hs->Add(new TH1D(sch->GetCVHistoWithError()));
	std::cout << std::endl << " Adding qelike";
	hs->Add(new TH1D(qe->GetCVHistoWithError()));
	*/
	
	std::cout << std::endl << " Adding other";
	hs->Add(other);
	std::cout << std::endl << " Adding multipion";
	hs->Add(multi);
	std::cout << std::endl << " Adding 1chargedpion";
	hs->Add(sch);
	std::cout << std::endl << " Adding qelike";
	hs->Add(qe);
	
	//std::cout << std::endl << "Figuring out y axis range";
	//int hs_max = hs->GetMaximum();
	//double data_max = dat->GetMaximum();
	//double hist_max = hs_max;
	//if (data_max > hs_max) {
	//	hist_max = data_max;
	//}
	
	std::cout << std::endl << "Setting titles";
	dat->GetYaxis()->SetTitle("Events");
	dat->SetTitle(Form("BDTG QELike for %s events for %d <= Q2QE < %d",sample.c_str(),low,high));
	dat->SetStats(0);
	//applyStyle(dat);
	
	std::cout << std::endl << "Creating legend";
	TLegend *leg = new TLegend(0.62,0.6,0.89,0.89);
	leg->SetFillColor(kWhite);
	leg->AddEntry(qe,"QELike","F");
	leg->AddEntry(sch,"Single #pi^{+/-} in FS","F");
	//leg->AddEntry(snu,"Single #pi^{0} in FS","F");
	leg->AddEntry(multi,"N#pi in FS","F");
	leg->AddEntry(other,"Other","F");
	/*
	double xmax = dat->GetXaxis()->GetBinUpEdge(dat->GetNbinsX());
	double xmin = dat->GetXaxis()->GetBinLowEdge(1);
	double xdel = xmax-xmin;
	double xtext = xmin+0.35*xdel;
	double ytext = dat->GetMaximum();
	
	TLatex *text = new TLatex(xtext,0.98*ytext,"Work in progress");
	text->SetTextAlign(13);
	text->SetTextColor(kRed);
	text->SetTextFont(13);
	text->SetTextSize(20);
	*/
	dat->Draw("HIST");
	hs->Draw("HISTSAME");
	//dolog[i]?data->GetYaxis()->SetRangeUser(0.1,yscale*data->GetBinContent(data->GetMaximumBin())):data->GetYaxis()->SetRangeUser(0,yscale*data->GetBinContent(data->GetMaximumBin()));
	leg->Draw("SAME");
	//text->Draw("SAME");
	//if(dolog[i]) c1->SetLogy(true);
	//if(dolog[i]) c1->SetLogx(true);
	gPad->RedrawAxis();			
	
	//c1->Print(Form("%s/1D/%s_%s.png",rootfolder.c_str(),sample.c_str(),vars1D[i].c_str()));
	std::cout << std::endl << "Saving plot";
	c1->Print(Form("%s___bdtgQELike___Q2QE_bin_%d.png",sample.c_str(),i));	
	
	delete c1;
	delete qe;
	delete sch;
	delete multi;
	delete other;
	delete dat;
		
	//}
   
	exit(0);
}

