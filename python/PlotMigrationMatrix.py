import ROOT
from PlotUtils import MnvH1D, MnvH2D, MnvPlotter
import os
import sys
from array import array

plotfiletype = "pdf"
# QElike
# QElike0Blob
samples = [
    "QElike",
    "QElike_0blob",
    "QElike_1blob"
]
sampletodo = "QElike"
# sampletodo = "QElike_0blob"
# sampletodo = "QElike_1blob"

var_names = {
    "recoil": "Recoil",
    "EAvail": "E_{Avail}",
    "EAvailWithNeutrons": "E_{Avail} w/ neutrons",
    "EAvailNoNonVtxBlobs": "E_{Avail} (recoil - nonvtx_iso_blobs)",
    "CalibRecoilWithNeutrons": "E_{Avail} w/ neutrons (calibrated)",
    "Q2QE": "Q^{2}_{QE}",
    "ptmu": "p_{T}",
    "pzmu": "p_{||}",
    "ptmuHD": "p_{T}",
    "pzmuHD": "p_{||}",
    "ThetamuDegrees": "#theta_{#mu}",
    "pmu": "p_{#mu}"
}

def CCQECanvas(name,title,xsize=1000,ysize=1000):
    c2 = ROOT.TCanvas(name,title,xsize,ysize)
    # c2.SetLeftMargin(0.1)
    # c2.SetRightMargin(0.04)
    # c2.SetLeftMargin(0.05)
    
    # c2.SetBottomMargin(0.14)
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
    if(xvar == "EAvail"):
        xaxis_name = "E_{Available}"
    if(yvar == "EAvail"):
        yaxis_name = "E_{Available}"
    if(xvar == "EAvailWithNeutrons"):
        xaxis_name = "E_{Available} w/ neutrons"
    if(yvar == "EAvailWithNeutrons"):
        yaxis_name = "E_{Available} w/ neutrons"

    
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

    plotdir = "/Users/nova/git/plots/eavailneutrontest"
    if not os.path.exists(plotdir): os.mkdir(plotdir)
    filebasename1=os.path.basename(filename1)
    # outfilename=filebasename1.replace(".root","_2DPlots")
    outdirname=os.path.join(plotdir,filebasename1.replace(".root","_migrationplots"))
    if not os.path.exists(outdirname): os.mkdir(outdirname)
    
    firstprint = True
    for sampletodo in samples:
        # Expects CCQENu naming convention
        print("Looking for hists...")
        hist_dict = {}
        histkeys_list = f.GetListOfKeys()
        foundsample = False
        for key in histkeys_list:
            hist_name = key.GetName()
            if firstprint:
                print(hist_name)
            # Get rid of non-hist branches.
            if hist_name.find("___") == -1:
                continue
            parse = hist_name.split('___')
            # Looking only for 2D hists
            # if parse[0]!="h":
            #     continue
            if parse[1]!= sampletodo:
                continue
            if parse[1]==sampletodo:
                foundsample = True
            if parse[2]!="qelike":
                continue
            if "response" not in parse[4]:
                continue
            if parse[3] not in hist_dict.keys():
                hist_dict[parse[3]]={"matrix":None,"reco":None,"truth":None}

            hist = f.Get(hist_name)
            if "migration" in parse[4]:
                hist_dict[parse[3]]["matrix"]=hist
                # hist.Print()
                continue
            if "reco" in parse[4]:
                hist_dict[parse[3]]["reco"]=hist
                # hist.Print()
                continue        
            if "truth" in parse[4]:
                hist_dict[parse[3]]["truth"]=hist
                # hist.Print()
                continue
        print("Done looking for hists.")
        firstprint=False
        if not foundsample:
            continue
        
        for var in hist_dict.keys():
            print("making normd matrix for ", var)
            binning = [hist_dict[var]["reco"].GetXaxis().GetBinLowEdge(1)]
            for bin in range(1,hist_dict[var]["reco"].GetNbinsX()+1):
                binning.append(hist_dict[var]["reco"].GetXaxis().GetBinUpEdge(bin))
            binning = array('d',binning)
            norm_matrix = hist_dict[var]["matrix"].Clone()
            nbinsy = hist_dict[var]["matrix"].GetNbinsY()
            nbinsx = hist_dict[var]["matrix"].GetNbinsX()
            print("binning: ", binning)
            print("binning size: ", len(binning), "\tnbinsx, nbinsy: ",nbinsx," ",nbinsy)

            #now the row normalized migration....
            if parse[0] not in ["h2D", "hHD"]:
                # binning = array('d',range(0,nbinsx+1))
                print("norm matrix")
                norm_matrix.SetBins(nbinsx,binning,nbinsy,binning)
                print("out matrix")
                out_matrix = ROOT.TH2D(norm_matrix.GetName(),norm_matrix.GetTitle(),nbinsx,binning,nbinsy,binning)
            else: 
                out_matrix = norm_matrix.Clone()
            for i in range(1,nbinsy+1):
                row_norm = 0.0
                for j in range(1,nbinsx+1):
                    row_norm += hist_dict[var]["matrix"].GetBinContent(j,i)
                # for j in range(0,nbinsy+1):
                for j in range(1,nbinsx+1):
                    if row_norm!=0.0:
                        _cont = norm_matrix.GetBinContent(j,i)
                        # norm_matrix.SetBinContent(j,i,_cont/row_norm)
                        # out_matrix.SetBinContent(j,i,0.5*_cont/row_norm)
                        out_matrix.SetBinContent(j,i,_cont/row_norm)
            # for i in range(0,nbinsx+1):
            #     row_norm = 0.0
            #     for j in range(0,nbinsy+1):
            #         row_norm += hist_dict["matrix"].GetBinContent(i,j)
            #     # for j in range(0,nbinsy+1):
            #     for j in range(0,nbinsy+1):
            #         _cont = norm_matrix.GetBinContent(i,j)
            #         if row_norm!=0.0:
            #             # norm_matrix.SetBinContent(j,i,_cont/row_norm)
            #             out_matrix.SetBinContent(i,j,_cont/row_norm)
            # out_matrix.Rebin2D()

            mnv = MnvPlotter()

            # mnv.SetBlackbodyPalette()
            mnv.SetRedHeatPalette()
            # mnv.SetBlackbodyPalette()
            pix = 1500
            if nbinsx*1.5 > 1000:
                print("nbinsx: ", nbinsx )
                pix = 5000
            canvas = ROOT.TCanvas("c","c",pix,round(1.3*pix))

            canvas.cd()
            canvas = CCQECanvas("c","c")
            # norm_matrix.SetMaximum(1.0)
            # norm_matrix.GetYaxis().SetTitle("True E_{Avail} bins")
            # norm_matrix.GetXaxis().SetTitle("Reconstructed Recoil bins")
            # norm_matrix.Draw("colz text")

            # out_matrix.SetMaximum(1.0)

            hist_name= hist_dict[var]["matrix"].GetName()
            parse = hist_name.split('___')
            canvas.SetTitle(str("Migration Row norm'd, "+sampletodo))
            # canvas.SetTitleSize(20.0)

            if parse[0] in ["h2D","hHD"]:
                out_matrix.Draw("colz") 
            else:
                out_matrix.SetMaximum(1.0)
                out_matrix.GetYaxis().SetTitle("True E_{Avail}")
                out_matrix.GetXaxis().SetTitle("Reconstructed "+var_names[var])
                if nbinsx>=20:
                    out_matrix.Draw("colz")
                else:
                    ROOT.gStyle.SetPaintTextFormat("0.2f")
                    out_matrix.Draw("colz text") 

            # canvas.SetLogx()
            # canvas.SetLogy()
            # canvas.SetLogz()
            if not os.path.exists(outdirname): os.mkdir(outdirname)

            canvas.Print(outdirname+"/plotmigration_"+sampletodo+"_"+var+".png")
            # canvas.Print("plotresponse_"+outfilename+".png")

            # canvas.Print("plotmigration_"+hist_dict["matrix"].GetName()+".png")

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