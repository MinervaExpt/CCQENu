#include <iostream>
#include <string>
#include "TFile.h"
#include "TVector2.h"
#include "PlotUtils/MnvH1D.h"
#include "PlotUtils/MnvH2D.h"

using namespace PlotUtils;

int main(const int argc, const char *argv[]) {

	std::string sample = std::string(argv[1]);

	TFile *file1 = new TFile(Form("%s_GENIE1.root",sample.c_str()));
	TFile *file2 = new TFile(Form("%s_GENIE2.root",sample.c_str()));
	TFile *file3 = new TFile(Form("%s_GENIE.root",sample.c_str()),"RECREATE");
	
	// TVector2 pot
	TVector2 *pot1 = (TVector2*) file1->Get("pot");
	TVector2 *pot2 = (TVector2*) file2->Get("pot");
	double X1 = pot1->X();
	double Y1 = pot1->Y();
	double X2 = pot2->X();
	double Y2 = pot2->Y();
	TVector2 *pot = new TVector2(X1+X2,Y1+Y2);
	
	std::cout << std::endl << "Data POT = " << X1 << " + " << X2 << " = " << X1+X2;
	std::cout << std::endl << "MC POT   = " << Y1 << " + " << Y2 << " = " << Y1+Y2 << std::endl;
	
	file3->WriteObject(pot,"pot");
	
	// Combine Histograms
	for(auto key : *(file1->GetListOfKeys())){
		std::string name = key->GetName();
		if(name.find("_") > name.size()) { // Only histograms contain "_"s
			continue;
		}
		else if(file2->FindKey(name.c_str()) == 0) {
			continue;
		}
		else if(name.find("migration") > name.size()) {
			MnvH1D *h1 = (MnvH1D*)file1->Get(name.c_str());
			MnvH1D *h2 = (MnvH1D*)file2->Get(name.c_str());
			MnvH1D *h3 = (MnvH1D*)h1->Clone();
			h3->Add(h2);
			file3->WriteObject(h3,name.c_str());
		}
		else {
			MnvH2D *h1 = (MnvH2D*)file1->Get(name.c_str());
			MnvH2D *h2 = (MnvH2D*)file2->Get(name.c_str());
			MnvH2D *h3 = (MnvH2D*)h1->Clone();
			h3->Add(h2);
			file3->WriteObject(h3,name.c_str());
		}
	}
}

