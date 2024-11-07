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
	std::vector<std::string> tags = {"1track","2track"};
	std::vector<std::string> title_tags = {"1 track","2 tracks"};
	
	for (int i=0; i<5; i++) {
		std::string fname = "Multiclassed_"+tags[i]+"_minervame1N_MAD_MC_TMVA.root";
		TFile *f = TFile::Open(fname.c_str(),"READONLY");

		TDirectory *dir1 = (TDirectory*)f->Get("dataset");
		TDirectory *dir2 = (TDirectory*)dir1->Get("Method_BDT");
		TDirectory *dir3 = (TDirectory*)dir2->Get("BDTG");

		TCanvas *c1 = new TCanvas("c1","ROC Curves",200,10,1200,800);
		c1->SetGrid();
		TMultiGraph *mg = new TMultiGraph();
		std::string title = "ROC Curves - "+title_tags[i];
		mg->SetTitle(title.c_str());
		mg->GetXaxis()->SetTitle("Signal efficiency (Sensitivity)");
		mg->GetXaxis()->SetTitleSize(0.05);
		mg->GetYaxis()->SetTitle("Background rejection (Specificity)");
		mg->GetYaxis()->SetTitleSize(0.05);

		TGraph *qelike = (TGraph*)dir3->Get("MVA_BDTG_Test_rejBvsS_qelike");
		TGraph *chargedpion = (TGraph*)dir3->Get("MVA_BDTG_Test_rejBvsS_1chargedpion");
		TGraph *neutralpion = (TGraph*)dir3->Get("MVA_BDTG_Test_rejBvsS_1neutralpion");
		TGraph *multipion = (TGraph*)dir3->Get("MVA_BDTG_Test_rejBvsS_multipion");
		TGraph *other = (TGraph*)dir3->Get("MVA_BDTG_Test_rejBvsS_other");

		qelike->SetLineColor(TColor::GetColor(0,133,173));
		chargedpion->SetLineColor(TColor::GetColor(175,39,47));
		neutralpion->SetLineColor(TColor::GetColor(76,140,43));
		multipion->SetLineColor(TColor::GetColor(234,170,0));
		other->SetLineColor(TColor::GetColor(82,37,6));

		qelike->SetLineWidth(2);
		chargedpion->SetLineWidth(2);
		neutralpion->SetLineWidth(2);
		multipion->SetLineWidth(2);
		other->SetLineWidth(2);

		mg->Add(qelike);
		mg->Add(chargedpion);
		mg->Add(neutralpion);
		mg->Add(multipion);
		mg->Add(other);

		mg->Draw("AL");

		auto legend = new TLegend(0.15,0.15,0.55,0.55);
		legend->SetTextSize(0.04);
		legend->SetBorderSize(0);
		legend->SetHeader("Signal/Background vs Rest","C"); // option "C" allows to center the header
		legend->AddEntry(qelike,"QELike","l");
		legend->AddEntry(chargedpion,"Single #pi^{+/-}","l");
		legend->AddEntry(neutralpion,"Single #pi^{0}","l");
		legend->AddEntry(multipion,"N#pi","l");
		legend->AddEntry(other,"Other","l");
		legend->Draw();

		std::string cfile = "ROCC_MAD_"+tags[i]+".C";
		std::string pngfile = "ROCC_MAD_"+tags[i]+".png";
		c1->SaveAs(cfile.c_str());
		c1->SaveAs(pngfile.c_str());
		
		delete c1;
	}
	
	return 0;
}
