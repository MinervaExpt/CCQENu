import ROOT
from PlotUtils import MnvH1D, MnvH2D, MnvPlotter
import os
import sys

plotfiletype = "pdf"

def CCQECanvas(name,title,xsize=1000,ysize=750):
    c2 = ROOT.TCanvas(name,title,xsize,ysize)
    # c2.SetLeftMargin(0.1)
    c2.SetRightMargin(0.04)
    c2.SetLeftMargin(0.11)
    
    c2.SetBottomMargin(0.14)
    return c2

def MakeHistPretty(i_hist,xvar,yvar):
    hist = i_hist.Clone()

    xaxis_name = hist.GetXaxis().GetName()
    hist.GetXaxis().CenterTitle()

    yaxis_name = hist.GetYaxis().GetName()
    hist.GetYaxis().CenterTitle()

    # hist.GetZaxis().SetTitle("Events")

    if(xvar == "Q2QE"):
        ROOT.gPad.SetLogx(1)
        xaxis_name= "Q^{2}_{QE}"
    if(yvar=="Q2QE"):
        ROOT.gPad.SetLogy(1)
        yaxis_name= "Q^{2}_{QE}"
    if(xvar == "recoil"):
        xaxis_name = "Recoil"
    if(yvar == "recoil"):
        yaxis_name = "Recoil"
    if(xvar == "ptmu"):
        xaxis_name = "p_{T}"
    if(yvar == "ptmu"):
        yaxis_name = "p_{T}"
    if(xvar == "pzmu"):
        xaxis_name = "p_{||}"
    if(yvar == "pzmu"):
        yaxis_name = "p_{||}"

    hist_title = yaxis_name+" vs. "+xaxis_name
    hist.SetTitle(hist_title)

    return hist


def Plot2D(canvas,i_hist,xvar,yvar,color="COLZ"):
    hist = MakeHistPretty(i_hist,xvar,yvar)
    ROOT.gStyle.SetPalette(ROOT.kBird)
    # ROOT.gPad.SetLogx(1)
    # ROOT.gPad.SetLogz(1)
    ROOT.gStyle.SetOptStat("e")
    # stats_pave = i_mc_hist.FindObject("stats")
    hist = MakeHistPretty(i_hist,xvar,yvar)
    hist.Draw(color)

    canvas.Print(canvas.GetName(), str("Title: " + hist.GetTitle()))
    ROOT.gPad.SetLogx(0)
    ROOT.gPad.SetLogz(0)


def main():
    ROOT.TH1.AddDirectory(ROOT.kFALSE)

    if len(sys.argv) < 2:
        print("python Plot2DHist.py <infile.root>")
    else:
        filename1 = sys.argv[1]

    print("Looking at file "+filename1)
    f = ROOT.TFile(filename1, "READONLY")


    # filebasename1=os.path.basename(filename1)
    # outfilename=filebasename1.replace(".root","_2DPlots")

    # Expects CCQENu naming convention
    print("Looking for hists...")
    hist_dict ={"matrix":None,"reco":None,"truth":None}
    histkeys_list = f.GetListOfKeys()
    for key in histkeys_list:
        hist_name = key.GetName()
        print(hist_name)
        # Get rid of non-hist branches.
        if hist_name.find("___") == -1:
            continue
        parse = hist_name.split('___')
        # Looking only for 2D hists
        if parse[0]!="h":
            continue
        if parse[2]!="qelike":
            continue
        if "response" not in parse[4]:
            continue
        
        hist = f.Get(hist_name)
        if "migration" in parse[4]:
            hist_dict["matrix"]=hist
            hist.Print()
            continue
        if "reco" in parse[4]:
            hist_dict["reco"]=hist
            hist.Print()
            continue        
        if "truth" in parse[4]:
            hist_dict["truth"]=hist
            hist.Print()
            continue
    print("Done looking for hists.")



    # binning = [0.0]
    # for bin in range(1,hist_dict["reco"].GetNbinsX()+1):
    #     binning.append(hist_dict["reco"].GetXaxis().GetBinUpEdge())
    norm_matrix = hist_dict["matrix"].Clone()

    #now the row normalized migration....

    nbinsy = hist_dict["matrix"].GetNbinsY()
    nbinsx = hist_dict["matrix"].GetNbinsX()
    for i in range(0,nbinsy+1):
        row_norm = 0.0
        for j in range(0,nbinsx+1):
            row_norm += hist_dict["matrix"].GetBinContent(j,i)
        for j in range(0,nbinsy+1):
            _cont = norm_matrix.GetBinContent(j,i)
            if row_norm!=0.0:
                norm_matrix.SetBinContent(j,i,_cont/row_norm)


    mnv = MnvPlotter()

    mnv.SetCorrelationPalette()
    canvas = ROOT.TCanvas("c","c",750,750)

    canvas.cd()

    norm_matrix.SetMaximum(1.0)

    norm_matrix.GetYaxis().SetTitle("True E_{Avail} bins")
    norm_matrix.GetXaxis().SetTitle("Reconstructed Recoil bins")
    norm_matrix.Draw("colz text")


    canvas.Print("plotmigration_"+hist_dict["matrix"].GetName()+".png")

    # print("Making plots...")
    # for key in hist_dict.keys():
    #     hist = hist_dict[key]["hist"]
    #     xvar = hist_dict[key]["xvar"]
    #     yvar = hist_dict[key]["yvar"]
    #     Plot2D(canvas,hist,xvar,yvar)
    # print("Done making plots.")
    
    # print("Writing hists to file "+outfilename+".pdf")
    # canvas.Print(str(outfilename+".pdf]"), "pdf")
    print("All done! uwu")


if __name__=="__main__":
    main()