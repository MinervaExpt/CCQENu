import ROOT
ROOT.gROOT.SetBatch(True) # Run in batch mode
from PlotUtils import MnvH1D, MnvH2D, MnvPlotter
# import PlotUtils
import os
import sys
from array import array
import datetime


mydate = datetime.datetime.now()
month = mydate.strftime("%B")
year = mydate.strftime("%Y")
# Set this to make bins with no content with some content for plotting purposes only (does not affect normalization)
set_nozero = True
set_logz = True
# do_manual = False
legendfontsize = 0.05
do_mctot = True
prelim_string = "MINER#it{^{}#nu}A Work In Progress"

_xsize = 3400
_ysize = 2400
topmarg = 0.05 #0.03 + 0.09
bottommarg = 0.09
leftmarg = 0.08
rightmarg = 0.14


var_names = {
    "recoil": {
        "reco": "Recoil", 
        "truth": "E_{Avail}", 
        "units": "GeV"
    },    
    "Fitrecoil": {
        "reco": "Recoil", 
        "truth": "E_{Avail}", 
        "units": "GeV"
    },
    "EAvail": {
        "reco": "E^{}_{Avail}^{}", 
        "truth": "E_{Avail}^{}", 
        "units": "GeV"
    },
    "EAvail_nohi": {
        "reco": "E_{Avail} (MADBlobs)",
        "truth": "E_{Avail}",
        "units": "GeV",
    },
    "EAvailLeadingBlob": {
        "reco": "E_{Avail} (Leading MADBlob)",
        "truth": "E_{Avail}",
        "units": "GeV",
    },
    "EAvailNoNonVtxBlobs": {
        "reco": "E_{Avail} (nonvtx blobs)",
        "truth": "E_{Avail}",
        "units": "GeV",
    },
    "EAvailWithNeutrons": {
        "reco": "Recoil",
        "truth": "E_{Avail} w/ neutrons",
        "units": "GeV",
    },
    "CalibRecoilWithNeutrons": {
        "reco": "Recoil (calibrated)",
        "truth": "E_{Avail} w/ neutrons",
        "units": "GeV",
    },
    "Q2QE": {
        "reco": "Q^{2}_{QE}", 
        "truth": "Q^{2}_{QE}", 
        "units": "GeV^{2}"
    },
    "FitQ2QE": {
        "reco": "Q^{2}_{QE}", 
        "truth": "Q^{2}_{QE}", 
        "units": "GeV^{2}"
    },
    "ptmu": {
        "reco": "p^{}_{T}^{}", 
        "truth": "p^{}_{T}^{}", 
        "units": "GeV/c"
    },
    "pzmu": {
        "reco": "p_{||}", 
        "truth": "p_{||}", 
        "units": "GeV/c"
    },
    "ptmuHD": {
        "reco": "p_{T}", 
        "truth": "p_{T}", 
        "units": "GeV/c"
    },
    "pzmuHD": {
        "reco": "p_{||}", 
        "truth": "p_{||}", 
        "units": "GeV/c"
    },
    "ThetamuDegrees": {
        "reco": "#theta_{#mu}",
        "truth": "#theta_{#mu}",
        "units": "(deg)",
    },
    "pmu": {"reco": "p_{#mu}", "truth": "p_{#mu}", "units": "(GeV)"},
    "NNeutCands": {
        "reco": "# blobs tagged as neutrons",
        "truth": "# blobs whose parents are neutrons",
        "units": "",
    },
}
scaleaxis = [
    "Q2QE",
    "FitQ2QE",
]

catstodo = [
    "qelike",
    "chargedpion",
    "neutralpion",
    "other",
    # "multipion",
    # "other_np",
    # "qelikenot",
]
def AddPreliminary():
    font = 112
    color = ROOT.kRed +1
    latex = ROOT.TLatex()
    latex.SetNDC()
    latex.SetTextSize(0.03)
    latex.SetTextColor(color)
    latex.SetTextFont(font)
    latex.SetTextAlign(11)
    return latex

def MakePlotDir(subdir=""):
    """
    Subdir is the one for all plots that this script should ouptut. You will need to add
    any other subdirs in the script itself (e.g. based off input file name)
    """
    plotdir = ""
    base_plotdir = os.environ.get("PLOTSLOC")
    if base_plotdir != None:
        plotdir = os.path.join(base_plotdir, month + year)
    else:
        plotdir = os.path.join("/Users/nova/git/plots/", month + year)
    if not os.path.exists(plotdir):
        print("Can't find plot dir. Making it now... ", plotdir)
        os.mkdir(plotdir)
    if subdir == "":
        return plotdir
    if not os.path.exists(os.path.join(plotdir, subdir)):
        print("Can't find plot dir. Making it now... ", os.path.join(plotdir, subdir))
        os.mkdir(os.path.join(plotdir, subdir))
    return os.path.join(plotdir, subdir)


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

    # base_plotdir = os.environ.get('PLOTSLOC')
    # if base_plotdir != None:
    #     plotdir = os.path.join(base_plotdir,month+year)
    #     if not os.path.exists(plotdir): os.mkdir(plotdir)
    #     plotdir = os.path.join(plotdir,"MigrationPlots")
    # else:
    #     plotdir = os.path.join("/Users/nova/git/plots/",month+year,"MigrationPlots")
    # print("outdir ", plotdir)
    # if not os.path.exists(plotdir): os.mkdir(plotdir)

    plotdir = MakePlotDir("HeatMaps")
    filebasename1=os.path.basename(filename1)
    # outfilename=filebasename1.replace(".root","_2DPlots")
    outdirname=os.path.join(plotdir,filebasename1.replace(".root","_heatmapplots"))
    if not os.path.exists(outdirname): os.mkdir(outdirname)

    hist_dict = {}
    print("Looking for hists...")
    for key in f.GetListOfKeys():
        name = key.GetName()
        if "___" not in name: continue
        parse = name.split("___")
        if parse[0] != "h2D": continue
        if parse[1] != "QElike": continue
        if "migration" in name: continue
        print("Found hist ", name)
        hist = f.Get(name).Clone()
        if hist.GetEntries() <= 0: continue
        hist.Scale(1., "width")
        hist_dict[name] = hist
    modelname = ""
    raw_filename_split = filename1.split("_")
    for part in raw_filename_split:
        if "MnvTunev" in part:
            print("Found model name as %s"%(part))
            modelname += part
    # These need to happen in order, so it needs to be in a separate loop
    for part in raw_filename_split:
        if part=="multipion" and "no_multipion" not in filename1:
            modelname += "_" + part
    if modelname == "":
        print("Guessing model name is MnvTunev2.0.1")
        modelname = "MnvTunev2.0.1"
    tmpmodelname = modelname
    if "_" in tmpmodelname:
        tmpmodelname = modelname.replace('_',' ')
    if tmpmodelname[7]!= " ":
        tmpmodelname = tmpmodelname[:7] + " " + tmpmodelname[7:]
    tmpmodelname = tmpmodelname.replace(" multipion","")

    tmp_canvas_basename = "%s_%s"%(tmpmodelname, "QElike")
    pdf_canvas_name = tmp_canvas_basename+"_heatmapplots"
    dummy_canvas = ROOT.TCanvas(pdf_canvas_name,pdf_canvas_name,_xsize,_ysize)
    dummy_canvas.Print(os.path.join(outdirname,pdf_canvas_name+".pdf")+"[","pdf")

    latex_x = leftmarg + 0.08
    latex_y =  1 - topmarg +0.02
    if do_mctot:
        mctot_dict = {}
        for histname in hist_dict:
            parse = histname.split("___")
            sample = parse[1]
            category = parse[2]
            var = parse[3]
            if category not in catstodo: continue
            if category != catstodo[0]: continue
            foundcats = True
            tmp_mctot = hist_dict[histname].Clone(hist_dict[histname].GetName().replace("qelike", "mctot"))
            for cat in catstodo[1:]:
                if histname.replace("qelike",cat) not in hist_dict: 
                    foundcats = False
                    break
                tmp_mctot.Add(hist_dict[histname.replace("qelike",cat)], 1.0)
            if not foundcats: continue

            mctot_dict[tmp_mctot.GetName()] = tmp_mctot.Clone()
        for histname in mctot_dict:
            hist_dict[histname] = mctot_dict[histname]
    for histname in hist_dict.keys():
        print("looking at migration ",histname)
        parse = histname.split("___")
        sample = parse[1]
        category = parse[2]
        var = parse[3]
        # tuned = ("tuned" in parse[4])
        tuned_tag = "untuned"
        if("tuned" in parse[4]):
            tuned_tag = "tuned"
            # continue
        raw_matrix_name = histname+"_unnormed"
        norm_matrix_name = histname+"_rownormed"
        
        hist = hist_dict[histname].Clone(norm_matrix_name)

        canvas_title = "%s %s %s"%(sample,category,var)

        x_title = "Reco "
        y_title = "True "
        plottitle_tail = ""
        var_parse = var.split("_")
        x_title = "%s #lower[-0.15]{#scale[0.75]{(%s)}}"%(var_names[var_parse[0]]["reco"],var_names[var_parse[0]]["units"])
        y_title = "%s #lower[-0.15]{#scale[0.75]{(%s)}}"%(var_names[var_parse[1]]["reco"],var_names[var_parse[1]]["units"])
        hist.GetXaxis().SetTitle(x_title)
        hist.GetXaxis().SetTitleOffset(1.2)
        hist.GetYaxis().SetTitle(y_title)
        hist.GetYaxis().SetTitleOffset(1.1)

        hist.GetXaxis().CenterTitle()
        hist.GetYaxis().CenterTitle()

        hist.GetZaxis().SetTitle("Counts / (%s) / (%s)"%(var_names[var_parse[0]]["units"],var_names[var_parse[1]]["units"]))
        hist.GetZaxis().CenterTitle()
        hist.GetZaxis().SetTitleOffset(1.2)
        mnv = MnvPlotter()

        ROOT.gStyle.SetPalette(ROOT.kBird)
        hist.SetTitle(canvas_title)

        cc = ROOT.TCanvas("norm_canvas_"+histname, canvas_title, _xsize, _ysize)
        cc.SetLeftMargin(leftmarg)
        cc.SetRightMargin(rightmarg)
        cc.SetTopMargin(topmarg)
        cc.SetBottomMargin(bottommarg)

        if var.split("_")[0] in scaleaxis:
            cc.SetLogx()
        if var.split("_")[1] in scaleaxis:
            cc.SetLogy()
        cc.cd()
        
        hist.Draw("colz")

        if set_logz:
            cc.SetLogz()
        # plottitle.Draw()
        prelim = AddPreliminary()
        prelim.DrawLatex(latex_x, latex_y, prelim_string)
        
        cc.Print(os.path.join(outdirname, pdf_canvas_name + ".pdf"),"Title: %s %s"%(canvas_title, tuned_tag))
        # del raw_canvas



    dummy_canvas.Print(os.path.join(outdirname,pdf_canvas_name+".pdf")+"]","pdf")

    print("All done! uwu")


if __name__=="__main__":
    main()
