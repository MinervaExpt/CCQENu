import ROOT
from ROOT import TCanvas, TPad, TFile, TPaveLabel, TPaveText, TH1F, TH2F, TLegend
from ROOT import gROOT
from array import array
from pathlib import Path


Path("SB_NuConfig_mult1pBDTG_me1N_1/2D").mkdir(parents=True, exist_ok=True)

styles = ["BOX","COLZ","CONT4Z"]
interactions = ["data","qelike","1chargedpion","1neutralpion","multipion","other"]
vars2d = ["bdtgQELike_ptmu",
          "bdtgQELike_pzmu",
          "bdtgQELike_Q2QE",
          "bdtgQELike_EnuCCQE",
          "bdtgQELike_NBlobs",
          "bdtgQELike_ImprovedMichelCount",
          "bdtgQELike_Multiplicity",
          "bdtgQELike_PrimaryProtonScore1",
          "bdtgQELike_SecProtonScore1_1",
          "bdtgQELike_SecProtonScore1_2",
          "bdtgQELike_NumClustsPrimaryProtonEnd",
          "bdtgQELike_NumClustsSecProtonEnd_1",
          "bdtgQELike_NumClustsSecProtonEnd_2",
          "bdtgQELike_PrimaryProtonTrackVtxGap",
          "bdtgQELike_SecProtonTrackVtxGap_1",
          "bdtgQELike_SecProtonTrackVtxGap_2",
          "bdtgQELike_PrimaryProtonTfromdEdx",
          "bdtgQELike_SecProtonTfromdEdx_1",
          "bdtgQELike_SecProtonTfromdEdx_2",
          "bdtgQELike_PrimaryProtonFractionVisEnergyInCone",
          "bdtgQELike_SecProtonFractionVisEnergyInCone_1",
          "bdtgQELike_SecProtonFractionVisEnergyInCone_2",
          "bdtgQELike_NumberOfProtonCandidates",
          "bdtgQELike_bdtg1ChargedPion",
          "bdtg1ChargedPion_bdtg1NeutralPion"]
          
rfile = "SB_NuConfig_mult1pBDTG_me1N_1.root"
f = TFile(rfile)
      
for style in styles:
	for var in vars2d:
	
		c1 = TCanvas( "c1", var+"___"+style, 200, 10, 1500, 900 )

		pad_qe = TPad( "qelike",       "qelike",       0.01, 0.46, 0.34, 0.92, 21)
		pad_1c = TPad( "1chargedpion", "1chargedpion", 0.34, 0.46, 0.67, 0.92, 21)
		pad_1n = TPad( "1neutralpion", "1neutralpion", 0.67, 0.46, 1.0,  0.92, 21)
		pad_mp = TPad( "multipion",    "multipion",    0.01, 0.0,  0.34, 0.46, 21)
		pad_ot = TPad( "other",        "other",        0.34, 0.0,  0.67, 0.46, 21)
		pad_dt = TPad( "data",         "data",         0.67, 0.0,  1.0,  0.46, 21)

		pad_qe.SetGrid()
		pad_1c.SetGrid()
		pad_1n.SetGrid()
		pad_mp.SetGrid()
		pad_ot.SetGrid()
		pad_dt.SetGrid()

		pad_qe.SetFillColor(0)
		pad_1c.SetFillColor(0)
		pad_1n.SetFillColor(0)
		pad_mp.SetFillColor(0)
		pad_ot.SetFillColor(0)
		pad_dt.SetFillColor(0)

		pad_qe.Draw()
		pad_1c.Draw()
		pad_1n.Draw()
		pad_mp.Draw()
		pad_ot.Draw()
		pad_dt.Draw()
		
		title = TPaveLabel( 0.1, 0.94, 0.9, 0.98, var )
		title.SetFillColor( 0 )
		title.SetTextFont( 52 )
		title.Draw()
		
		pad_qe.cd()
		h2D_qe = gROOT.FindObject( "h2D___Mult1p___qelike___"+var+"___reconstructed" )
		h2D_qe.SetTitle("qelike")
		h2D_qe.SetStats(0)
		h2D_qe.Draw(style)
		
		pad_1c.cd()
		h2D_1c = gROOT.FindObject( "h2D___Mult1p___1chargedpion___"+var+"___reconstructed" )
		h2D_1c.SetTitle("1chargedpion")
		h2D_1c.SetStats(0)
		h2D_1c.Draw(style)
		
		pad_1n.cd()
		h2D_1n = gROOT.FindObject( "h2D___Mult1p___1neutralpion___"+var+"___reconstructed" )
		h2D_1n.SetTitle("1neutralpion")
		h2D_1n.SetStats(0)
		h2D_1n.Draw(style)
		
		pad_mp.cd()
		h2D_mp = gROOT.FindObject( "h2D___Mult1p___multipion___"+var+"___reconstructed" )
		h2D_mp.SetTitle("multipion")
		h2D_mp.SetStats(0)
		h2D_mp.Draw(style)
		
		pad_ot.cd()
		h2D_ot = gROOT.FindObject( "h2D___Mult1p___other___"+var+"___reconstructed" )
		h2D_ot.SetTitle("other")
		h2D_ot.SetStats(0)
		h2D_ot.Draw(style)
		
		pad_dt.cd()
		h2D_dt = gROOT.FindObject( "h2D___Mult1p___data___"+var+"___reconstructed" )
		h2D_dt.SetTitle("data")
		h2D_dt.SetStats(0)
		h2D_dt.Draw(style)
			
		c1.SaveAs("SB_NuConfig_mult1pBDTG_me1N_1/2D/"+var+"___2D_"+style+".pdf")
		
		del c1,pad_qe,pad_1c,pad_1n,pad_mp,pad_ot,pad_dt,h2D_qe,h2D_1c,h2D_1n,h2D_mp,h2D_ot,h2D_dt
		




































