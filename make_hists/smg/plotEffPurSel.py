import ROOT
from ROOT import TCanvas, TPad, TFile, TPaveLabel, TPaveText, TH1F, TLegend
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

h_qelike = gROOT.FindObject( "h___Mult1p___qelike___bdtgQELike___reconstructed" )
h_1chargedpion = gROOT.FindObject( "h___Mult1p___1chargedpion___bdtgQELike___reconstructed" )
h_1neutralpion = gROOT.FindObject( "h___Mult1p___1neutralpion___bdtgQELike___reconstructed" )
h_multipion = gROOT.FindObject( "h___Mult1p___multipion___bdtgQELike___reconstructed" )
h_other = gROOT.FindObject( "h___Mult1p___other___bdtgQELike___reconstructed" )

nbin = h_qelike.GetNbinsX()

############## Purity ##############
#pad1.cd()
h_pur = TH1F( 'purity', 'QELike BDTG Response Cut Metrics', nbin-1, 0, 1 )
h_pur.SetFillColor( 0 )
h_pur.SetLineColor(ROOT.kBlue+1)
h_pur.SetAxisRange(0,1,"Y")
h_pur.SetStats(0)
h_pur.GetXaxis().SetTitle("QELike BDTG Response")
# Fill
for i in range(0,nbin):
	n = h_qelike.Integral(i,nbin)/(h_qelike.Integral(i,nbin)+
	                             h_1chargedpion.Integral(i,nbin)+
	                             h_1neutralpion.Integral(i,nbin)+
	                             h_multipion.Integral(i,nbin)+
	                             h_other.Integral(i,nbin))
	h_pur.SetBinContent(i,n)
# Draw
h_pur.DrawCopy()

############## Efficiency ##############
#pad2.cd()
h_eff = TH1F( 'efficiency', 'Efficiency', h_qelike.GetNbinsX()-1, 0, 1 )
h_eff.SetLineColor(ROOT.kGreen+2)
h_eff.SetStats(0)
# Fill
for i in range(0,nbin):
	n = h_qelike.Integral(i,nbin)/h_qelike.Integral()
	h_eff.SetBinContent(i,n)
# Draw
h_eff.DrawCopy("Same")

############## Selectivity ##############
h_spec = TH1F( 'specificity', 'Specificity', h_qelike.GetNbinsX()-1, 0, 1 )
h_spec.SetLineColor(ROOT.kRed+1)
h_spec.SetStats(0)
# Fill
for i in range(0,nbin):
	n = (h_1chargedpion.Integral(0,i)+
	     h_1neutralpion.Integral(0,i)+
	     h_multipion.Integral(0,i)+
	     h_other.Integral(0,i))/(h_1chargedpion.Integral()+
	                             h_1neutralpion.Integral()+
	                             h_multipion.Integral()+
	                             h_other.Integral())
	h_spec.SetBinContent(i,n)
# Draw
h_spec.DrawCopy("Same")

############## Legend ##############
legend = TLegend(0.3,0.2,0.5,0.4)
legend.SetBorderSize(1)
legend.SetFillColor(0)
legend.AddEntry(h_pur, "purity (sensitivity)", "l")
legend.AddEntry(h_eff, "efficiency", "l")
legend.AddEntry(h_spec, "specificity", "l")
legend.Draw()

############## Save ##############
c1.SaveAs('Eff_Pur_Spec_vs_Response.png')




