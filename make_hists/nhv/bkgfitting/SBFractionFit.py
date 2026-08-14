# from unicodedata import category
import ROOT
ROOT.gROOT.SetBatch(True) # Run in batch mode
# from PlotUtils import MnvH1D, MnvH2D, MnvH1DToCSV
from PlotUtils import *
import os
import gc
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
doplots = False
dosimulfithists = False
dorebin_internal_global = False
combinefirstbins = False
category_list = [
    "data", 
    "qelike", 
    "chargedpion", 
    "neutralpion", 
    "other",
    # "multipion",
    # "other_np",
    # "mctot",
]
mc_category_list = [
    "qelike", 
    "chargedpion", 
    "neutralpion", 
    "other",
    # "multipion", 
    # "other_np",
]
mc_cat_color_list = [
    # ROOT.kBlue-6,
    # ROOT.kMagenta-6,
    # ROOT.kRed-6,
    # # ROOT.kGreen-6,
    # ROOT.kYellow-6,
    ROOT.kP6Blue,
    ROOT.kP6Yellow,
    ROOT.kP6Red,
    ROOT.kP6Grape,
    ROOT.kP6Gray,
]

mc_cat_name_list = {
    "qelike":"QElike", 
    "chargedpion":"1 #pi^{#pm}", 
    "neutralpion":"1 #pi^{0}",
    "other": "Other",
    "multipion": "N#pi", 
    "other_np": "Other",
}

fixed_cats_list = [
    # "qelike",
    "other", 
    "other_np", 
    # "multipion"
]
overconstraint_cats_list = [
    # "neutralpion"
    # "multipion",
    # "other",
]
doqelikerebin = False
scale_var = "Q2QE"
fit_var = "recoil"
# scaletype = "area"
# scaletype = "POT"
scaletype = "SBarea" # This area scales the sidebands individually

variable_list = ["FitQ2QE_Fitrecoil"]
# names associated with each "sample" e.g. QElike, QElikeALL
sample_list = [
    "QElike", 
    "TrackSideband",
    "BlobSideband", 
    # "MultipBlobSideband",
]

fit_sample_list = [
    "QElike", 
    "TrackSideband",
    "BlobSideband",
    # "MultipBlobSideband",

]
skipbins = [
]
up_skipbins = [
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
# rebin = 4
rebin = 2

if rebin == 5:
    if len(fit_sample_list) == 4:
        skipbins = [
            0,
            4,
            4,
            16,
        ]
        up_skipbins = [
            0,
            16,
            11,
            4,
        ] 
    if len(fit_sample_list) == 3:
        skipbins = [
            0,
            4,
            4,
        ]
        up_skipbins = [
            0,
            16,
            11,
        ] 
if rebin in [1,2,4]:
    if len(fit_sample_list) == 4:
        skipbins = [
            0,
            4,
            6,
            16,
        ]
        up_skipbins = [
            0,
            16,
            14,
            4,
        ]
    if len(fit_sample_list) == 3:
        skipbins = [
            0,
            4,
            6,
        ]
        up_skipbins = [
            0,
            12,
            14,
        ]
    skipbins = []
    up_skipbins = []
# skipbins = [
#     0,
#     4,
#     4,
#     # 4,
# ]
# up_skipbins = [
#     0,
#     4,
#     4,
#     # 0,
# ]

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

def BuildLongTH1D(i_hist_list,doskips=True,out_name = "",dorebin_internal=False):
    # This function will build a long histogram from the input hists in 
    # hist_list. If doskips is set, it will skip the bins of bins according to 
    # the globally assigned skipbins and up_skipbins. Out_name is the output
    # name for the hist. dorebin_internal will rebin the histograms. This should
    # only be set if you're not already rebinning your hists, and it will allow
    # you to start/end at bins that are not multiples of the rebin if you set it
    # up correctly.


    # Build a long hist from several input hists
    if len(i_hist_list) != len(fit_sample_list):
        print("SOMETHING WRONG, more input hists than samples to use: ",  len(i_hist_list)," ", len(fit_sample_list))
        sys.exit(1)
    hist_list = [hist.Clone() for hist in i_hist_list]
    # for hist in i_hist_list:
    #     if doskips: hist.Rebin(rebin)
    nxbins_list = [hist.GetNbinsX() for hist in hist_list]
    # print(nxbins_list)
    xbins_list = [list(hist.GetXaxis().GetXbins()) for hist in hist_list]
    # nybins = i_hist_list[0].GetNbinsX()
    # ybins = list(i_hist_list[0].GetXaxis().GetXbins())
    if out_name == "":
        out_name = hist_list[0].GetName() + "_long"
    out_title = out_name
    tmp_skipbins = skipbins
    tmp_up_skipbins = up_skipbins
    nskips = 0
    for skips in tmp_skipbins+tmp_up_skipbins: 
        nskips += skips
    if not doskips or nskips==0: 
        tmp_skipbins = [0 for skips in skipbins]
        tmp_up_skipbins = [0 for skips in up_skipbins]
    # else:
    elif not dorebin_internal:
        tmp_skipbins = [int(skips/rebin) for skips in skipbins]
        tmp_up_skipbins = [int(skips/rebin) for skips in up_skipbins]
        # for i in rebins:
        #     tmp_skipbins[i] = int(skipbins[i]/rebins[i])
        #     tmp_up_skipbins[i] = int(up_skipbins[i]/rebins[i])
    
    else: # if dorebin_internal:
        # If you're doing the rebin inside here, you need to check that the total number of skips is divisible by the rebin
        # If they are, you can start/end at bins that are not multiples of the rebin
        for i in range(len(skipbins)):
            sample_nskips = skipbins[i] + up_skipbins[i]
            n_unskips = nxbins_list[i] - sample_nskips
            if n_unskips%rebin != 0:
            # if n_unskips%rebin[i] != 0:
                print("WARNING: skips not compatible with rebin, rounding skips off")
                dorebin_internal = False
                tmp_skipbins = [int(skips/rebin) for skips in skipbins]
                tmp_up_skipbins = [int(skips/rebin) for skips in up_skipbins]
                for j in range(len(hist_list)):
                    if i == 0 and rebin%2 == 0 and doqelikerebin:
                        hist_list[i].Rebin(int(rebin/2))
                    else:
                        hist_list[i].Rebin(rebin)
                    # hist_list[i].Rebin(rebin)
                    nxbins_list[j] = hist_list[j].GetNbinsX()
                    xbins_list[j] = list(hist_list[j].GetXaxis().GetXbins())
                break

    nskips = 0
    for skips in tmp_skipbins+tmp_up_skipbins: 
        nskips += skips
    # print("nskips:", nskips)
    tmp_xbins_list = xbins_list

    if nskips!=0:
        tmp_xbins_list = []
        for i in range(len(xbins_list)):
            top = len(xbins_list[i])
            bins = xbins_list[i][tmp_skipbins[i]:(top - tmp_up_skipbins[i])]
            tmp_xbins_list.append(bins)
    
    new_xbins = tmp_xbins_list[0]
    high_edge = tmp_xbins_list[0][-1]
    for bins in tmp_xbins_list[1::]:
        lowerlim = bins[0]
        tmp_bins = [edge - lowerlim for edge in bins]
        for edge in tmp_bins[1::]:
            tmpedge = edge+high_edge
            new_xbins.append(tmpedge)
        high_edge = new_xbins[-1]
    totbins = 0
    for num in nxbins_list:
        totbins += num
    # print("totbins:",totbins)
    totbins -= nskips
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
    if nskips != 0:
        for j in range(len(hist_list)):
            hist = hist_list[j]
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
    else:
        for j in range(len(hist_list)):
            hist = hist_list[j]
            for i in range(1, hist.GetNbinsX()+1):
                new_hist_content.append(hist.GetBinContent(i))
                new_hist_error.append(hist.GetBinError(i))
    for i in range(len(new_hist_content)):
        new_hist.SetBinContent(i+1,new_hist_content[i])
        new_hist.SetBinError(i+1,new_hist_error[i])

    if dorebin_internal:
        # if new_hist.GetNbinsX() % rebin != 0:
        #     print("SOMETHING WRONG, binning of new hist is not divisible by rebin. Exiting...")
        #     sys.exit(1)
        # new_hist.Rebin(rebin)
        if new_hist.GetNbinsX() % rebin != 0:
            print("SOMETHING WRONG, binning of new hist is not divisible by rebin. Exiting...")
            sys.exit(1)
        new_hist.Rebin(rebin)
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
        elif mc_category_list[i] in overconstraint_cats_list:
            # if mc_frac_list[i] < 0.1:
            #     virtual_fitter.Config().ParSettings(i).Fix()
            # else:
            lower = 0.5 * mc_frac_list[i]
            upper = 1.5 * mc_frac_list[i]
            if upper > 1.0: upper = 1.0
            print("\t\t OVER >>>>>>>>> lower: %f, \tupper: %f"%(lower,upper))
            fit.Constrain(i, lower, upper)
        else:
            # lower = 0.01 * mc_frac_list[i]
            # # lower = 0.0
            # upper = 3.0 * mc_frac_list[i]
            # if upper > 1.0: upper = 1.0
            # # if lower < 0.005: lower = 0.005
            # print("\t\t\t >>>>>>>>> lower: %f, \tupper: %f"%(lower,upper))

            # fit.Constrain(i, lower, upper)
            fit.Constrain(i, 0.0, 1.0)

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

def DrawHistCompPNG(name,title,i_data_hist, i_mc_dict, outdir):
    data = i_data_hist.Clone()
    data.SetTitle(title)
    data.SetMarkerColor(ROOT.kBlack)
    data.SetLineColor(ROOT.kBlack)

    stack = ROOT.THStack()
    for i in range(len(mc_category_list)):
        tmp_hist = i_mc_dict[mc_category_list[i]].Clone()
        tmp_hist.SetFillColor(mc_cat_color_list[i])
        stack.Add(tmp_hist)
    
    canvas = ROOT.TCanvas()
    data.Draw("Axis")
    stack.Draw("HIST same")
    data.Draw("E1 X0 same")

    canvas.Print(os.path.join(outdir,name+".png"),"png")
    del canvas

    return



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
        ordered_filenames = []
        for sample in sample_list:
            for name in filenames:
                if "_"+sample+"_" in name:
                    ordered_filenames.append(name)
        for name in ordered_filenames:
            # tmp_infile = ROOT.TFile(name, "READONLY")
            with ROOT.TFile(name,"READONLY") as tmp_infile:
                if firstfile:
                    fitvar2Dbins = GetVarBinning(tmp_infile, variable_list[0])
                    outfilebase = name.replace(".root","_"+recoil_type+".root")

                    firstfile = False
                # tmp_hist_dict = GetDataMCHistDict(tmp_infile)
                print("Before GetDataMCHistDict")
                keys = tmp_infile.GetListOfKeys()
                print("After GetListOfKeys")
                tmp_hist_dict = {}
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
                    tmp_hist_dict[hist_name]=tmp_infile.Get(hist_name).Clone()
                # return data_hist_dict, mc_hist_dict
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
        category_dict[category] = []
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
                    category_dict[category].append(raw_hist_dict[hist_name].Clone())
                    print("    appended hist", hist_name)

    # Make an mctotal, kind of have to hack this
    category_dict["mctot"] = []
    for hist in category_dict["qelike"]:
        category_dict["mctot"].append(hist.Clone())
    for category in category_list:
        if category in ["data","qelike","mctot"]:
            continue
        for i in range(len(category_dict[category])):
            category_dict["mctot"][i].Add(category_dict[category][i],1.0)

    # Make a dict for the scale factor hists (hacky I know)
    scalefrac_mnvh1d_dict = {}
    for cat in mc_category_list:
        scalename = "h___QElike___"+cat+"___"+scale_var+"___scale"
        fracname = "h___QElike___"+cat+"___"+scale_var+"___fraction"
        fitfracname = "h___"+outsample_name+"___"+cat+"___"+scale_var+"___fitfraction"
        scalefrac_mnvh1d_dict[cat] = {
            "scale": dummy_scalevar_mnvh1d.Clone(scalename), 
            "fraction": dummy_scalevar_mnvh1d.Clone(fracname), 
            "fitfrac": dummy_scalevar_mnvh1d.Clone(fitfracname),
        }


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
    for univ_name in category_dict["qelike"][0].GetVertErrorBandNames():
        universe_names_list.append(univ_name)

    for raw_univ_name in universe_names_list:
        print("  Starting universe ", raw_univ_name, "...")
        univ_name = raw_univ_name
        if raw_univ_name in skip_univs:
            print("\tjust using CV for ", raw_univ_name)
            univ_name == "cv"
        scale_univhist_dict = {}
        frac_univhist_dict = {}
        fitfrac_univhist_dict = {}
        for cat in mc_category_list:
            scale_univhist_dict[cat] = []
            frac_univhist_dict[cat] = []
            fitfrac_univhist_dict[cat] = []

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
            n_universes = category_dict["qelike"][0].GetVertErrorBand(raw_univ_name).GetNHists()
        n_totunivs+=n_universes
        for univ in range(0,n_universes):
            print("  Starting universe ", univ, "...")
            # Dict of list of hists for each sample
            tmp_th2d_shortlist_dict = {}
            for key in category_dict:
                # This is the list of hists that haven't been combined yet
                tmp_th2d_shortlist = []
                if raw_univ_name not in skip_univs:
                    if univ_name == "cv" or key == "data":
                        tmp_th2d_shortlist = [hist.GetCVHistoWithStatError().Clone() for hist in category_dict[key]]
                    else:
                        tmp_th2d_shortlist = [hist.GetVertErrorBand(univ_name).GetHist(univ).Clone() for hist in category_dict[key]]
                else: 
                    tmp_th2d_shortlist = [hist.GetCVHistoWithStatError().Clone() for hist in category_dict[key]]
                if key in mc_category_list:
                    scale_univhist_dict[key].append(dummy_scalevar_th1d.Clone())
                    frac_univhist_dict[key].append(dummy_scalevar_th1d.Clone())
                    fitfrac_univhist_dict[key].append(dummy_scalevar_th1d.Clone())
                # tmp_th2d_dict[key] = tmp_th2d
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
                    pre_fitbin_cat_univ_hist_dict_uncut[fitbin][cat] = []
                    pre_fitbin_cat_univ_hist_dict_shortlist[fitbin][cat] = []

                    fitbin_cat_univ_hist_dict[fitbin][cat] = []
                    fitbin_cat_univ_hist_dict_uncut[fitbin][cat] = []
                    fitbin_cat_univ_hist_dict_shortlist[fitbin][cat] = []

                    for i in range(len(category_dict[cat])):
                         pre_fitbin_cat_univ_hist_dict_shortlist[fitbin][cat].append([])
                         fitbin_cat_univ_hist_dict_shortlist[fitbin][cat].append([])

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

                # for cat in tmp_th2d_dict.keys():
                for cat in tmp_th2d_shortlist_dict:
                    # Make the projections
                    proj_name = fitbin_name + '_' + cat
                    tmp_fitbin_th1d_shortlist = []
                    for hist in tmp_th2d_shortlist_dict[cat]:
                        tmp_proj = ROOT.TH1D()
                        if combinefirstbins and fitbin in [3,4,5]:
                            if fitbin in [3,4,5]:
                                tmp_proj = hist.ProjectionY(proj_name, 3, 5, "e")
                            # elif fitbin in [8,9]:
                            #     tmp_proj = hist.ProjectionY(proj_name, 8, 9, "e")
                        else:
                            tmp_proj = hist.ProjectionY(proj_name, fitbin, fitbin, "e")
                        # if rebin>1.:
                        #     tmp_proj.Rebin(rebin)
                        tmp_fitbin_th1d_shortlist.append(tmp_proj.Clone())
                    prefit_th1d_dict_shortlist[cat] = tmp_fitbin_th1d_shortlist

                    # print("     Number of entries in ", cat,": ", tmp_fitbin_th1d.GetEntries())
                    total_entries = 0
                    for hist in prefit_th1d_dict_shortlist[cat]:
                        total_entries += hist.GetEntries()
                    print("     Number of entries in ", cat,": ", total_entries)
                print("Doing area scaling by sideband...")
                # tmp_min_bin = min_bin
                # if rebin != 1:
                #     tmp_min_bin = int((min_bin - 1)/rebin + 1)
                # if not dosimulfithists:
                #     tmp_min_bin = 1
                # max_xbin = prefit_th1d_dict["data"].GetNbinsX()
                for i in range(len(prefit_th1d_dict_shortlist["data"])):
                    # tmp_max_bin = max_xbin
                    # tmp_max_bin = max_xbin - skipbins[i]
                    # if len(prefit_th1d_dict_shortlist["data"]) == 2 or i in [1,2]:
                    #     tmp_max_bin -= int(up_skipbins[i]/rebin)
                    tmp_min_bin = 1
                    tmp_max_bin = prefit_th1d_dict_shortlist["data"][i].GetNbinsX()
                    if scaletype=="SBarea_fit":
                        tmp_min_bin = skipbins[i] + 1
                        tmp_max_bin -= up_skipbins[i]
                    tmp_area_scale = 1.0
                    tmp_data_area = prefit_th1d_dict_shortlist["data"][i].Integral(tmp_min_bin, tmp_max_bin)
                    tmp_mc_area = prefit_th1d_dict_shortlist["mctot"][i].Integral(tmp_min_bin, tmp_max_bin)
                    if tmp_mc_area == 0:
                        print("WARNING: MC area is zero for some reason, and i can't scale this.")
                        print("\tfitbin: %s\tuniv: %s%03d"%(fitbin_name, raw_univ_name,univ))
                    else:
                        tmp_area_scale = tmp_data_area/tmp_mc_area
                    print("\tarea scale for fitbin %s univ %s%03d: %f"%(fitbin_name, raw_univ_name,univ,tmp_area_scale))
                    for cat in mc_category_list + ["mctot"]:
                        prefit_th1d_dict_shortlist[cat][i].Scale(tmp_area_scale)
                # Now we can combine these histograms
                prefit_th1d_dict = {}
                for cat in prefit_th1d_dict_shortlist:
                    # hist_list = prefit_th1d_dict_shortlist[cat]
                    print("making the long hist for cat %s"%(cat))
                    doskips = True
                    out_name = ""
                    dorebin_internal_short = True
                    tmp_prefit_th1d = BuildLongTH1D(prefit_th1d_dict_shortlist[cat],doskips,out_name,dorebin_internal_short)
                    prefit_th1d_dict[cat] = tmp_prefit_th1d.Clone()

                    print("making the uncut long hist for cat %s"%(cat))
                    doskips = False
                    # dorebin_internal_uncut = True
                    prefit_th1d_uncut = BuildLongTH1D(prefit_th1d_dict_shortlist[cat],doskips,out_name,dorebin_internal_global)
                    prefit_th1d_dict_uncut[cat] = prefit_th1d_uncut.Clone()

                    # If you're rebinning inside the buildlong so you can use non-multiple bins to start/end at, you'll need to rebin these outside now
                    if dorebin_internal_global and rebin > 1:
                        for i in range(len(prefit_th1d_dict_shortlist[cat])):
                            if i == 0 and rebin%2 == 0 and doqelikerebin:
                                prefit_th1d_dict_shortlist[cat][i].Rebin(int(rebin/2))
                            else:
                                prefit_th1d_dict_shortlist[cat][i].Rebin(int(rebin/2))
                            # prefit_th1d_dict_shortlist[cat][i].Rebin(rebin)
                prefit_th1d_dict["data"].Print()
                
                if raw_univ_name == "cv":
                    print("Building mnvh1d prefit manually")
                    print("filling prefit cv")
                    # for cat in mc_category_list+["mctot"]:
                    for cat in prefit_th1d_dict.keys():
                        tmp_prefit_mnvh1d = MnvH1D()
                        tmp_prefit_uncut_mnvh1d = MnvH1D()
                        tmp_prefit_mnvh1d = MnvH1D(prefit_th1d_dict[cat].Clone())
                        tmp_prefit_uncut_mnvh1d = MnvH1D(prefit_th1d_dict_uncut[cat].Clone())
                        prefit_mnvh1d_name = ""
                        if 'tuned' in cat:
                            tmpname = cat.replace('_tuned','')
                            prefit_mnvh1d_name = "h___"+outsample_name+"__" + tmpname + "___" + recoil_type + "_" + fitbin_name + "___prefit_tuned"
                        else:
                            prefit_mnvh1d_name = "h___"+outsample_name+"__" + cat + "___" + recoil_type + "_" + fitbin_name + "___prefit"
                        
                        tmp_prefit_mnvh1d.SetName(prefit_mnvh1d_name)
                        prefit_mnvh1d_dict[fitbin][cat] = tmp_prefit_mnvh1d.Clone()

                        tmp_prefit_uncut_mnvh1d.SetName(prefit_mnvh1d_name+"_uncut")
                        prefit_mnvh1d_dict_uncut[fitbin][cat] = tmp_prefit_uncut_mnvh1d.Clone()

                        prefit_mnvh1d_dict_shortlist[fitbin][cat] = []
                        # for hist in prefit_th1d_dict_shortlist[cat]:
                        for i in range(len(prefit_th1d_dict_shortlist[cat])):
                            # hist = prefit_th1d_dict_shortlist[cat][i]
                            tmp_prefit_mnvh1d = MnvH1D()
                            tmp_prefit_mnvh1d = MnvH1D(prefit_th1d_dict_shortlist[cat][i].Clone())
                            prefit_mnvh1d_name = ""
                            # tmpname = cat
                            # if "other_np" in tmpname:
                            #     tmpname = tmpname.replace("_np","")
                            if 'tuned' in cat:
                                tmpname = cat.replace('_tuned','')
                                prefit_mnvh1d_name = "h___"+sample_list[i]+"__" + cat + "___" + recoil_type + "_" + fitbin_name + "___prefit_tuned"
                            else:
                                prefit_mnvh1d_name = "h___"+sample_list[i]+"__" + cat + "___" + recoil_type + "_" + fitbin_name + "___prefit"
                            tmp_prefit_mnvh1d.SetName(prefit_mnvh1d_name)
                            prefit_mnvh1d_dict_shortlist[fitbin][cat].append(tmp_prefit_mnvh1d.Clone())
                else:
                    print("filling prefit errorband ", raw_univ_name,  "...")
                    for cat in mc_category_list+["mctot"]:
                        pre_fitbin_cat_univ_hist_dict[fitbin][cat].append(prefit_th1d_dict[cat].Clone())
                        pre_fitbin_cat_univ_hist_dict_uncut[fitbin][cat].append(prefit_th1d_dict_uncut[cat].Clone())
                        if univ == n_universes - 1:
                            prefit_mnvh1d_dict[fitbin][cat].AddVertErrorBand(raw_univ_name,pre_fitbin_cat_univ_hist_dict[fitbin][cat])
                            prefit_mnvh1d_dict_uncut[fitbin][cat].AddVertErrorBand(raw_univ_name,pre_fitbin_cat_univ_hist_dict_uncut[fitbin][cat])
                        for i in range(len(prefit_th1d_dict_shortlist[cat])):
                            pre_fitbin_cat_univ_hist_dict_shortlist[fitbin][cat][i].append(prefit_th1d_dict_shortlist[cat][i].Clone())
                            if univ == n_universes - 1:
                                prefit_mnvh1d_dict_shortlist[fitbin][cat][i].AddVertErrorBand(raw_univ_name,pre_fitbin_cat_univ_hist_dict_shortlist[fitbin][cat][i])


                
                # Moved chi2 stuff to "if 'cv'" part at end of this loop
                mc_frac_list = GetMCFracList(prefit_th1d_dict) #["mctot"],mc_hist_list)

                print("        Running Fraction Fitter... fitbin ", fitbin)
                fit = RunFractionFitter(prefit_th1d_dict,raw_univ_name,fitbin_name)
                fit_frac_list, fit_frac_err_list, scale_list, scale_err_list = GetOutVals(fit,mc_frac_list)

                # Make the scaled "fitted" hists, and new mctot
                fit_th1d_dict = {}
                fit_th1d_dict_uncut = {}
                fit_th1d_dict_shortlist = {}
                for i in range(len(mc_category_list)):
                    tmp_fit_th1d = prefit_th1d_dict[mc_category_list[i]].Clone()
                    tmp_fit_th1d.Scale(scale_list[i])
                    fit_th1d_dict[mc_category_list[i]] = tmp_fit_th1d.Clone()

                    tmp_fit_th1d_uncut = prefit_th1d_dict_uncut[mc_category_list[i]].Clone()
                    tmp_fit_th1d_uncut.Scale(scale_list[i])
                    fit_th1d_dict_uncut[mc_category_list[i]] = tmp_fit_th1d_uncut.Clone()

                    fit_th1d_shortlist_tmp = []
                    for j in range(len(prefit_th1d_dict_shortlist[mc_category_list[i]])):
                        tmp_fit_th1d_short = prefit_th1d_dict_shortlist[mc_category_list[i]][j].Clone()
                        tmp_fit_th1d_short.Scale(scale_list[i])
                        fit_th1d_shortlist_tmp.append(tmp_fit_th1d_short.Clone())
                    fit_th1d_dict_shortlist[mc_category_list[i]] = fit_th1d_shortlist_tmp

                dummy_mctot_hist = fit_th1d_dict[mc_category_list[0]].Clone()
                dummy_mctot_hist_uncut = fit_th1d_dict_uncut[mc_category_list[0]].Clone()
                for cat in mc_category_list[1::]:
                    dummy_mctot_hist.Add(fit_th1d_dict[cat].Clone(),1.0)
                    dummy_mctot_hist_uncut.Add(fit_th1d_dict_uncut[cat].Clone(),1.0)
                fit_th1d_dict["mctot"] = dummy_mctot_hist.Clone()
                fit_th1d_dict_uncut["mctot"] = dummy_mctot_hist_uncut.Clone()
                fit_th1d_dict_shortlist_mctottmp = []
                for i in range(len(fit_th1d_dict_shortlist[mc_category_list[0]])):
                    dummy_mctot_hist_short = fit_th1d_dict_shortlist[mc_category_list[0]][i].Clone()
                    for cat in mc_category_list[1::]:
                        dummy_mctot_hist_short.Add(fit_th1d_dict_shortlist[cat][i].Clone(),1.0)
                    fit_th1d_dict_shortlist_mctottmp.append(dummy_mctot_hist_short.Clone())
                fit_th1d_dict_shortlist["mctot"] = fit_th1d_dict_shortlist_mctottmp

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

                    print("=-=-=-=-=-=-=-=-= from fit \tchi2: %f\t ndf: %f" %(fit_chi2, fit_ndf))
                    print("=-=-=-=-=-=-=-=-=- pre fit \tchi2: %f\t ndf: %f" %(prefit_chi2, prefit_ndf))
                    print("=-=-=-=-=-=-=-=-= post fit \tchi2: %f\t ndf: %f" %(postfit_chi2, prefit_ndf))

                    # store the chi2
                    fit_chi2_dict[fitbin] = {"chi2":fit_chi2,"ndf":fit_ndf}
                    prefit_chi2_dict[fitbin] = {"chi2":prefit_chi2,"ndf":prefit_ndf}
                    postfit_chi2_dict[fitbin] = {"chi2":postfit_chi2,"ndf":prefit_ndf}
                    
                    print("      Filling CVs...")

                    tmp_mctotint = fit_th1d_dict_shortlist["mctot"][0].Integral(1,fit_th1d_dict_shortlist["mctot"][0].GetNbinsX())
                    for i in range(len(mc_category_list)):
                        # store scale factors and fractions from the fit into their own hists for output
                        scalefrac_mnvh1d_dict[mc_category_list[i]]["fitfrac"].SetBinContent(fitbin,fit_frac_list[i])
                        scalefrac_mnvh1d_dict[mc_category_list[i]]["fitfrac"].SetBinError(fitbin,fit_frac_err_list[i])
                        scalefrac_mnvh1d_dict[mc_category_list[i]]["scale"].SetBinContent(fitbin,scale_list[i])
                        scalefrac_mnvh1d_dict[mc_category_list[i]]["scale"].SetBinError(fitbin,scale_err_list[i])
                        print("==========",mc_category_list[i]," fit_frac: ", fit_frac_list[i], "\t fit_err: ", fit_frac_err_list[i], "\t scale: ", scale_list[i], "\t scale_err: ", scale_err_list[i])
                        
                        # The "fraction" is for just the QElike sample, which takes some extra care
                        tmp_catint = fit_th1d_dict_shortlist[mc_category_list[i]][0].Integral(1,fit_th1d_dict_shortlist[mc_category_list[i]][0].GetNbinsX())
                        tmp_frac = tmp_catint/tmp_mctotint
                        scalefrac_mnvh1d_dict[mc_category_list[i]]["fraction"].SetBinContent(fitbin,tmp_frac)
                        scalefrac_mnvh1d_dict[mc_category_list[i]]["fraction"].SetBinError(fitbin,fit_frac_err_list[i])

                        # Start building mnvh1ds of each hist scaled from fit
                        tmp_fit_mnvh1d = MnvH1D(fit_th1d_dict[mc_category_list[i]].Clone())
                        tmp_fit_mnvh1d.SetName("h___"+outsample_name+"__"+mc_category_list[i]+"___"+fit_var+"_"+fitbin_name+"___fit")
                        fit_mnvh1d_dict[fitbin][mc_category_list[i]] = tmp_fit_mnvh1d.Clone()

                        tmp_fit_mnvh1d_uncut = MnvH1D(fit_th1d_dict_uncut[mc_category_list[i]].Clone())
                        tmp_fit_mnvh1d_uncut.SetName(tmp_fit_mnvh1d.GetName()+"_uncut")
                        fit_mnvh1d_dict_uncut[fitbin][mc_category_list[i]] = tmp_fit_mnvh1d_uncut.Clone()

                        fit_mnvh1d_dict_shortlist_tmp = []
                        for j in range(len(fit_th1d_dict_shortlist[mc_category_list[i]])):
                            tmp_fit_mnvh1d_short = MnvH1D(fit_th1d_dict_shortlist[mc_category_list[i]][j].Clone())
                            tmp_fit_mnvh1d_short.SetName("h___"+sample_list[j]+"__"+mc_category_list[i]+"___"+fit_var+"_"+fitbin_name+"___fit")
                            fit_mnvh1d_dict_shortlist_tmp.append(tmp_fit_mnvh1d_short.Clone())
                        fit_mnvh1d_dict_shortlist[fitbin][mc_category_list[i]] = fit_mnvh1d_dict_shortlist_tmp
                    # Do the same for the mctot hist
                    tmp_fit_mctot_mnvh1d = MnvH1D(fit_th1d_dict["mctot"].Clone())
                    tmp_fit_mctot_mnvh1d.SetName("h___"+outsample_name+"__mctot___"+fit_var+"_"+fitbin_name+"___fit")
                    fit_mnvh1d_dict[fitbin]["mctot"] = tmp_fit_mctot_mnvh1d.Clone()

                    tmp_fit_mctot_mnvh1d_uncut = MnvH1D(fit_th1d_dict_uncut["mctot"].Clone())
                    tmp_fit_mctot_mnvh1d_uncut.SetName(tmp_fit_mctot_mnvh1d.GetName()+"_uncut")
                    fit_mnvh1d_dict_uncut[fitbin]["mctot"] = tmp_fit_mctot_mnvh1d_uncut.Clone()

                    fit_mnvh1d_dict_shortlist_mctottmp = []
                    for j in range(len(fit_th1d_dict_shortlist["mctot"])):
                        tmp_fit_mctot_mnvh1d_short = MnvH1D(fit_th1d_dict_shortlist["mctot"][j].Clone())
                        tmp_fit_mctot_mnvh1d_short.SetName("h___"+sample_list[j]+"__mctot___"+fit_var+"_"+fitbin_name+"___fit")
                        fit_mnvh1d_dict_shortlist_mctottmp.append(tmp_fit_mctot_mnvh1d_short.Clone())
                    fit_mnvh1d_dict_shortlist[fitbin]["mctot"] = fit_mnvh1d_dict_shortlist_mctottmp
                else:
                    print("        Filling hists for error band ", raw_univ_name, "...")
                    tmp_catint = fit_th1d_dict_shortlist[mc_category_list[i]][0].Integral(1,fit_th1d_dict_shortlist[mc_category_list[i]][0].GetNbinsX())
                    for i in range(len(mc_category_list)):
                        cat = mc_category_list[i]
                        # print("                Inside cat loop for ", cat)
                        # Set the bin content for this universes scale/frac
                        frac_univhist_dict[cat][univ].SetBinContent(fitbin,fit_frac_list[i])
                        # frac_univhist_dict[cat][univ].SetBinError(fitbin,fit_frac_err_list[i])
                        # print (" after set bin contents for frac")                        
                        scale_univhist_dict[cat][univ].SetBinContent(fitbin,scale_list[i])
                        # scale_univhist_dict[cat][univ].SetBinError(fitbin,scale_err_list[i])
                        # print (" after set bin contents for scale")

                        # Calculate the fraction for the signal sample alone
                        tmp_mctotint = fit_th1d_dict_shortlist["mctot"][0].Integral(1,fit_th1d_dict_shortlist["mctot"][0].GetNbinsX())
                        tmp_frac = tmp_catint/tmp_mctotint
                        fitfrac_univhist_dict[cat][univ].SetBinContent(fitbin,tmp_frac)

                        # Make a list of histograms for this universe so we can add all as one error band
                        fitbin_cat_univ_hist_dict[fitbin][cat].append(fit_th1d_dict[cat].Clone())
                        fitbin_cat_univ_hist_dict_uncut[fitbin][cat].append(fit_th1d_dict_uncut[cat].Clone())
                        # kind of hacky but oh well
                        if univ == n_universes - 1:
                            fit_mnvh1d_dict[fitbin][cat].AddVertErrorBand(raw_univ_name, fitbin_cat_univ_hist_dict[fitbin][cat])               
                            fit_mnvh1d_dict_uncut[fitbin][cat].AddVertErrorBand(raw_univ_name, fitbin_cat_univ_hist_dict_uncut[fitbin][cat])               
                        # cat = mc_category_list[i]
                        for j in range(len(fit_th1d_dict_shortlist[cat])):
                            fitbin_cat_univ_hist_dict_shortlist[fitbin][cat][j].append(fit_th1d_dict_shortlist[cat][j].Clone())
                            if univ == n_universes - 1:
                                fit_mnvh1d_dict_shortlist[fitbin][cat][j].AddVertErrorBand(raw_univ_name,fitbin_cat_univ_hist_dict_shortlist[fitbin][cat][j])

                    fitbin_cat_univ_hist_dict[fitbin]["mctot"].append(fit_th1d_dict["mctot"].Clone())
                    fitbin_cat_univ_hist_dict_uncut[fitbin]["mctot"].append(fit_th1d_dict_uncut["mctot"].Clone())
                    # kind of hacky but oh well
                    if univ == n_universes - 1:
                        fit_mnvh1d_dict[fitbin]["mctot"].AddVertErrorBand(raw_univ_name, fitbin_cat_univ_hist_dict[fitbin]["mctot"])               
                        fit_mnvh1d_dict_uncut[fitbin]["mctot"].AddVertErrorBand(raw_univ_name, fitbin_cat_univ_hist_dict_uncut[fitbin]["mctot"])               
                    for j in range(len(fit_th1d_dict_shortlist["mctot"])):
                        fitbin_cat_univ_hist_dict_shortlist[fitbin]["mctot"][j].append(fit_th1d_dict_shortlist["mctot"][j].Clone())
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
                scalefrac_mnvh1d_dict[cat]["fitfrac"].AddVertErrorBand(raw_univ_name,fitfrac_univhist_dict[cat])
                scalefrac_mnvh1d_dict[cat]["fraction"].AddVertErrorBand(raw_univ_name,frac_univhist_dict[cat])
                scalefrac_mnvh1d_dict[cat]["scale"].AddVertErrorBand(raw_univ_name,scale_univhist_dict[cat])
    # end univ_name loop
    print("Done filling hists... ")
    del prefit_th1d_dict
    del prefit_th1d_dict_uncut
    del prefit_th1d_dict_shortlist
    del fit_th1d_dict
    del fit_th1d_dict_uncut
    del fit_th1d_dict_shortlist

    # fitbin_cat_univ_hist_dict = {}
    # fitbin_cat_univ_hist_dict_uncut = {}
    # fitbin_cat_univ_hist_dict_shortlist = {}
    # pre_fitbin_cat_univ_hist_dict = {}
    # pre_fitbin_cat_univ_hist_dict_uncut = {}
    # pre_fitbin_cat_univ_hist_dict_shortlist = {}
    del fitbin_cat_univ_hist_dict
    del fitbin_cat_univ_hist_dict_uncut
    del fitbin_cat_univ_hist_dict_shortlist
    del pre_fitbin_cat_univ_hist_dict
    del pre_fitbin_cat_univ_hist_dict_uncut
    del pre_fitbin_cat_univ_hist_dict_shortlist
    # print("Syncing bands... ")
    for cat in scalefrac_mnvh1d_dict.keys():
        SyncBands(scalefrac_mnvh1d_dict[cat]["fraction"])
        SyncBands(scalefrac_mnvh1d_dict[cat]["scale"])
    for fitbin in fit_mnvh1d_dict.keys():
        for cat in fit_mnvh1d_dict[fitbin]:
            SyncBands(fit_mnvh1d_dict[fitbin][cat])
        for cat in prefit_mnvh1d_dict[fitbin]:
            SyncBands(prefit_mnvh1d_dict[fitbin][cat])
    
    if not os.path.exists("plots"):
        os.mkdir("plots")
    plotter = MnvPlotter()
    print(">>>>>>>>> chi2 in fitbin:")
    postchi2_text = ROOT.TLatex(0.65,0.6, "#chi^{2}")
    postchi2_text.SetNDC()
    postchi2_text.SetTextSize(0.03)
    postchi2_text.SetTextAlign(11)
    postchi2_text.SetTextFont(42)
    prechi2_text = ROOT.TLatex(0.65,0.6, "#chi^{2}")
    prechi2_text.SetNDC()
    prechi2_text.SetTextSize(0.03)
    prechi2_text.SetTextAlign(11)
    prechi2_text.SetTextFont(42)

    prelim = ROOT.TLatex(0.88, 0.7, "MINER#it{#nu}A Work in Progress")
    prelim.SetTextFont(112)
    prelim.SetTextSize(0.03)
    prelim.SetTextColor(ROOT.kRed +1)
    prelim.SetTextAlign(31)
    for fitbin in fit_mnvh1d_dict.keys():
        # tmp_prefitmctot = prefit_mnvh1d_dict[fitbin]["mctot"].Clone()
        # tmp_fitmctot = fit_mnvh1d_dict[fitbin]["mctot"].Clone()
        # tmp_data = prefit_mnvh1d_dict[fitbin]["data"].Clone()
        tmp_prefitmctot = MnvH1D()
        tmp_fitmctot = MnvH1D()

        tmp_data = prefit_mnvh1d_dict_uncut[fitbin]["data"].Clone()
        tmp_first = True
        for cat in mc_category_list:
            tmp_prefit_hist = prefit_mnvh1d_dict_uncut[fitbin][cat].Clone()
            tmp_fit_hist = fit_mnvh1d_dict_uncut[fitbin][cat].Clone()
            if tmp_first:
                # tmp_prefitmctot = prefit_mnvh1d_dict[fitbin][cat].Clone()
                # tmp_fitmctot = fit_mnvh1d_dict[fitbin][cat].Clone()
                tmp_prefitmctot = tmp_prefit_hist.Clone()
                tmp_fitmctot = tmp_fit_hist.Clone()
                tmp_first = False
                continue
            # tmp_prefitmctot.Add(prefit_mnvh1d_dict[fitbin][cat], 1.0)
            # tmp_fitmctot.Add(fit_mnvh1d_dict[fitbin][cat], 1.0)
            tmp_prefitmctot.Add(tmp_prefit_hist, 1.0)
            tmp_fitmctot.Add(tmp_fit_hist, 1.0)
        # tmp_preareascale = tmp_data.Integral(min_bin, max_xbin)/tmp_prefitmctot.Integral(min_bin, max_xbin)
        # tmp_prefitmctot.Scale(tmp_preareascale)
        # tmp_areascale = tmp_data.Integral(min_bin, max_xbin)/tmp_fitmctot.Integral(min_bin, max_xbin)
        # tmp_fitmctot.Scale(tmp_areascale)
        # tmp_data.Print()
        tmp_data_rebin = tmp_data.Clone()
        tmp_prefitmctot_rebin = tmp_prefitmctot.Clone()
        tmp_fitmctot_rebin = tmp_fitmctot.Clone()

        if not dorebin_internal_global:
            print("Hists have not been rebinned yet. Doing it now for comparisons.")
            tmp_data_rebin.Rebin(rebin)
            tmp_prefitmctot_rebin.Rebin(rebin)
            tmp_fitmctot_rebin.Rebin(rebin)
        else:
            print("Hists have already been rebinned, so I won't do that over again.")
        # pre_chi2 = plotter.Chi2DataMC(tmp_data_rebin,tmp_prefitmctot_rebin)
        # post_chi2 = plotter.Chi2DataMC(tmp_data_rebin,tmp_fitmctot_rebin)
        pre_chi2 = plotter.Chi2DataMC(
            tmp_data_rebin,
            tmp_prefitmctot_rebin,
            ctypes.c_int(tmp_data_rebin.GetNbinsX()),
            ctypes.c_double(1.0),
            # False,
            # False,
            # True,
            # None,
        )
        post_chi2 = plotter.Chi2DataMC(
            tmp_data_rebin,
            tmp_fitmctot_rebin,
            ctypes.c_int(tmp_data_rebin.GetNbinsX()),
            ctypes.c_double(1.0),
            # False,
            # False,
            # True,
            # None,
        )
        print(">>>>>>>>> REBIN\tprefit: %f \t postfit: %f\t delta: %f"%(pre_chi2,post_chi2,post_chi2-pre_chi2))
        # pre_chi2_orig = plotter.Chi2DataMC(tmp_data,tmp_prefitmctot)
        # post_chi2_orig = plotter.Chi2DataMC(tmp_data,tmp_fitmctot)
        pre_chi2_orig = plotter.Chi2DataMC(
            tmp_data,
            tmp_prefitmctot,
            ctypes.c_int(tmp_data.GetNbinsX()),
            ctypes.c_double(1.0),
            # False,
            # False,
            # True,
            # None,        
        )
        post_chi2_orig = plotter.Chi2DataMC(
            tmp_data,
            tmp_fitmctot,
            ctypes.c_int(tmp_data.GetNbinsX()),
            ctypes.c_double(1.0),
            # False,
            # False,
            # True,
            # None,  
        )
        print(">>>>>>>>> ORIG\tprefit: %f \t postfit: %f\t delta: %f"%(pre_chi2_orig,post_chi2_orig,post_chi2_orig-pre_chi2_orig))

        ROOT.gStyle.SetOptTitle(1)

        canvas = ROOT.TCanvas("mycanvas%s"%fitbin,"mycanvas",3200,2400)
        prestack = ROOT.THStack()
        poststack = ROOT.THStack()
        leg = ROOT.TLegend(0.65,0.65,0.85,0.85)
        leg.SetTextFont(42)
        leg.SetTextSize(0.04)
        leg.SetBorderSize(0)
        leg.SetFillColor(-1)


        for i in range(len(mc_category_list)):
            prefit_mnvh1d_dict_uncut[fitbin][mc_category_list[i]].SetFillColor(mc_cat_color_list[i])
            prefit_mnvh1d_dict_uncut[fitbin][mc_category_list[i]].SetLineColor(ROOT.TColor.GetColorDark(mc_cat_color_list[i]))
            leg.AddEntry(prefit_mnvh1d_dict_uncut[fitbin][mc_category_list[i]],mc_cat_name_list[mc_category_list[i]])
            fit_mnvh1d_dict_uncut[fitbin][mc_category_list[i]].SetFillColor(mc_cat_color_list[i])
            fit_mnvh1d_dict_uncut[fitbin][mc_category_list[i]].SetLineColor(ROOT.TColor.GetColorDark(mc_cat_color_list[i]))
        for cat in reversed(mc_category_list):
            prestack.Add(prefit_mnvh1d_dict_uncut[fitbin][cat])
            poststack.Add(fit_mnvh1d_dict_uncut[fitbin][cat])
        tmp_data.SetMaximum(max(tmp_data.GetMaximum(),prestack.GetMaximum(),poststack.GetMaximum())*1.2)
        tmp_data.SetMarkerColor(ROOT.kBlack)
        tmp_data.SetLineColor(ROOT.kBlack)
        tmp_data.SetMarkerStyle(20)
        tmp_data.SetLineWidth(2)
        tmp_data.GetXaxis().CenterTitle()
        tmp_data.GetXaxis().SetTitle("Recoil (GeV)")
        tmp_data.GetYaxis().SetTitle("Counts / (GeV)")
        leg.AddEntry(tmp_data,"Data","p")
        tmp_data.SetTitle("prefit MC vs data fitbin%02d"%(fitbin))

        tmp_prefitmctot.SetFillColorAlpha(ROOT.kRed, 0.3)
        tmp_prefitmctot.SetLineColor(ROOT.kRed)
        tmp_prefitmctot.SetLineWidth(2)

        tmp_data.Draw("P E1 X0 same")
        prestack.Draw("HIST same")
        tmp_prefitmctot.Draw("E2 E0 same")
        tmp_data.Draw("AP E1 X0 same")
        leg.Draw()
        # prechi2_text.Modify()
        prechi2_text.SetTitle("#chi^{2} = %.2f"%(round(pre_chi2,3)))
        prechi2_text.Draw()
        prelim.Draw()
        canvas.ModifiedUpdate()
        # canvas.Print("long_prefitvsdata_fitbin%02d.png"%(fitbin))
        if fitbin==1:
            canvas.Print("long_mc_vs_data.pdf(","Title:%s"%(tmp_data.GetTitle()))
        else:
            canvas.Print("long_mc_vs_data.pdf","Title:%s"%(tmp_data.GetTitle()))

        # chi2_text.Modfiy()

        tmp_data.SetTitle("postfit MC vs data fitbin%02d"%(fitbin))
        tmp_fitmctot.SetFillColorAlpha(ROOT.kRed, 0.3)
        tmp_fitmctot.SetLineColor(ROOT.kRed)
        tmp_fitmctot.SetLineWidth(2)

        tmp_data.Draw("P E1 X0 same")
        poststack.Draw("HIST same")
        tmp_fitmctot.Draw("E2 E0 same")
        tmp_data.Draw("AP E1 X0 same")
        leg.Draw()
        postchi2_text.SetTitle("#chi^{2} = %.2f"%(round(post_chi2,3)))
        postchi2_text.Draw()
        prelim.Draw()

        canvas.Modified()
        canvas.Update()
        # canvas.Print("long_postfitvsdata_fitbin%02d.png"%(fitbin))
        if fitbin < n_xbins:    
            canvas.Print("long_mc_vs_data.pdf","Title:%s"%(tmp_data.GetTitle()))
        else:
            canvas.Print("long_mc_vs_data.pdf)","Title:%s"%(tmp_data.GetTitle()))
        print("")


    # gc.enable()
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
            # tmp_areascale = tmp_data.Integral(min_bin, max_xbin)/tmp_fitmctot.Integral(min_bin, max_xbin)
            # tmp_fitmctot.Scale(tmp_areascale)

            tmp_data_rebin = tmp_data.Clone()
            tmp_prefitmctot_rebin = tmp_prefitmctot.Clone()
            tmp_fitmctot_rebin = tmp_fitmctot.Clone()
            if not dorebin_internal_global:
                print("Hists have not been rebinned yet. Doing it now for comparisons.")
                tmp_rebin = rebin
                if (sample == "QElike" or sample == 0) and rebin%2 == 0 and doqelikerebin:
                    tmp_rebin = int(rebin/2)
                tmp_data_rebin.Rebin(tmp_rebin)
                tmp_prefitmctot_rebin.Rebin(tmp_rebin)
                tmp_fitmctot_rebin.Rebin(tmp_rebin)
            else:
                print("Hists have already been rebinned, so I won't do that over again.")

            # pre_chi2 = plotter.Chi2DataMC(tmp_data_rebin,tmp_prefitmctot_rebin)
            # post_chi2 = plotter.Chi2DataMC(tmp_data_rebin,tmp_fitmctot_rebin)
            pre_chi2 = plotter.Chi2DataMC(
                tmp_data_rebin,
                tmp_prefitmctot_rebin,
                ctypes.c_int(tmp_data_rebin.GetNbinsX()),
                ctypes.c_double(1.0),
                # False,
                # False,
                # True,
                # None,
            )
            post_chi2 = plotter.Chi2DataMC(
                tmp_data_rebin,
                tmp_fitmctot_rebin,
                ctypes.c_int(tmp_data_rebin.GetNbinsX()),
                ctypes.c_double(1.0),
                # False,
                # False,
                # True,
                # None,
            )
            print("%s\t>>>>>>>>> REBIN\tprefit: %f \t postfit: %f \t delta: %f"%(sample_list[sample],pre_chi2,post_chi2,post_chi2-pre_chi2))

            tmp_prefitmctot_orig = prefit_mnvh1d_dict_shortlist[fitbin]["mctot"][sample].Clone()
            # tmp_prefitmctot_orig.SetLineColor(ROOT.kRed)
            tmp_fitmctot_orig = fit_mnvh1d_dict_shortlist[fitbin]["mctot"][sample].Clone()
            # tmp_fitmctot_orig.SetLineColor(ROOT.kRed)

            # pre_chi2_orig = plotter.Chi2DataMC(tmp_data,tmp_prefitmctot_orig)
            # post_chi2_orig = plotter.Chi2DataMC(tmp_data,tmp_fitmctot_orig)
            pre_chi2_orig = plotter.Chi2DataMC(
                tmp_data,
                tmp_prefitmctot_orig,
                ctypes.c_int(tmp_data.GetNbinsX()),
                ctypes.c_double(1.0),
                # False,
                # False,
                # True,
                # None,
            )
            post_chi2_orig = plotter.Chi2DataMC(
                tmp_data,
                tmp_fitmctot_orig,
                ctypes.c_int(tmp_data.GetNbinsX()),
                ctypes.c_double(1.0),
                # False,
                # False,
                # True,
                # None,
            )
            print("%s\t>>>>>>>>> ORIG\tprefit: %f \t postfit: %f \t delta: %f"%(sample_list[sample],pre_chi2_orig,post_chi2_orig,post_chi2_orig-pre_chi2_orig))
            
            ROOT.gStyle.SetOptTitle(1)

            canvas = ROOT.TCanvas()
            prestack = ROOT.THStack()
            poststack = ROOT.THStack()
            legleft = 0.0
            if sample == 3:
                legleft = -0.4
            leg = ROOT.TLegend(0.65+legleft,0.65,0.8+legleft,0.9)
            leg.SetTextFont(42)
            leg.SetTextSize(0.04)
            leg.SetBorderSize(0)
            leg.SetFillColor(-1)

            chi2_text = ROOT.TLatex()
            chi2_text.SetNDC()
            chi2_text.SetTextSize(0.03)
            chi2_text.SetTextAlign(11)
            chi2_text.SetTextFont(42)
            for i in range(len(mc_category_list)):
                prefit_mnvh1d_dict_shortlist[fitbin][mc_category_list[i]][sample].SetFillColor(mc_cat_color_list[i])
                prefit_mnvh1d_dict_shortlist[fitbin][mc_category_list[i]][sample].SetLineColor(ROOT.kBlack)
                leg.AddEntry(prefit_mnvh1d_dict_shortlist[fitbin][mc_category_list[i]][sample],mc_cat_name_list[mc_category_list[i]])
                prestack.Add(prefit_mnvh1d_dict_shortlist[fitbin][mc_category_list[i]][sample])
                fit_mnvh1d_dict_shortlist[fitbin][mc_category_list[i]][sample].SetFillColor(mc_cat_color_list[i])
                fit_mnvh1d_dict_shortlist[fitbin][mc_category_list[i]][sample].SetLineColor(ROOT.kBlack)
                poststack.Add(fit_mnvh1d_dict_shortlist[fitbin][mc_category_list[i]][sample])
            # data_hist.SetMaximum(stack.GetMaximum())
            tmp_data.SetMarkerColor(ROOT.kBlack)
            tmp_data.SetLineColor(ROOT.kBlack)
            tmp_data.SetLineWidth(2)
            tmp_data.SetMarkerStyle(20)
            loedge = dummy_scalevar_th1d.GetXaxis().GetBinLowEdge(int(fitbin))
            hiedge = dummy_scalevar_th1d.GetXaxis().GetBinUpEdge(int(fitbin))
            tmp_data.SetMaximum(max(tmp_data.GetMaximum(),prestack.GetMaximum(),poststack.GetMaximum())*1.2)
            # tmp_data.SetTitle("%s prefit MC vs data fitbin%02d"%(sample_list[sample],fitbin))
            # tmp_data.SetTitle("%s prefit MC vs data %02f < Q^{2}_{QE} < %02f"%(sample_list[sample],loedge,hiedge))
            pre_title = "Prefit, "+str(loedge)+" < Q^{2}_{QE} <"+str(hiedge)
            tmp_data.SetTitle(pre_title)
            prefitband = tmp_prefitmctot_orig.GetCVHistoWithError(True,False)
            prefitband.SetFillColorAlpha(ROOT.kRed, 0.3)
            prefitband.SetLineColor(ROOT.kRed)
            prefitband.SetLineWidth(2)

            leg.AddEntry(tmp_data,"Data","p")

            tmp_data.Draw("P E1 X0")
            prestack.Draw("HIST same")
            prefitband.Draw("E2 E0 same")
            tmp_data.Draw("AP E1 X0 same")
            leg.Draw()
            chi2_text.DrawLatex(0.65+legleft,0.6, "#chi^{2} = %.2f"%(round(pre_chi2,3)))
            prelim.DrawLatex(0.65+legleft, 0.5, "MINER#it{#nu}A Work in Progress")

            canvas.Print("%s_prefitvsdata_fitbin%02d.png" %(sample_list[sample],fitbin))
            if fitbin == 1:
                canvas.Print("%s_mc_vs_data.pdf("%(sample_list[sample]),"Title:%s"%(tmp_data.GetTitle()))
            else:
                canvas.Print("%s_mc_vs_data.pdf"%(sample_list[sample]),"Title:%s"%(tmp_data.GetTitle()))

            post_title = "Postfit, "+str(loedge)+" < Q^{2}_{QE} <"+str(hiedge)
            tmp_data.SetTitle(post_title)

            fitband = tmp_fitmctot_orig.GetCVHistoWithError(True,False)
            fitband.SetFillColorAlpha(ROOT.kRed, 0.3)
            fitband.SetLineColor(ROOT.kRed)
            fitband.SetLineWidth(2)

            tmp_data.Draw("P E1 X0")
            poststack.Draw("HIST same")
            fitband.Draw("E2 E0 same")
            tmp_data.Draw("AP E1 X0 same")
            leg.Draw()
            chi2_text.DrawLatex(0.65+legleft,0.6, "#chi^{2} = %.2f"%(round(post_chi2,3)))
            prelim.DrawLatex(0.45+legleft, 0.57, "MINER#it{#nu}A Work in Progress")

            canvas.Modified()
            canvas.Update()
            canvas.Print("%s_postfitvsdata_fitbin%02d.png" %(sample_list[sample],fitbin))
            if fitbin < n_xbins:
                canvas.Print("%s_mc_vs_data.pdf"%(sample_list[sample]),"Title:%s"%(tmp_data.GetTitle()))
            else:
                canvas.Print("%s_mc_vs_data.pdf)"%(sample_list[sample]),"Title:%s"%(tmp_data.GetTitle()))

            print("")
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
        scalefrac_mnvh1d_dict[category]["fitfrac"].Write()
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
