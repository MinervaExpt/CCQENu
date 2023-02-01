#include <iostream>
#include <string>
#include <fstream>
#include <sys/stat.h>
#include <algorithm>
#include "PlotUtils/MnvH1D.h"
#include "PlotUtils/MnvH2D.h"
#include "PlotUtils/MnvH1DToCSV.h"
#include "TFile.h"
#include "TROOT.h"
#include "TStyle.h"
#include "TTree.h"
#include "TKey.h"
#include "TCanvas.h"

int main(const int argc, const char *argv[]) {

	std::string rootFile = std::string(argv[1]);
	TFile *file = new TFile(rootFile.c_str(),"READONLY");

	std::vector<std::string> samples = {"QElike","MichelSideBand","BlobSideBand","MicBlobSideBand","QElike_noProtonCuts","MichelSideBand_noProtonCuts","BlobSideBand_noProtonCuts","MicBlobSideBand_noProtonCuts"};
	std::vector<std::string> constraints = {"qelike","1chargedpion","1neutralpion","multipion","other"};
	std::map<std::string,std::map<std::string,std::map<int,int>>> pdgcounts;
	std::vector<int> pdglist;
	int pdg;
	bool inlist;
	PlotUtils::MnvH1D* h;
	
	for( auto s : samples ) {
		for( auto c : constraints ) {
			h = (PlotUtils::MnvH1D*)file->Get(("h___"+s+"___"+c+"___PrimaryProtonCandidatePDG___reconstructed").c_str());
			int nx = h->GetNbinsX();
			for( int i=1; i<=nx; i++ ) {
				if(h->GetBinContent(i)>0) {
					inlist = 0;
					pdg = ceil(h->GetXaxis()->GetBinLowEdge(i));
					pdgcounts[s][c][pdg] = ceil(h->GetBinContent(i));
					for( auto n : pdglist ) {
						if(n == pdg) {
							inlist = 1;
							break;
						}
					}
					if(!inlist) pdglist.push_back(pdg);
				}
			}
		}	
	}
	
	std::sort(pdglist.begin(),pdglist.end());
	std::ofstream outfile;
	outfile.open("PrimaryProtonCandidatePDG_multitrack_me1N.csv");
	outfile << "sample,constraint";
	for( auto n : pdglist ) outfile << "," << n;
	outfile << std::endl;
	
	for( auto s : samples ) {
		for( auto c : constraints ) {
			outfile << s << "," << c;
			for( auto n : pdglist ) {
				if(pdgcounts[s][c].count(n)) {
					outfile << "," << pdgcounts[s][c][n];
				}
				else outfile << ",0";
			}
			outfile << std::endl;
		}
	}
	outfile.close();
	
	return 0;
}
