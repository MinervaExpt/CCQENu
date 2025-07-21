import ROOT
from PlotUtils import MnvH1D, MnvH2D, MnvPlotter
# import PlotUtils
import os
import sys
from array import array

# Set this to make bins with no content with some content for plotting purposes only (does not affect normalization)
set_nozero = True
set_logz = False
do_manual = True
# do_manual = False
categorytodo = "qelike"


var_names = {
    "recoil": {
        "reco": "Recoil",
        "truth": "E_{Avail}",
        "units": "(GeV)"
    },
    "EAvail": {
        "reco": "E_{Avail} (MADBlobs)",
        "truth": "E_{Avail}",
        "units": "(GeV)"
    },
    "EAvailLeadingBlob": {
        "reco": "E_{Avail} (Leading MADBlob)",
        "truth": "E_{Avail}",
        "units": "(GeV)"
    },
    "EAvailNoNonVtxBlobs": {
        "reco": "E_{Avail} (nonvtx blobs)",
        "truth": "E_{Avail}",
        "units": "(GeV)"
    },
    "EAvailWithNeutrons": {
        "reco": "Recoil",
        "truth": "E_{Avail} w/ neutrons",
        "units": "(GeV)"
    },
    "CalibRecoilWithNeutrons": {
        "reco": "Recoil (calibrated)",
        "truth": "E_{Avail} w/ neutrons",
        "units": "(GeV)"
    },
    "Q2QE": {
        "reco":"Q^{2}_{QE}",
        "truth":"Q^{2}_{QE}",
        "units": "(GeV^{2})"
    },
    "ptmu": {
        "reco":"p_{T}",
        "truth": "p_{T}",
        "units": "(GeV)"
    },
    "pzmu": {
        "reco":"p_{||}",
        "truth": "p_{||}",
        "units": "(GeV)"
    },
    "ptmuHD": {
        "reco":"p_{T}",
        "truth": "p_{T}",
        "units": "(GeV)"
    },
    "pzmuHD": {
        "reco":"p_{||}",
        "truth": "p_{||}",
        "units": "(GeV)"
    },
    "ThetamuDegrees": {
        "reco":"#theta_{#mu}",
        "truth":"#theta_{#mu}",
        "units": "(deg)"
    },
    "pmu": {
        "reco":"p_{#mu}",
        "truth": "p_{#mu}",
        "units": "(GeV)"
    }
}

def CCQECanvas(name,title,xsize=1000,ysize=1000):
    c2 = ROOT.TCanvas()
    # c2 = ROOT.TCanvas(name,title,xsize,ysize)
    # c2.SetLeftMargin(0.1)
    # c2.SetRightMargin(0.04)
    # c2.SetLeftMargin(0.05)
    
    # c2.SetBottomMargin(0.14)
    return c2

def main():
    ROOT.TH1.AddDirectory(ROOT.kFALSE)

    if len(sys.argv) < 2:
        print("python PlotMigrationMatrix.py <infile.root>")
    else:
        filename1 = sys.argv[1]

    print("Looking at file "+filename1)
    f = ROOT.TFile(filename1, "READONLY")

    base_plotdir = os.environ.get('PLOTSLOC')
    if base_plotdir != None:
        plotdir = base_plotdir
    else:
        plotdir = "/Users/nova/git/plots/Summer2025MnvWeek/MigrationMatrices/"
    print("outdir ", plotdir)
    if not os.path.exists(plotdir): os.mkdir(plotdir)
    filebasename1=os.path.basename(filename1)
    # outfilename=filebasename1.replace(".root","_2DPlots")
    outdirname=os.path.join(plotdir,"Summer2025MnvWeek/MigrationPlots/lowbins/",filebasename1.replace(".root","_migrationplots"))
    if not os.path.exists(outdirname): os.mkdir(outdirname)

    hist_dict = {}
    print("Looking for hists...")
    for key in f.GetListOfKeys():
        hist_name = key.GetName()
        if "migration" not in hist_name or "noPOTscale" in hist_name:
            continue
        print("Found hist ", hist_name)
        hist_dict[hist_name] = f.Get(hist_name).Clone()

    for response_name in hist_dict.keys():
        print("looking at migration ",response_name)
        parse = response_name.split("___")
        sample = parse[1]
        category = parse[2]
        var = parse[3]
        # tuned = ("tuned" in parse[4])
        tuned_tag = "untuned"
        if("tuned" in parse[4]):
            tuned_tag = "tuned"
            continue
        if not do_manual:
            print("in do_mnvplotter")
            mnv_canvas_title = "Migration Row norm'd, " + sample + "_"+ tuned_tag
            mnv_canvas = ROOT.TCanvas("norm_canvas_" + response_name, mnv_canvas_title)
            print("here")

            mnv = MnvPlotter()
            if set_logz:
                mnv_canvas.SetLogz()
            mnv.SetBlackbodyPalette()
            # mnv.SetWhiteRainbowPalette()
            # mnv.SetRedHeatPalette()
            # mnv.SetROOT6Palette(ROOT.kBird)

            hist = hist_dict[response_name].Clone()
            hist.GetXaxis().CenterTitle()
            hist.GetYaxis().CenterTitle()
            text_opt = False
            if hist_dict[response_name].GetNbinsX()>=20:
                text_opt = True
            mnv.DrawNormalizedMigrationHistogram(
                hist, True, False, False, text_opt
            )
            raw_outname = os.path.join(outdirname,"mnv_plotmigration__%s_%s_%s_%s.png"%(sample,category,tuned_tag,var))

            mnv_canvas.Print(raw_outname)
        if do_manual:
            raw_matrix_name = response_name+"_unnormed"
            norm_matrix_name = response_name+"_rownormed"

            norm_matrix = hist_dict[response_name].Clone(norm_matrix_name)
            raw_matrix = norm_matrix.Clone(raw_matrix_name)
            reco_hist_name = response_name.replace("migration","reco")
            true_hist_name = response_name.replace("migration","truth")
            if "noPOTscale" in response_name:
                continue
                # reco_hist_name = response_name.replace("migration_noPOTscale","reco")
                # true_hist_name = response_name.replace("migration_noPOTscale","truth")
            # print("\t",reco_hist_name,"\t",true_hist_name)

            reco_hist = f.Get(reco_hist_name)
            true_hist = f.Get(true_hist_name)

            nbinsy = hist_dict[response_name].GetNbinsY()
            nbinsx = hist_dict[response_name].GetNbinsX()
            # If 1D, use the binning of the hists
            if parse[0] not in ["h2D","hHD"]:
                reco_binning = [reco_hist.GetXaxis().GetBinLowEdge(1)]
                true_binning = [true_hist.GetXaxis().GetBinLowEdge(1)]

                for bin in range(1,reco_hist.GetNbinsX()+1):
                    reco_binning.append(reco_hist.GetXaxis().GetBinUpEdge(bin))
                for bin in range(1,true_hist.GetNbinsX()+1):
                    true_binning.append(true_hist.GetXaxis().GetBinUpEdge(bin))
                reco_binning = array('d', reco_binning)
                true_binning = array('d',true_binning)
                raw_matrix.SetBins(nbinsx, reco_binning, nbinsy, true_binning)

            norm_matrix = raw_matrix.Clone(norm_matrix_name)

            for i in range(1,nbinsy+1):
                row_norm = 0.
                for j in range(1,nbinsx+1):
                    row_norm += hist_dict[response_name].GetBinContent(j,i)
                for j in range(1,nbinsx+1):
                    if row_norm!=0.0:
                        _cont = norm_matrix.GetBinContent(j,i)
                        if _cont == 0:# and set_nozero:
                            _cont == 1
                        norm_matrix.SetBinContent(j,i,_cont/row_norm)
                        raw_matrix.SetBinContent(j,i,_cont)
            print("\tfinished making matrices, now plotting")

            # Make the hists pretty
            # norm_matrix.SetMaximum(1.0)

            norm_canvas_title = "Migration Row norm'd, " + sample
            raw_canvas_title = "Migration, no norm, " + sample

            x_title = "Reco"
            y_title = "True"
            if parse[0] in ["h2D","hHD"]:
                var_parse = var.split("_")
                for var in var_parse:
                    x_title+= " "+ var_names[var]["reco"]
                    y_title+= " "+ var_names[var]["truth"]
                norm_matrix.GetXaxis().SetTitle(x_title)
                norm_matrix.GetYaxis().SetTitle(y_title)
                raw_matrix.GetXaxis().SetTitle(x_title)
                raw_matrix.GetYaxis().SetTitle(y_title)

            else:
                # norm_matrix.SetMaximum(1.0)
                norm_matrix.GetXaxis().SetTitle(x_title+" "+var_names[var]["reco"]+" "+var_names[var]["units"])
                norm_matrix.GetYaxis().SetTitle(y_title+" "+var_names[var]["truth"]+" "+var_names[var]["units"])
                raw_matrix.GetXaxis().SetTitle(x_title+" "+var_names[var]["reco"]+" "+var_names[var]["units"])
                raw_matrix.GetYaxis().SetTitle(y_title+" "+var_names[var]["truth"]+" "+var_names[var]["units"])
            norm_matrix.GetXaxis().CenterTitle()
            norm_matrix.GetYaxis().CenterTitle()
            raw_matrix.GetXaxis().CenterTitle()
            raw_matrix.GetYaxis().CenterTitle()

            norm_matrix.GetZaxis().SetTitle("Fraction of events")
            norm_matrix.GetZaxis().CenterTitle()
            mnv = MnvPlotter()

            # mnv.SetBlackbodyPalette()
            # mnv.SetWhiteRainbowPalette()
            mnv.SetROOT6Palette(ROOT.kBird)
            # mnv.SetRedHeatPalette()
            # mnv.SetWhiteRainbowPalette()
            norm_matrix.SetTitle(norm_canvas_title)
            raw_matrix.SetTitle(raw_canvas_title)

            # This is used for hyperdim migrations which can be big
            pix = 1500
            if nbinsx*1.5 > 1000:
                print("nbinsx: ", nbinsx )
                pix = 5000

            # Do the norm'd ones first
            # if parse[0] != "hHD":
            #     norm_canvas = CCQECanvas("norm_canvas_"+response_name, norm_canvas_title)
            # else:
            #     norm_canvas = ROOT.TCanvas("norm_canvas_"+response_name, norm_canvas_title,pix,round(1.3*pix))
            norm_canvas = ROOT.TCanvas("norm_canvas_"+response_name, norm_canvas_title)
            norm_canvas.cd()

            if parse[0] in ["h2D","hHD"]:
                # norm_canvas.cd()
                norm_matrix.Draw("colz")
            else:
                if nbinsx>=20:
                    # norm_canvas.cd()
                    norm_matrix.Draw("colz")
                else:
                    ROOT.gStyle.SetPaintTextFormat("0.2f")
                    # norm_canvas.cd()
                    norm_matrix.Draw("colz text")

            if "Q2QE" in var:
                norm_canvas.SetLogx()
                norm_canvas.SetLogy()        
            if set_logz:
                norm_canvas.SetLogz()

            norm_outname = os.path.join(outdirname,"normd_plotmigration__%s_%s_%s_%s.png"%(sample,category,tuned_tag,var))
            norm_canvas.Print(norm_outname)

            # Do the raw ones now
            # mnv.SetROOT6Palette(ROOT.kNeon)

            # if parse[0] != "hHD":
            #     raw_canvas = CCQECanvas("raw_canvas_"+response_name, raw_canvas_title)
            # else:
            #     raw_canvas = ROOT.TCanvas("raw_canvas_"+response_name, raw_canvas_title,pix,round(1.3*pix))
            raw_canvas = ROOT.TCanvas("raw_canvas_"+response_name, raw_canvas_title)

            raw_canvas.cd()
            raw_matrix.Draw("colz")

            if "Q2QE" in var:
                raw_canvas.SetLogx()
                raw_canvas.SetLogy()        
            if set_logz:
                raw_canvas.SetLogz()
            # raw_canvas.SetLogz()

            raw_outname = os.path.join(outdirname,"raw_plotmigration__%s_%s_%s_%s.png"%(sample,category,tuned_tag,var))
            raw_canvas.Print(raw_outname)

    print("All done! uwu")


if __name__=="__main__":
    main()
