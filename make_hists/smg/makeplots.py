import sys,os,math
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

filename = "SB_NuConfig_bdtg_MAD_2track_me1N_1_testing.root"
noData = True;
variables = ["ptmu","pzmu","Q2QE","bdtgQELike","bdtg1ChargedPion",
	"bdtg1NeutralPion","bdtgMultiPion","bdtgOther"]

scaleX = ["Q2QE"]
scaleY = ["Q2QE","bdtg1NeutralPion","bdtgQELike"]

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

variable_limits = {
	"bdtgQELike":[0.0,1.0]
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

for var in variables:

	cc = CCQECanvas("canvas","canvas")
	if var in scaleX: cc.SetLogx()
	if var in scaleY: cc.SetLogy()

	h_data = f.Get("h___2track___data___"+var+"___reconstructed")
	h_qelike = f.Get("h___2track___qelike___"+var+"___reconstructed")
	h_1chargedpion = f.Get("h___2track___1chargedpion___"+var+"___reconstructed")
	h_multipion = f.Get("h___2track___multipion___"+var+"___reconstructed")
	h_other = f.Get("h___2track___other1neutralpion___"+var+"___reconstructed")

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

	h_qelike.Scale(POTScale,"width")
	h_1chargedpion.Scale(POTScale,"width")
	h_multipion.Scale(POTScale,"width")
	h_other.Scale(POTScale,"width")

	nbins = h_data.GetNbinsX()
	if var not in variable_limits.keys():
		xmin = h_data.GetBinLowEdge(1)
		xmax = h_data.GetBinLowEdge(nbins+1)
	else:
		xmin = variable_limits[var][0]
		xmax = variable_limits[var][1]
		
	h_data.GetXaxis().SetRangeUser(xmin,xmax)
	h_qelike.GetXaxis().SetRangeUser(xmin,xmax)
	h_1chargedpion.GetXaxis().SetRangeUser(xmin,xmax)
	h_multipion.GetXaxis().SetRangeUser(xmin,xmax)
	h_other.GetXaxis().SetRangeUser(xmin,xmax)
		
	centerX = (xmax+xmin)/2

	title = "2track:"+" "+var

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

	#leg = CCQELegend(centerX-0.15,0.73,centerX+0.09,0.89)
	leg = CCQELegend(0.705,0.73,0.942,0.89)
	leg.SetNColumns(1)
	if not noData: leg.AddEntry(h_data,"Data","pe")
	leg.AddEntry(h_qelike,"QELike",'f')
	leg.AddEntry(h_1chargedpion,"Single #pi^{+/-} in FS","f")
	leg.AddEntry(h_multipion,"N#pi in FS","f")
	leg.AddEntry(h_other,"Other","f")

	stack = THStack("stack","stack")
	stack.Add(h_qelike)
	stack.Add(h_1chargedpion)
	stack.Add(h_multipion)
	stack.Add(h_other)

	dmax = h_data.GetMaximum()
	smax = stack.GetMaximum()
	if noData:
		dmax = 0.0
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
		h_data.GetXaxis().SetRangeUser(xmin, xmax)
	else:
		h_data.Reset()
		h_data.Draw("hist")  # need to this to get the axis titles from data
		stack.Draw("hist same")
		h_data.GetXaxis().SetRangeUser(xmin, xmax)
	if not noData: 
		h_data.Draw("PE same")
		
	text = TLatex(0.852,0.714,"MINER#nuA Preliminary")
	text.SetNDC()
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
	cc.Print("SB_NuConfig_bdtg_MAD_2track_me1N_1_testing/2track_"+var+".png")
	cc.Close()

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
	del title
	del cc


































