//File: MultiScaleFactor.h
//Info: Class for passing as a function to TMinuit for minimization.
//      Largely derived by example from Andrew Olivier's 
//      github.com/MinervaExpt/NucCCNeutrons/tree/develop/fits/Universe.h 
//      as of 03/16/2022.
//
//Author: David Last dlast@sas.upenn.edu/lastd44@gmail.com

#ifndef MULTISCALEFACTORS_H
#define MULTISCALEFACTORS_H

#include "TH1D.h"
#include "TVector3.h"
#include "Math/IFunction.h"
#include "stdlib.h"
#include <iostream>
#include <string>
#include <vector>
#include <map>
#include <unordered_map>
#include <bitset>

namespace fit{
  class MultiScaleFactors: public ROOT::Math::IBaseFunctionMultiDimTempl<double>{
  private:
    //Members to hold the histos
    std::vector<std::vector<TH1D*>> fFitHists;
    std::vector<std::vector<TH1D*>> fUnfitHists;
    std::vector<TH1D*> fDataHist;
    //Members for fit range
    std::string fSignal;
    int fFirstBin;
    int fLastBin;
    bool fDoFit;

  public:
    //CTOR
    MultiScaleFactors(const std::vector<std::vector<TH1D*>> fitHists, const std::vector<std::vector<TH1D*>> unfitHists, const std::vector<TH1D*> dataHist, const int firstBin = 1, const int lastBin = -1);

    unsigned int NDim() const override;

    //Function which the ROOT fitter will minimize
    double DoEval(const double* parameters) const override;

    //Required for ROOT fittable function base class :( (indeed this is sad, Andrew)
    IBaseFunctionMultiDimTempl<double>* Clone() const override;

    //DTOR
    virtual ~MultiScaleFactors() = default;
  };
}

#endif
