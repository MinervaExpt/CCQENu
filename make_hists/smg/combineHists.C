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

	std::string configfilename = std::string(argv[1]);
	NuConfig config;
	std::cout << std::endl;
	config.Read(configfilename);

	std::cout << std::endl;
	config.Print();

	std::vector<std::string> infilenames = config.GetStringVector("infiles");
	std::string outfilename = config.GetString("outfile");
	TFile *outfile = new TFile(outfilename.c_str(),"RECREATE");

	int n_infiles = infilenames.size();
	std::cout << std::endl << "Combining the following " << n_infiles << " files:" << std::endl;
	for(int i=0; i<n_infiles; i++) {
		std::cout << "   " << infilenames[i] << std::endl;
	}
	std::cout << "to create new file " << outfilename << std::endl;

	// vectors of Data (X) and MC (Y) POTs
	std::vector<double> Xs;
	std::vector<double> Ys;

	// Loop over files to be combined
	for(int i=0; i<n_infiles; i++) { // Skipping first infile because already "added"
	
		std::cout << std::endl << "Opening " << infilenames[i] << " and adding to " << outfilename;
		TFile *infile_i = new TFile(infilenames[i].c_str());
		
		// TVector2 pot
		TVector2 *pot_i = (TVector2*) infile_i->Get("pot");
		double X_i = pot_i->X();
		double Y_i = pot_i->Y();
		Xs.push_back(X_i);
		Ys.push_back(Y_i);
		if(i == 0) {
			TVector2 *pot = new TVector2(X_i,Y_i);
			outfile->WriteObject(pot,"pot");
			delete pot;
		}
		else {
			TVector2 *pot = (TVector2*) outfile->Get("pot");
			double X = pot->X();
			double Y = pot->Y();
			TVector2 *pot_new = new TVector2(X+X_i,Y+Y_i);		
			outfile->WriteObject(pot_new,"pot","Overwrite"); // Replace old pot with new
			delete pot;
			delete pot_new;
		}	
		delete pot_i;
		
		// Combine Histograms
		for(auto key : *(infile_i->GetListOfKeys())){
			std::string name = key->GetName();
			if(name.find("_") == std::string::npos) { // Only histograms contain "_"s
				continue;
			}
			else if(i != 0 & infile_i->FindKey(name.c_str()) == 0) {
				std::cout << std::endl << "Input file " << infilenames[i] << " does not contain " << name << ".";
				continue;
			}
			else if(name.find("migration") == std::string::npos || name.find("h2D") == std::string::npos) {
				MnvH1D *h_i = (MnvH1D*)infile_i->Get(name.c_str());
				if(i == 0) {
					MnvH1D *h = (MnvH1D*)h_i->Clone();
					outfile->WriteObject(h,name.c_str());
					delete h;
				}
				else {
					MnvH1D *h = (MnvH1D*)outfile->Get(name.c_str());
					h->Add(h_i);
					outfile->WriteObject(h,name.c_str(),"Overwrite");
					delete h;
				}
				delete h_i;
			}
			else {
				MnvH2D *h_i = (MnvH2D*)infile_i->Get(name.c_str());
				if(i == 0) {
					MnvH2D *h2d = (MnvH2D*)h_i->Clone();
					outfile->WriteObject(h2d,name.c_str());
					delete h2d;
				}
				else {
					MnvH2D *h2d = (MnvH2D*)outfile->Get(name.c_str());
					h2d->Add(h_i);
					outfile->WriteObject(h2d,name.c_str(),"Overwrite");
					delete h2d;
				}
				delete h_i;
			}
		}
		
		infile_i->Close();
		
	}
	
	// Print old and new POTs
	std::cout << std::endl << std::endl << "Data POT = "; 
	for(int i=0; i<Xs.size(); i++) {
		if(i>0) {
			std::cout << " + ";
		}
		std::cout << Xs[i];
	}
	std::cout << " = " << std::accumulate(Xs.begin(),Xs.end(),decltype(Xs)::value_type(0));
	std::cout << std::endl << "MC POT   = "; 
	for(int i=0; i<Ys.size(); i++) {
		if(i>0) {
			std::cout << " + ";
		}
		std::cout << Ys[i];
	}
	std::cout << " = " << std::accumulate(Ys.begin(),Ys.end(),decltype(Ys)::value_type(0));;
	std::cout << std::endl << std::endl;
	
	outfile->Close();
	
	std::cout << "Success" << std::endl;	
}

