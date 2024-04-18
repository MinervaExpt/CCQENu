import ROOT
from ROOT import TCanvas, TPad, TFile, TPaveLabel, TPaveText, TH1F, TH2F, TLegend, TLatex
from ROOT import gROOT
from array import array

c1 = TCanvas( 'c1', 'Histogram Drawing Options', 200, 10, 900, 500 )
c1.SetGrid()
#pad1 = TPad( 'pad1', 'The pad with the function',  0.03, 0.48, 0.97, 0.92, 21 )
#pad2 = TPad( 'pad2', 'The pad with the histogram', 0.03, 0.02, 0.97, 0.46, 21 )
#pad1.SetFillColor( 0 )
#pad2.SetFillColor( 0 )
#pad1.Draw()
#pad2.Draw()

ofile = "SB_NuConfig_v8_multitrack_me1N_1.root"
of = TFile(ofile)
rfile = "SB_NuConfig_mult1pBDTG_me1N_1.root"
f = TFile(rfile)

vars = ['ptmu']

for var in vars:

	h_qelike = gROOT.FindObject( "h2D___Mult1p___qelike___bdtgQELike_"+var+"___reconstructed" )
	h_1chargedpion = gROOT.FindObject( "h2D___Mult1p___1chargedpion___bdtgQELike_"+var+"___reconstructed" )
	h_1neutralpion = gROOT.FindObject( "h2D___Mult1p___1neutralpion___bdtgQELike_"+var+"___reconstructed" )
	h_multipion = gROOT.FindObject( "h2D___Mult1p___multipion___bdtgQELike_"+var+"___reconstructed" )
	h_other = gROOT.FindObject( "h2D___Mult1p___other___bdtgQELike_"+var+"___reconstructed" )

	#title = TPaveLabel( 0.1, 0.94, 0.9, 0.98,'QELike selection from BDTG metrics' )
	#title.SetFillColor( 0 )
	#title.SetTextFont( 52 )
	#title.Draw()

	nbinX = h_qelike.GetNbinsX()
	nbinY = h_qelike.GetNbinsY()

	h_pur = []
	h_eff = []
	h_pureff = []

	h_start = TH1F( 'start', 'QELike BDTG Response Cut Metrics for '+var, nbinX-1, 0, 1 )
	h_start.GetXaxis().SetTitle("QELike BDTG Response")
	h_start.SetAxisRange(0,1,"Y")
	h_start.SetFillColor(0)
	h_start.SetStats(0)
	h_start.DrawCopy()

	for j in range(1,nbinY):

		############## Purity ##############
		h_pur.append(TH1F( 'purity'+str(j), 'Purity', nbinX-1, 0, 1 ))
		h_pur[j-1].SetLineColor(ROOT.kBlue+1)
		h_pur[j-1].SetLineWidth(2)
		h_pur[j-1].SetStats(0)
		# Fill
		for i in range(0,nbinX):
			denom = (h_qelike.Integral(i,nbinX,j,j)+
				       h_1chargedpion.Integral(i,nbinX,j,j)+
				       h_1neutralpion.Integral(i,nbinX,j,j)+
				       h_multipion.Integral(i,nbinX,j,j)+
				       h_other.Integral(i,nbinX,j,j))
			if denom > 0:
				n = h_qelike.Integral(i,nbinX,j,j)/denom
				h_pur[j-1].SetBinContent(i,n)
		# Draw
		h_pur[j-1].DrawCopy("Same")

		############## Efficiency ##############
		h_eff.append(TH1F( 'efficiency'+str(j), 'Efficiency', h_qelike.GetNbinsX()-1, 0, 1 ))
		h_eff[j-1].SetLineColor(ROOT.kGreen+2)
		h_eff[j-1].SetLineWidth(2)
		h_eff[j-1].SetStats(0)
		# Fill
		for i in range(0,nbinX):
			denom = h_qelike.Integral(1,nbinX,j,j)
			if denom > 0:
				n = h_qelike.Integral(i,nbinX,j,j)/denom
				h_eff[j-1].SetBinContent(i,n)
		# Draw
		h_eff[j-1].DrawCopy("Same")

		############## Selectivity ##############
		h_pureff.append(TH1F( 'purity*efficiency'+str(j), 'Purity*Efficiency', h_qelike.GetNbinsX()-1, 0, 1 ))
		h_pureff[j-1].SetLineColor(ROOT.kRed+1)
		h_pureff[j-1].SetLineWidth(2)
		h_pureff[j-1].SetStats(0)
		# Fill
		for i in range(0,nbinX):
			n = h_pur[j-1].GetBinContent(i)*h_eff[j-1].GetBinContent(i)
			h_pureff[j-1].SetBinContent(i,n)
		# Draw
		h_pureff[j-1].DrawCopy("Same")

	############## Legend ##############
	legend = TLegend(0.3,0.2,0.5,0.4)
	legend.SetBorderSize(1)
	legend.SetFillColor(0)
	legend.AddEntry(h_pur[0], "purity", "l")
	legend.AddEntry(h_eff[0], "efficiency", "l")
	legend.AddEntry(h_pureff[0], "purity*efficiency", "l")
	legend.Draw()

	############## Save ##############
	c1.SaveAs(var+'_Eff_Pur_vs_Response_2D.png')
	
	del h_qelike, h_1chargedpion, h_1neutralpion, h_multipion, h_other
	del h_start, legend, h_pur, h_eff, h_pureff
	
for var in vars:

	c2 = TCanvas( 'c2', 'Histogram Drawing Options', 1800, 1200 )

	pads = []
	padX = [1,2,3,1,2,3]
	padY = [2,2,2,1,1,1]

	title = TPaveLabel( 0.1, 0.94, 0.9, 0.99,var+' - QELike selection metrics for cuts on BDTG response' )
	title.SetFillColor( 0 )
	title.SetTextFont( 52 )
	title.Draw()

	h_qelike = gROOT.FindObject( "h2D___Mult1p___qelike___bdtgQELike_"+var+"___reconstructed" )
	h_1chargedpion = gROOT.FindObject( "h2D___Mult1p___1chargedpion___bdtgQELike_"+var+"___reconstructed" )
	h_1neutralpion = gROOT.FindObject( "h2D___Mult1p___1neutralpion___bdtgQELike_"+var+"___reconstructed" )
	h_multipion = gROOT.FindObject( "h2D___Mult1p___multipion___bdtgQELike_"+var+"___reconstructed" )
	h_other = gROOT.FindObject( "h2D___Mult1p___other___bdtgQELike_"+var+"___reconstructed" )
	
	#oh_qelike = gROOT.FindObject( "h___QElike_Mult2p___qelike___"+var+"___reconstructed" )
	#oh_1chargedpion = gROOT.FindObject( "h___QElike_Mult2p___1chargedpion___"+var+"___reconstructed" )
	#oh_1neutralpion = gROOT.FindObject( "h___QElike_Mult2p___1neutralpion___"+var+"___reconstructed" )
	#oh_multipion = gROOT.FindObject( "h___QElike_Mult2p___multipion___"+var+"___reconstructed" )
	#oh_other = gROOT.FindObject( "h___QElike_Mult2p___other___"+var+"___reconstructed" )

	nbinX = h_qelike.GetNbinsX()
	nbinY = h_qelike.GetNbinsY()

	yEdges = []
	for j in range(1,nbinY+2):
		yEdges.append(h_qelike.GetYaxis().GetBinLowEdge(j))

	if var == "Q2QE":
		yEdges[0] = 0.002

	h_pur = []
	h_eff = []
	h_pureff = []
	
	#oh_pur = TH1F( 'old purity', 'old purity', nbinY, array('f',yEdges))
	#oh_eff = TH1F( 'old efficiency', 'old efficiency', nbinY, array('f',yEdges))
	#oh_pureff = TH1F( 'old specificity', 'old specificity', nbinY, array('f',yEdges))

	for i in range(5,11):
		pads.append(TPad( 'pad1', 'The pad with the function', 
			                0.33*(padX[i-5]-1), 0.42*(padY[i-5]-1)+0.07, 
			                0.33*(padX[i-5])+0.01,   0.42*(padY[i-5])+0.07, 10 ))
		pads[i-5].SetFillColor( 0 )
		pads[i-5].Draw()
		pads[i-5].SetGrid()
		
	for i in range(5,11):
		pads[i-5].cd()
		
		if var == "Q2QE":
			pads[i-5].SetLogx()
		
		cut = (i-1)/20

		############## Purity ##############
		h_pur.append(TH1F( 'purity', 'BDTG QELike Response >= '+str(cut), nbinY, array('f',yEdges)))
		h_pur[i-5].SetLineColor(ROOT.kBlue+1)
		h_pur[i-5].SetLineWidth(2)
		h_pur[i-5].SetFillColor(0)
		h_pur[i-5].SetStats(0)
		#h_pur[i-5].GetXaxis().SetTitle(var)
		h_pur[i-5].SetXTitle(var)
		h_pur[i-5].GetXaxis().SetTitleSize(0.05)
		h_pur[i-5].SetAxisRange(0,1,"Y")
		# Fill
		for j in range(1,nbinY+1):
			denom = (h_qelike.Integral(i,nbinX,j,j)+
					     h_1chargedpion.Integral(i,nbinX,j,j)+
					     h_1neutralpion.Integral(i,nbinX,j,j)+
					     h_multipion.Integral(i,nbinX,j,j)+
					     h_other.Integral(i,nbinX,j,j))
			if denom > 0:
				n = h_qelike.Integral(i,nbinX,j,j)/denom
				h_pur[i-5].SetBinContent(j,n)
		#oh_pur.SetLineColor(ROOT.kBlue+1)
		#oh_pur.SetLineStyle(5)
		#for j in range(1,nbinY+1):
		#	denom = (oh_qelike.Integral(j,j)+
		#			     oh_1chargedpion.Integral(j,j)+
		#			     oh_1neutralpion.Integral(j,j)+
		#			     oh_multipion.Integral(j,j)+
		#			     oh_other.Integral(j,j))
		#	if denom > 0:
		#		n = oh_qelike.Integral(j,j)/denom
		#		oh_pur.SetBinContent(j,n)
		# Draw
		h_pur[i-5].DrawCopy()
		#oh_pur.DrawCopy()

		############## Efficiency ##############
		h_eff.append(TH1F( 'efficiency', 'Efficiency', nbinY, array('f',yEdges)))
		h_eff[i-5].SetLineColor(ROOT.kGreen+2)
		h_eff[i-5].SetLineWidth(2)
		h_eff[i-5].SetStats(0)
		# Fill
		for j in range(1,nbinY+1):
			denom = h_qelike.Integral(1,nbinX,j,j)
			if denom > 0:
				n = h_qelike.Integral(i,nbinX,j,j)/denom
				h_eff[i-5].SetBinContent(j,n)
		# Draw
		h_eff[i-5].DrawCopy("Same")

		############## Selectivity ##############
		h_pureff.append(TH1F( 'purity*efficiency', 'Purity*Efficiency', nbinY, array('f',yEdges)))
		h_pureff[i-5].SetLineColor(ROOT.kRed+1)
		h_pureff[i-5].SetLineWidth(2)
		h_pureff[i-5].SetStats(0)
		# Fill
		for j in range(1,nbinY+1):
			n = h_pur[i-5].GetBinContent(j)*h_eff[i-5].GetBinContent(j)
			h_pureff[i-5].SetBinContent(j,n)
		# Draw
		h_pureff[i-5].DrawCopy("Same")

	c2.cd()
	############## Legend ##############
	#legend = TLegend(0.3,0.2,0.5,0.4)
	legend = TLegend(0.3,0.01,0.7,0.06)
	legend.SetBorderSize(1)
	legend.SetFillColor(0)
	legend.AddEntry(h_pur[0], "purity", "l")
	legend.AddEntry(h_eff[0], "efficiency (sensitivity)", "l")
	legend.AddEntry(h_pureff[0], "purity*efficiency", "l")
	legend.Draw()
		
	c2.SaveAs(var+'_Eff_Pur_for_Response_cut_2D.png')
	
	del h_qelike, h_1chargedpion, h_1neutralpion, h_multipion, h_other
	del legend, h_pur, h_eff, h_pureff





