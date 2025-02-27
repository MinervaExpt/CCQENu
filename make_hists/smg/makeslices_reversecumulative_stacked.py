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
	#leg.SetFillStyle(0)
	leg.SetFillColor(ROOT.kWhite)
	leg.SetBorderSize(1)
	leg.SetTextSize(0.035)
	return leg

tracks = sys.argv[1]
bin_i = int(sys.argv[2])
filename = "SB_NuConfig_bdtg_MAD_2track_me1N_1_testing.root"
if tracks == "1track": filename = "SB_NuConfig_bdtg_MAD_2track_me1N_1.root"

scaleX = ["Q2QE"]
scaleY = ["Q2QE"]

colors = {
    "qelike":TColor.GetColor(0,133,173),#ROOT.kMagenta-4,
    "1chargedpion":TColor.GetColor(175,39,47),#ROOT.kBlue-7,
    "1neutralpion":TColor.GetColor(76,140,43),
    "multipion":TColor.GetColor(234,170,0),#ROOT.kRed-4,
    "other":TColor.GetColor(76,140,43)#ROOT.kGreen-3
}
if tracks == "2tracks": colors["other"] = TColor.GetColor(82,37,6)
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

h2D_data = f.Get("h2D___"+tracks+"___data___bdtgQELike_Q2QE___reconstructed")
lows = {}
highs = {}
nbinY = h2D_data.GetNbinsY()
nbinX = h2D_data.GetNbinsX()
for j in range(1,nbinY):
	lows[j] = h2D_data.GetYaxis().GetBinLowEdge(j)
	highs[j] = h2D_data.GetYaxis().GetBinLowEdge(j+1)

h_data = f.Get("h2D___"+tracks+"___data___bdtgQELike_Q2QE___reconstructed").Projection("data",1,bin_i,bin_i,"")
h_qelike = f.Get("h2D___"+tracks+"___qelike___bdtgQELike_Q2QE___reconstructed").Projection("qelike",1,bin_i,bin_i,"")
h_1chargedpion = f.Get("h2D___"+tracks+"___1chargedpion___bdtgQELike_Q2QE___reconstructed").Projection("1chargedpion",1,bin_i,bin_i,"")
h_multipion = f.Get("h2D___"+tracks+"___multipion___bdtgQELike_Q2QE___reconstructed").Projection("multipion",1,bin_i,bin_i,"")
if tracks == "2track":
	h_other = f.Get("h2D___"+tracks+"___other1neutralpion___bdtgQELike_Q2QE___reconstructed").Projection("other",1,bin_i,bin_i,"")
else:
	h_1neutralpion = f.Get("h2D___"+tracks+"___other___bdtgQELike_Q2QE___reconstructed").Projection("other",1,bin_i,bin_i,"")
	h_other = f.Get("h2D___"+tracks+"___other___bdtgQELike_Q2QE___reconstructed").Projection("other",1,bin_i,bin_i,"")

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

xmin = 0
xmax = 1
h_qelike.GetXaxis().SetRangeUser(xmin,xmax)
h_1chargedpion.GetXaxis().SetRangeUser(xmin,xmax)
h_multipion.GetXaxis().SetRangeUser(xmin,xmax)
h_other.GetXaxis().SetRangeUser(xmin,xmax)
if tracks == "1track": h_1neutralpion.GetXaxis().SetRangeUser(xmin,xmax)

title = "Reverse Cumulative | "+tracks+" | "+str(lows[bin_i])+" #leq "+"Q_{2}QE"+" < "+str(highs[bin_i])

h_data.SetTitle(title)
h_data.GetYaxis().SetTitle("Signal Proportion")
h_data.GetXaxis().CenterTitle(True)
h_data.GetYaxis().CenterTitle(True)
h_data.GetYaxis().SetRangeUser(0.0, 1)
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
h_other.SetStats(0)

for i in range(1,nbinX+1):
	sum_qelike = h_qelike.Integral(i,nbinX+1)
	sum_1chargedpion = h_1chargedpion.Integral(i,nbinX+1)
	sum_multipion = h_multipion.Integral(i,nbinX+1)
	sum_other = h_other.Integral(i,nbinX+1)
	sum_total = sum_qelike+sum_1chargedpion+sum_multipion+sum_other
	if tracks == "1track": 
		sum_1neutralpion = h_1neutralpion.Integral(i,nbinX+1)
	
	if sum_total != 0:
		h_qelike.SetBinContent(i,sum_qelike/sum_total)
		h_1chargedpion.SetBinContent(i,sum_1chargedpion/sum_total)
		h_multipion.SetBinContent(i,sum_multipion/sum_total)
		h_other.SetBinContent(i,sum_other/sum_total)
		if tracks == "1track": h_1neutralpion.SetBinContent(i,sum_1neutralpion/sum_total)
	else:
		h_qelike.SetBinContent(i,0)
		h_1chargedpion.SetBinContent(i,0)
		h_multipion.SetBinContent(i,0)
		h_other.SetBinContent(i,0)
		if tracks == "1track": h_1neutralpion.SetBinContent(i,0)


h_data.GetXaxis().SetRangeUser(xmin,xmax)
h_qelike.GetXaxis().SetRangeUser(xmin,xmax)
h_1chargedpion.GetXaxis().SetRangeUser(xmin,xmax)
h_multipion.GetXaxis().SetRangeUser(xmin,xmax)
h_other.GetXaxis().SetRangeUser(xmin,xmax)
if tracks == "1track": h_1neutralpion.GetXaxis().SetRangeUser(xmin,xmax)

xmin = 0
xmax = 1
centerX = (xmax+xmin)/2

leg = CCQELegend(centerX+0.2,0.15,xmax-0.06,0.3)
leg.SetNColumns(1)
leg.AddEntry(h_qelike,"QELike",'f')
leg.AddEntry(h_1chargedpion,"Single #pi^{+/-} in FS","f")
leg.AddEntry(h_multipion,"N#pi in FS","f")
if tracks == "1track": leg.AddEntry(h_1neutralpion,"Single #pi^{0} in FS","f")
leg.AddEntry(h_other,"Other","f")

stack = THStack("stack","stack")
stack.Add(h_qelike)
stack.Add(h_1chargedpion)
stack.Add(h_multipion)
if tracks == "1track": stack.Add(h_1neutralpion)
stack.Add(h_other)

h_data.SetMaximum(1)
stack.SetMaximum(1)

text = TLatex(xmin+0.85*(xmax-xmin),0.25,"MINER#nuA Preliminary")
text.SetTextAlign(22)
text.SetTextColor(ROOT.kRed)
text.SetTextFont(13)
text.SetTextSize(25)

h_data.Reset()
h_data.Draw("hist")  # need to this to get the axis titles from data
stack.Draw("hist same")
leg.Draw()
text.Draw()
cc.SetLeftMargin(0.12)
cc.SetBottomMargin(0.12)
cc.RedrawAxis()
cc.Draw()
cc.Print("SB_NuConfig_bdtg_MAD_"+tracks+"_me1N_1_testing/bdtgQELike_reversecumulative_proportional_"+str(bin_i)+".png")
cc.Close()

del h2D_data
del h_qelike
del h_1chargedpion
del h_multipion
del h_other
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
del scaleX
del scaleY
del bin_i
del f
