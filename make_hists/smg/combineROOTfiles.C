#include <iostream>
#include <string>
#include <vector>
#include <numeric>
#include "utils/NuConfig.h"
#include "TFile.h"
#include "TVector2.h"
#include "TSystem.h"
#include "PlotUtils/MnvH1D.h"
#include "PlotUtils/MnvH2D.h"

using namespace PlotUtils;

int main(const int argc, const char *argv[]) {
	
	std::string outfilename = std::string(argv[1]);
	std::vector<std::string> infilenames;
	
	std::cout << "Combinging root files" << std::endl;
	for(int i=2; i<argc; i++) {
		infilenames.push_back(std::string(argv[i]));
		std::cout << "   " << argv[i] << std::endl;
	}
	std::cout << "to produce " << outfilename << std::endl;
	
	TFile *outfile = new TFile(outfilename.c_str(),"RECREATE");
	
	for(int i=2; i<argc; i++) {
	
		std::string infilename = argv[i];
		TFile *infile = new TFile(infilename.c_str());
		
		if(i == 2) {
			MnvH1D *pot_summary_in = (MnvH1D*)infile->Get("POT_summary");
			MnvH1D *pot_summary_out = (MnvH1D*)pot_summary_in->Clone();
			outfile->WriteObject(pot_summary_out,"POT_summary");
			delete pot_summary_in;
			delete pot_summary_out;
			
			TVector2 *pot_in = (TVector2*) infile->Get("pot");
			double X1 = pot_in->X();
			double Y1 = pot_in->Y();
			TVector2 *pot_out = new TVector2(X1,Y1);
			outfile->WriteObject(pot_out,"pot");
			delete pot_in;
			delete pot_out;
		}
		
		for(auto key : *(infile->GetListOfKeys())){
		
			std::string name = key->GetName();
			if(outfile->FindKey(name.c_str())) {
				continue;
			}
			else {
				if(name.find("migration") == std::string::npos & name.find("h2D") == std::string::npos) { // 1D Histograms
					MnvH1D *hIn = (MnvH1D*)infile->Get(name.c_str());
					MnvH1D *hOut = (MnvH1D*)hIn->Clone();
					outfile->WriteObject(hOut,name.c_str());
					delete hIn;
					delete hOut;
				}
				else if(name.find("h2D") == 0 || name.find("migration") != std::string::npos) { // 1D Histograms
					MnvH2D *hIn = (MnvH2D*)infile->Get(name.c_str());
					MnvH2D *hOut = (MnvH2D*)hIn->Clone();
					outfile->WriteObject(hOut,name.c_str());
					delete hIn;
					delete hOut;
				}
				else {
					continue;
				}
			}
		}
		infile->Close();
	}
	outfile->Close();
	std::cout << std::endl << "Success" << std::endl;	
}
