#ifndef fitfunction_h
#define fitfunction_h
#include "fits/MultiScaleFactors.h"
#include "Minuit2/Minuit2Minimizer.h"
#include "TMinuitMinimizer.h"
#include "PlotUtils/MnvH1D.h"
#include <map>
#include <vector>

namespace fit{

int DoTheFit(std::map<const std::string, std::vector< PlotUtils::MnvH1D*>> fitHists, const std::map<const std::string, std::vector< PlotUtils::MnvH1D*> > unfitHists, const std::map<const std::string, PlotUtils::MnvH1D*>  dataHist, const std::map<const std::string, bool> includeInFit, const std::vector<std::string> categories, const fit_type type, const int lowBin = 1, const int hiBin = -1){
    
    std::map<const std::string, std::vector< TH1D*>> unfitHistsCV;
    std::map<const std::string, TH1D* > dataHistCV;
    
    // first pull out  the right hists in the PlotUtils::MnvH1D
    ROOT::Minuit2::Minuit2Minimizer * mini2;
    
    std::string univ = "CV";
    int nuniv = 0;
    
    std::cout << " do the fit for " << univ << " " << nuniv << std::endl;
    
    for (auto sample:dataHist){
        std::cout << " sample is " << sample.first << std::endl;
        dataHistCV[sample.first] = (TH1D*) dataHist.at(sample.first);
    }
    
    if (univ == "CV"){
        for (auto sample:unfitHists){
            std::cout << " sample size " << sample.first << " " <<  sample.second.size() << " " << categories.size() << std::endl;
            for (int i = 0; i < categories.size(); i++){
                TH1D* hist = (TH1D*) unfitHists.at(sample.first).at(i);
                hist->Print();
                unfitHistsCV[sample.first].push_back(hist);
            }
        }
    }
    else{
        for (auto sample:unfitHists){
            for (int i = 0; i < sample.second.size(); i++){
                PlotUtils::MnvVertErrorBand*  errorband = unfitHists.at(sample.first).at(i)->GetVertErrorBand(univ);
                unfitHistsCV[sample.first].push_back((TH1D*) errorband->GetHist(nuniv));
            }
        }
    }
    
    std::cout << " have made the local samples for this universe"<< std::endl;
    
    fit::MultiScaleFactors func2(unfitHistsCV,dataHistCV,includeInFit,type,lowBin,hiBin);
    
   
    
    std::cout << "Have made the fitter " << std::endl;
    
    std::cout << " now set up parameters" << func2.NDim() <<std::endl;
    
    int nextPar = 0;
    
    mini2->SetLowerLimitedVariable(0,"0",1.0,0.1,0.0);
    std::cout << " made one parameter" << std::endl;
    mini2->SetLowerLimitedVariable(1,"1",1.0,0.1,0.0);
    mini2->SetLowerLimitedVariable(2,"2",1.0,0.1,0.0);
    mini2->SetLowerLimitedVariable(3,"3",1.0,0.1,0.0);
    mini2->SetLowerLimitedVariable(4,"4",1.0,0.1,0.0);
    
//    for(unsigned int i=0; i < func2.NDim(); ++i){
//
//        std::string name = categories[i];
//        std::cout << " set parameter " << i << " " << name << std::endl;
//        mini2->SetLowerLimitedVariable(i,name,1.0,0.1,0.0);
//        nextPar++;
//    }
//
//
//    if (nextPar != func2.NDim()){
//        std::cout << "The number of parameters was unexpected for some reason for fitHists1." << std::endl;
//        return 6;
//    }
    
    std::cout << "Have set up the parameters " << std::endl;
    
    mini2->SetFunction(func2);
    
    mini2->PrintResults();
    
    std::cout << "Fitting " << "combination" << std::endl;
    if(!mini2->Minimize()){
        std::cout << "Printing Results." << std::endl;
        mini2->PrintResults();
        //printCorrMatrix(*mini2, func2.NDim());
        std::cout << "FIT FAILED" << std::endl;
        //return 7;
    }
    else{
        std::cout << "Printing Results." << std::endl;
        mini2->PrintResults();
        //printCorrMatrix(*mini2, func2.NDim());
        //cout << mini2->X() << endl;
        //cout << mini2->Errors() << endl;
        std::cout << "FIT SUCCEEDED" << std::endl;
    }
    
    // have done the fit, now rescale all histograms by the appropriate scale factors
    
    const double* combScaleResults = mini2->X();
    //    for (auto side:sidebands){
    //        for (int i = 0; i < categories.size(); i++){
    //            fitHistsCV[side.first][i]->Scale(combScaleResults[i]);
    //        }
    //    }
    if (univ == "CV"){
        // hack the main histogram by brute force
        for (auto sample:fitHists){
            for (int i = 0; i < func2.NDim(); i++){
                int nbins = fitHists[sample.first][i]->GetNbinsX();
                for (int j = 0; j < nbins+2; j++){
                    fitHists[sample.first][i]->SetBinContent(j,fitHists[sample.first][i]->GetBinContent(j)*combScaleResults[i]);
                    fitHists[sample.first][i]->SetBinError(j,fitHists[sample.first][i]->GetBinError(j)*combScaleResults[i]);
                }
            }
        }
    }
    else{
        // tweak other error bands
        for (auto sample:fitHists){
            for (int i = 0; i < categories.size(); i++){
                PlotUtils::MnvVertErrorBand*  errorband = fitHists.at(sample.first).at(i)->GetVertErrorBand(univ);
                TH1D* hist = errorband->GetHist(nuniv);
                hist->Scale(combScaleResults[i]);
            }
        }
        
    }
    return 0;
}
    
}
//end namespace
#endif
