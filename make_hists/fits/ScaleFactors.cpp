//File: ScaleFactor.cpp
//Info: Class for passing as a function to TMinuit for minimization.
//      Largely derived by example from Andrew Olivier's 
//      github.com/MinervaExpt/NucCCNeutrons/tree/develop/fits/Universe.h 
//      as of 03/16/2022.
//
//Author: David Last dlast@sas.upenn.edu/lastd44@gmail.com

#include "fits/ScaleFactors.h"

namespace fit{
  ScaleFactors::ScaleFactors(const std::vector<TH1D*> fitHists, const std::vector<TH1D*> unfitHists, const TH1D* dataHist, 
			     const int firstBin, const int lastBin):IBaseFunctionMultiDimTempl<double>(), fFitHists(fitHists), 
								    fUnfitHists(unfitHists), fDataHist(dataHist), fFirstBin(firstBin), fLastBin(lastBin), fDoFit(true)
  {
    if (fFitHists.size() == 0){
      std::cout << "Function has no histos to fit... Setting the fit condition to false." << std::endl;
      fDoFit = false;
    }

    int nBins = 0;
    if (fDoFit) nBins = fFitHists.at(0)->GetNbinsX();

    for(unsigned int iFit; iFit < fFitHists.size(); ++iFit){
      if (!fDoFit) break;
      if (fFitHists.at(iFit)->GetNbinsX() != nBins){
	std::cout << "No. of bins not consistent... Setting the fit condition to false." << std::endl;
	fDoFit = false;
      }
    }

    for(unsigned int iFit; iFit < fUnfitHists.size(); ++iFit){
      if (!fDoFit) break;
      if (fUnfitHists.at(iFit)->GetNbinsX() != nBins){
	std::cout << "No. of bins not consistent... Setting the fit condition to false." << std::endl;
	fDoFit = false;
      }
    }

    if (fDataHist->GetNbinsX() != nBins){
      std::cout << "No. of bins not consistent... Setting the fit condition to false." << std::endl;
      fDoFit = false;
    }

    //Avoid fitting overflow
    if (fDoFit && fLastBin < 0 || fLastBin > nBins) fLastBin=nBins;
  }

  unsigned int ScaleFactors::NDim() const{
    if (!fDoFit) return 0;
    else return fFitHists.size();
  }
  
  double ScaleFactors::DoEval(const double* parameters) const{
    //For now just copying in the chi^2 function more or less directly from Andrew
    double chi2 = 0.0;
    if (!fDoFit) return chi2;
    
    for (int whichBin = fFirstBin; whichBin <= fLastBin; ++whichBin){
      int whichParam = 0;
      double fitSum = 0.0;

      for(unsigned int whichFit=0; whichFit < fFitHists.size(); ++whichFit){
	fitSum += fFitHists.at(whichFit)->GetBinContent(whichBin)*((parameters+whichParam)[0]);
	whichParam+=1;
      }

      for (unsigned int whichUnfit=0; whichUnfit < fUnfitHists.size(); ++whichUnfit){
	fitSum += fUnfitHists.at(whichUnfit)->GetBinContent(whichBin);
      }

      double dataContent = fDataHist->GetBinContent(whichBin);
      double dataErr = fDataHist->GetBinError(whichBin);
      double diff = fitSum-dataContent;
      //std::cout << "Fit Sum: " << fitSum << ", Data: " << dataContent << ", Difference: " << diff << ", Error: " << dataErr << std::endl;
      //std::cout << "How the chi2 should change: " << (diff*diff)/(dataErr*dataErr) << std::endl;
      if (dataErr > 1e-10) chi2 += (diff*diff)/(dataErr*dataErr);
      //std::cout << "Updated chi2: " << chi2 << std::endl;
    }

    //std::cout << "About to return chi2 of: " << chi2 << std::endl;

    return chi2;
  }

  //Required for ROOT fittable function base class :( (indeed this is sad, Andrew)
  ROOT::Math::IBaseFunctionMultiDimTempl<double>* ScaleFactors::Clone() const{
    return new ScaleFactors(fFitHists, fUnfitHists, fDataHist, fFirstBin, fLastBin);
  }

}
