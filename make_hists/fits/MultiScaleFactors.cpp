//File: MultiScaleFactor.cpp
//Info: Class for passing as a function to TMinuit for minimization.
//      Largely derived by example from Andrew Olivier's 
//      github.com/MinervaExpt/NucCCNeutrons/tree/develop/fits/Universe.h 
//      as of 03/16/2022.
//
//Author: David Last dlast@sas.upenn.edu/lastd44@gmail.com

#include "fits/MultiScaleFactors.h"


namespace fit{
MultiScaleFactors::MultiScaleFactors(const std::vector<std::vector<TH1D*>> fitHists, const std::vector<std::vector<TH1D*>> unfitHists, const std::vector<TH1D*> dataHist, const int firstBin, const int lastBin):IBaseFunctionMultiDimTempl<double>(),fFitHists(fitHists),
fUnfitHists(unfitHists), fDataHist(dataHist), fFirstBin(firstBin), fLastBin(lastBin), fDoFit(true)
{
    std::cout << " making the MultiScaleFactor" << fFitHists.size() <<  std::endl;

    if (fFitHists.size() == 0 || fFitHists[0].size() == 0){
        std::cout << "Function has no histos to fit... Setting the fit condition to false." << std::endl;
        fDoFit = false;
    }
    std::cout << " making the MultiScaleFactor" << fFitHists[0].size() <<  std::endl;
    
    int nBins = 0;
    if (fDoFit) nBins = fFitHists.at(0).at(0)->GetNbinsX();
    
    //    for(unsigned int iFit; iFit < fFitHists.size(); ++iFit){
    //      if (!fDoFit) break;
    //      if (fFitHists.at(iFit)->GetNbinsX() != nBins){
    //	std::cout << "No. of bins not consistent... Setting the fit condition to false." << std::endl;
    //	fDoFit = false;
    //      }
    //    }
    //
    //    for(unsigned int iFit; iFit < fUnfitHists.size(); ++iFit){
    //      if (!fDoFit) break;
    //      if (fUnfitHists.at(iFit)->GetNbinsX() != nBins){
    //	std::cout << "No. of bins not consistent... Setting the fit condition to false." << std::endl;
    //	fDoFit = false;
    //      }
    //    }
    //
    //    if (fDataHist->GetNbinsX() != nBins){
    //      std::cout << "No. of bins not consistent... Setting the fit condition to false." << std::endl;
    //      fDoFit = false;
    //    }
    
    //Avoid fitting overflow
    if (fDoFit && fLastBin < 0 || fLastBin > nBins) fLastBin=nBins;
    std::cout << " made the MultiScaleFactor" << std::endl;
}

unsigned int MultiScaleFactors::NDim() const{
    if (!fDoFit) return 0;
    else return fFitHists[0].size();
}

double MultiScaleFactors::DoEval(const double* parameters) const{
    //For now just copying in the chi^2 function more or less directly from Andrew
    double chi2 = 0.0;
    if (!fDoFit) return chi2;
    
    double fitSum = 0.0;
    std::cout << "parameters ";
    int ndim = NDim();
    for (int i = 0; i < ndim; i++){
         std::cout << parameters[i] << " ";
    }
    std::cout << std::endl;
    for (int whichBin = fFirstBin; whichBin <= fLastBin; ++whichBin){
        double fitSum = 0.0;
        for (unsigned int whichsample=0; whichsample < fUnfitHists.size(); ++whichsample){
            for(unsigned int whichFit=0; whichFit < ndim; ++whichFit){
                double temp = fUnfitHists.at(whichsample).at(whichFit)->GetBinContent(whichBin)*parameters[whichFit];
                fitSum += temp;
            }
            double dataContent = fDataHist.at(whichsample)->GetBinContent(whichBin);
            double dataErr = fDataHist.at(whichsample)->GetBinError(whichBin);
            double diff = fitSum-dataContent;
            
            std::cout << "Fit Sum: " << fitSum << ", Data: " << dataContent << ", Difference: " << diff << ", Error: " << dataErr << std::endl;
            //std::cout << "How the chi2 should change: " << (diff*diff)/(dataErr*dataErr) << std::endl;
            if (dataErr > 1e-10) chi2 += (diff*diff)/(dataErr*dataErr);
        }
        //std::cout << "Updated chi2: " << chi2 << std::endl;
    }
    
    
    //std::cout << "About to return chi2 of: " << chi2 << std::endl;
    
    return chi2;
}

//Required for ROOT fittable function base class :( (indeed this is sad, Andrew)
ROOT::Math::IBaseFunctionMultiDimTempl<double>* MultiScaleFactors::Clone() const{
    return new MultiScaleFactors(fFitHists, fUnfitHists, fDataHist, fFirstBin, fLastBin);
}

}
