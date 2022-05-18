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
enum fit_type{kFastChi2,kSlowChi2,kML};

  class MultiScaleFactors: public ROOT::Math::IBaseFunctionMultiDimTempl<double>{
  private:
    //Members to hold the histos -
    // order is sample, category
    // the category templates need to be in a vector to make the fitting indexing work well.
    std::map<const std::string, std::vector< TH1D*> > fFitHists;
    std::map<const std::string, std::vector< TH1D*> > fUnfitHists;
    std::map<const std::string, TH1D*>  fDataHist;
    // this says which samples to include
    std::map<const std::string, bool> fInclude;
      // in principle, each sample may be a different variable so need to make these into maps in future.
    int fFirstBin;
    int fLastBin;
    int fNdim;
    fit_type fType;
    bool fDoFit;

  public:
    //CTOR
    MultiScaleFactors(const std::map<const std::string, std::vector< TH1D*> > unfitHists, const std::map<const std::string, TH1D*>  dataHist, const std::map<const std::string, bool> Include, const fit_type type,  const int firstBin = 1, const int lastBin = -1);

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
