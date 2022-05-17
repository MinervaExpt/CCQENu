import ROOT
from PlotUtils import MnvH1D, MnvH2D
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
TEST = False
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

        if histocategory=='data':
            data_hist2D = rfile.Get(hist_name).Clone()
            datafound = 1
        if histocategory=='qelike':
            qelike_hist2d = rfile.Get(hist_name).Clone()
            qelikefound = 1
        if histocategory=='qelikenot':
            qelikenot_hist2d = rfile.Get(hist_name).Clone()
            qelikenotfound = 1

        if datafound==1 and qelikefound==1 and qelikenotfound==1:
            return data_hist2D, qelike_hist2d, qelikenot_hist2d
        else:
            continue

    if datafound+qelikefound+qelikenotfound<3:
        print("Error: Could not find the required histograms in the input file.")
        sys.exit()

def GetFitBinning(rfile):
    # Grabs binning from a CCQENuMAT variable config stored in root file.
    varsFile = rfile.Get("varsFile").GetTitle()
    vars_dict = json.loads(varsFile)
    binning = vars_dict['1D']['Q2QE']['bins']
    return binning


def GetDummyHistCV(rfile):
    # Make a dummy 1D hist to get binning. Just grabs first 1D Q2QE plot
    histkeys_list = rfile.GetListOfKeys()
    for histkey in histkeys_list:
        hist_name = histkey.GetName()
        if hist_name.find("___Q2QE___") == -1: #TODO: This is hardcoded, should change it
            continue
        else:
            # This *should* be a TH1D
            dummy_mnvh1d = rfile.Get(hist_name).Clone()
            dummy_th1d = dummy_mnvh1d.GetCVHistoWithStatError().Clone()
            # Clears hist, leaves only binning
            dummy_mnvh1d.ClearAllErrorBands()
            dummy_mnvh1d.Reset("ICES")
            dummy_th1d.Reset("ICES")
            return dummy_mnvh1d,dummy_th1d
    print("No suitable hist to make a dummy with. Exiting...")
    sys.exit()

def MakeValDict(n_xbins,universe_names_list,qelike_MnvH2D):
    uni_val_dict = {}
    fitbin_list = []
    for fitbin in range(1,n_xbins+1):
        fitbin_list.append([])

    for uni_name in universe_names_list:
        if uni_name=="cv":
            n_universes = 1
        else:
            n_universes = qelike_MnvH2D.GetVertErrorBand(uni_name).GetNHists()

        uni_list=[]
        for uni in range(0,n_universes):
            uni_list.append(fitbin_list)
        print("Number of universes: ",len(uni_list))
        uni_val_dict[uni_name]=uni_list
    return uni_val_dict


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

    #Close logfile
    def close(self):
        self.logfile.close()


def PrintFitResults(fit, function):
    print("Function: ",function.GetExpFormula())
    print("chi2: ",function.GetChisquare())
    print("ndf: ",function.GetNDF())
    print("Covariance Matrix: ",fit.GetCovarianceMatrix())
    print("Correlation Matrix: ",fit.GetCorrelationMatrix())


def MakeMCandScale(i_data_hist, qelike_hist, qelikenot_hist):
    data_hist = i_data_hist.Clone()

    # Make total MC hist by adding qelike, qelikenot
    mctot_hist = qelike_hist.Clone("mc")
    mctot_hist.Add(qelikenot_hist, 1.0)

    # Make area scale for MC hists. Don't include underflow & overflow bins
    min_bin = 1
    max_xbin = data_hist.GetNbinsX()
    max_ybin = data_hist.GetNbinsY()
    area_scale = (data_hist.Integral(min_bin, max_xbin, min_bin, max_ybin))/ (mctot_hist.Integral(min_bin, max_xbin, min_bin, max_ybin))

    # Scale MC hists to area normalize them to Data (so # counts is the same)
    mctot_hist.Scale(area_scale)
    qelike_hist.Scale(area_scale)
    qelikenot_hist.Scale(area_scale)

    return qelike_hist, qelikenot_hist, mctot_hist


def GetSigBkgFrac(i_mctot_hist, i_sig_hist, i_bkg_hist):
    mc_int = i_mctot_hist.Integral(1,i_mctot_hist.GetNbinsX())
    qelike_int = i_sig_hist.Integral(1,i_sig_hist.GetNbinsX())
    qelikenot_int = i_bkg_hist.Integral(1,i_bkg_hist.GetNbinsX())

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
    before_sig_frac, before_bkg_frac = GetSigBkgFrac(mctot_hist,qelike_hist,qelikenot_hist)

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
        'qelike', before_sig_frac, binwid, 0.0, 1.0)
    # Confgure the fit for the qelikenot hist
    virtual_fitter.Config().ParSettings(1).Set(
        'qelikenot', before_bkg_frac, binwid, 0.0, 1.0)
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

def GetOutVals(fit, before_frac, sample='qelikenot'):
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

    scale = fit_frac / before_frac
    scale_err = fit_err / before_frac
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
            return p[0] + p[1] * x + p[2] * 0.5*(3.0 * x * x - 1.0)
        elif order == 4:
            return p[0] + p[1] * x + p[2] * 0.5*(3.0 * x * x - 1.0) + p[3] * 0.5 * (5.0 * x * x * x - 3.0 * x)

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
    ROOT.TVirtualFitter.GetFitter().GetConfidenceIntervals(confint_hist,0.95)

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

    # Get the binning of Q2QE
    binning = GetFitBinning(infile)
    dummy_q2_mnvh1d, dummy_q2_th1d = GetDummyHistCV(infile)

    # Loop if you want to do several samples (like different energy cuts).
    # Loops over samples based off of hist name.
    for sample in sample_list:
        # Make dictionary of hists by sample & category from the in root file
        print("Starting on sample ", sample)
        # Grab the MnvH2D's from the file for data, and MC categories
        print("Getting MnvH2D's from file...")
        data_MnvH2D, qelike_MnvH2D, qelikenot_MnvH2D = GetDataMCMnvH2D(infile, category_list, sample)
        print("     Done getting MnvH2D's from file.")
        # Area normalize MC categories to match data, and make total MC MnvH2D
        print("Making MC total and scaling MC hists...")
        qelike_MnvH2D, qelikenot_MnvH2D, mctot_MnvH2D = MakeMCandScale(data_MnvH2D, qelike_MnvH2D, qelikenot_MnvH2D)
        print("     Done making MC total and scaling MC hists.")

        # This finds the number of x bins in Q^2 for fit bins.
        n_xbins = data_MnvH2D.GetNbinsX()
        # Quick dict to store MnvH2Ds
        MnvH2D_dict = {'data':data_MnvH2D,'mctot':mctot_MnvH2D,'qelike':qelike_MnvH2D,'qelikenot':qelikenot_MnvH2D}

        universe_names = qelike_MnvH2D.GetVertErrorBandNames()
        # Add in cv to universe
        universe_names_list = ["cv"]
        for name in universe_names:
            universe_names_list.append(name)

        # Set up a dict to fill values in
        sig_fit_dict = MakeValDict(n_xbins,universe_names_list,qelike_MnvH2D)
        bkg_fit_dict = MakeValDict(n_xbins,universe_names_list,qelikenot_MnvH2D)

        # sig_nofit_dict = MakeValDict(n_xbins,universe_names_list,qelike_MnvH2D)
        # bkg_nofit_dict = MakeValDict(n_xbins,universe_names_list,qelike_MnvH2D)

        sig_scale_dict = MakeValDict(n_xbins,universe_names_list,qelike_MnvH2D)
        bkg_scale_dict = MakeValDict(n_xbins,universe_names_list,qelikenot_MnvH2D)

        # TODO: Try putting these here to fill?
        # sig_fit_mnvh1d = dummy_q2_mnvh1d.Clone("h___QELike___qelike___fraction")
        # sig_scale_mnvh1d = dummy_q2_mnvh1d.Clone("h___QELike___qelike___scale")
        # bkg_fit_mnvh1d = dummy_q2_mnvh1d.Clone("h___QELike___qelikenot___fraction")
        # bkg_scale_mnvh1d = dummy_q2_mnvh1d.Clone("h___QELike___qelikenot___scale")

        # Loop over fitbins (excluding under/overflow)
        for fitbin in range(1, n_xbins + 1):
            print("Working on fitbin number ",fitbin)
            fitbin_name = "Q2bin" + str("%02d" % (fitbin))
            fitbin_hist1d_dict = {}
            # Make MnvH1D hists by projecting on fit bin
            for key in MnvH2D_dict.keys():
                proj_name = fitbin_name + '_' + key
                tmp_fitbin_MnvH1D = MnvH2D_dict[key].ProjectionY(proj_name, fitbin, fitbin, "e")
                # tmp_fitbin_MnvH1D = tmp_fitbin_MnvH1D.Rebin(2)
                fitbin_hist1d_dict[key] = tmp_fitbin_MnvH1D
                print("     Number of entries in ",key,": ",tmp_fitbin_MnvH1D.GetEntries())

            # Get a copy of the data
            data_hist = fitbin_hist1d_dict['data'].GetCVHistoWithStatError().Clone()
            # Loop over universes
            for uni_name in universe_names_list:

                uni_val_list = []
                if uni_name=="cv":
                    n_universes = 1
                else:
                    # Most have 2 hists (+/- 1 sigma or something similar)
                    n_universes = mctot_MnvH2D.GetVertErrorBand(uni_name).GetNHists()
                # Loop over number of universes in each universe
                for uni in range(0,n_universes):

                    # Grab the CV or the error band hist
                    if uni_name=="cv":
                        before_mctot_hist = fitbin_hist1d_dict['mctot'].GetCVHistoWithStatError().Clone()
                        before_qelike_hist = fitbin_hist1d_dict['qelike'].GetCVHistoWithStatError().Clone()
                        before_qelikenot_hist = fitbin_hist1d_dict['qelikenot'].GetCVHistoWithStatError().Clone()
                    else:
                        before_mctot_hist = fitbin_hist1d_dict['mctot'].GetVertErrorBand(uni_name).GetHist(uni).Clone()
                        before_qelike_hist = fitbin_hist1d_dict['qelike'].GetVertErrorBand(uni_name).GetHist(uni).Clone()
                        before_qelikenot_hist = fitbin_hist1d_dict['qelikenot'].GetVertErrorBand(uni_name).GetHist(uni).Clone()

                    # Calculate Chi2 between data & MC before the fit.
                    before_chi2 = data_hist.Chi2Test(before_mctot_hist,"CHI2")
                    before_ndf = data_hist.GetNbinsX()-1

                    # Calculate & store pre-fit fractions of MC samples.
                    before_sig_frac, before_bkg_frac = GetSigBkgFrac(before_mctot_hist,before_qelike_hist,before_qelikenot_hist)

                    # Test values to debug to streamline testing functionality downsteam
                    if TEST:
                        fit_sig_frac = before_sig_frac
                        fit_sig_err = 0.0
                        sig_scale = 1.0
                        sig_scale_err = 0.0
                        fit_bkg_frac = before_bkg_frac
                        fit_bkg_err = 0.0
                        bkg_scale = 1.0
                        bkg_scale_err = 0.0
                    else:
                        # Run the TFractionFitter and get values out
                        fit = RunFractionFitter(before_mctot_hist, before_qelike_hist, before_qelikenot_hist, data_hist)

                        # Calculate scale factors for sig and bkg and errors
                        fit_sig_frac, fit_sig_err, sig_scale, sig_scale_err = GetOutVals(fit, before_sig_frac, 'qelike')
                        fit_bkg_frac, fit_bkg_err, bkg_scale, bkg_scale_err = GetOutVals(fit, before_bkg_frac, 'qelikenot')
                        print("universe: ",uni, uni_name," fit sig frac: ",fit_sig_frac," sig scale: ",sig_scale)
                        print("universe: ",uni, uni_name," fit bkg frac: ",fit_bkg_frac," sig scale: ",bkg_scale)

                    sig_fit_vals = [fit_sig_frac,fit_sig_err]
                    sig_scale_vals = [sig_scale,sig_scale_err]
                    bkg_fit_vals = [fit_bkg_frac,fit_bkg_err]
                    bkg_scale_vals = [bkg_scale,bkg_scale_err]

                    # Store all the values in the appropriate dict
                    sig_fit_dict[uni_name][uni][fitbin-1]=sig_fit_vals
                    # sig_nofit_dict[uni_name][uni][fitbin-1]=[before_sig_frac,0]
                    sig_scale_dict[uni_name][uni][fitbin-1]=sig_scale_vals

                    bkg_fit_dict[uni_name][uni][fitbin-1]=bkg_fit_vals
                    # bkg_fit_dict[uni_name][uni][fitbin-1]=[fit_bkg_frac,fit_bkg_err]
                    # print("universe: ",uni_name,uni," check bkg_fit_dict: ",bkg_fit_dict[uni_name][uni][fitbin-1], " here")
                    # bkg_nofit_dict[uni_name][uni][fitbin-1]=[before_bkg_frac,0]
                    bkg_scale_dict[uni_name][uni][fitbin-1]=bkg_scale_vals

        # Make an empty copy of the dummy Q^2 hist to fill with scale factors or fractions
        # sig_fit_mnvh1d = dummy_q2_mnvh1d.Clone("h___QELike___qelike___fraction")
        # sig_scale_mnvh1d = dummy_q2_mnvh1d.Clone("h___QELike___qelike___scale")
        # bkg_fit_mnvh1d = dummy_q2_mnvh1d.Clone("h___QELike___qelikenot___fraction")
        # bkg_scale_mnvh1d = dummy_q2_mnvh1d.Clone("h___QELike___qelikenot___scale")

        print(sig_fit_dict)
        # Loop over fitbins (excluding under/overflow)
        for fitbin in range(1,n_xbins+1):
            # Fill the CV for each value hist
            sig_fit_mnvh1d.SetBinContent(fitbin,sig_fit_dict["cv"][0][fitbin-1][0])
            sig_fit_mnvh1d.SetBinError(fitbin,sig_fit_dict["cv"][0][fitbin-1][1])
            # print("sig fit ", sig_fit_dict["cv"][0][fitbin-1][0])

            sig_scale_mnvh1d.SetBinContent(fitbin,sig_scale_dict["cv"][0][fitbin-1][0])
            sig_scale_mnvh1d.SetBinError(fitbin,sig_scale_dict["cv"][0][fitbin-1][1])
            # print("sig scale ", sig_scale_dict["cv"][0][fitbin-1][0])

            bkg_fit_mnvh1d.SetBinContent(fitbin,bkg_fit_dict["cv"][0][fitbin-1][0])
            bkg_fit_mnvh1d.SetBinError(fitbin,bkg_fit_dict["cv"][0][fitbin-1][1])
            # print("bkg fit ", bkg_fit_dict["cv"][0][fitbin-1][0])

            bkg_scale_mnvh1d.SetBinContent(fitbin,bkg_scale_dict["cv"][0][fitbin-1][0])
            bkg_scale_mnvh1d.SetBinError(fitbin,bkg_scale_dict["cv"][0][fitbin-1][1])
            # print("bkg scale ", bkg_scale_dict["cv"][0][fitbin-1][0])

        # Loop over universes to fill in TH1D's
        for uni_name in sig_fit_dict.keys():
            if uni_name=="cv":
                continue
            else:
                print("Filling hist for universe ",uni_name)
                sig_fit_hist_list = []
                sig_scale_hist_list = []
                bkg_fit_hist_list = []
                bkg_scale_hist_list = []
                n_universes = mctot_MnvH2D.GetVertErrorBand(uni_name).GetNHists()
                for uni in range(0,n_universes):
                    sig_fit_hist = dummy_q2_th1d.Clone()
                    sig_scale_hist = dummy_q2_th1d.Clone()
                    bkg_fit_hist = dummy_q2_th1d.Clone()
                    bkg_scale_hist = dummy_q2_th1d.Clone()
                    for fitbin in range(1,n_xbins+1):
                        sig_fit_hist.SetBinContent(fitbin,sig_fit_dict[uni_name][uni][fitbin-1][0])
                        sig_fit_hist.SetBinError(fitbin,sig_fit_dict[uni_name][uni][fitbin-1][1])

                        sig_scale_hist.SetBinContent(fitbin,sig_scale_dict[uni_name][uni][fitbin-1][0])
                        sig_scale_hist.SetBinError(fitbin,sig_scale_dict[uni_name][uni][fitbin-1][1])

                        bkg_fit_hist.SetBinContent(fitbin,bkg_fit_dict[uni_name][uni][fitbin-1][0])
                        bkg_fit_hist.SetBinError(fitbin,bkg_fit_dict[uni_name][uni][fitbin-1][1])
                        # print("universe: ",uni_name,uni," check bkg_fit_dict: ",bkg_fit_dict[uni_name][uni][fitbin-1], " here")

                        bkg_scale_hist.SetBinContent(fitbin,bkg_scale_dict[uni_name][uni][fitbin-1][0])
                        bkg_scale_hist.SetBinError(fitbin,bkg_scale_dict[uni_name][uni][fitbin-1][1])
                    # Add universe TH1D to list of hists
                    sig_fit_hist_list.append(sig_fit_hist)
                    sig_scale_hist_list.append(sig_scale_hist)
                    bkg_fit_hist_list.append(bkg_fit_hist)
                    bkg_scale_hist_list.append(bkg_scale_hist)
                # Add list of universe hists to error band in mnvh1d
                # TODO: check this out,
                sig_fit_mnvh1d.AddVertErrorBand(uni_name,sig_fit_hist_list)
                sig_scale_mnvh1d.AddVertErrorBand(uni_name,sig_scale_hist_list)
                bkg_fit_mnvh1d.AddVertErrorBand(uni_name,bkg_fit_hist_list)
                bkg_scale_mnvh1d.AddVertErrorBand(uni_name,bkg_scale_hist_list)

        # Write out each hist to a root file.
        scalehistfile_tail = "_OutVals.root"
        outfilename = filename.replace(".root", scalehistfile_tail)
        outfile = ROOT.TFile(outfilename, "RECREATE")
        outfile.cd()
        sig_fit_mnvh1d.Write()
        outfile.cd()
        sig_scale_mnvh1d.Write()
        outfile.cd()
        bkg_fit_mnvh1d.Write()
        outfile.cd()
        bkg_scale_mnvh1d.Write()
        outfile.Close()


if __name__ == "__main__":
    main()
