#include <vector>
#include <string>
#include "TFile.h"
#include "TDirectory.h"
#include "TColor.h"
#include "TGraph.h"
#include "TCanvas.h"
#include "TMultiGraph.h"
#include "TLegend.h"
#include "TAxis.h"

int main()
{
	std::vector<std::string> tags = {"multipion_bdt_2track"};//{"1track","2track"};//}{"1track","2track","3ptrack"};
	std::vector<std::string> title_tags = {"Multipion 2 tracks"};//{"1 track","2 tracks"};//{"1 track","2 tracks","3+ tracks"};
	//std::vector<int> ntrees = {100,200,300,500,1000};
	std::vector<int> ntrees = {100};
	std::vector<std::string> learnrate = {"5"};
	

	for (int i=0; i<tags.size(); i++) {
		for (int j=0; j<ntrees.size(); j++) {
			for (int k=0; k<learnrate.size(); k++) {
				//std::string fname = "Multiclassed_"+tags[i]+"_MAD_mc_me1N_TMVA_"+std::to_string(ntrees[j])+"_learnrate0dot"+learnrate[k]+".root";
				std::string fname = "TMVAC.root";
				TFile *f = TFile::Open(fname.c_str(),"READONLY");

				TDirectory *dir1 = (TDirectory*)f->Get("dataset");
				TDirectory *dir2 = (TDirectory*)dir1->Get("Method_BDT");
				TDirectory *dir3 = (TDirectory*)dir2->Get("BDTG");
				TDirectory *dir4 = (TDirectory*)dir2->Get("BDT");

				TCanvas *c1 = new TCanvas("c1","ROC Curves",200,10,1200,800);
				c1->SetGrid();
				c1->DrawFrame(0., 0., 1., 1.);
				TMultiGraph *mg = new TMultiGraph();
				/*std::string title = "ROC Curves - "+title_tags[i]+" - "+std::to_string(ntrees[j])+" Trees - Learning Rate=0."+learnrate[k];
				mg->SetTitle(title.c_str());
				mg->GetXaxis()->SetTitle("Signal efficiency (Sensitivity)");
				mg->GetXaxis()->SetTitleSize(0.05);
				mg->GetYaxis()->SetTitle("Background rejection (Specificity)");
				mg->GetYaxis()->SetTitleSize(0.05);*/

				/*TGraph *qelike = (TGraph*)dir3->Get("MVA_BDTG_Test_rejBvsS_qelike");
				TGraph *chargedpion = (TGraph*)dir3->Get("MVA_BDTG_Test_rejBvsS_1chargedpion");
				TGraph *neutralpion = (TGraph*)dir3->Get("MVA_BDTG_Test_rejBvsS_1neutralpion");
				TGraph *multipion = (TGraph*)dir3->Get("MVA_BDTG_Test_rejBvsS_multipion");
				TGraph *other = (TGraph*)dir3->Get("MVA_BDTG_Test_rejBvsS_other");*/
				
				TGraph *bdtg = (TGraph*)dir3->Get("MVA_BDTG_rejBvsS");
				TGraph *bdt = (TGraph*)dir4->Get("MVA_BDT_rejBvsS");
				
				//bdtg->GetYaxis()->SetLimits(0.,1.);
				//bdt->GetYaxis()->SetLimits(0.,1.);
				
				/*bdtg->GetHistogram()->SetMinimum(0);
				bdtg->GetHistogram()->SetMaximum(1);
				bdt->GetHistogram()->SetMinimum(0);
				bdt->GetHistogram()->SetMaximum(1);*/

				/*qelike->SetLineColor(TColor::GetColor(0,133,173));
				chargedpion->SetLineColor(TColor::GetColor(175,39,47));
				neutralpion->SetLineColor(TColor::GetColor(76,140,43));
				multipion->SetLineColor(TColor::GetColor(234,170,0));
				other->SetLineColor(TColor::GetColor(82,37,6));*/
				
				bdtg->SetLineColor(TColor::GetColor(0,133,173));
				bdt->SetLineColor(TColor::GetColor(175,39,47));

				/*qelike->SetLineWidth(2);
				chargedpion->SetLineWidth(2);
				neutralpion->SetLineWidth(2);
				multipion->SetLineWidth(2);
				other->SetLineWidth(2);*/
				
				bdtg->SetLineWidth(2);
				bdt->SetLineWidth(2);
				
				bdtg->SetLineStyle(1);
				bdt->SetLineStyle(1);

				/*mg->Add(qelike);
				mg->Add(chargedpion);
				mg->Add(neutralpion);
				mg->Add(multipion);
				mg->Add(other);*/
				
				//mg->Add(bdtg);
				mg->Add(bdt);

				//mg->Draw("AL");
				mg->Draw();

				/*auto legend = new TLegend(0.15,0.15,0.55,0.55);
				legend->SetTextSize(0.04);
				legend->SetBorderSize(0);
				legend->SetHeader("Signal/Background vs Rest","C"); // option "C" allows to center the header
				legend->AddEntry(qelike,"QELike","l");
				legend->AddEntry(chargedpion,"Single #pi^{+/-}","l");
				legend->AddEntry(neutralpion,"Single #pi^{0}","l");
				legend->AddEntry(multipion,"N#pi","l");
				legend->AddEntry(other,"Other","l");
				legend->Draw();*/

				std::string cfile = "ROCC_MAD_"+tags[i]+"_"+std::to_string(ntrees[j])+"_0dot"+learnrate[k]+".C";
				std::string pngfile = "ROCC_MAD_"+tags[i]+"_"+std::to_string(ntrees[j])+"_0dot"+learnrate[k]+".png";
				c1->SaveAs(cfile.c_str());
				c1->SaveAs(pngfile.c_str());
				
				delete c1;
			}
		}
	}
	
	return 0;
}
