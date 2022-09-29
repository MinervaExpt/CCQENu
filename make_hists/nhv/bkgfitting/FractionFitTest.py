import ROOT
from PlotUtils import MnvH1D, MnvH2D
import os
import sys
import math
import ctypes
import json
import numpy as np
import time

# Filename
_filename = "BkgStudy_BkgStudy_1.root"
# names associated with each category: data for full data, qelike for MC signal, qelikenot for MC bkg
category_list = ["data", "qelike", "qelikenot"]
# names associated with each "sample" e.g. QElike, QElikeALL
sample_list = ["QElike", "QElike_hiE", "QElike_loE"]

stack_plot_name = "OutHistsTest"

DO_SYSTEMATICS = False
DRAW = True
CONFINT = True

# This is based off of how fitbins are made (i.e. making sidebands that have
# cuts on binedges of the variable you're making), and the histogram naming
# convention CCQENuMAT


def MakeHistDict(rfile, category_list, sample):
    # Make a dictionary of the histos for fitting.
    # Requires CCQENuMAT naming convention for hists.
    hist_dict = {}
    histkeys_list = rfile.GetListOfKeys()
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
        # Only grab data and qelike & qelikenot MC reco
        histocategory = str(splitnames_list[2])
        if not histocategory in ['data', 'qelike', 'qelikenot']:
            continue
        # Only grab recoil vs. Q2QE 2D hists
        histovariable = str(splitnames_list[3])
        if histovariable != 'Q2QE_recoil':
            continue


        # Grab the MnvH2D
        hist = rfile.Get(hist_name).Clone()
        n_xbins = hist.GetNbinsX()
        nevents = hist.GetEntries()
        print("Number of events for ", histocategory, ": ", nevents)


        # Loop over each of the Q2QE bins
        for fitbin in range(1, n_xbins + 1):
            fitbin_name = "Q2bin" + str("%02d" % (fitbin))
            mnvh_name = fitbin_name + '_' + histocategory
            # Project a single Q2QE bin along recoil resulting in a 1D recoil
            # distribution for events in that Q2QE bin, stored as an MnvH1D
            mnvh = hist.ProjectionY(mnvh_name, fitbin, fitbin, "e")

            # Rebin from 50 -> 25 fixed width bins
            # mnvh = mnvh.Rebin(2)

            # Start organizing hists by their category (qelike, qelikenot, etc.)
            if fitbin_name in hist_dict:
                if histocategory in hist_dict[fitbin_name]:
                    print(histocategory, " already in ", fitbin_name)
                else:
                    hist_dict[fitbin_name][histocategory] = {
                        "name": mnvh_name, "MnvH1D": mnvh, "hists": None}
            else:
                hist_dict[fitbin_name] = {histocategory: {
                    "name": mnvh_name, "MnvH1D": mnvh, "hists": None}}
    return hist_dict, hist


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
            dummyhist_cv = rfile.Get(hist_name).GetCVHistoWithStatError().Clone()
            # Clears hist, leaves only binning
            dummyhist_cv.Reset("ICES")
            return dummyhist_cv
    print("No suitable hist to make a dummy with. Exiting...")
    sys.exit()

# def InitializeOutHists(infile):
def InitializeChi2Hists(infile):
    # Set up hists (chi2 and scale factor) that are plotted in Q2QE
    dummyhist_q2 = GetDummyHistCV(infile)

    # The ICES option clears out the hists, but leaves the binning
    before_chi2_hist = dummyhist_q2.Clone()
    before_chi2_hist.Reset("ICES")
    after_chi2_hist = dummyhist_q2.Clone()
    after_chi2_hist.Reset("ICES")
    # sig_scale_hist = dummyhist_q2.Clone()
    # sig_scale_hist.Reset("ICES")
    # bkg_scale_hist = dummyhist_q2.Clone()
    # bkg_scale_hist.Reset("ICES")

    # Clean up dummy hist
    del dummyhist_q2

    return before_chi2_hist, after_chi2_hist, sig_scale_hist, bkg_scale_hist




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
    canvas.Print(str(canvas_name + ".pdf["), "pdf")
    return canvas


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


def RebinRecoil(i_hist, n_lobins_merge=0, n_highbins_merge=0):
    hist = i_hist.Clone()
    xmax = hist.GetXaxis().GetXmax()
    xmin = hist.GetXaxis().GetXmin()
    n_bins = hist.GetNbinsX()
    binwid = xmax / n_bins
    # print(binwid)
    if n_lobins_merge == 0:
        return i_hist
    hi_edge_lobin = n_lobins_merge * binwid
    xbins_start = np.array((xmin, hi_edge_lobin))
    xbins_rest = np.arange(hi_edge_lobin + binwid, xmax + binwid, binwid)
    xbins = np.concatenate((xbins_start, xbins_rest), axis=None)
    o_hist = hist.Rebin(len(xbins) - 1, "new", xbins)
    del hist
    return o_hist


def MakeMCandScale(fitbinhist_dict):
    qelike_hist = fitbinhist_dict['qelike']['MnvH1D'].Clone()
    qelikenot_hist = fitbinhist_dict['qelikenot']['MnvH1D'].Clone()
    data_hist = fitbinhist_dict['data']['MnvH1D'].Clone()

    # Make total MC hist by adding qelike, qelikenot
    mctot_hist = qelike_hist.Clone("mc")
    mctot_hist.Add(qelikenot_hist, 1.0)
    fitbinhist_dict['mc'] = {'MnvH1D': mctot_hist, 'hists': None}

    # Make area scale for MC hists. Don't include underflow & overflow bins
    min_bin = 1
    max_dbin = data_hist.GetNbinsX()
    max_mcbin = mctot_hist.GetNbinsX()
    area_scale = (data_hist.Integral(min_bin, max_dbin))/ (mctot_hist.Integral(min_bin, max_mcbin))

    # Scale MC hists to area normalize them to Data (so # counts is the same)
    fitbinhist_dict['mc']['MnvH1D'].Scale(area_scale)
    fitbinhist_dict['qelike']['MnvH1D'].Scale(area_scale)
    fitbinhist_dict['qelikenot']['MnvH1D'].Scale(area_scale)

    del qelike_hist, qelikenot_hist, data_hist


def GetUniverseHists(fitbin_dict, mcuniverse_names, DO_SYSTEMATICS=False):
    # This needs to be seperate from making the dict, get seg fault otherwise
    # Loop over qelike, qelikenot, data, mctot
    for sample in fitbin_dict.keys():
        tmp_dict = {}
        # Put CV universe in dict
        cv_hist = fitbin_dict[sample]['MnvH1D'].GetCVHistoWithStatError()
        tmp_dict['cv'] = [cv_hist]
        # Loop over systematic universes, switch for DO_SYSTEMATICS at top
        if sample != 'data' and DO_SYSTEMATICS == True:
            for name in mcuniverse_names:
                n_universes = fitbin_dict[sample]['MnvH1D'].GetVertErrorBand(
                    name).GetNHists()
                tmp_unihist_list = []
                for i in range(0, n_universes):
                    uni_hist = fitbin_dict[sample]['MnvH1D'].GetVertErrorBand(name).GetHist(i).Clone()
                    tmp_unihist_list.append(uni_hist)
                tmp_dict[name] = tmp_unihist_list
        fitbin_dict[sample]['hists'] = tmp_dict
    return fitbin_dict


def RunFractionFitter(i_mctot_hist, i_qelike_hist, i_qelikenot_hist, i_data_hist):
    mctot_hist = i_mctot_hist.Clone()
    qelike_hist = i_qelike_hist.Clone()
    qelikenot_hist = i_qelikenot_hist.Clone()
    data_hist = i_data_hist.Clone()

    # Get some info for some calculations
    min_bin = 1
    max_bin = mctot_hist.GetNbinsX()

    # Calculate & store pre-fit fractions of MC samples.
    mc_int = mctot_hist.Integral(min_bin,max_bin)
    qelike_int = qelike_hist.Integral(min_bin,max_bin)
    qelikenot_int = qelikenot_hist.Integral(min_bin,max_bin)

    qelike_frac = qelike_int / mc_int
    qelikenot_frac = qelikenot_int / mc_int

    frac_dict = {'qelike': qelike_frac,
                 'qelikenot': qelikenot_frac}

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
        'qelike', frac_dict['qelike'], binwid, 0.0, 1.0)
    # Confgure the fit for the qelikenot hist
    virtual_fitter.Config().ParSettings(1).Set(
        'qelikenot', frac_dict['qelikenot'], binwid, 0.0, 1.0)
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
        return fit, frac_dict
    if status == 0:
        print("Fit converged.")
        return fit, frac_dict


def CalculateScaleFactor(fit, frac_dict, sample='qelikenot'):
    prefit_frac = frac_dict[sample]

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
    return scale, scale_err

    # TODO: Systematics.
    # Idea: Find scale factor for all universes,then combine to make a scale
    # factor MnvH1D? Only need to find stat error for just CV, not for the
    # systematic universes.


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

    ROOT.gPad.SetLogx(0)
    ROOT.gPad.SetLogy(0)


def Plot2D(canvas,i_mc_hist):
    ROOT.gPad.SetLogx(1)
    ROOT.gPad.SetLogz(1)
    ROOT.gStyle.SetOptStat("e")
    # stats_pave = i_mc_hist.FindObject("stats")

    i_mc_hist.SetTitle("Recoil vs. Q^{2}_{QE}")
    i_mc_hist.GetXaxis().SetTitle("Q^{2}_{QE} (GeV^{2})")
    i_mc_hist.GetXaxis().CenterTitle()

    i_mc_hist.GetYaxis().SetTitle("Recoil (GeV)")
    i_mc_hist.GetYaxis().CenterTitle()

    i_mc_hist.GetZaxis().SetTitle("Events")

    i_mc_hist.Draw("COLZ")

    canvas.Print(canvas.GetName(), str("Title: " + i_mc_hist.GetTitle()))
    ROOT.gPad.SetLogx(0)
    ROOT.gPad.SetLogz(0)


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


def MakeChi2Plot(canvas, i_before_chi2_hist, i_after_chi2_hist, ndf):
    before_chi2_hist = i_before_chi2_hist.Clone()
    after_chi2_hist = i_after_chi2_hist.Clone()

    legend = ROOT.TLegend(0.15, 0.85, 0.36, 0.7)
    legend.SetBorderSize(1)

    before_chi2_hist.SetMarkerStyle(ROOT.kFullCircle)
    before_chi2_hist.SetMarkerColor(ROOT.kRed)
    before_chi2_hist.SetLineColor(ROOT.kRed)
    before_chi2_hist.SetMarkerSize(2)
    before_chi2_hist.GetXaxis().SetTitle("Q^{2}_{QE} (GeV^{2})")
    before_chi2_hist.GetXaxis().CenterTitle()
    before_chi2_hist.GetYaxis().SetTitle("\chi^{2} / NDF")
    before_chi2_hist.GetYaxis().CenterTitle()
    before_chi2_hist.SetMinimum(0.0)
    before_chi2_hist.SetTitle("\chi^{2} / NDF Before and After Fit")
    legend.AddEntry(before_chi2_hist, "Before Fit", "p")

    after_chi2_hist.SetMarkerStyle(ROOT.kFullSquare)
    after_chi2_hist.SetMarkerColor(ROOT.kBlue)
    after_chi2_hist.SetLineColor(ROOT.kBlue)
    after_chi2_hist.SetMarkerSize(2)
    after_chi2_hist.GetXaxis().SetTitle("Q^{2}_{QE} (GeV^{2})")
    after_chi2_hist.GetXaxis().CenterTitle()
    legend.AddEntry(after_chi2_hist, "After Fit", "p")

    ndf_label = "NDF = " + str(ndf)
    legend.AddEntry("ndf", ndf_label, "")

    ROOT.gPad.SetLogx()

    before_chi2_hist.Draw("P")
    after_chi2_hist.Draw("P,same")
    legend.Draw("same")

    canvas.Modified()

    canvas.Print(canvas.GetName(), str("Title: Chi2"))

    del before_chi2_hist, after_chi2_hist


def MakeScaleFactorPlot(canvas, i_scale_hist_dict,sample_str='',color=ROOT.kBlack):
    scale_hist = i_scale_hist_dict['hist'].Clone()
    scale_fit = i_scale_hist_dict['fit']
    fit_chi2 = i_scale_hist_dict['chi2']
    fit_ndf = i_scale_hist_dict['ndf']


    xmax = 2.0
    ROOT.gPad.SetLogx(1)

    title = "Background Scale Factor vs. Q^{2}_{QE}"
    if len(sample_str)>0:
        title_suffix = sample_str
        title += ', '+title_suffix
    scale_hist.SetTitle(title)
    scale_hist.GetXaxis().SetTitle("Q^{2}_{QE} (GeV^{2})")
    scale_hist.GetXaxis().CenterTitle()
    scale_hist.GetYaxis().SetTitle("Scale Factor")
    scale_hist.GetYaxis().CenterTitle()

    scale_hist.SetMaximum(1.2)
    scale_hist.SetMinimum(0.3)

    scale_hist.SetMarkerStyle(20)
    scale_hist.SetMarkerColor(color)
    scale_hist.SetLineColor(color)

    scale_fit.SetLineColor(color)

    confint_hist = i_scale_hist_dict['confint_hist'].Clone()
    confint_hist.SetFillColorAlpha(color, 0.2)

    line = ROOT.TLine(0, 1., xmax, 1.)
    line.SetLineStyle(2)
    line.SetLineWidth(3)
    line.SetLineColor(36)

    legend = ROOT.TLegend(0.45, 0.9, 0.2, 0.7)
    legend.SetBorderSize(1)
    legend.AddEntry(scale_hist, "Scale Factor", "p")
    legend.AddEntry(scale_fit, "Fit")

    fit_chi2_label = 'Fit \chi^{2} = ' + str("{:.2f}".format(fit_chi2))
    fit_ndf_label = 'Fit NDF = ' + str(fit_ndf)

    legend2 = ROOT.TLegend(0.7, 0.15, 0.9, 0.35)
    legend2.SetBorderSize(1)
    legend2.AddEntry("chi2", fit_chi2_label, "")
    legend2.AddEntry("NDF", fit_ndf_label, "")

    scale_hist.Draw("PE1")
    line.Draw("same")
    confint_hist.Draw("e5 same")
    scale_fit.Draw("same")
    legend.Draw("same")
    legend2.Draw("same")

    canvas.Print(canvas.GetName(), str("Title: BkgScaleFactor"))
    ROOT.gPad.SetLogx(0)

    del scale_hist


def MakeScaleCompPlot(canvas, i_h1_dict,h1_name,i_h2_dict,h2_name,h1_color=ROOT.kBlue,h2_color=ROOT.kRed):
    h1_hist = i_h1_dict['hist'].Clone()
    h2_hist = i_h2_dict['hist'].Clone()

    h1_fit = i_h1_dict['fit']
    h2_fit = i_h2_dict['fit']

    # xmin = 0.02 #0.02
    xmax = 2.0  # 1.4
    ROOT.gPad.SetLogx(1)

    h1_hist.SetTitle("Scale Factor vs. Q^{2}_{QE}: "+h1_name+", "+h2_name)
    h1_hist.GetXaxis().SetTitle("Q^{2}_{QE} (GeV^{2})")
    h1_hist.GetXaxis().CenterTitle()
    h1_hist.GetYaxis().SetTitle("Scale Factor")
    h1_hist.GetYaxis().CenterTitle()

    h1_hist.SetMarkerStyle(20)
    h1_hist.SetMarkerColor(h1_color)
    h1_hist.SetLineColor(h1_color)

    h1_fit.SetLineColor(h1_color)

    h1_hist.SetMaximum(1.2)
    h1_hist.SetMinimum(0.3)


    h2_hist.SetMarkerStyle(20)
    h2_hist.SetMarkerColor(h2_color)
    h2_hist.SetLineColor(h2_color)

    h2_fit.SetLineColor(h2_color)


    line = ROOT.TLine(0, 1., xmax, 1.)
    line.SetLineStyle(2)
    line.SetLineWidth(3)
    line.SetLineColor(36)

    h1confint_hist = i_h1_dict['confint_hist'].Clone()
    h2confint_hist = i_h2_dict['confint_hist'].Clone()
    h1confint_hist.SetFillColorAlpha(h1_color, 0.2)
    h2confint_hist.SetFillColorAlpha(h2_color, 0.2)

    legend = ROOT.TLegend(0.45, 0.9, 0.2, 0.7)
    legend.SetBorderSize(1)

    legend.AddEntry(h1_hist, h1_name)
    legend.AddEntry(h2_hist, h2_name)

    ks = h1_hist.KolmogorovTest(h2_hist)
    chi2 = h1_hist.Chi2Test(h2_hist,"CHI2")
    ndf = h1_hist.GetNbinsX() - 1
    h1_hist.Chi2Test(h2_hist,"P")

    ks_label = 'K-S GoF = ' + str("{:.4f}".format(ks))
    chi2_label = '\chi^{2} = ' + str("{:.2f}".format(chi2))
    ndf_label = 'NDF = ' + str(ndf)

    legend2 = ROOT.TLegend(0.7, 0.15, 0.9, 0.35)
    legend2.SetBorderSize(1)

    legend2.AddEntry("ks", ks_label, "")
    legend2.AddEntry("chi2",chi2_label,"")
    legend2.AddEntry("ndf",ndf_label,"")

    h1_hist.Draw("E1")
    line.Draw("same")
    h1confint_hist.Draw("e3,same")
    h1_fit.Draw("same")
    h2_hist.Draw("E1,same")
    h2confint_hist.Draw("e3,same")
    h2_fit.Draw("same")

    legend.Draw("same")
    legend2.Draw("same")

    canvas_title = "Title: ScaleComp "+h1_name+" "+h2_name
    canvas.Print(canvas.GetName(), canvas_title)
    ROOT.gPad.SetLogx(0)


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


def CleanUpHists(hist_dict):
    # Clean up any hists left behind.
    print("Cleaning up...")
    for fitbin in hist_dict.keys():
        for sample in hist_dict[fitbin].keys():
            # Sets them to None instead of deleting to avoid breaking the dict
            hist_dict[fitbin][sample]['MnvH1D'] = None
            hist_dict[fitbin][sample]['hists'] = None
    print("Done")


def main():
    # This automatically does SetDirectory(0) to all hists. Makes code faster,
    # clean up easier, and mitigates segfault.
    ROOT.TH1.AddDirectory(ROOT.kFALSE)

    # Read in a file
    timestr = time.strftime("%Y%m%d-%H%M%S")

    if len(sys.argv) < 3:
        print("python FractionFitTest.py <infile>.root <outfilename>")
    else:
        filename = sys.argv[1]
        plotfilename_base = sys.argv[2]

    # ROOT file from output of eventloop in CCQENuMAT
    infile = ROOT.TFile(filename, "READONLY")

    scale_hist_dict = {}

    # Get the binning of Q2QE
    binning = GetFitBinning(infile)
    for sample in sample_list:
        # Make dictionary of hists by sample & category from the in root file
        print("Starting on sample ", sample)
        hist_dict,hist2D = MakeHistDict(infile, category_list, sample)



        # index for which bin, used to check fitbin edges
        i_fitbin = 0

        # Initialize two of the final hists.
        # before_chi2_hist, after_chi2_hist, sig_scale_hist, bkg_scale_hist = InitializeOutHists(infile)

        before_chi2_hist = GetDummyHistCV(infile).Clone()
        after_chi2_hist = GetDummyHistCV(infile).Clone()
        sig_scale_hist = GetDummyHistCV(infile).Clone()
        bkg_scale_hist = GetDummyHistCV(infile).Clone()

        plotfilename = plotfilename_base + '_' + sample
        if sample == 'QElike':
            canvas_name=plotfilename + "_2D"
            canvas = ROOT.TCanvas(str(canvas_name + ".pdf"))

            canvas.cd()
            canvas.SetLeftMargin(0.15)
            canvas.SetRightMargin(0.15)
            canvas.SetBottomMargin(0.15)
            canvas.SetTopMargin(0.15)
            # Each canvas needs a closing statement to match this Print
            # TODO: Make this a class that handles opening/closing
            canvas.Print(str(canvas_name + ".pdf["), "pdf")
            Plot2D(canvas,hist2D)
            canvas.Print(str(canvas_name + ".pdf]"), "pdf")


        # Set up the logging for the fraction fit
        logfilebase = 'logs/log_' + plotfilename_base
        tff_logfile_name = logfilebase + '_' + \
            sample + '_fractionfits_' + timestr + '.log'
        frac_logger = printfLogger(tff_logfile_name)

        # Set up your canvas
        canvas = InitializeCanvas(plotfilename)

        for fitbin in hist_dict.keys():
            print("Starting fitbin ", fitbin)
            fitbin_loedge = binning[i_fitbin]
            fitbin_upedge = binning[i_fitbin + 1]
            # Base title for plotting later
            title = "Recoil: " + \
                str(fitbin_loedge) + \
                " GeV^{2} < Q^{2}_{QE} < " + str(fitbin_upedge) + " GeV^{2}"

            # Make a total MC hist from the qelike, qelikenot MC hists
            print("Making MC total and scaling MC hists.")
            MakeMCandScale(hist_dict[fitbin])

            # Get the TH1D for each systematic universe in the MnvH1D
            print("Pulling out universe hists...")
            mcuniverse_names = hist_dict[fitbin]['mc']['MnvH1D'].GetVertErrorBandNames()
            hist_dict[fitbin] = GetUniverseHists(
                hist_dict[fitbin], mcuniverse_names, DO_SYSTEMATICS)

            # Start writing to the log file.
            frac_logger.PrintToLog()

            print("Running Fraction fitter for ",
                  sample, " in fitbin ", fitbin)

            # No systematic universes for data, so no universes to loop over
            data_cv_hist = hist_dict[fitbin]['data']['hists']['cv'][0].Clone()

            # Loop over universes
            for mcuni_name in hist_dict[fitbin]['mc']['hists'].keys():
                for mc_uni in range(0, len(hist_dict[fitbin]['mc']['hists'][mcuni_name])):

                    # Make a copy of all the hists you need...
                    data_hist = data_cv_hist.Clone()
                    mctot_hist = hist_dict[fitbin]['mc']['hists'][mcuni_name][mc_uni].Clone()
                    qelike_hist = hist_dict[fitbin]['qelike']['hists'][mcuni_name][mc_uni].Clone()
                    qelikenot_hist = hist_dict[fitbin]['qelikenot']['hists'][mcuni_name][mc_uni].Clone()

                    # Calculate Chi2 between data & MC before the fit.
                    before_chi2 = data_hist.Chi2Test(mctot_hist,"CHI2")
                    before_ndf = data_hist.GetNbinsX()-1

                    # fit is TFractionFitter, will be the output of the fit
                    # frac_dict is a dictionary of the fractions (with stat
                    # error) before the fit
                    fit, frac_dict = RunFractionFitter(
                        mctot_hist, qelike_hist, qelikenot_hist, data_cv_hist)

                    # Calculate scale factors
                    qelike_scale, qelike_scale_err = CalculateScaleFactor(fit, frac_dict, 'qelike')
                    qelikenot_scale, qelikenot_scale_err = CalculateScaleFactor(fit, frac_dict, 'qelikenot')

                    # Make a scaled qelike hist using the fit
                    scale_qelike_rechist = qelike_hist.Clone()
                    recoil_nbins = scale_qelike_rechist.GetNbinsX()
                    # This includes underflow (0) and overflow (n_bins+1) bins,
                    # however the fit excludes these bins.
                    for bin in range(0, recoil_nbins + 2):
                        scale_qelike_rechist.SetBinContent(bin, qelike_scale)
                        scale_qelike_rechist.SetBinError(bin, qelike_scale_err)
                    corr_qelike_rechist = qelike_hist.Clone()
                    corr_qelike_rechist.Multiply(scale_qelike_rechist)

                    # Make a scaled qelikenot hist using the fit
                    scale_qelikenot_hist = qelikenot_hist.Clone()
                    for bin in range(0, recoil_nbins + 2):
                        scale_qelikenot_hist.SetBinContent(bin, qelikenot_scale)
                        scale_qelikenot_hist.SetBinError(bin, qelikenot_scale_err)
                    corr_qelikenot_rechist = qelikenot_hist.Clone()
                    corr_qelikenot_rechist.Multiply(scale_qelikenot_hist)

                    # Make a total MC hist from scaled qelike, qelikenot hists
                    corr_mctot_hist = corr_qelike_rechist.Clone()
                    corr_mctot_hist.Add(corr_qelikenot_rechist, 1.0)

                    # This is the normal chi2 for two TH1D's to measure goodness
                    # of fit of the scaled MC to data
                    corr_chi2 = data_hist.Chi2Test(corr_mctot_hist,"CHI2")
                    corr_ndf = data_hist.GetNbinsX()-1

                    # These are the predictions from the fit of each sample. They
                    # are not totally correct, since TFracFit changes the shape.
                    pred_qelike_hist = fit.GetMCPrediction(0)
                    pred_qelikenot_hist = fit.GetMCPrediction(1)

                    pred_mctot_hist = pred_qelike_hist.Clone()
                    pred_mctot_hist.Add(pred_qelikenot_hist,1.0)

                    # This is the chi2 of the predicted histograms
                    pred_chi2 = data_hist.Chi2Test(pred_mctot_hist,"CHI2")
                    pred_ndf = data_hist.GetNbinsX()-1

                    # This gives you the chi2 from the fit.
                    fit_chi2 = fit.GetChisquare()
                    # Our fit parameters are totally correllated, so we add back 1.
                    fit_ndf = fit.GetNDF() + 1


                    print("Entries: Data: ", data_hist.Integral(), " MC: Before: ",
                          mctot_hist.Integral(), " After: ", corr_mctot_hist.Integral())

                    # Plot only central value
                    if mcuni_name == 'cv':
                        # Switch at start if you want to turn plotting off for
                        # faster testing.
                        if DRAW:
                            # Switches for log-axes
                            logx = False
                            logy = True
                            # Plot Data & pre-fit MC
                            MakeDataMCPlot(canvas, title, data_hist, qelike_hist,
                                           qelikenot_hist, before_chi2, before_ndf, logx, logy)
                            # Plot Data & post-fit MC
                            MakeDataMCPlot(canvas, title, data_hist, corr_qelike_rechist,
                                           corr_qelikenot_rechist, corr_chi2, corr_ndf, logx, logy, fit_chi2)
                            # Plot the MCPrediction hists output by the fitter
                            MakeDataMCPlot(canvas, title, data_hist, pred_qelike_hist,
                                           pred_qelikenot_hist, pred_chi2, pred_ndf, logx, logy, fit_chi2, True)
                            # Plot Data/MC ratio for both pre- and post-fit MC
                            MakeFitRatioPlot(
                                canvas, title, data_hist, mctot_hist, corr_mctot_hist, logx)

                        # Fill the bins of some of the outgoing hists.
                        before_chi2_hist.SetBinContent(
                            i_fitbin + 1, before_chi2 / before_ndf)
                        after_chi2_hist.SetBinContent(
                            i_fitbin + 1, corr_chi2 / corr_ndf)

                        bkg_scale_hist.SetBinContent(i_fitbin + 1, qelikenot_scale)
                        bkg_scale_hist.SetBinError(i_fitbin + 1, qelikenot_scale_err)
                        sig_scale_hist.SetBinContent(i_fitbin + 1, qelike_scale)
                        sig_scale_hist.SetBinError(i_fitbin + 1, qelike_scale_err)

                    # del mctot_hist, data_hist, qelike_hist, qelikenot_hist, pred_qelike_hist, pred_qelikenot_hist, pred_mctot_hist

            # Stop writing things to logfile.
            frac_logger.PrintToConsole()

            del data_cv_hist

            print("Done with fitbin ", fitbin)
            i_fitbin += 1

        # Close logfile for this samples Fraction fits
        frac_logger.close()

        # Plot chi2 values for each fitbin against Q2QE
        ndf = before_ndf
        MakeChi2Plot(canvas, before_chi2_hist, after_chi2_hist, ndf)
        canvas.Print(str(plotfilename + ".pdf]"), "pdf")

        # Setup logging for scale factor fitting
        scale_logfile_name = logfilebase + '_scalefits_' + timestr + '.log'
        scale_logger = printfLogger(scale_logfile_name)

        # Order is the order of the Chebyshev fit you want to do (although
        # techinically sets up a function of to order [order-1])
        order = 3
        xmin = binning[0]
        xmax = binning[-1]

        scale_logger.PrintToLog()
        print("Fitting Scale Factor for ", sample, "...")

        # Fit scalefactor against Q2QE, make a confidence interval hist (confint_hist)
        scale_hist, confint_hist, fit_func = DoScaleFactorFit(scale_hist, order, xmin, xmax)
        scale_logger.PrintToConsole()
        scale_logger.close()

        fit_chi2 = fit_func.GetChisquare()
        fit_ndf = fit_func.GetNDF()
        # Fit function doesn't seem to stick along, so making separate instance.
        cheb = logcheb(order, xmin, xmax)
        plot_fit_func = ROOT.TF1("f2", cheb, xmin, xmax, order)
        # leg = logleg(order, xmin, xmax)
        # plot_fit_func = ROOT.TF1("f2", leg, xmin, xmax, order)
        for i in range(order):
            plot_fit_func.SetParameter(i, fit_func.GetParameter(i))

        # Plot scale factor and fit against Q2QE.
        # MakeScaleFactorPlot(canvas, scale_hist, confint_hist, plot_fit_func)
        # Close out sample canvas

        # Write scale factor to a root file to use.
        scalehistfile_tail = "_ScaleFactor.root"
        outfilename = filename.replace(".root", scalehistfile_tail)
        outfile = ROOT.TFile(outfilename, "RECREATE")
        outfile.cd()
        scale_hist.Write()
        outfile.Close()

        # Store the scale factor hist, fit, and confidence interval hist.
        scale_hist_dict[sample] = {
            'hist': scale_hist, 'fit': plot_fit_func, 'confint_hist': confint_hist,'chi2':fit_chi2,'ndf':fit_ndf}

        CleanUpHists(hist_dict)
        print("Finished up sample ", sample)

    # Make scale factor plot to compare low E_\nu and high E_\nu parts of sample
    scalefile_name = plotfilename_base + "_ScaleComparison"
    scale_canvas = InitializeCanvas(scalefile_name)
    scale_qelike = scale_hist_dict['QElike']
    scale_loE = scale_hist_dict['QElike_loE']
    scale_hiE = scale_hist_dict['QElike_hiE']

    loE_ks = scale_qelike['hist'].KolmogorovTest(scale_loE['hist'])
    hiE_ks = scale_qelike['hist'].KolmogorovTest(scale_hiE['hist'])

    MakeScaleFactorPlot(scale_canvas, scale_qelike,'Full Sample',ROOT.kGreen+4)
    MakeScaleFactorPlot(scale_canvas, scale_loE,'E_{#nu} < 6 GeV',ROOT.kBlue)
    MakeScaleFactorsPlot(scale_canvas, scale_hiE,'E_{#nu} > 6 GeV',ROOT.kRed)

    MakeScaleCompPlot(scale_canvas, scale_loE,'E_{#nu} < 6 GeV', scale_hiE,'E_{#nu} > 6 GeV')
    MakeScaleCompPlot(scale_canvas,scale_qelike,'Full Sample',scale_loE,'E_{#nu} < 6 GeV',ROOT.kGreen+4,ROOT.kBlue)
    MakeScaleCompPlot(scale_canvas,scale_qelike,'Full Sample',scale_hiE,'E_{#nu} > 6 GeV',ROOT.kGreen+4,ROOT.kRed)

    scale_canvas.Print(str(scalefile_name + ".pdf]"), "pdf")


if __name__ == "__main__":
    main()
