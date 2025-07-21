import ROOT
from PlotUtils import MnvH1D, MnvH2D, MnvPlotter
import os
import sys
from array import array

plotfiletype = "pdf"
# QElike
# QElike0Blob
# sampletodo = "QElike"

# var_names = {
#     "recoil": "Recoil",
#     "EAvail": "E_{Avail}",
#     "Q2QE": "Q^{2}_{QE}",
#     "ptmu": "p_{T}",
#     "pzmu": "p_{||}",
#     "ptmuHD": "p_{T}",
#     "pzmuHD": "p_{||}",
#     "ThetamuDegrees": "#theta_{#mu}",
#     "pmu": "p_{#mu}"
# }

# bins = {
#     "recoil": 5,
#     "EAvail": 5,
#     "EAvailNoNonVtxBlobs": 5,
#     "ptmu": 13,
#     "EAvailLeadingBlob": 5,
# }
max_chi2_dict = {
    "recoil": {
        "MnvTunev2": 350,
        "no2p2htune": 1500,
    },
    "EAvail": {
        "MnvTunev2": 350,
        "no2p2htune": 1500,
    },
    "EAvailNoNonVtxBlobs": {
        "MnvTunev2": 350,
        "no2p2htune": 1500,
    },
    "ptmu": {
        "MnvTunev2": 50,
        "no2p2htune": 100,
    },
    "EAvailLeadingBlob": {
        "MnvTunev2": 350,
        "no2p2htune": 1500,
    },
}

lineWidth = 5
def main():
    ROOT.TH1.AddDirectory(ROOT.kFALSE)

    if len(sys.argv) < 2:
        print("python PlotWarpingStudies.py <dir_with_warped_files>")
    else:
        filedir = sys.argv[1]

    print("Looking at files in " + filedir)

    plotdir = filedir
    outdirname = os.path.join(plotdir, "transwarp_plots")
    if not os.path.exists(outdirname):
        os.mkdir(outdirname)
    canvas = ROOT.TCanvas("chi2", "chi2")
    canvas.SetRightMargin(0.17)
    # canvas.SetLogx()
    # canvas.SetLogy()
    for file_name in os.listdir(filedir):
        if ".root" not in file_name or "TransWarpOut_" not in file_name:
            continue
        print("looking at file",file_name)
        f = ROOT.TFile(os.path.join(filedir,file_name), "READONLY")

        ymax = -1.
        # filebasename1=os.path.basename(filename1)
        for var in max_chi2_dict.keys():
            if "_"+var+"_" not in file_name: continue
            for study in max_chi2_dict[var].keys():
                if "_"+study+"_" not in file_name: continue
                ymax = max_chi2_dict[var][study]
        # Expects CCQENu naming convention

        print("Looking for hists...")
        chi2summary_hist = (
            f.Get("Chi2_Iteration_Dists")
            .Get("h_chi2_modelData_trueData_iter_chi2_percentile")
            .Clone()
        )
        chi2med_hist = (
            f.Get("Chi2_Iteration_Dists")
            .Get("h_median_chi2_modelData_trueData_iter_chi2")
            .Clone()
        )
        chi2avg_hist = (
            f.Get("Chi2_Iteration_Dists")
            .Get("m_avg_chi2_modelData_trueData_iter_chi2_truncated")
            .Clone()
        )
        axisTitle = chi2summary_hist.GetYaxis().GetTitle()
        yNDF = int(axisTitle[axisTitle.find("ndf=") + 4 : axisTitle.find(")")])

        # canvas = ROOT.TCanvas("c", "c", 1100, 720)
        # canvas.SetLeftMargin(0.1)
        # canvas.SetRightMargin(0.2)
        # c2.SetLeftMargin(0.05)
        # canvas.SetBottomMargin(0.14)
        # ROOT.gStyle.SetColorPalette(ROOT.kBird)

        chi2summary_hist.GetXaxis().SetTitle("N_{iter}")
        chi2summary_hist.GetXaxis().CenterTitle()
        chi2summary_hist.GetYaxis().SetTitle("#chi^{2}")
        chi2summary_hist.GetYaxis().CenterTitle()
        chi2summary_hist.GetZaxis().SetTitle("N_{univ}")
        chi2summary_hist.GetZaxis().CenterTitle()

        chi2summary_hist.SetTitleOffset(0.75, "X")
        chi2summary_hist.SetTitleOffset(0.65, "Y")
        chi2summary_hist.SetTitleOffset(0.85, "Z")

        if ymax > 0:
            chi2summary_hist.GetYaxis().SetRangeUser(0,ymax)
        chi2med_hist.SetLineColor(ROOT.kBlack)
        chi2med_hist.SetLineWidth(lineWidth)
        chi2med_hist.SetTitle("Median Chi2")

        chi2avg_hist.SetTitle("Mean Chi2")
        chi2avg_hist.SetLineWidth(lineWidth)
        chi2avg_hist.SetLineColor(ROOT.kViolet)
        chi2avg_hist.SetMarkerStyle(0)

        # chi2summary_hist.GetYaxis().SetRangeUser(0,200)
        chi2summary_hist.Draw("COLZ")
        chi2avg_hist.Draw("same")
        chi2med_hist.Draw("HIST,same")
        chi2summary_hist.Draw("axis, same")
        if "_Clousure_" in file_name:
            chi2summary_hist.getYaxis().SetRangeUser(0,ymax*1.2)
        # if "Clousure" not in file_name:
        #     ndfLine = ROOT.TLine(1, yNDF, chi2summary_hist.GetXaxis().GetXmax(), yNDF)
        #     ndfLine.SetLineWidth(lineWidth-2)
        #     ndfLine.SetLineStyle(ROOT.kDashed)
        #     ndfLine.Draw()

        #     doubleNDFLine = ROOT.TLine(
        #         1, 2 * yNDF, chi2summary_hist.GetXaxis().GetXmax(), 2 * yNDF
        #     )
        #     print("yNDF=",yNDF)
        #     doubleNDFLine.SetLineColor(ROOT.kRed)
        #     doubleNDFLine.SetLineWidth(lineWidth-2)
        #     doubleNDFLine.SetLineStyle(ROOT.kDashed)
        #     doubleNDFLine.Draw()

        # leg = ROOT.TLegend(0.6, 0.6, 0.9, 0.9)
        leg = ROOT.TLegend(0.52, 0.6, 0.82, 0.9)
        leg.AddEntry(chi2avg_hist)
        leg.AddEntry(chi2med_hist)
        # if "_Clousure_" not in file_name:
        #     leg.AddEntry(ndfLine, "Number of Bins", "l")
        #     leg.AddEntry(doubleNDFLine, "2x Number of Bins", "l")
        # leg.AddEntry(iterLine, str(iterChosen) + " iterations", "l")
        leg.Draw()
        out_file_name = "plots_"+file_name.replace(".root", "warp_chi2_niter.png")
        canvas.Print(os.path.join(outdirname, out_file_name))


if __name__=="__main__":
    main()
