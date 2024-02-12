import ROOT
from ROOT import TCanvas, TPad, TFile, TPaveLabel, TPaveText, TH1F, TH2F, TLegend
from ROOT import gROOT
from array import array

c1 = TCanvas( 'c1', 'Histogram Drawing Options', 200, 10, 1200, 700 )
c1.SetGrid()
c1.SetLogx()

rfile = "SB_NuConfig_mult1pBDTG_me1N_1.root"
f = TFile(rfile)

h_qelike = gROOT.FindObject( "h2D___Mult1p___qelike___bdtgQELike_Q2QE___reconstructed" )
h_1chargedpion = gROOT.FindObject( "h2D___Mult1p___1chargedpion___bdtgQELike_Q2QE___reconstructed" )
h_1neutralpion = gROOT.FindObject( "h2D___Mult1p___1neutralpion___bdtgQELike_Q2QE___reconstructed" )
h_multipion = gROOT.FindObject( "h2D___Mult1p___multipion___bdtgQELike_Q2QE___reconstructed" )
h_other = gROOT.FindObject( "h2D___Mult1p___other___bdtgQELike_Q2QE___reconstructed" )

nbinX = h_qelike.GetNbinsX()
nbinY = h_qelike.GetNbinsY()

yEdges = []
for j in range(1,nbinY+2):
	yEdges.append(h_qelike.GetYaxis().GetBinLowEdge(j))
yEdges[0] = 0.01

h_start = TH1F( 'start', 'QELike BDTG Response Cut Metrics for Q2QE', nbinY, array('f',yEdges))
h_start.SetXTitle("Q2QE (GeV^2)")
h_start.SetYTitle("(purity)*(efficiency)")
h_start.GetXaxis().SetTitleSize(0.05)
h_start.GetYaxis().SetTitleSize(0.05)
h_start.SetAxisRange(0.25,0.75,"Y")
h_start.SetFillColor(0)
h_start.SetStats(0)
h_start.DrawCopy()

hs = []

colors = [ROOT.kRed+1,ROOT.kOrange-3,ROOT.kYellow+1,ROOT.kGreen+1,ROOT.kBlue,ROOT.kMagenta]
for i in range(5,11):
	
	cut = (i-1)/20
	hs.append(TH1F( 'cut '+str(cut), 'BDTG QELike Response >= '+str(cut), nbinY, array('f',yEdges)))
	hs[i-5].SetLineColor(colors[i-5])
	hs[i-5].SetLineWidth(2)
	hs[i-5].SetFillColor(0)
	hs[i-5].SetStats(0)
	# Fill
	for j in range(1,nbinY+1):
		denom_purity = (h_qelike.Integral(i,nbinX,j,j)+
				            h_1chargedpion.Integral(i,nbinX,j,j)+
				            h_1neutralpion.Integral(i,nbinX,j,j)+
				            h_multipion.Integral(i,nbinX,j,j)+
				            h_other.Integral(i,nbinX,j,j))
		denom_eff = h_qelike.Integral(1,nbinX,j,j)
		if denom_purity > 0 and denom_eff > 0:
			n_purity = h_qelike.Integral(i,nbinX,j,j)/denom_purity
			n_eff = h_qelike.Integral(i,nbinX,j,j)/denom_eff
			n = n_purity*n_eff
			hs[i-5].SetBinContent(j,n)
	# Draw
	hs[i-5].DrawCopy("Same")

c1.cd()
############## Legend ##############
#legend = TLegend(0.3,0.2,0.5,0.4)
legend = TLegend(0.91,0.3,0.99,0.7)
legend.SetHeader("Cut","C")
legend.SetBorderSize(1)
legend.SetFillColor(0)
for i in range(5,11):
	cut = (i-1)/20
	legend.AddEntry(hs[i-5], ">= "+str(cut), "l")
legend.Draw()
	
c1.SaveAs('purty_x_efficiency_Q2QE.png')

del h_qelike, h_1chargedpion, h_1neutralpion, h_multipion, h_other
del legend, hs
