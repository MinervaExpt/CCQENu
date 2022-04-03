#include "fits/DoTheFit.h"
#include "fits/MultiScaleFactors.h"
#include "Minuit2/Minuit2Minimizer.h"
#include "TMinuitMinimizer.h"


namespace fit{

int DoTheFit(std::map<const std::string, std::vector< PlotUtils::MnvH1D*>> fitHists, const std::map<const std::string, std::vector< PlotUtils::MnvH1D*> > unfitHists, const std::map<const std::string, PlotUtils::MnvH1D*>  dataHist, const std::map<const std::string, bool> includeInFit, const std::vector<std::string> categories, const fit_type type, const int lowBin, const int hiBin ){
    
    
    
    // first pull out  the right hists in the PlotUtils::MnvH1D
    
    
    auto* mini2 = new ROOT::Minuit2::Minuit2Minimizer(ROOT::Minuit2::kMigrad);
    
    
    std::map<const std::string, TH1D* > dataHistCV;
    for (auto sample:dataHist){
        std::cout << " sample is " << sample.first << std::endl;
        dataHistCV[sample.first] = (TH1D*) dataHist.at(sample.first);
    }
    
    // long winded way to pull out the universes list
    // could make this in to a consistency check later.
    std::vector<std::string> universes;
    PlotUtils::MnvH1D* ahist;    int count = 0;
    for (auto sample:unfitHists){
        count++;
        if (count>1)continue;
        ahist = sample.second.at(0);
        universes = ahist->GetVertErrorBandNames();
    }
    
    universes.push_back("CV");
    for (auto univ:universes){
        
        int nuniv;
        if (univ != "CV"){
            nuniv = ahist->GetVertErrorBand(univ)->GetNHists();
            
        }
        else{ nuniv = 1;}
        
        std::cout << " look at universe " << univ << " " << nuniv <<  std::endl;
        
        for (int iuniv = 0; iuniv < nuniv; iuniv++){
            std::cout << " now do the fit for " << univ << " " << iuniv << std::endl;
            std::map<const std::string, std::vector< TH1D*>> unfitHistsCV;
            
            if (univ == "CV"){
                for (auto sample:unfitHists){
                    std::cout << univ << " sample size " << sample.first << " " <<  sample.second.size() << " " << categories.size() << std::endl;
                    for (int i = 0; i < categories.size(); i++){
                        TString name = unfitHists.at(sample.first).at(i)->GetName()+TString("_"+univ);
                        TH1D* hist = (TH1D*) unfitHists.at(sample.first).at(i)->Clone(name);
                        unfitHistsCV[sample.first].push_back(hist);
                        hist->Print();
                    }
                }
            }
            else{
                for (auto sample:unfitHists){
                    std::cout << univ << " sample size " << sample.first << " " <<  sample.second.size() << " " << categories.size() << std::endl;
                    for (int i = 0; i < categories.size(); i++){
                        PlotUtils::MnvVertErrorBand*  errorband = unfitHists.at(sample.first).at(i)->GetVertErrorBand(univ);
                        if (errorband == 0){
                            std::cout << " no such band " << std::endl;
                        }
                        TString name = errorband->GetName();
                        name += TString("_" + univ);
                        TH1D* hist = (TH1D*) errorband->GetHist(iuniv)->Clone(name);
                        unfitHistsCV[sample.first].push_back(hist);
                        hist->Print();
                    }
                }
            }
            
            std::cout << " have made the local samples for this universe"<< std::endl;
            
            
            
            fit::MultiScaleFactors func2(unfitHistsCV,dataHistCV,includeInFit,type,lowBin,hiBin);
            

            
            std::cout << "Have made the fitter " << std::endl;
            
            std::cout << " now set up parameters" << func2.NDim() <<std::endl;
            
            int nextPar = 0;
            
            for(unsigned int i=0; i < func2.NDim(); ++i){
                
                std::string name = categories[i];
                std::cout << " set parameter " << i << " " << name << std::endl;
                mini2->SetLowerLimitedVariable(i,name,1.0,0.1,0.0);
                nextPar++;
            }
            
            
            if (nextPar != func2.NDim()){
                std::cout << "The number of parameters was unexpected for some reason for fitHists1." << std::endl;
                return 6;
            }
            
            std::cout << "Have set up the parameters " << std::endl;
            
            mini2->SetFunction(func2);
            
            std::cout << " check link to function" << mini2->NDim() << std::endl;
            
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
                        TH1D* hist = errorband->GetHist(iuniv);
                        hist->Scale(combScaleResults[i]);
                    }
                }
            }
            //delete mini2;
        }
    }
    return 0;
}

}
//end namespace

