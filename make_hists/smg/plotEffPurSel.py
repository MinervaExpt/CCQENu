import ROOT
from ROOT import TCanvas, TPad, TFile, TPaveLabel, TPaveText, TH1F, TLegend, TLatex, TLine
from ROOT import gROOT

c1 = TCanvas( 'c1', 'Histogram Drawing Options', 200, 10, 900, 500 )
c1.SetGrid()
#pad1 = TPad( 'pad1', 'The pad with the function',  0.03, 0.48, 0.97, 0.92, 21 )
#pad2 = TPad( 'pad2', 'The pad with the histogram', 0.03, 0.02, 0.97, 0.46, 21 )
#pad1.SetFillColor( 0 )
#pad2.SetFillColor( 0 )
#pad1.Draw()
#pad2.Draw()

rfile = "SB_NuConfig_mult1pBDTG_me1N_1.root"
f = TFile(rfile)

h_qelike = gROOT.FindObject( "h___Mult1p_2track___qelike___bdtgQELike___reconstructed" )
h_1chargedpion = gROOT.FindObject( "h___Mult1p_2track___1chargedpion___bdtgQELike___reconstructed" )
h_1neutralpion = gROOT.FindObject( "h___Mult1p_2track___1neutralpion___bdtgQELike___reconstructed" )
h_multipion = gROOT.FindObject( "h___Mult1p_2track___multipion___bdtgQELike___reconstructed" )
h_other = gROOT.FindObject( "h___Mult1p_2track___other___bdtgQELike___reconstructed" )

nbin = h_qelike.GetNbinsX()

############## Purity ##############
#pad1.cd()
h_pur = TH1F( 'purity', 'QELike BDTG Response Cut Metrics for 2 Tracks', nbin-1, 0, 1 )
h_pur.SetFillColor(0)
h_pur.SetLineColor(ROOT.kBlue+1)
h_pur.SetLineWidth(2)
h_pur.SetAxisRange(0,1,"Y")
h_pur.SetStats(0)
h_pur.GetXaxis().SetTitle("QELike BDTG Response")
# Fill
for i in range(0,nbin):
	denom = (h_qelike.Integral(i,nbin)+
	        h_1chargedpion.Integral(i,nbin)+
	        h_1neutralpion.Integral(i,nbin)+
	        h_multipion.Integral(i,nbin)+
	        h_other.Integral(i,nbin))
	if denom > 0:
		n = h_qelike.Integral(i,nbin)/denom
	else:
		n = 0
	h_pur.SetBinContent(i,n)
# Draw
h_pur.DrawCopy()

# Line
line = TLine(0.35,-0.04,0.35,1.)
line.SetLineColor(ROOT.kViolet-1);
line.SetLineWidth(2)
line.Draw();
h_pur.DrawCopy("Same")

############## Efficiency ##############
#pad2.cd()
h_eff = TH1F( 'efficiency', 'Efficiency', h_qelike.GetNbinsX()-1, 0, 1 )
h_eff.SetLineColor(ROOT.kGreen+2)
h_eff.SetLineWidth(2)
h_eff.SetStats(0)
# Fill
for i in range(0,nbin):
	n = h_qelike.Integral(i,nbin)/h_qelike.Integral()
	h_eff.SetBinContent(i,n)
# Draw
h_eff.DrawCopy("Same")

############## Purity*Efficiency ##############
h_pureff = TH1F( 'purity*efficiency', 'Purity*Efficiency', h_qelike.GetNbinsX()-1, 0, 1 )
h_pureff.SetLineColor(ROOT.kRed+1)
h_pureff.SetLineWidth(2)
h_pureff.SetStats(0)
# Fill
for i in range(0,nbin):
	n = h_pur.GetBinContent(i)*h_eff.GetBinContent(i)
	h_pureff.SetBinContent(i,n)
# Draw
h_pureff.DrawCopy("Same")

############## Legend ##############
legend = TLegend(0.45,0.2,0.65,0.4)
legend.SetBorderSize(1)
legend.SetFillColor(0)
legend.AddEntry(h_pur, "purity", "l")
legend.AddEntry(h_eff, "efficiency", "l")
legend.AddEntry(h_pureff, "purity #times efficiency", "l")
legend.Draw()
	
text = TLatex(0.41,0.98,"Work in progress");
text.SetTextAlign(13);
text.SetTextColor(ROOT.kRed);
text.SetTextFont(13);
text.SetTextSize(20);
text.Draw();

ltext = TLatex(0.35,-0.07,"0.35");
ltext.SetTextAlign(22);
ltext.SetTextColor(ROOT.kViolet-1);
ltext.SetTextFont(23);
ltext.SetTextSize(19);
ltext.Draw();

############## Save ##############
c1.SaveAs('Eff_Pur_vs_Response_2track_v2.png')




