import os,sys
from ROOT import TH2D, TMatrixD, RooUnfold
from PlotUtils import MnvH1D, MnvH2D 
#from UnfoldUtils import MnvUnfold
from MatrixUtils import SyncBands, ZeroDiagonal
from RebinFlux import GetFluxFlat, GetFluxEbins
from plotting_pdf import PlotCVAndError, PlotErrorSummary, Plot2DFraction, integrator
DEBUG = True
# /**
#  * @file
#  * @author  Heidi Schellman/Noah Vaughan/SeanGilligan
#  * @version 1.0 *
#  * @section LICENSE *
#  * This program is free software you can redistribute it and/or
#  * modify it under the terms of the GNU General Public License as
#  * published by the Free Software Foundation either version 2 of
#  * the License, or (at your option) any later version. *
#  * @section DESCRIPTION *
#  * Code to fill histograms
#  */

# #define DEBUG=1
#include <filesystem>
#include <iostream>
#include <map>
#include <string>
#include <vector>

#include "MinervaUnfold/MnvResponse.h"
#include "MinervaUnfold/MnvUnfold.h"
#include "PlotUtils/FluxReweighter.h"
#include "PlotUtils/MnvH1D.h"
#include "PlotUtils/MnvH2D.h"
#include "TCanvas.h"
#include "TF2.h"
#include "TH2D.h"
#include "utils/NuConfig.h"
#include "utils/RebinFlux.h"
#include "utils/SyncBands.h"
#ifndef __CINT__
#include "include/plotting_pdf.h"
#endif

# *
# ================================= GetXSec.h ====================================

# This templates the analysis steps of doing a 1D and 2D cross section analysis at
# MINERvA. Each step is templated to recieve both 1D and 2D inputs. The steps are
# as follows:
#   - MakeMC: Combine MC signal and bkg to make full MC
#   - GetSignalFraction: Uses MC bkg and full MC to create a signal fraction
#   - DoBkgSutraction: Uses signal fraction to make bkg on data, then subtracts it
#       from data
#   - DoUnfolding: Does unfolding in one oftwo ways depending on the variable you
#       are analyzing: 1. Crude ratio of (selected truth)/(all truth), 2. Using
#       UnfoldUtils.
#   - DoEfficiencyCorrection: Corrects unsmeared data for efficiency.
#   - DoNormalization: Normalizes for Flux and number of targets. For 1D can do an
#       flat flux or energy dependent flux if the variable needs it. For 2D can do
#       only flat right now.


# Noah Harvey Vaughan, May 2021
# Schellman Neutrino Group, Oregon State University
# vaughann@oregonstate.edu
# ================================================================================
# *//
#============================ Some Useful Tools ===============================

# Splits a string by given delimiter, useful for separating categories of 2D variable names
# fixme split(s, delimiter) 
    # pos_start = 0, pos_end, delim_len = delimiter.length()
    # token
    # # fixme res

    # while ((pos_end = s.find(delimiter, pos_start)) not = std.string.npos) 
    #     token = s.substr(pos_start, pos_end - pos_start)
    #     pos_start = pos_end + delim_len
    #     rsize_t es.append(token)
    

    # res.append(s.substr(pos_start))
    # return res


# TMatrixD ZeroDiagonal(TMatrixD& m) 
#     print(" TRACE: enter ZeroDiagonal  " )
#     TMatrixD newm = TMatrixD(m)
#     n = newm.GetNrows()
#     fori = 0 i < n i++: 
#         newm[i][i] = 0
    
#     return newm



# Returns a map of bools for  'fluxnorm', 'xfluxnorm', 'yfluxnorm' based off "fluxnorm" set in variable config
# Used to tell the code when and how to use an integrated flux normalization vs an energy dependent flux normalization
def CheckFluxNorm(configvar, variable):
    # what it will spit out
    fluxnormBoolMap = {}
    # Default to False. 1D uses fluxnorm only, 2D uses xfluxnorm and yfluxnorm
    fluxnormBoolMap["fluxnorm"] = False
    fluxnormBoolMap["xfluxnorm"] = False
    fluxnormBoolMap["yfluxnorm"] = False

    #  varsFile = config["varsFile")
    # NuConfig configvar
    #  if (varsFile not = "" ):
    #    configvar.Read(varsFile)
    #  
    #  else:
    #    print(" no varsFile" )
    #    sys.exit(1)
    #  
    if variable not in configvar:
        print ("missing variable in varconfig",variable,varconfig)
        return
    varconfig = configvar[variable]
    if "fluxnorm" in varconfig:
        fluxnormBoolMap["fluxnorm"] = varconfig["fluxnorm"]
    
    #elif(varconfig.IsMember("xvar") and varconfig.IsMember("yvar"):): 
    elif "xvar" in varconfig and "yvar" in varconfig:
        xvar = varconfig["xvar"]
        xconfig = configvar[xvar]
        if "fluxnorm" in xconfig:
            fluxnormBoolMap["xfluxnorm"] = xconfig["fluxnorm"]
            if fluxnormBoolMap["xfluxnorm"]:
                fluxnormBoolMap["fluxnorm"] = True
        
        yvar = varconfig["yvar"]
        yconfig = configvar[yvar]
        if "fluxnorm" in yconfig:
            fluxnormBoolMap["yfluxnorm"] = yconfig["fluxnorm"]
            if (fluxnormBoolMap["yfluxnorm"]): 
                fluxnormBoolMap["fluxnorm"] = True
        
    
    else: 
        print(" CheckFluxNorm: " , variable , " has no fluxnorm member, defaulting to False." )
    

    # sets 'fluxnorm' to True if xfluxnorm or yfluxnorm are set to True.
    # if (fluxnormBoolMap["xfluxnorm"] || fluxnormBoolMap["yfluxnorm"]): 
    #   fluxnormBoolMap["fluxnorm"] = True
    # 

    return fluxnormBoolMap


#================================= Make MC ====================================
# Makes a total MC hist from MC signal + MC background
def MakeMC(basename, imcsighist, imcbkghist):
    mcname = basename + "_mc_tot"
    mc = MnvH1D()
    mc = imcsighist.Clone(mcname)
    mc.SetDirectory(0)

    mc.Add(imcbkghist)
    SyncBands(mc)

    return mc

# template MnvH1D MakeMC<MnvH1D>(basename, MnvH1D imcsighist, MnvH1D imcbkghist)
# template MnvH2D MakeMC<MnvH2D>(basename, MnvH2D imcsighist, MnvH2D imcbkghist)

#============================== Signal Fraction ===============================
# Gets signal fraction of MC signal over MC total
#template <class MnvHistoType>
def GetSignalFraction(basename,  imcsighist,  mc): 
    fracname = basename + "_signalfraction"
    signalFraction = imcsighist.Clone(fracname)
    signalFraction.SetDirectory(0)

    signalFraction.Divide(imcsighist, mc, 1., 1., "B")
    SyncBands(signalFraction)

    return signalFraction

# template MnvH1D GetSignalFraction<MnvH1D>(basename, MnvH1D imcsighist, MnvH1D mc)
# template MnvH2D GetSignalFraction<MnvH2D>(basename, MnvH2D imcsighist, MnvH2D mc)

#template <class MnvHistoType>
def GetBkgFraction(basename,  imcbkghist,  mc):
    fracname = basename + "_bkgfraction"
    bkgFraction = imcbkghist.Clone(fracname)
    bkgFraction.SetDirectory(0)

    bkgFraction.Divide(imcbkghist, mc, 1., 1., "B")
    SyncBands(bkgFraction)

    return bkgFraction

# template MnvH1D GetBkgFraction<MnvH1D>(basename, MnvH1D imcbkghist, MnvH1D mc)
# template MnvH2D GetBkgFraction<MnvH2D>(basename, MnvH2D imcbkghist, MnvH2D mc)

#========================== Background Subtraction ============================
# Rough background subtraction using input signal fraction
#template <class MnvHistoType>
def DoBkgSubtraction(basename, idatahist, mc, signalFraction):
    bkgsubname = basename + "_bkgsub"
    bkgsub = idatahist.Clone(bkgsubname)
    bkgsub.SetDirectory(0)

    bkgsub.AddMissingErrorBandsAndFillWithCV(mc)
    bkgsub.Multiply(bkgsub, signalFraction)
    SyncBands(bkgsub)

    return bkgsub

# template MnvH1D DoBkgSubtraction<MnvH1D>(basename, MnvH1D idatahist, MnvH1D mc, MnvH1D signalFraction)
# template MnvH2D DoBkgSubtraction<MnvH2D>(basename, MnvH2D idatahist, MnvH2D mc, MnvH2D signalFraction)

#================================ Unfolding ===================================

#------------------------------ Ratio Unfolding -------------------------------
# Unfolding for things that don't really need it. Just uses crude ratio of
# sel_truth over full MCReco.
# template <class MnvHistoType>
def DoRatioUnfolding(basename, bkgsub, imcsighist, idatahist, iseltruhist): 
    outUnsmearingVec = []
    unsmearedname = (bkgsub.GetName()) + "_unfolded"
    unsmeared = idatahist.Clone(unsmearedname)

    unsmeared.SetDirectory(0)

    unsmearingname = basename + "_ratiounsmearing"
    unsmearing = bkgsub.Clone(unsmearingname)
    unsmearing.AddMissingErrorBandsAndFillWithCV(iseltruhist)
    unsmearing.SetDirectory(0)

    unsmearing.Divide(iseltruhist, imcsighist, 1., 1., "B")
    unsmeared.Multiply(unsmeared, unsmearing, 1., 1.)

    # Commenting out since may not be necessary.
    SyncBands(unsmeared)
    SyncBands(unsmearing)
    outUnsmearingVec.append(unsmeared)
    outUnsmearingVec.append(unsmearing)
    # Returns a vector of size two of < (roughly unsmeared variable hist), ( rough unsmearing hist ) >
    return outUnsmearingVec


# template <MnvH1D> DoRatioUnfolding<MnvH1D>(basename, MnvH1D bkgsub, MnvH1D imcsighist, MnvH1D idatahist, MnvH1D iseltruhist)
# template <MnvH2D> DoRatioUnfolding<MnvH2D>(basename, MnvH2D bkgsub, MnvH2D imcsighist, MnvH2D idatahist, MnvH2D iseltruhist)

#---------------------------- Response Unfolding ------------------------------

# Dummy template. Do not use.
# template <class MnvHistoType>
# def DoResponseUnfolding(basename, iresponse, imcsighist, iseltruhist,  bkgsub, idatahist, unfold, num_iter): 
#     unsmearedname = (bkgsub.GetName()) + "_notunfolded"
#     unsmeared = idatahist.Clone(unsmearedname)
#     unsmeared.SetDirectory(0)
#     SyncBands(unsmeared)
#     print(" WARNING: something's wrong, used default response unfolding that does nothing." )
#     return unsmeared


# 1D
# template 

def DoResponseUnfolding(basename,  iresponse,  imcsighist, iseltruhist,  bkgsub, idatahist,  unfold, num_iter):
    if imcsighist.InheritsFrom("MnvH2D"):
        return DoResponseUnfolding2D(basename,  iresponse,  imcsighist, iseltruhist,  bkgsub, idatahist,  unfold, num_iter)
    else:
        return DoResponseUnfolding1D(basename,  iresponse,  imcsighist, iseltruhist,  bkgsub, idatahist,  unfold, num_iter)

def DoResponseUnfolding1D(basename,  iresponse,  imcsighist, iseltruhist,  bkgsub, idatahist,  unfold, num_iter):
    migration = iresponse.Clone()
    if (migration == 0): 
        print(" no migration, stop here for " , basename)
        SyncBands(bkgsub)
        return bkgsub
    
    # Commenting out since may not be necessary.
    SyncBands(migration)
    # you can't put the cv in as the unfolding code does not expect it.
    migration.PopVertErrorBand("cv")

    unsmearedname = (bkgsub.GetName()) + "_unfolded"
    #MnvH1D unsmeared  # = (MnvH1D)iseltruhist.Clone(unsmearedname)
                        # make an unsmeared without error bands so that the unfolding can add them
    #unsmeared = (iseltruhist).GetCVHistoWithStatError()
    # HMS - make certain it is a real MnvH1D. 
    unsmeared = MnvH1D()
    unsmeared = MnvH1D((iseltruhist).GetCVHistoWithStatError())
    unsmeared.SetName(unsmearedname)
    #  unsmeared.SetName(unsmearedname)
    # unsmeared.AddMissingErrorBandsAndFillWithCV(iseltruhist)
    unsmeared.SetDirectory(0)
    print(" Migration matrix has size " , len(migration.GetErrorBandNames()) )
    print(" Data has  size " , len(bkgsub.GetErrorBandNames()) )
    # MnvH1D empty = (MnvH1D)bkgsub.Clone(((bkgsub.GetName())+"_empty"))
    # empty.Reset()
    #  make an empty covariance matrix for the unfolding to give back to you
    n = unsmeared.GetXaxis().GetNbins()
    covmatrix = TMatrixD(n,n)  # need to check to see if want n or n+2

    # try doing with variable size matrices.
    data_unfolded = unfold.UnfoldHisto(unsmeared, covmatrix, migration, bkgsub, RooUnfold.kBayes, num_iter, True, True)
    # MnvUnfold.UnfoldHistoWithFakes(PlotUtils.MnvH1D &h_unfold, TMatrixD &covmx, PlotUtils.MnvH2D h_migration, PlotUtils.MnvH1D h_data, PlotUtils.MnvH1D  h_model_reco, PlotUtils.MnvH1D h_model_truth, PlotUtils.MnvH1D h_model_background, regparam,addSystematics,useSysVariatedMigrations) const
    # this defaults to Bayesian
    # data_unfolded = unfold.UnfoldHistoWithFakes(unsmeared,covmatrix,migration,bkgsub,imcsighist,iseltruhist,empty,4.,True, True)
    if (DEBUG): bkgsub.Print("ALL")
    # zero out the diagonal
    for i in range(0,  covmatrix.GetNrows()):  
        covmatrix[i][i] = 0.0
    
    covmatrix.Print()
    unsmeared.FillSysErrorMatrix("Unfolding", covmatrix)


    # Commenting out since may not be necessary.
    SyncBands(unsmeared)

    #  unsmeared.Print("ALL")
    return unsmeared


# Response unfolding for 2D histos
#
def DoResponseUnfolding2D(basename, iresponse,
                                     imcsighist,  iseltruhist,  bkgsub,  idatahist,
                                     unfold, num_iter): 
    migration = iresponse.Clone()
    if (migration == 0): 
        print(" no migration, stop here for " , basename )
        return bkgsub
    
    # Commenting out since may not be necessary.
    SyncBands(migration)
    # you can't put the cv in as the unfolding code does not expect it.
    migration.PopVertErrorBand("cv")
    # print(" Migration matrix has size " , migration.GetErrorBandNames().size() )
    # print(" Data has  size " , bkgsub.GetErrorBandNames().size() )

    unsmearedname = (bkgsub.GetName()) + "_unfolded"
    # HMS MnvH2D unsmeared = (MnvH2D)idatahist.Clone(unsmearedname)
    unsmeared = iseltruhist.Clone(unsmearedname)
    unsmeared.SetDirectory(0)
    bkgsub.Print()
    iseltruhist.Print()
    imcsighist.Print()

    # now to get the covariance matrix for the unfolding itself using only the central value  This is the method Amit used
    # make an empty covariance matrix for the unfolding to give back to you
    print(" starting 2D unfolding " )
    # data_unfolded = unfold.UnfoldHisto2D(unsmeared,migration,mc,iseltruhist,bkgsub,num_iter,True,True)
    print("imcsighist " , imcsighist.Integral() , " " , imcsighist.Integral() )
    print("iseltruhist " , iseltruhist.Integral() , " " , iseltruhist.Integral() )
    print("bkgsub " , bkgsub.Integral() , " " , bkgsub.Integral() )

    print("migration x y" , migration.ProjectionX().Integral() , " " , migration.ProjectionY().Integral() )
    #  if (imcsighist.Integral(): not = migration.ProjectionX():.Integral(): ):
    #    print(" make migration matrix have same scale as imcsighist" )
    #    migration.Scale(imcsighist.Integral()/migration.ProjectionX().Integral())
    #  
    data_unfolded = unfold.UnfoldHisto2D(unsmeared, migration, imcsighist, iseltruhist, bkgsub, num_iter, True, True)
    print(" Done with 2D unfolding " )
    print("unsmeared " , unsmeared.Integral() , " " , unsmeared.Integral() )
    bkgsub.Print()
    imcsighist.Print()
    iseltruhist.Print()
    # extra code just to get CV covmx
    
    hUnfoldedDummy =  TH2D()
    hUnfoldedDummy = unsmeared.GetCVHistoWithStatError()
    hMigrationDummy= TH2D()
    hMigrationDummy = (migration.GetCVHistoWithStatError())
    hRecoDummy = TH2D()
    hRecoDummy = (imcsighist.GetCVHistoWithStatError())
    hTruthDummy = TH2D()
    hTruthDummy = (iseltruhist.GetCVHistoWithStatError())
    hBGSubDataDummy = TH2D()
    hBGSubDataDummy = (bkgsub.GetCVHistoWithStatError())
    n = hBGSubDataDummy.GetXaxis().GetNbins()
    m = hBGSubDataDummy.GetYaxis().GetNbins()
    nrows = n*m
    unfoldingCovMatrixOrig_hist_type = TMatrixD(nrows,nrows)
    print("HERE for COVARIANCE " )
    # unfoldingCovMatrixOrig_hist_type.Print("ALL")
    unfold.UnfoldHisto2D(hUnfoldedDummy, unfoldingCovMatrixOrig_hist_type, hMigrationDummy, hRecoDummy, hTruthDummy, hBGSubDataDummy, num_iter)
    correctNbins = hUnfoldedDummy.fN
    matrixRows = unfoldingCovMatrixOrig_hist_type.GetNrows()

    if (correctNbins != matrixRows): 
        print("****************************************************************************" )
        print ( "*  Fixing unfolding matrix size because of RooUnfold bug. From " , matrixRows , " to " , correctNbins )
        print ("****************************************************************************" )
        # It looks like this DTRT, since the extra last two bins don't have any content
        unfoldingCovMatrixOrig_hist_type.ResizeTo(correctNbins, correctNbins)
    
    unfoldingCov = ZeroDiagonal(unfoldingCovMatrixOrig_hist_type)
    # unsmeared.PushCovMatrix("",unfoldingCov)
    unfoldingCov.Print()
    unsmeared.FillSysErrorMatrix("Unfolding", unfoldingCov)
    # Commenting out since may not be necessary.
    SyncBands(unsmeared)
    return unsmeared


#-------------------------------- DoUnfolding ---------------------------------
# Putting the unfolding all together.

# check call  <MnvHistoType*> unsmearedVec = DoUnfolding(basename,iresponse,iresponse_reco,iresponse_truth,bkgsub,idatahist,unfold,num_iter)
#template <class MnvHistoType>
def DoUnfolding(basename, iresponse, imcsighist, iseltruhist, bkgsub,
                idatahist, unfold, num_iter):
    # If there's no response, do a rough ratio unfold<MnvHistoType*> DoUnfolding(ba        print(" use ratio unfolding for " , basename :
        # If there's no truth histogram you can't do unfolding.
    if (iseltruhist == 0): 
        print (" No truth info so no unsmearing possible for " , basename )
        # Returns an empty vector, which makes the loop continue to the next variable, useful for sidebands
        return 
        
        # Output is a vector of size two < (unsmeared variable hist), (rough unsmearing hist) >
        unsmearedVec = DoRatioUnfolding(basename, bkgsub, imcsighist, idatahist, iseltruhist)

        return unsmearedVec
    
    # If there is response, do real unfolding
    else: 
        print(" use response unfolding for " , basename )
        # Output is a vector of size one < (unsmeared variable hist) >
        unsmearedVec = []
        unsmeared = DoResponseUnfolding(basename, iresponse, imcsighist, iseltruhist, bkgsub, idatahist, unfold, num_iter)
        SyncBands(unsmeared)
        unsmearedVec.append(unsmeared)

        return unsmearedVec
    

# template <MnvH1D> DoUnfolding<MnvH1D>(basename, MnvH2D iresponse, MnvH1D mc, MnvH1D iseltruhist, MnvH1D bkgsub, MnvH1D idatahist, MinervaUnfold.MnvUnfold unfold, num_iter)
# template <MnvH2D> DoUnfolding<MnvH2D>(basename, MnvH2D iresponse, MnvH2D mc, MnvH2D iseltruhist, MnvH2D bkgsub, MnvH2D idatahist, MinervaUnfold.MnvUnfold unfold, num_iter)

#========================== Efficiency Correction =============================
# Divides unfolded hists by efficiency (calculated as (selected truth)/(all truth) )
#template <class MnvHistoType>
def DoEfficiencyCorrection(basename, unsmeared,  iseltruhist, ialltruhist, fluxhere = False):
    # Vector passed out of < (efficiency corrected hist), (efficiency hist) >
    outEffVec = []
    print("start DoEfficiencyCorrection" )
    effcorrname = (unsmeared.GetName()) + "_effcorr"
    effcorr = unsmeared.Clone(effcorrname)
    print("clone unsmeared" )
    effcorr.SetDirectory(0)

    # make the efficiency
    efficiencyname = basename + "_efficiency"
    print("make efficiency" )
    efficiency = iseltruhist.Clone(efficiencyname)
    efficiency.SetDirectory(0)

    # apply the efficiency
    efficiency.AddMissingErrorBandsAndFillWithCV(ialltruhist)  # should be seltruhists?
    SyncBands(efficiency)
    # make certain efficiency has all error bands for thing it will be applied to
    if (fluxhere):   # special code to make the errors include variable dependend flux
        efficiency.PopVertErrorBand("Flux")

        print("removed Flux Error band from efficiency" )
    
    efficiency.AddMissingErrorBandsAndFillWithCV(unsmeared)
    SyncBands(efficiency)
    efficiency.Divide(efficiency, ialltruhist, 1., 1., "B")
    # efficiency.AddMissingErrorBandsAndFillWithCV(unsmeared)
    #  Commenting out since may not be necessary.
    SyncBands(efficiency)
    effcorr.Divide(unsmeared, efficiency, 1., 1.)
    # Commenting out since may not be necessary.
    SyncBands(effcorr)

    outEffVec.append(effcorr)
    outEffVec.append(efficiency)
    return outEffVec

# template <MnvH1D> DoEfficiencyCorrection<MnvH1D>(basename, MnvH1D unsmeared, MnvH1D iseltruhist, MnvH1D ialltruhist, fluxhere)
# template <MnvH2D> DoEfficiencyCorrection<MnvH2D>(basename, MnvH2D unsmeared, MnvH2D iseltruhist, MnvH2D ialltruhist, fluxhere)

#============================== Normalization =================================
# Does number of target normalization (passed in from analyze code) and flux normalization.
# Returns a vector of size to of < (Data xsec), (MC xsec) >
#template <class MnvHistoType>
def DoNormalization(configs, basename, FluxNorm, norm, effcorr,  ialltruhist, h_flux_dewidthed, outname): 
    config = configs["main"]
    # tag = config["outRoot")
    # thename = effcorr.GetName()
    # if (thename.find("tuned"): not = std.string.npos): tag += "_tuned"

    csvdir = ("./csv_") + os.path.basename(outname)
    if not os.path.exists(csvdir):
        os.mkdir(csvdir)
    sigmaname = (effcorr.GetName()) + "_sigma"
    sigma = effcorr.Clone(sigmaname)
    sigma.SetDirectory(0)
    sigmaMCname = basename + "_sigmaMC"
    sigmaMC = ialltruhist.Clone(sigmaMCname)
    sigmaMC.SetDirectory(0)

    # Integrated flux normalization for non-energy variables
    # Set by 'fluxnorm':False on 1D variables in the variables config
    if (not FluxNorm["fluxnorm"]): 
        print(" Using flat flux normalization. " )
        # Returns integrated flux hist in bins input hist
        theflux = GetFluxFlat(configs, sigma)

        theflux.AddMissingErrorBandsAndFillWithCV(sigma)
        sigma.AddMissingErrorBandsAndFillWithCV(theflux)
        sigma.Divide(sigma, theflux)
        # target normalization
        sigma.Scale(norm)

        theflux.AddMissingErrorBandsAndFillWithCV(sigmaMC)
        sigmaMC.AddMissingErrorBandsAndFillWithCV(theflux)
        sigmaMC.Divide(sigmaMC, theflux)
        # target normalization
        sigmaMC.Scale(norm)
    
    # Energy dependent flux normalization
    # Set by 'fluxnorm':True on 1D variables in the variables config
    else: 
        print(" Using energy dependent flux normalization. " )
        # Returns flux hist in bins of energy variable of input hist (for 2D the bins on the non-energy axis are integrated:
        h_flux_ebins = GetFluxEbins(h_flux_dewidthed, ialltruhist, config, FluxNorm)

        # TODO: Flipped the order of the Divide and Scale steps. Does this matter?
        h_flux_ebins.AddMissingErrorBandsAndFillWithCV(sigma)
        h_flux_ebins.SetName(("h_flux_ebins_" + basename))
        h_flux_ebins.Write()
        sigma.AddMissingErrorBandsAndFillWithCV(h_flux_ebins)
        sigma.Print("ALL")
        h_flux_ebins.Print("ALL")
        sigma.Divide(sigma, h_flux_ebins)
        sigma.Print("ALL")
        
        # target normalization
        sigma.Scale(norm)

        SyncBands(sigma)
        # if (DEBUG): sigma.GetSysErrorMatrix("Unfolding"):.Print():

        h_flux_ebins.AddMissingErrorBandsAndFillWithCV(sigmaMC)
        sigmaMC.AddMissingErrorBandsAndFillWithCV(h_flux_ebins)
        sigmaMC.Divide(sigmaMC, h_flux_ebins, 1.0, 1.0)
        # target normalization
        sigmaMC.Scale(norm)

    print ("have done sigmaMC",sigmaMC.GetName())
    
    SyncBands(sigma)
    SyncBands(sigmaMC)

    print ("Synced bands")
    if sigma.InheritsFrom("TH2"):  # bunch of dynamic casts here 
        sigma2D = MnvH2D()
        sigma2DMC = MnvH2D()
        sigma2D = (sigma.Clone())
        sigma2DMC = (sigmaMC.Clone())
        sigma2D.MnvH2DToCSV(sigma2D.GetName(), csvdir, 1.E39, False, True, True, True)
        sigma2DMC.MnvH2DToCSV(sigma2DMC.GetName(), csvdir, 1.E39, False, True, True, True)
        # sigma2D.Delete()
        sigma2DMC.Delete()
    else: 
        
        sigma1D = MnvH1D()
        sigma1DMC = MnvH1D()
        sigma1D = (sigma.Clone())
        sigma1DMC = (sigmaMC.Clone())
        sigma1D.MnvH1DToCSV(sigma1D.GetName(), csvdir, 1.E39, False, True, True, True)
        sigma1DMC.MnvH1DToCSV(sigma1DMC.GetName(), csvdir, 1.E39, False, True, True, True)
        # sigma1D.Delete()
        # sigma1DMC.Delete()
    
    sigmaVec = []
    sigmaVec.append(sigma)
    sigmaVec.append(sigmaMC)
    return sigmaVec


# template <MnvH1D> DoNormalization<MnvH1D>(std.map<std.string, NuConfig*> configs, basename, std.map<std.string, bool> FluxNorm, norm, MnvH1D effcorr, MnvH1D ialltruhist, MnvH1D h_flux_dewidthed, outname)
# template <MnvH2D> DoNormalization<MnvH2D>(std.map<std.string, NuConfig*> configs, basename, std.map<std.string, bool> FluxNorm, norm, MnvH2D effcorr, MnvH2D ialltruhist, MnvH1D h_flux_dewidthed, outname)

#============================= GetCrossSection ================================

# dummy for backwards compatibility config > map of config*
#template <class MnvHistoType>
def GetCrossSection(sample,  variable,  basename,
                    histsND,
                    responseND,
                    oneconfig, canvas, norm, POTScale, h_flux_dewidthed,
                    unfold, num_iter, DEBUG, hasbkgsub, usetune, rescale, outname) :
    configmap = []
    
    configmap["main"] = oneconfig
    print(" pass single config into map" )
    return GetCrossSection(sample, variable, basename,
                           histsND,
                           responseND,
                           configmap, canvas, norm, POTScale, h_flux_dewidthed,
                           unfold, num_iter, DEBUG, hasbkgsub, usetune, rescale,  outname)


#template <class MnvHistoType>
def GetCrossSection(sample, variable, basename,
                    histsND,
                    responseND,
                    configs,  canvas, norm, POTScale, h_flux_dewidthed,
                    unfold, num_iter, DEBUG, hasbkgsub, usetune, rescale, outname): 
    binwid = True

    logscale = 0  # 0 for none, 1 for x, 2 for y, 3 for both

    # Get "category" tags set in config. Needs to match ones used in the event loop.
    # TODO: Make this a map in config.

    print(" at the top of GetXsec" , sample )
    # this can come out of the sample information:
    # configs["main"].Print()
    sigkey = configs["main"]["signal"]
    # sigkey.Print() 
    sig = sigkey[sample]
    print(" got sig " , sig )
    bkgkey = []

    if (not hasbkgsub): 
        # this likely needs to be fixed
        bkgkey = configs["main"]["background"]
        # bkgkey.Print()
        print(sample in bkgkey )
        
        bkg = bkgkey[sample]
        print(" got bkg " , bkg )
    
    datkey = configs["main"]["data"]
    dat = datkey[sample]
    print(" got dat " , dat )

    # datkey.Print()
    # bkg = config["background")
    #  dat = config["data")

    # parse out variable to get axes
    # fixme varparse

    # "basename" input of the form "h_<sample>_<variable>" or "h2D_<sample>_<variable>"
    # Check if not 2D then make logscale for plotting if looking at Q^2_QE
    if ("h2D_" not in basename): 
        if ("Q2QE" in variable): logscale = 1
    
    # If 2D, then set log scale for each axis if needed
    else: 
        varparse = variable.split("_")
        if ("Q2QE" in varparse[0]): logscale += 1
        if ("Q2QE" in varparse[1]): logscale += 2
    

    print(" analyze " , variable )

    if (DEBUG): print("logscale " , variable , " " , logscale )

    # Prout the "type" tag from analyze code (e.g. "reconstructed", "selected_truth", etc.)
    # Scale POT for all MC hists, except response (get segfault if done this way.... -NHV

    hasdata = False
    print(" starting on variable " , sample , " " , variable )
    for type in histsND.keys(): 
        print("hists key " , type )
        for category in histsND[type].keys(): 
            #print("category " , category )
            if (category == "data"): hasdata = True
            if (dat not in category): 
                if (histsND[type][category] != 0): 
                    t = histsND[type][category].Integral()
                    histsND[type][category].Scale(POTScale)
                    #print(" POTScaled " , histsND[type][category].GetName() , " " , t , " " , histsND[type][category].Integral() )
                
               
    if (not hasdata): return hasdata
    for type in responseND.keys(): 
        print("response key " , type )
        for category in responseND[type].keys(): 
            if (dat not in category): 
                if (responseND[type][category] != 0): 
                    t = responseND[type][category].Integral()
                    responseND[type][category].Scale(POTScale)
                    print(" POTScaled " , responseND[type][category].GetName() , " " , t , " " , responseND[type][category].Integral() )
                
            
        
    

    # Assign each input histogram type used for doing the analysis.
    # MnvHistoType can be MnvH1D or MnvH2D so far. Response is always MnvH2D.

    mctype = "reconstructed"
    seltype = "selected_truth"
    trutype = "all_truth"
    migtype = "response_migration"
    mrecotype = "response_reco"
    mtrutype = "response_truth"
    if usetune:
        mctype += "_tuned"
        seltype += "_tuned"
        trutype += "_tuned"
        migtype += "_tuned"
        mrecotype = mrecotype.replace("response_reco","response_tuned_reco")
        mtrutype = mtrutype.replace("response_truth","response_tuned_truth")
    if rescale:
        mctype += "_scaledmc"
        seltype += "_scaledmc"
        trutype += "_scaledmc"
        migtype += "_scaledmc"
        mrecotype += "_scaledmc"
        mtrutype +=  "_scaledmc"
    idatahist = histsND["reconstructed"][dat]
    imcsighist = histsND[mctype][sig]

    print ("check stuff",dat,sig,idatahist.GetName(),imcsighist.GetName())
    
    stuned = ""
    # if ("reconstructed_tuned" in histsND.keys() and usetune): 
    #     stuned = "Tuned "
    #     imcsighist = histsND["reconstructed_tuned"][sig]
    #     print(" using " , imcsighist.GetName() )
    # if ("_scaledmc" in histND.keys() and rescale):

    # print("using signal " , imcsighist.GetName() )
    #MnvHistoType* imcbkghist
    #MnvHistoType* ibkgsubhist
    imcbkghist = 0
    if (not hasbkgsub): 
        imcbkghist = histsND[mctype][bkg]
        print(" using " , imcbkghist.GetName() )
    else:
        ibkgsubhist = histsND["fitted"]["bkgsub"]

        #print("using background " , imcbkghist.GetName() )

    #if (DEBUG): print("test pointers " , ibkgsubhist )
    #MnvHistoType* iseltruhist
    
    iseltruhist = histsND[seltype][sig]
    

    if (DEBUG and hasbkgsub): print("test pointers " , ibkgsubhist , " " , iseltruhist )
    #MnvHistoType* ialltruhist

    # if ("all_truth_tuned" in histsND and usetune): 
    #     ialltruhist = histsND["all_truth_tuned"][sig]
    #     print(" using " , ialltruhist.GetName() )
    # else: 
    ialltruhist = histsND[trutype][sig]
    
    if (DEBUG): print("test pointers " , sig , " " , iseltruhist.GetName() , ialltruhist )
    iresponse = MnvH2D()
    #MnvHistoType* iresponse_reco = imcsighist
    #MnvHistoType* iresponse_truth = iseltruhist
    # if ("response_migration_tuned" in responseND.keys() and usetune): 
    #     iresponse = responseND["response_migration_tuned"][sig]
    #     iresponse_reco = histsND["response_tuned_reco"][sig]
    #     iresponse_truth = histsND["response_tuned_truth"][sig]
    #     print(" using " , iresponse.GetName() , " " , iresponse.ProjectionX().Integral() , " " , iresponse.ProjectionY().Integral() )
    # else: 
    iresponse = responseND[migtype][sig]
    iresponse_reco = histsND[mrecotype][sig]
    iresponse_truth = histsND[mtrutype][sig]
    print(" using " , iresponse.GetName() , " " , iresponse.ProjectionX().Integral() , " " , iresponse.ProjectionY().Integral() )

    # TODO: POTScale by if (not data): -. POTScale

    # Check for each hist "category" for the variable you're analyzing.
    if (idatahist == 0): 
        print(" no data for " , variable )
        return 1  # Exits if cannot be found
    
    idatahist.Print()
    idatahist.Write()

    if (imcsighist == 0): 
        print(" no sig for " , variable )
        return 1
    
    # imcsighist.Scale(POTScale)
    imcsighist.Print()
    imcsighist.Write()
    if DEBUG: print(" MC sig scaled by POT for " , variable )

    if (imcbkghist == 0 and not hasbkgsub): 
        print(" no bkg for " , variable )
        return 1
    
    # imcbkghist.Scale(POTScale)
    if (not hasbkgsub): 
        imcbkghist.Print()
        imcbkghist.Write()
    

    if (DEBUG):  print(" MC bkg scaled by POT for " , variable )

# HACK as the response seems to have gotten the wrong normalization
    #  fix = imcsighist.Integral()/iresponse.ProjectionX().Integral()
    #  iresponse.Scale(fix)
    #  if (DEBUG. print(" HACK? response scaled by " , fix , " for " , iresponse.GetName(. , "POTScale would be ", POTScale:

    #==================================Make MC=====================================
    #MnvHistoType* mc
    #MnvHistoType* signalFraction

    if (not hasbkgsub): 

        if (DEBUG): print(" Start MakeMC... " )
        # mcname = basename+"_mc_tot"
        if (True): 
            print(" basename is " , basename)

            print (imcsighist.GetName())
            #imcsighist.Print("ALL")
            print (imcbkghist.GetName())
            #imcbkghist.Print("ALL")
        
        mc = MakeMC(basename, imcsighist, imcbkghist)
        if (DEBUG): mc.Print()
        mc.Write()

        PlotCVAndError(canvas, idatahist, mc, stuned + sample + "_" + "DATA_vs_MC", True, logscale, binwid)
        PlotErrorSummary(canvas, mc, sample + "_" + "Raw MC Systematics", logscale)

        #================================Signal Fraction===========================

        if (DEBUG): print(" Start signal fraction... " )
        # fracname = basename+"_signalfraction"
        signalFraction = GetSignalFraction(basename, imcsighist, mc)
        bkgFraction = GetBkgFraction(basename, imcbkghist, mc)
        if (DEBUG): signalFraction.Print()
        signalFraction.Write()
        bkgFraction.Write()
        Plot2DFraction(canvas, signalFraction, bkgFraction, stuned + sample + "_fractions", logscale)

        PlotCVAndError(canvas, signalFraction, signalFraction, stuned + sample + "_" + "Signal Fraction", True, logscale, False)
        PlotErrorSummary(canvas, signalFraction, stuned + sample + " Signal Fraction Systematics", 0)
    else: 
        mc = imcsighist.Clone()
    

    #============================Background Subtraction========================

    if (DEBUG): print(" Start background subtraction... " )
    # bkgsubname = basename+"_bkgsub"
    #MnvHistoType* bkgsub
    if (hasbkgsub): 
        if (ibkgsubhist): 
            bkgsub = ibkgsubhist.Clone((basename + "_bkgsub"))
        else: 
            print(" failed to find background histogram" )
            sys.exit(0)
        
    else: 
        bkgsub = DoBkgSubtraction(basename, idatahist, mc, signalFraction)
    
    if (DEBUG): bkgsub.Print()
    bkgsub.Write()

    PlotCVAndError(canvas, bkgsub, imcsighist, stuned + sample + "_" + "BKGsub vs. MC signal", True, logscale, binwid)
    PlotErrorSummary(canvas, bkgsub, stuned + sample + "_" + "BKGsub Systematics", 0)

    #==================================Unfolding===============================

    if (DEBUG): print(" Start unfolding... " )
    # unsmearedname = bkgsubname+"_unfolded"
    # unsmearingname = basename+"_unsmearing"
    #MnvHistoType* unsmeared
    # change this to use
    unsmearedVec = DoUnfolding(basename, iresponse, iresponse_reco, iresponse_truth, bkgsub, idatahist, unfold, num_iter)

    print("Unfolding Vector Size: " , len(unsmearedVec) )
    if (len(unsmearedVec) == 0): 
        print(" No unfolding. Exiting now. " )
        return 0
    
    if (len(unsmearedVec) > 0): 
        # Output for Bayesian unfolding, does not include the "unsmearing"
        unsmeared = unsmearedVec[0]
        if (DEBUG): unsmeared.Print()
        unsmeared.Write()
        PlotCVAndError(canvas, bkgsub, unsmeared, stuned + sample + "_" + "Data Before and After Unsmearing", True, logscale, binwid)
    
    if (len(unsmearedVec)  == 2): 
        # Output for crude ratio unfolding, DOES include "unsmearing" hist, so this picks that up
        unsmearing = unsmearedVec[1]
        if (DEBUG): unsmearing.Print()
        unsmearing.Write()
        # PlotCVAndError(canvas,imcsighist,iseltruhist,"Fractional Unfolding" ,True,logscale,binwid)
    

    PlotCVAndError(canvas, unsmeared, iseltruhist, stuned + sample + "_" + "Unsmeared Data Compared to Selected MC", True, logscale, binwid)
    PlotErrorSummary(canvas, unsmeared, stuned + sample + "_" + "Unsmeared Data Systematics", 0)

    #==================================Efficiency==============================

    if (DEBUG): print(" Start efficiency correction... " )
    if (iseltruhist == 0): 
        print(" No efficiency numerator. Stopping here." )
        return 2
    
    if (ialltruhist == 0): 
        print(" No efficiency denominator. Stopping here." )
        return 2
    
    fluxhere = False  # this was just a test to see if using bin by bin to see the error might be interesting.
    vecEffCorr = DoEfficiencyCorrection(basename, unsmeared, iseltruhist, ialltruhist, fluxhere)
    if (fluxhere): 
        h_flux_dewidthed.PopVertErrorBand("Flux")
    
    effcorr = vecEffCorr[0]
    if (DEBUG): effcorr.Print()
    effcorr.Write()
    efficiency = vecEffCorr[1]
    if (DEBUG): efficiency.Print()
    efficiency.Write()
    PlotCVAndError(canvas, iseltruhist, ialltruhist, stuned + sample + "_" + "efficiency: selected and True", True, logscale, binwid)
    PlotCVAndError(canvas, effcorr, ialltruhist, stuned + sample + "_" + "effcorr data vs truth", True, logscale, binwid)
    PlotErrorSummary(canvas, efficiency, stuned + sample + "_" + "Efficiency Factor Systematics", 0)
    PlotErrorSummary(canvas, effcorr, stuned + sample + "_" + "Efficiency Corrected Data Systematics", 0)

    #============================POT/Flux Normalization========================
    # energydep = False
    # energydepx = False
    # energydepy = False
    # #TODO: may need to check where this is originally defined.
    #
    if (DEBUG): print(" Start normalization... " )
    # # This checks if you need to use an energy dependent flux, and sets binwidth
    # # corrections needed for plotting.
    # if(variable.find("enuQE"):==std.string.npos && variable.find("EnuHad"):==std.string.npos && variable.find("EnuCCQE"):==std.string.npos):
    #   print(" Using a flat flux. " )
    #   energydep = False
    # 
    # else:
    #   print(" Using an energy dependent flux. "
    #   energydep = True
    # 
    # binwid = energydep
    # hack in a varsFile if it does not exist
    #print ("check configs",configs.keys())
    # if ("varsFile" not in configs): 
    #     # backwards compatibility change a file read into a configmap
    #     vars = configs["main"]["varsFile"]
    #     configs["varsFile"] = vars
    #     print ("had to make varsfile")
    
    #print (configs["varsFile"])
    varconfigs = configs["varsFile"]["1D"]

    if ialltruhist.InheritsFrom("TH2D"):
        varconfigs = configs["varsFile"]["2D"]
    print (varconfigs.keys())
    fluxnorm = CheckFluxNorm(varconfigs, variable)
    if (DEBUG): print(" fluxnorm: " , fluxnorm["fluxnorm"] , ", xfluxnorm: " , fluxnorm["xfluxnorm"] , ", yfluxnorm: " , fluxnorm["yfluxnorm"] )

    # HMS dec-1-2021 - flip these?
    if (fluxnorm["fluxnorm"]): 
        binwid = True
    
    if (not fluxnorm["fluxnorm"]): 
        binwid = True
    

    sigmaVec = DoNormalization(configs, basename, fluxnorm, norm, effcorr, ialltruhist, h_flux_dewidthed, outname)
    sigma = sigmaVec[0]
    sigma.Write()
    sigma.Print()
    if (DEBUG): sigma.Print("ALL")

    sigmaMC = sigmaVec[1]
    sigmaMC.Write()
    sigmaMC.Print()

    PlotCVAndError(canvas, sigma, sigmaMC, stuned + sample + "_" + "sigma", True, logscale, binwid)
    PlotErrorSummary(canvas, sigma, stuned + sample + "_" + "Cross Section Systematics", 0)

    #============================Binwidth Normalization============================
    # Just a check on bin width corrections...
    id = integrator(sigma, binwid)
    im = integrator(sigmaMC, binwid)
    print("sigma " , variable , " " , id , " " , sigma.Integral() , " " , im , " " , sigmaMC.Integral() )
    print(" end of loop over types " )

    #=====================================Exit======================================
    return 0


# template GetCrossSection<MnvH1D>(sample, variable, basename,
#                                      std.map<std.string, std.map<std.string, MnvH1D> > histsND,
#                                      std.map<std.string, std.map<std.string, MnvH2D> > responseND,
#                                      std.map<std.string, NuConfig*> configs, TCanvas& canvas, norm, POTScale, MnvH1D h_flux_dewidthed,
#                                      MinervaUnfold.MnvUnfold unfold, num_iter, DEBUG = False, hasbksub = False, usetune = False,
#                                      outname="")

# template GetCrossSection<MnvH2D>(sample, variable, basename,
#                                      std.map<std.string, std.map<std.string, MnvH2D> > histsND,
#                                      std.map<std.string, std.map<std.string, MnvH2D> > responseND,
#                                      std.map<std.string, NuConfig*> configs, TCanvas& canvas, norm, POTScale, MnvH1D h_flux_dewidthed,
#                                      MinervaUnfold.MnvUnfold unfold, num_iter, DEBUG = False, hasbksub = False, usetune = False,
#                                      outname="")

# template GetCrossSection<MnvH1D>(sample, variable, basename,
#                                      std.map<std.string, std.map<std.string, MnvH1D> > histsND,
#                                      std.map<std.string, std.map<std.string, MnvH2D> > responseND,
#                                      NuConfig mainconfig, TCanvas& canvas, norm, POTScale, MnvH1D h_flux_dewidthed,
#                                      MinervaUnfold.MnvUnfold unfold, num_iter, DEBUG = False, hasbksub = False, usetune = False,
#                                      outname)

# template GetCrossSection<MnvH2D>(sample, variable, basename,
#                                      std.map<std.string, std.map<std.string, MnvH2D> > histsND,
#                                      std.map<std.string, std.map<std.string, MnvH2D> > responseND,
#                                      NuConfig mainconfig, TCanvas& canvas, norm, POTScale, MnvH1D h_flux_dewidthed,
#                                      MinervaUnfold.MnvUnfold unfold, num_iter, DEBUG = False, hasbksub = False, usetune = False,
#                                      outname="")

    