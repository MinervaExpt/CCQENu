#include <iostream>
#include <string>
#include "TFile.h"
#include "PlotUtils/MnvH1D.h"
#include "PlotUtils/MnvH2D.h"
#include "TVector2.h"
#include "utils/SyncBands.h"

using namespace PlotUtils;

int main(const int argc, const char *argv[]) {

	std::string sample = std::string(argv[1]);
	int prescale = std::stoi(argv[2]);
	
	TFile *file1 = new TFile(Form("SB_NuConfig_bdtg_%s_muon_%d.root",sample.c_str(),prescale));
	TFile *file2 = new TFile(Form("SB_NuConfig_bdtg_%s_other_%d.root",sample.c_str(),prescale));
	TFile *file3 = new TFile(Form("SB_NuConfig_bdtg_%s_GENIE_combined_%d.root",sample.c_str(),prescale));
	TFile *file4 = new TFile(Form("SB_NuConfig_bdtg_%s_%d.root",sample.c_str(),prescale),"RECREATE");

	bool first = true;

	for(auto key : *(file1->GetListOfKeys())){
	
		std::string name = key->GetName();
		
		// Determine if histogram will be used; if so, and not first histogram to be used, print name
		if(file2->FindKey(name.c_str()) == 0 ||
		   file3->FindKey(name.c_str()) == 0 ||    // Only combine errors for histograms in all files
		   name.find("___") > name.size()      ) { // Only variable histograms contain "___"s
			continue;
		}
		else if(!first) {
			std::cout << "   " << name << std::endl;
		}
		// Start combining error bands
		if (name.find("migration") == std::string::npos & name.find("h2D") == std::string::npos) { // 1D Histograms
			MnvH1D *h1 = (MnvH1D*)file1->Get(name.c_str());
			MnvH1D *h2 = (MnvH1D*)file2->Get(name.c_str());
			MnvH1D *h3 = (MnvH1D*)file3->Get(name.c_str());
			MnvH1D *h4 = (MnvH1D*)h1->Clone();

			h2->TransferErrorBands(h4,false);
			h3->TransferErrorBands(h4,false);
				
			SyncBands(h4);

			file4->WriteObject(h4,name.c_str());
			
			// On first histogram print the error bands for each file and start histogram list
			std::vector<std::string> h1_error_bands = h1->GetErrorBandNames();	
			if (first & h1_error_bands.size() > 0) {
				std::cout << std::endl << "Error Bands in " << file1->GetName() << ":" << std::endl;
				for ( int i=0; i<h1_error_bands.size(); i++ ) {
					std::cout << "   " << h1_error_bands[i] << std::endl;
				}
				std::vector<std::string> h2_error_bands = h2->GetErrorBandNames();
				std::cout << "Error Bands in " << file2->GetName() << ":" << std::endl;
				for ( int i=0; i<h2_error_bands.size(); i++ ) {
					std::cout << "   " << h2_error_bands[i] << std::endl;
				}
				std::vector<std::string> h3_error_bands = h3->GetErrorBandNames();
				std::cout << "Error Bands in " << file3->GetName() << ":" << std::endl;
				for ( int i=0; i<h3_error_bands.size(); i++ ) {
					std::cout << "   " << h3_error_bands[i] << std::endl;
				}
				std::vector<std::string> h4_error_bands = h4->GetErrorBandNames();
				std::cout << "Error Bands in output " << file4->GetName() << ":" << std::endl;
				for ( int i=0; i<h4_error_bands.size(); i++ ) {
					std::cout << "   " << h4_error_bands[i] << std::endl;
				}
				first = false;
				std::cout << std::endl;
				std::cout << "Combining errors for:" << std::endl;
				std::cout << "   " << name << std::endl;
			}
			
			delete h1;
			delete h2;
			delete h3;
			delete h4;	
		}
		else if(name.find("h2D") == 0 || name.find("migration") != std::string::npos) { // MnvH2D Matrices			
			MnvH2D *h1 = (MnvH2D*)file1->Get(name.c_str());
			MnvH2D *h2 = (MnvH2D*)file2->Get(name.c_str());
			MnvH2D *h3 = (MnvH2D*)file3->Get(name.c_str());
			MnvH2D *h4 = (MnvH2D*)h1->Clone();
			
			h2->TransferErrorBands(h4,false);
			h3->TransferErrorBands(h4,false);
			
			SyncBands(h4);
			
			file4->WriteObject(h4,name.c_str());
			
			delete h1;
			delete h2;
			delete h3;
			delete h4;
		}
		else {
			continue;
		}
	}
	
	std::cout << std::endl << "Finished tranferring error bands" << std::endl;
	
	// POT_summary
	std::cout << std::endl << "Copying over POT_summary";
	MnvH1D* pot_summary1 = (MnvH1D*) file1->Get("POT_summary");
	MnvH1D* pot_summary4 = (MnvH1D*)pot_summary1->Clone();
	file4->WriteObject(pot_summary4,"POT_summary");
	
	delete pot_summary1;
	delete pot_summary4;
	
	// TVector2 pot
	std::cout << std::endl << "Copying over pot";
	TVector2 *pot1 = (TVector2*) file1->Get("pot");
	double X1 = pot1->X();
	double Y1 = pot1->Y();
	TVector2 *pot4 = new TVector2(X1,Y1);
	file4->WriteObject(pot4,"pot");
	
	delete pot1;
	delete pot4;

	std::cout << std::endl << "Closing files" << std::endl;
	
	file1->Close();
	file2->Close();
	file3->Close();
	file4->Close();
	
	std::cout << "Success" << std::endl;
}
