#include "PlotUtils/MnvH1D.h"
#include "TFile.h"
#include "TString.h"
#include "utils/BinomialMC.h"
#include "utils/BinomialMC.cxx"
/** 
Program that does a binomial divide on 2 weighted histograms but then rescales the binomial errors. 
**/



int main(){
    TString inputpath = "/Users/schellma/Dropbox/CCQE/p4_test/p4.root"; TFile* f = TFile::Open(inputpath.Data(), "READONLY");
    TString name2 = "h___QElike___qelike___recoil___all_truth_tuned";
    TString name1 = "h___QElike___qelike___recoil___selected_truth_tuned" ;PlotUtils::MnvH1D* hist1 = (PlotUtils::MnvH1D*) f->Get(name1);
    PlotUtils::MnvH1D* hist2 = (PlotUtils::MnvH1D*) f->Get(name2);
    hist1->Print("ALL");
    hist2->Print("ALL");
    TString newname = TString(hist1->GetName()).ReplaceAll("selected_truth_tuned", "efficiency");
    PlotUtils::MnvH1D* eff = BinomialMC( hist1, hist2, newname);
    eff->Print("ALL");
    eff->Fit("pol3");
    TFile* g = TFile::Open("test.root","RECREATE");
    g->cd();
    hist1->Write();
    hist2->Write();
    eff->Write();
    g->Close();
    return 0;
}


