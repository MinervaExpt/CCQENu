#include <iostream>
#include <string>
#include "TFile.h"
#include "PlotUtils/MnvH1D.h"
#include "utils/SyncBands.h"

using namespace PlotUtils;

int main(const int argc, const char *argv[]) {

	std::string sample = std::string(argv[1]);
	std::vector<std::string> vars1D = {"zvtx","pzmu","ptmu","Q2QE","bdtgQELike","bdtg1ChargedPion","bdtg1NeutralPion","bdtgMultiPion","bdtgOther"};

	TFile *file1 = new TFile(Form("%s_1.root",sample.c_str()));
	TFile *file2 = new TFile(Form("%s_2.root",sample.c_str()));
	TFile *file3 = new TFile(Form("%s_3.root",sample.c_str()));
	TFile *file4 = new TFile(Form("%s_4.root",sample.c_str()));
	TFile *file5 = new TFile(Form("%s_5.root",sample.c_str()),"RECREATE");

	for ( int i=0; i<vars1D.size(); i++ ) {

		MnvH1D *qe1 = (MnvH1D*)file1->Get(Form("h___%s___qelike___%s___reconstructed",sample.c_str(),vars1D[i].c_str()));
		MnvH1D *sch1 = (MnvH1D*)file1->Get(Form("h___%s___1chargedpion___%s___reconstructed",sample.c_str(),vars1D[i].c_str()));
		MnvH1D *snu1 = (MnvH1D*)file1->Get(Form("h___%s___1neutralpion___%s___reconstructed",sample.c_str(),vars1D[i].c_str()));
		MnvH1D *multi1 = (MnvH1D*)file1->Get(Form("h___%s___multipion___%s___reconstructed",sample.c_str(),vars1D[i].c_str()));
		MnvH1D *other1 = (MnvH1D*)file1->Get(Form("h___%s___other___%s___reconstructed",sample.c_str(),vars1D[i].c_str()));
		MnvH1D *data1 = (MnvH1D*)file1->Get(Form("h___%s___data___%s___reconstructed",sample.c_str(),vars1D[i].c_str()));

		MnvH1D *qe2 = (MnvH1D*)file2->Get(Form("h___%s___qelike___%s___reconstructed",sample.c_str(),vars1D[i].c_str()));
		MnvH1D *sch2 = (MnvH1D*)file2->Get(Form("h___%s___1chargedpion___%s___reconstructed",sample.c_str(),vars1D[i].c_str()));
		MnvH1D *snu2 = (MnvH1D*)file2->Get(Form("h___%s___1neutralpion___%s___reconstructed",sample.c_str(),vars1D[i].c_str()));
		MnvH1D *multi2 = (MnvH1D*)file2->Get(Form("h___%s___multipion___%s___reconstructed",sample.c_str(),vars1D[i].c_str()));
		MnvH1D *other2 = (MnvH1D*)file2->Get(Form("h___%s___other___%s___reconstructed",sample.c_str(),vars1D[i].c_str()));
		MnvH1D *data2 = (MnvH1D*)file2->Get(Form("h___%s___data___%s___reconstructed",sample.c_str(),vars1D[i].c_str()));

		MnvH1D *qe3 = (MnvH1D*)file3->Get(Form("h___%s___qelike___%s___reconstructed",sample.c_str(),vars1D[i].c_str()));
		MnvH1D *sch3 = (MnvH1D*)file3->Get(Form("h___%s___1chargedpion___%s___reconstructed",sample.c_str(),vars1D[i].c_str()));
		MnvH1D *snu3 = (MnvH1D*)file3->Get(Form("h___%s___1neutralpion___%s___reconstructed",sample.c_str(),vars1D[i].c_str()));
		MnvH1D *multi3 = (MnvH1D*)file3->Get(Form("h___%s___multipion___%s___reconstructed",sample.c_str(),vars1D[i].c_str()));
		MnvH1D *other3 = (MnvH1D*)file3->Get(Form("h___%s___other___%s___reconstructed",sample.c_str(),vars1D[i].c_str()));
		MnvH1D *data3 = (MnvH1D*)file3->Get(Form("h___%s___data___%s___reconstructed",sample.c_str(),vars1D[i].c_str()));
		
		MnvH1D *qe4 = (MnvH1D*)file4->Get(Form("h___%s___qelike___%s___reconstructed",sample.c_str(),vars1D[i].c_str()));
		MnvH1D *sch4 = (MnvH1D*)file4->Get(Form("h___%s___1chargedpion___%s___reconstructed",sample.c_str(),vars1D[i].c_str()));
		MnvH1D *snu4 = (MnvH1D*)file4->Get(Form("h___%s___1neutralpion___%s___reconstructed",sample.c_str(),vars1D[i].c_str()));
		MnvH1D *multi4 = (MnvH1D*)file4->Get(Form("h___%s___multipion___%s___reconstructed",sample.c_str(),vars1D[i].c_str()));
		MnvH1D *other4 = (MnvH1D*)file4->Get(Form("h___%s___other___%s___reconstructed",sample.c_str(),vars1D[i].c_str()));
		MnvH1D *data4 = (MnvH1D*)file4->Get(Form("h___%s___data___%s___reconstructed",sample.c_str(),vars1D[i].c_str()));

		qe1->GetErrorBandNames();
		qe2->GetErrorBandNames();
		qe3->GetErrorBandNames();
		qe4->GetErrorBandNames();

		qe1->TransferErrorBands(qe2,false);
		sch1->TransferErrorBands(sch2,false);
		snu1->TransferErrorBands(snu2,false);
		multi1->TransferErrorBands(multi2,false);
		other1->TransferErrorBands(other2,false);

		qe2->TransferErrorBands(qe3,false);
		sch2->TransferErrorBands(sch3,false);
		snu2->TransferErrorBands(snu3,false);
		multi2->TransferErrorBands(multi3,false);
		other2->TransferErrorBands(other3,false);
		
		qe3->TransferErrorBands(qe4,false);
		sch3->TransferErrorBands(sch4,false);
		snu3->TransferErrorBands(snu4,false);
		multi3->TransferErrorBands(multi4,false);
		other3->TransferErrorBands(other4,false);

		MnvH1D *qe5 = (MnvH1D*)qe4->Clone();
		MnvH1D *sch5 = (MnvH1D*)sch4->Clone();
		MnvH1D *snu5 = (MnvH1D*)snu4->Clone();
		MnvH1D *multi5 = (MnvH1D*)multi4->Clone();
		MnvH1D *other5 = (MnvH1D*)other4->Clone();
		MnvH1D *data5 = (MnvH1D*)data4->Clone();
		
		SyncBands(qe5);
		SyncBands(sch5);
		SyncBands(snu5);
		SyncBands(multi5);
		SyncBands(other5);

		file5->WriteObject(qe5,Form("h___%s___qelike___%s___reconstructed",sample.c_str(),vars1D[i].c_str()));
		file5->WriteObject(sch5,Form("h___%s___1chargedpion___%s___reconstructed",sample.c_str(),vars1D[i].c_str()));
		file5->WriteObject(snu5,Form("h___%s___1neutralpion___%s___reconstructed",sample.c_str(),vars1D[i].c_str()));
		file5->WriteObject(multi5,Form("h___%s___multipion___%s___reconstructed",sample.c_str(),vars1D[i].c_str()));
		file5->WriteObject(other5,Form("h___%s___other___%s___reconstructed",sample.c_str(),vars1D[i].c_str()));
		file5->WriteObject(data5,Form("h___%s___data___%s___reconstructed",sample.c_str(),vars1D[i].c_str()));

	}
	
	TH1F* pot_summary1 = (TH1F*) file1->Get("POT_summary");
	TH1F* pot_summary5 = (TH1F*)pot_summary1->Clone();
	file5->WriteObject(pot_summary5,"POT_summary");
	
	file5->Close();
}
