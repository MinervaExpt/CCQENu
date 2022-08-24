#include <iostream>
#include <string>
#include <fstream>
#include <sys/stat.h>
#include <algorithm>
#include "PlotUtils/MnvH1D.h"
#include "TFile.h"
#include "TROOT.h"
#include "TStyle.h"
#include "TTree.h"
#include "TKey.h"
#include "TLine.h"
#include "TLegend.h"
#include "TCanvas.h"
#include "utils/NuConfig.h"

int main(const int argc, const char *argv[]){
	
	// Read in config file
    std::cout << std::endl;
	std::string configfilename = std::string(argv[1]);
	NuConfig config;
	config.Read(configfilename);
	
	// Get stuff from config file
	std::string pdfname = config.GetString("outputpdf");
    std::string rootFile1 = config.GetString("rootFile1");
    std::string rootFile2 = config.GetString("rootFile2");
    std::string legendTitle = config.GetString("legendTitle");
    std::string legendLabel1 = config.GetString("legendLabel1");
    std::string legendLabel2 = config.GetString("legendLabel2");
    std::string ratioLabel = config.GetString("ratioLabel");
    
    // Read in root files
    std::cout << std::endl;
    std::cout << "Reading in \033[1;33m" << rootFile1 << "\033[0m";
    std::cout << std::endl;
    TFile *file1 = new TFile(rootFile1.c_str(),"READONLY");
    std::cout << "Reading in \033[1;33m" << rootFile2 << "\033[0m";
    std::cout << std::endl << std::endl;
    TFile *file2 = new TFile(rootFile2.c_str(),"READONLY");
			
	// Making canvas for plotting
	TCanvas canvas("canvas","canvas",800,600);
	canvas.cd();
	
	// Open output pdf
	canvas.Print(Form("%s[",pdfname.c_str()));
	std::cout << std::endl;

    // Looping over keys to take ratio of histrograms and plot
    for(TObject* keyAsObj : *file1->GetListOfKeys()) {
    	auto key = dynamic_cast<TKey*>(keyAsObj);
        std::string name = key->GetName();
        std::string classname = key->GetClassName();
        if(classname == "PlotUtils::MnvH1D") {
            
            // Making hist1 and hist2
            PlotUtils::MnvH1D* hist1 = (PlotUtils::MnvH1D*)file1->Get(name.c_str());
            hist1->SetDirectory(0);     
            PlotUtils::MnvH1D* hist2 = (PlotUtils::MnvH1D*)file2->Get(name.c_str());
            hist2->SetDirectory(0);
            
            // Making ratio hist, hist3
			PlotUtils::MnvH1D* hist3 = (PlotUtils::MnvH1D*)hist1->Clone();
			hist3->Divide(hist3,hist2,1.,1.);
			hist3->SetDirectory(0);
    	
    		// Create pad 1 for overlay plot of hist1 and hist2
			TPad pad1("pad1","pad1",0,0.3,1,1);
			pad1.SetBottomMargin(0);
			pad1.Draw();
			pad1.cd();
			
			// Customize and draw hist1 and hist2
			hist1->SetLineColor(kRed);
			hist1->SetStats(0);
			hist1->SetTitle(name.c_str());
			hist1->GetXaxis()->SetLabelSize(0);
			hist1->GetXaxis()->SetTitleSize(0);
			hist1->GetYaxis()->SetTitle("Number of events");
			hist1->GetYaxis()->SetTitleSize(0.05);
			hist2->SetLineColor(kBlack);
			hist2->SetStats(0);
			hist1->Draw("h");
			hist2->Draw("pe,same");
			
			// Create pad2 for plot of ratio hist, hist3
			canvas.cd();
			TPad pad2("pad2","pad2",0,0,1,0.3);
			pad2.SetTopMargin(0);
			pad2.SetBottomMargin(0.27);
			pad2.Draw();
			pad2.cd();
		    
		    // Customize and draw hist3
		    hist3->SetLineColor(kRed);
		    hist3->SetStats(0);
			hist3->SetTitle("");
			hist3->GetXaxis()->SetLabelSize(0.12);
			hist3->GetXaxis()->SetTitleSize(0.12);
			hist3->GetYaxis()->SetLabelSize(0.1);
			hist3->GetYaxis()->SetTitleSize(0.13);
			hist3->GetYaxis()->SetTitle(ratioLabel.c_str());
			hist3->GetYaxis()->SetTitleOffset(0.35);
			hist3->Draw("pe");
		    
		    // Add zero line in ratio plot
		    TLine line(0,1,2.5,1);
		    line.SetLineColor(kBlack);
		    line.Draw("same");
		    
		    // Add legend to plot of hist1 and hist2
		    pad1.cd();
			TLegend legend(0.7,0.6,0.85,0.75);
		    legend.AddEntry(hist1,legendLabel1.c_str());
		    legend.AddEntry(hist2,legendLabel2.c_str());
		    legend.SetTextSize(0.04);
		    legend.SetLineWidth(0);
		    legend.SetHeader(legendTitle.c_str(),"L");
		    legend.Draw("same");
		    canvas.cd();
		    
		    // Print canvas to pdf file
		    canvas.Print(pdfname.c_str());
		    
		    // Delete pointers to prevent memory complaints
		    delete hist1;
		    delete hist2;
		    delete hist3;
    	}
    }
    
    // Close output pdf file
    std::cout << std::endl;
    canvas.Print(Form("%s]",pdfname.c_str()));
    std::cout << std::endl;
    
    // Closing root files, deleting pointers
    file1->Close();
    file2->Close();
    delete file1;
    delete file2;

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
