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
#include "utils/NuConfig.h"

// To use this type "./getCSVs [filename]" without ".root" for any root file with MnvH1Ds.

std::vector<std::string> split (std::string s, std::string delimiter) {
  size_t pos_start = 0, pos_end, delim_len = delimiter.length();
  std::string token;
  std::vector<std::string> res;
  
  while ((pos_end = s.find (delimiter, pos_start)) != std::string::npos) {
    token = s.substr (pos_start, pos_end - pos_start);
    pos_start = pos_end + delim_len;
    res.push_back (token);
  }
  
  res.push_back (s.substr (pos_start));
  return res;
}

int main(const int argc, const char *argv[]){

	std::string configfilename = std::string(argv[1])+".root";
	NuConfig config;
	config.Read(configfilename);
	
	std::string recoName1 = config.GetString("recoName1");
	std::string recoName2 = config.GetString("recoName2");
	std::string playlist = config.GetString("playlist");

    // Read in root files
    std::string rootFile1 = config.GetString("rootFile1");
    std::string rootFile2 = config.GetString("rootFile2");
    std::cout << std::endl;
    std::cout << "Reading in\n\n\t\033[1;34m./\033[1;33m" << rootFile1 << "\033[0m\n";
    std::cout << std::endl;
    TFile *file1 = new TFile(rootFile1.c_str(),"READONLY");
    std::cout << "Reading in\n\n\t\033[1;34m./\033[1;33m" << rootFile2 << "\033[0m\n";
    std::cout << std::endl;
    TFile *file2 = new TFile(rootFile2.c_str(),"READONLY");

    /////////////////////////////////////////////////////////////////////////////////////////
    //////////////// Extracting information on every object in the root file ////////////////
    /////////////////////////////////////////////////////////////////////////////////////////

    // Declare empty containers for objects and their information
    std::vector<std::string> keys1;
    std::map<std::string, std::string> classes1;
    std::map<std::string, std::string> titles1;
    std::map<std::string, std::string> cycles1;
    std::map<std::string, std::vector<std::string>> parsekey1;
    
    std::vector<std::string> keys2;
    std::map<std::string, std::string> classes2;
    std::map<std::string, std::string> titles2;
    std::map<std::string, std::string> cycles2;
    std::map<std::string, std::vector<std::string>> parsekey2;

    // Cycle through objects in root file
    std::cout << "Extracting object information..." << std::endl;
    for(TObject* keyAsObj : *file1->GetListOfKeys())
    { 
        // Get object key
        auto key = dynamic_cast<TKey*>(keyAsObj);
        std::string name = key->GetName();

        // Fill information containers
        keys1.push_back(name);
        classes1[name] = key->GetClassName();
        titles1[name] = key->GetTitle(); 
        cycles1[name] = key->GetCycle();
    }
    for(TObject* keyAsObj : *file2->GetListOfKeys())
    { 
        // Get object key
        auto key = dynamic_cast<TKey*>(keyAsObj);
        std::string name = key->GetName();

        // Fill information containers
        keys2.push_back(name);
        classes2[name] = key->GetClassName();
        titles2[name] = key->GetTitle(); 
        cycles2[name] = key->GetCycle();
    }

    /////////////////////////////////////////////////////////////////////////////////////////
    /////////////////////// Creating csv file to store parsekey stuff ///////////////////////
    /////////////////////////////////////////////////////////////////////////////////////////

    // Initiate  output file
    std::string parseFile1 = playlist+"_"+recoName1+"_ParseKey1.csv";
    std::cout << "Parsing keys for " << recoName1 << "." << std::endl;
    std::cout << "Putting parsed keys in" << std::endl;
    std::cout << "\n\t\033[1;34m./\033[1;33m" << parseFile1 << "\033[0m\n";
    std::cout << std::endl;
    std::ofstream parsefile1;
    parsefile1.open((parseFile1).c_str());
    parsefile1 << "key,parsekey size,[0],[1],[2]";
    parsefile1 << ",[3],[4]" << std::endl; // Column headers

    // Loop over keys to add info to file
    for(auto name : keys1)
    {
        // Split Key
        parsekey1[name] = split(name,"___");
        parsefile1 << name << "," << parsekey1[name].size() << ",";
        // print splitted key
        for(int i = 0; i < parsekey1[name].size(); i++){
            parsefile1 << parsekey1[name][i] << ",";
        }
        parsefile1 << std::endl;
    }

    // Close object list output file
    parsefile1.close();
    
    // Initiate  output file
    std::string parseFile2 = playlist+"_"+recoName2+"_ParseKey2.csv";
    std::cout << "Parsing keys for " << recoName2 << "." << std::endl;
    std::cout << "Putting parsed keys in" << std::endl;
    std::cout << "\n\t\033[1;34m./\033[1;33m" << parseFile2 << "\033[0m\n";
    std::cout << std::endl;
    std::ofstream parsefile2;
    parsefile2.open((parseFile2).c_str());
    parsefile2 << "key,parsekey size,[0],[1],[2]";
    parsefile2 << ",[3],[4]" << std::endl; // Column headers

    // Loop over keys to add info to file
    for(auto name : keys2)
    {
        // Split Key
        parsekey2[name] = split(name,"___");
        parsefile2 << name << "," << parsekey2[name].size() << ",";
        // print splitted key
        for(int i = 0; i < parsekey2[name].size(); i++){
            parsefile2 << parsekey2[name][i] << ",";
        }
        parsefile2 << std::endl;
    }

    // Close object list output file
    parsefile2.close();

    /////////////////////////////////////////////////////////////////////////////////////////
    ////////////////////// Retrieving histogram objects from root file //////////////////////
    /////////////////////////////////////////////////////////////////////////////////////////

    // Create empty containers for histograms
    std::map<std::string, PlotUtils::MnvH1D*> hists1_1d;
    std::map<std::string, PlotUtils::MnvH2D*> hists1_2d;
    std::vector<std::string> hists1_1d_keys;
    std::vector<std::string> hists1_2d_keys;
    
    std::map<std::string, PlotUtils::MnvH1D*> hists2_1d;
    std::map<std::string, PlotUtils::MnvH2D*> hists2_2d;
    std::vector<std::string> hists2_1d_keys;
    std::vector<std::string> hists2_2d_keys;
    
    std::map<std::string, PlotUtils::MnvH1D> hists_1d_ratio;

    // Looping over keys to fill histogram containers
    std::cout << "Extracting histograms from " << std::string(argv[1]);
    std::cout << ".root" << std::endl;
    for(auto name : keys1)
    {
        if(classes1[name] == "PlotUtils::MnvH1D")
        {
            hists1_1d_keys.push_back(name);
            hists1_1d[name] = (PlotUtils::MnvH1D*)file->Get(name.c_str());
            hists1_1d[name]->SetDirectory(0);
        }
        else if(classes1[name] == "PlotUtils::MnvH2D")
        {
            hists1_2d_keys.push_back(name);
            hists1_2d[name] = (PlotUtils::MnvH2D*)file->Get(name.c_str());
            hists1_2d[name]->SetDirectory(0);
        }
    }
    std::cout << "Extracting histograms from " << std::string(argv[2]);
    std::cout << ".root" << std::endl;
    for(auto name : keys2)
    {
        if(classes2[name] == "PlotUtils::MnvH1D")
        {
            hists2_1d_keys.push_back(name);
            hists2_1d[name] = (PlotUtils::MnvH1D*)file->Get(name.c_str());
            hists2_1d[name]->SetDirectory(0);
        }
        else if(classes2[name] == "PlotUtils::MnvH2D")
        {
            hists2_2d_keys.push_back(name);
            hists2_2d[name] = (PlotUtils::MnvH2D*)file->Get(name.c_str());
            hists2_2d[name]->SetDirectory(0);
        }
    }
    for(auto name1 : keys1)
    {
    	for(auto name2 : keys2)
    	{
    		if(classes1[name1] == classes2[name2]){
    			hists_1d_ratio[name1] = Divide(hists1_1d[name1],hists1_1d[name2]);
    		}
    	}
    }

    // Closing root files
    file1->Close();
    file2->Close();

    /////////////////////////////////////////////////////////////////////////////////////////
    ////////////////////// Creating pdf to print each histogram object //////////////////////
    /////////////////////////////////////////////////////////////////////////////////////////
    
    // Initializing pdf file and TCanvas
    std::string pdfFileName = "hists_"+playlist+"_ratio_";
    std::string pdfFileName = pdfFileName+recoName1+"_"+recoName2+".pdf";
    std::cout << "Drawing histograms to\n\n\t\033[1;34m./";
    std::cout << "\033[1;33m" << pdfFileName << "\033[0m\n" << std::endl;
    TCanvas canvas(pdfFileName.c_str());
    canvas.SetLeftMargin(0.15);
    canvas.SetBottomMargin(0.15);
    canvas.cd();
    //canvas.Print(Form("%s(",pdfFileName.c_str()));
    canvas.Print(Form("%s(",("./"+std::string(argv[1])+"/"+pdfFileName).c_str()));

    // Looping over keys to draw histograms
    for(auto name : hists1_1d_keys){
        hists_1d_ratio[name]->Draw("pe");
        canvas.Print((pdfFileName).c_str());
    }

    //canvas.Print(Form("%s)",pdfFileName.c_str()));
    canvas.Print(Form("%s)",(pdfFileName).c_str()));
    std::cout << std::endl;

    return 0;
}


/*


hist->GetEntries()
hist->GetEffectiveEntries()????????????


hist->GetNbinsX()
hist->GetXaxis()->GetBinLowEdge(i)
hist->GetXaxis()->GetBinUpEdge(i)
hist->GetBinContent(i)

hist->GetBinContent(i,j)








*/
