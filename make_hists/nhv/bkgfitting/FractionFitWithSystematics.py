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
# sample_list = ["Background"]
sample = "Background"
sample_list = [sample]
# DO_SYSTEMATICS = False
# DRAW = True
# CONFINT = True

# This is based off of how fitbins are made (i.e. making sidebands that have
# cuts on binedges of the variable you're making), and the histogram naming
# convention CCQENuMAT

# recoil_type = "Log10recoil"
recoil_type = "recoil"


def GetDataMCMnvH2D(rfile, category_list, sample, useTuned=0):
    # Make a dictionary of the histos for fitting.
    # Requires CCQENuMAT naming convention for hists.
    print("Before GetDataMCMnvH2D")
    histkeys_list = rfile.GetListOfKeys()
    print("After GetListOfKeys")
    datafound = 0
    qelikefound = 0
    qeliketunedfound = 0
    qelikenotfound = 0
    qelikenottunedfound = 0
    for histkey in histkeys_list:
        hist_name = histkey.GetName()
        print(hist_name)
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
        # if histovariable != 'Q2QE_recoil':
        if histovariable != 'Q2QE_'+recoil_type:
            continue
        # Only grab data and qelike & qelikenot MC reco
        histocategory = str(splitnames_list[2])
        if not histocategory in ['data', 'qelike', 'qelikenot']:
            continue

        if useTuned>0:
            if 'tuned' not in splitnames_list[4]:
                if histocategory!='data':
                        continue

        if histocategory == 'data':
            data_hist2D = rfile.Get(hist_name).Clone()
            datafound = 1
        if histocategory == 'qelike':
            if 'tuned' not in splitnames_list[4]:
                qelike_hist2d = rfile.Get(hist_name).Clone()
                qelikefound = 1
            else:
                # qelike_hist2d_tuned = rfile.Get(hist_name).Clone()
                qeliketunedfound = 1
        if histocategory == 'qelikenot':
            if 'tuned' not in splitnames_list[4]:
                qelikenot_hist2d = rfile.Get(hist_name).Clone()
                qelikenotfound = 1
            else:
                # qelikenot_hist2d_tuned = rfile.Get(hist_name).Clone()
                qelikenottunedfound = 1
        print("Before if found check")
        if datafound == 1 and qelikefound == 1 and qelikenotfound == 1: #and qeliketunedfound == 1 and qelikenottunedfound == 1:
            print("Looking at hist: ",hist_name)
            return data_hist2D, qelike_hist2d, qelikenot_hist2d#, qelike_hist2d_tuned, qelikenot_hist2d_tuned
        else:
            continue


    if datafound + qelikefound + qelikenotfound < 3:
        print("Error: Could not find the required histograms in the input file.")
        sys.exit()

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

def InitializeCanvas(canvas_name):
    # Initialize a pdf canvas for making plots
    canvas = ROOT.TCanvas(str(canvas_name + ".pdf"))

    canvas.cd()
    canvas.SetLeftMargin(0.1)
    canvas.SetRightMargin(0.07)
    canvas.SetBottomMargin(0.11)
    canvas.SetTopMargin(0.1)
    # Each canvas needs a closing statement to match this Print
    # TODO: Make this a class that handles opening/closing
    # canvas.Print(str(canvas_name + ".pdf["), "pdf")
    return canvas

def InitializeLegend(twocolumns=False):
    legend = ROOT.TLegend(0.95, 0.9, 0.65, 0.65)

    legend.SetBorderSize(1)
    if twocolumns:
        legend.SetNColumns(2)

    # legend.SetLegendTextSize(1)
    return legend


def MakeDataMCPlotPretty(data_hist, qelike_hist, qelikenot_hist, title_suffix):
    ROOT.gStyle.SetOptStat(0)

    data_hist.SetMarkerStyle(20)
    data_hist.SetMarkerColor(ROOT.kBlack)
    data_hist.SetLineColor(ROOT.kBlack)
    data_hist.GetXaxis().SetTitle("Recoil (GeV)")
    data_hist.GetXaxis().CenterTitle()
    data_hist.GetXaxis().SetTitleSize(0.1)
    data_hist.GetYaxis().SetTitle("Number of Events")
    data_hist.GetYaxis().CenterTitle()
    data_hist.GetYaxis().SetTitleSize(0.1)

    # data_hist.SetTitle("Total Data")

    qelike_hist.SetFillStyle(3224)
    qelike_hist.SetLineColor(ROOT.kBlue)
    qelike_hist.SetFillColor(ROOT.kBlue)
    qelike_hist.SetTitle("QELike")

    qelikenot_hist.SetFillStyle(3225)
    qelikenot_hist.SetLineColor(ROOT.kRed)
    qelikenot_hist.SetFillColor(ROOT.kRed)
    qelikenot_hist.SetTitle("QELikeNot")
    qelikenot_hist.GetXaxis().SetTitle("Recoil (GeV)")
    qelikenot_hist.GetXaxis().CenterTitle()
    qelikenot_hist.GetXaxis().SetTitleSize(0.1)


def MakeDataMCPlot(canvas, title, i_data_hist, i_qelike_hist, i_qelikenot_hist, chi2, ndf, logx=False, logy=False, fit_chi2=0, mcprediction=False):

    data_hist = i_data_hist.Clone()
    qelike_hist = i_qelike_hist.Clone()
    qelikenot_hist = i_qelikenot_hist.Clone()

    legend = InitializeLegend(True)

    tmp_title = title
    title_suffix = ''
    if fit_chi2 == 0:
        title_suffix = ' prefit'
    else:
        if mcprediction:
            title_suffix = ' from fit'
        else:
            title_suffix = ' scaled'
    tmp_title += "," + title_suffix
    name = tmp_title.replace(" ", "_")

    MakeDataMCPlotPretty(data_hist, qelike_hist, qelikenot_hist, title_suffix)

    # stack_title = tmp_title + "; Recoil (GeV); Counts"
    stack = ROOT.THStack("mc_stack", tmp_title)
    stack.Add(qelikenot_hist)
    stack.Add(qelike_hist)
    qelikenot_min = qelikenot_hist.GetMinimum()
    # if qelikenot_min <= 10.0:
    stack.SetMinimum(qelikenot_min)

    fit_chi2_label = ''
    chi2_label = 'Hist \chi^{2} = ' + str("{:.2f}".format(chi2))
    ndf_label = 'NDF = ' + str(ndf)

    if fit_chi2 > 0:
        fit_chi2_label = 'Fit \chi^{2} = ' + str("{:.2f}".format(fit_chi2))

    legend.AddEntry(data_hist, "Total Data")
    legend.AddEntry("fit_chi2",fit_chi2_label,"")
    legend.AddEntry(qelike_hist, "QELike")
    legend.AddEntry("chi2", chi2_label, "")
    legend.AddEntry(qelikenot_hist, "QELikeNot")
    legend.AddEntry("ndf", ndf_label, "")


    xtext = ROOT.TText(0.5,0.045,"Recoil (GeV)")
    xtext.SetNDC(1)
    xtext.SetTextSize(0.05)
    xtext.SetTextAlign(22)
    xtext.SetTextFont(42)

    ytext =ROOT.TText(0.03,0.5,"Number of Events")
    ytext.SetNDC(1)
    ytext.SetTextSize(0.05)
    ytext.SetTextAngle(90)
    ytext.SetTextAlign(22)
    ytext.SetTextFont(42)

    if logx:
        ROOT.gPad.SetLogx(1)
    else:
        ROOT.gPad.SetLogx(0)
    if logy:
        ROOT.gPad.SetLogy(1)
    else:
        ROOT.gPad.SetLogy(0)
    # ROOT.gPad.SetLogy(1)

    stack_max = stack.GetMaximum()
    data_max = 1.1 * data_hist.GetMaximum()

    if stack_max <= data_max:
        stack.SetMaximum(data_max)
    stack.SetTitle(tmp_title)
    stack.Draw("HIST")
    # stack.GetXaxis().SetTitle("Recoil (GeV)")
    # stack.GetXaxis().CenterTitle()
    # stack.GetXaxis().SetTitleSize(0.1)
    # stack.GetYaxis().SetTitle("Number of Events")
    # stack.GetYaxis().CenterTitle()
    # stack.GetYaxis().SetTitleSize(0.1)
    # canvas.Update()
    data_hist.Draw("same,PE1")
    legend.Draw("same")
    xtext.Draw("same")
    ytext.Draw("same")
    # canvas.BuildLegend(0.77, 0.75, 0.98, 0.6)

    canvas.Print(canvas.GetName(), str("Title: " + name))

    # canvas.Print(canvas.GetName(),"Title: Recoil")
    # ROOT.gPad.SetLogx(0)
    # ROOT.gPad.SetLogy(0)

def MakeFitRatioPlot(canvas, title, i_data_hist, i_mctot_hist, i_fit_mctot_hist, logx=False,logy=False):
    # canvas.cd(2)
    ROOT.gStyle.SetOptStat(0)

    legend = ROOT.TLegend(0.35, 0.15, 0.14, 0.3)
    legend.SetBorderSize(1)

    tmp_title = title + ", Data/MC Ratio"
    name = tmp_title.replace(" ", "_")

    data_hist = i_data_hist.Clone()
    mctot_hist = i_mctot_hist.Clone()
    fit_mctot_hist = i_fit_mctot_hist.Clone()

    before_ratio = data_hist.Clone()
    before_ratio.Divide(data_hist, mctot_hist, 1.0, 1.0, "B")
    # before_ratio = mctot_hist.Clone()
    # before_ratio.Divide(mctot_hist, data_hist, 1.0, 1.0, "B")
    before_ratio.SetTitle(tmp_title)
    before_ratio.GetYaxis().SetTitle("Data/MC")
    before_ratio.GetYaxis().CenterTitle()
    before_ratio.GetXaxis().SetTitle("Recoil (GeV)")
    before_ratio.GetXaxis().SetTitleSize(0.05)


    before_ratio.GetXaxis().CenterTitle()
    before_ratio.SetMarkerColor(ROOT.kRed)
    before_ratio.SetLineColor(ROOT.kRed)
    before_ratio.SetMarkerStyle(ROOT.kFullCircle)
    legend.AddEntry(before_ratio, "Before Fit", "p")

    after_ratio = data_hist.Clone()
    after_ratio.Divide(data_hist, fit_mctot_hist, 1.0, 1.0, "B")
    # after_ratio = fit_mctot_hist.Clone()
    # after_ratio.Divide(fit_mctot_hist, data_hist, 1.0, 1.0, "B")
    after_ratio.SetMarkerColor(ROOT.kBlue)
    after_ratio.SetLineColor(ROOT.kBlue)
    after_ratio.SetMarkerStyle(ROOT.kFullSquare)
    legend.AddEntry(after_ratio, "After Fit", "p")

    max_before = before_ratio.GetMaximum()
    min_before = before_ratio.GetMinimum()
    max_after = after_ratio.GetMaximum()
    min_after = after_ratio.GetMinimum()

    if max_after >= max_before:
        max = max_after
    else:
        max = max_before
    if min_after <= min_before:
        min = min_after
    else:
        min = min_before

    maxdiff = max - 1.0
    mindiff = 1.0 - min

    if maxdiff >= mindiff:
        before_ratio.SetMaximum(1 + (1.5 * maxdiff))
        before_ratio.SetMinimum(1 - (1.5 * maxdiff))
    else:
        before_ratio.SetMaximum(1 + (1.5 * mindiff))
        before_ratio.SetMinimum(1 - (1.5 * mindiff))

    if logx:
        ROOT.gPad.SetLogx(1)
    else:
        ROOT.gPad.SetLogx(0)
    if logy:
        ROOT.gPad.SetLogy(1)
    else:
        ROOT.gPad.SetLogy(0)

    before_ratio.Draw("PE1")
    after_ratio.Draw("PE1,same")

    line = ROOT.TLine(0, 1., 0.5, 1.)
    line.SetLineStyle(2)
    line.SetLineWidth(3)
    line.SetLineColor(36)

    line.Draw("same")

    legend.Draw("same")

    canvas.Print(canvas.GetName(), str("Title: " + name))

    ROOT.gPad.SetLogx(0)
    ROOT.gPad.SetLogy(0)


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


def MakeMCandScale2D(i_data_hist, qelike_hist, qelikenot_hist):
    data_hist = i_data_hist.Clone()

    # Make total MC hist by adding qelike, qelikenot
    mctot_hist = qelike_hist.Clone("mc")
    mctot_hist.Add(qelikenot_hist, 1.0)

    # Make area scale for MC hists. Don't include underflow & overflow bins
    min_bin = 1
    max_xbin = data_hist.GetNbinsX()
    max_ybin = data_hist.GetNbinsY()
    # area_scale = (data_hist.Integral(min_bin, max_xbin, min_bin, max_ybin)) / (mctot_hist.Integral(min_bin, max_xbin, min_bin, max_ybin))

    # Scale MC hists to area normalize them to Data (so # counts is the same)
    mctot_hist.Scale(area_scale)
    qelike_hist.Scale(area_scale)
    qelikenot_hist.Scale(area_scale)

    return qelike_hist, qelikenot_hist, mctot_hist

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
    min_bin = 6
    mc_int = i_mctot_hist.Integral(min_bin, i_mctot_hist.GetNbinsX())
    qelike_int = i_sig_hist.Integral(min_bin, i_sig_hist.GetNbinsX())
    qelikenot_int = i_bkg_hist.Integral(min_bin, i_bkg_hist.GetNbinsX())

    sig_frac = qelike_int / mc_int
    bkg_frac = qelikenot_int / mc_int
    return sig_frac, bkg_frac


def RunFractionFitter(i_mctot_hist, i_qelike_hist, i_qelikenot_hist, i_data_hist):
    mctot_hist = i_mctot_hist.Clone()
    qelike_hist = i_qelike_hist.Clone()
    qelikenot_hist = i_qelikenot_hist.Clone()
    data_hist = i_data_hist.Clone()

    # Get some info for some calculations
    min_bin = 6
    max_bin = mctot_hist.GetNbinsX()

    print(">>>>>>>>>max_bin ", max_bin)

    # Calculate & store pre-fit fractions of MC samples.
    prefit_sig_frac, prefit_bkg_frac = GetSigBkgFrac(
        mctot_hist, qelike_hist, qelikenot_hist)

    # Make a list of the MC hists for the fitter...
    mc_list = ROOT.TObjArray(2)
    mc_list.append(qelike_hist)
    mc_list.append(qelikenot_hist)

    # Get bin width for "step size" of fit
    x_max = mctot_hist.GetXaxis().GetXmax()
    x_min = mctot_hist.GetXaxis().GetXmin()
    # binwid = (x_max-x_min) / ((max_bin-min_bin)+1)
    # print(">>>>>>>>>binwid ",binwid)
    # Set up fitter in verbose mode
    fit = ROOT.TFractionFitter(data_hist, mc_list, "V")
    virtual_fitter = fit.GetFitter()
    # Configure the fit for the qelike hist
    # virtual_fitter.Config().ParSettings(0).Set('qelike', prefit_sig_frac, binwid, 0.0, 1.0)
    virtual_fitter.Config().ParSettings(0).Set('qelike', prefit_sig_frac, 0.02, 0.0, 1.0) #Switched step size to be the bin width of 25 recoil bins
    # Confgure the fit for the qelikenot hist
    # virtual_fitter.Config().ParSettings(1).Set('qelikenot', prefit_bkg_frac, binwid, 0.0, 1.0)
    virtual_fitter.Config().ParSettings(1).Set('qelikenot', prefit_bkg_frac, 0.02, 0.0, 1.0)
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
    dummy_q2_mnvh1d, dummy_q2_th1d = GetDummyHistCV(infile)

    dummy_recoil_mnvh1d, dummy_recoil_th1d = GetDummyHistCV(
        infile, "___"+recoil_type+"___")
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
