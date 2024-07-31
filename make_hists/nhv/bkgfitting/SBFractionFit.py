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
combinefirstbins = False
category_list = [
    "data", 
    "qelike", 
    "chargedpion", 
    "neutralpion", 
    # "multipion",
    "other"
]
mc_category_list = [
    "qelike", 
    "chargedpion", 
    "neutralpion", 
    # "multipion", 
    "other"
]
fixed_cats_list = [
    "other"#, 
    # "multipion"
]
scale_var = "Q2QE"
fit_var = "recoil"
scaletype = "area"

variable_list = ["FitQ2QE_recoil"]
# names associated with each "sample" e.g. QElike, QElikeALL
sample_list = [
    "QElike", 
    # "LoPionThetaSideband", 
    # "HiPionThetaSideband", 
    "TrackSideband",
    "BlobSideband"#, 
    # "MultipBlobSideband"
    # "TrackBlobSideband"
]

outsample_name = ""
for sample in sample_list:
    outsample_name+=sample+"_"

# DRAW = True
# CONFINT = True

# Do fit on tuned hists or not
useTuned = 0
# rebin = 2

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
    hist_dict = {}
    # data_hist_dict = {}
    # mc_hist_dict = {}
    for key in keys:
        hist_name = key.GetName()
        # print(hist_name)
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
        if hist_type!='reconstructed_simulfit':
            continue
        print("found hist ",hist_name)
        hist_dict[hist_name]=rfile.Get(hist_name).Clone()
    return hist_dict
    # return data_hist_dict, mc_hist_dict

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

def GetDummyHistCV(rfile, variable_name=scale_var):
    # Make a dummy 1D hist to get binning. Just grabs first 1D Q2QE plot
    histkeys_list = rfile.GetListOfKeys()
    for histkey in histkeys_list:
        hist_name = histkey.GetName()
        # TODO: This is hardcoded, should change it
        if hist_name.find("___"+variable_name+"___") == -1:
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

def MakeLongHist2D(i_hist_list):
    first = True
    out_hist = i_hist_list[0].Clone()
    for hist in i_hist_list:
        if first:
            first = False
            continue
        tmp_hist = hist.Clone()
        out_hist.Add(tmp_hist,1.0)
    return out_hist



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

def GetMCFracList(i_hist_dict):
    # Gets fraction of 1D MC hists relative to total mc
    mctot = i_hist_dict["mctot"].Clone()
    mctot_int = mctot.Integral(min_bin, mctot.GetNbinsX())
    mc_frac_list = []

    for cat in mc_category_list:
        mc_hist_int = i_hist_dict[cat].Integral(min_bin, mctot.GetNbinsX())
        mc_frac = mc_hist_int / mctot_int
        mc_frac_list.append(mc_frac)
    return mc_frac_list


# def RunFractionFitter(i_mctot_hist, i_qelike_hist, i_qelikenot_hist, i_data_hist):
def RunFractionFitter(i_hist_dict):
    data_hist = i_hist_dict["data"].Clone()
    mc_hist_list = []
    for cat in mc_category_list:
        mc_hist_list.append(i_hist_dict[cat].Clone())

    # Get min and max bin for fitting (underflow is 0, overflow is nbins+1)
    # min_bin = 1
    max_bin = i_hist_dict["mctot"].GetNbinsX()

    print(">>>>>>>>>max_bin ", max_bin)

    # Calculate & store pre-fit fractions of MC samples.
    mc_frac_list = GetMCFracList(i_hist_dict)

    # Make a list of the MC hists for the fitter...
    # mc_list = ROOT.TObjArray(2)
    # mc_list.append(qelike_hist)
    # mc_list.append(qelikenot_hist)
    mc_hist_array = ROOT.TObjArray(len(mc_frac_list))
    for mc_hist in mc_hist_list:
        mc_hist_array.append(mc_hist)

    # Set up fitter in verbose mode
    fit = ROOT.TFractionFitter(data_hist, mc_hist_array, "V") 
    virtual_fitter = fit.GetFitter()

    # Configure the fit for each mc hist. Names from mc_category_list should share index with hist and histfrac lists
    for i in range(len(mc_hist_list)):
            # virtual_fitter.Config().ParSettings(i).Set(mc_category_list[i], mc_frac_list[i], 0.001, 0.0, 0.05) # Switched step size to be the bin width of 25 recoil bins
        #     # Constrain the fit to between [0,1], since they are fracs and area-normed
        #     fit.Constrain(i, 0.0, 0.05)   

        # Set(<name>,<fraction>,<stepsize>,<lowerbound>,<upperbound>)
        virtual_fitter.Config().ParSettings(i).Set(mc_category_list[i], mc_frac_list[i], mc_frac_list[i]*0.01)#, 0.0, 1.0) # Switched step size to be the bin width of 25 recoil bins
        # Constrain the fit to between [0,1], since they are fracs and area-normed
        # if mc_frac_list[i] < 0.01:
        #     virtual_fitter.Config().ParSettings(i).Fix()
        if mc_category_list[i] in fixed_cats_list:
            virtual_fitter.Config().ParSettings(i).Fix()
        else:
            # fit.Constrain(i, mc_frac_list[i]*0.05, mc_frac_list[i]*5.)
            fit.Constrain(i, 0., 1.)

    # Set the bin range you want to fit on
    fit.SetRangeX(min_bin, max_bin)
    # Do the fit
    status = fit.Fit()

    # Clean up
    # del mctot_hist, qelike_hist, qelikenot_hist, data_hist # TODO: reimpliment with lists. Necessary?

    if status != 0:
        print(">>>>>>>>>>>>>>>>>>>> WARNING: Fit did not converge...")
        sys.exit(1)
        return fit
    if status == 0:
        print(">>>>>>>>>>>>>>>>>>>> Fit converged.")
        return fit


def GetOutVals(fit, prefit_frac_list):
    fit_frac_list = []
    fit_frac_err_list = []
    scale_list = []
    scale_err_list = []
    for i in range(len(mc_category_list)):
        fit_frac = ctypes.c_double(0)
        fit_err = ctypes.c_double(0)
        fit.GetResult(i, fit_frac, fit_err)

        fit_frac = fit_frac.value
        fit_err = fit_err.value
        scale = fit_frac / prefit_frac_list[i]
        scale_err = fit_err / prefit_frac_list[i]

        fit_frac_list.append(fit_frac)
        fit_frac_err_list.append(fit_err)
        scale_list.append(scale)
        scale_err_list.append(scale_err)
        print("==========",mc_category_list[i]," fit_frac: ", fit_frac, "\t fit_err: ", fit_err, "\t scale: ", scale, "\t scale_err: ", scale_err)

    return fit_frac_list, fit_frac_err_list, scale_list, scale_err_list


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
    dummy_scalevar_mnvh1d, dummy_scalevar_th1d = GetDummyHistCV(infile, scale_var)

    dummy_fitvar_mnvh1d, dummy_fitvar_th1d = GetDummyHistCV(infile, recoil_type)

    n_xbins = dummy_scalevar_mnvh1d.GetNbinsX()

    # raw_data_mnvh2d_dict, raw_mc_mnvh2d_dict = GetDataMCHistDict(infile)
    raw_hist_dict = GetDataMCHistDict(infile)
    category_dict = {}
    for category in category_list:
        category_dict[category] = {"hist":None, "list":[]}
        for hist_name in raw_hist_dict.keys():
            splitnames_list = hist_name.split('___')
            hist_sample = splitnames_list[1]
            hist_category = splitnames_list[2]
            if hist_category!=category:
                continue
            for sample in sample_list:
                if hist_sample!=sample:
                    continue
                else:
                    category_dict[category]["list"].append(raw_hist_dict[hist_name].Clone())
        category_dict[category]["hist"] = MakeLongHist2D(category_dict[category]["list"])

    # Make an mctotal, kind of have to hack this
    category_dict["mctot"] = {"hist":None, "list":[]}
    # category_dict["mctot"]["hist"] = category_dict["qelike"]["hist"].Clone()
    for hist in category_dict["qelike"]["list"]:
        category_dict["mctot"]["list"].append(hist.Clone())
    for category in category_list:
        if category in ["data","qelike","mctot"]:
            continue
        # category_dict["mctot"]["hist"] = category_dict["mctot"]["hist"].Add(category_dict[category]["hist"])
        for i in range(len(category_dict[category]["list"])):
            category_dict["mctot"]["list"][i].Add(category_dict[category]["list"][i],1.0)
    category_dict["mctot"]["hist"] = MakeLongHist2D(category_dict["mctot"]["list"])

    # Make a dict for the scale factor hists (hacky I know)
    scalefrac_mnvh1d_dict = {}
    for cat in mc_category_list:
        scalename = "h___QElike___"+cat+"___"+scale_var+"___scale"
        fracname = "h___QElike___"+cat+"___"+scale_var+"___fraction"
        scalefrac_mnvh1d_dict[cat] = {"scale": dummy_scalevar_mnvh1d.Clone(scalename), "fraction": dummy_scalevar_mnvh1d.Clone(fracname)}


    # del raw_hist_dict # TODO delete raw hist dict?
    prefit_mnvh1d_dict = {}
    fit_mnvh1d_dict = {}
    fit_chi2_dict = {}
    prefit_chi2_dict = {}
    postfit_chi2_dict = {}
    universe_names_list = ['cv']
    for univ_name in category_dict["qelike"]["hist"].GetVertErrorBandNames():
        universe_names_list.append(univ_name)

    for univ_name in universe_names_list:
        print("  Starting universe ", univ_name, "...")

        scale_univhist_dict = {}
        frac_univhist_dict = {}
        for cat in mc_category_list:
            scale_univhist_dict[cat] = []
            frac_univhist_dict[cat] = []

        fitbin_cat_univ_hist_dict = {}
        if univ_name == "cv":
            n_universes = 1
        else:
            n_universes = category_dict["qelike"]["hist"].GetVertErrorBand(univ_name).GetNHists()

        for univ in range(0,n_universes):
            print("  Starting universe ", univ, "...")
            tmp_th2d_dict = {}
            
            for key in category_dict:
                if univ_name == "cv" or key == "data":
                    tmp_th2d = category_dict[key]["hist"].GetCVHistoWithStatError().Clone()
                else:
                    tmp_th2d = category_dict[key]["hist"].GetVertErrorBand(univ_name).GetHist(univ).Clone()                        
                if key in mc_category_list:
                    scale_univhist_dict[key].append(dummy_scalevar_th1d.Clone())
                    frac_univhist_dict[key].append(dummy_scalevar_th1d.Clone())
                tmp_th2d_dict[key] = tmp_th2d
            
            print("***********************************************",frac_univhist_dict.keys())
            for key in frac_univhist_dict.keys():
                print(len(frac_univhist_dict[key]))

            for fitbin in range(1, n_xbins + 1):
                print("        Working on fitbin number ", fitbin)
                fitbin_name = "fitbin" + str("%02d" % fitbin)
                fitbin_cat_univ_hist_dict[fitbin] = {}
                for cat in mc_category_list:
                    fitbin_cat_univ_hist_dict[fitbin][cat] = []
                prefit_th1d_dict = {}

                if univ_name == 'cv': 
                    prefit_mnvh1d_dict[fitbin] = {}
                    fit_mnvh1d_dict[fitbin] = {}

                for key in tmp_th2d_dict.keys():
                    proj_name = fitbin_name + '_' + key
                    tmp_fitbin_th1d = ROOT.TH1D()
                    if fitbin == 1 and combinefirstbins:
                        tmp_fitbin_th1d = tmp_th2d_dict[key].ProjectionY(proj_name, fitbin, fitbin+1, "e")
                    elif fitbin == 2 and combinefirstbins:
                        tmp_fitbin_th1d = tmp_th2d_dict[key].ProjectionY(proj_name, fitbin-1, fitbin, "e")
                    else:
                        tmp_fitbin_th1d = tmp_th2d_dict[key].ProjectionY(proj_name, fitbin, fitbin, "e")

                    tmp_fitbin_th1d.Rebin(3)

                    # if rebin>1.:
                    #     tmp_fitbin_th1d.Rebin(rebin)
                    prefit_th1d_dict[key] = tmp_fitbin_th1d
                    print("     Number of entries in ", key,": ", tmp_fitbin_th1d.GetEntries())
                    # Need to make a MnvH1D of each fitbin before the fit. Using 'cv' universe so this only happens once (rather than doing this step needlessly in every universe)
                    if univ_name == 'cv':
                        print(">>>>>>>>> key: ",key)
                        if 'tuned' in key:
                            tmpname = key.replace('_tuned','')
                            prefit_mnvh1d_name = "h___"+outsample_name+"__" + tmpname + "___" + recoil_type + "_" + fitbin_name + "___prefit_tuned"
                        else:
                            prefit_mnvh1d_name = "h___"+outsample_name+"__" + key + "___" + recoil_type + "_" + fitbin_name + "___prefit"

                        print(prefit_mnvh1d_name)
                        prefit_fitvar_mnvh = category_dict[key]["hist"].ProjectionY(prefit_mnvh1d_name, fitbin, fitbin, "e").Clone()
                        # if rebin>1.:
                        #     prefit_fitvar_mnvh.Rebin(rebin)
                        prefit_mnvh1d_dict[fitbin][key] = prefit_fitvar_mnvh #TODO need to scale these
                
                # mc_hist_list = []
                # for cat in mc_category_list:
                #     mc_hist_list.append(prefit_th1d_dict[cat])
                
                if scaletype!="POT":
                    print("Doing area scaling...")
                    max_xbin = prefit_th1d_dict["data"].GetNbinsX()
                    area_scale = (prefit_th1d_dict["data"].Integral(min_bin, max_xbin)) / (prefit_th1d_dict["mctot"].Integral(min_bin, max_xbin))
                    prefit_th1d_dict["mctot"].Scale(area_scale)
                    for cat in mc_category_list:
                        prefit_th1d_dict[cat].Scale(area_scale)

                    # TODO set up scaling, configable (if necessary) to do POT or area norming (which is why you need to do it this late)
                
                # Moved chi2 stuff to "if 'cv'" part at end of this loop
                # prefit_chi2 = prefit_th1d_dict["data"].Chi2Test(prefit_th1d_dict["mctot"], "UW,CHI2")
                # prefit_ndf = prefit_th1d_dict["data"].GetNbinsX() - 1 # TODO: this might be different for so many hists
                mc_frac_list = GetMCFracList(prefit_th1d_dict) #["mctot"],mc_hist_list)

                print("        Running Fraction Fitter... fitbin ", fitbin)
                fit = RunFractionFitter(prefit_th1d_dict)
                fit_frac_list, fit_frac_err_list, scale_list, scale_err_list = GetOutVals(fit,mc_frac_list)

                # Moved chi2 stuff to "if 'cv'" part at end of this loop
                # fit_chi2 = fit.GetChisquare()
                # fit_ndf = fit.GetNDF()

                # Make the scaled "fitted" hists, and new mctot
                fit_th1d_dict = {}
                for i in range(len(mc_category_list)):
                    tmp_fit_th1d = prefit_th1d_dict[mc_category_list[i]].Clone()
                    tmp_fit_th1d.Scale(scale_list[i])
                    fit_th1d_dict[mc_category_list[i]] = tmp_fit_th1d
                dummy_mctot_hist = fit_th1d_dict[mc_category_list[0]].Clone()
                for cat in mc_category_list:
                    if cat == mc_category_list[0]:
                        continue
                    else:
                        dummy_mctot_hist.Add(tmp_fit_th1d,1.0)
                fit_th1d_dict["mctot"] = dummy_mctot_hist
                # Moved chi2 stuff to "if 'cv'" part at end of this loop
                # postfit_chi2 = prefit_th1d_dict["data"].Chi2Test(fit_th1d_dict["mctot"],"UW,CHI2")

                if univ_name == "cv":
                    print("        Calculating chi2 for the CV and storing")
                    # chi2 of hists before the fit
                    prefit_chi2 = prefit_th1d_dict["data"].Chi2Test(prefit_th1d_dict["mctot"], "UW,CHI2")
                    prefit_ndf = prefit_th1d_dict["data"].GetNbinsX() - 1 # TODO: this might be different now
                    # chi2 output from the fitter, the chi2 that it minimizes
                    fit_chi2 = fit.GetChisquare()
                    fit_ndf = fit.GetNDF()
                    # chi2 of hists after the fit (same ndf as prefit)
                    postfit_chi2 = prefit_th1d_dict["data"].Chi2Test(fit_th1d_dict["mctot"],"UW,CHI2")

                    # store the chi2
                    fit_chi2_dict[fitbin] = {"chi2":fit_chi2,"ndf":fit_ndf}
                    prefit_chi2_dict[fitbin] = {"chi2":prefit_chi2,"ndf":prefit_ndf}
                    postfit_chi2_dict[fitbin] = {"chi2":postfit_chi2,"ndf":prefit_ndf}
                    
                    print("      Filling CVs...")
                    for i in range(len(mc_category_list)):
                        # store scale factors and fractions into their own hists for output
                        scalefrac_mnvh1d_dict[mc_category_list[i]]["fraction"].SetBinContent(fitbin,fit_frac_list[i])
                        scalefrac_mnvh1d_dict[mc_category_list[i]]["fraction"].SetBinError(fitbin,fit_frac_err_list[i])
                        scalefrac_mnvh1d_dict[mc_category_list[i]]["scale"].SetBinContent(fitbin,scale_list[i])
                        scalefrac_mnvh1d_dict[mc_category_list[i]]["scale"].SetBinError(fitbin,scale_err_list[i])
                        print("==========",mc_category_list[i]," fit_frac: ", fit_frac_list[i], "\t fit_err: ", fit_frac_err_list[i], "\t scale: ", scale_list[i], "\t scale_err: ", scale_err_list[i])

                        # Start building mnvh1ds of each hist scaled from fit
                        tmp_fit_mnvh1d = MnvH1D(fit_th1d_dict[mc_category_list[i]])
                        tmp_fit_mnvh1d.SetName("h___"+outsample_name+"__"+mc_category_list[i]+"___"+fit_var+"_"+fitbin_name+"___fit")
                        fit_mnvh1d_dict[fitbin][mc_category_list[i]] = tmp_fit_mnvh1d
                    # Do the same for the mctot hist
                    tmp_fit_mctot_mnvh1d = MnvH1D(fit_th1d_dict["mctot"])
                    tmp_fit_mctot_mnvh1d.SetName("h___"+outsample_name+"__mctot___"+fit_var+"_"+fitbin_name+"___fit")
                    fit_mnvh1d_dict[fitbin]["mctot"] = tmp_fit_mctot_mnvh1d
                else:
                    print("        Filling hists for error band ", univ_name, "...")  
                    for i in range(len(mc_category_list)):
                        cat = mc_category_list[i]
                        print("                Inside cat loop for ", cat)
                        # Set the bin content for this universes scale/frac
                        frac_univhist_dict[cat][univ].SetBinContent(fitbin,fit_frac_list[i])
                        # frac_univhist_dict[cat][univ].SetBinError(fitbin,fit_frac_err_list[i])
                        print (" after set bin contents for frac")                        
                        scale_univhist_dict[cat][univ].SetBinContent(fitbin,scale_list[i])
                        # scale_univhist_dict[cat][univ].SetBinError(fitbin,scale_err_list[i])
                        print (" after set bin contents for scale")
                        # Make a list of histograms for this universe so we can add all as one error band
                        fitbin_cat_univ_hist_dict[fitbin][cat].append(fit_th1d_dict[cat])
                        # kind of hacky but oh well
                        if univ == n_universes - 1:
                            fit_mnvh1d_dict[fitbin][cat].AddVertErrorBand(univ_name, fitbin_cat_univ_hist_dict[fitbin][cat])               
                # end if "cv"/else
            # end fitbin loop
        # end n_universes loop
        if univ_name == "cv":
            print("    Done filling CVs...")
        else:
            print("    Adding vert error band ", univ_name, " to scale/frac MnvH1Ds...")
            for cat in mc_category_list:
                scalefrac_mnvh1d_dict[cat]["fraction"].AddVertErrorBand(univ_name,frac_univhist_dict[cat])
                scalefrac_mnvh1d_dict[cat]["scale"].AddVertErrorBand(univ_name,scale_univhist_dict[cat])
    # end univ_name loop
    print("Done filling hists... ")
    print("Syncing bands... ")
    for cat in scalefrac_mnvh1d_dict.keys():
        SyncBands(scalefrac_mnvh1d_dict[cat]["fraction"])
        SyncBands(scalefrac_mnvh1d_dict[cat]["scale"])
    for fitbin in fit_mnvh1d_dict.keys():
        for cat in fit_mnvh1d_dict[fitbin]:
            SyncBands(fit_mnvh1d_dict[fitbin][cat])
        for cat in prefit_mnvh1d_dict[fitbin]:
            SyncBands(prefit_mnvh1d_dict[fitbin][cat])

    histfile_tail = "_FractionFitHists.root"
    histfile_name = outfilebase.replace(".root", histfile_tail)
    print("Writing input & fitted hists to file: ", histfile_name)

    outhistfile = ROOT.TFile(histfile_name, "RECREATE")
    # for category in category_dict:
    #     for histkey in category_dict[category]:
    #         outhistfile.cd()
    #         category_dict[category][histkey].Write()
    for fitbin in fit_mnvh1d_dict.keys():
        for cat in fit_mnvh1d_dict[fitbin]:
            outhistfile.cd()
            fit_mnvh1d_dict[fitbin][cat].Write()
            outhistfile.cd()
            prefit_mnvh1d_dict[fitbin][cat].Write()
    outhistfile.Close()

    outvalfile_tail = "_FractionFitOutVals.root"
    outvalfile_name = outfilebase.replace(".root", outvalfile_tail)
    print("Writing scale and fraction hists to file: ", outvalfile_name)
    outvalfile = ROOT.TFile(outvalfile_name, "RECREATE")
    outvalfile.cd()
    for category in scalefrac_mnvh1d_dict.keys():
        outvalfile.cd()
        scalefrac_mnvh1d_dict[category]["fraction"].Write()
        outvalfile.cd()
        scalefrac_mnvh1d_dict[category]["scale"].Write()
    outvalfile.cd()
    outvalfile.Close()

    print("Done writing hists to file!")
    print(histfile_name)
    print(outvalfile_name)
    print("Success")



if __name__ == "__main__":
    main()
