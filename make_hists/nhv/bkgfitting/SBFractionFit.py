from unicodedata import category
import ROOT
# from PlotUtils import MnvH1D, MnvH2D, MnvH1DToCSV
from PlotUtils import *
import os
import sys
import math
import ctypes
import json, re
import numpy as np
import time
from array import array

# names associated with each category: data for full data, qelike for MC signal, qelikenot for MC bkg
# noconverge_count = 0
# noconverge_lowbins_count = 0
# noconverge_firstbin_count = 0
skip_univs = [
    "NeutronInelasticExclusives",
]
skipbins = 0

dosimulfithists = False

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
mc_cat_color_list = [
    ROOT.kBlue-6,
    ROOT.kMagenta-6,
    ROOT.kRed-6,
    # ROOT.kGreen-6,
    ROOT.kYellow-6
]
fixed_cats_list = [
    "other", 
    # "multipion"
]
scale_var = "Q2QE"
fit_var = "recoil"
# scaletype = "area"
# scaletype = "POT"
scaletype = "SBarea" # This area scales the sidebands individually
buildprefitmnvh1d = True

variable_list = ["FitQ2QE_Fitrecoil"]
# names associated with each "sample" e.g. QElike, QElikeALL
sample_list = [
    "QElike", 
    "TrackSideband",
    "BlobSideband"#, 
    # "MultipBlobSideband"
    # "TrackBlobSideband"
]

fit_sample_list = [
    "QElike", 
    "TrackSideband",
    "BlobSideband",
]
skipbins = [
    0,
    12,
    # 0,
    12,
    # 0,
]
up_skipbins = [
    0,
    36,
    24,
]
skipbinsdict = {
    "QElike": 0,
    "TrackSideband": 10,
    "BlobSideband": 10
}
outsample_name = ""
for sample in fit_sample_list:
    outsample_name+=sample+"_"

# DRAW = True
# CONFINT = True

# Do fit on tuned hists or not
useTuned = 0
rebin = 12

# Some fit parameters globally set
# min_bin = 51
min_bin = 1
step_size = 0.02
# There's a set list in RunFractionFitter that gets turned on with this option
excludebinsinfit = False
# This is based off of how fitbins are made (i.e. making sidebands that have
# cuts on binedges of the variable you're making), and the histogram naming
# convention CCQENuMAT

# recoil_type = "Log10recoil"

recoil_type = "recoil"

def GetDataMCHistDict(rfile, ):
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
        if dosimulfithists and hist_type not in ['reconstructed_simulfit','reconstructed_simulfit_noPOTscale']:
            continue
        if not dosimulfithists and hist_type!='reconstructed':
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

def GetDummyHistFromBins(i_bins):
    # Make a dummy 1D hist to get binning. Just grabs first 1D Q2QE plot
    dummy_th1d = ROOT.TH1D()
    dummy_mnvh1d = MnvH1D()
    bins = array("d", i_bins)
    dummy_th1d.SetBins(len(i_bins) - 1, bins)
    dummy_mnvh1d = MnvH1D(dummy_th1d)
    return dummy_mnvh1d, dummy_th1d

    # histkeys_list = rfile.GetListOfKeys()
    # for histkey in histkeys_list:
    #     hist_name = histkey.GetName()
    #     # TODO: This is hardcoded, should change it
    #     if hist_name.find("___"+variable_name+"___") == -1:
    #         continue
    #     else:
    #         dummy_mnvh1d = rfile.Get(hist_name).Clone()
    #         dummy_th1d = dummy_mnvh1d.GetCVHistoWithStatError().Clone()

    #         # Clears hist, leaves only binning
    #         dummy_mnvh1d.ClearAllErrorBands()

    #         dummy_mnvh1d.Reset("ICES")
    #         dummy_th1d.Reset("ICES")

            # return dummy_mnvh1d, dummy_th1d

    # print("No suitable hist to make a dummy with. Exiting...")
    # sys.exit()

def PrintFitResults(fit, function):
    print("Function: ", function.GetExpFormula())
    print("chi2: ", function.GetChisquare())
    print("ndf: ", function.GetNDF())
    print("Covariance Matrix: ", fit.GetCovarianceMatrix())
    print("Correlation Matrix: ", fit.GetCorrelationMatrix())

def MakeLongHist2D(i_hist_list, mctot=False):
    first = True
    out_hist = i_hist_list[0].Clone()
    for hist in i_hist_list:
        if first:
            first = False
            continue
        tmp_hist = hist.Clone()
        out_hist.Add(tmp_hist,1.0)
    return out_hist

def BuildLongTH1D(hist_list,doskips=True,out_name = ""):
    # Build a long hist from several input hists
    if len(hist_list) != len(fit_sample_list):
        print("SOMETHING WRONG, more input hists than samples to use: ",  len(hist_list)," ", len(fit_sample_list))
        sys.exit(1)
    i_hist_list = [hist.Clone() for hist in hist_list]
    # for hist in i_hist_list:
    #     if doskips: hist.Rebin(rebin)
    nxbins_list = [hist.GetNbinsX() for hist in i_hist_list]
    # print(nxbins_list)
    xbins_list = [list(hist.GetXaxis().GetXbins()) for hist in i_hist_list]
    # nybins = i_hist_list[0].GetNbinsX()
    # ybins = list(i_hist_list[0].GetXaxis().GetXbins())
    if out_name == "":
        out_name = i_hist_list[0].GetName() + "_long"
    out_title = out_name
    tmp_skipbins = skipbins
    tmp_up_skipbins = up_skipbins

    nskips = 0
    for skips in tmp_skipbins+tmp_up_skipbins: 
        nskips += skips
    if not doskips or nskips==0: 
        tmp_skipbins = [0 for skips in skipbins]
        tmp_up_skipbins = [0 for skips in up_skipbins]
    else: 
        tmp_skipbins = [int(skips/rebin) for skips in skipbins]
        tmp_up_skipbins = [int(skips/rebin) for skips in up_skipbins]
    nskips = 0
    for skips in tmp_skipbins+tmp_up_skipbins: 
        nskips += skips
    print("nskips:", nskips)
    tmp_xbins_list = xbins_list

    if nskips!=0:
        # tmp_skipbins = [int(skips/rebin) for skips in skipbins]
            
        tmp_xbins_list = []
        for i in range(len(xbins_list)):
            top = len(xbins_list[i])
            bins = xbins_list[i][tmp_skipbins[i]:(top - tmp_up_skipbins[i])]
            # bins = xbins_list[i][tmp_skipbins[i]::]
            # print(bins)
            # binslist = xbins_list[i]
            # del binslist[0:tmp_skipbins[i]]
            # print(binslist)
            tmp_xbins_list.append(bins)
        # xbins_list = tmp_xbins_list
    # print(tmp_skipbins)
    # eval('{:.{p}g}'.format(global_max / tmp_pad_max, p=3))
    new_xbins = tmp_xbins_list[0]
    high_edge = tmp_xbins_list[0][-1]

    # print(tmp_xbins_list)
    for bins in tmp_xbins_list[1::]:
        lowerlim = bins[0]
        tmp_bins = [edge - lowerlim for edge in bins]
        for edge in tmp_bins[1::]:
            # tmpedge = eval('{:.{p}g}'.format(edge+high_edge,p=3))
            tmpedge = edge+high_edge
            new_xbins.append(tmpedge)
        high_edge = new_xbins[-1]
    totbins = 0
    for num in nxbins_list:
        totbins += num
    print("totbins:",totbins)
    # nskips = 0
    # for skips in tmp_skipbins: 
    #     nskips += skips
    # totbins -= len(xbins_list)*tmp_skipbins
    totbins -= nskips
    # print(nskips)
    if len(new_xbins)-1 != totbins:
        print(xbins_list)
        print(tmp_xbins_list)
        print(new_xbins)
        print("SOMETHING WRONG, binning doesn't match. n new xbins:", len(new_xbins)-1," n bins supposed", totbins)
        sys.exit(1)
    new_hist = ROOT.TH1D(out_name,out_title, len(new_xbins) - 1, array("d",new_xbins))

    shift = 0
    # for hist in i_hist_list:
    new_hist_content = []
    new_hist_error = []
    for j in range(len(i_hist_list)):
        hist = i_hist_list[j]

        tmp_skips = tmp_skipbins[j]
        # for i in range(1,hist.GetNbinsX()+1-tmp_skips):
        #     new_hist.SetBinContent(i+shift, hist.GetBinContent(i+tmp_skips))
        #     new_hist.SetBinError(i+shift, hist.GetBinError(i+tmp_skips))
        # shift += hist.GetNbinsX()-tmp_skips
        tmp_up_skip = tmp_up_skipbins[j]
        for i in range(tmp_skips+1, hist.GetNbinsX()+1 - tmp_up_skip):
            new_hist_content.append(hist.GetBinContent(i))
            new_hist_error.append(hist.GetBinError(i))
    if len(new_hist_content) != new_hist.GetNbinsX():
        print(len(new_hist_content), new_hist.GetNbinsX())
        sys.exit(1)
    
    for i in range(len(new_hist_content)):
        new_hist.SetBinContent(i+1,new_hist_content[i])
        new_hist.SetBinError(i+1,new_hist_error[i])

    return new_hist
            



def GetMCFracList(i_hist_dict):
    # Gets fraction of 1D MC hists relative to total mc
    mctot = i_hist_dict["mctot"].Clone()
    tmp_min_bin = min_bin
    if rebin != 1:
        tmp_min_bin = int((min_bin - 1)/rebin + 1)
    if not dosimulfithists:
        tmp_min_bin = 1
    # mctot_int = mctot.Integral(min_bin, mctot.GetNbinsX())
    mctot_int = mctot.Integral(tmp_min_bin, mctot.GetNbinsX())
    mc_frac_list = []
    print(">>>>>>>>>>>>>>>>>>>>>>>>> max bins", mctot.GetNbinsX())
    print(">>>>>>>>>>>>>>>>>>>>>>>>> tmp min bins", tmp_min_bin)

    for cat in mc_category_list:
        # mc_hist_int = i_hist_dict[cat].Integral(min_bin, mctot.GetNbinsX())
        mc_hist_int = i_hist_dict[cat].Integral(tmp_min_bin, mctot.GetNbinsX())
        mc_frac = mc_hist_int / mctot_int
        mc_frac_list.append(mc_frac)
    return mc_frac_list


# def RunFractionFitter(i_mctot_hist, i_qelike_hist, i_qelikenot_hist, i_data_hist):
def RunFractionFitter(i_hist_dict, univ_name="", fitbin_name=""):
    data_hist = i_hist_dict["data"].Clone()
    mc_hist_list = []
    for cat in mc_category_list:
        mc_hist_list.append(i_hist_dict[cat].Clone())

    # Get min and max bin for fitting (underflow is 0, overflow is nbins+1)
    tmp_min_bin = min_bin
    if rebin != 1:
        tmp_min_bin = int((min_bin - 1)/rebin + 1)
    if not dosimulfithists:
        tmp_min_bin = 1
    tmp_max_bin = i_hist_dict["mctot"].GetNbinsX()

    print("\tmin_bin ", tmp_min_bin, "\tmax_bin ", tmp_max_bin)

    # Calculate & store pre-fit fractions of MC samples.
    mc_frac_list = GetMCFracList(i_hist_dict)
    print(">>>>>>>>>>>>>>>>>> mc_frac_list: ",mc_frac_list)
    # Make a list of the MC hists for the fitter...
    # mc_list = ROOT.TObjArray(2)
    # mc_list.append(qelike_hist)
    # mc_list.append(qelikenot_hist)
    mc_hist_array = ROOT.TObjArray(len(mc_frac_list))
    for mc_hist in mc_hist_list:
        mc_hist_array.Add(mc_hist)
        # mc_hist_array.append(mc_hist)

    # Set up fitter in verbose mode
    fit = ROOT.TFractionFitter(data_hist, mc_hist_array, "V") 
    virtual_fitter = fit.GetFitter()
    # virtual_fitter.Offset(true)
    # Configure the fit for each mc hist. Names from mc_category_list should share index with hist and histfrac lists
    for i in range(len(mc_hist_list)):
            # virtual_fitter.Config().ParSettings(i).Set(mc_category_list[i], mc_frac_list[i], 0.001, 0.0, 0.05) # Switched step size to be the bin width of 25 recoil bins
        #     # Constrain the fit to between [0,1], since they are fracs and area-normed
        #     fit.Constrain(i, 0.0, 0.05)   
        # fit.Constrain(i, 0., 1.)

        # Set(<name>,<fraction>,<stepsize>,<lowerbound>,<upperbound>)
        virtual_fitter.Config().ParSettings(i).Set(mc_category_list[i], mc_frac_list[i],0.005)# 0.3*mc_frac_list[i])#, 0.001)#mc_frac_list[i]*0.01)#, 0.0, 1.0) # Switched step size to be the bin width of 25 recoil bins
        # Constrain the fit to between [0,1], since they are fracs and area-normed
        # if mc_frac_list[i] < 0.07 and (mc_category_list[i] in fixed_cats_list):
        #     virtual_fitter.Config().ParSettings(i).Fix()
        if mc_category_list[i] in fixed_cats_list:
            # if mc_frac_list[i] < 0.1:
            #     virtual_fitter.Config().ParSettings(i).Fix()
            # else:
            #     lower = 0.5 * mc_frac_list[i]
            #     # lower = 0.0
            #     upper = 2.0 * mc_frac_list[i]
            #     if upper > 1.0: upper = 1.0
            #     # if lower < 0.005: lower = 0.005
            #     print("\t\t\t >>>>>>>>> lower: %f, \tupper: %f"%(lower,upper))

            #     fit.Constrain(i, lower, upper)
            virtual_fitter.Config().ParSettings(i).Fix()
        else:
            lower = 0.01 * mc_frac_list[i]
            # lower = 0.0
            upper = 3.0 * mc_frac_list[i]
            if upper > 1.0: upper = 1.0
            # if lower < 0.005: lower = 0.005
            print("\t\t\t >>>>>>>>> lower: %f, \tupper: %f"%(lower,upper))

            fit.Constrain(i, lower, upper)

        # if mc_category_list[i] == "chargedpion":
        #     upper = mc_frac_list[i]*1.1
        #     if upper > 1.0:
        #         upper = 1.0
        #     lower = 0.01 * mc_frac_list[i]
        #     print("\t\t\t >>>>>>>>> lower: %f, \tupper: %f"%(lower,upper))
        #     fit.Constrain(i, lower, upper)
        # else:
            # upper = mc_frac_list[i]*3.0
            # # upper = mc_frac_list[i]*2.0
            # lower = 0.01 * mc_frac_list[i]
            # if upper > 1.0:
            #     upper = 1.0
            # # lower = 0.01
            # # if lower < mc_frac_list[i]*0.05:
            # #     lower = mc_frac_list[i]*0.05

            # print("\t\t\t >>>>>>>>> lower: %f, \tupper: %f"%(lower,upper))
            # fit.Constrain(i, lower, upper)
        # fit.Constrain(i, 0., 1.)
    # Set the bin range you want to fit on
    fit.SetRangeX(tmp_min_bin, tmp_max_bin)
    # if excludebinsinfit:
    #     excludebins = [
    #         51,
    #         52,
    #         53,
    #         54,
    #         55,
    #         101,
    #         102,
    #         103,
    #         104,
    #         105,
    #     ]
    #     if rebin == 2:
    #         excludebins = [
    #             26,
    #             27,
    #             28,
    #             29,
    #             30,
    #             51,
    #             52,
    #             53,
    #             54,
    #             55,
    #         ]
    #     for xbin in excludebins:
    #         fit.ExcludeBin(xbin)
    # Do the fit
    # fit.ExcludeBin(1)
    status = fit.Fit()

    # Clean up
    # del mctot_hist, qelike_hist, qelikenot_hist, data_hist # TODO: reimpliment with lists. Necessary?

    if status == 0:
        print(">>>>>>>>>>>>>>>>>>>> Fit converged.")
        return fit
    else:
            # noconverge_firstbin_count += 1
        print(">>>>>>>>>>>>>>>>>>>> WARNING: Fit did not converge on band %s in fitbin %s ..."%(univ_name,fitbin_name))
        ROOT.gStyle.SetOptStat(0)
        canvas = ROOT.TCanvas()
        stack = ROOT.THStack()
        
        for i in range(len(mc_hist_list)):
            mc_hist_list[i].SetFillColor(mc_cat_color_list[i])
            stack.Add(mc_hist_list[i])
        # data_hist.SetMaximum(stack.GetMaximum())
        data_hist.SetMaximum(max(data_hist.GetMaximum(),stack.GetMaximum())*1.2)
        data_hist.Draw("E1 X0")
        stack.Draw("HIST same")
        data_hist.Draw("E1 X0 same")

        canvas.Print("fitfailure_%s_%s.png"%(univ_name,fitbin_name))
        sys.exit(1)
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
        # print("==========",mc_category_list[i]," fit_frac: ", fit_frac, "\t fit_err: ", fit_err, "\t scale: ", scale, "\t scale_err: ", scale_err)

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

def GetVarBinning(i_file, var2D_name):
    bins = []
    bigvarconfig_string = ""
    if "varsFile" not in i_file.GetListOfKeys():
        bigvarconfig_string = i_file.Get("varsFile_5A").GetTitle()
    else:
        bigvarconfig_string = i_file.Get("varsFile").GetTitle()
    # print(bigvarconfig_string)
    bigvarconfig_dict = json.loads(re.sub("//.*","",bigvarconfig_string,flags=re.MULTILINE))
    if var2D_name in bigvarconfig_dict["2D"].keys():
        var2Dconfig = bigvarconfig_dict["2D"][var2D_name]
        axisvars = [var2Dconfig["xvar"],var2Dconfig["yvar"]]
    else:
        axisvars = var2D_name.split("_")
    vars1Dconfig = bigvarconfig_dict["1D"]
    for var in axisvars:
        varconfig = vars1Dconfig[var]
        if "bins" in varconfig.keys():
            bins1D = [float(bin) for bin in varconfig["bins"]]
            bins.append(bins1D)
            continue
        elif "nbins" in varconfig.keys():
            min = varconfig["min"]
            max = varconfig["max"]
            width = (max - min)/varconfig["nbins"]
            bins1D = [min + bin*width for bin in range(0,varconfig["nbins"]+1)]
            # print(bins1D)
            bins.append(bins1D)
    # print(bins)
    return bins


def main():
    # noconverge_count = 0
    # This automatically does SetDirectory(0) to all hists. Makes code faster,
    # clean up easier, and mitigates segfault.
    ROOT.TH1.AddDirectory(ROOT.kFALSE)
    n_totunivs = 0
    # Read in a file
    timestr = time.strftime("%Y%m%d-%H%M%S")
    use_separate_files = False
    filenames = []
    if len(sys.argv) < 2:
        print("python FractionFitWithSystematics.py <infile>.root")
    elif len(sys.argv) > 2:
        filenames = sys.argv[1::]
        use_separate_files = True
    else:
        filename = sys.argv[1]
    
    raw_hist_dict = {}

    if use_separate_files:
        firstfile = True
        comb_raw_hist_dict = {}
        for name in filenames:
            tmp_infile = ROOT.TFile(name, "READONLY")

            if firstfile:
                fitvar2Dbins = GetVarBinning(tmp_infile, variable_list[0])
                outfilebase = name.replace(".root","_"+recoil_type+".root")

                firstfile = False
            tmp_hist_dict = GetDataMCHistDict(tmp_infile)

            comb_raw_hist_dict = comb_raw_hist_dict | tmp_hist_dict
        raw_hist_dict = comb_raw_hist_dict
    else:
        # ROOT file from output of eventloop in CCQENuMAT
        infile = ROOT.TFile(filename, "READONLY")
        outfilebase = filename.replace(".root","_"+recoil_type+".root")
        fitvar2Dbins = GetVarBinning(infile, variable_list[0])
        raw_hist_dict = GetDataMCHistDict(infile)



    # ROOT file from output of eventloop in CCQENuMAT
    # infile = ROOT.TFile(filename, "READONLY")

    # outfilebase = filename.replace(".root","_"+recoil_type+".root")

    # dummy q2 and recoil hists, both mnvhnd and th2d
    # dummy_scalevar_mnvh1d, dummy_scalevar_th1d = GetDummyHistCV(infile, scale_var)

    # n_xbins = dummy_scalevar_mnvh1d.GetNbinsX()

    # fitvar2Dbins = GetVarBinning(infile, variable_list[0])
    n_xbins = len(fitvar2Dbins[0]) - 1 
    dummy_scalevar_mnvh1d, dummy_scalevar_th1d = GetDummyHistFromBins(fitvar2Dbins[0])

    # raw_hist_dict = GetDataMCHistDict(infile)
    category_dict = {}
    for category in category_list:
        category_dict[category] = {"hist":None, "list":[]}
        print("making hist for cat", category)
        for hist_name in raw_hist_dict.keys():
            splitnames_list = hist_name.split('___')
            hist_sample = splitnames_list[1]
            hist_category = splitnames_list[2]
            # print(hist_category)
            if hist_category!=category:
                continue
            for sample in fit_sample_list:
                if hist_sample!=sample:
                    continue
                else:
                    category_dict[category]["list"].append(raw_hist_dict[hist_name].Clone())
                    print("    appended hist", hist_name)
        print(len(category_dict[category]["list"]))
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
    prefit_mnvh1d_dict_uncut = {}
    prefit_mnvh1d_dict_shortlist = {}
    fit_mnvh1d_dict = {}
    fit_mnvh1d_dict_uncut = {}
    fit_mnvh1d_dict_shortlist = {}
    fit_chi2_dict = {}
    prefit_chi2_dict = {}
    postfit_chi2_dict = {}
    universe_names_list = ['cv']
    for univ_name in category_dict["qelike"]["hist"].GetVertErrorBandNames():
        universe_names_list.append(univ_name)

    for raw_univ_name in universe_names_list:
        print("  Starting universe ", raw_univ_name, "...")
        univ_name = raw_univ_name
        if raw_univ_name in skip_univs:
            print("\tjust using CV for ", raw_univ_name)
            univ_name == "cv"
        scale_univhist_dict = {}
        frac_univhist_dict = {}
        for cat in mc_category_list:
            scale_univhist_dict[cat] = []
            frac_univhist_dict[cat] = []

        # This holds the pre fit hists to build the error band later
        pre_fitbin_cat_univ_hist_dict = {}
        pre_fitbin_cat_univ_hist_dict_uncut = {}
        pre_fitbin_cat_univ_hist_dict_shortlist = {}
        # This holds the post fit hists to build the error band later
        fitbin_cat_univ_hist_dict = {}
        fitbin_cat_univ_hist_dict_uncut = {}
        fitbin_cat_univ_hist_dict_shortlist = {}

        if raw_univ_name == "cv":
            n_universes = 1
        else:
            n_universes = category_dict["qelike"]["hist"].GetVertErrorBand(raw_univ_name).GetNHists()
        n_totunivs+=n_universes
        for univ in range(0,n_universes):
            print("  Starting universe ", univ, "...")
            # Dict of hists that have been combined
            tmp_th2d_dict = {}
            # Dict of list of hists for each sample
            tmp_th2d_shortlist_dict = {}
            for key in category_dict:
                # This is the already summed hists
                tmp_th2d = ROOT.TH2D()
                # This is the list of hists that haven't been combined yet
                tmp_th2d_shortlist = []

                if raw_univ_name not in skip_univs:
                    if univ_name == "cv" or key == "data":
                        tmp_th2d = category_dict[key]["hist"].GetCVHistoWithStatError().Clone()
                        tmp_th2d_shortlist = [hist.GetCVHistoWithStatError().Clone() for hist in category_dict[key]["list"]]
                    else:
                        tmp_th2d = category_dict[key]["hist"].GetVertErrorBand(univ_name).GetHist(univ).Clone()                        
                        tmp_th2d_shortlist = [hist.GetVertErrorBand(univ_name).GetHist(univ).Clone() for hist in category_dict[key]["list"]]

                else: 
                    tmp_th2d = category_dict[key]["hist"].GetCVHistoWithStatError().Clone()
                    tmp_th2d_shortlist = [hist.GetCVHistoWithStatError().Clone() for hist in category_dict[key]["list"]]
                if key in mc_category_list:
                    scale_univhist_dict[key].append(dummy_scalevar_th1d.Clone())
                    frac_univhist_dict[key].append(dummy_scalevar_th1d.Clone())
                tmp_th2d_dict[key] = tmp_th2d
                tmp_th2d_shortlist_dict[key] = tmp_th2d_shortlist
            
            print("***********************************************",frac_univhist_dict.keys())
            for key in frac_univhist_dict.keys():
                print(len(frac_univhist_dict[key]))

            for fitbin in range(1, n_xbins + 1):
                print("        Working on fitbin number ", fitbin)
                fitbin_name = "fitbin" + str("%02d" % fitbin)
                # This holds the pre fit hists to build the error band later
                pre_fitbin_cat_univ_hist_dict[fitbin] = {}
                pre_fitbin_cat_univ_hist_dict_uncut[fitbin] = {}
                pre_fitbin_cat_univ_hist_dict_shortlist[fitbin] = {}

                # This holds the post fit hists to build the error band later
                fitbin_cat_univ_hist_dict[fitbin] = {}
                fitbin_cat_univ_hist_dict_uncut[fitbin] = {}
                fitbin_cat_univ_hist_dict_shortlist[fitbin] = {}
                for cat in mc_category_list+["mctot"]:
                    pre_fitbin_cat_univ_hist_dict[fitbin][cat] = []
                    fitbin_cat_univ_hist_dict[fitbin][cat] = []
                    pre_fitbin_cat_univ_hist_dict_uncut[fitbin][cat] = []
                    fitbin_cat_univ_hist_dict_uncut[fitbin][cat] = []
                    pre_fitbin_cat_univ_hist_dict_shortlist[fitbin][cat] = []
                    fitbin_cat_univ_hist_dict_shortlist[fitbin][cat] = []

                prefit_th1d_dict = {}
                prefit_th1d_dict_uncut = {}
                prefit_th1d_dict_shortlist = {}
                if raw_univ_name == 'cv': 
                    # this is gonna be used to store the mnvh1d's 
                    prefit_mnvh1d_dict[fitbin] = {}
                    prefit_mnvh1d_dict_uncut[fitbin] = {}
                    prefit_mnvh1d_dict_shortlist[fitbin] = {}
                    fit_mnvh1d_dict[fitbin] = {}
                    fit_mnvh1d_dict_uncut[fitbin] = {}
                    fit_mnvh1d_dict_shortlist[fitbin] = {}

                    # This is gonna be used to 
                    tmp_prefit_mnvh1d_shortlist_dict = {}

                for cat in tmp_th2d_dict.keys():
                    # Make the projections
                    proj_name = fitbin_name + '_' + cat
                    tmp_fitbin_th1d = ROOT.TH1D()
                    # I dont think i need to combine the first q2 bins anymore
                    if combinefirstbins and fitbin in [3,4,5]:
                        if fitbin in [3,4,5]:
                            tmp_fitbin_th1d = tmp_th2d_dict[cat].ProjectionY(proj_name, 3,5, "e")
                        # elif fitbin in [8,9]:
                        #     tmp_fitbin_th1d = tmp_th2d_dict[cat].ProjectionY(proj_name, 8, 9, "e")
                    else:
                        tmp_fitbin_th1d = tmp_th2d_dict[cat].ProjectionY(proj_name, fitbin, fitbin, "e")

                    # This will project the combined sb hists
                    # tmp_fitbin_th1d = tmp_th2d_dict[cat].ProjectionY(proj_name, fitbin, fitbin, "e")
                    # if rebin>1.:
                    #     tmp_fitbin_th1d.Rebin(rebin)
                    prefit_th1d_dict[cat] = tmp_fitbin_th1d
                    # prefit_th1d_dict_uncut[cat] = tmp_fitbin_th1d
                    # This will project the separate sb hists
                    tmp_fitbin_th1d_shortlist = []
                    for hist in tmp_th2d_shortlist_dict[cat]:
                        if combinefirstbins and fitbin in [3,4,5]:
                            if fitbin in [3,4,5]:
                                tmp_proj = hist.ProjectionY(proj_name, 3, 5, "e")
                            # elif fitbin in [8,9]:
                            #     tmp_proj = hist.ProjectionY(proj_name, 8, 9, "e")
                        else:
                            tmp_proj = hist.ProjectionY(proj_name, fitbin, fitbin, "e")
                        if rebin>1.:
                            tmp_proj.Rebin(rebin)
                        tmp_fitbin_th1d_shortlist.append(tmp_proj)
                    prefit_th1d_dict_shortlist[cat] = tmp_fitbin_th1d_shortlist

                    print("     Number of entries in ", cat,": ", tmp_fitbin_th1d.GetEntries())
                    # Need to make a MnvH1D of each fitbin before the fit. Using 'cv' universe so this only happens once (rather than doing this step needlessly in every universe)
                    if raw_univ_name == 'cv' and (cat == "data" or not buildprefitmnvh1d):
                        # print(">>>>>>>>> cat: ",cat)
                        if 'tuned' in cat:
                            tmpname = cat.replace('_tuned','')
                            prefit_mnvh1d_name = "h___"+outsample_name+"__" + tmpname + "___" + recoil_type + "_" + fitbin_name + "___prefit_tuned"
                        else:
                            prefit_mnvh1d_name = "h___"+outsample_name+"__" + cat + "___" + recoil_type + "_" + fitbin_name + "___prefit"

                        # print(prefit_mnvh1d_name)
                        prefit_fitvar_mnvh = MnvH1D()
                        prefit_fitvar_mnvh = category_dict[cat]["hist"].ProjectionY(prefit_mnvh1d_name, fitbin, fitbin, "e").Clone()
                        if rebin>1.:
                            prefit_fitvar_mnvh.Rebin(rebin)
                        prefit_mnvh1d_dict[fitbin][cat] = prefit_fitvar_mnvh #TODO need to scale these
                # mc_hist_list = []
                # for cat in mc_category_list:
                #     mc_hist_list.append(prefit_th1d_dict[cat])
                # TODO set up scaling, configable (if necessary) to do POT or area norming (which is why you need to do it this late)
                # This will area scale the combined sideband histograms
                if scaletype not in ["POT"]:
                    print("Doing area scaling...")
                    max_xbin = prefit_th1d_dict["data"].GetNbinsX()
                    tmp_min_bin = min_bin
                    if rebin != 1:
                        tmp_min_bin = int((min_bin - 1)/rebin + 1)
                    if not dosimulfithists:
                        tmp_min_bin = 1
                    print(">>>>>>>>>>>>>>> tmpminbin", tmp_min_bin)
                    tmp_area_scale = (prefit_th1d_dict["data"].Integral(tmp_min_bin, max_xbin)) / (prefit_th1d_dict["mctot"].Integral(tmp_min_bin, max_xbin))
                    prefit_th1d_dict["mctot"].Scale(tmp_area_scale)

                    if not buildprefitmnvh1d:
                        prefit_mnvh1d_dict[fitbin]["mctot"] = prefit_fitvar_mnvh 
                        for cat in mc_category_list:
                            prefit_th1d_dict[cat].Scale(tmp_area_scale)
                            prefit_mnvh1d_dict[fitbin][cat].Scale(tmp_area_scale)
                # prefit_th1d_dict_uncut[cat] = prefit
                # This will area scale the sidebands separately
                if scaletype == "SBarea":
                    print("Doing area scaling by sideband...")
                    tmp_min_bin = min_bin
                    if rebin != 1:
                        tmp_min_bin = int((min_bin - 1)/rebin + 1)
                    if not dosimulfithists:
                        tmp_min_bin = 1
                    max_xbin = prefit_th1d_dict["data"].GetNbinsX()
                    for i in range(len(prefit_th1d_dict_shortlist["data"])):
                        tmp_max_bin = max_xbin
                        # tmp_max_bin = max_xbin - skipbins[i]
                        # if len(prefit_th1d_dict_shortlist["data"]) == 2 or i in [1,2]:
                        #     tmp_max_bin -= int(up_skipbins[i]/rebin)
                        tmp_area_scale = 1.0
                        tmp_data_area = prefit_th1d_dict_shortlist["data"][i].Integral(tmp_min_bin, tmp_max_bin)
                        tmp_mc_area = prefit_th1d_dict_shortlist["mctot"][i].Integral(tmp_min_bin, tmp_max_bin)
                        if tmp_mc_area == 0:
                            print("WARNING: MC area is zero for some reason, and i can't scale this.")
                            print("\tfitbin: %s\tuniv: %s%03d"%(fitbin_name, raw_univ_name,univ))
                        else:
                            tmp_area_scale = tmp_data_area/tmp_mc_area
                        prefit_th1d_dict_shortlist["mctot"][i].Scale(tmp_area_scale)
                        for cat in mc_category_list:
                            prefit_th1d_dict_shortlist[cat][i].Scale(tmp_area_scale)
                    # Now we can combine these histograms
                    print("WARNING: Combining scaled 1D hists to make a long hist. This will clear the previous prefit_th1d_dict")
                    prefit_th1d_dict = {}
                    if dosimulfithists:
                        print("=========I SHOULDN'T BE HERE")
                        for cat in prefit_th1d_dict_shortlist:
                            first_hist = True
                            tmp_tot_hist = ROOT.TH1D()
                            for tmp_hist in prefit_th1d_dict_shortlist[cat]:
                                if first_hist:
                                    tmp_tot_hist = tmp_hist.Clone()
                                    first_hist = False
                                    continue
                                tmp_tot_hist.Add(tmp_hist,1.0)
                            prefit_th1d_dict[cat] = tmp_tot_hist
                    else:
                        print("===========================HERE I AM")
                        for cat in prefit_th1d_dict_shortlist:
                            # hist_list = prefit_th1d_dict_shortlist[cat]
                            print("making the long hist")
                            prefit_th1d_dict[cat] = BuildLongTH1D(prefit_th1d_dict_shortlist[cat])
                            print("making the uncut long hist")
                            prefit_th1d_dict_uncut[cat] = BuildLongTH1D(prefit_th1d_dict_shortlist[cat],False)
                prefit_th1d_dict["data"].Print()
                
                if buildprefitmnvh1d:
                    if raw_univ_name == "cv":
                        print("Building mnvh1d prefit manually")
                        print("filling prefit cv")
                        # for cat in mc_category_list+["mctot"]:
                        for cat in prefit_th1d_dict.keys():
                            tmp_prefit_mnvh1d = MnvH1D(prefit_th1d_dict[cat])
                            tmp_prefit_uncut_mnvh1d = MnvH1D(prefit_th1d_dict_uncut[cat])
                            prefit_mnvh1d_name = ""
                            if 'tuned' in cat:
                                tmpname = cat.replace('_tuned','')
                                prefit_mnvh1d_name = "h___"+outsample_name+"__" + tmpname + "___" + recoil_type + "_" + fitbin_name + "___prefit_tuned"
                            else:
                                prefit_mnvh1d_name = "h___"+outsample_name+"__" + cat + "___" + recoil_type + "_" + fitbin_name + "___prefit"
                            tmp_prefit_mnvh1d.SetName(prefit_mnvh1d_name)
                            prefit_mnvh1d_dict[fitbin][cat] = tmp_prefit_mnvh1d

                            tmp_prefit_uncut_mnvh1d.SetName(prefit_mnvh1d_name+"_uncut")
                            prefit_mnvh1d_dict_uncut[fitbin][cat] = tmp_prefit_uncut_mnvh1d

                            prefit_mnvh1d_dict_shortlist[fitbin][cat] = []
                            # for hist in prefit_th1d_dict_shortlist[cat]:
                            for i in range(len(prefit_th1d_dict_shortlist[cat])):
                                hist = prefit_th1d_dict_shortlist[cat][i]
                                tmp_prefit_mnvh1d = MnvH1D(hist)
                                prefit_mnvh1d_name = ""
                                if 'tuned' in cat:
                                    tmpname = cat.replace('_tuned','')
                                    prefit_mnvh1d_name = "h___"+sample_list[i]+"__" + tmpname + "___" + recoil_type + "_" + fitbin_name + "___prefit_tuned"
                                else:
                                    prefit_mnvh1d_name = "h___"+sample_list[i]+"__" + cat + "___" + recoil_type + "_" + fitbin_name + "___prefit"
                                tmp_prefit_mnvh1d.SetName(prefit_mnvh1d_name)
                                prefit_mnvh1d_dict_shortlist[fitbin][cat].append(tmp_prefit_mnvh1d)
                    else:
                        print("filling prefit errorband ", raw_univ_name,  "...")
                        for cat in mc_category_list+["mctot"]:
                            pre_fitbin_cat_univ_hist_dict[fitbin][cat].append(prefit_th1d_dict[cat])
                            pre_fitbin_cat_univ_hist_dict_uncut[fitbin][cat].append(prefit_th1d_dict_uncut[cat])
                            if univ == n_universes - 1:
                                prefit_mnvh1d_dict[fitbin][cat].AddVertErrorBand(raw_univ_name,pre_fitbin_cat_univ_hist_dict[fitbin][cat])
                                prefit_mnvh1d_dict_uncut[fitbin][cat].AddVertErrorBand(raw_univ_name,pre_fitbin_cat_univ_hist_dict_uncut[fitbin][cat])
                            for i in range(len(prefit_th1d_dict_shortlist[cat])):
                                if len(pre_fitbin_cat_univ_hist_dict_shortlist[fitbin][cat]) <= i: 
                                    pre_fitbin_cat_univ_hist_dict_shortlist[fitbin][cat].append([])
                                pre_fitbin_cat_univ_hist_dict_shortlist[fitbin][cat][i].append(prefit_th1d_dict_shortlist[cat][i])
                                if univ == n_universes - 1:
                                    prefit_mnvh1d_dict_shortlist[fitbin][cat][i].AddVertErrorBand(raw_univ_name,pre_fitbin_cat_univ_hist_dict_shortlist[fitbin][cat][i])


                
                # Moved chi2 stuff to "if 'cv'" part at end of this loop
                # prefit_chi2 = prefit_th1d_dict["data"].Chi2Test(prefit_th1d_dict["mctot"], "UW,CHI2")
                # prefit_ndf = prefit_th1d_dict["data"].GetNbinsX() - 1 # TODO: this might be different for so many hists
                mc_frac_list = GetMCFracList(prefit_th1d_dict) #["mctot"],mc_hist_list)

                print("        Running Fraction Fitter... fitbin ", fitbin)
                fit = RunFractionFitter(prefit_th1d_dict,raw_univ_name,fitbin_name)
                fit_frac_list, fit_frac_err_list, scale_list, scale_err_list = GetOutVals(fit,mc_frac_list)

                # Moved chi2 stuff to "if 'cv'" part at end of this loop
                # fit_chi2 = fit.GetChisquare()
                # fit_ndf = fit.GetNDF()

                # Make the scaled "fitted" hists, and new mctot
                fit_th1d_dict = {}
                fit_th1d_dict_uncut = {}
                fit_th1d_dict_shortlist = {}
                for i in range(len(mc_category_list)):
                    tmp_fit_th1d = prefit_th1d_dict[mc_category_list[i]].Clone()
                    tmp_fit_th1d.Scale(scale_list[i])
                    fit_th1d_dict[mc_category_list[i]] = tmp_fit_th1d
                    tmp_fit_th1d_uncut = prefit_th1d_dict_uncut[mc_category_list[i]].Clone()
                    tmp_fit_th1d_uncut.Scale(scale_list[i])
                    fit_th1d_dict_uncut[mc_category_list[i]] = tmp_fit_th1d_uncut

                    fit_th1d_shortlist_tmp = []
                    for j in range(len(prefit_th1d_dict_shortlist[mc_category_list[i]])):
                        tmp_fit_th1d_short = prefit_th1d_dict_shortlist[mc_category_list[i]][j].Clone()
                        tmp_fit_th1d_short.Scale(scale_list[i])
                        fit_th1d_shortlist_tmp.append(tmp_fit_th1d_short)
                    fit_th1d_dict_shortlist[mc_category_list[i]] = fit_th1d_shortlist_tmp
                dummy_mctot_hist = fit_th1d_dict[mc_category_list[0]].Clone()
                dummy_mctot_hist_uncut = fit_th1d_dict_uncut[mc_category_list[0]].Clone()
                for cat in mc_category_list:
                    if cat == mc_category_list[0]:
                        continue
                    else:
                        dummy_mctot_hist.Add(fit_th1d_dict[cat],1.0)
                        dummy_mctot_hist_uncut.Add(fit_th1d_dict_uncut[cat],1.0)
                fit_th1d_dict["mctot"] = dummy_mctot_hist
                fit_th1d_dict_uncut["mctot"] = dummy_mctot_hist_uncut
                fit_th1d_dict_shortlist_mctottmp = []
                for i in range(len(fit_th1d_dict_shortlist[mc_category_list[0]])):
                    dummy_mctot_hist_short = fit_th1d_dict_shortlist[mc_category_list[0]][i].Clone()
                    for cat in mc_category_list:
                        if cat == mc_category_list[0]:
                            continue
                        else:
                            dummy_mctot_hist_short.Add(fit_th1d_dict_shortlist[cat][i],1.0)
                    fit_th1d_dict_shortlist_mctottmp.append(dummy_mctot_hist_short)
                fit_th1d_dict_shortlist["mctot"] = fit_th1d_dict_shortlist_mctottmp
                # Moved chi2 stuff to "if 'cv'" part at end of this loop
                # postfit_chi2 = prefit_th1d_dict["data"].Chi2Test(fit_th1d_dict["mctot"],"UW,CHI2")

                if raw_univ_name == "cv":
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
                        tmp_fit_mnvh1d_uncut = MnvH1D(fit_th1d_dict_uncut[mc_category_list[i]])
                        tmp_fit_mnvh1d_uncut.SetName("h___"+outsample_name+"__"+mc_category_list[i]+"___"+fit_var+"_"+fitbin_name+"___fit_uncut")
                        fit_mnvh1d_dict_uncut[fitbin][mc_category_list[i]] = tmp_fit_mnvh1d_uncut
                        # cat = mc_category_list[i]
                        fit_mnvh1d_dict_shortlist_tmp = []
                        for j in range(len(fit_th1d_dict_shortlist[mc_category_list[i]])):
                            tmp_fit_mnvh1d_short = MnvH1D(fit_th1d_dict_shortlist[mc_category_list[i]][j])
                            tmp_fit_mnvh1d_short.SetName("h___"+sample_list[j]+"__"+mc_category_list[i]+"___"+fit_var+"_"+fitbin_name+"___fit")
                            fit_mnvh1d_dict_shortlist_tmp.append(tmp_fit_mnvh1d_short)
                        fit_mnvh1d_dict_shortlist[fitbin][mc_category_list[i]] = fit_mnvh1d_dict_shortlist_tmp
                    # Do the same for the mctot hist
                    tmp_fit_mctot_mnvh1d = MnvH1D(fit_th1d_dict["mctot"])
                    tmp_fit_mctot_mnvh1d.SetName("h___"+outsample_name+"__mctot___"+fit_var+"_"+fitbin_name+"___fit")
                    fit_mnvh1d_dict[fitbin]["mctot"] = tmp_fit_mctot_mnvh1d
                    tmp_fit_mctot_mnvh1d_uncut = MnvH1D(fit_th1d_dict_uncut["mctot"])
                    tmp_fit_mctot_mnvh1d_uncut.SetName("h___"+outsample_name+"__mctot___"+fit_var+"_"+fitbin_name+"___fit_uncut")
                    fit_mnvh1d_dict_uncut[fitbin]["mctot"] = tmp_fit_mctot_mnvh1d_uncut
                    fit_mnvh1d_dict_shortlist_mctottmp = []
                    for j in range(len(fit_th1d_dict_shortlist["mctot"])):
                        tmp_fit_mctot_mnvh1d_short = MnvH1D(fit_th1d_dict_shortlist["mctot"][j])
                        tmp_fit_mctot_mnvh1d_short.SetName("h___"+sample_list[j]+"__mctot___"+fit_var+"_"+fitbin_name+"___fit")
                        fit_mnvh1d_dict_shortlist_mctottmp.append(tmp_fit_mctot_mnvh1d_short)
                    fit_mnvh1d_dict_shortlist[fitbin]["mctot"] = fit_mnvh1d_dict_shortlist_mctottmp
                else:
                    print("        Filling hists for error band ", raw_univ_name, "...")  
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
                        fitbin_cat_univ_hist_dict_uncut[fitbin][cat].append(fit_th1d_dict_uncut[cat])
                        # kind of hacky but oh well
                        if univ == n_universes - 1:
                            fit_mnvh1d_dict[fitbin][cat].AddVertErrorBand(raw_univ_name, fitbin_cat_univ_hist_dict[fitbin][cat])               
                            fit_mnvh1d_dict_uncut[fitbin][cat].AddVertErrorBand(raw_univ_name, fitbin_cat_univ_hist_dict_uncut[fitbin][cat])               
                        # cat = mc_category_list[i]
                        for j in range(len(fit_th1d_dict_shortlist[cat])):
                            if len(fitbin_cat_univ_hist_dict_shortlist[fitbin][cat]) <= j: 
                                fitbin_cat_univ_hist_dict_shortlist[fitbin][cat].append([])
                            fitbin_cat_univ_hist_dict_shortlist[fitbin][cat][j].append(fit_th1d_dict_shortlist[cat][j])
                            if univ == n_universes - 1:
                                fit_mnvh1d_dict_shortlist[fitbin][cat][j].AddVertErrorBand(raw_univ_name,fitbin_cat_univ_hist_dict_shortlist[fitbin][cat][j])

                    fitbin_cat_univ_hist_dict[fitbin]["mctot"].append(fit_th1d_dict["mctot"])
                    fitbin_cat_univ_hist_dict_uncut[fitbin]["mctot"].append(fit_th1d_dict_uncut["mctot"])
                    # kind of hacky but oh well
                    if univ == n_universes - 1:
                        fit_mnvh1d_dict[fitbin]["mctot"].AddVertErrorBand(raw_univ_name, fitbin_cat_univ_hist_dict[fitbin]["mctot"])               
                        fit_mnvh1d_dict_uncut[fitbin]["mctot"].AddVertErrorBand(raw_univ_name, fitbin_cat_univ_hist_dict_uncut[fitbin]["mctot"])               
                    for j in range(len(fit_th1d_dict_shortlist["mctot"])):
                        if len(fitbin_cat_univ_hist_dict_shortlist[fitbin]["mctot"]) <=j: 
                            fitbin_cat_univ_hist_dict_shortlist[fitbin]["mctot"].append([])
                        fitbin_cat_univ_hist_dict_shortlist[fitbin]["mctot"][j].append(fit_th1d_dict_shortlist["mctot"][j])
                        if univ == n_universes - 1:
                            fit_mnvh1d_dict_shortlist[fitbin]["mctot"][j].AddVertErrorBand(raw_univ_name,fitbin_cat_univ_hist_dict_shortlist[fitbin]["mctot"][j])

                # end if "cv"/else
            # end fitbin loop
        # end n_universes loop
        if raw_univ_name == "cv":
            print("    Done filling CVs...")
        else:
            print("    Adding vert error band ", raw_univ_name, " to scale/frac MnvH1Ds...")
            for cat in mc_category_list:
                scalefrac_mnvh1d_dict[cat]["fraction"].AddVertErrorBand(raw_univ_name,frac_univhist_dict[cat])
                scalefrac_mnvh1d_dict[cat]["scale"].AddVertErrorBand(raw_univ_name,scale_univhist_dict[cat])
    # end univ_name loop
    print("Done filling hists... ")
    print("Syncing bands... ")
    # for cat in scalefrac_mnvh1d_dict.keys():
    #     SyncBands(scalefrac_mnvh1d_dict[cat]["fraction"])
    #     SyncBands(scalefrac_mnvh1d_dict[cat]["scale"])
    plotter = MnvPlotter()

    # for fitbin in fit_mnvh1d_dict.keys():
    #     for cat in fit_mnvh1d_dict[fitbin]:
    #         SyncBands(fit_mnvh1d_dict[fitbin][cat])
    #     for cat in prefit_mnvh1d_dict[fitbin]:
    #         SyncBands(prefit_mnvh1d_dict[fitbin][cat])
    print(">>>>>>>>> chi2 in fitbin:")
    for fitbin in fit_mnvh1d_dict.keys():
        # tmp_prefitmctot = prefit_mnvh1d_dict[fitbin]["mctot"].Clone()
        # tmp_fitmctot = fit_mnvh1d_dict[fitbin]["mctot"].Clone()

        # tmp_data = prefit_mnvh1d_dict[fitbin]["data"].Clone()
        tmp_data = prefit_mnvh1d_dict_uncut[fitbin]["data"].Clone()
        tmp_prefitmctot = MnvH1D()
        tmp_fitmctot = MnvH1D()
        tmp_first = True
        for cat in mc_category_list:
            if tmp_first:
                # tmp_prefitmctot = prefit_mnvh1d_dict[fitbin][cat].Clone()
                # tmp_fitmctot = fit_mnvh1d_dict[fitbin][cat].Clone()
                tmp_prefitmctot = prefit_mnvh1d_dict_uncut[fitbin][cat].Clone()
                tmp_fitmctot = fit_mnvh1d_dict_uncut[fitbin][cat].Clone()
                tmp_first = False
                continue
            # tmp_prefitmctot.Add(prefit_mnvh1d_dict[fitbin][cat], 1.0)
            # tmp_fitmctot.Add(fit_mnvh1d_dict[fitbin][cat], 1.0)
            tmp_prefitmctot.Add(prefit_mnvh1d_dict_uncut[fitbin][cat], 1.0)
            tmp_fitmctot.Add(fit_mnvh1d_dict_uncut[fitbin][cat], 1.0)
        # tmp_preareascale = tmp_data.Integral(min_bin, max_xbin)/tmp_prefitmctot.Integral(min_bin, max_xbin)
        # tmp_prefitmctot.Scale(tmp_preareascale)
        pre_chi2 = plotter.Chi2DataMC(tmp_data,tmp_prefitmctot)

        # tmp_areascale = tmp_data.Integral(min_bin, max_xbin)/tmp_fitmctot.Integral(min_bin, max_xbin)
        # tmp_fitmctot.Scale(tmp_areascale)
        post_chi2 = plotter.Chi2DataMC(tmp_data,tmp_fitmctot)
        print(">>>>>>>>> \tprefit: %f \t postfit: %f"%(pre_chi2,post_chi2))

        tmp_prefit_stack = ROOT.THStack()
        tmp_fit_stack = ROOT.THStack()
        for i in range(len(mc_category_list)):
            cat = mc_category_list[i]
            prefit_mnvh1d_dict_uncut[fitbin][cat].SetFillColor(mc_cat_color_list[i])
            fit_mnvh1d_dict_uncut[fitbin][cat].SetFillColor(mc_cat_color_list[i])
            tmp_prefit_stack.Add(prefit_mnvh1d_dict_uncut[fitbin][cat])
            tmp_fit_stack.Add(fit_mnvh1d_dict_uncut[fitbin][cat])
        
        cc1 = ROOT.TCanvas(tmp_data.GetName()+"vsprefit")
        
        tmp_data.SetMarkerColor(ROOT.kBlack)
        # tmp_prefitmctot.SetMarkerColor(ROOT.kRed)
        # tmp_data.SetMaximum(tmp_data.GetMaximum()*1.2)
        tmp_data.SetMaximum(max(tmp_data.GetMaximum(),tmp_prefit_stack.GetMaximum())*1.2)
        tmp_data.Draw()
        # tmp_prefitmctot.Draw("same")
        tmp_prefit_stack.Draw("Hist same")
        tmp_data.Draw("E1 X0 same")
        # cc1.SetLogy()
        cc1.Print("plots/prefitvsdata_fitbin%02d.png" %(fitbin))
        del cc1
        cc2 = ROOT.TCanvas(tmp_data.GetName()+"vspostfit")

        tmp_data.SetMarkerColor(ROOT.kBlack)
        # tmp_fit_stack.SetMarkerColor(ROOT.kRed)
        # tmp_data.SetMaximum(tmp_data.GetMaximum()*1.2)
        tmp_data.Draw()
        # tmp_fitmctot.Draw("same")
        tmp_fit_stack.Draw("Hist same")
        tmp_data.Draw("E1 X0 same")

        # cc2.SetLogy()
        cc2.Print("plots/postfitvsdata_fitbin%02d.png" %(fitbin))
        del cc2
    print("\n\n\n")
        # Now do each individual sample?
    # for sample in range(len(sample_list)):
    for sample in range(len(prefit_mnvh1d_dict_shortlist[1]["data"])):
        for fitbin in prefit_mnvh1d_dict_shortlist.keys():
            tmp_data = prefit_mnvh1d_dict_shortlist[fitbin]["data"][sample].Clone()
            tmp_first = True
            tmp_prefitmctot = MnvH1D()
            tmp_fitmctot = MnvH1D()
            for cat in mc_category_list:
                if tmp_first:
                    tmp_prefitmctot = prefit_mnvh1d_dict_shortlist[fitbin][cat][sample].Clone()
                    tmp_fitmctot = fit_mnvh1d_dict_shortlist[fitbin][cat][sample].Clone()
                    tmp_first = False
                    continue
                tmp_prefitmctot.Add(prefit_mnvh1d_dict_shortlist[fitbin][cat][sample], 1.0)
                tmp_fitmctot.Add(fit_mnvh1d_dict_shortlist[fitbin][cat][sample], 1.0)
            # tmp_preareascale = tmp_data.Integral(min_bin, max_xbin)/tmp_prefitmctot.Integral(min_bin, max_xbin)
            # tmp_prefitmctot.Scale(tmp_preareascale)

            pre_chi2 = plotter.Chi2DataMC(tmp_data,tmp_prefitmctot)

            # tmp_areascale = tmp_data.Integral(min_bin, max_xbin)/tmp_fitmctot.Integral(min_bin, max_xbin)
            # tmp_fitmctot.Scale(tmp_areascale)
            post_chi2 = plotter.Chi2DataMC(tmp_data,tmp_fitmctot)
            print("%s\t>>>>>>>>> \tprefit: %f \t postfit: %f"%(sample_list[sample],pre_chi2,post_chi2))

            tmp_prefitmctot_orig = prefit_mnvh1d_dict_shortlist[fitbin]["mctot"][sample].Clone()
            tmp_prefitmctot_orig.SetLineColor(ROOT.kRed)
            tmp_fitmctot_orig = fit_mnvh1d_dict_shortlist[fitbin]["mctot"][sample].Clone()
            tmp_fitmctot_orig.SetLineColor(ROOT.kRed)

            pre_chi2_orig = plotter.Chi2DataMC(tmp_data,tmp_prefitmctot_orig)

            post_chi2_orig = plotter.Chi2DataMC(tmp_data,tmp_fitmctot_orig)

            print("%s\t>>>>>>>>> ORIG\tprefit: %f \t postfit: %f"%(sample_list[sample],pre_chi2_orig,post_chi2_orig))

            tmp_prefit_stack = ROOT.THStack()
            tmp_fitmctot_stack = ROOT.THStack()
            for i in range(len(mc_category_list)):
                cat = mc_category_list[i]

                tmp_prefit_hist = prefit_mnvh1d_dict_shortlist[fitbin][cat][sample].Clone()
                tmp_prefit_hist.SetFillColor(mc_cat_color_list[i])
                # tmp_prefit_hist.Scale(tmp_preareascale)

                tmp_fit_hist = fit_mnvh1d_dict_shortlist[fitbin][cat][sample].Clone()
                tmp_fit_hist.SetFillColor(mc_cat_color_list[i])
                # tmp_fit_hist.Scale(tmp_areascale)

                tmp_prefit_stack.Add(tmp_prefit_hist)
                tmp_fitmctot_stack.Add(tmp_fit_hist)

            cc1 = ROOT.TCanvas(tmp_data.GetName()+"vsprefit")
        
            tmp_data.SetMarkerColor(ROOT.kBlack)
            # tmp_prefitmctot.SetMarkerColor(ROOT.kRed)
            # tmp_data.SetMaximum(tmp_data.GetMaximum()*1.2)
            tmp_data.SetMaximum(max(tmp_data.GetMaximum(),tmp_prefit_stack.GetMaximum())*1.2)
            tmp_data.Draw()
            tmp_prefit_stack.Draw("Hist same")
            tmp_prefitmctot_orig.Draw("hist same")
            tmp_data.Draw("E1 X0 same")
            # cc1.SetLogy()
            cc1.Print("%s_prefitvsdata_fitbin%02d.png" %(sample_list[sample],fitbin))
            del cc1
            cc2 = ROOT.TCanvas(tmp_data.GetName()+"vspostfit")

            tmp_data.SetMarkerColor(ROOT.kBlack)
            # tmp_fit_stack.SetMarkerColor(ROOT.kRed)
            # tmp_data.SetMaximum(tmp_data.GetMaximum()*1.2)
            tmp_data.Draw()
            tmp_fitmctot_orig.Draw("hist same")
            tmp_fitmctot_stack.Draw("Hist same")
            tmp_data.Draw("E1 X0 same")

            # cc2.SetLogy()
            cc2.Print("%s_postfitvsdata_fitbin%02d.png" %(sample_list[sample],fitbin))
            del cc2
        print("\n")





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
    print("ntotunivs ", n_totunivs)
    print("Done writing hists to file!")
    print(histfile_name)
    print(outvalfile_name)
    # print("\tnoconverge: %d, \tnoconverge_lowbins: %d, \t noconverge_firstbin: %d"%(noconverge_count,noconverge_lowbins_count,noconverge_firstbin_count))
    # print("\tnoconverge: %d, \tnoconverge_lowbins: %d, \t noconverge_firstbin: %d"%(noconverge_count,noconverge_lowbins_count,noconverge_firstbin_count))
    print("Now making plots")

    # histfile_tail = "_FractionFitHists"
    # histfile_name = outfilebase.replace(".root", histfile_tail)
    fit_mnvh1d_dict
    
    
    print("Success")



if __name__ == "__main__":
    main()
