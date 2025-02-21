import sys,os
import ROOT
from ROOT import gROOT,gStyle,TFile,THStack,TH1D,TCanvas,TColor,TObjArray,TH2F,THStack,TFractionFitter,TLegend,TLatex,TString,TText


ROOT.gStyle.SetOptStat(0)

def CCQECanvas(name,title,xsize=1000,ysize=750):
	c2 = ROOT.TCanvas(name,title,xsize,ysize)
	c2.SetLeftMargin(0.20)
	c2.SetRightMargin(0.05)
	c2.SetBottomMargin(0.15)
	return c2

def CCQELegend(xlow,ylow,xhigh,yhigh):
	leg = ROOT.TLegend(xlow,ylow,xhigh,yhigh)
	#leg.SetFillStyle(0)
	leg.SetFillColor(ROOT.kWhite)
	leg.SetBorderSize(1)
	leg.SetTextSize(0.035)
	return leg

bin_i = int(sys.argv[1])
filename = "SB_NuConfig_bdtg_MAD_2track_me1N_1_testing.root"

scaleX = ["Q2QE"]
scaleY = ["Q2QE"]

process=["data","qelike","1chargedpion","multipion","other1neutralpion"]

colors = {
    "qelike":TColor.GetColor(0,133,173),#ROOT.kMagenta-4,
    "1chargedpion":TColor.GetColor(175,39,47),#ROOT.kBlue-7,
    "multipion":TColor.GetColor(234,170,0),#ROOT.kRed-4,
    "other1neutralpion":TColor.GetColor(76,140,43)#ROOT.kGreen-3
}
legend_labels = {
    "qelike":"QELike",
    "1chargedpion":"Single #pi^{+/-} in FS",
    "multipion":"N#pi in FS",
    "other1neutralpion":"Other"
}

f = TFile.Open(filename,"READONLY")
dirname = filename.replace(".root","")
if not os.path.exists(dirname): os.mkdir(dirname)

keys = f.GetListOfKeys()

cc = CCQECanvas("canvas","canvas")

h2D_data = f.Get("h2D___2track___data___bdtgQELike_Q2QE___reconstructed")
lows = {}
highs = {}
for j in range(1,h2D_data.GetNbinsY()):
	lows[j] = h2D_data.GetYaxis().GetBinLowEdge(j)
	highs[j] = h2D_data.GetYaxis().GetBinLowEdge(j+1)
nbinY = h2D_data.GetNbinsY()
nbinX = h2D_data.GetNbinsX()

h_data = f.Get("h2D___2track___data___bdtgQELike_Q2QE___reconstructed").Projection("data",1,bin_i,bin_i,"")
h_qelike = f.Get("h2D___2track___qelike___bdtgQELike_Q2QE___reconstructed").Projection("qelike",1,bin_i,bin_i,"")
h_1chargedpion = f.Get("h2D___2track___1chargedpion___bdtgQELike_Q2QE___reconstructed").Projection("1chargedpion",1,bin_i,bin_i,"")
h_multipion = f.Get("h2D___2track___multipion___bdtgQELike_Q2QE___reconstructed").Projection("multipion",1,bin_i,bin_i,"")
h_other = f.Get("h2D___2track___other1neutralpion___bdtgQELike_Q2QE___reconstructed").Projection("other",1,bin_i,bin_i,"")

h_qelike.SetLineColor(TColor.GetColor(0,133,173))
h_1chargedpion.SetLineColor(TColor.GetColor(175,39,47))
h_multipion.SetLineColor(TColor.GetColor(234,170,0))
h_other.SetLineColor(TColor.GetColor(76,140,43))

h_qelike.SetFillColor(TColor.GetColor(0,133,173))
h_1chargedpion.SetFillColor(TColor.GetColor(175,39,47))
h_multipion.SetFillColor(TColor.GetColor(234,170,0))
h_other.SetFillColor(TColor.GetColor(76,140,43))

h_qelike.SetFillStyle(3001)
h_1chargedpion.SetFillStyle(3001)
h_multipion.SetFillStyle(3001)
h_other.SetFillStyle(3001)

for i in range(1,nbinX+1):
	counts_qelike = h_qelike.GetBinContent(i)
	counts_1chargedpion = h_1chargedpion.GetBinContent(i)
	counts_multipion = h_multipion.GetBinContent(i)
	counts_other = h_other.GetBinContent(i)
	counts_all = counts_qelike+counts_1chargedpion+counts_multipion+counts_other
	
	if counts_all != 0:
		h_qelike.SetBinContent(i,counts_qelike/counts_all)
		h_1chargedpion.SetBinContent(i,counts_1chargedpion/counts_all)
		h_multipion.SetBinContent(i,counts_multipion/counts_all)
		h_other.SetBinContent(i,counts_all/counts_all)
	else:
		h_qelike.SetBinContent(i,0)
		h_1chargedpion.SetBinContent(i,0)
		h_multipion.SetBinContent(i,0)
		h_other.SetBinContent(i,0)

xmin = 0.0
xmax = 1.0
centerX = (xmax+xmin)/2

h_data.GetXaxis().SetRangeUser(xmin,xmax)
h_qelike.GetXaxis().SetRangeUser(xmin,xmax)
h_1chargedpion.GetXaxis().SetRangeUser(xmin,xmax)
h_multipion.GetXaxis().SetRangeUser(xmin,xmax)
h_other.GetXaxis().SetRangeUser(xmin,xmax)

title = "2track:"+" "+str(lows[bin_i])+" #leq "+"Q_{2}QE"+" < "+str(highs[bin_i])

h_data.SetTitle(title)
h_data.GetYaxis().SetTitle("Bin Relative Contribution")
h_data.GetXaxis().CenterTitle(True)
h_data.GetYaxis().CenterTitle(True)
h_data.SetMarkerStyle(8)
h_data.SetLineWidth(2)
h_data.SetLabelFont(42)
h_data.SetTitleFont(42)
h_data.SetLabelSize(0.03,"x");
h_data.SetTitleSize(0.04,"x");
h_data.SetLabelSize(0.03,"y");
h_data.SetTitleSize(0.04,"y");
h_data.SetTickLength(0.01, "Y");
h_data.SetTickLength(0.02, "X");
h_data.SetNdivisions(510, "XYZ");

leg = CCQELegend(centerX+0.2,0.15,xmax-0.06,0.31)
leg.SetNColumns(1)
leg.AddEntry(h_qelike,"QELike",'f')
leg.AddEntry(h_1chargedpion,"Single #pi^{+/-} in FS","f")
leg.AddEntry(h_multipion,"N#pi in FS","f")
leg.AddEntry(h_other,"Other","f")

stack = THStack("stack","stack")
stack.Add(h_qelike)
stack.Add(h_1chargedpion)
stack.Add(h_multipion)
stack.Add(h_other)

h_data.Reset()
h_data.Draw("hist")  # need to this to get the axis titles from data
stack.Draw("hist same")
h_data.GetXaxis().SetRangeUser(0.0, 1)

text = TLatex(xmin+0.85*(xmax-xmin),0.275,"MINER#nuA Preliminary")
text.SetTextAlign(22)
text.SetTextColor(ROOT.kRed)
text.SetTextFont(13)
text.SetTextSize(25)

text.Draw()
leg.Draw()
cc.SetLeftMargin(0.12)
cc.SetBottomMargin(0.12)
cc.RedrawAxis()
cc.Draw()
cc.Print("SB_NuConfig_bdtg_MAD_2track_me1N_1_testing/bdtgQELike_proportional_"+str(bin_i)+".png")
cc.Close()

del h2D_data
del h_data
del h_qelike
del h_1chargedpion
del h_multipion
del h_other
del stack
del leg
del text
del dmax
del smax
del lows
del highs
del title
del POTScale
del mcPOTprescaled
del dataPOT
del h_pot
del cc
del keys
del dirname
del filename
del noData
del process
del scaleX
del scaleY
del i
del f
