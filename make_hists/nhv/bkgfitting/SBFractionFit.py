from unicodedata import category
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
category_list = ["data", "qelike", "chargedpion", "neutralpion", "multipion", "other"]
mc_category_list = ["qelike", "chargedpion", "neutralpion", "multipion", "other"]
variable_list = ["Q2QE_recoil"]
# names associated with each "sample" e.g. QElike, QElikeALL
# sample_list = ["QElike", "QElike_hiE", "QElike_loE"]
# sample_list = ["Background"]
sample = "Background"
sample_list = ["Background"]
# DO_SYSTEMATICS = False
# DRAW = True
# CONFINT = True

# Do fit on tuned hists or not
useTuned = 0

# Some fit parameters globally set
min_bin = 1
step_size = 0.02

# This is based off of how fitbins are made (i.e. making sidebands that have
# cuts on binedges of the variable you're making), and the histogram naming
# convention CCQENuMAT

# recoil_type = "Log10recoil"

recoil_type = "recoil"

def GetDataMCHistDict(rfile):
    print("Before GetDataMCHistDict")
    keys = rfile.GetListOfKeys()
    print("After GetListOfKeys")
    # raw_hist_dict = {}
    data_hist_dict = {}
    mc_hist_dict = {}
    for key in keys:
        hist_name = key.GetName()
        print(hist_name)
        # Get rid of non-hist branches.
        if hist_name.find("___") == -1:
            continue
        splitnames_list = hist_name.split('___')
        hist_dim = splitnames_list[0]
        hist_sample = splitnames_list[1]
        hist_category = splitnames_list[2]
        hist_variable = splitnames_list[3]
        hist_type = splitnames_list[4]

        if hist_dim != 'h2D':
            continue
        if hist_sample not in sample_list:
            continue
        if hist_variable not in variable_list:
            continue
        if hist_category not in category_list:
            continue
        if hist_category!='data' and useTuned>0 and 'tuned' not in hist_type:
            continue
        
        if hist_category=='data':
            data_hist_dict[hist_name]=rfile.Get(hist_name).Clone()
        elif 'reconstructed' in hist_type:
            mc_hist_dict[hist_name]=rfile.Get(hist_name).Clone()
        
        # raw_hist_dict[hist_name]=rfile.Get(hist_name).Clone()
    # return raw_hist_dict
    return data_hist_dict, mc_hist_dict

def GetConfigFromFile(rfile):
    config_dict = {}

    config_dict["main"] = NuConfig(rfile.Get("main").GetTitle())
    config_dict["varsFile"] = NuConfig(rfile.Get("varsFile").GetTitle())
    config_dict["cutsFile"] = NuConfig(rfile.Get("cutsFile").GetTitle())
    config_dict["samplesFile"] = NuConfig(rfile.Get("samplesFile").GetTitle())

    return config_dict

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

def PrintFitResults(fit, function):
    print("Function: ", function.GetExpFormula())
    print("chi2: ", function.GetChisquare())
    print("ndf: ", function.GetNDF())
    print("Covariance Matrix: ", fit.GetCovarianceMatrix())
    print("Correlation Matrix: ", fit.GetCorrelationMatrix())



def MakeMC(i_qelike_hist, i_qelikenot_hist):
    qelike_hist = i_qelike_hist.Clone()
    qelikenot_hist = i_qelikenot_hist.Clone()

    # Make total MC hist by adding qelike, qelikenot
    mctot_hist = qelike_hist.Clone("mc")
    mctot_hist.Add(qelikenot_hist, 1.0)

    return mctot_hist

def ScaleMC(i_data_hist,i_mctot_hist,i_qelike_hist,i_qelikenot_hist):
    data_hist = i_data_hist.Clone()
    mctot_hist = i_mctot_hist.Clone()
    qelike_hist=i_qelike_hist.Clone()
    qelikenot_hist=i_qelikenot_hist.Clone()

    min_bin = 6 #1
    max_xbin = data_hist.GetNbinsX()
    area_scale = (data_hist.Integral(min_bin, max_xbin)) / (mctot_hist.Integral(min_bin, max_xbin))

    # Scale MC hists to area normalize them to Data (so # counts is the same)
    mctot_hist.Scale(area_scale)
    qelike_hist.Scale(area_scale)
    qelikenot_hist.Scale(area_scale)

    return mctot_hist,qelike_hist,qelikenot_hist


def GetSigBkgFrac(i_mctot_hist, i_sig_hist, i_bkg_hist):
    # min_bin = 6
    mc_int = i_mctot_hist.Integral(min_bin, i_mctot_hist.GetNbinsX())
    qelike_int = i_sig_hist.Integral(min_bin, i_sig_hist.GetNbinsX())
    qelikenot_int = i_bkg_hist.Integral(min_bin, i_bkg_hist.GetNbinsX())

    sig_frac = qelike_int / mc_int
    bkg_frac = qelikenot_int / mc_int
    return sig_frac, bkg_frac

def GetMCFracList(i_mctot_hist, i_mc_hist_list):
    mctot_int = i_mctot_hist.Integral(min_bin, i_mctot_hist.GetNbinsX())
    mc_frac_list = []
    for mc_hist in i_mc_hist_list:
        mc_hist_int = mc_hist.Integral(min_bin, mc_hist.GetNbinsX())
        mc_frac = mc_hist_int / mctot_int
        mc_frac_list.append(mc_frac)
    return mc_frac_list


# def RunFractionFitter(i_mctot_hist, i_qelike_hist, i_qelikenot_hist, i_data_hist):
def RunFractionFitter(i_data_hist, i_mc_hist_list, i_mctot_hist):
    data_hist = i_data_hist.Clone()
    mctot_hist = i_mctot_hist.Clone()
    mc_hist_list = []
    for mc_hist in i_mc_hist_list:
        mc_hist_list.append(mc_hist.Clone())

    # Get min and max bin for fitting (underflow is 0, overflow is nbins+1)
    # min_bin = 1
    max_bin = mctot_hist.GetNbinsX()

    print(">>>>>>>>>max_bin ", max_bin)

    # Calculate & store pre-fit fractions of MC samples.
    # prefit_sig_frac, prefit_bkg_frac = GetSigBkgFrac(
    #     mctot_hist, qelike_hist, qelikenot_hist)
    mc_frac_list = GetMCFracList(mctot_hist,mc_hist_list)

    # Make a list of the MC hists for the fitter...
    # mc_list = ROOT.TObjArray(2)
    # mc_list.append(qelike_hist)
    # mc_list.append(qelikenot_hist)
    mc_hist_array = ROOT.TObjArray(len(mc_frac_list))
    for mc_hist in mc_hist_list:
        mc_hist_array.append(mc_hist)

    # Set up fitter in verbose mode
    fit = ROOT.TFractionFitter(data_hist, mc_list, "V") # TODO: what's the V do here again? Verbose mode?
    virtual_fitter = fit.GetFitter()
    # Configure the fit for the qelike hist
    # # virtual_fitter.Config().ParSettings(0).Set('qelike', prefit_sig_frac, binwid, 0.0, 1.0)
    # virtual_fitter.Config().ParSettings(0).Set('qelike', prefit_sig_frac, 0.02, 0.0, 1.0) #Switched step size to be the bin width of 25 recoil bins
    # # Confgure the fit for the qelikenot hist
    # # virtual_fitter.Config().ParSettings(1).Set('qelikenot', prefit_bkg_frac, binwid, 0.0, 1.0)
    # virtual_fitter.Config().ParSettings(1).Set('qelikenot', prefit_bkg_frac, 0.02, 0.0, 1.0)

    # Configure the fit for each mc hist. Names from mc_category_list should share index with hist and histfrac lists
    for i in range(len(mc_hist_list)):
        virtual_fitter.Config().ParSettings(i).Set(mc_category_list[i], mc_frac_list[i], step_size, 0.0, 1.0) #Switched step size to be the bin width of 25 recoil bins
        fit.Constrain(i, 0.0, 1.0)

    # # Constrain the fit to between [0,1], since they are fracs and area-normed
    # # fit.Constrain(0, 0.0, 1.0)
    # fit.Constrain(1, 0.0, 1.0)

    # Set the bin range you want to fit on
    fit.SetRangeX(min_bin, max_bin)
    # Do the fit
    status = fit.Fit()

    # Clean up
    # del mctot_hist, qelike_hist, qelikenot_hist, data_hist # TODO: reimpliment with lists. Necessary?

    if status != 0:
        print("WARNING: Fit did not converge...")
        return fit
    if status == 0:
        print("Fit converged.")
        return fit


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

def GetFitBinning(rfile):
    # Grabs binning from a CCQENuMAT variable config stored in root file.
    varsFile = rfile.Get("varsFile").GetTitle()
    vars_dict = json.loads(varsFile)
    binning = vars_dict['1D']['Q2QE']['recobins']
    return binning


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

    outfilebase = filename.replace(".root","_"+recoil_type+".root")
    # dummy q2 and recoil hists, both mnvhnd and th2d
    dummy_q2_mnvh1d, dummy_q2_th1d = GetDummyHistCV(infile)

    dummy_recoil_mnvh1d, dummy_recoil_th1d = GetDummyHistCV(infile, "___"+recoil_type+"___")

    n_xbins = dummy_q2_mnvh1d.GetNbinsX()

    raw_data_mnvh2d_dict, raw_mc_mnvh2d_dict = GetDataMCHistDict(infile)

    mnvh2d_sample_dict = {}    
    dummy_category_dict = {}
    for category in category_list:
        dummy_category_dict[category] = None
    
    for sample in sample_list:
        mnvh2d_sample_dict[sample] = dummy_category_dict
    
    for hist_name in raw_data_mnvh2d_dict.keys():
        for sample in sample_list:
            if sample in hist_name:
                mnvh2d_sample_dict[sample]['data'] = raw_data_mnvh2d_dict[hist_name]
    for hist_name in raw_mc_mnvh2d_dict:
        for sample in sample_list:
                if sample in hist_name:
                    for category in mc_category_list:
                        if category in hist_name:
                            mnvh2d_sample_dict[sample][category] = raw_mc_mnvh2d_dict[hist_name]
    
    mnvh2d_category_dict = {}    
    dummy_sample_dict = {}
    for sample in sample_list:
        dummy_sample_dict[sample] = None
    
    for category in category_list:
        mnvh2d_category_dict[category] = dummy_sample_dict
    
    for hist_name in raw_data_mnvh2d_dict.keys():
        for sample in sample_list:
            if sample in hist_name:
                mnvh2d_sample_dict['data'][sample] = raw_data_mnvh2d_dict[hist_name]
    for hist_name in raw_mc_mnvh2d_dict:
        for sample in sample_list:
                if sample in hist_name:
                    for category in mc_category_list:
                        if category in hist_name:
                            mnvh2d_sample_dict[sample][category] = raw_mc_mnvh2d_dict[hist_name]
    



    universe_names_list = ['cv']
    for univ_name in dummy_q2_mnvh1D.GetVertErrorBandNames():
        universe_names_list.append()

    for univ_name in universe_names_list:
        print("  Starting universe ", uni_name, "...")







    # Loop if you want to do several samples (like different energy cuts).
    # Loops over samples based off of hist name.
    

    for sample in sample_list:
        # Make dictionary of hists by sample & category from the in root file
        print("Starting on sample ", sample)
        # Grab the MnvH2D's from the file for data, and MC categories
        print("Getting MnvH2D's from file...")
        # data_MnvH2D, qelike_MnvH2D, qelikenot_MnvH2D, qelike_tuned_MnvH2D, qelikenot_tuned_MnvH2D= GetDataMCMnvH2D(infile, category_list, sample)
        data_MnvH2D, qelike_MnvH2D, qelikenot_MnvH2D= GetDataMCMnvH2D(infile, category_list, sample)
        print("Done getting MnvH2D's from file.")
        # Area normalize MC categories to match data, and make total MC MnvH2D
        print("Making MC total and scaling MC hists...")
        mctot_MnvH2D = MakeMC(qelike_MnvH2D, qelikenot_MnvH2D)
        # mctot_tuned_MnvH2D = MakeMC(qelike_tuned_MnvH2D, qelikenot_tuned_MnvH2D)
        print("Done making MC total and scaling MC hists.")

        # This finds the number of x bins in Q^2 for fit bins.
        n_xbins = data_MnvH2D.GetNbinsX()

        # Make a dictionary for fitted recoil mnvh1ds to store later
        data_mnvh_dict = {}
        prefit_mctot_dict = {}
        prefit_mctot_mnvh_dict = {}
        prefit_sig_mnvh_dict = {}
        prefit_bkg_mnvh_dict = {}

        prefit_mnvh1d_dict = {}
        fit_mnvh1d_dict = {}


        fit_mctot_mnvh_dict = {}
        fit_sig_mnvh_dict = {}
        fit_bkg_mnvh_dict = {}



        fit_chi2_dict = {}
        prefit_chi2_dict = {}
        postfit_chi2_dict = {}
        # Quick dict to store MnvH2Ds
        # MnvH2D_dict = {'data': data_MnvH2D, 'mctot': mctot_MnvH2D, 'mctot_tuned':mctot_tuned_MnvH2D, 'qelike': qelike_MnvH2D, 'qelike_tuned': qelike_tuned_MnvH2D, 'qelikenot': qelikenot_MnvH2D, 'qelikenot_tuned':qelikenot_tuned_MnvH2D}
        MnvH2D_dict = {'data': data_MnvH2D, 'mctot': mctot_MnvH2D, 'qelike': qelike_MnvH2D, 'qelikenot': qelikenot_MnvH2D}

        universe_names = qelike_MnvH2D.GetVertErrorBandNames()
        # Add in cv to universe
        universe_names_list = ["cv"]
        for name in universe_names:
            universe_names_list.append(name)

        sig_fitfrac_mnvh1d = dummy_q2_mnvh1d.Clone("h___"+sample+"___qelike___Q2QE___fraction")
        # sig_tuned_fitfrac_mnvh1d = dummy_q2_mnvh1d.Clone("h___QELike___qelike___Q2QE___fraction_tuned")

        sig_scale_mnvh1d = dummy_q2_mnvh1d.Clone("h___"+sample+"___qelike___Q2QE___scale")
        # sig_tuned_scale_mnvh1d = dummy_q2_mnvh1d.Clone("h___QELike___qelike___Q2QE___scale_tuned")

        bkg_fitfrac_mnvh1d = dummy_q2_mnvh1d.Clone("h___"+sample+"___qelikenot___Q2QE___fraction")
        # bkg_tuned_fitfrac_mnvh1d = dummy_q2_mnvh1d.Clone("h___QELike___qelikenot___Q2QE___fraction_tuned")

        bkg_scale_mnvh1d = dummy_q2_mnvh1d.Clone("h___"+sample+"___qelikenot___Q2QE___scale")
        # bkg_tuned_scale_mnvh1d = dummy_q2_mnvh1d.Clone("h___QELike___qelikenot___Q2QE___scale_tuned")
#
        # Loop over universe names
        for uni_name in universe_names_list:
            print("  Starting universe ", uni_name, "...")
            sig_fitfrac_hist_list = []

            sig_scale_hist_list = []

            bkg_fitfrac_hist_list = []

            bkg_scale_hist_list = []

            # To store the fitted recoil hists in
            fit_uni_hist_dict = {}


            fit_sig_uni_dict = {}
            fit_bkg_uni_dict = {}
            if uni_name == 'cv':
                n_universes = 1
            else:
                # Most have 2 sys hists and a CV (+/- 1 sigma or something similar)
                n_universes = mctot_MnvH2D.GetVertErrorBand(uni_name).GetNHists()
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
                        tmp_th2d = MnvH2D_dict[key].GetCVHistoWithStatError().Clone()
                    else:
                        tmp_th2d = MnvH2D_dict[key].GetVertErrorBand(uni_name).GetHist(uni).Clone()
                    tmp_th2d_dict[key] = tmp_th2d

                tmp_fitbin_th1d_dict = {}
                # Loop over fitbins for that universe
                for fitbin in range(1, n_xbins + 1):
                    fit_sig_uni_dict[fitbin] = []
                    fit_bkg_uni_dict[fitbin] = []
                    print("      Working on fitbin number ", fitbin)
                    fitbin_name = "Q2bin" + str("%02d" % (fitbin))
                    prefit_th1d_dict = {}

                    if uni_name == 'cv':
                        prefit_mnvh1d_dict[fitbin] = {}
                        fit_mnvh1d_dict[fitbin] = {}
                    # Make MnvH1D hists by projecting on fit bin
                    tmp_prefit_dict = {}
                    for key in tmp_th2d_dict.keys():
                        proj_name = fitbin_name + '_' + key
                        tmp_fitbin_th1d = tmp_th2d_dict[key].ProjectionY(proj_name, fitbin, fitbin, "e")
                        # for i in range(1,6):
                        #     tmp_fitbin_th1d.SetBinContent(i,0)
                        prefit_th1d_dict[key] = tmp_fitbin_th1d
                        print("     Number of entries in ", key,": ", tmp_fitbin_th1d.GetEntries())
                        # Need to make a Mnvh1d of each fitbin before the fit.
                        # Using 'cv' universe so this only happens once (rather
                        # than doing this step needlessly in every universe)

                        if uni_name == 'cv':
                        # if uni_name == 'cv' and key in ['mctot','data','qelike', 'qelikenot']:
                            print(">>>>>>>>> key: ",key)
                            if 'tuned' in key:
                                tmpname = key.replace('_tuned','')
                                prefit_mnvh1d_name = "h___"+sample+"___" + tmpname + "___"+recoil_type+"_" + fitbin_name + "___prefit_tuned"
                            else:
                                prefit_mnvh1d_name = "h___"+sample+"___" + key + "___"+recoil_type+"_" + fitbin_name + "___prefit"

                            print(prefit_mnvh1d_name)
                            prefit_recoil_mnvh = MnvH2D_dict[key].ProjectionY(prefit_mnvh1d_name, fitbin, fitbin, "e").Clone()
                            # for i in range(1,6):
                            #     prefit_recoil_mnvh.SetBinContent(i,0)

                            prefit_mnvh1d_dict[fitbin][key] = prefit_recoil_mnvh

                    # Scale prefit MnvH1D's
                    if uni_name=='cv':
                        prefit_mnvh1d_dict[fitbin]['mctot'],prefit_mnvh1d_dict[fitbin]['qelike'],prefit_mnvh1d_dict[fitbin]['qelikenot'] = ScaleMC(prefit_mnvh1d_dict[fitbin]['data'],prefit_mnvh1d_dict[fitbin]['mctot'],prefit_mnvh1d_dict[fitbin]['qelike'],prefit_mnvh1d_dict[fitbin]['qelikenot'])


                    data_hist = prefit_th1d_dict['data']
                    prefit_mctot_hist = prefit_th1d_dict['mctot']
                    prefit_qelike_hist = prefit_th1d_dict['qelike']
                    prefit_qelikenot_hist = prefit_th1d_dict['qelikenot']

                    # Scale MC hists to area normalize them to Data (so # counts is the same)
                    prefit_mctot_hist, prefit_qelike_hist, prefit_qelikenot_hist = ScaleMC(data_hist,prefit_mctot_hist,prefit_qelike_hist,prefit_qelikenot_hist)

                    # Calculate Chi2 between data & MC before the fit.
                    prefit_chi2 = data_hist.Chi2Test(prefit_mctot_hist, "UW,CHI2")
                    prefit_ndf = data_hist.GetNbinsX() - 1


                    # Calculate & store pre-fit fractions of MC samples.
                    prefit_sig_frac, prefit_bkg_frac = GetSigBkgFrac(prefit_mctot_hist, prefit_qelike_hist, prefit_qelikenot_hist)

                    print("      Running Fraction Fitter... ")
                    # Run the TFractionFitter and get values out
                    fit = RunFractionFitter(prefit_mctot_hist, prefit_qelike_hist, prefit_qelikenot_hist, data_hist)
                    # Calculate scale factors for sig and bkg and errors
                    fit_sig_frac, fit_sig_err, sig_scale, sig_scale_err = GetOutVals(fit, prefit_sig_frac, 'qelike')
                    fit_bkg_frac, fit_bkg_err, bkg_scale, bkg_scale_err = GetOutVals(fit, prefit_bkg_frac, 'qelikenot')
                    # This gives you the chi2 from the fit.
                    fit_chi2 = fit.GetChisquare()
                    # Our fit parameters are totally correllated, so we add back 1.
                    fit_ndf = fit.GetNDF() + 1

                    fit_qelike_hist = prefit_qelike_hist.Clone()
                    fit_qelike_hist.Scale(sig_scale)
                    fit_qelikenot_hist = prefit_qelikenot_hist.Clone()
                    fit_qelikenot_hist.Scale(bkg_scale)

                    fit_mctot_hist = fit_qelike_hist.Clone("fit_mctot")
                    fit_mctot_hist.Add(fit_qelikenot_hist)

                    postfit_chi2 = data_hist.Chi2Test(fit_mctot_hist,"UW,CHI2")
                    postfit_ndf = prefit_ndf


                    if uni_name == 'cv':
                        fit_chi2_dict[fitbin] = {"chi2":fit_chi2,"ndf":fit_ndf}
                        prefit_chi2_dict[fitbin] = {"chi2":prefit_chi2,"ndf":prefit_ndf}
                        postfit_chi2_dict[fitbin] = {"chi2":postfit_chi2,"ndf":postfit_ndf}

                        print("      Filling CVs...")
                        sig_fitfrac_mnvh1d.SetBinContent(fitbin, fit_sig_frac)
                        sig_fitfrac_mnvh1d.SetBinError(fitbin, fit_sig_err)

                        sig_scale_mnvh1d.SetBinContent(fitbin, sig_scale)
                        sig_scale_mnvh1d.SetBinError(fitbin, sig_scale_err)

                        bkg_fitfrac_mnvh1d.SetBinContent(fitbin, fit_bkg_frac)
                        bkg_fitfrac_mnvh1d.SetBinError(fitbin, fit_bkg_err)

                        bkg_scale_mnvh1d.SetBinContent(fitbin, bkg_scale)
                        bkg_scale_mnvh1d.SetBinError(fitbin, bkg_scale_err)


                        fit_sig_mnvh1d = MnvH1D(fit_qelike_hist)
                        fit_sig_mnvh1d.SetName("h___"+sample+"___qelike___"+recoil_type+"_" + fitbin_name + "___fit")
                        fit_mnvh1d_dict[fitbin]['qelike'] = fit_sig_mnvh1d

                        fit_bkg_mnvh1d = MnvH1D(fit_qelikenot_hist)
                        fit_bkg_mnvh1d.SetName("h___"+sample+"___qelikenot___"+recoil_type+"_" + fitbin_name + "___fit")
                        fit_mnvh1d_dict[fitbin]['qelikenot'] = fit_bkg_mnvh1d

                        fit_mctot_mnvh1d = MnvH1D(fit_mctot_hist)
                        fit_mctot_mnvh1d.SetName("h___"+sample+"___mctot___"+recoil_type+"_" + fitbin_name + "___fit")
                        fit_mnvh1d_dict[fitbin]['mctot'] = fit_mctot_mnvh1d

                    else:
                        print("      Filling hists for error band ",uni_name, "...")
                        sig_fitfrac_hist.SetBinContent(fitbin, fit_sig_frac)
                        sig_fitfrac_hist.SetBinError(fitbin, fit_sig_err)

                        sig_scale_hist.SetBinContent(fitbin, sig_scale)
                        sig_scale_hist.SetBinError(fitbin, sig_scale_err)

                        bkg_fitfrac_hist.SetBinContent(fitbin, fit_bkg_frac)
                        bkg_fitfrac_hist.SetBinError(fitbin, fit_bkg_err)

                        bkg_scale_hist.SetBinContent(fitbin, bkg_scale)
                        bkg_scale_hist.SetBinError(fitbin, bkg_scale_err)
                        fit_sig_uni_dict[fitbin].append(fit_qelike_hist)
                        fit_bkg_uni_dict[fitbin].append(fit_qelikenot_hist)

                        # Kind of hacky. When you've looped over every universe,
                        # add the vert error band for the recoil plots.
                        if uni == n_universes - 1:
                            fit_mnvh1d_dict[fitbin]['qelike'].AddVertErrorBand(uni_name, fit_sig_uni_dict[fitbin])
                            fit_mnvh1d_dict[fitbin]['qelikenot'].AddVertErrorBand(uni_name, fit_bkg_uni_dict[fitbin])

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
                sig_fitfrac_mnvh1d.AddVertErrorBand(uni_name, sig_fitfrac_hist_list)
                sig_scale_mnvh1d.AddVertErrorBand(uni_name, sig_scale_hist_list)
                bkg_fitfrac_mnvh1d.AddVertErrorBand(uni_name, bkg_fitfrac_hist_list)
                bkg_scale_mnvh1d.AddVertErrorBand(uni_name, bkg_scale_hist_list)

        print("Done filling hists... ")
        print("Syncing bands... ")
        SyncBands(sig_fitfrac_mnvh1d)
        SyncBands(sig_scale_mnvh1d)
        SyncBands(bkg_fitfrac_mnvh1d)
        SyncBands(bkg_scale_mnvh1d)
        for fitbin in prefit_mnvh1d_dict:
            for key in prefit_mnvh1d_dict[fitbin]:
                SyncBands(prefit_mnvh1d_dict[fitbin][key])
            for key in fit_mnvh1d_dict[fitbin]:
                SyncBands(fit_mnvh1d_dict[fitbin][key])
        histfile_tail = "_Hists.root"
        histfile_name = outfilebase.replace(".root", histfile_tail)
        print("Writing input & fitted hists to file: ", histfile_name)

        outhistfile = ROOT.TFile(histfile_name, "RECREATE")
        for histkey in MnvH2D_dict:
            outhistfile.cd()
            MnvH2D_dict[histkey].Write()
        for fitbin in range(1, n_xbins + 1):
            outhistfile.cd()
            for key in prefit_mnvh1d_dict[fitbin]:
                outhistfile.cd()
                prefit_mnvh1d_dict[fitbin][key].Write()
            for key in  fit_mnvh1d_dict[fitbin]:
                outhistfile.cd()
                fit_mnvh1d_dict[fitbin][key].Write()
            outhistfile.cd()
        outhistfile.Close()

        # Write out each hist to a root file.
        outvalhistfile_tail = "_OutVals_100MeVFit.root"
        outvalhistfile = outfilebase.replace(".root", outvalhistfile_tail)
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
        outvalfile.cd()
        outvalfile.Close()

        plotfilename = outfilebase.replace(".root", "_Hists_100MeVFit")
        i_fitbin = 0

        binning = GetFitBinning(infile)
        # Initialize a pdf canvas for making plots
        canvas = ROOT.TCanvas(str(str(plotfilename) + ".pdf"))

        canvas.cd()
        canvas.SetLeftMargin(0.1)
        canvas.SetRightMargin(0.07)
        canvas.SetBottomMargin(0.11)
        canvas.SetTopMargin(0.1)

        canvas.Print(str(plotfilename+".pdf["), "pdf")

        for fitbin in range(1, n_xbins + 1):

            print("Starting fitbin ", fitbin)
            fitbin_loedge = binning[i_fitbin]
            fitbin_upedge = binning[i_fitbin + 1]
            # Base title for plotting later
            title = "Recoil: " + str(fitbin_loedge) +" GeV^{2} < Q^{2}_{QE} < " + str(fitbin_upedge) + " GeV^{2}"

            data_hist = prefit_mnvh1d_dict[fitbin]['data'].Clone().GetCVHistoWithStatError()
            prefit_mctot_hist = prefit_mnvh1d_dict[fitbin]['mctot'].Clone().GetCVHistoWithStatError()
            prefit_sig_hist = prefit_mnvh1d_dict[fitbin]['qelike'].Clone().GetCVHistoWithStatError()
            prefit_bkg_hist = prefit_mnvh1d_dict[fitbin]['qelikenot'].Clone().GetCVHistoWithStatError()
            fit_mctot_hist = fit_mnvh1d_dict[fitbin]['mctot'].Clone()
            fit_sig_hist = fit_mnvh1d_dict[fitbin]['qelike'].Clone().GetCVHistoWithStatError()
            fit_bkg_hist = fit_mnvh1d_dict[fitbin]['qelikenot'].Clone().GetCVHistoWithStatError()


            fit_chi2 = fit_chi2_dict[fitbin]["chi2"]
            fit_ndf = fit_chi2_dict[fitbin]["ndf"]
            prefit_chi2 = prefit_chi2_dict[fitbin]["chi2"]
            prefit_ndf = prefit_chi2_dict[fitbin]["ndf"]
            postfit_chi2 = postfit_chi2_dict[fitbin]["chi2"]
            postfit_ndf = postfit_chi2_dict[fitbin]["ndf"]

            # Plot Data & pre-fit MC
            logx=False
            logy=True
            MakeDataMCPlot(canvas, title+", prefit", data_hist, prefit_sig_hist,prefit_bkg_hist, prefit_chi2, prefit_ndf, logx, logy)
            # Plot Data & post-fit MC
            MakeDataMCPlot(canvas, title+", postfit", data_hist, fit_sig_hist,fit_bkg_hist, postfit_chi2, postfit_ndf, logx, logy, fit_chi2)
            ROOT.gPad.SetLogx(0)
            ROOT.gPad.SetLogy(0)

            # Plot Data/MC ratio for both pre- and post-fit MC
            MakeFitRatioPlot(canvas, title+" data/MC ratio", data_hist, prefit_mctot_hist, fit_mctot_hist, logx)
            # canvas.Print(str(plotfilename +"_"+fitbin+".pdf]"), "pdf")
            i_fitbin+=1
        canvas.Print(str(plotfilename +".pdf]"), "pdf")




if __name__ == "__main__":
    main()
