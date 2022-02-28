#include "TROOT.h"
#include "TFile.h"
#include "TTree.h"

#include "utils/NuConfig.h"
#include "include/CVUniverse.h"

#include <iostream>
#include <fstream>
#include <sstream>
#include <string>
#include <vector>


int main(const int argc, const char *argv[]){

	std::string pl = std::string(argv[1]);
	std::string configfilename(pl+".json");
	NuConfig config;
	config.Read(configfilename);
	
	std::fstream input;
	input.open(config.GetString("mcIn"));
	std::map<int,int> pdgCounts;
	std::cout << std::endl << "Reading in files." << std::endl;
	for(std::string line; getline(input, line);){
		TFile* inFile = TFile::Open(line.c_str(),"READ");
		std::cout << std::endl << "Opened " << line.c_str() << std::endl;
		TTree* tree = (TTree*)inFile->Get("Truth");
		std::cout << std::endl << "Pointing to Truth Tree." << std::endl;
		int mc_nFSPart;
		int mc_FSPartPDG[100];
		tree->SetBranchAddress("mc_nFSPart",&mc_nFSPart);
		tree->SetBranchAddress("mc_FSPartPDG",&mc_FSPartPDG);
		
		std::cout << std::endl << "Starting Loop...";
		for(int entry = 0; entry < 100; entry++){
			tree->GetEntry(entry);
			if (entry+1 % 1000 == 0) std::cout << (entry / 1000) << "k " << std::endl;
			
			for(int i = 0; i < mc_nFSPart; i++){
				int part = mc_FSPartPDG[i];
				bool newParticle = 0;
				for(std::map<int,int>::iterator it = pdgCounts.begin(); it != pdgCounts.end(); ++it){
					if(it->first != part){
						newParticle = 1;
						
					}
				}
				
				if(newParticle) pdgCounts[part] = 1;
				else pdgCounts[part]++;
			}
		}
		std::cout << std::endl << "Loop finished.";
		
		inFile->Close();
		
	}
	input.close();
	
	std::cout << std::endl << "Printing." << std::endl;
	
	/*
	std::vector<int> pdgs;
	for(std::map<int,int>::iterator it = pdgCounts.begin(); it != pdgCounts.end(); ++it){
		pdgs.push_back(it->first);
	}
	
	std::cout << std::endl << std::endl;
	std::cout << "________________________" << std::endl;
	std::cout << "|        |             |" << std::endl;
	std::cout << "|  PDG   |    count    |" << std::endl;
	std::cout << "|________|_____________|" << std::endl;
	std::cout << "|        |             |" << std::endl;
	std::sort(pdgs.begin(),pdgs.end());
	for(int part : pdgs){
		if(part < 10) std::cout << "|     ";
		else if(part < 100) std::cout << "|    ";
		else if(part < 1000) std::cout << "|   ";
		else if(part < 10000) std::cout << "|  ";
		else std::cout << "| ";
		std::cout << part << " |";
		
		if(pdgCounts[part] < 10) std::cout << "           ";
		else if(pdgCounts[part] < 100) std::cout << "          ";
		else if(pdgCounts[part] < 1000) std::cout << "         ";
		else if(pdgCounts[part] < 10000) std::cout << "        ";
		else if(pdgCounts[part] < 100000) std::cout << "       ";
		else if(pdgCounts[part] < 1000000) std::cout << "      ";
		else if(pdgCounts[part] < 10000000) std::cout << "     ";
		else if(pdgCounts[part] < 100000000) std::cout << "    ";
		else if(pdgCounts[part] < 1000000000) std::cout << "   ";
		else if(pdgCounts[part] < 10000000000) std::cout << "  ";
		else std::cout << " ";
		std::cout << pdgCounts[part] << " |" << std::endl;
	}
	std::cout << "|________|_____________|" << std::endl << std::endl;
	*/
	return 0;
}
