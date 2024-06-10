#include <iostream>
#include <string>
#include "PlotUtils/MnvH1D.h"
#include "MinervaUnfold/MnvResponse.h"
#include "TH2D.h"
#include "TH1D.h"
#include "TF2.h"
#include "TCanvas.h"
#include "PlotUtils/FluxReweighter.h"
#include <math.h>
#include "TColor.h"
#include "TLatex.h"

int main() {

	std::string rootfilename_old = "SB_NuConfig_mult1pBDTG_me1N_1.root";
	std::string rootfilename_1track = "SB_NuConfig_bdtg_1track_1.root";
	std::string rootfilename_2track = "SB_NuConfig_bdtg_2track_1.root";
	std::string rootfilename_3ptrack = "SB_NuConfig_bdtg_3ptrack_1.root";
	
	std::vector<std::string> variables = {"bdtg1ChargedPion","bdtg1NeutralPion","bdtgMultiPion","bdtgQELike","bdtgOther"};
	std::vector<std::string> samples = {"1track","2track","3ptrack"};
	
	for (auto sample : samples) {
		for ( int i=0; i<variables.size(); i++ ) {
		
			TCanvas *c1 = new TCanvas(Form("qelike_%s_%s", variables[i].c_str(), sample.c_str()),
			                          Form("qelike_%s_%s", variables[i].c_str(), sample.c_str()));
			c1->SetLeftMargin(0.15);
			c1->SetRightMargin(0.1);
			c1->SetBottomMargin(0.15);
			c1->SetTopMargin(0.1);
			
			TCanvas *c2 = new TCanvas(Form("1chargedpion_%s_%s", variables[i].c_str(), sample.c_str()),
			                          Form("1chargedpion_%s_%s", variables[i].c_str(), sample.c_str()));
			c2->SetLeftMargin(0.15);
			c2->SetRightMargin(0.1);
			c2->SetBottomMargin(0.15);
			c2->SetTopMargin(0.1);
			
			TCanvas *c3 = new TCanvas(Form("1neutralpion_%s_%s", variables[i].c_str(), sample.c_str()),
			                          Form("1neutralpion_%s_%s", variables[i].c_str(), sample.c_str()));
			c3->SetLeftMargin(0.15);
			c3->SetRightMargin(0.1);
			c3->SetBottomMargin(0.15);
			c3->SetTopMargin(0.1);
			
			TCanvas *c4 = new TCanvas(Form("multipion_%s_%s", variables[i].c_str(), sample.c_str()),
			                          Form("multipion_%s_%s", variables[i].c_str(), sample.c_str()));
			c4->SetLeftMargin(0.15);
			c4->SetRightMargin(0.1);
			c4->SetBottomMargin(0.15);
			c4->SetTopMargin(0.1);
			
			TCanvas *c5 = new TCanvas(Form("other_%s_%s", variables[i].c_str(), sample.c_str()),
			                          Form("other_%s_%s", variables[i].c_str(), sample.c_str()));
			c5->SetLeftMargin(0.15);
			c5->SetRightMargin(0.1);
			c5->SetBottomMargin(0.15);
			c5->SetTopMargin(0.1);
			
			TCanvas *c6 = new TCanvas(Form("data_%s_%s", variables[i].c_str(), sample.c_str()),
			                          Form("data_%s_%s", variables[i].c_str(), sample.c_str()));
			c6->SetLeftMargin(0.15);
			c6->SetRightMargin(0.1);
			c6->SetBottomMargin(0.15);
			c6->SetTopMargin(0.1);
		
			TFile *rootfile1 = TFile::Open(rootfilename_old.c_str());
			TFile *rootfile2 = TFile::Open(Form("SB_NuConfig_bdtg_%s_1.root",sample.c_str()));
		
			MnvH1D *qe1 = (MnvH1D*)rootfile1->Get(Form("h___Mult1p_%s___qelike___%s___reconstructed",sample.c_str(),variables[i].c_str()));
			MnvH1D *sch1 = (MnvH1D*)rootfile1->Get(Form("h___Mult1p_%s___1chargedpion___%s___reconstructed",sample.c_str(),variables[i].c_str()));
			MnvH1D *snu1 = (MnvH1D*)rootfile1->Get(Form("h___Mult1p_%s___1neutralpion___%s___reconstructed",sample.c_str(),variables[i].c_str()));
			MnvH1D *multi1 = (MnvH1D*)rootfile1->Get(Form("h___Mult1p_%s___multipion___%s___reconstructed",sample.c_str(),variables[i].c_str()));
			MnvH1D *other1 = (MnvH1D*)rootfile1->Get(Form("h___Mult1p_%s___other___%s___reconstructed",sample.c_str(),variables[i].c_str()));
			MnvH1D *data1 = (MnvH1D*)rootfile1->Get(Form("h___Mult1p_%s___data___%s___reconstructed",sample.c_str(),variables[i].c_str()));
			
			MnvH1D *qe2 = (MnvH1D*)rootfile2->Get(Form("h___%s___qelike___%s___reconstructed",sample.c_str(),variables[i].c_str()));
			MnvH1D *sch2 = (MnvH1D*)rootfile2->Get(Form("h___%s___1chargedpion___%s___reconstructed",sample.c_str(),variables[i].c_str()));
			MnvH1D *snu2 = (MnvH1D*)rootfile2->Get(Form("h___%s___1neutralpion___%s___reconstructed",sample.c_str(),variables[i].c_str()));
			MnvH1D *multi2 = (MnvH1D*)rootfile2->Get(Form("h___%s___multipion___%s___reconstructed",sample.c_str(),variables[i].c_str()));
			MnvH1D *other2 = (MnvH1D*)rootfile2->Get(Form("h___%s___other___%s___reconstructed",sample.c_str(),variables[i].c_str()));
			MnvH1D *data2 = (MnvH1D*)rootfile2->Get(Form("h___%s___data___%s___reconstructed",sample.c_str(),variables[i].c_str()));
			
			TH1D *ratio_qe = (TH1D*)qe2->Clone("ratio_qe");
			TH1D *ratio_sch = (TH1D*)sch2->Clone("ratio_sch");
			TH1D *ratio_snu = (TH1D*)snu2->Clone("ratio_snu");
			TH1D *ratio_multi = (TH1D*)multi2->Clone("ratio_multi");
			TH1D *ratio_other = (TH1D*)other2->Clone("ratio_other");
			TH1D *ratio_data = (TH1D*)data2->Clone("ratio_data");
			
			ratio_qe->Divide(qe1);
			ratio_sch->Divide(sch1);
			ratio_snu->Divide(snu1);
			ratio_multi->Divide(multi1);
			ratio_other->Divide(other1);
			ratio_data->Divide(data1);
			
			ratio_qe->SetTitle(Form("%s, %s, qelike", sample.c_str(), variables[i].c_str()));
			ratio_sch->SetTitle(Form("%s, %s, 1chargedpion", sample.c_str(), variables[i].c_str()));
			ratio_snu->SetTitle(Form("%s, %s, 1neutralpion", sample.c_str(), variables[i].c_str()));
			ratio_multi->SetTitle(Form("%s, %s, multipion", sample.c_str(), variables[i].c_str()));
			ratio_other->SetTitle(Form("%s, %s, other", sample.c_str(), variables[i].c_str()));
			ratio_data->SetTitle(Form("%s, %s, data", sample.c_str(), variables[i].c_str()));
			
			c1->cd();
			ratio_qe->Draw();
			c2->cd();
			ratio_sch->Draw();
			c3->cd();
			ratio_snu->Draw();
			c4->cd();
			ratio_multi->Draw();
			c5->cd();
			ratio_other->Draw();
			c6->cd();
			ratio_data->Draw();
			
			c1->Print(Form("ratio_%s_%s.pdf[", variables[i].c_str(), sample.c_str()));
			c1->Print(Form("ratio_%s_%s.pdf", variables[i].c_str(), sample.c_str()),"qelike");
			c2->Print(Form("ratio_%s_%s.pdf", variables[i].c_str(), sample.c_str()),"1chargedpion");
			c3->Print(Form("ratio_%s_%s.pdf", variables[i].c_str(), sample.c_str()),"1neutralpion");
			c4->Print(Form("ratio_%s_%s.pdf", variables[i].c_str(), sample.c_str()),"multipion");
			c5->Print(Form("ratio_%s_%s.pdf", variables[i].c_str(), sample.c_str()),"other");
			c6->Print(Form("ratio_%s_%s.pdf", variables[i].c_str(), sample.c_str()),"data");
			c1->Print(Form("ratio_%s_%s.pdf]", variables[i].c_str(), sample.c_str()));
			
			delete c1;
			delete c2;
			delete c3;
			delete c4;
			delete c5;
			delete c6;
	
		}
	}
	
	exit(0);

}
