import ROOT
from PlotUtils import MnvH1D, MnvH2D
import os
import sys
import math
import ctypes
import json
import numpy as np

plotfiletype = "pdf"

def InitializeCanvas(canvas_name):
    # Initialize a pdf canvas for making plots
    canvas = ROOT.TCanvas(str(canvas_name + "."+plotfiletype))

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


def GetScaleHists(i_file,scale_fraction="scale"):
    hist_dict = {}
    histkeys_list = i_file.GetListOfKeys()
    for key in histkeys_list:
        hist_name = key.GetName()
        if hist_name.find("___") == -1:
            continue
        splitnames_list = hist_name.split('___')

        sig_key = splitnames_list[2]

        if sig_key in hist_dict:
            # print("key already here")
            x = 1
        else:
            hist_dict[sig_key] = {}

        if scale_fraction not in splitnames_list[4]:
            continue

        # if "tuned" not in splitnames_list[4]:
        #     tuned_key = 'untuned'
        # else:
        #     tuned_key = 'tuned'
        # hist_dict[sig_key][tuned_key]=i_file.Get(hist_name).Clone()
        hist_dict[sig_key]=i_file.Get(hist_name).Clone()
        print(hist_name)
    # print(hist_dict)
    return hist_dict


# def MakeScaleFactorPlot(canvas, i_scale_hist_dict,sample_str='',color=ROOT.kBlack):
def MakeScaleFactorPlot(canvas, i_scale_hist,sample_str='',color=ROOT.kBlack):
    # scale_hist = i_scale_hist_dict['hist'].Clone()
    # scale_fit = i_scale_hist_dict['fit']
    # fit_chi2 = i_scale_hist_dict['chi2']
    # fit_ndf = i_scale_hist_dict['ndf']
    scale_hist = i_scale_hist.Clone()
    ROOT.gStyle.SetOptStat(0)

    xmax = 2.0
    ROOT.gPad.SetLogx(1)
    # scale_hist.SetMaximum(1.5)
    # scale_hist.SetMinimum(0.7)

    title_base = "Scale Factor vs. Q^{2}_{QE}"
    if len(sample_str)>0:
        # title_suffix = sample_str
        title = sample_str+' '+title_base
        if "QELikeNot" in sample_str:
            scale_hist.SetMaximum(0.8)
            scale_hist.SetMinimum(1.7)
        else:
            scale_hist.SetMaximum(0.3)
            scale_hist.SetMinimum(1.2)

    else:
        title = title_base

    scale_hist.SetTitle(title)
    scale_hist.GetXaxis().SetTitle("Q^{2}_{QE} (GeV^{2})")
    scale_hist.GetXaxis().CenterTitle()
    scale_hist.GetYaxis().SetTitle("Scale Factor")
    scale_hist.GetYaxis().CenterTitle()


    scale_hist.SetMarkerStyle(20)
    scale_hist.SetMarkerColor(color)
    scale_hist.SetLineColor(color)

    # scale_fit.SetLineColor(color)

    # confint_hist = i_scale_hist_dict['confint_hist'].Clone()
    # confint_hist.SetFillColorAlpha(color, 0.2)

    line = ROOT.TLine(0, 1., xmax, 1.)
    line.SetLineStyle(2)
    line.SetLineWidth(3)
    line.SetLineColor(36)

    # legend = ROOT.TLegend(0.45, 0.9, 0.2, 0.7)
    # legend.SetBorderSize(1)
    # legend.AddEntry(scale_hist, "Scale Factor", "p")
    # legend.AddEntry(scale_fit, "Fit")

    # fit_chi2_label = 'Fit \chi^{2} = ' + str("{:.2f}".format(fit_chi2))
    # fit_ndf_label = 'Fit NDF = ' + str(fit_ndf)

    # legend2 = ROOT.TLegend(0.7, 0.15, 0.9, 0.35)
    # legend2.SetBorderSize(1)
    # legend2.AddEntry("chi2", fit_chi2_label, "")
    # legend2.AddEntry("NDF", fit_ndf_label, "")

    scale_hist.Draw("PE1")
    line.Draw("same")
    # confint_hist.Draw("e5 same")
    # scale_fit.Draw("same")
    # legend.Draw("same")
    # legend2.Draw("same")

    canvas.Print(canvas.GetName(), str("Title: ScaleFactor"))
    ROOT.gPad.SetLogx(0)


# def MakeScaleCompPlot(canvas, i_h1_dict,h1_name,i_h2_dict,h2_name,h1_color=ROOT.kBlue,h2_color=ROOT.kRed):
def MakeScaleCompPlot(canvas, i_h1,h1_name,i_h2,h2_name,plot_name='',h1_color=ROOT.kBlue+1,h2_color=ROOT.kRed+1):
    # h1_hist = i_h1_dict['hist'].Clone()
    # h2_hist = i_h2_dict['hist'].Clone()
    h1_hist = i_h1.Clone()
    h2_hist = i_h2.Clone()

    # h1_fit = i_h1_dict['fit']
    # h2_fit = i_h2_dict['fit']

    # xmin = 0.02 #0.02
    xmax = 2.0  # 1.4
    ROOT.gPad.SetLogx(1)
    # ROOT.gPad.SetLogy(1)
    ROOT.gStyle.SetOptStat(0)

    h1_hist.SetTitle("Scale Factor vs. Q^{2}_{QE}: "+plot_name+" Comparison")
    h1_hist.GetXaxis().SetTitle("Q^{2}_{QE} (GeV^{2})")
    h1_hist.GetXaxis().CenterTitle()
    h1_hist.GetYaxis().SetTitle("Scale Factor")
    h1_hist.GetYaxis().CenterTitle()

    h1_hist.SetMarkerStyle(20)
    h1_hist.SetMarkerColor(h1_color)
    h1_hist.SetLineColor(h1_color)

    # h1_fit.SetLineColor(h1_color)
    if plot_name in ["QELike", "QElike","qelike"]:
        h1_hist.SetMaximum(1.45)
        h1_hist.SetMinimum(0.85)
        legend = ROOT.TLegend(0.7, 0.8, 0.95, 0.7)
        legend.SetBorderSize(1)

    if plot_name in ["QELikeNot", "QElikenot","QElikenot","qelikenot"]:
        h1_hist.SetMaximum(1.17)
        h1_hist.SetMinimum(0.45)
        legend = ROOT.TLegend(0.7, 0.25, 0.95, 0.35)
        legend.SetBorderSize(1)


    h2_hist.SetMarkerStyle(20)
    h2_hist.SetMarkerColor(h2_color)
    h2_hist.SetLineColor(h2_color)

    # h2_fit.SetLineColor(h2_color)


    line = ROOT.TLine(0, 1., xmax, 1.)
    line.SetLineStyle(2)
    line.SetLineWidth(3)
    line.SetLineColor(36)

    # h1confint_hist = i_h1_dict['confint_hist'].Clone()
    # h2confint_hist = i_h2_dict['confint_hist'].Clone()
    # h1confint_hist.SetFillColorAlpha(h1_color, 0.2)
    # h2confint_hist.SetFillColorAlpha(h2_color, 0.2)

    #
    legend.AddEntry(h1_hist, h1_name)
    legend.AddEntry(h2_hist, h2_name)

    # ks = h1_hist.KolmogorovTest(h2_hist)
    # chi2 = h1_hist.Chi2Test(h2_hist,"CHI2")
    # ndf = h1_hist.GetNbinsX() - 1
    # h1_hist.Chi2Test(h2_hist,"P")

    # ks_label = 'K-S GoF = ' + str("{:.4f}".format(ks))
    # chi2_label = '\chi^{2} = ' + str("{:.2f}".format(chi2))
    # ndf_label = 'NDF = ' + str(ndf)

    # legend2 = ROOT.TLegend(0.7, 0.15, 0.9, 0.35)
    # legend2.SetBorderSize(1)

    # legend2.AddEntry("ks", ks_label, "")
    # legend2.AddEntry("chi2",chi2_label,"")
    # legend2.AddEntry("ndf",ndf_label,"")

    h1_hist.Draw("E1")
    line.Draw("same")
    # h1confint_hist.Draw("e3,same")
    # h1_fit.Draw("same")
    h2_hist.Draw("E1,same")
    # h2confint_hist.Draw("e3,same")
    # h2_fit.Draw("same")

    legend.Draw("same")
    # legend2.Draw("same")

    canvas_title = "Title: ScaleComp "+h1_name+" "+h2_name
    canvas.Print(canvas.GetName(), canvas_title)
    ROOT.gPad.SetLogx(0)
    # ROOT.gPad.SetLogy(0)


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

def main():
    ROOT.TH1.AddDirectory(ROOT.kFALSE)

    if len(sys.argv) < 2:
        print("python FitPlotting.py <infile>.root <outfilename>")
    else:
        filename = sys.argv[1]
        # if len(sys.argv)>=3:
        #     plotfilename_base = sys.argv[2]
        # else if len(sys.argv)==2:
        #     plotfilename_base = filename.replace(".root","_plots")
        plotfilename_base = filename.replace(".root","_plots")

    f = ROOT.TFile(filename, "READONLY")
    plotfilename = plotfilename_base # + '_' + sample

    scale_hist_dict = GetScaleHists(f)
    canvas = InitializeCanvas(plotfilename)
    canvas.Print(str(plotfilename + "." + plotfiletype+"["), plotfiletype)
    # MakeScaleFactorPlot(canvas, scale_hist_dict['qelike']['tuned'],'Tuned QELike',ROOT.kBlue+1)
    # MakeScaleFactorPlot(canvas, scale_hist_dict['qelike']['untuned'],'Untuned QELike',ROOT.kBlue)
    # MakeScaleFactorPlot(canvas, scale_hist_dict['qelikenot']['tuned'],'Tuned QELikeNot',ROOT.kRed+1)
    # MakeScaleFactorPlot(canvas, scale_hist_dict['qelikenot']['untuned'],'Untuned QELikeNot',ROOT.kRed)

    MakeScaleFactorPlot(canvas, scale_hist_dict['qelike'],'Untuned QELike',ROOT.kBlue)

    MakeScaleFactorPlot(canvas, scale_hist_dict['qelikenot'],'Untuned QELikeNot',ROOT.kRed)

    # MakeScaleCompPlot(canvas, scale_hist_dict['qelike']['tuned'],'Tuned', scale_hist_dict['qelike']['untuned'],'Untuned','QELike')
    # MakeScaleCompPlot(canvas, scale_hist_dict['qelikenot']['tuned'],'Tuned', scale_hist_dict['qelikenot']['untuned'],'Untuned','QELikeNot')

    canvas.Print(str(plotfilename + "." + plotfiletype+"]"), plotfiletype)


    # canvas = ROOT.TCanvas(str(canvas_name + ".pdf"))
    #
    #
    #
    #
    #
    # logx = False
    # logy = True
    #
    # scalefile_name = plotfilename_base + "_ScaleComparison"
    # scale_canvas = InitializeCanvas(scalefile_name)
    # # scale_qelike = scale_hist_dict['QElike']
    # # scale_loE = scale_hist_dict['QElike_loE']
    # # scale_hiE = scale_hist_dict['QElike_hiE']
    #
    # # loE_ks = scale_qelike['hist'].KolmogorovTest(scale_loE['hist'])
    # # hiE_ks = scale_qelike['hist'].KolmogorovTest(scale_hiE['hist'])
    #
    #
    #
    # MakeScaleFactorPlot(scale_canvas, scale_qelike,'Full Sample',ROOT.kGreen+4)
    # MakeScaleFactorPlot(scale_canvas, scale_loE,'E_{#nu} < 6 GeV',ROOT.kBlue)
    # MakeScaleFactorsPlot(scale_canvas, scale_hiE,'E_{#nu} > 6 GeV',ROOT.kRed)
    #
    # MakeScaleCompPlot(scale_canvas, scale_loE,'E_{#nu} < 6 GeV', scale_hiE,'E_{#nu} > 6 GeV')
    # MakeScaleCompPlot(scale_canvas,scale_qelike,'Full Sample',scale_loE,'E_{#nu} < 6 GeV',ROOT.kGreen+4,ROOT.kBlue)
    # MakeScaleCompPlot(scale_canvas,scale_qelike,'Full Sample',scale_hiE,'E_{#nu} > 6 GeV',ROOT.kGreen+4,ROOT.kRed)
    #
    # scale_canvas.Print(str(scalefile_name + ".pdf]"), "pdf")

    # canvas_name=plotfilename + "_2D"
    # canvas = ROOT.TCanvas(str(canvas_name + ".pdf"))
    #
    # canvas.cd()
    # canvas.SetLeftMargin(0.15)
    # canvas.SetRightMargin(0.15)
    # canvas.SetBottomMargin(0.15)
    # canvas.SetTopMargin(0.15)
    # # Each canvas needs a closing statement to match this Print
    # # TODO: Make this a class that handles opening/closing
    # canvas.Print(str(canvas_name + ".pdf["), "pdf")
    # Plot2D(canvas,hist2D)
    # canvas.Print(str(canvas_name + ".pdf]"), "pdf")

    # # Plot Data & pre-fit MC
    # MakeDataMCPlot(canvas, title, data_hist, qelike_hist,qelikenot_hist, before_chi2, before_ndf, logx, logy)
    # # Plot Data & post-fit MC
    # MakeDataMCPlot(canvas, title, data_hist, corr_qelike_rechist,corr_qelikenot_rechist, corr_chi2, corr_ndf, logx, logy, fit_chi2)
    # # Plot the MCPrediction hists output by the fitter
    # MakeDataMCPlot(canvas, title, data_hist, pred_qelike_hist,pred_qelikenot_hist, pred_chi2, pred_ndf, logx, logy, fit_chi2, True)
    # # Plot Data/MC ratio for both pre- and post-fit MC
    # MakeFitRatioPlot(canvas, title, data_hist, mctot_hist, corr_mctot_hist, logx)

    # MakeChi2Plot(canvas, before_chi2_hist, after_chi2_hist, ndf)
    # canvas.Print(str(plotfilename + ".pdf]"), "pdf")


if __name__ == "__main__":
    main()
