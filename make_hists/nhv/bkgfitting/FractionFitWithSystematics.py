import ROOT
# from PlotUtils import MnvH1D, MnvH2D, MnvH1DToCSV
from PlotUtils import *
import os
import sys
import math
import ctypes
import json
import numpy as np
import time

# names associated with each category: data for full data, qelike for MC signal, qelikenot for MC bkg
category_list = ["data", "qelike", "qelikenot"]
# names associated with each "sample" e.g. QElike, QElikeALL
# sample_list = ["QElike", "QElike_hiE", "QElike_loE"]
sample_list = ["QElike"]
# DO_SYSTEMATICS = False
# DRAW = True
# CONFINT = True

# This is based off of how fitbins are made (i.e. making sidebands that have
# cuts on binedges of the variable you're making), and the histogram naming
# convention CCQENuMAT


def GetDataMCMnvH2D(rfile, category_list, sample):
    # Make a dictionary of the histos for fitting.
    # Requires CCQENuMAT naming convention for hists.
    histkeys_list = rfile.GetListOfKeys()
    datafound = 0
    qelikefound = 0
    qelikenotfound = 0
    for histkey in histkeys_list:
        hist_name = histkey.GetName()
        # Get rid of non-hist branches.
        if hist_name.find("___") == -1:
            continue
        splitnames_list = hist_name.split('___')
        # Looking only for 2D hists
        histotype = str(splitnames_list[0])
        if histotype != 'h2D':
            continue
        # Only grab correct sample (e.g. QElike) defined at top
        histosample = str(splitnames_list[1])
        if histosample != sample:
            continue
        # Only grab recoil vs. Q2QE 2D hists
        histovariable = str(splitnames_list[3])
        if histovariable != 'Q2QE_recoil':
            continue
        # Only grab data and qelike & qelikenot MC reco
        histocategory = str(splitnames_list[2])
        if not histocategory in ['data', 'qelike', 'qelikenot']:
            continue

        if histocategory == 'data':
            data_hist2D = rfile.Get(hist_name).Clone()
            datafound = 1
        if histocategory == 'qelike':
            qelike_hist2d = rfile.Get(hist_name).Clone()
            qelikefound = 1
        if histocategory == 'qelikenot':
            qelikenot_hist2d = rfile.Get(hist_name).Clone()
            qelikenotfound = 1

        if datafound == 1 and qelikefound == 1 and qelikenotfound == 1:
            return data_hist2D, qelike_hist2d, qelikenot_hist2d
        else:
            continue

    if datafound + qelikefound + qelikenotfound < 3:
        print("Error: Could not find the required histograms in the input file.")
        sys.exit()


def SyncBands(thehist):
    print(thehist.GetName())
    theCVHisto = ROOT.TH1D(thehist)
    theCVHisto.SetDirectory(0)
    bandnames = thehist.GetErrorBandNames()

    for bandname in bandnames:

        band = MnvVertErrorBand()
        band = thehist.GetVertErrorBand(bandname)

        for i in range(0, band.GetNbinsX() + 2):
            # if(i < 4 and i != 0):
            #     print ("Sync band ", thehist.GetName(), bandname, i, theCVHisto.GetBinContent(i), theCVHisto.GetBinContent(i)-band.GetBinContent(i))
            band.SetBinContent(i, theCVHisto.GetBinContent(i))
            band.SetBinError(i, theCVHisto.GetBinError(i))


def GetDummyHistCV(rfile, variable_name="___Q2QE___"):
    # Make a dummy 1D hist to get binning. Just grabs first 1D Q2QE plot
    histkeys_list = rfile.GetListOfKeys()
    for histkey in histkeys_list:
        hist_name = histkey.GetName()
        # TODO: This is hardcoded, should change it
        if hist_name.find(variable_name) == -1:
            continue
        else:
            dummy_mnvh1d = rfile.Get(hist_name).Clone()
            dummy_th1d = dummy_mnvh1d.GetCVHistoWithStatError().Clone()

            # Clears hist, leaves only binning
            dummy_mnvh1d.ClearAllErrorBands()

            dummy_mnvh1d.Reset("ICES")
            dummy_th1d.Reset("ICES")

            return dummy_mnvh1d, dummy_th1d

    print("No suitable hist to make a dummy with. Exiting...")
    sys.exit()


class printfLogger:
    # Class that handles logs from printf's in some ROOT functions

    # Initialize and open a log file
    def __init__(self, logfile_name):
        self.save = os.dup(sys.stdout.fileno())
        self.logfile = open(logfile_name, 'a')

    # Switch printf/print statements to write to logfile
    def PrintToLog(self):
        logfile = self.logfile
        os.dup2(logfile.fileno(), sys.stdout.fileno())

    # Switch printf/print statements to stdout
    def PrintToConsole(self):
        save = self.save
        os.dup2(save, sys.stdout.fileno())

    # Close logfile
    def close(self):
        self.logfile.close()


def PrintFitResults(fit, function):
    print("Function: ", function.GetExpFormula())
    print("chi2: ", function.GetChisquare())
    print("ndf: ", function.GetNDF())
    print("Covariance Matrix: ", fit.GetCovarianceMatrix())
    print("Correlation Matrix: ", fit.GetCorrelationMatrix())


def MakeMCandScale(i_data_hist, qelike_hist, qelikenot_hist):
    data_hist = i_data_hist.Clone()

    # Make total MC hist by adding qelike, qelikenot
    mctot_hist = qelike_hist.Clone("mc")
    mctot_hist.Add(qelikenot_hist, 1.0)

    # Make area scale for MC hists. Don't include underflow & overflow bins
    min_bin = 1
    max_xbin = data_hist.GetNbinsX()
    max_ybin = data_hist.GetNbinsY()
    area_scale = (data_hist.Integral(min_bin, max_xbin, min_bin, max_ybin)) / \
        (mctot_hist.Integral(min_bin, max_xbin, min_bin, max_ybin))

    # Scale MC hists to area normalize them to Data (so # counts is the same)
    mctot_hist.Scale(area_scale)
    qelike_hist.Scale(area_scale)
    qelikenot_hist.Scale(area_scale)

    return qelike_hist, qelikenot_hist, mctot_hist


def GetSigBkgFrac(i_mctot_hist, i_sig_hist, i_bkg_hist):
    mc_int = i_mctot_hist.Integral(1, i_mctot_hist.GetNbinsX())
    qelike_int = i_sig_hist.Integral(1, i_sig_hist.GetNbinsX())
    qelikenot_int = i_bkg_hist.Integral(1, i_bkg_hist.GetNbinsX())

    sig_frac = qelike_int / mc_int
    bkg_frac = qelikenot_int / mc_int
    return sig_frac, bkg_frac


def RunFractionFitter(i_mctot_hist, i_qelike_hist, i_qelikenot_hist, i_data_hist):
    mctot_hist = i_mctot_hist.Clone()
    qelike_hist = i_qelike_hist.Clone()
    qelikenot_hist = i_qelikenot_hist.Clone()
    data_hist = i_data_hist.Clone()

    # Get some info for some calculations
    min_bin = 1
    max_bin = mctot_hist.GetNbinsX()

    # Calculate & store pre-fit fractions of MC samples.
    prefit_sig_frac, prefit_bkg_frac = GetSigBkgFrac(
        mctot_hist, qelike_hist, qelikenot_hist)

    # Make a list of the MC hists for the fitter...
    mc_list = ROOT.TObjArray(2)
    mc_list.append(qelike_hist)
    mc_list.append(qelikenot_hist)

    # Get bin width for "step size" of fit
    x_max = mctot_hist.GetXaxis().GetXmax()
    binwid = x_max / max_bin

    # Set up fitter in verbose mode
    fit = ROOT.TFractionFitter(data_hist, mc_list, "V")
    virtual_fitter = fit.GetFitter()
    # Configure the fit for the qelike hist
    virtual_fitter.Config().ParSettings(0).Set(
        'qelike', prefit_sig_frac, binwid, 0.0, 1.0)
    # Confgure the fit for the qelikenot hist
    virtual_fitter.Config().ParSettings(1).Set(
        'qelikenot', prefit_bkg_frac, binwid, 0.0, 1.0)
    # Constrain the fit to between [0,1], since they are fracs and area-normed
    # fit.Constrain(0, 0.0, 1.0)
    fit.Constrain(1, 0.0, 1.0)
    fit.SetRangeX(min_bin, max_bin)
    # Do the fit
    status = fit.Fit()

    # Clean up
    del mctot_hist, qelike_hist, qelikenot_hist, data_hist

    if status != 0:
        print("WARNING: Fit did not converge...")
        return fit
    if status == 0:
        print("Fit converged.")
        return fit

    # TODO: Systematics.
    # Idea: Find scale factor for all universes,then combine to make a scale
    # factor MnvH1D? Only need to find stat error for just CV, not for the
    # systematic universes.


def GetOutVals(fit, prefit_frac, sample='qelikenot'):
    fit_frac = ctypes.c_double(0)
    fit_err = ctypes.c_double(0)
    if sample == 'qelike':
        fit.GetResult(0, fit_frac, fit_err)
    elif sample == 'qelikenot':
        fit.GetResult(1, fit_frac, fit_err)
    else:
        "CalculateScaleFactor: Error in sample name."
        sys.exit(0)
    fit_frac = fit_frac.value
    fit_err = fit_err.value

    scale = fit_frac / prefit_frac
    scale_err = fit_err / prefit_frac
    return fit_frac, fit_err, scale, scale_err


class logcheb:
    # Class for making a user defined Chebyshev polynomial to fit to.
    # Initialize some inputs
    def __init__(self, i_order, i_xmin, i_xmax):
        self.order = i_order
        self.xmin = i_xmin
        self.xmax = i_xmax

    # When calling in the TF1, you don't put in xx and p. ROOT does that for you.
    # This builds a parameterized function in the format needed for a fit TF1
    def __call__(self, xx, p):
        order = self.order
        xmin = self.xmin
        xmax = self.xmax

        # Chebyshev polynomials are defined on [-1,1], and this fit is over
        # log(x), so we need to transform x so the domain is correct.
        logx = math.log10(xx[0])
        logtop = math.log10(xmin * xmax)
        logbottom = math.log10(xmax / xmin)
        x = (2.0 * logx - logtop) / (logbottom)

        if order == 1:
            return p[0]
        elif order == 2:
            return p[0] + p[1] * x
        elif order == 3:
            return p[0] + p[1] * x + p[2] * (2.0 * x * x - 1.0)
        elif order == 4:
            return p[0] + p[1] * x + p[2] * (2.0 * x * x - 1.0) + p[3] * (4 * x * x * x - 3 * x)

        else:
            print("WARNING: Polys of order ", order,
                  " not set up. Returning order 1.")
            return p[0]


class logleg:
    # Class for making a user defined Legendre polynomial to fit to.
    # Initialize some inputs
    def __init__(self, i_order, i_xmin, i_xmax):
        self.order = i_order
        self.xmin = i_xmin
        self.xmax = i_xmax

    # When calling in the TF1, you don't put in xx and p. ROOT does that for you.
    # This builds a parameterized function in the format needed for a fit TF1
    def __call__(self, xx, p):
        order = self.order
        xmin = self.xmin
        xmax = self.xmax

        # Chebyshev polynomials are defined on [-1,1], and this fit is over
        # log(x), so we need to transform x so the domain is correct.
        logx = math.log10(xx[0])
        logtop = math.log10(xmin * xmax)
        logbottom = math.log10(xmax / xmin)
        x = (2.0 * logx - logtop) / (logbottom)

        if order == 1:
            return p[0]
        elif order == 2:
            return p[0] + p[1] * x
        elif order == 3:
            return p[0] + p[1] * x + p[2] * 0.5 * (3.0 * x * x - 1.0)
        elif order == 4:
            return p[0] + p[1] * x + p[2] * 0.5 * (3.0 * x * x - 1.0) + p[3] * 0.5 * (5.0 * x * x * x - 3.0 * x)

        else:
            print("WARNING: Polys of order ", order,
                  " not set up. Returning order 1.")
            return p[0]


def DoScaleFactorFit(scale_hist, order, xmin, xmax):
    # Initialize a chebyshev function in logx
    cheb = logcheb(order, xmin, xmax)
    function = ROOT.TF1("f1", cheb, xmin, xmax, order)
    # leg = logleg(order, xmin, xmax)
    # function = ROOT.TF1("f1", leg, xmin, xmax, order)

    # Run the fit. Could call the variable 'function' here instead if wanted.
    status = scale_hist.Fit("f1", "R,S,V")

    # Make a hist to plot the confidence interval for the fit function
    confint_hist = scale_hist.Clone("confint_hist")
    confint_hist.Reset()
    ROOT.TVirtualFitter.GetFitter().GetConfidenceIntervals(confint_hist, 0.95)

    status.Print("V")

    print("Finished fitting Scale Factor...")
    return scale_hist, confint_hist, function


def main():
    # This automatically does SetDirectory(0) to all hists. Makes code faster,
    # clean up easier, and mitigates segfault.
    ROOT.TH1.AddDirectory(ROOT.kFALSE)

    # Read in a file
    timestr = time.strftime("%Y%m%d-%H%M%S")

    if len(sys.argv) < 2:
        print("python FractionFitWithSystematics.py <infile>.root")
    else:
        filename = sys.argv[1]

    # ROOT file from output of eventloop in CCQENuMAT
    infile = ROOT.TFile(filename, "READONLY")

    dummy_q2_mnvh1d, dummy_q2_th1d = GetDummyHistCV(infile)

    dummy_recoil_mnvh1d, dummy_recoil_th1d = GetDummyHistCV(
        infile, "___recoil___")
    # Loop if you want to do several samples (like different energy cuts).
    # Loops over samples based off of hist name.
    for sample in sample_list:
        # Make dictionary of hists by sample & category from the in root file
        print("Starting on sample ", sample)
        # Grab the MnvH2D's from the file for data, and MC categories
        print("Getting MnvH2D's from file...")
        data_MnvH2D, qelike_MnvH2D, qelikenot_MnvH2D = GetDataMCMnvH2D(
            infile, category_list, sample)
        print("Done getting MnvH2D's from file.")
        # Area normalize MC categories to match data, and make total MC MnvH2D
        print("Making MC total and scaling MC hists...")
        qelike_MnvH2D, qelikenot_MnvH2D, mctot_MnvH2D = MakeMCandScale(
            data_MnvH2D, qelike_MnvH2D, qelikenot_MnvH2D)
        print("Done making MC total and scaling MC hists.")

        # This finds the number of x bins in Q^2 for fit bins.
        n_xbins = data_MnvH2D.GetNbinsX()

        # Make a dictionary for fitted recoil mnvh1ds to store later
        prefit_sig_mnvh_dict = {}
        prefit_bkg_mnvh_dict = {}
        fit_sig_mnvh_dict = {}
        fit_bkg_mnvh_dict = {}

        # Quick dict to store MnvH2Ds
        MnvH2D_dict = {'data': data_MnvH2D, 'mctot': mctot_MnvH2D,
                       'qelike': qelike_MnvH2D, 'qelikenot': qelikenot_MnvH2D}

        universe_names = qelike_MnvH2D.GetVertErrorBandNames()
        # Add in cv to universe
        universe_names_list = ["cv"]
        for name in universe_names:
            universe_names_list.append(name)

        sig_fitfrac_mnvh1d = dummy_q2_mnvh1d.Clone(
            "h___QELike___qelike___Q2QE___fraction")
        sig_scale_mnvh1d = dummy_q2_mnvh1d.Clone(
            "h___QELike___qelike___Q2QE___scale")
        bkg_fitfrac_mnvh1d = dummy_q2_mnvh1d.Clone(
            "h___QELike___qelikenot___Q2QE___fraction")
        bkg_scale_mnvh1d = dummy_q2_mnvh1d.Clone(
            "h___QELike___qelikenot___Q2QE___scale")

        # Loop over universe names
        for uni_name in universe_names_list:
            print("  Starting universe ", uni_name, "...")
            sig_fitfrac_hist_list = []
            sig_scale_hist_list = []
            bkg_fitfrac_hist_list = []
            bkg_scale_hist_list = []

            # To store the fitted recoil hists in
            fit_sig_uni_dict = {}
            fit_bkg_uni_dict = {}

            if uni_name == 'cv':
                n_universes = 1
            else:
                # Most have 2 hists (+/- 1 sigma or something similar)
                n_universes = mctot_MnvH2D.GetVertErrorBand(
                    uni_name).GetNHists()
            # Loop over each universe in the name
            for uni in range(0, n_universes):
                print("    Starting universe number", uni, "...")
                sig_fitfrac_hist = dummy_q2_th1d.Clone()
                sig_scale_hist = dummy_q2_th1d.Clone()
                bkg_fitfrac_hist = dummy_q2_th1d.Clone()
                bkg_scale_hist = dummy_q2_th1d.Clone()

                tmp_th2d_dict = {}
                # Grab the universe hist from the MnvH2D
                for key in MnvH2D_dict.keys():
                    if uni_name == "cv" or key == "data":
                        tmp_th2d = MnvH2D_dict[key].GetCVHistoWithStatError(
                        ).Clone()
                    else:
                        tmp_th2d = MnvH2D_dict[key].GetVertErrorBand(
                            uni_name).GetHist(uni).Clone()
                    tmp_th2d_dict[key] = tmp_th2d

                tmp_fitbin_th1d_dict = {}
                # Loop over fitbins for that universe
                for fitbin in range(1, n_xbins + 1):
                    fit_sig_uni_dict[fitbin] = []
                    fit_bkg_uni_dict[fitbin] = []
                    print("      Working on fitbin number ", fitbin)
                    fitbin_name = "Q2bin" + str("%02d" % (fitbin))
                    prefit_th1d_dict = {}

                    # Make MnvH1D hists by projecting on fit bin
                    tmp_prefit_dict = {}
                    for key in tmp_th2d_dict.keys():
                        proj_name = fitbin_name + '_' + key
                        tmp_fitbin_th1d = tmp_th2d_dict[key].ProjectionY(
                            proj_name, fitbin, fitbin, "e")
                        prefit_th1d_dict[key] = tmp_fitbin_th1d
                        print("     Number of entries in ", key,
                              ": ", tmp_fitbin_th1d.GetEntries())

                        # Need to make a Mnvh1d of each fitbin before the fit.
                        # Using 'cv' universe so this only happens once (rather
                        # than doing this step needlessly in every universe)

                        if uni_name == 'cv' and key in ['qelike', 'qelikenot']:
                            prefit_mnvh1d_name = "h___QELike___" + key + \
                                "___recoil_" + fitbin_name + "___prefit"
                            print(prefit_mnvh1d_name)
                            prefit_recoil_mnvh = MnvH2D_dict[key].ProjectionY(
                                prefit_mnvh1d_name, fitbin, fitbin, "e").Clone()

                            if key == 'qelike':
                                prefit_sig_mnvh_dict[fitbin] = prefit_recoil_mnvh
                            else:
                                prefit_bkg_mnvh_dict[fitbin] = prefit_recoil_mnvh

                    # Take out the hist for each sample type
                    data_hist = prefit_th1d_dict['data']
                    prefit_mctot_hist = prefit_th1d_dict['mctot']
                    prefit_qelike_hist = prefit_th1d_dict['qelike']
                    prefit_qelikenot_hist = prefit_th1d_dict['qelikenot']

                    # Calculate Chi2 between data & MC before the fit.
                    prefit_chi2 = data_hist.Chi2Test(prefit_mctot_hist, "CHI2")
                    prefit_ndf = data_hist.GetNbinsX() - 1

                    # Calculate & store pre-fit fractions of MC samples.
                    prefit_sig_frac, prefit_bkg_frac = GetSigBkgFrac(
                        prefit_mctot_hist, prefit_qelike_hist, prefit_qelikenot_hist)

                    print("      Running Fraction Fitter... ")
                    # Run the TFractionFitter and get values out
                    fit = RunFractionFitter(
                        prefit_mctot_hist, prefit_qelike_hist, prefit_qelikenot_hist, data_hist)
                    # Calculate scale factors for sig and bkg and errors
                    fit_sig_frac, fit_sig_err, sig_scale, sig_scale_err = GetOutVals(
                        fit, prefit_sig_frac, 'qelike')
                    fit_bkg_frac, fit_bkg_err, bkg_scale, bkg_scale_err = GetOutVals(
                        fit, prefit_bkg_frac, 'qelikenot')

                    # tmp_unihist_dict = {}
                    tmp_fit_sig_th1d = prefit_th1d_dict['qelike'].Clone()
                    tmp_fit_sig_th1d.Scale(sig_scale)
                    tmp_fit_bkg_th1d = prefit_th1d_dict['qelikenot'].Clone()
                    tmp_fit_bkg_th1d.Scale(bkg_scale)

                    if uni_name == 'cv':
                        print("      Filling CVs...")
                        sig_fitfrac_mnvh1d.SetBinContent(fitbin, fit_sig_frac)
                        sig_fitfrac_mnvh1d.SetBinError(fitbin, fit_sig_err)

                        sig_scale_mnvh1d.SetBinContent(fitbin, sig_scale)
                        sig_scale_mnvh1d.SetBinError(fitbin, sig_scale_err)

                        bkg_fitfrac_mnvh1d.SetBinContent(fitbin, fit_bkg_frac)
                        bkg_fitfrac_mnvh1d.SetBinError(fitbin, fit_bkg_err)

                        bkg_scale_mnvh1d.SetBinContent(fitbin, bkg_scale)
                        bkg_scale_mnvh1d.SetBinError(fitbin, bkg_scale_err)

                        fit_sig_mnvh1d = MnvH1D(tmp_fit_sig_th1d)
                        fit_sig_mnvh1d.SetName(
                            "h___QELike___qelike___recoil_" + fitbin_name + "___fit")

                        fit_bkg_mnvh1d = MnvH1D(tmp_fit_bkg_th1d)
                        fit_bkg_mnvh1d.SetName(
                            "h___QELike___qelikenot___recoil_" + fitbin_name + "___fit")

                        fit_sig_mnvh_dict[fitbin] = fit_sig_mnvh1d
                        fit_bkg_mnvh_dict[fitbin] = fit_bkg_mnvh1d
                    else:
                        print("      Filling hists for error band ",
                              uni_name, "...")
                        sig_fitfrac_hist.SetBinContent(fitbin, fit_sig_frac)
                        sig_fitfrac_hist.SetBinError(fitbin, fit_sig_err)

                        sig_scale_hist.SetBinContent(fitbin, sig_scale)
                        sig_scale_hist.SetBinError(fitbin, sig_scale_err)

                        bkg_fitfrac_hist.SetBinContent(fitbin, fit_bkg_frac)
                        bkg_fitfrac_hist.SetBinError(fitbin, fit_bkg_err)

                        bkg_scale_hist.SetBinContent(fitbin, bkg_scale)
                        bkg_scale_hist.SetBinError(fitbin, bkg_scale_err)

                        fit_sig_uni_dict[fitbin].append(tmp_fit_sig_th1d)
                        fit_bkg_uni_dict[fitbin].append(tmp_fit_bkg_th1d)

                        # Kind of hacky. When you've looped over every universe,
                         # add the vert error band for the recoil plots.
                        if uni == n_universes - 1:
                            fit_sig_mnvh_dict[fitbin].AddVertErrorBand(
                                uni_name, fit_sig_uni_dict[fitbin])
                            fit_bkg_mnvh_dict[fitbin].AddVertErrorBand(
                                uni_name, fit_bkg_uni_dict[fitbin])

                # Add the hists for this universe to a list (unless its the cv)
                if uni_name != 'cv':
                    sig_fitfrac_hist_list.append(sig_fitfrac_hist)
                    sig_scale_hist_list.append(sig_scale_hist)
                    bkg_fitfrac_hist_list.append(bkg_fitfrac_hist)
                    bkg_scale_hist_list.append(bkg_scale_hist)
            # Add list of TH1D's for error band to MnvH1D
            # NOTE 'cv' needs to be first in the list of universes
            if uni_name == 'cv':
                print("  Done filling CVs...")
            else:
                print("  Adding vert error band ", uni_name, " to MnvH1Ds... ")
                sig_fitfrac_mnvh1d.AddVertErrorBand(
                    uni_name, sig_fitfrac_hist_list)
                sig_scale_mnvh1d.AddVertErrorBand(
                    uni_name, sig_scale_hist_list)
                bkg_fitfrac_mnvh1d.AddVertErrorBand(
                    uni_name, bkg_fitfrac_hist_list)
                bkg_scale_mnvh1d.AddVertErrorBand(
                    uni_name, bkg_scale_hist_list)

        print("Done filling hists... ")
        print("Syncing bands... ")
        SyncBands(sig_fitfrac_mnvh1d)
        SyncBands(sig_scale_mnvh1d)
        SyncBands(bkg_fitfrac_mnvh1d)
        SyncBands(bkg_scale_mnvh1d)
        for hist in fit_sig_mnvh_dict:
            SyncBands(fit_sig_mnvh_dict[hist])
            SyncBands(fit_bkg_mnvh_dict[hist])

        histfile_tail = "_Hists.root"
        histfile_name = filename.replace(".root", histfile_tail)
        print("Writing input & fitted hists to file: ", histfile_name)
        outhistfile = ROOT.TFile(histfile_name, "RECREATE")
        for histkey in MnvH2D_dict:
            outhistfile.cd()
            MnvH2D_dict[histkey].Write()
        for fitbin in range(1, n_xbins + 1):
            outhistfile.cd()
            prefit_sig_mnvh_dict[fitbin].Write()
            outhistfile.cd()
            fit_sig_mnvh_dict[fitbin].Write()
            outhistfile.cd()
            prefit_bkg_mnvh_dict[fitbin].Write()
            outhistfile.cd()
            fit_bkg_mnvh_dict[fitbin].Write()
        outhistfile.Close()

        # Write out each hist to a root file.
        outvalhistfile_tail = "_OutVals_fix.root"
        outvalhistfile = filename.replace(".root", outvalhistfile_tail)
        print("Writing scale and fraction hists to file: ", outvalhistfile)
        outvalfile = ROOT.TFile(outvalhistfile, "RECREATE")
        outvalfile.cd()
        sig_fitfrac_mnvh1d.Write()
        outvalfile.cd()
        sig_scale_mnvh1d.Write()
        outvalfile.cd()
        bkg_fitfrac_mnvh1d.Write()
        outvalfile.cd()
        bkg_scale_mnvh1d.Write()
        outvalfile.Close()


if __name__ == "__main__":
    main()
