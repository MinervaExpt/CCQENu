import sys,os,math
import ROOT
import commentjson
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
	
fn = open(sys.argv[1])
config = commentjson.load(fn)
fn.close()

prescale = config["prescale"]
if len(sys.argv) == 3:
	prescale = sys.argv[2]
#tracks = sys.argv[1]
#tag = ""
#if len(sys.argv) == 3: 
#	tag = "_"+sys.argv[2]
	
filename = "SB_"+sys.argv[1].split("/")[-1].split(".")[0]+"_"+prescale+".root"
	
noData = True;
variables = config["AnalyzeVariables"]
#variables = ["ptmu","pzmu","Q2QE","bdtgQELike","bdtg1ChargedPion",
#	"bdtg1NeutralPion","bdtgMultiPion","bdtgOther"]

scaleX = ["Q2QE"]
scaleY = []#"Q2QE"]#,"bdtg1NeutralPion","bdtgQELike"]

colors = {
    "qelike":TColor.GetColor(0,133,173),
    "1chargedpion":TColor.GetColor(175,39,47),
    "1neutralpion":TColor.GetColor(76,140,43),
    "multipion":TColor.GetColor(234,170,0),
    "multipionother":TColor.GetColor(234,170,0),
    "other":TColor.GetColor(82,37,6)
}
legend_labels = {
    "qelike":"QELike",
    "1chargedpion":"Single #pi^{+/-} in FS",
    "1neutralpion":"Single #pi^{0} in FS",
    "multipion":"N#pi in FS",
    "multipionother":"N#pi in FS + Other",
    "other":"Other"
}

variable_limits = {
	"bdtgQELike":[0.0,1.0],
	"bdtgMultiPion":[0.0,1.0],
	"bdtgResponse":[0.0,1.0]
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

for sample in config["runsamples"]:
	categories = [config["signal"][sample]] + config["background"][sample]
	for var in variables:

		cc = CCQECanvas("canvas","canvas")
		if var in scaleX: cc.SetLogx()
		if var in scaleY: cc.SetLogy()
		title = sample+": "+var
		#if len(sys.argv) == 3:
		#	title = title+" (w/ MultiPion Cut)"

		h_data = f.Get("h___"+sample+"___data___"+var+"___reconstructed")
		h_data.SetLineColor(TColor.GetColor(0,0,0))
		h_data.Scale(1,"width")
		nbins = h_data.GetNbinsX()
		if var not in variable_limits.keys():
			xmin = h_data.GetBinLowEdge(1)
			xmax = h_data.GetBinLowEdge(nbins+1)
		else:
			xmin = variable_limits[var][0]
			xmax = variable_limits[var][1]
		h_data.GetXaxis().SetRangeUser(xmin,xmax)
		h_data.SetMinimum(0)
		
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
		h_data.SetTickLength(0.01,"Y");
		h_data.SetTickLength(0.02,"X");
		h_data.SetNdivisions(510,"XYZ");
		
		hs = {};
		for cat in categories:
			hs[cat] = f.Get("h___"+sample+"___"+cat+"___"+var+"___reconstructed")
			hs[cat].SetLineColor(colors[cat])
			hs[cat].SetFillColor(colors[cat])
			hs[cat].SetFillStyle(3001)
			hs[cat].Scale(POTScale,"width")
			hs[cat].GetXaxis().SetRangeUser(xmin,xmax)
			
		centerX = (xmax+xmin)/2

		#leg = CCQELegend(centerX-0.15,0.73,centerX+0.09,0.89)
		leg = CCQELegend(0.725,0.73,0.942,0.89)
		leg.SetNColumns(1)
		if not noData: leg.AddEntry(h_data,"Data","pe")
		for cat in categories:
			leg.AddEntry(hs[cat],legend_labels[cat],"f")
		leg.SetTextSize(0.03)

		stack = THStack("stack","stack")
		for cat in categories:
			stack.Add(hs[cat])

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
		cc.Print(dirname+"/"+var+"_"+sample+".png")
		cc.Close()

		del h_data
		del hs
		del stack
		del leg
		del text
		del tmax
		del dmax
		del smax
		del title
		del cc


































