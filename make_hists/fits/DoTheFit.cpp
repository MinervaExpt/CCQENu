#include "fits/DoTheFit.h"

#include "Minuit2/Minuit2Minimizer.h"
#include "MnvH2D.h"
#include "TMinuitMinimizer.h"
#include "TMatrixD.h"
#include "TVectorD.h"
#include "TMatrixDSymEigen.h"
#include "fits/MultiScaleFactors.h"
#include "utils/SyncBands.h"

#define DEBUG
namespace fit {

TMatrixD  extrabands(const TMatrixDSym cov) {
    //int n = parameters.size();
    //n = 5;
    int n = cov.GetNrows();

    const TMatrixDSymEigen E = TMatrixDSymEigen(cov);
    TVectorD  e = E.GetEigenValues();
    TMatrixD  m = E.GetEigenVectors();

    e.Print();
    m.Print();
    TMatrixD results(n,n);
    int count = 0;
    for (int vi = 0; vi < n ; vi++){
        count++;
        if (count > 100) return results;
        if (vi > n) return results;
        for (int j = 0; j < n ; j++){
            results[vi][j] = 0.0;
        }
        for (int j = 0; j < n ; j++){
           // std::cout << "eigen " << vi << " " << j << " " << results[vi][j] << " " << e[vi][vi] <<  " " << m[vi][j] << std::endl;
            results[j][vi] += std::sqrt(e[vi]) * m[j][vi];
        }
    }
    
    results.Print();
    return results;
}

int DoTheFit(std::map<const std::string, std::vector<PlotUtils::MnvH1D*>> fitHists, 
             std::map<const std::string, std::vector<PlotUtils::MnvH1D*>> unfitHists, 
             const std::map<const std::string, PlotUtils::MnvH1D*> dataHist, 
             std::map<const std::string, std::map<const std::string, std::vector<PlotUtils::MnvH1D*>>> addFitHists, 
             std::map<const std::string, std::map<const std::string, std::vector<PlotUtils::MnvH1D*>>> addUnfitHists, 
             const std::map<const std::string, std::map<const std::string, PlotUtils::MnvH1D*>> addDataHist, 
             const std::map<const std::string, bool> includeInFit, const std::vector<std::string> categories, const fit_type type, 
             const int lowBin, const int hiBin, const std::map<const std::string, int> addHiBin, 
             const double upperLimit, const bool binbybin) {
    // takes the histograms in unfitHists[sample][category], fits to dataHist by combining all the samples by changing the normalization of the category templates and then makes fitHists[sample][category] which contains the best template fit for each universe.
    // writes the chi2 value, parameters and covariance of the parameters into the output root file but does not return them.

    // make a fitter
    auto* mini2 = new ROOT::Minuit2::Minuit2Minimizer(ROOT::Minuit2::kCombined);

    int ncat = categories.size();

    // the fit code wants TH1D so make a copy of the data for that purpose
    std::map<const std::string, TH1D*> dataHistCV;
    TString aname;
    int count = 0;
    for (auto sample : dataHist) {
        if (count == 0) {
            aname = dataHist.at(sample.first)->GetName();
            count++;
        }
        dataHistCV[sample.first] = (TH1D*)dataHist.at(sample.first)->Clone();
    }
    std::cout << std::endl << "Making and filling addDataHistCV" << std::endl;
    std::map<const std::string, std::map<const std::string, TH1D*>> addDataHistCV;
    std::vector<TString> addanames;
    int counter = 0;
    for (auto sample : addDataHist) {
    	for (auto var : sample.second) {
		    if (counter == 0) {
		        addanames.push_back(var.second->GetName());
		    }
		    addDataHistCV[sample.first][var.first] = (TH1D*)var.second->Clone();
        }
        counter++;
    }
    std::cout << std::endl << "count = " << count << std::endl;

    // long winded way to pull out the universes list
    // could make this in to a consistency check later.
    // this assumes that all histograms have the same universes, which they really should

    std::vector<std::string> universes;
    PlotUtils::MnvH1D* ahist;
    int acount = 0;

    for (auto sample : unfitHists) {
        acount++;
        if (acount > 1) continue;
        ahist = sample.second.at(0);
        universes = ahist->GetVertErrorBandNames();
        universes.push_back("CV");
        std::cout << " universe names:" ;
        for (auto a:universes){
            std::cout << a << ", ";
        }
        std::cout << std::endl;
    }

    // make objects to contain the fit information
    PlotUtils::MnvH1D parameters(TString("parameters_" + aname), "fit parameters", ncat, 0.0, double(ncat));
    PlotUtils::MnvH2D covariance(TString("covariance_" + aname), "fit parameters", ncat, 0.0, double(ncat), ncat, 0.0, double(ncat));
    PlotUtils::MnvH2D correlation(TString("correlation_" + aname), "fit parameters", ncat, 0.0, double(ncat), ncat, 0.0, double(ncat));
    PlotUtils::MnvH1D fcn(TString("fcn" + aname), "fcn", 1, 0., 1.);

    
    TMatrixD variants(ncat,ncat);
    TVectorD theparameters(ncat);
    TMatrixDSym CovMatrix(ncat,ncat);
    CovMatrix.ResizeTo(ncat,ncat);
    //int ndim;//

    // add in the CV so you do a loop over universes
    //  now loop over all universes and fit each one
    for (auto univ : universes) {
        std::cout << "Universe is " << univ << " " << universes.size() << std::endl;
        int nuniv;
        if (univ != "CV") {
            nuniv = ahist->GetVertErrorBand(univ)->GetNHists();
            fcn.AddVertErrorBandAndFillWithCV(univ, nuniv);
            parameters.AddVertErrorBandAndFillWithCV(univ, nuniv);
            covariance.AddVertErrorBandAndFillWithCV(univ, nuniv);
            correlation.AddVertErrorBandAndFillWithCV(univ, nuniv);
        } else {
            nuniv = 1;
        }
        // loop over universes within a band
        for (int iuniv = 0; iuniv < nuniv; iuniv++) {
            std::cout << " now do the fit for " << univ << " " << iuniv << std::endl;
            // make a local TH1F map unfitHistsCV that the fitter expects
            std::map<const std::string, std::vector<TH1D*>> unfitHistsCV;
            std::map<const std::string, std::map<const std::string, std::vector<TH1D*>>> addUnfitHistsCV;
            if (univ == "CV") {
                for (auto sample : unfitHists) {
                    for (int i = 0; i < ncat; i++) {
                        TString name = unfitHists.at(sample.first).at(i)->GetName() + TString("_" + univ);
                        TH1D* hist = (TH1D*)unfitHists.at(sample.first).at(i)->Clone(name);
                        unfitHistsCV[sample.first].push_back(hist);
                    }
                }
                for (auto sample : addUnfitHists) {
                	for (auto var : sample.second) {
		                for (int i = 0; i < ncat; i++) {
		                    TString name = var.second[i]->GetName() + TString("_" + univ);
		                    TH1D* hist = (TH1D*)var.second[i]->Clone(name);
		                    addUnfitHistsCV[sample.first][var.first].push_back(hist);
		                }
                    }
                }
            } else {
                for (auto sample : unfitHists) {
                    for (int i = 0; i < ncat; i++) {
                        PlotUtils::MnvVertErrorBand* errorband = unfitHists.at(sample.first).at(i)->GetVertErrorBand(univ);
                        if (errorband == 0) {
                            std::cout << " no such band " << std::endl;
                        }
                        TString name = errorband->GetName();
                        name += TString("_" + univ);
                        TH1D* hist = (TH1D*)errorband->GetHist(iuniv)->Clone(name);
                        unfitHistsCV[sample.first].push_back(hist);
                    }
                }
                for (auto sample : addUnfitHists) {
                	for(auto var : sample.second) {
		                for (int i = 0; i < ncat; i++) {
		                    PlotUtils::MnvVertErrorBand* errorband = var.second[i]->GetVertErrorBand(univ);
		                    if (errorband == 0) {
		                        std::cout << " no such band " << std::endl;
		                    }
		                    TString name = errorband->GetName();
		                    name += TString("_" + univ);
		                    TH1D* hist = (TH1D*)errorband->GetHist(iuniv)->Clone(name);
		                    addUnfitHistsCV[sample.first][var.first].push_back(hist);
		                }
                    }
                }
            }
            std::cout << " have made the local samples for this universe" << std::endl;

            //for (int thebin = lowBin; thebin <= hiBin; thebin++) {
            if (true){
                fit::MultiScaleFactors func2(unfitHistsCV, dataHistCV, includeInFit, type, lowBin, hiBin);

                // set parameters with lower limit of 0
                int nextPar = 0;
                int ndim = func2.NDim();
                for (unsigned int i = 0; i < func2.NDim(); ++i) {
                    std::string name = categories[i];
                    std::cout << " set parameter " << i << " " << name << std::endl;
                    mini2->SetLowerLimitedVariable(i, name, 1.0, 0.1, 0.0);
                    //mini2->SetUpperLimitedVariable(i, name, 1.0, 0.1, upperLimit);
                    nextPar++;
                }

                if (nextPar != func2.NDim()) {
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
                if (status > 1) {
                    std::cout << "Printing Results." << std::endl;
                    mini2->PrintResults();
                    std::cout << "FIT FAILED" << std::endl;
                    success = false;
                    // return 7;
                } else {
                    std::cout << "Printing Results." << std::endl;
                    mini2->PrintResults();
                    std::cout << "FIT SUCCEEDED" << std::endl;
                    success = true;
                }

                // have done the fit, now rescale all histograms by the appropriate scale factors

                const double* combScaleResults = mini2->X();
                // make it a vector.
                std::vector<double> ScaleResults;

                ndim = func2.NDim();
                //TMatrixDSym CovMatrix(ncat, ncat);
                //CovMatrix.ResizeTo(ncat,ncat);
                
                //std::cout << "ncat" << ncat << std::endl;
                //CovMatrix.Print();
                for (int i = 0; i < ndim; i++) {
                    ScaleResults.push_back(combScaleResults[i]);
                    //if (univ == "CV"){
                    for (int j = 0; j < ndim; j++){
                        //std::cout << i << " " << j << std::endl;
                        CovMatrix[i][j] = mini2->CovMatrix(i, j);
                    }
                    //}
                }
                CovMatrix.Print();


                if (!success) {
                    // if it failed, just scale the components to the data with the original ratios
                    for (auto sample : fitHists) {
                        double tot = 0;
                        double data = dataHist.at(sample.first)->Integral(lowBin, hiBin);
                        for (int i = 0; i < func2.NDim(); i++) {
                            if (univ == "CV") {
                                tot += fitHists[sample.first][i]->Integral(lowBin, hiBin);
                            } else {
                                PlotUtils::MnvVertErrorBand* errorband = fitHists.at(sample.first).at(i)->GetVertErrorBand(univ);
                                tot += errorband->GetHist(iuniv)->Integral(lowBin, hiBin);
                            }
                            ScaleResults[i] = data / tot;
                        }
                    }
                }  // end of failure
                // print out the parameters
                std::cout << "fix" << success << " " << status << " " << univ << " " << iuniv << " " << status;
                for (int i = 0; i < func2.NDim(); i++) {
                    std::cout << " test " << i << " " << combScaleResults[i] << " " << ScaleResults[i];
                }
                std::cout << std::endl;

                // now record the parameters and rescale the template to return as fitHists
                std::cout << "Universe is " << univ << std::endl;
                //theparameters.ResizeTo(ncat);
                if (univ == "CV") {
                    fcn.SetBinContent(1, mini2->MinValue());
                    for (int i = 0; i < func2.NDim(); i++) {
                        parameters.SetBinContent(i + 1, ScaleResults[i]);
                        theparameters[i] = ScaleResults[i]; // persistent outside loops
                        for (int j = 0; j < func2.NDim(); j++) {
                            covariance.SetBinContent(i + 1, j + 1, mini2->CovMatrix(i, j));
                        }
                        double err = std::sqrt(covariance.GetBinContent(i + 1, i + 1));
                        parameters.SetBinError(i+1,err);
                    }
                    for (int i = 0; i < func2.NDim(); i++) {
                        double erri = parameters.GetBinError(i+1);
                        for (int j = 0; j < func2.NDim(); j++) {
                            double errj = parameters.GetBinError(j + 1);
                            correlation.SetBinContent(i + 1, j + 1, covariance.GetBinContent(i+1,j+1)/erri/errj);
                        }
                    }
                    //variants.ResizeTo(ncat,ncat);
                    //variants  = covbands(ScaleResults, CovMatrix);

                        // parameters.Print("ALL");
                        // parameters.Write();
                        //  hack the main histogram by brute force
                    for (auto sample : fitHists) {
                        const std::string myname = sample.first;
                        for (int i = 0; i < func2.NDim(); i++) {
                            int nbins = fitHists[sample.first][i]->GetNbinsX();
                            std::cout << "scale CV" << myname << " " << i << " " << ScaleResults[i] << std::endl;
                            //fitHists[myname][i]->Print();
                            //unfitHists[myname][i]->Print();
                            for (int j = lowBin; j <= hiBin; j++) {
                                fitHists[myname][i]->SetBinContent(j, unfitHists[myname][i]->GetBinContent(j) * ScaleResults[i]);
                                fitHists[myname][i]->SetBinError(j, unfitHists[myname][i]->GetBinError(j) * ScaleResults[i]);
                            }
                        }
                    }
                    for (auto sample : addFitHists) {
                        const std::string myname = sample.first;
                        for (auto var : sample.second) {
		                    for (int i = 0; i < func2.NDim(); i++) {
		                    	std::string varname = var.first;
		                        int nbins = var.second[i]->GetNbinsX();
		                        std::cout << "scale CV" << myname << " " << varname << " " << i << " " << ScaleResults[i] << std::endl;
		                        //fitHists[myname][i]->Print();
		                        //unfitHists[myname][i]->Print();
		                        for (int j = lowBin; j <= hiBin; j++) {
		                            addFitHists[myname][varname][i]->SetBinContent(j, addUnfitHists[myname][varname][i]->GetBinContent(j) * ScaleResults[i]);
		                            addFitHists[myname][varname][i]->SetBinError(j, addUnfitHists[myname][varname][i]->GetBinError(j) * ScaleResults[i]);
		                        }
		                    }
                        }
                    }
                } 
                else {  // not CV
                    std::cout << " non CV Universe" << univ << std::endl;
                    // scale the error bands appropriately and record the changes in fcn, parameter, covariance
                    TH1D* fcnhist = fcn.GetVertErrorBand(univ)->GetHist(iuniv);
                    fcnhist->SetBinContent(1, mini2->MinValue());
                    TH1D* phist = parameters.GetVertErrorBand(univ)->GetHist(iuniv);
                    TH2D* chist = covariance.GetVertErrorBand(univ)->GetHist(iuniv);
                    TH2D* corhist = correlation.GetVertErrorBand(univ)->GetHist(iuniv);
                    for (int i = 0; i < ncat; i++) {
                        phist->SetBinContent(i + 1, ScaleResults[i]);
                        for (int j = 0; j < ncat; j++) {
                            chist->SetBinContent(i + 1, j + 1, mini2->CovMatrix(i, j));
                        }
                    }
                    for (int i = 0; i < func2.NDim(); i++) {
                        double erri = phist->GetBinError(i + 1);
                        for (int j = 0; j < func2.NDim(); j++) {
                            double errj = phist->GetBinError(j + 1);
                            corhist->SetBinContent(i + 1, j + 1, chist->GetBinContent(i + 1, j + 1) / erri / errj);
                        }
                    }
                    for (auto sample : unfitHists) {
                        // need to figure out how to fill the fcn/parameter/covariance error bands.

                        for (int i = 0; i < ncat; i++) {
                            PlotUtils::MnvVertErrorBand* errorband = unfitHists.at(sample.first).at(i)->GetVertErrorBand(univ);
                            PlotUtils::MnvVertErrorBand* newerrorband = fitHists.at(sample.first).at(i)->GetVertErrorBand(univ);
                            TH1D* hist = errorband->GetHist(iuniv);

                            TH1D* newhist = newerrorband->GetHist(iuniv);

                            for (int j = lowBin; j <= hiBin; j++) {
                                // HMS change to only do the bin range
                                newhist->SetBinContent(j, hist->GetBinContent(j) * ScaleResults[i]);
                                newhist->SetBinError(j, hist->GetBinError(j) * ScaleResults[i]);
                            }

                            // if (true) {
                            //     std::cout << "check bands" << i << " " << univ << " " << iuniv << std::endl;
                            //     hist->Print();
                            //     newhist->Print();
                            // }
                        }
                        // hist->Scale(ScaleResults[i]);
                    }
                    for (auto sample : addUnfitHists) {
                        // need to figure out how to fill the fcn/parameter/covariance error bands.
						for (auto var : sample.second) {
		                    for (int i = 0; i < ncat; i++) {
		                        PlotUtils::MnvVertErrorBand* errorband = addUnfitHists.at(sample.first).at(var.first).at(i)->GetVertErrorBand(univ);
		                        PlotUtils::MnvVertErrorBand* newerrorband = addFitHists.at(sample.first).at(var.first).at(i)->GetVertErrorBand(univ);
		                        TH1D* hist = errorband->GetHist(iuniv);

		                        TH1D* newhist = newerrorband->GetHist(iuniv);

		                        for (int j = lowBin; j <= hiBin; j++) {
		                            // HMS change to only do the bin range
		                            newhist->SetBinContent(j, hist->GetBinContent(j) * ScaleResults[i]);
		                            newhist->SetBinError(j, hist->GetBinError(j) * ScaleResults[i]);
		                        }

		                        // if (true) {
		                        //     std::cout << "check bands" << i << " " << univ << " " << iuniv << std::endl;
		                        //     hist->Print();
		                        //     newhist->Print();
		                        // }
		                    }
		                    // hist->Scale(ScaleResults[i]);
                        }
                    }
                }
            }
        }  // end of nuniv loop
        
    }  // end of universes loop

    

    int neigen=3;  // only use the top 3 eigenvalues. 
    // variants.ResizeTo(ncat,ncat);
    variants = extrabands(CovMatrix);
    for (int var = 0; var< ncat; var++){
        TVectorD tmp = variants[var];
        tmp.Print();
    }

    for (auto sample:fitHists){ //loop over samples
        
        for (int i = 0; i < ncat; i++){  // loop over categories for that sample
            fitHists.at(sample.first).at(i)->AddVertErrorBandAndFillWithCV(std::string("FitVariations"), ncat * 2);
            PlotUtils::MnvVertErrorBand* errorband = fitHists.at(sample.first).at(i)->GetVertErrorBand("FitVariations");
            for (int var = 0; var < neigen; var++){ // loop over variations
                for (int k = 0; k < 2; k++){
                    int iuniv = var*2+k;

                    TH1D* hist = errorband->GetHist(iuniv);

                    int sign = (2*k)-1;
                    // central value already scaled by the fit parameter so have to back it off. 
                    double variation = (1. + variants[var][i] * sign/theparameters[i]);
                    //std::cout << "factor" << var << " " << i << " " << variation << std::endl;
                    //hist->Scale(variation);
                    //hist->Print();
                    
                    for (int j = lowBin; j <= hiBin; j++) {
                        hist->SetBinContent(j, hist->GetBinContent(j)*variation);
                    }

                    std::cout << "varied by " << sample.first << " " << i << " " << iuniv << " " << theparameters[i] << " " << variants[var][i] << " " << variation << " " << theparameters[i]*variation << std::endl;
                 }      
            }
        }
    }
    for (auto sample:addFitHists){ //loop over samples
    
        for (auto variable:sample.second) {
		    for (int i = 0; i < ncat; i++){  // loop over categories for that sample
		        addFitHists.at(sample.first).at(variable.first).at(i)->AddVertErrorBandAndFillWithCV(std::string("FitVariations"), ncat * 2);
		        PlotUtils::MnvVertErrorBand* errorband = addFitHists.at(sample.first).at(variable.first).at(i)->GetVertErrorBand("FitVariations");
		        for (int var = 0; var < neigen; var++){ // loop over variations
		            for (int k = 0; k < 2; k++){
		                int iuniv = var*2+k;

		                TH1D* hist = errorband->GetHist(iuniv);

		                int sign = (2*k)-1;
		                // central value already scaled by the fit parameter so have to back it off. 
		                double variation = (1. + variants[var][i] * sign/theparameters[i]);
		                //std::cout << "factor" << var << " " << i << " " << variation << std::endl;
		                //hist->Scale(variation);
		                //hist->Print();
		                
		                for (int j = lowBin; j <= hiBin; j++) {
		                    hist->SetBinContent(j, hist->GetBinContent(j)*variation);
		                }

		                std::cout << "varied by " << sample.first << " " << variable.first << " " << i << " " << iuniv << " " << theparameters[i] << " " << variants[var][i] << " " << variation << " " << theparameters[i]*variation << std::endl;
		             }      
		        }
		    }
        }
    }

    for (auto sample : fitHists) {
        for (int i = 0; i < ncat; i++) {
            SyncBands(fitHists[sample.first][i]);
        }
    }
    for (auto sample : addFitHists) {
    	for (auto variable : sample.second) {
		    for (int i = 0; i < ncat; i++) {
		        SyncBands(addFitHists[sample.first][variable.first][i]);
		    }
        }
    }

    SyncBands(&fcn);
    SyncBands(&parameters);
    SyncBands(&covariance);
    SyncBands(&correlation);

    fcn.MnvH1DToCSV("fcn", "./csv/");
    fcn.Write();
    parameters.MnvH1DToCSV("parameters", "./csv/");
    covariance.MnvH2DToCSV("covariance", "./csv/");
    correlation.MnvH2DToCSV("correlation", "./csv/");
    parameters.Write();
    covariance.Write();
    correlation.Write();
    return 0;
}

int DoTheFitSlices(std::map<const int, std::map<const std::string, std::vector<PlotUtils::MnvH1D*>>> fitHists, 
                   std::map<const int, std::map<const std::string, std::vector<PlotUtils::MnvH1D*>>> unfitHists, 
                   const std::map<const int, std::map<const std::string, PlotUtils::MnvH1D*>> dataHist, 
	               std::map<const std::string, std::vector<PlotUtils::MnvH1D*>> fitHists_combined,
	               std::map<const std::string, std::vector<PlotUtils::MnvH1D*>> unfitHists_combined,
                   const std::map<const std::string, PlotUtils::MnvH1D*> dataHist_combined,
                   const std::map<const std::string, bool> includeInFit, 
                   const std::vector<std::string> categories, const fit_type type, 
                   const int lowBin, const int hiBin, 
                   const double upperLimit, const bool binbybin) {
    // takes the histograms in unfitHists[slice][sample][category], fits to dataHist by combining all the samples by changing the normalization of the category templates and then makes fitHists[slice][sample][category] which contains the best template fit for each universe.
    // writes the chi2 value, parameters and covariance of the parameters into the output root file but does not return them.

    // make a fitter
    auto* mini2 = new ROOT::Minuit2::Minuit2Minimizer(ROOT::Minuit2::kCombined);

    int ncat = categories.size();
    
    std::map<std::string,int> nperuniv;
    
    std::vector<TMatrixD> variants_all;
	std::vector<TVectorD> theparameters_all;
	std::map<int,std::map<std::string,std::vector<TMatrixDSym>>> CovMatrix_all;
	std::vector<std::vector<double>> ScaleResults_all;
	
	std::vector<std::string> universes;
	
	for (auto slice : dataHist){
		// the fit code wants TH1D so make a copy of the data for that purpose
		std::map<const std::string, TH1D*> dataHistCV;
		TString aname;
		int count = 0;
		for (auto sample : dataHist.at(slice.first)) {
		    if (count == 0) {
		        aname = dataHist.at(slice.first).at(sample.first)->GetName();
		        count++;
		    }
		    dataHistCV[sample.first] = (TH1D*)dataHist.at(slice.first).at(sample.first)->Clone();
		}
		std::cout << std::endl << "count = " << count << std::endl;

		// long winded way to pull out the universes list
		// could make this in to a consistency check later.
		// this assumes that all histograms have the same universes, which they really should

		PlotUtils::MnvH1D* ahist;
		int acount = 0;

		for (auto sample : unfitHists.at(slice.first)) {
		    acount++;
		    if (acount > 1) continue;
		    ahist = sample.second.at(0);
		    universes = ahist->GetVertErrorBandNames();
		    universes.push_back("CV");
		    std::cout << " universe names:" ;
		    for (auto a:universes){
		        std::cout << a;
		        if (a == "CV") std::cout << "";
		        else std::cout << ", ";
		    }
		    std::cout << std::endl;
		}
		

		// make objects to contain the fit information
		PlotUtils::MnvH1D parameters(TString("parameters_" + aname), "fit parameters", ncat, 0.0, double(ncat));
		PlotUtils::MnvH2D covariance(TString("covariance_" + aname), "fit parameters", ncat, 0.0, double(ncat), ncat, 0.0, double(ncat));
		PlotUtils::MnvH2D correlation(TString("correlation_" + aname), "fit parameters", ncat, 0.0, double(ncat), ncat, 0.0, double(ncat));
		PlotUtils::MnvH1D fcn(TString("fcn" + aname), "fcn", 1, 0., 1.);

		TMatrixD variants(ncat,ncat);
		TVectorD theparameters(ncat);
		TMatrixDSym CovMatrix(ncat,ncat);
		CovMatrix.ResizeTo(ncat,ncat);
		
		//int ndim;//

		// add in the CV so you do a loop over universes
		//  now loop over all universes and fit each one
		for (auto univ : universes) {
		    std::cout << "Universe is " << univ << " " << universes.size() << std::endl;
		    int nuniv;
		    if (univ != "CV") {
		        nuniv = ahist->GetVertErrorBand(univ)->GetNHists();
		        fcn.AddVertErrorBandAndFillWithCV(univ, nuniv);
		        parameters.AddVertErrorBandAndFillWithCV(univ, nuniv);
		        covariance.AddVertErrorBandAndFillWithCV(univ, nuniv);
		        correlation.AddVertErrorBandAndFillWithCV(univ, nuniv);
		    } else {
		        nuniv = 1;
		    }	
		    if(slice.first==1) {
		    	nperuniv[univ] = nuniv;
		    }
		    // loop over universes within a band
		    for (int iuniv = 0; iuniv < nuniv; iuniv++) {
		        std::cout << " now do the fit for " << univ << " " << iuniv << std::endl;
		        // make a local TH1F map unfitHistsCV that the fitter expects
		        std::map<const std::string, std::vector<TH1D*>> unfitHistsCV;
		        if (univ == "CV") {
		            for (auto sample : unfitHists.at(slice.first)) {
		                for (int i = 0; i < ncat; i++) {
		                    TString name = unfitHists.at(slice.first).at(sample.first).at(i)->GetName() + TString("_" + univ);
		                    TH1D* hist = (TH1D*)unfitHists.at(slice.first).at(sample.first).at(i)->Clone(name);
		                    hist->Print();
		                    unfitHistsCV[sample.first].push_back(hist);
		                }
		            }
		        } else {
		            for (auto sample : unfitHists.at(slice.first)) {
		                for (int i = 0; i < ncat; i++) {
		                    PlotUtils::MnvVertErrorBand* errorband = unfitHists.at(slice.first).at(sample.first).at(i)->GetVertErrorBand(univ);
		                    if (errorband == 0) {
		                        std::cout << " no such band " << std::endl;
		                    }
		                    TString name = errorband->GetName();
		                    name += TString("_" + univ);
		                    TH1D* hist = (TH1D*)errorband->GetHist(iuniv)->Clone(name);
		                    hist->Print();
		                    unfitHistsCV[sample.first].push_back(hist);
		                }
		            }
		        }
		        std::cout << " have made the local samples for this universe" << std::endl;

		        //for (int thebin = lowBin; thebin <= hiBin; thebin++) {
		        if (true){
		            fit::MultiScaleFactors func2(unfitHistsCV, dataHistCV, includeInFit, type, lowBin, hiBin);

		            // set parameters with lower limit of 0
		            int nextPar = 0;
		            int ndim = func2.NDim();
		            for (unsigned int i = 0; i < func2.NDim(); ++i) {
		                std::string name = categories[i];
		                std::cout << " set parameter " << i << " " << name << std::endl;
		                mini2->SetLowerLimitedVariable(i, name, 1.0, 0.1, 0.0);
		                //mini2->SetUpperLimitedVariable(i, name, 1.0, 0.1, upperLimit);
		                nextPar++;
		            }

		            if (nextPar != func2.NDim()) {
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
		            if (status > 1) {
		                std::cout << "Printing Results." << std::endl;
		                mini2->PrintResults();
		                std::cout << "FIT FAILED" << std::endl;
		                success = false;
		                // return 7;
		            } else {
		                std::cout << "Printing Results." << std::endl;
		                mini2->PrintResults();
		                std::cout << "FIT SUCCEEDED" << std::endl;
		                success = true;
		            }

		            // have done the fit, now rescale all histograms by the appropriate scale factors

		            const double* combScaleResults = mini2->X();
		            // make it a vector.
		            std::vector<double> ScaleResults;

		            ndim = func2.NDim();
		            
		            //std::cout << "ncat" << ncat << std::endl;
		            //CovMatrix.Print();
		            for (int i = 0; i < ndim; i++) {
		                ScaleResults.push_back(combScaleResults[i]);
		                //if (univ == "CV"){
		                for (int j = 0; j < ndim; j++){
		                    //std::cout << i << " " << j << std::endl;
		                    CovMatrix[i][j] = mini2->CovMatrix(i, j);
		                }
		                //}
		            }
		            CovMatrix.Print();
					//CovMatrix_all[slice.first] = CovMatrix;
					CovMatrix_all[slice.first][univ].push_back(CovMatrix);
		            //ScaleResults_all[slice.first] = ScaleResults;
		            ScaleResults_all.push_back(ScaleResults);

		            if (!success) {
		                // if it failed, just scale the components to the data with the original ratios
		                for (auto sample : fitHists.at(slice.first)) {
		                    double tot = 0;
		                    double data = dataHist.at(slice.first).at(sample.first)->Integral(lowBin, hiBin);
		                    for (int i = 0; i < func2.NDim(); i++) {
		                        if (univ == "CV") {
		                            tot += fitHists.at(slice.first).at(sample.first).at(i)->Integral(lowBin, hiBin);
		                        } else {
		                            PlotUtils::MnvVertErrorBand* errorband = fitHists.at(slice.first).at(sample.first).at(i)->GetVertErrorBand(univ);
		                            tot += errorband->GetHist(iuniv)->Integral(lowBin, hiBin);
		                        }
		                        ScaleResults[i] = data / tot;
		                    }
		                }
		            }  // end of failure
		            // print out the parameters
		            std::cout << "fix" << success << " " << status << " " << univ << " " << iuniv << " " << status;
		            for (int i = 0; i < func2.NDim(); i++) {
		                std::cout << " test " << i << " " << combScaleResults[i] << " " << ScaleResults[i];
		            }
		            std::cout << std::endl;

		            // now record the parameters and rescale the template to return as fitHists
		            std::cout << "Universe is " << univ << std::endl;
		            //theparameters.ResizeTo(ncat);
		            if (univ == "CV") {
		                fcn.SetBinContent(1, mini2->MinValue());
		                for (int i = 0; i < func2.NDim(); i++) {
		                    parameters.SetBinContent(i + 1, ScaleResults[i]);
		                    theparameters[i] = ScaleResults[i]; // persistent outside loops
		                    for (int j = 0; j < func2.NDim(); j++) {
		                        covariance.SetBinContent(i + 1, j + 1, mini2->CovMatrix(i, j));
		                    }
		                    double err = std::sqrt(covariance.GetBinContent(i + 1, i + 1));
		                    parameters.SetBinError(i+1,err);
		                }
		                //theparameters_all[slice.first] = theparameters;
		                theparameters_all.push_back(theparameters);
		                for (int i = 0; i < func2.NDim(); i++) {
		                    double erri = parameters.GetBinError(i+1);
		                    for (int j = 0; j < func2.NDim(); j++) {
		                        double errj = parameters.GetBinError(j + 1);
		                        correlation.SetBinContent(i + 1, j + 1, covariance.GetBinContent(i+1,j+1)/erri/errj);
		                    }
		                }
		                //variants.ResizeTo(ncat,ncat);
		                //variants  = covbands(ScaleResults, CovMatrix);

		                    // parameters.Print("ALL");
		                    // parameters.Write();
		                    //  hack the main histogram by brute force
		                for (auto sample : fitHists.at(slice.first)) {
		                    const std::string myname = sample.first;
		                    const int myslice = slice.first;
		                    for (int i = 0; i < func2.NDim(); i++) {
		                    	// not sure why using []'s here instead of .at()'s. Maybe to save space
		                        int nbins = fitHists[myslice][myname][i]->GetNbinsX();
		                        std::cout << "scale CV (slice " << myslice << ") " << myname << " " << i << " " << ScaleResults[i] << std::endl;
		                        //fitHists[myslice][myname][i]->Print();
		                        //unfitHists[myslice][myname][i]->Print();
		                        for (int j = lowBin; j <= hiBin; j++) {
		                            fitHists[myslice][myname][i]->SetBinContent(j, unfitHists[myslice][myname][i]->GetBinContent(j) * ScaleResults[i]);
		                            fitHists[myslice][myname][i]->SetBinError(j, unfitHists[myslice][myname][i]->GetBinError(j) * ScaleResults[i]);
		                        }
		                    }
		                }
		                for (auto sample : fitHists_combined) {
		                    const std::string myname = sample.first;
		                    for (int i = 0; i < func2.NDim(); i++) {
		                        int nbins = fitHists_combined[sample.first][i]->GetNbinsX();
		                        std::cout << "scale CV" << myname << " " << i << " " << ScaleResults[i] << std::endl;
	                            fitHists_combined[myname][i]->SetBinContent(slice.first, unfitHists_combined[myname][i]->GetBinContent(slice.first) * ScaleResults[i]);
	                            fitHists_combined[myname][i]->SetBinError(slice.first, unfitHists_combined[myname][i]->GetBinError(slice.first) * ScaleResults[i]);
		                    }
		                }
		            } 
		            else {  // not CV
		                std::cout << " non CV Universe" << univ << std::endl;
		                // scale the error bands appropriately and record the changes in fcn, parameter, covariance
		                TH1D* fcnhist = fcn.GetVertErrorBand(univ)->GetHist(iuniv);
		                fcnhist->SetBinContent(1, mini2->MinValue());
		                TH1D* phist = parameters.GetVertErrorBand(univ)->GetHist(iuniv);
		                TH2D* chist = covariance.GetVertErrorBand(univ)->GetHist(iuniv);
		                TH2D* corhist = correlation.GetVertErrorBand(univ)->GetHist(iuniv);
		                for (int i = 0; i < ncat; i++) {
		                    phist->SetBinContent(i + 1, ScaleResults[i]);
		                    for (int j = 0; j < ncat; j++) {
		                        chist->SetBinContent(i + 1, j + 1, mini2->CovMatrix(i, j));
		                    }
		                }
		                for (int i = 0; i < func2.NDim(); i++) {
		                    double erri = phist->GetBinError(i + 1);
		                    for (int j = 0; j < func2.NDim(); j++) {
		                        double errj = phist->GetBinError(j + 1);
		                        corhist->SetBinContent(i + 1, j + 1, chist->GetBinContent(i + 1, j + 1) / erri / errj);
		                    }
		                }
		                for (auto sample : unfitHists.at(slice.first)) {
		                    // need to figure out how to fill the fcn/parameter/covariance error bands.

		                    for (int i = 0; i < ncat; i++) {
		                        PlotUtils::MnvVertErrorBand* errorband = unfitHists.at(slice.first).at(sample.first).at(i)->GetVertErrorBand(univ);
		                        PlotUtils::MnvVertErrorBand* newerrorband = fitHists.at(slice.first).at(sample.first).at(i)->GetVertErrorBand(univ); 
		                                        
		                        TH1D* hist = errorband->GetHist(iuniv);
		                        TH1D* newhist = newerrorband->GetHist(iuniv);

		                        for (int j = lowBin; j <= hiBin; j++) {
		                            // HMS change to only do the bin range
		                            newhist->SetBinContent(j, hist->GetBinContent(j) * ScaleResults[i]);
		                            newhist->SetBinError(j, hist->GetBinError(j) * ScaleResults[i]);
		                        }

		                        // if (true) {
		                        //     std::cout << "check bands" << i << " " << univ << " " << iuniv << std::endl;
		                        //     hist->Print();
		                        //     newhist->Print();
		                        // }
		                    }
		                    // hist->Scale(ScaleResults[i]);
		                }
		                for (auto sample : unfitHists_combined) {
		                    for (int i = 0; i < ncat; i++) {
		                    	PlotUtils::MnvVertErrorBand* errorband_combined = unfitHists_combined.at(sample.first).at(i)->GetVertErrorBand(univ);
		                        PlotUtils::MnvVertErrorBand* newerrorband_combined = fitHists_combined.at(sample.first).at(i)->GetVertErrorBand(univ);
		                                      
		                        TH1D* hist_combined = errorband_combined->GetHist(iuniv);
		                        TH1D* newhist_combined = newerrorband_combined->GetHist(iuniv);
		                        
		                        newhist_combined->SetBinContent(slice.first, hist_combined->GetBinContent(slice.first) * ScaleResults[i]);
		                        newhist_combined->SetBinError(slice.first, hist_combined->GetBinError(slice.first) * ScaleResults[i]);
		                    }
						}
		            }
				}
		    }  // end of nuniv loop
		    
		}  // end of universes loop

		int neigen=3;  // only use the top 3 eigenvalues. 
		// variants.ResizeTo(ncat,ncat);
		variants = extrabands(CovMatrix);
		for (int var = 0; var< ncat; var++){
		    TVectorD tmp = variants[var];
		    tmp.Print();
		}
		//variants_all[slice.first] = variants;
		variants_all.push_back(variants);

		for (auto sample : fitHists.at(slice.first)){ //loop over samples
		    
		    for (int i = 0; i < ncat; i++){  // loop over categories for that sample
		        fitHists.at(slice.first).at(sample.first).at(i)->AddVertErrorBandAndFillWithCV(std::string("FitVariations"), neigen * 2);
		        PlotUtils::MnvVertErrorBand* errorband = fitHists.at(slice.first).at(sample.first).at(i)->GetVertErrorBand("FitVariations");
		        for (int var = 0; var < neigen; var++){ // loop over variations
		            for (int k = 0; k < 2; k++){
		                int iuniv = var*2+k;

		                TH1D* hist = errorband->GetHist(iuniv);

		                int sign = (2*k)-1;
		                // central value already scaled by the fit parameter so have to back it off. 
		                double variation = (1. + variants[var][i] * sign/theparameters[i]);
		                //std::cout << "factor" << var << " " << i << " " << variation << std::endl;
		                //hist->Scale(variation);
		                //hist->Print();
		                
		                for (int j = lowBin; j <= hiBin; j++) {
		                    hist->SetBinContent(j, hist->GetBinContent(j)*variation);
		                }

		                std::cout << "varied by " << sample.first << " " << i << " " << iuniv << " " << theparameters[i] << " " << variants[var][i] << " " << variation << " " << theparameters[i]*variation << std::endl;
		             }      
		        }
		    }
		}
		for (auto sample : fitHists.at(slice.first)) {
		    for (int i = 0; i < ncat; i++) {
		        SyncBands(fitHists[slice.first][sample.first][i]);
		        std::string fitname = sample.first + "_" + std::to_string(slice.first) + "_" + std::to_string(i);
		        fitHists[slice.first][sample.first][i]->MnvH1DToCSV(fitname, "./csv/", 1.0, false);
		    }
		}

		SyncBands(&fcn);
		SyncBands(&parameters);
		SyncBands(&covariance);
		SyncBands(&correlation);

		fcn.MnvH1DToCSV("fcn", "./csv/");
		fcn.Write();
		parameters.MnvH1DToCSV("parameters", "./csv/");
		covariance.MnvH2DToCSV("covariance", "./csv/");
		correlation.MnvH2DToCSV("correlation", "./csv/");
		parameters.Write();
		covariance.Write();
		correlation.Write();
    }
    
	
	/*std::cout << std::endl << std::endl << "Covariance Matrices:" << std::endl;
	for (auto slice : CovMatrix_all) {
		for (auto univ : slice.second) {
			for (int i=0; i<univ.second.size(); i++) {
				std::cout << slice.first << " " << univ.first << " " << i << std::endl;
				univ.second[i].Print();
				std::cout << std::endl;
			}
		}
	}
	std::cout << std::endl;*/
	
	/*std::cout << std::endl << std::endl << "variants_all.size() = " << variants_all.size() << std::endl;
	std::cout << "theparameters_all.size() = " << theparameters_all.size() << std::endl;
	std::cout << "hiBin = " << hiBin << std::endl << std::endl;*/
	
	int neigen = 3;
    for (auto sample : fitHists_combined){ //loop over samples  
	    for (int i = 0; i < ncat; i++){  // loop over categories for that sample
	        fitHists_combined.at(sample.first).at(i)->AddVertErrorBandAndFillWithCV(std::string("FitVariations"), neigen * 2);
	        PlotUtils::MnvVertErrorBand* errorband_combined = fitHists_combined.at(sample.first).at(i)->GetVertErrorBand("FitVariations");
	        for (int var = 0; var < neigen; var++){ // loop over variations
	            for (int k = 0; k < 2; k++){
	                int iuniv = var*2+k;
					TH1D* hist_combined = errorband_combined->GetHist(iuniv);
		            int sign = (2*k)-1;
	                for (int j=0; j<theparameters_all.size(); j++) {
			            // central value already scaled by the fit parameter so have to back it off. 
			            double variation = (1. + variants_all[j][var][i] * sign/theparameters_all[j][i]);
	                    hist_combined->SetBinContent(j+1, hist_combined->GetBinContent(j+1)*variation);
	                    
	                    std::cout << "bin " << j+1 << " varied by " << sample.first << " " << i << " " << iuniv << " " << theparameters_all[j][i] << " " << variants_all[j][var][i] << " " << variation << " " << theparameters_all[j][i]*variation << std::endl;
	                }
	             }      
	        }
	    }
	}
	for (auto sample : fitHists_combined) {
	    for (int i = 0; i < ncat; i++) {
	        SyncBands(fitHists_combined[sample.first][i]);
	    }
	}
    
    return 0;
}

}  // namespace fit
// end namespace
