import sys,os
import ROOT
from ROOT import gROOT,gStyle,TFile,THStack,TH1D,TCanvas,TColor,TObjArray,TH2F,THStack,TFractionFitter,TLegend,TLatex,TString,TText,TPad


ROOT.gStyle.SetOptStat(0)

def CCQECanvas(name,title,xsize=1000,ysize=750):
	c2 = ROOT.TCanvas(name,title,xsize,ysize)
	c2.SetLeftMargin(0.20)
	c2.SetRightMargin(0.05)
	c2.SetBottomMargin(0.15)
	return c2

def CCQELegend(xlow,ylow,xhigh,yhigh):
	leg = ROOT.TLegend(xlow,ylow,xhigh,yhigh)
	leg.SetFillStyle(0)
	leg.SetBorderSize(1)
	leg.SetTextSize(0.035)
	return leg

tracks = sys.argv[1]
bin_i = int(sys.argv[2])
tag = ""
if len(sys.argv) == 4: 
	tag = "_"+sys.argv[3]
print(tag)

if tracks == "2track":
	filename = "SB_NuConfig_bdtg_MAD"+tag+"_2track_me1N_1_testing.root"
if tracks == "1track":
	filename = "SB_NuConfig_bdtg_MAD"+tag+"_1track_me1N_1.root"
noData = True;

scaleX = ["Q2QE"]
scaleY = ["Q2QE"]

colors = {
    "qelike":TColor.GetColor(0,133,173),
    "1chargedpion":TColor.GetColor(175,39,47),
    "1neutralpion":TColor.GetColor(76,140,43),
    "multipion":TColor.GetColor(234,170,0),
    "other":TColor.GetColor(82,37,6)
}
legend_labels = {
    "qelike":"QELike",
    "1chargedpion":"Single #pi^{+/-} in FS",
    "1neutralpion":"Single #pi^{0} in FS",
    "multipion":"N#pi in FS",
    "other":"Other"
}

f = TFile.Open(filename,"READONLY")
dirname = filename.replace(".root","")
if not os.path.exists(dirname): os.mkdir(dirname)

keys = f.GetListOfKeys()

h_pot = TH1D()
h_pot = f.Get("POT_summary")
dataPOT = h_pot.GetBinContent(1)
mcPOTprescaled = h_pot.GetBinContent(3)
POTScale = dataPOT / mcPOTprescaled

cc = CCQECanvas("canvas","canvas")

if tracks == "2track":
	pad_qelike       = TPad("qelike",       "qelike",       0.0, 0.45, 0.50, 0.90, 21)
	pad_1chargedpion = TPad("1chargedpion", "1chargedpion", 0.5, 0.45, 1.00, 0.90, 21)
	pad_multipion    = TPad("multipion",    "multipion",    0.0, 0.00, 0.50, 0.45, 21)
	pad_other        = TPad("other",        "other",        0.5, 0.00, 1.00, 0.45, 21)
	pad_title        = TPad("title",        "title",        0.0, 0.90, 1.00, 1,00, 21)
else:
	pad_qelike       = TPad("qelike",       "qelike",       0.000, 0.45, 0.333, 0.90, 21)
	pad_1chargedpion = TPad("1chargedpion", "1chargedpion", 0.333, 0.45, 0.666, 0.90, 21)
	pad_1neutralpion = TPad("1neutralpion", "1neutralpion", 0.666, 0.45, 1.000, 0.90, 21)
	pad_multipion    = TPad("multipion",    "multipion",    0.167, 0.00, 0.500, 0.45, 21)
	pad_other        = TPad("other",        "other",        0.500, 0.00, 0.833, 0.45, 21)
	pad_title        = TPad("title",        "title",        0.000, 0.90, 1.000, 1,00, 21)

pad_qelike.SetFillColor(0)
pad_1chargedpion.SetFillColor(0)
if tracks == "1track": pad_1neutralpion.SetFillColor(0)
pad_multipion.SetFillColor(0)
pad_other.SetFillColor(0)

pad_qelike.Draw()
pad_1chargedpion.Draw()
if tracks == "1track": pad_1neutralpion.Draw()
pad_multipion.Draw()
pad_other.Draw()
pad_title.Draw()

h2D_data = f.Get("h2D___"+tracks+tag+"___data___bdtgQELike_Q2QE___reconstructed")
lows = {}
highs = {}
nbinY = h2D_data.GetNbinsY()
nbinX = h2D_data.GetNbinsX()
for j in range(1,nbinY):
	lows[j] = h2D_data.GetYaxis().GetBinLowEdge(j)
	highs[j] = h2D_data.GetYaxis().GetBinLowEdge(j+1)

h_data = f.Get("h2D___"+tracks+tag+"___data___bdtgQELike_Q2QE___reconstructed").Projection("data",1,bin_i,bin_i,"")
h_qelike = f.Get("h2D___"+tracks+tag+"___qelike___bdtgQELike_Q2QE___reconstructed").Projection("qelike",1,bin_i,bin_i,"")
h_1chargedpion = f.Get("h2D___"+tracks+tag+"___1chargedpion___bdtgQELike_Q2QE___reconstructed").Projection("1chargedpion",1,bin_i,bin_i,"")
h_multipion = f.Get("h2D___"+tracks+tag+"___multipion___bdtgQELike_Q2QE___reconstructed").Projection("multipion",1,bin_i,bin_i,"")
if tracks == "1track":
	h_1neutralpion = f.Get("h2D___"+tracks+tag+"___1neutralpion___bdtgQELike_Q2QE___reconstructed").Projection("1neutralpion",1,bin_i,bin_i,"")
	h_other = f.Get("h2D___"+tracks+tag+"___other___bdtgQELike_Q2QE___reconstructed").Projection("other",1,bin_i,bin_i,"")
else:
	h_other = f.Get("h2D___"+tracks+tag+"___other1neutralpion___bdtgQELike_Q2QE___reconstructed").Projection("other",1,bin_i,bin_i,"")
	

h_qelike.SetLineColor(TColor.GetColor(0,133,173))
h_1chargedpion.SetLineColor(TColor.GetColor(175,39,47))
h_multipion.SetLineColor(TColor.GetColor(234,170,0))
h_other.SetLineColor(colors["other"])
if tracks == "1track": h_1neutralpion.SetLineColor(colors["1neutralpion"])

h_qelike.SetFillColor(TColor.GetColor(0,133,173))
h_1chargedpion.SetFillColor(TColor.GetColor(175,39,47))
h_multipion.SetFillColor(TColor.GetColor(234,170,0))
h_other.SetFillColor(colors["other"])
if tracks == "1track": h_1neutralpion.SetFillColor(colors["1neutralpion"])

h_qelike.SetFillStyle(3001)
h_1chargedpion.SetFillStyle(3001)
h_multipion.SetFillStyle(3001)
h_other.SetFillStyle(3001)
if tracks == "1track": h_1neutralpion.SetFillStyle(3001)

xmin = 0.0
xmax = 1.0
h_qelike.GetXaxis().SetRangeUser(xmin,xmax)
h_1chargedpion.GetXaxis().SetRangeUser(xmin,xmax)
h_multipion.GetXaxis().SetRangeUser(xmin,xmax)
h_other.GetXaxis().SetRangeUser(xmin,xmax)
if tracks == "1track": h_1neutralpion.GetXaxis().SetRangeUser(xmin,xmax)

h_qelike.SetTitle("")
h_qelike.GetYaxis().SetRangeUser(0,1.005)
h_qelike.GetYaxis().SetTitle("Cumulative Counts")
h_qelike.GetXaxis().CenterTitle(True)
h_qelike.GetYaxis().CenterTitle(True)
h_qelike.SetMarkerStyle(8)
h_qelike.SetLineWidth(2)
h_qelike.SetLabelFont(42)
h_qelike.SetTitleFont(42)
h_qelike.SetLabelSize(0.03,"x")
h_qelike.SetTitleSize(0.05,"x")
h_qelike.SetLabelSize(0.03,"y")
h_qelike.SetTitleSize(0.05,"y")
h_qelike.SetTickLength(0.01, "Y")
h_qelike.SetTickLength(0.02, "X")
h_qelike.SetNdivisions(510, "XYZ")
h_qelike.SetStats(0)

h_1chargedpion.SetTitle("")
h_1chargedpion.GetYaxis().SetRangeUser(0,1.005)
h_1chargedpion.GetYaxis().SetTitle("Cumulative Counts")
h_1chargedpion.GetXaxis().CenterTitle(True)
h_1chargedpion.GetYaxis().CenterTitle(True)
h_1chargedpion.SetMarkerStyle(8)
h_1chargedpion.SetLineWidth(2)
h_1chargedpion.SetLabelFont(42)
h_1chargedpion.SetTitleFont(42)
h_1chargedpion.SetLabelSize(0.03,"x")
h_1chargedpion.SetTitleSize(0.05,"x")
h_1chargedpion.SetLabelSize(0.03,"y")
h_1chargedpion.SetTitleSize(0.05,"y")
h_1chargedpion.SetTickLength(0.01, "Y")
h_1chargedpion.SetTickLength(0.02, "X")
h_1chargedpion.SetNdivisions(510, "XYZ")
h_1chargedpion.SetStats(0)

if tracks == "1track":
	h_1neutralpion.SetTitle("")
	h_1neutralpion.GetYaxis().SetTitle("Cumulative Counts")
	h_1neutralpion.GetYaxis().SetRangeUser(0,1.005)
	h_1neutralpion.GetXaxis().CenterTitle(True)
	h_1neutralpion.GetYaxis().CenterTitle(True)
	h_1neutralpion.SetMarkerStyle(8)
	h_1neutralpion.SetLineWidth(2)
	h_1neutralpion.SetLabelFont(42)
	h_1neutralpion.SetTitleFont(42)
	h_1neutralpion.SetLabelSize(0.03,"x")
	h_1neutralpion.SetTitleSize(0.05,"x")
	h_1neutralpion.SetLabelSize(0.03,"y")
	h_1neutralpion.SetTitleSize(0.05,"y")
	h_1neutralpion.SetTickLength(0.01, "Y")
	h_1neutralpion.SetTickLength(0.02, "X")
	h_1neutralpion.SetNdivisions(510, "XYZ")
	h_1neutralpion.SetStats(0)

h_multipion.SetTitle("")
h_multipion.GetYaxis().SetTitle("Cumulative Counts")
h_multipion.GetYaxis().SetRangeUser(0,1.005)
h_multipion.GetXaxis().CenterTitle(True)
h_multipion.GetYaxis().CenterTitle(True)
h_multipion.SetMarkerStyle(8)
h_multipion.SetLineWidth(2)
h_multipion.SetLabelFont(42)
h_multipion.SetTitleFont(42)
h_multipion.SetLabelSize(0.03,"x")
h_multipion.SetTitleSize(0.05,"x")
h_multipion.SetLabelSize(0.03,"y")
h_multipion.SetTitleSize(0.05,"y")
h_multipion.SetTickLength(0.01, "Y")
h_multipion.SetTickLength(0.02, "X")
h_multipion.SetNdivisions(510, "XYZ")
h_multipion.SetStats(0)

h_other.SetTitle("")
h_other.GetYaxis().SetTitle("Cumulative Counts")
h_other.GetYaxis().SetRangeUser(0,1.005)
h_other.GetXaxis().CenterTitle(True)
h_other.GetYaxis().CenterTitle(True)
h_other.SetMarkerStyle(8)
h_other.SetLineWidth(2)
h_other.SetLabelFont(42)
h_other.SetTitleFont(42)
h_other.SetLabelSize(0.03,"x")
h_other.SetTitleSize(0.05,"x")
h_other.SetLabelSize(0.03,"y")
h_other.SetTitleSize(0.05,"y")
h_other.SetTickLength(0.01, "Y")
h_other.SetTickLength(0.02, "X")
h_other.SetNdivisions(510, "XYZ")
h_other.SetStats(0)

total_qelike = h_qelike.Integral(1,nbinX+1)
total_1chargedpion = h_1chargedpion.Integral(1,nbinX+1)
total_multipion = h_multipion.Integral(1,nbinX+1)
total_other = h_other.Integral(1,nbinX+1)
if tracks == "1track": 
	total_1neutralpion = h_1neutralpion.Integral(1,nbinX+1)

sums_qelike = {}
sums_1chargedpion = {}
sums_multipion = {}
sums_other = {}
if tracks == "1track": 
	sums_1neutralpion = {}

for i in range(1,nbinX+1):
	sums_qelike[i] = h_qelike.Integral(i,nbinX+1)
	sums_1chargedpion[i] = h_1chargedpion.Integral(i,nbinX+1)
	sums_multipion[i] = h_multipion.Integral(i,nbinX+1)
	sums_other[i] = h_other.Integral(i,nbinX+1)
	if tracks == "1track": 
		sums_1neutralpion[i] = h_1neutralpion.Integral(i,nbinX+1)

for i in range(1,nbinX+1):	
	h_qelike.SetBinContent(i,sums_qelike[i]/total_qelike)
	h_1chargedpion.SetBinContent(i,sums_1chargedpion[i]/total_1chargedpion)
	h_multipion.SetBinContent(i,sums_multipion[i]/total_multipion)
	h_other.SetBinContent(i,sums_other[i]/total_other)
	if tracks == "1track":
		h_1neutralpion.SetBinContent(i,sums_1neutralpion[i]/total_1neutralpion)


pad_qelike.cd()
pad_qelike.SetLeftMargin(0.1)
pad_qelike.SetBottomMargin(0.12)
pad_qelike.SetRightMargin(0.05)
pad_qelike.SetTopMargin(0.1)
#h_qelike.GetCumulative(False).Draw("hist")
h_qelike.Draw("hist")
title_qelike = TLatex(0.5,1.06,legend_labels["qelike"])
title_qelike.SetTextSize(0.06)
title_qelike.SetTextAlign(21)
title_qelike.SetTextFont(42)
title_qelike.Draw()

pad_1chargedpion.cd()
pad_1chargedpion.SetLeftMargin(0.1)
pad_1chargedpion.SetBottomMargin(0.12)
pad_1chargedpion.SetRightMargin(0.05)
pad_1chargedpion.SetTopMargin(0.1)
#h_1chargedpion.GetCumulative(False).Draw("hist")
h_1chargedpion.Draw("hist")
title_1chargedpion = TLatex(0.5,1.06,legend_labels["1chargedpion"])
title_1chargedpion.SetTextSize(0.06)
title_1chargedpion.SetTextAlign(21)
title_1chargedpion.SetTextFont(42)
title_1chargedpion.Draw()

if tracks == "1track":
	pad_1neutralpion.cd()
	pad_1neutralpion.SetLeftMargin(0.1)
	pad_1neutralpion.SetBottomMargin(0.12)
	pad_1neutralpion.SetRightMargin(0.05)
	pad_1neutralpion.SetTopMargin(0.1)
	#h_1neutralpion.GetCumulative(False).Draw("hist")
	h_1neutralpion.Draw("hist")
	title_1neutralpion = TLatex(0.5,1.06,legend_labels["1chargedpion"])
	title_1neutralpion.SetTextSize(0.06)
	title_1neutralpion.SetTextAlign(21)
	title_1neutralpion.SetTextFont(42)
	title_1neutralpion.Draw()

pad_multipion.cd()
pad_multipion.SetLeftMargin(0.1)
pad_multipion.SetBottomMargin(0.12)
pad_multipion.SetRightMargin(0.05)
pad_multipion.SetTopMargin(0.1)
#h_multipion.GetCumulative(False).Draw("hist")
h_multipion.Draw("hist")
title_multipion = TLatex(0.5,1.06,legend_labels["multipion"])
title_multipion.SetTextSize(0.06)
title_multipion.SetTextAlign(21)
title_multipion.SetTextFont(42)
title_multipion.Draw()

pad_other.cd()
pad_other.SetLeftMargin(0.1)
pad_other.SetBottomMargin(0.12)
pad_other.SetRightMargin(0.05)
pad_other.SetTopMargin(0.1)
#h_other.GetCumulative(False).Draw("hist")
h_other.Draw("hist")
title_other = TLatex(0.5,1.06,legend_labels["other"])
title_other.SetTextSize(0.06)
title_other.SetTextAlign(21)
title_other.SetTextFont(42)
title_other.Draw()
	
#text = TLatex(xmin+0.875*(xmax-xmin),0.975*1.1*tmax,"MINER#nuA Preliminary")
#text.SetTextAlign(22)
#text.SetTextColor(ROOT.kRed)
#text.SetTextFont(13)
#text.SetTextSize(20)

title = "Reverse Cumulative Plots | "+tracks+" | "+str(lows[bin_i])+" #leq "+"Q_{2}QE"+" < "+str(highs[bin_i])
if len(sys.argv) == 4:
	title = title+" (w/ MultiPion Cut)"
title_text = TLatex(0.5,0.5,title)
title_text.SetTextAlign(22)
title_text.SetTextColor(ROOT.kBlack)
title_text.SetTextSize(0.4)
title_text.SetTextFont(42)
pad_title.cd()
title_text.Draw()

#text.Draw()
#leg.Draw()

cc.RedrawAxis()
cc.Draw()
if tracks == "1track":
	cc.Print("SB_NuConfig_bdtg_MAD"+tag+"_"+tracks+"_me1N_1/bdtgQELike_reverseCumulatives_"+tracks+"_"+str(bin_i)+".png")
else:
	cc.Print("SB_NuConfig_bdtg_MAD"+tag+"_"+tracks+"_me1N_1_testing/bdtgQELike_reverseCumulatives_"+tracks+"_"+str(bin_i)+".png")
pad_qelike.Close()
pad_1chargedpion.Close()
if tracks == "1track": pad_1neutralpion.Close()
pad_multipion.Close()
pad_other.Close()
cc.Close()

del h2D_data
del h_qelike
del h_1chargedpion
del h_multipion
del h_other
del lows
del highs
del title_text
del POTScale
del mcPOTprescaled
del dataPOT
del h_pot
del cc
del keys
del dirname
del filename
del noData
del scaleX
del scaleY
del bin_i
del f
