#include "fits/DoTheFit.h"
#include "fits/MultiScaleFactors.h"
#include "Minuit2/Minuit2Minimizer.h"
#include "TMinuitMinimizer.h"
#include "MnvH2D.h"


namespace fit{

int DoTheFit(std::map<const std::string, std::vector< PlotUtils::MnvH1D*>> fitHists, const std::map<const std::string, std::vector< PlotUtils::MnvH1D*> > unfitHists, const std::map<const std::string, PlotUtils::MnvH1D*>  dataHist, const std::map<const std::string, bool> includeInFit, const std::vector<std::string> categories, const fit_type type, const int lowBin, const int hiBin ){
    
    
    
    // first pull out  the right hists in the PlotUtils::MnvH1D
    
    
    auto* mini2 = new ROOT::Minuit2::Minuit2Minimizer(ROOT::Minuit2::kCombined);
    
    int ncat= categories.size();
    
    std::map<const std::string, TH1D* > dataHistCV;
    for (auto sample:dataHist){
        std::cout << " sample is " << sample.first << std::endl;
        dataHistCV[sample.first] = (TH1D*) dataHist.at(sample.first);
    }
    
    PlotUtils::MnvH1D parameters("parameters","fit parameters",ncat,0.0,double(ncat));
    PlotUtils::MnvH2D covariance("covariance","fit parameters",ncat,0.0,double(ncat),ncat,0.0,double(ncat));
    PlotUtils::MnvH1D fcn("fcn","fcn",1,0.,1.);
    
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
            fcn.AddVertErrorBandAndFillWithCV(univ,nuniv);
            parameters.AddVertErrorBandAndFillWithCV(univ,nuniv);
            covariance.AddVertErrorBandAndFillWithCV(univ,nuniv);
            
        }
        else{
            nuniv = 1;
        }
        
        
        std::cout << " look at universe " << univ << " " << nuniv <<  std::endl;
        
        for (int iuniv = 0; iuniv < nuniv; iuniv++){
            std::cout << " now do the fit for " << univ << " " << iuniv << std::endl;
            std::map<const std::string, std::vector< TH1D*>> unfitHistsCV;
            
            
            if (univ == "CV"){
                for (auto sample:unfitHists){
                    std::cout << univ << " sample size " << sample.first << " " <<  sample.second.size() << " " << ncat << std::endl;
                    double total=0.0;
                    for (int i = 0; i < ncat; i++){
                        TString name = unfitHists.at(sample.first).at(i)->GetName()+TString("_"+univ);
                        TH1D* hist = (TH1D*) unfitHists.at(sample.first).at(i)->Clone(name);
                        unfitHistsCV[sample.first].push_back(hist);
                        //hist->Print();
                        total+=hist->Integral(lowBin,hiBin);
                    }
                }
            }
            else{
                for (auto sample:unfitHists){
                    std::cout << univ << " sample size " << sample.first << " " <<  sample.second.size() << " " << ncat << std::endl;
                    double total = 0.0;
                    for (int i = 0; i < ncat; i++){
                        PlotUtils::MnvVertErrorBand*  errorband = unfitHists.at(sample.first).at(i)->GetVertErrorBand(univ);
                        if (errorband == 0){
                            std::cout << " no such band " << std::endl;
                        }
                        TString name = errorband->GetName();
                        name += TString("_" + univ);
                        TH1D* hist = (TH1D*) errorband->GetHist(iuniv)->Clone(name);
                        //hist->Print();
                        unfitHistsCV[sample.first].push_back(hist);
                        total+=hist->Integral(lowBin,hiBin);
                        //hist->Print();
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
                mini2->SetLowerLimitedVariable(i,name,1.3,0.1,0.0);
                nextPar++;
            }
            
            if (nextPar != func2.NDim()){
                std::cout << "The number of parameters was unexpected for some reason for fitHists1." << std::endl;
                return 6;
            }
            
            std::cout << "Have set up the parameters " << std::endl;
            
            mini2->SetFunction(func2);
            
            std::cout << " check link to function" << mini2->NDim() << std::endl;
            
            //mini2->PrintResults();
            bool success = true;
            std::cout << "Fitting " << "combination" << std::endl;
            mini2->Minimize();
        
            // https://root-forum.cern.ch/t/is-fit-validity-or-minimizer-status-more-important/30637
            int status = mini2->Status();
            std::cout << " fit status was " << status << std::endl;
            if(status > 1){
                std::cout << "Printing Results." << std::endl;
                mini2->PrintResults();
                //printCorrMatrix(*mini2, func2.NDim());
                std::cout << "FIT FAILED" << std::endl;
                success=false;
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
            std::vector<double> ScaleResults;
            for (int i = 0; i < func2.NDim(); i++){
                ScaleResults.push_back(combScaleResults[i]);
            }
            
            
            if (!success){
                // if it failed, just normalize the components to the original ratios
                for (auto sample:fitHists){
                    double tot = 0;
                    double data = dataHist.at(sample.first)->Integral(lowBin,hiBin);
                    for (int i = 0; i < func2.NDim(); i++){
                        if (univ == "CV"){
                            tot += fitHists[sample.first][i] ->Integral(lowBin,hiBin);
                        }
                        else{
                            PlotUtils::MnvVertErrorBand*  errorband = fitHists.at(sample.first).at(i)->GetVertErrorBand(univ);
                            tot += errorband->GetHist(iuniv)->Integral(lowBin,hiBin);
                            //errorband->GetHist(iuniv)->Write();
                        }
                        
                        ScaleResults[i] = data/tot;
                    }
                }
            }
            std::cout << "fix" << success << " " << status << " " << univ << " " << iuniv << " " << status;
            for (int i = 0; i < func2.NDim(); i++){
                std::cout  << " " << i << " " << combScaleResults[i] << " " << ScaleResults[i];
            }
            std::cout << std::endl;
            if (univ == "CV"){
                fcn.SetBinContent(1,mini2->MinValue());
                for (int i = 0; i < func2.NDim(); i++){
                    parameters.SetBinContent(i+1, combScaleResults[i]);
                    for (int j = 0; j < func2.NDim(); j++){
                        covariance.SetBinContent(i+1,j+1,mini2->CovMatrix(i,j));
                    }
                }
                // hack the main histogram by brute force
                for (auto sample:fitHists){
                    for (int i = 0; i < func2.NDim(); i++){
                        int nbins = fitHists[sample.first][i]->GetNbinsX();
                        for (int j = 0; j < nbins+2; j++){
                            fitHists[sample.first][i]->SetBinContent(j,fitHists[sample.first][i]->GetBinContent(j)*combScaleResults[i]);
                            fitHists[sample.first][i]->SetBinError(j,fitHists[sample.first][i]->GetBinError(j)*ScaleResults[i]);
                        }
                    }
                }
            }
            else{
                // tweak other error bands
                TH1D* fcnhist = fcn.GetVertErrorBand(univ)->GetHist(iuniv);
                fcnhist->SetBinContent(1,mini2->MinValue());
                TH1D* phist = parameters.GetVertErrorBand(univ)->GetHist(iuniv);
                TH2D* chist = covariance.GetVertErrorBand(univ)->GetHist(iuniv);
                for (int i = 0; i < ncat; i++){
                    phist->SetBinContent(i+1,combScaleResults[i]);
                    for (int j = 0; j < ncat; j++){
                        chist->SetBinContent(i+1,j+1,mini2->CovMatrix(i,j));
                    }
                }
                for (auto sample:fitHists){
                    // need to figure out how to fill the fcn/parameter/covariance error bands.
                    for (int i = 0; i < ncat; i++){
                        PlotUtils::MnvVertErrorBand*  errorband = fitHists.at(sample.first).at(i)->GetVertErrorBand(univ);
                        TH1D* hist = errorband->GetHist(iuniv);
                        hist->Scale(ScaleResults[i]);
                    }
                }
            }
            
            
            //delete mini2;
        }
    }
    fcn.MnvH1DToCSV("fcn","");
    fcn.Write();
    parameters.MnvH1DToCSV("parameters","./csv/");
    parameters.Write();
    covariance.Write();
    return 0;
}

}
//end namespace

