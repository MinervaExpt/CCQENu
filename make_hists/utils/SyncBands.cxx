#include "utils/SyncBands.h"

#ifndef SYNC_CPP
#define SYNC_CPP
void SyncBands(PlotUtils::MnvH1D* hist) {
  TH1D* theCVHisto = new TH1D(*hist);
  theCVHisto->SetDirectory(0);
  std::vector<std::string> bandnames = hist->GetErrorBandNames();
  //std::cout << "Synching Error Band CV's with MnvH1D's CV" << hist->GetName() << std::endl;
  // loop this MnvH1D's bands
  for (std::vector<std::string>::const_iterator bandname = bandnames.begin();
       bandname != bandnames.end(); ++bandname) {
    // std::cout << *bandname << std::endl;
    // band is a reference to the error band's CV histo
     
    PlotUtils::MnvVertErrorBand& band =
        *(hist->GetVertErrorBand((*bandname).c_str()));
    // set the BAND's CV histo to the MnvH1D's CV histo
    band.TH1D::operator=(*theCVHisto);
  }
  delete theCVHisto;
}

void SyncBands(PlotUtils::MnvH2D* hist) {
  TH2D* theCVHisto = new TH2D(*hist);
  theCVHisto->SetDirectory(0);
  std::vector<std::string> bandnames = hist->GetErrorBandNames();
  //std::cout << "Synching Error Band CV's with MnvH2D's CV" << hist->GetName() << std::endl;
  // loop this MnvH2D's bands
  for (std::vector<std::string>::const_iterator bandname = bandnames.begin();
       bandname != bandnames.end(); ++bandname) {
    // std::cout << *bandname << std::endl;
    // band is a reference to the error band's CV histo
     
    PlotUtils::MnvVertErrorBand2D& band =
        *(hist->GetVertErrorBand((*bandname).c_str()));
    // set the BAND's CV histo to the MnvH1D's CV histo
    band.TH2D::operator=(*theCVHisto);
  }
}
#endif
