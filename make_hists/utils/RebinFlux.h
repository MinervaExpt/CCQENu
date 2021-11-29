// utilities to deal with flux

#ifndef REBIN_FLUX_H
#define REBIN_FLUX_H
#include <string>
#include <map>
#include "utils/NuConfig.h"
#include "PlotUtils/MnvH1D.h"
#include "TFile.h"


// - return a flux histogram for the playlist in config with bin width correction removed - integral is total flux


MnvH1D* GetFlux(const NuConfig config);

// - get the flux histogram derived above back rebinned according to histogram ehist

MnvH1D* GetFluxEbins(const MnvH1D* h_flux_dewidthed, const MnvH1D* ehist );
MnvH2D* GetFluxEbins(const MnvH1D* h_flux_dewidthed, const MnvH2D* ehist );

// DeWidth -- utility to remove binwidth correction from an MnvH1D
void DeWidth(MnvH1D* h_mnv_with_binwidth, MnvH1D *&h_mnv_with_binwidth_removed){

  //cout << "TRACE: remove binwidth correction from MnvH1D " << h_mnv_with_binwidth->GetName() << endl;

  //strategy is to recale orig by bin width (undo bin width normalization) then combine bins and then rescale by binwidth again
  MnvH1D* scaler = (MnvH1D*)h_mnv_with_binwidth->Clone("widths");
  scaler->SetDirectory(0);
  std::string name = h_mnv_with_binwidth->GetName();
  name += std::string("_counts");

  double flux = 0.0;
  for(int i=0;i<scaler->GetNbinsX()+2;i++) {
    scaler->SetBinContent(i,scaler->GetBinWidth(i));
    flux += scaler->GetBinWidth(i)*h_mnv_with_binwidth->GetBinContent(i);
    // std::cout << "bin " << i << " " << scaler->GetBinCenter(i) << " " << scaler->GetBinWidth(0) << " " << h_mnv_with_binwidth->GetBinContent(i)<< " "  << flux << std::endl;
  }
  h_mnv_with_binwidth_removed = (MnvH1D*)h_mnv_with_binwidth->Clone(name.c_str());
  h_mnv_with_binwidth_removed->SetDirectory(0);
  h_mnv_with_binwidth_removed->MultiplySingle(h_mnv_with_binwidth,scaler, 1., 1.);//undid bin width normalization
  //std::cout << "integral for mnv after removing binwidth correction " << h_mnv_with_binwidth_removed->GetName() << " is " <<  h_mnv_with_binwidth_removed->Integral() << std::endl;
}

// rebin an MnvH1D to match a different subset of bins
template <class HistoType1D>
  HistoType1D* RebinDeWidthedFluxHist(const HistoType1D* h_mnv_without_binwidth, const HistoType1D * h_mnv_rebinned_without_binwidth){
    // this operates on a dewidthed as we want total counts.
    //cout << "TRACE: Rebin an MnvH1D " << h_mnv_without_binwidth->GetName() << " into  "  << h_mnv_rebinned_without_binwidth->GetName() << endl;
    std::vector<double>mnv_rebinned_without_binwidth_bin_edges;
    for(int i=1;i<h_mnv_rebinned_without_binwidth->GetNbinsX()+2;i++){//need low edge of overflow (high edge of last bin)
      mnv_rebinned_without_binwidth_bin_edges.push_back(h_mnv_rebinned_without_binwidth->GetBinLowEdge(i));
    }
    HistoType1D* not_rebinned = (HistoType1D*)h_mnv_without_binwidth->Clone();  // have to do this as otherwise the rebin occurs multiple times
    HistoType1D* new_rebinned = (HistoType1D*)h_mnv_rebinned_without_binwidth->Clone();
    new_rebinned->SetDirectory(0);
    new_rebinned = (HistoType1D*)not_rebinned->Rebin(mnv_rebinned_without_binwidth_bin_edges.size()-1,"Rebinned",&mnv_rebinned_without_binwidth_bin_edges[0]);
    new_rebinned->SetName("flux");
    //new_rebinned->Print("ALL");
    //cout << "TRACE: Rebin an MnvH1D " << h_mnv_without_binwidth->GetName() << " into  "  << new_rebinned->GetName() << endl;
    return new_rebinned;
  }

template MnvH1D* RebinDeWidthedFluxHist<MnvH1D>(const MnvH1D* h_mnv_without_binwidth, const MnvH1D * h_mnv_rebinned_without_binwidth);
// TH1D is sometimes useful for doing 2D stuff
template TH1D* RebinDeWidthedFluxHist<TH1D>(const TH1D* h_mnv_without_binwidth, const TH1D * h_mnv_rebinned_without_binwidth);

// sometimes you need to make # of universes match - this does that

void TruncateNumberOfFluxUniverses( MnvH1D* h, int nUniverses)
{
  MnvVertErrorBand *poppedFluxErrorBand = h->PopVertErrorBand("Flux");
  std::vector<TH1D*> fluxUniverses = poppedFluxErrorBand->GetHists();
  fluxUniverses.resize(nUniverses);
  h->AddVertErrorBand("Flux",fluxUniverses);
  //CheckAndFixFluxErrorBand(h);
}
//2D
void TruncateNumberOfFluxUniverses( MnvH2D* h, int nUniverses)
{
  MnvVertErrorBand2D *poppedFluxErrorBand = h->PopVertErrorBand("Flux");
  std::vector<TH2D*> fluxUniverses = poppedFluxErrorBand->GetHists();
  fluxUniverses.resize(nUniverses);
  h->AddVertErrorBand("Flux",fluxUniverses);
  //CheckAndFixFluxErrorBand(h);
}
// implementation of GetFlux
MnvH1D* GetFlux(const NuConfig config){
  std::string playlist = config.GetString("playlist");
  int m_fluxUniverses = config.GetInt("fluxUniverses");
  bool m_nue_constraint = config.GetInt("NuEConstraint");
  int pdg = config.GetInt("pdg");

  //++++++++++++++++++=  Initialization +++++++++++++++++++++++++

  // Get the flux hist, clean it up a bit, remove binwidth correction that should not be there and return

  // someone thought an enum was a good idea.  It was not.
  std::map<std::string, enum FluxReweighter::EPlaylist> fluxplaylist;
  fluxplaylist["minervame1A"] = FluxReweighter::minervame1A;
  fluxplaylist["minervame1B"] = FluxReweighter::minervame1B;
  fluxplaylist["minervame1C"] = FluxReweighter::minervame1C;
  fluxplaylist["minervame1D"] = FluxReweighter::minervame1D;
  fluxplaylist["minervame1E"] = FluxReweighter::minervame1E;
  fluxplaylist["minervame1F"] = FluxReweighter::minervame1F;
  fluxplaylist["minervame1G"] = FluxReweighter::minervame1G;
//  fluxplaylist["minervame1H"] = FluxReweighter::minervame1H;
//  fluxplaylist["minervame1I"] = FluxReweighter::minervame1I;
//  fluxplaylist["minervame1J"] = FluxReweighter::minervame1J;
//  fluxplaylist["minervame1K"] = FluxReweighter::minervame1K;
  fluxplaylist["minervame1L"] = FluxReweighter::minervame1L;
  fluxplaylist["minervame1M"] = FluxReweighter::minervame1M;
  fluxplaylist["minervame1N"] = FluxReweighter::minervame1N;
  fluxplaylist["minervame5A"] = FluxReweighter::minervame5A;
  fluxplaylist["minervame6A"] = FluxReweighter::minervame6A;
  fluxplaylist["minervame6B"] = FluxReweighter::minervame6A;
  fluxplaylist["minervame6C"] = FluxReweighter::minervame6A;
  fluxplaylist["minervame6D"] = FluxReweighter::minervame6A;
  fluxplaylist["minervame6E"] = FluxReweighter::minervame6A;
  fluxplaylist["minervame6F"] = FluxReweighter::minervame6A;
  fluxplaylist["minervame6G"] = FluxReweighter::minervame6A;
  fluxplaylist["minervame6H"] = FluxReweighter::minervame6A;
  fluxplaylist["minervame6I"] = FluxReweighter::minervame6A;
  fluxplaylist["minervame6J"] = FluxReweighter::minervame6A;

  if( fluxplaylist.find(playlist) == fluxplaylist.end() ){
    std::cout << " playlist " << playlist << " not yet implemented in RebinFlux.h " << std::endl;
    exit(0);
  }

  FluxReweighter *frw = new PlotUtils::FluxReweighter(pdg,m_nue_constraint,fluxplaylist[playlist],FluxReweighter::gen2thin, FluxReweighter::g4numiv6,m_fluxUniverses);

  MnvH1D *h_flux = frw->GetFluxReweighted(pdg);
  h_flux->SetDirectory(0);
  // clean up the external flux by removing error bands we won't use in this analysis
  h_flux->PopVertErrorBand("Flux_BeamFocus");
  h_flux->PopVertErrorBand("ppfx1_Total");
  TruncateNumberOfFluxUniverses(h_flux,m_fluxUniverses);

  //
  //  flux hist is stored with binwidth correction, need to undo that to get the integral and use for sigma(E)
  //
  MnvH1D* h_flux_dewidthed;

  DeWidth(h_flux,h_flux_dewidthed);
  h_flux_dewidthed->SetName("flux_dewidthed");
  h_flux_dewidthed->Scale(1/10000.); // convert from m^2 to cm^2
  return h_flux_dewidthed;
}

// given energy histogram, rebin flux to match
MnvH1D* GetFluxEbins(const MnvH1D* h_flux_dewidthed, const MnvH1D* ihist, NuConfig config, std::map<std::string, bool> FluxEnormBool){
  TString newname = ihist->GetName()+TString("_Flux");
  MnvH1D* h_flux_ebins = RebinDeWidthedFluxHist(h_flux_dewidthed,ihist);
  h_flux_ebins->SetName(newname);
  h_flux_ebins->SetTitle("Integrated Flux/bin; GeV");
  // reapply the bin width correction to flux(this cancels out the plotter applying it later to the numerator)
  h_flux_ebins->Scale(1.0,"width");
  return h_flux_ebins;
}


MnvH2D* GetFluxEbins(const MnvH1D* h_flux, const MnvH2D* ihist , NuConfig config, std::map<std::string, bool> FluxEnormBool){  //std::vector<std::string> varparse){
  // hist that will come out with flux hist in bins you want
  MnvH2D* h2D_flux_ebins = (MnvH2D*)ihist->Clone();
  // changed ehist to h2D_flux_ebins
  // MnvH2D* ehist = (MnvH2D*)enu_hist->Clone();
  h2D_flux_ebins->ClearAllErrorBands(); // need to do this so you can add them back later.
  h2D_flux_ebins->Reset();
  // Make a blank dummy hist
  MnvH2D* dummyhist; //->Divide(h2D_flux_ebins,h2D_flux_ebins,1.,1.);
  if( !FluxEnormBool["xfluxnorm"] && !FluxEnormBool["yfluxnorm"]){
    std::cout << " fluxnorm not set for axes. Doing flat flux instead." << std::endl;
    // MnvH2D* flux = GetFluxFlat(config,ihist);
    // return flux;
    return dummyhist;
  }
  if( FluxEnormBool["xfluxnorm"] && FluxEnormBool["yfluxnorm"]){
    std::cout << " Both axes have energy dependent flux normalization, which isn't implimented yet." << std::endl;
    // MnvH2D* flux = GetFluxFlat(config,ihist);
    // return flux;
    return dummyhist;
  }


  // Take projection on x or y axis (depending on which variable is on which axis) to get input hist binning for 1D flux
  MnvH1D* ihistproj;
  if(FluxEnormBool["xfluxnorm"] && !FluxEnormBool["yfluxnorm"]) {
    std::cout << " Using an energy dependent flux for the x axis. " << std::endl;
    ihistproj = h2D_flux_ebins->ProjectionX("_proj_x",0,-1);
  }
  if(FluxEnormBool["yfluxnorm"] && !FluxEnormBool["xfluxnorm"]) {
    std::cout << " Using an energy dependent flux for the y axis. " << std::endl;
    ihistproj = h2D_flux_ebins->ProjectionY("_proj_y",0,-1);
  }

  // Borrowed from 1D code
  MnvH1D* h_flux_dewidthed = (MnvH1D*)h_flux->Clone();
  // Rebin flux to energy hist bins, Amit works with TH1D's for all this...
  MnvH1D* mnvh_rebinned_flux = RebinDeWidthedFluxHist(h_flux_dewidthed,ihistproj);
  mnvh_rebinned_flux->SetTitle("Integrated Flux/projected bin; GeV");
  // reapply the bin width correction to flux(this cancels out the plotter applying it later to the numerator)
  // is this necessary for 2D?
  mnvh_rebinned_flux->Scale(1.0,"width");

  // Borrowed from Amit's code. Don't need hist tmphist though, since already rebinned flux.
  TH1D* h_rebinned_flux = new TH1D(mnvh_rebinned_flux->GetCVHistoWithStatError());
  // find number of bins to help rebin the flux
  const int nxbins = h2D_flux_ebins->GetNbinsX();
  const int nybins = h2D_flux_ebins->GetNbinsY();
  // Fill the 2D flux hist with contents of 1D. Filling by xbins or ybins depending on the case.
  for(int i=0;i<nxbins+1;i++){
    for(int j=0;j<nybins+1;j++){
        if(FluxEnormBool["xfluxnorm"] && !FluxEnormBool["yfluxnorm"]) h2D_flux_ebins->SetBinContent(i,j,h_rebinned_flux->GetBinContent(i));
        if(FluxEnormBool["yfluxnorm"] && !FluxEnormBool["xfluxnorm"]) h2D_flux_ebins->SetBinContent(i,j,h_rebinned_flux->GetBinContent(j));
    }
  }
  // TODO: Binwidth is being corrected too many times or not enough on 2D
  // look at cheryl's paper about this
  // Is this ^^^ true??? May need to do binwidth correction for 2D on my own. NHV, 6/22

  // This hist doesn't have (vertical) errorbands, so we'll need to do the same for them.


  std::cout << "Now for verts" << endl;
  int nfluxUniverses = config.GetInt("fluxUniverses");
  //Do the same with the vertical error bands
  std::vector<std::string> vertNames = h_flux_dewidthed->GetVertErrorBandNames();
  for(unsigned int k=0; k<vertNames.size(); ++k ){
    MnvVertErrorBand *errBand = h_flux_dewidthed->GetVertErrorBand( vertNames[k] );
    int nuniverses = errBand->GetNHists();
    if(vertNames[k]=="Flux") nuniverses = nfluxUniverses;//cout << "Flux Universes = " << universes << endl;
    if(vertNames[k].find("_BeamFocus")!=-1||vertNames[k].find("ppfx1_Total")!=-1) continue;
    std::vector<TH2D*> vert_hists;
    std::cout << "Working on " << vertNames[k] << endl;
    for(int u=0 ; u < nuniverses; ++u)
      {
        TH2D *h_vert = new TH2D( (TH2D)*h2D_flux_ebins);
        h_vert->SetName( Form("h_vert_%s_%i", vertNames[k].c_str(), u) );
        //strategy is get 1D th1d and fill up h_flux_normalization
        TH1D* univerrBand = new TH1D(*errBand->GetHist(u));
        RebinDeWidthedFluxHist(univerrBand, h_rebinned_flux);
        for(int i=0;i<nxbins+1;i++){
          for(int j=0;j<nybins+1;j++){
            h_vert->SetBinContent(i,j,h_rebinned_flux->GetBinContent(i));
          }
        }
        vert_hists.push_back( h_vert );
      }
    h2D_flux_ebins->AddVertErrorBand( vertNames[k], vert_hists );
    //cleaning
    for(std::vector<TH2D*>::iterator itHist = vert_hists.begin(); itHist != vert_hists.end(); ++itHist)
      delete *itHist;
  }
  return h2D_flux_ebins;
}


// implementation of GetFlux for a special histogram
template<class MnvHistoType>
  MnvHistoType* GetFluxFlat(const NuConfig config,  MnvHistoType* h){

    std::string playlist = config.GetString("playlist");
    int m_fluxUniverses = config.GetInt("fluxUniverses");
    bool m_nue_constraint = config.GetInt("NuEConstraint");
    int pdg = config.GetInt("pdg");

    //++++++++++++++++++=  Initialization +++++++++++++++++++++++++

    // Get the flux hist, clean it up a bit, remove binwidth correction that should not be there and return

    // someone thought an enum was a good idea.  It was not.
    std::map<std::string, enum FluxReweighter::EPlaylist> fluxplaylist;
    fluxplaylist["minervame1A"] = FluxReweighter::minervame1A;
    fluxplaylist["minervame1B"] = FluxReweighter::minervame1B;
    fluxplaylist["minervame1C"] = FluxReweighter::minervame1C;
    fluxplaylist["minervame1D"] = FluxReweighter::minervame1D;
    fluxplaylist["minervame1E"] = FluxReweighter::minervame1E;
    fluxplaylist["minervame1F"] = FluxReweighter::minervame1F;
    fluxplaylist["minervame1G"] = FluxReweighter::minervame1G;
    fluxplaylist["minervame1H"] = FluxReweighter::minervame1G;
    fluxplaylist["minervame1I"] = FluxReweighter::minervame1G;
    fluxplaylist["minervame1J"] = FluxReweighter::minervame1G;
    fluxplaylist["minervame1K"] = FluxReweighter::minervame1G;
    fluxplaylist["minervame1L"] = FluxReweighter::minervame1G;
    fluxplaylist["minervame1M"] = FluxReweighter::minervame1M;
    fluxplaylist["minervame1N"] = FluxReweighter::minervame1N;
    fluxplaylist["minervame1O"] = FluxReweighter::minervame1N;
    fluxplaylist["minervame1P"] = FluxReweighter::minervame1N;
//anti-nu
    fluxplaylist["minervame5A"] = FluxReweighter::minervame5A;
    fluxplaylist["minervame6A"] = FluxReweighter::minervame6A;
    fluxplaylist["minervame6B"] = FluxReweighter::minervame6A;
    fluxplaylist["minervame6C"] = FluxReweighter::minervame6A;
    fluxplaylist["minervame6D"] = FluxReweighter::minervame6A;
    fluxplaylist["minervame6E"] = FluxReweighter::minervame6A;
    fluxplaylist["minervame6F"] = FluxReweighter::minervame6A;
    fluxplaylist["minervame6G"] = FluxReweighter::minervame6A;
    fluxplaylist["minervame6H"] = FluxReweighter::minervame6A;
    fluxplaylist["minervame6I"] = FluxReweighter::minervame6A;
    fluxplaylist["minervame6J"] = FluxReweighter::minervame6A;

    if( fluxplaylist.find(playlist) == fluxplaylist.end() ){
      std::cout << " playlist " << playlist << " not yet implemented in RebinFlux.h " << std::endl;
      exit(0);
    }


    FluxReweighter *frw = new PlotUtils::FluxReweighter(pdg,m_nue_constraint,fluxplaylist[playlist],FluxReweighter::gen2thin, FluxReweighter::g4numiv6,m_fluxUniverses);
    bool use_muon_correlations = false;
    MnvHistoType *h_flux = frw->GetIntegratedFluxReweighted<MnvHistoType>(pdg,h,0.,120., use_muon_correlations);
    h_flux->SetDirectory(0);
    // clean up the external flux by removing error bands we won't use in this analysis
    h_flux->PopVertErrorBand("Flux_BeamFocus");
    h_flux->PopVertErrorBand("ppfx1_Total");
    TruncateNumberOfFluxUniverses(h_flux,m_fluxUniverses);

    //
    //  flux hist is stored with binwidth correction, need to undo that to get the integral and use for sigma(E)
    //
    h_flux->Scale(1./10000.); //convert from m^2 to cm^2
    return h_flux;
  }

template MnvH1D* GetFluxFlat<MnvH1D>(const NuConfig config, MnvH1D* h);
template MnvH2D* GetFluxFlat<MnvH2D>(const NuConfig config, MnvH2D* h);


#endif
