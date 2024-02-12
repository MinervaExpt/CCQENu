import ROOT
from ROOT import TCanvas, TPad, TFile, TPaveLabel, TPaveText, TH1F, TH2F, TLegend
from ROOT import gROOT
from array import array


rfile = "SB_NuConfig_mult1pBDTGcuts_me1N_1.root"
f = TFile(rfile)

vars = ['ptmu','pzmu','Q2QE','EnuCCQE']
	
for var in vars:

	h_qelike = gROOT.FindObject( "h___Mult1p___qelike___"+var+"___selected_truth" )
	h_1chargedpion = gROOT.FindObject( "h___Mult1p___1chargedpion___"+var+"___selected_truth" )
	h_1neutralpion = gROOT.FindObject( "h___Mult1p___1neutralpion___"+var+"___selected_truth" )
	h_multipion = gROOT.FindObject( "h___Mult1p___multipion___"+var+"___selected_truth" )
	h_other = gROOT.FindObject( "h___Mult1p___other___"+var+"___selected_truth" )

	nbinX = h_qelike.GetNbinsX()

	xEdges = []
	for i in range(1,nbinX+2):
		xEdges.append(h_qelike.GetXaxis().GetBinLowEdge(i))

	if var == "Q2QE":
		xEdges[0] = 0.002

	##### >= 0.3 #####
	h_qelike_3 = gROOT.FindObject( "h___Mult1p03___qelike___"+var+"___selected_truth" )
	h_1chargedpion_3 = gROOT.FindObject( "h___Mult1p03___1chargedpion___"+var+"___selected_truth" )
	h_1neutralpion_3 = gROOT.FindObject( "h___Mult1p03___1neutralpion___"+var+"___selected_truth" )
	h_multipion_3 = gROOT.FindObject( "h___Mult1p03___multipion___"+var+"___selected_truth" )
	h_other_3 = gROOT.FindObject( "h___Mult1p03___other___"+var+"___selected_truth" )
	
	c1 = TCanvas( 'c1', 'Histogram Drawing Options', 200, 10, 900, 500 )
	c1.SetGrid()
	if var == "Q2QE":
		c1.SetLogx()

	############## Purity ##############
	h_pur = TH1F( 'purity', 'BDTG QELike Response >= 0.3 - Truth', nbinX, array('f',xEdges))
	h_pur.SetLineColor(ROOT.kBlue+1)
	h_pur.SetFillColor(0)
	h_pur.SetStats(0)
	h_pur.SetXTitle("true "+var)
	h_pur.GetXaxis().SetTitleSize(0.05)
	h_pur.SetAxisRange(0,1,"Y")
	# Fill
	for i in range(1,nbinX+1):
		denom = (h_qelike_3.GetBinContent(i)+
				     h_1chargedpion_3.GetBinContent(i)+
				     h_1neutralpion_3.GetBinContent(i)+
				     h_multipion_3.GetBinContent(i)+
				     h_other_3.GetBinContent(i))
		if denom > 0:
			n = h_qelike_3.GetBinContent(i)/denom
			h_pur.SetBinContent(i,n)
	# Draw
	h_pur.DrawCopy()

	############## Efficiency ##############
	h_eff = TH1F( 'efficiency', 'Efficiency', nbinX, array('f',xEdges))
	h_eff.SetLineColor(ROOT.kGreen+2)
	h_eff.SetStats(0)
	# Fill
	for i in range(1,nbinX+1):
		denom = h_qelike.GetBinContent(i)
		if denom > 0:
			n = h_qelike_3.GetBinContent(i)/denom
			h_eff.SetBinContent(i,n)
	# Draw
	h_eff.DrawCopy("Same")

	############## Selectivity ##############
	h_spec = TH1F( 'specificity', 'Specificity', nbinX, array('f',xEdges))
	h_spec.SetLineColor(ROOT.kRed+1)
	h_spec.SetStats(0)
	# Fill
	for i in range(1,nbinX+1):
		denom = (h_1chargedpion.GetBinContent(i)+
			       h_1neutralpion.GetBinContent(i)+
			       h_multipion.GetBinContent(i)+
			       h_other.GetBinContent(i))
		if denom > 0:
			n = (denom-
			     h_1chargedpion_3.GetBinContent(i)+
					 h_1neutralpion_3.GetBinContent(i)+
					 h_multipion_3.GetBinContent(i)+
					 h_other_3.GetBinContent(i))/denom
			h_spec.SetBinContent(i,n)
	# Draw
	h_spec.DrawCopy("Same")

	c1.cd()
	############## Legend ##############
	legend = TLegend(0.2,0.15,0.5,0.35)
	legend.SetBorderSize(1)
	legend.SetFillColor(0)
	legend.AddEntry(h_pur, "purity", "l")
	legend.AddEntry(h_eff, "efficiency (sensitivity)", "l")
	legend.AddEntry(h_spec, "specificity", "l")
	legend.Draw()
		
	c1.SaveAs(var+'_Eff_Pur_Spec_for_Truth_cut_03.png')
	
	del legend, h_pur, h_eff, h_spec, c1
	del h_qelike_3, h_1chargedpion_3, h_1neutralpion_3, h_multipion_3, h_other_3
	
	##### >= 0.4 #####
	h_qelike_4 = gROOT.FindObject( "h___Mult1p04___qelike___"+var+"___selected_truth" )
	h_1chargedpion_4 = gROOT.FindObject( "h___Mult1p04___1chargedpion___"+var+"___selected_truth" )
	h_1neutralpion_4 = gROOT.FindObject( "h___Mult1p04___1neutralpion___"+var+"___selected_truth" )
	h_multipion_4 = gROOT.FindObject( "h___Mult1p04___multipion___"+var+"___selected_truth" )
	h_other_4 = gROOT.FindObject( "h___Mult1p04___other___"+var+"___selected_truth" )
	
	c1 = TCanvas( 'c1', 'Histogram Drawing Options', 200, 10, 900, 500 )
	c1.SetGrid()
	if var == "Q2QE":
		c1.SetLogx()
	
	############## Purity ##############
	h_pur = TH1F( 'purity', 'BDTG QELike Response >= 0.4 - Truth', nbinX, array('f',xEdges))
	h_pur.SetLineColor(ROOT.kBlue+1)
	h_pur.SetFillColor(0)
	h_pur.SetStats(0)
	h_pur.SetXTitle("true "+var)
	h_pur.GetXaxis().SetTitleSize(0.05)
	h_pur.SetAxisRange(0,1,"Y")
	# Fill
	for i in range(1,nbinX+1):
		denom = (h_qelike_4.GetBinContent(i)+
				     h_1chargedpion_4.GetBinContent(i)+
				     h_1neutralpion_4.GetBinContent(i)+
				     h_multipion_4.GetBinContent(i)+
				     h_other_4.GetBinContent(i))
		if denom > 0:
			n = h_qelike_4.GetBinContent(i)/denom
			h_pur.SetBinContent(i,n)
	# Draw
	h_pur.DrawCopy()

	############## Efficiency ##############
	h_eff = TH1F( 'efficiency', 'Efficiency', nbinX, array('f',xEdges))
	h_eff.SetLineColor(ROOT.kGreen+2)
	h_eff.SetStats(0)
	# Fill
	for i in range(1,nbinX+1):
		denom = h_qelike.GetBinContent(i)
		if denom > 0:
			n = h_qelike_4.GetBinContent(i)/denom
			h_eff.SetBinContent(i,n)
	# Draw
	h_eff.DrawCopy("Same")

	############## Selectivity ##############
	h_spec = TH1F( 'specificity', 'Specificity', nbinX, array('f',xEdges))
	h_spec.SetLineColor(ROOT.kRed+1)
	h_spec.SetStats(0)
	# Fill
	for i in range(1,nbinX+1):
		denom = (h_1chargedpion.GetBinContent(i)+
			       h_1neutralpion.GetBinContent(i)+
			       h_multipion.GetBinContent(i)+
			       h_other.GetBinContent(i))
		if denom > 0:
			n = (denom-
			     h_1chargedpion_4.GetBinContent(i)+
					 h_1neutralpion_4.GetBinContent(i)+
					 h_multipion_4.GetBinContent(i)+
					 h_other_4.GetBinContent(i))/denom
			h_spec.SetBinContent(i,n)
	# Draw
	h_spec.DrawCopy("Same")

	c1.cd()
	############## Legend ##############
	legend = TLegend(0.2,0.15,0.5,0.35)
	legend.SetBorderSize(1)
	legend.SetFillColor(0)
	legend.AddEntry(h_pur, "purity", "l")
	legend.AddEntry(h_eff, "efficiency (sensitivity)", "l")
	legend.AddEntry(h_spec, "specificity", "l")
	legend.Draw()
		
	c1.SaveAs(var+'_Eff_Pur_Spec_for_Truth_cut_04.png')
	
	del legend, h_pur, h_eff, h_spec, c1
	del h_qelike, h_1chargedpion, h_1neutralpion, h_multipion, h_other
	del h_qelike_4, h_1chargedpion_4, h_1neutralpion_4, h_multipion_4, h_other_4
