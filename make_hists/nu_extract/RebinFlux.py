import os,sys
from ROOT import TH1D, TH2D, TString
from PlotUtils import MnvH1D, MnvH2D, MnvVertErrorBand, MnvVertErrorBand2D
from PlotUtils import FluxReweighter
import numpy as np
# utilities to deal with flux

#ifndef REBIN_FLUX_H
#define REBIN_FLUX_H
#include <string>
#include <map>
#include "utils/NuConfig.h"
#include "PlotUtils/MnvH1D.h"
#include "TFile.h"


# - return a flux histogram for the playlist in config with bin width correction removed - integral is total flux

# HMS change to use map of configs instead of config.  Put in calls with just a config to allow backwards compatibility.  Get rid of in future as they are nasty in terms of potential memory leaks.

#MnvH1D GetFlux(NuConfig config)
#MnvH1D GetFlux(CONFIGMAP)

# - get the flux histogram derived above back rebinned according to histogram ehist

#MnvH1D GetFluxEbins(MnvH1D h_flux_dewidthed, MnvH1D ehist )
#MnvH2D GetFluxEbins(MnvH1D h_flux_dewidthed, MnvH2D ehist )

# DeWidth -- utility to remove binwidth correction from an MnvH1D
def DeWidth(h_mnv_with_binwidth):#, h_mnv_with_binwidth_removed):

  #cout , "TRACE: remove binwidth correction from MnvH1D " , h_mnv_with_binwidth.GetName() , endl

  #strategy is to recale orig by bin width (undo bin width normalization) then combine bins and then rescale by binwidth again
  scaler = MnvH1D()
  scaler = h_mnv_with_binwidth.Clone("widths")
  scaler.SetDirectory(0)
  name = h_mnv_with_binwidth.GetName()
  name += ("_counts")

  flux = 0.0
  for i in range (0,scaler.GetNbinsX()+2): 
    scaler.SetBinContent(i,scaler.GetBinWidth(i))
    flux += scaler.GetBinWidth(i)*h_mnv_with_binwidth.GetBinContent(i)
    # print("bin " , i , " " , scaler.GetBinCenter(i) , " " , scaler.GetBinWidth(0) , " " , h_mnv_with_binwidth.GetBinContent(i), " "  , flux )
  h_mnv_with_binwidth_removed = MnvH1D()
  h_mnv_with_binwidth_removed = h_mnv_with_binwidth.Clone(name)
  h_mnv_with_binwidth_removed.SetDirectory(0)
  h_mnv_with_binwidth_removed.MultiplySingle(h_mnv_with_binwidth,scaler, 1., 1.)#undid bin width normalization
  #print("integral for mnv after removing binwidth correction " , h_mnv_with_binwidth_removed.GetName(: , " is " ,  h_mnv_with_binwidth_removed.Integral(: :
  #h_mnv_with_binwidth_removed.Print()
  return h_mnv_with_binwidth_removed

# rebin an MnvH1D to match a different subset of bins
#template <class HistoType1D>
def RebinDeWidthedFluxHist(h_mnv_without_binwidth,  h_mnv_rebinned_without_binwidth):
    # this operates on a dewidthed as we want total counts.
    print( "TRACE: Rebin an MnvH1D " , h_mnv_without_binwidth.GetName() , " into  "  , h_mnv_rebinned_without_binwidth.GetName() )
    mnv_rebinned_without_binwidth_bin_edges = []
    for i in range( 1, h_mnv_rebinned_without_binwidth.GetNbinsX()+2): #need low edge of overflow (high edge of last bin:
      mnv_rebinned_without_binwidth_bin_edges.append(h_mnv_rebinned_without_binwidth.GetBinLowEdge(i))
    newbins = np.array(mnv_rebinned_without_binwidth_bin_edges)
    not_rebinned = MnvH1D()
    not_rebinned = h_mnv_without_binwidth.Clone()  # have to do this as otherwise the rebin occurs multiple times
    new_rebinned = h_mnv_rebinned_without_binwidth.Clone()
    new_rebinned.SetDirectory(0)

    print ("pre-rebin",h_mnv_rebinned_without_binwidth.GetNbinsX(),len(mnv_rebinned_without_binwidth_bin_edges))
    # new_rebinned = not_rebinned.Rebin(len(mnv_rebinned_without_binwidth_bin_edges)-1,"Rebinned",mnv_rebinned_without_binwidth_bin_edges[0])
    #not_rebinned.Print("ALL")
    new_rebinned = not_rebinned.Rebin(len(mnv_rebinned_without_binwidth_bin_edges)-1,"Rebinned",newbins)
    
    new_rebinned.SetName("flux")
    #new_rebinned.Print("ALL")
    #cout , "TRACE: Rebin an MnvH1D " , h_mnv_without_binwidth.GetName() , " into  "  , new_rebinned.GetName() , endl
    return new_rebinned
  

# template MnvH1D RebinDeWidthedFluxHist<MnvH1D>(MnvH1D h_mnv_without_binwidth, MnvH1D * h_mnv_rebinned_without_binwidth)
# # TH1D is sometimes useful for doing 2D stuff
# template TH1D* RebinDeWidthedFluxHist<TH1D>(TH1D* h_mnv_without_binwidth, TH1D * h_mnv_rebinned_without_binwidth)

# sometimes you need to make # of universes match - this does that

def TruncateNumberOfFluxUniverses(h, nUniverses):
  poppedFluxErrorBand = MnvVertErrorBand()
  poppedFluxErrorBand = h.PopVertErrorBand("Flux")
  #fluxUniverses = []
  fluxUniverses = poppedFluxErrorBand.GetHists()
  fluxUniverses = fluxUniverses[0:nUniverses]
  h.AddVertErrorBand("Flux",fluxUniverses)
  #CheckAndFixFluxErrorBand(h)

#2D
def TruncateNumberOfFluxUniverses(h, nUniverses):
  poppedFluxErrorBand = MnvVertErrorBand2D()
  poppedFluxErrorBand = h.PopVertErrorBand("Flux")
  fluxUniverses = poppedFluxErrorBand.GetHists()
  fluxUniverses = fluxUniverses[0:nUniverses]
  h.AddVertErrorBand("Flux",fluxUniverses)
  #CheckAndFixFluxErrorBand(h)

# implementation of GetFlux

# make a version that takes a pointer to the config
# def GetFlux(config):
#     allconfigs = []
#     allconfigs["main"]=(config)
#     return GetFlux(allconfigs)
    


def GetFlux(configmap):
    
  playlist = configmap["main"]["playlist"]
  m_fluxUniverses = configmap["main"]["fluxUniverses"]
  m_nue_constraint = configmap["main"]["NuEConstraint"]
  pdg = configmap["main"]["pdg"]

  #++++++++++++++++++=  Initialization +++++++++++++++++++++++++

  # Get the flux hist, clean it up a bit, remove binwidth correction that should not be there and return

  # someone thought an enum was a good idea.  It was not.
  fluxplaylist = {}
  fluxplaylist["minervame1A"] = FluxReweighter.minervame1A
  fluxplaylist["minervame1B"] = FluxReweighter.minervame1B
  fluxplaylist["minervame1C"] = FluxReweighter.minervame1C
  fluxplaylist["minervame1D"] = FluxReweighter.minervame1D
  fluxplaylist["minervame1E"] = FluxReweighter.minervame1E
  fluxplaylist["minervame1F"] = FluxReweighter.minervame1F
  fluxplaylist["minervame1G"] = FluxReweighter.minervame1G
#  fluxplaylist["minervame1H"] = FluxReweighter.minervame1H
#  fluxplaylist["minervame1I"] = FluxReweighter.minervame1I
#  fluxplaylist["minervame1J"] = FluxReweighter.minervame1J
#  fluxplaylist["minervame1K"] = FluxReweighter.minervame1K
  fluxplaylist["minervame1L"] = FluxReweighter.minervame1L
  fluxplaylist["minervame1M"] = FluxReweighter.minervame1M
  fluxplaylist["minervame1N"] = FluxReweighter.minervame1N
  fluxplaylist["minervame5A"] = FluxReweighter.minervame5A
  fluxplaylist["minervame6A"] = FluxReweighter.minervame6A
  fluxplaylist["minervame6B"] = FluxReweighter.minervame6A
  fluxplaylist["minervame6C"] = FluxReweighter.minervame6A
  fluxplaylist["minervame6D"] = FluxReweighter.minervame6A
  fluxplaylist["minervame6E"] = FluxReweighter.minervame6A
  fluxplaylist["minervame6F"] = FluxReweighter.minervame6A
  fluxplaylist["minervame6G"] = FluxReweighter.minervame6A
  fluxplaylist["minervame6H"] = FluxReweighter.minervame6A
  fluxplaylist["minervame6I"] = FluxReweighter.minervame6A
  fluxplaylist["minervame6J"] = FluxReweighter.minervame6A

  if( playlist not in  fluxplaylist ):
    print(" playlist " , playlist , " not yet implemented in RebinFlux.h " )
    sys.exit(0)
  

  
  frw = FluxReweighter(pdg,m_nue_constraint,fluxplaylist[playlist],FluxReweighter.gen2thin, FluxReweighter.g4numiv6,m_fluxUniverses)

  h_flux = MnvH1D()
  h_flux = frw.GetFluxReweighted(pdg)
  h_flux.SetDirectory(0)
  # clean up the external flux by removing error bands we won't use in this analysis
  h_flux.PopVertErrorBand("Flux_BeamFocus")
  h_flux.PopVertErrorBand("ppfx1_Total")
  TruncateNumberOfFluxUniverses(h_flux,m_fluxUniverses)

  #
  #  flux hist is stored with binwidth correction, need to undo that to get the integral and use for sigma(E:
  #
  h_flux_dewidthed = MnvH1D()
  #h_flux.Print("ALL")
  h_flux_dewidthed = DeWidth(h_flux)
  #h_flux_dewidthed.Print("ALL")
  h_flux_dewidthed.SetName("flux_dewidthed")
  h_flux_dewidthed.Scale(1/10000.) # convert from m^2 to cm^2
  return h_flux_dewidthed
  

# given energy histogram, rebin flux to match

def  GetFluxEbins(h_flux_dewidthed, ihist, configs , FluxEnormBool):
   if ihist.InheritsFrom("TH2D"):
      return GetFluxEbins2D(h_flux_dewidthed, ihist, configs , FluxEnormBool)
   else:
      return GetFluxEbins1D(h_flux_dewidthed, ihist, configs , FluxEnormBool)
   
def  GetFluxEbins1D(h_flux_dewidthed, ihist, configs , FluxEnormBool):
  newname = ihist.GetName()+"_Flux"
  h_flux_ebins = MnvH1D()
  h_flux_ebins = RebinDeWidthedFluxHist(h_flux_dewidthed,ihist)
  h_flux_ebins.SetName(newname)
  h_flux_ebins.SetTitle("Integrated Flux/bin GeV")
  # reapply the bin width correction to flux(this cancels out the plotter applying it later to the numerator)
  h_flux_ebins.Scale(1.0,"width")
  return h_flux_ebins


# def GetFluxEbins1D(h_flux_dewidthed, ihist, config, FluxEnormBool):
#     allconfigs = []
#     allconfigs["main"]=(config)
#     return GetFluxEbins( h_flux_dewidthed, ihist , allconfigs,  FluxEnormBool)


#MnvH2D GetFluxEbins(MnvH1D h_flux, MnvH2D ihist , NuConfig* pconfig, std.map<std.string, bool> FluxEnormBool)
#    return GetFluxEbins(h_flux, ihist , *pconfig, FluxEnormBool)
#

def  GetFluxEbins2D(h_flux, ihist , configmap, FluxEnormBool):  ## fixme varparse)
  # hist that will come out with flux hist in bins you want
  h2D_flux_ebins = MnvH2D()  
  h2D_flux_ebins = ihist.Clone()
  # changed ehist to h2D_flux_ebins
  # MnvH2D ehist = (MnvH2D)enu_hist.Clone()
  h2D_flux_ebins.ClearAllErrorBands() # need to do this so you can add them back later.
  h2D_flux_ebins.Reset()
  # Make a blank dummy hist
  dummyhist = MnvH2D()
  #MnvH2D dummyhist #.Divide(h2D_flux_ebins,h2D_flux_ebins,1.,1.)
  if( not FluxEnormBool["xfluxnorm"] and not FluxEnormBool["yfluxnorm"]):
    print(" fluxnorm not set for axes. Doing flat flux instead." )
    # MnvH2D flux = GetFluxFlat(config,ihist)
    # return flux
    return dummyhist
  
  if( FluxEnormBool["xfluxnorm"] and FluxEnormBool["yfluxnorm"]):
    print(" Both axes have energy dependent flux normalization, which isn't implimented yet." )
    # MnvH2D flux = GetFluxFlat(config,ihist)
    # return flux
    return dummyhist
  


  # Take projection on x or y axis (depending on which variable is on which axis: to get input hist binning for 1D flux
  ihistproj = MnvH1D()

  if(FluxEnormBool["xfluxnorm"] and not FluxEnormBool["yfluxnorm"]): 
    print(" Using an energy dependent flux for the x axis. " )
    ihistproj = h2D_flux_ebins.ProjectionX("_proj_x",0,-1)
  
  if(FluxEnormBool["yfluxnorm"] and not FluxEnormBool["xfluxnorm"]): 
    print(" Using an energy dependent flux for the y axis. " )
    ihistproj = h2D_flux_ebins.ProjectionY("_proj_y",0,-1)
  

  # Borrowed from 1D code
  h_flux_dewidthed = MnvH1D()
  h_flux_dewidthed = h_flux.Clone()
  # Rebin flux to energy hist bins, Amit works with TH1D's for all this...
  mnvh_rebinned_flux = MnvH1D()
  mnvh_rebinned_flux = RebinDeWidthedFluxHist(h_flux_dewidthed,ihistproj)
  mnvh_rebinned_flux.SetTitle("Integrated Flux/projected bin GeV")
  # reapply the bin width correction to flux(this cancels out the plotter applying it later to the numerator)
  # is this necessary for 2D?
  mnvh_rebinned_flux.Scale(1.0,"width")

  # Borrowed from Amit's code. Don't need hist tmphist though, since already rebinned flux.
  h_rebinned_flux = TH1D()
  h_rebinned_flux = mnvh_rebinned_flux.GetCVHistoWithStatError()
  # find number of bins to help rebin the flux
  nxbins = h2D_flux_ebins.GetNbinsX()
  nybins = h2D_flux_ebins.GetNbinsY()
  # Fill the 2D flux hist with contents of 1D. Filling by xbins or ybins depending on the case.
  for i in range(0, nxbins+1): 
    for j in range (0, nybins+1):
        if(FluxEnormBool["xfluxnorm"] and not FluxEnormBool["yfluxnorm"]): 
           h2D_flux_ebins.SetBinContent(i,j,h_rebinned_flux.GetBinContent(i))
        if(FluxEnormBool["yfluxnorm"] and not FluxEnormBool["xfluxnorm"]): 
           h2D_flux_ebins.SetBinContent(i,j,h_rebinned_flux.GetBinContent(j))
    
  
  # TODO: Binwidth is being corrected too many times or not enough on 2D
  # look at cheryl's paper about this
  # Is this ^^^ True??? May need to do binwidth correction for 2D on my own. NHV, 6/22

  # This hist doesn't have (vertical: errorbands, so we'll need to do the same for them.


  print("Now for verts" )
  nfluxUniverses = configmap["main"]["fluxUniverses"]
  #Do the same with the vertical error bands
  vertNames = h_flux_dewidthed.GetVertErrorBandNames()
  for k in range(0,len(vertNames)): # k=0 k<vertNames.size(: ++k :
    errBand = MnvVertErrorBand()
    errBand = h_flux_dewidthed.GetVertErrorBand( vertNames[k] )
    nuniverses = errBand.GetNHists()
    if(vertNames[k]=="Flux"):
        nuniverses = nfluxUniverses#cout , "Flux Universes = " , universes , endl
    #if(vertNames[k].find("_BeamFocus"):not =-1||vertNames[k].find("ppfx1_Total"):not =-1): continue
    if "_BeamFocus" in vertNames[k] or "ppfx1_Total" in vertNames[k]: 
      continue
    vert_hists = TH2D()
    print("Working on " , vertNames[k] )
    for u in range(0, nuniverses):
        h_vert = TH2D()
        h_vert = h2D_flux_ebins.Clone()
        h_vert.SetName("h_vert_%s_%i"%(vertNames[k], u) )
        #strategy is get 1D th1d and fill up h_flux_normalization
        univerrBand = TH1D()
        univerrBand = errBand.GetHist(u)
        RebinDeWidthedFluxHist(univerrBand, h_rebinned_flux)
        for i in range (0, nxbins+1): 
          for j in range (0, nybins+1):
            h_vert.SetBinContent(i,j,h_rebinned_flux.GetBinContent(i))
        vert_hists.append( h_vert )
      
    h2D_flux_ebins.AddVertErrorBand( vertNames[k], vert_hists )
    #cleaning
    #for(<TH2D*>.iterator itHist = vert_hists.begin(: itHist not = vert_hists.end(: ++itHist:
      #delete *itHist
  
  return h2D_flux_ebins


# def GetFluxEbins(h_flux, ihist , config, FluxEnormBool):
#     allconfigs = {}
#     allconfigs["main" ]=config
#     return GetFluxEbins( h_flux, ihist , allconfigs,  FluxEnormBool)



# implementation of GetFlux for a special histogram

# backwards compatibility
def  GetFluxFlat(config,   h):
      allconfigs = {}
      allconfigs["main"] = (config)
      return GetFluxFlat(allconfigs,h)
  

#template<class MnvHistoType>
def GetFluxFlat(configs, h):

    playlist = configs["main"]["playlist"]
    m_fluxUniverses = configs["main"]["fluxUniverses"]
    m_nue_constraint= configs["main"]["NuEConstraint"]
    pdg = configs["main"]["pdg"]

    #++++++++++++++++++=  Initialization +++++++++++++++++++++++++

    # Get the flux hist, clean it up a bit, remove binwidth correction that should not be there and return

    # someone thought an enum was a good idea.  It was not.
    fluxplaylist = {}
    fluxplaylist["minervame1A"] = FluxReweighter.minervame1A
    fluxplaylist["minervame1B"] = FluxReweighter.minervame1B
    fluxplaylist["minervame1C"] = FluxReweighter.minervame1C
    fluxplaylist["minervame1D"] = FluxReweighter.minervame1D
    fluxplaylist["minervame1E"] = FluxReweighter.minervame1E
    fluxplaylist["minervame1F"] = FluxReweighter.minervame1F
    fluxplaylist["minervame1G"] = FluxReweighter.minervame1G
    fluxplaylist["minervame1H"] = FluxReweighter.minervame1G
    fluxplaylist["minervame1I"] = FluxReweighter.minervame1G
    fluxplaylist["minervame1J"] = FluxReweighter.minervame1G
    fluxplaylist["minervame1K"] = FluxReweighter.minervame1G
    fluxplaylist["minervame1L"] = FluxReweighter.minervame1G
    fluxplaylist["minervame1M"] = FluxReweighter.minervame1M
    fluxplaylist["minervame1N"] = FluxReweighter.minervame1N
    fluxplaylist["minervame1O"] = FluxReweighter.minervame1N
    fluxplaylist["minervame1P"] = FluxReweighter.minervame1N
#anti-nu
    fluxplaylist["minervame5A"] = FluxReweighter.minervame5A
    fluxplaylist["minervame6A"] = FluxReweighter.minervame6A
    fluxplaylist["minervame6B"] = FluxReweighter.minervame6A
    fluxplaylist["minervame6C"] = FluxReweighter.minervame6A
    fluxplaylist["minervame6D"] = FluxReweighter.minervame6A
    fluxplaylist["minervame6E"] = FluxReweighter.minervame6A
    fluxplaylist["minervame6F"] = FluxReweighter.minervame6A
    fluxplaylist["minervame6G"] = FluxReweighter.minervame6A
    fluxplaylist["minervame6H"] = FluxReweighter.minervame6A
    fluxplaylist["minervame6I"] = FluxReweighter.minervame6A
    fluxplaylist["minervame6J"] = FluxReweighter.minervame6A

    if( playlist not in fluxplaylist):
      print(" playlist " , playlist , " not yet implemented in RebinFlux.h " )
      sys.exit(0)
    

    #frw = FluxReweighter()
    frw = FluxReweighter(pdg,m_nue_constraint,fluxplaylist[playlist],FluxReweighter.gen2thin, FluxReweighter.g4numiv6,m_fluxUniverses)
    use_muon_correlations = False
    
    h_flux = frw.GetIntegratedFluxReweighted(pdg,h,0.,120., use_muon_correlations)
    h_flux.SetDirectory(0)
    # clean up the external flux by removing error bands we won't use in this analysis
    h_flux.PopVertErrorBand("Flux_BeamFocus")
    h_flux.PopVertErrorBand("ppfx1_Total")
    TruncateNumberOfFluxUniverses(h_flux,m_fluxUniverses)

    #
    #  flux hist is stored with binwidth correction, need to undo that to get the integral and use for sigma(E:
    #
    h_flux.Scale(1./10000.) #convert from m^2 to cm^2
    return h_flux
  

# template MnvH1D GetFluxFlat<MnvH1D>(NuConfig config, MnvH1D h)
# template MnvH2D GetFluxFlat<MnvH2D>(NuConfig config, MnvH2D h)
# template MnvH1D GetFluxFlat<MnvH1D>(CONFIGMAP configs, MnvH1D h)
# template MnvH2D GetFluxFlat<MnvH2D>(CONFIGMAP configs, MnvH2D h)
#template MnvH1D GetFluxFlat<MnvH1D>(NuConfig* pconfig, MnvH1D h)
#template MnvH2D GetFluxFlat<MnvH2D>(NuConfig* pconfig, MnvH2D h)



#endif
