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
	leg.SetFillStyle(0)
	leg.SetBorderSize(1)
	leg.SetTextSize(0.035)
	return leg


tracks = sys.argv[1]
bin_i = int(sys.argv[2])
tag = ""
if len(sys.argv) == 4: 
	tag = "_"+sys.argv[3]

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

h2D_data = f.Get("h2D___"+tracks+tag+"___data___bdtgQELike_Q2QE___reconstructed")
lows = {}
highs = {}
for j in range(1,h2D_data.GetNbinsY()):
	lows[j] = h2D_data.GetYaxis().GetBinLowEdge(j)
	highs[j] = h2D_data.GetYaxis().GetBinLowEdge(j+1)
nbinY = h2D_data.GetNbinsY()
nbinX = h2D_data.GetNbinsX()

h_data = f.Get("h2D___"+tracks+tag+"___data___bdtgQELike_Q2QE___reconstructed").Projection("data",1,bin_i,bin_i,"")
h_qelike = f.Get("h2D___"+tracks+tag+"___qelike___bdtgQELike_Q2QE___reconstructed").Projection("qelike",1,bin_i,bin_i,"")
h_1chargedpion = f.Get("h2D___"+tracks+tag+"___1chargedpion___bdtgQELike_Q2QE___reconstructed").Projection("1chargedpion",1,bin_i,bin_i,"")
h_multipion = f.Get("h2D___"+tracks+tag+"___multipion___bdtgQELike_Q2QE___reconstructed").Projection("multipion",1,bin_i,bin_i,"")
if tracks == "2track":
	h_other = f.Get("h2D___"+tracks+tag+"___other1neutralpion___bdtgQELike_Q2QE___reconstructed").Projection("other",1,bin_i,bin_i,"")
else:
	h_1neutralpion = f.Get("h2D___"+tracks+tag+"___1neutralpion___bdtgQELike_Q2QE___reconstructed").Projection("1neutralpion",1,bin_i,bin_i,"")
	h_other = f.Get("h2D___"+tracks+tag+"___other___bdtgQELike_Q2QE___reconstructed").Projection("other",1,bin_i,bin_i,"")
	

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

h_data.Scale(1,"width")
h_qelike.Scale(POTScale,"width")
h_1chargedpion.Scale(POTScale,"width")
h_multipion.Scale(POTScale,"width")
h_other.Scale(POTScale,"width")
if tracks == "1track": h_1neutralpion.Scale(POTScale,"width")

xmin = 0
xmax = 1

h_data.GetXaxis().SetRangeUser(xmin,xmax)
h_qelike.GetXaxis().SetRangeUser(xmin,xmax)
h_1chargedpion.GetXaxis().SetRangeUser(xmin,xmax)
h_multipion.GetXaxis().SetRangeUser(xmin,xmax)
h_other.GetXaxis().SetRangeUser(xmin,xmax)
if tracks == "1track": h_1neutralpion.GetXaxis().SetRangeUser(xmin,xmax)

title = tracks+": "+str(lows[bin_i])+" #leq "+"Q_{2}QE"+" < "+str(highs[bin_i])
if len(sys.argv) == 4:
	title = title+" (w/ MultiPion Cut)"

h_data.SetTitle(title)
h_data.GetYaxis().SetTitle("Counts/unit (bin width normalized)")
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

centerX = (xmax+xmin)/2

leg = CCQELegend(centerX-0.15,0.73,centerX+0.09,0.895)
leg.SetNColumns(1)
if not noData: leg.AddEntry(h_data,"Data","pe")
leg.AddEntry(h_qelike,"QELike",'f')
leg.AddEntry(h_1chargedpion,"Single #pi^{+/-} in FS","f")
if tracks == "1track": leg.AddEntry(h_1neutralpion,"Single #pi^{0} in FS","f")
leg.AddEntry(h_multipion,"N#pi in FS","f")
leg.AddEntry(h_other,"Other","f")
leg.SetTextSize(0.03)

stack = THStack("stack","stack")
stack.Add(h_qelike)
stack.Add(h_1chargedpion)
if tracks == "1track": stack.Add(h_1neutralpion)
stack.Add(h_multipion)
stack.Add(h_other)

dmax = h_data.GetMaximum()
if noData:
	dmax = 0.0
smax = stack.GetMaximum()
if smax > dmax:
	h_data.SetMaximum(smax*1.1)
	stack.SetMaximum(smax*1.1)
	tmax = smax
else:
	h_data.SetMaximum(dmax*1.1)
	stack.SetMaximum(dmax*1.1)
	tmax = dmax

if not noData: 
	h_data.Draw("PE")
	stack.Draw("hist same")
	h_data.GetXaxis().SetRangeUser(0, 1)
else:
	h_data.Reset()
	h_data.Draw("hist")  # need to this to get the axis titles from data
	stack.Draw("hist same")
	h_data.GetXaxis().SetRangeUser(0, 1)
if not noData: 
	h_data.Draw("PE same")
	
text = TLatex(xmin+0.875*(xmax-xmin),0.975*1.1*tmax,"MINER#nuA Preliminary")
text.SetTextAlign(22)
text.SetTextColor(ROOT.kRed)
text.SetTextFont(13)
text.SetTextSize(20)

text.Draw()
leg.Draw()
cc.SetLeftMargin(0.12)
cc.SetBottomMargin(0.12)
cc.RedrawAxis()
cc.Draw()
if tracks == "2track":
	cc.Print("SB_NuConfig_bdtg_MAD"+tag+"_"+tracks+"_me1N_1_testing/bdtgQELike_"+tracks+"_"+str(bin_i)+".png")
else:
	cc.Print("SB_NuConfig_bdtg_MAD"+tag+"_"+tracks+"_me1N_1/bdtgQELike_"+tracks+"_"+str(bin_i)+".png")
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
del tmax
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
del scaleX
del scaleY
del bin_i
del f
