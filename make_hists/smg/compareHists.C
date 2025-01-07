#include <iostream>
#include <string>
#include "PlotUtils/MnvH1D.h"
#include "MinervaUnfold/MnvResponse.h"
#include "TCanvas.h"
#include "PlotUtils/FluxReweighter.h"
#include <math.h>
#include "TColor.h"
#include "TLatex.h"
#include "TVector2.h"

using namespace PlotUtils;

int main(const int argc, const char *argv[]) {

	std::string fname1 = std::string(argv[1]);
	std::string fname2 = std::string(argv[2]);
	
	TFile *file1 = new TFile(fname1.c_str());
	TFile *file2 = new TFile(fname1.c_str());
	
	TVector2 *pot1 = (TVector2*) file1->Get("pot");
	TVector2 *pot2 = (TVector2*) file2->Get("pot");
	std::cout << std::endl << fname1 << " POTs:";
	std::cout << std::endl << "   Data POT: " << pot1->X();
	std::cout << std::endl << "   MC POT: " << pot1->Y();
	std::cout << std::endl << fname2 << " POTs:";
	std::cout << std::endl << "   Data POT: " << pot2->X();
	std::cout << std::endl << "   MC POT: " << pot2->Y() << std::endl << std::endl;
	delete pot1;
	delete pot2;
	
	for(auto key : *(file1->GetListOfKeys())){
		std::string name = key->GetName();
		if(name.find("_") > name.size()) { // Only histograms contain "_"s
			continue;
		}
		else if (name.find("migration") < name.size()) {
			continue;
		}
		else {
			
			TCanvas *c1 = new TCanvas(name.c_str(),name.c_str());
			c1->SetLeftMargin(0.15);
			c1->SetRightMargin(0.1);
			c1->SetBottomMargin(0.15);
			c1->SetTopMargin(0.1);
		
			MnvH1D *h1 = (MnvH1D*)file1->Get(name.c_str());
			MnvH1D *h2 = (MnvH1D*)file2->Get(name.c_str());
			
			MnvH1D *diff = (MnvH1D*)h1->Clone("diff");
			diff->Add(h2,-1);
			diff->SetTitle(name.c_str());
			
			c1->cd();
			diff->Draw();
			c1->Print(Form("%s.png",name.c_str()));
			
			delete c1;
			delete diff;
			delete h1;
			delete h2;
		}
	}
	
	delete file1;
	delete file2;
	
	exit(0);
}
