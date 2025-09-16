#include "utils/BinomialMC.h"
#include <string>

#ifndef BINOMIALMC_CPP
#define BINOMIALMC_CPP
PlotUtils::MnvH1D* BinomialMC( PlotUtils::MnvH1D* hist1,  PlotUtils::MnvH1D* hist2,  TString newname) {
    int nbins = hist1->GetXaxis()->GetNbins();
    std::vector<double> n1(nbins+2);
    std::vector<double> n2(nbins+2);
    std::vector<double> err1(nbins+2);
    std::vector<double> err2(nbins+2);
    std::vector<double> err1sq(nbins+2);
    std::vector<double> err2sq(nbins+2);
    PlotUtils::MnvH1D* efficiency = (PlotUtils::MnvH1D*) hist1->Clone(newname);
    efficiency->Divide(efficiency, hist2, 1., 1., "B");
    return efficiency;
}

PlotUtils::MnvH2D* BinomialMC(PlotUtils::MnvH2D* hist1, PlotUtils::MnvH2D* hist2,  TString newname) {
    // TH2D* theCVHisto = new TH2D(*hist);
    // theCVHisto->SetDirectory(0);
    // std::vector<TString> bandnames = hist->GetErrorBandNames();
    // // std::cout << "Synching Error Band CV's with MnvH2D's CV" << hist->GetName() << std::endl;
    // //  loop this MnvH2D's bands
    // for (std::vector<TString>::_iterator bandname = bandnames.begin();
    //      bandname != bandnames.end(); ++bandname) {
    //     // std::cout << *bandname << std::endl;
    //     // band is a reference to the error band's CV histo

    //     PlotUtils::MnvVertErrorBand2D& band =
    //         *(hist->GetVertErrorBand((*bandname).c_str()));
    //     // set the BAND's CV histo to the MnvH1D's CV histo
    //     band.TH2D::operator=(*theCVHisto);
    // }
}
#endif
