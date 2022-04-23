#include "fits/DoTheFit.h"
#include "fits/MultiScaleFactors.h"
#include "Minuit2/Minuit2Minimizer.h"
#include "TMinuitMinimizer.h"
#include "MnvH2D.h"


namespace fit{

int DoTheFit(std::map<const std::string, std::vector< PlotUtils::MnvH1D*>> fitHists, const std::map<const std::string, std::vector< PlotUtils::MnvH1D*> > unfitHists, const std::map<const std::string, PlotUtils::MnvH1D*>  dataHist, const std::map<const std::string, bool> includeInFit, const std::vector<std::string> categories, const fit_type type, const int lowBin, const int hiBin, const bool binbybin ){
    
    // takes the histograms in unfitHists[sample][category], fits to dataHist by combining all the samples by changing the normalization of the category templates and then makes fitHists[sample][category] which contains the best template fit for each universe.
    // writes the chi2 value, parameters and covariance of the parameters into the output root file but does not return them.
    
    // make a fitter
    auto* mini2 = new ROOT::Minuit2::Minuit2Minimizer(ROOT::Minuit2::kCombined);
    
    int ncat= categories.size();
    
    // the fit code wants TH1D so make a copy of the data for that purpose
    std::map<const std::string, TH1D* > dataHistCV;
  TString aname;
  int count = 0;
    for (auto sample:dataHist){
      if (count == 0){
        aname = dataHist.at(sample.first)->GetName();
        count++;
      }
        dataHistCV[sample.first] = (TH1D*) dataHist.at(sample.first)->Clone();
    }
    
    
    // long winded way to pull out the universes list
    // could make this in to a consistency check later.
    // this assumes that all histograms have the same universes, which they really should
    
    std::vector<std::string> universes;
    PlotUtils::MnvH1D* ahist;
    int acount = 0;
    
    for (auto sample:unfitHists){
        acount++;
        if (acount>1)continue;
        ahist = sample.second.at(0);
        universes = ahist->GetVertErrorBandNames();
    }
  
    
  // make objects to contain the fit information
  PlotUtils::MnvH1D parameters(TString("parameters_"+aname),"fit parameters",ncat,0.0,double(ncat));
  PlotUtils::MnvH2D covariance(TString("covariance_"+aname),"fit parameters",ncat,0.0,double(ncat),ncat,0.0,double(ncat));
  PlotUtils::MnvH1D fcn(TString("fcn"+aname),"fcn",1,0.,1.);
    
    // add in the CV so you do a loop over universes
    
    universes.push_back("CV");
    
    //  now loop over all universes and fit each one
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
        // loop over universes within a band
        for (int iuniv = 0; iuniv < nuniv; iuniv++){
            std::cout << " now do the fit for " << univ << " " << iuniv << std::endl;
            // make a local TH1F map unfitHistsCV that the fitter expects
            std::map<const std::string, std::vector< TH1D*>> unfitHistsCV;
             if (univ == "CV"){
                for (auto sample:unfitHists){
                    for (int i = 0; i < ncat; i++){
                        TString name = unfitHists.at(sample.first).at(i)->GetName()+TString("_"+univ);
                        TH1D* hist = (TH1D*) unfitHists.at(sample.first).at(i)->Clone(name);
                        unfitHistsCV[sample.first].push_back(hist);
                    }
                }
            }
            else{
                for (auto sample:unfitHists){
                    for (int i = 0; i < ncat; i++){
                        PlotUtils::MnvVertErrorBand*  errorband = unfitHists.at(sample.first).at(i)->GetVertErrorBand(univ);
                        if (errorband == 0){
                            std::cout << " no such band " << std::endl;
                        }
                        TString name = errorband->GetName();
                        name += TString("_" + univ);
                        TH1D* hist = (TH1D*) errorband->GetHist(iuniv)->Clone(name);
                        unfitHistsCV[sample.first].push_back(hist);
                    }
                }
            }
            std::cout << " have made the local samples for this universe"<< std::endl;
            
          for (int thebin = lowBin; thebin <= hiBin; thebin++){
            fit::MultiScaleFactors func2(unfitHistsCV,dataHistCV,includeInFit,type,lowBin,hiBin);
 
            // set parameters with lower limit of 0
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
            
            // tell it what the fit function is
            mini2->SetFunction(func2);
           
            // do the actual fit
            bool success = true;
            mini2->Minimize();
        
            // https://root-forum.cern.ch/t/is-fit-validity-or-minimizer-status-more-important/30637
            int status = mini2->Status();
            std::cout << " fit status was " << status << std::endl;
            if(status > 1){
                std::cout << "Printing Results." << std::endl;
                mini2->PrintResults();
                std::cout << "FIT FAILED" << std::endl;
                success=false;
                //return 7;
            }
            else{
                std::cout << "Printing Results." << std::endl;
                mini2->PrintResults();
                std::cout << "FIT SUCCEEDED" << std::endl;
                success = true;
            }
            
            // have done the fit, now rescale all histograms by the appropriate scale factors
            
            const double* combScaleResults = mini2->X();
            // make it a vector.
            std::vector<double> ScaleResults;
            for (int i = 0; i < func2.NDim(); i++){
                ScaleResults.push_back(combScaleResults[i]);
            }
            
            
            if (!success){
                // if it failed, just scale the components to the data with the original ratios
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
                        }
                        ScaleResults[i] = data/tot;
                    }
                }
            }
            // print out the parameters
            std::cout << "fix" << success << " " << status << " " << univ << " " << iuniv << " " << status;
            for (int i = 0; i < func2.NDim(); i++){
                std::cout  << " " << i << " " << combScaleResults[i] << " " << ScaleResults[i];
            }
            std::cout << std::endl;
            
            // now record the parameters and rescale the template to return as fitHists
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
                        for (int j = lowBin; j <= hiBin; j++){
                            fitHists[sample.first][i]->SetBinContent(j,fitHists[sample.first][i]->GetBinContent(j)*combScaleResults[i]);
                            fitHists[sample.first][i]->SetBinError(j,fitHists[sample.first][i]->GetBinError(j)*ScaleResults[i]);
                        }
                    }
                }
            }
            else{
                // scale the error bands appropriately and record the changes in fcn, parameter, covariance
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
                        for (int j = lowBin; j <= hiBin; j++){
                          // HMS change to only do the bin range
                          hist->SetBinContent(j,hist->GetBinContent(j)*combScaleResults[i]);
                          hist->SetBinError(j,hist->GetBinError(j)*ScaleResults[i]);
                      }
                        //hist->Scale(ScaleResults[i]);
                    }
                }
            }
        } // end of nuniv loop
    }// end of universes loop
    fcn.MnvH1DToCSV("fcn","./csv/");
    fcn.Write();
    parameters.MnvH1DToCSV("parameters","./csv/");
    covariance.MnvH2DToCSV("parameters","./csv/");
    parameters.Write();
    covariance.Write();
    return 0;
}

}
//end namespace

