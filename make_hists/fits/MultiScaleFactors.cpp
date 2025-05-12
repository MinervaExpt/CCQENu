//File: MultiScaleFactor.cpp
//Info: Class for passing as a function to TMinuit for minimization.
//      Largely derived by example from Andrew Olivier's 
//      github.com/MinervaExpt/NucCCNeutrons/tree/develop/fits/Universe.h 
//      as of 03/16/2022.
//
//Author: David Last dlast@sas.upenn.edu/lastd44@gmail.com
// Modified extensively by Heidi Schellman (hschellman on github)

#include "fits/MultiScaleFactors.h"
//#define DEBUG 

namespace fit{
MultiScaleFactors::MultiScaleFactors(const std::map<const std::string, std::vector <TH1D*>> unfitHists, const std::map<const std::string, TH1D*> dataHist, const std::map<const std::string, bool> include,
                                     fit_type type, const int firstBin, const int lastBin):IBaseFunctionMultiDimTempl<double>(),fUnfitHists(unfitHists), fDataHist(dataHist), fInclude(include), fType(type), fFirstBin(firstBin), fLastBin(lastBin), fDoFit(true)
{
    int check = 0;
    for (auto side:fUnfitHists){
        fNdim = side.second.size();
        if (check !=0 && fNdim != check){
            std::cout << " inconsistent number of fit templates" << check << side.first << fNdim << std::endl;
        }
        check = fNdim;
    }
    std::cout << " made the MultiScaleFactor" << std::endl;
}

unsigned int MultiScaleFactors::NDim() const{
    if (!fDoFit) return 0;
    else return fNdim;
}

double MultiScaleFactors::DoEval(const double* parameters) const{
    //For now just copying in the chi^2 function more or less directly from Andrew
    double chi2 = 0.0;
    if (!fDoFit) return chi2;
    double fitSum;
#ifdef DEBUG
    std::cout << "parameters ";
    for (int i = 0; i < fNdim; i++){
         std::cout << parameters[i] << " ";
    }
    std::cout << std::endl;
#endif
    for (auto const sample:fUnfitHists){ // loop over samples
        std::string whichsample = sample.first;
        if (!fInclude.at(whichsample)) continue; // skip some samples
        for (int whichBin = fFirstBin; whichBin <= fLastBin; ++whichBin){
            double fitSum = 0.0;
            for (int whichFit = 0; whichFit < fNdim; whichFit++){
                double temp = fUnfitHists.at(whichsample).at(whichFit)->GetBinContent(whichBin)*parameters[whichFit];
                fitSum += temp;
            }
            double diff;
            double dataErr=0.0;
            double dataContent = fDataHist.at(whichsample)->GetBinContent(whichBin);
            if (fType == kFastChi2){
                dataErr = fDataHist.at(whichsample)->GetBinError(whichBin);
                diff = fitSum-dataContent;
                if (dataErr > 1e-10) chi2 += (diff*diff)/(dataErr*dataErr);
            }
            if (fType == kSlowChi2){ // use the MC as a better estimator
                double MCval = fitSum>0?fitSum:-fitSum;
                
                diff = fitSum-dataContent;
                if (MCval > 0) {
                    chi2 += (diff*diff)/MCval;
                }
            
                
            }
            if (fType == kML){
                diff = fitSum-dataContent;
                chi2 -= 2.*TMath::Log(TMath::Poisson(dataContent,fitSum));
            }
#ifdef DEBUG
            std::cout << whichsample << "Fit Sum: " << fitSum << ", Data: " << dataContent << ", Difference: " << diff << ", Error: " << dataErr << ", chi2" << chi2 << std::endl;
#endif
        }
    }
    
#ifdef DEBUG
    
    std::cout << "About to return chi2 of: " << chi2 << std::endl;
#endif
    return chi2;
}

//Required for ROOT fittable function base class :( (indeed this is sad, Andrew)
ROOT::Math::IBaseFunctionMultiDimTempl<double>* MultiScaleFactors::Clone() const{
    return new MultiScaleFactors( fUnfitHists, fDataHist, fInclude, fType, fFirstBin, fLastBin);
}

}
