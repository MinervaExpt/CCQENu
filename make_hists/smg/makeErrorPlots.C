#include <iostream>
#include <string>
#include "PlotUtils/MnvH1D.h"
#include "PlotUtils/MnvH2D.h"
#include "MinervaUnfold/MnvResponse.h"
#include "MinervaUnfold/MnvUnfold.h"
#include "utils/RebinFlux.h"
#include "utils/SyncBands.h"
#include "TH2D.h"
#include "TH1D.h"
#include "TF2.h"
#include "TCanvas.h"
#include "TPad.h"
#include "TPaveLabel.h"
#include "utils/NuConfig.h"
#include "PlotUtils/FluxReweighter.h"
#include "PlotUtils/MnvPlotter.h"
#include <math.h>
#include "TColor.h"
#include "TLatex.h"

int main(const int argc, const char *argv[]) {

	bool includeStat = true;
	bool solidLinesOnly = true;
	double ignoreThreshold = 0.00001;
	bool covAreaNormalize = false;
	std::string errorGroupName = "";
	bool asfrac = true;
	bool ignoreUngrouped = false;
	
	int mc_line_width = 3;
	std::string stat_error_name = "Statistical";

	std::string pl = std::string(argv[1]);
	std::string configfilename(pl+".json");
	NuConfig config;
	config.Read(configfilename);

	std::string path(pl);
	std::string prescale;
	prescale = std::string(argv[2]);
	std::string base = path.substr(path.find_last_of("/\\") + 1);
	std::string rootfilename = Form("%s_%s_%s.root",config.GetString("outRoot").c_str(),base.c_str(),prescale.c_str());
	std::cout << "\nroot file: " << rootfilename << std::endl;
	std::string rootfolder = rootfilename.substr(0, rootfilename.size()-5);

	std::vector<std::string> vars1D = config.GetStringVector("AnalyzeVariables");
	std::vector<std::string> samples = config.GetStringVector("runsamples");

	TFile *infile = new TFile(Form(rootfilename.c_str()));

	PlotUtils::MnvPlotter mnvPlotter(PlotUtils::kCCQEAntiNuStyle);
	mnvPlotter.axis_maximum=0.4;
	mnvPlotter.axis_minimum=0.0;
	mnvPlotter.error_color_map["Flux"]                   = kViolet+6;
	mnvPlotter.error_color_map["Recoil Reconstruction"]  = kOrange+2;
	mnvPlotter.error_color_map["Cross Section Models"]   = kMagenta;
	mnvPlotter.error_color_map["FSI Model"]              = kRed;
	mnvPlotter.error_color_map["Muon Reconstruction"]    = kGreen;
	mnvPlotter.error_color_map["Muon Energy"]            = kGreen+3;
	mnvPlotter.error_color_map["Muon_Energy_MINERvA"]    = kRed-3;
	mnvPlotter.error_color_map["Muon_Energy_MINOS"]      = kViolet-3;
	mnvPlotter.error_color_map["Other"]                  = kGreen+3;
	mnvPlotter.error_color_map["Low Recoil Fits"]        = kRed+3;
	mnvPlotter.error_color_map["GEANT4"]                 = kBlue;
	mnvPlotter.error_color_map["Background Subtraction"] = kGreen;
	mnvPlotter.error_color_map["Tune"]                   = kOrange+2;
	
	mnvPlotter.error_summary_group_map.clear();

	mnvPlotter.error_summary_group_map["FSI Model"].push_back("GENIE_FrAbs_N");
	mnvPlotter.error_summary_group_map["FSI Model"].push_back("GENIE_FrAbs_pi");
	mnvPlotter.error_summary_group_map["FSI Model"].push_back("GENIE_FrCEx_N");
	mnvPlotter.error_summary_group_map["FSI Model"].push_back("GENIE_FrCEx_pi");
	mnvPlotter.error_summary_group_map["FSI Model"].push_back("GENIE_FrElas_N");
	mnvPlotter.error_summary_group_map["FSI Model"].push_back("GENIE_FrElas_pi");
	mnvPlotter.error_summary_group_map["FSI Model"].push_back("GENIE_FrInel_N");
	mnvPlotter.error_summary_group_map["FSI Model"].push_back("GENIE_FrInel_pi");
	mnvPlotter.error_summary_group_map["FSI Model"].push_back("GENIE_FrPiProd_N");
	mnvPlotter.error_summary_group_map["FSI Model"].push_back("GENIE_FrPiProd_pi");
	mnvPlotter.error_summary_group_map["FSI Model"].push_back("GENIE_MFP_N");
	mnvPlotter.error_summary_group_map["FSI Model"].push_back("GENIE_MFP_pi");

	mnvPlotter.error_summary_group_map["Genie Interaction Model"].push_back("GENIE_AGKYxF1pi");
	mnvPlotter.error_summary_group_map["Genie Interaction Model"].push_back("GENIE_AhtBY");
	mnvPlotter.error_summary_group_map["Genie Interaction Model"].push_back("GENIE_BhtBY");
	mnvPlotter.error_summary_group_map["Genie Interaction Model"].push_back("GENIE_CCQEPauliSupViaKF");
	mnvPlotter.error_summary_group_map["Genie Interaction Model"].push_back("GENIE_CV1uBY");
	mnvPlotter.error_summary_group_map["Genie Interaction Model"].push_back("GENIE_CV2uBY");
	mnvPlotter.error_summary_group_map["Genie Interaction Model"].push_back("GENIE_EtaNCEL");
	mnvPlotter.error_summary_group_map["Genie Interaction Model"].push_back("GENIE_MaCCQE");
	mnvPlotter.error_summary_group_map["Genie Interaction Model"].push_back("GENIE_MaCCQEshape");
	mnvPlotter.error_summary_group_map["Genie Interaction Model"].push_back("GENIE_MaNCEL");
	mnvPlotter.error_summary_group_map["Genie Interaction Model"].push_back("GENIE_MaRES");
	mnvPlotter.error_summary_group_map["Genie Interaction Model"].push_back("GENIE_MvRES");
	mnvPlotter.error_summary_group_map["Genie Interaction Model"].push_back("GENIE_NormCCQE");
	mnvPlotter.error_summary_group_map["Genie Interaction Model"].push_back("GENIE_NormCCRES");
	mnvPlotter.error_summary_group_map["Genie Interaction Model"].push_back("GENIE_NormDISCC");
	mnvPlotter.error_summary_group_map["Genie Interaction Model"].push_back("GENIE_NormNCRES");
	mnvPlotter.error_summary_group_map["Genie Interaction Model"].push_back("GENIE_RDecBR1gamma");
	mnvPlotter.error_summary_group_map["Genie Interaction Model"].push_back("GENIE_Rvn1pi");
	mnvPlotter.error_summary_group_map["Genie Interaction Model"].push_back("GENIE_Rvn2pi");
	mnvPlotter.error_summary_group_map["Genie Interaction Model"].push_back("GENIE_Rvn3pi");
	mnvPlotter.error_summary_group_map["Genie Interaction Model"].push_back("GENIE_Rvp1pi");
	mnvPlotter.error_summary_group_map["Genie Interaction Model"].push_back("GENIE_Rvp2pi");
	mnvPlotter.error_summary_group_map["Genie Interaction Model"].push_back("GENIE_Theta_Delta2Npi");
	mnvPlotter.error_summary_group_map["Genie Interaction Model"].push_back("GENIE_VecFFCCQEshape");

	mnvPlotter.error_summary_group_map["Tune"].push_back("RPA_LowQ2");
	mnvPlotter.error_summary_group_map["Tune"].push_back("RPA_HighQ2");
	mnvPlotter.error_summary_group_map["Tune"].push_back("NonResPi");
	mnvPlotter.error_summary_group_map["Tune"].push_back("2p2h");
	mnvPlotter.error_summary_group_map["Tune"].push_back("LowQ2Pi");
	mnvPlotter.error_summary_group_map["Tune"].push_back("Low_Recoil_2p2h_Tune");

	mnvPlotter.error_summary_group_map["Response"].push_back("response_em");
	mnvPlotter.error_summary_group_map["Response"].push_back("response_proton");
	mnvPlotter.error_summary_group_map["Response"].push_back("response_pion");
	mnvPlotter.error_summary_group_map["Response"].push_back("response_meson");
	mnvPlotter.error_summary_group_map["Response"].push_back("response_other");
	mnvPlotter.error_summary_group_map["Response"].push_back("response_low_neutron");
	mnvPlotter.error_summary_group_map["Response"].push_back("response_mid_neutron");
	mnvPlotter.error_summary_group_map["Response"].push_back("response_high_neutron");

	mnvPlotter.error_summary_group_map["Geant"].push_back("GEANT_Neutron");
	mnvPlotter.error_summary_group_map["Geant"].push_back("GEANT_Proton");
	mnvPlotter.error_summary_group_map["Geant"].push_back("GEANT_Pion");

	mnvPlotter.error_summary_group_map["Muon Energy"].push_back("Muon_Energy_MINOS");
	mnvPlotter.error_summary_group_map["Muon Energy"].push_back("Muon_Energy_MINERvA");
	mnvPlotter.error_summary_group_map["Muon Energy"].push_back("MINOS_Reconstruction_Efficiency");
	mnvPlotter.error_summary_group_map["Muon Energy"].push_back("Muon_Energy_Resolution");
	mnvPlotter.error_summary_group_map["Muon Energy"].push_back("BeamAngleX");
	mnvPlotter.error_summary_group_map["Muon Energy"].push_back("BeamAngleY");
  
	for (auto samp : samples) {
		for ( int i=0; i<vars1D.size(); i++ ) {
		
			MnvH1D *qe    = (MnvH1D*)infile->Get(Form("h___%s___qelike___%s___reconstructed",samp.c_str(),vars1D[i].c_str()));
			MnvH1D *sch   = (MnvH1D*)infile->Get(Form("h___%s___1chargedpion___%s___reconstructed",samp.c_str(),vars1D[i].c_str()));
			MnvH1D *snu   = (MnvH1D*)infile->Get(Form("h___%s___1neutralpion___%s___reconstructed",samp.c_str(),vars1D[i].c_str()));
			MnvH1D *multi = (MnvH1D*)infile->Get(Form("h___%s___multipion___%s___reconstructed",samp.c_str(),vars1D[i].c_str()));
			MnvH1D *other = (MnvH1D*)infile->Get(Form("h___%s___other___%s___reconstructed",samp.c_str(),vars1D[i].c_str()));
			MnvH1D *data  = (MnvH1D*)infile->Get(Form("h___%s___data___%s___reconstructed",samp.c_str(),vars1D[i].c_str()));
		
			TCanvas *c1 = new TCanvas( "canvas1", "variable", 200, 10, 1800, 1050 );
			
			TPad *pad1 = new TPad("pad1", "qelike",       0.04, 0.48, 0.35, 0.92);
			TPad *pad2 = new TPad("pad2", "1chargedpion", 0.35, 0.48, 0.66, 0.92);
			TPad *pad3 = new TPad("pad3", "1neutralpion", 0.66, 0.48, 0.97, 0.92);
			TPad *pad4 = new TPad("pad4", "multipion",    0.04, 0.06, 0.35, 0.48);
			TPad *pad5 = new TPad("pad5", "other",        0.35, 0.06, 0.66, 0.48);
			TPad *pad6 = new TPad("pad6", "legend",       0.66, 0.06, 0.97, 0.48);

			pad1->SetMargin(0.09,0.05,0.05,0.1);
			pad2->SetMargin(0.09,0.05,0.05,0.1);
			pad3->SetMargin(0.09,0.05,0.05,0.1);
			pad4->SetMargin(0.09,0.05,0.05,0.1);
			pad5->SetMargin(0.09,0.05,0.05,0.1);
			pad6->SetMargin(0.09,0.05,0.05,0.1);

			pad1->Draw();
			pad2->Draw();
			pad3->Draw();
			pad4->Draw();
			pad5->Draw();
			pad6->Draw();
			
			TPaveLabel *title = new TPaveLabel(0.10, 0.93, 0.9, 0.99, Form("%s - %s",samp.c_str(),vars1D[i].c_str()));
			title->SetTextFont(52);
			title->Draw();

			TText *ylabel = new TText( 0.03, 0.50, "Fractional Uncertainty" );
			ylabel->SetTextSize(0.03);
			ylabel->SetTextAlign(21);
			ylabel->SetTextAngle(90);
			ylabel->SetTextFont(52);
			ylabel->Draw();

			TText *xlabel = new TText( 0.50, 0.02, qe->GetXaxis()->GetTitle() );
			xlabel->SetTextSize(0.03);
			xlabel->SetTextAlign(21);
			xlabel->SetTextFont(52);
			xlabel->Draw();
			
			pad1->cd();
			mnvPlotter.DrawErrorSummary(qe,"N",includeStat,solidLinesOnly,0.0,covAreaNormalize,"",asfrac);
			double xm1 = pad1->GetUxmax();
			double ym1 = pad1->GetUymax();
			TText *htitle1 = new TText( xm1, 1.02*ym1, "qelike" );
			htitle1->SetTextSize(0.08);
			htitle1->SetTextAlign(31);
			htitle1->SetTextFont(52);
			htitle1->Draw();

			pad2->cd();
			mnvPlotter.DrawErrorSummary(sch,"N",includeStat,solidLinesOnly,0.0,covAreaNormalize,"",asfrac);
			double xm2 = pad2->GetUxmax();
			double ym2 = pad2->GetUymax();
			TText *htitle2 = new TText( xm2, 1.02*ym2, "1chargedpion" );
			htitle2->SetTextSize(0.08);
			htitle2->SetTextAlign(31);
			htitle2->SetTextFont(52);
			htitle2->Draw();

			pad3->cd();
			mnvPlotter.DrawErrorSummary(snu,"N",includeStat,solidLinesOnly,0.0,covAreaNormalize,"",asfrac);
			double xm3 = pad3->GetUxmax();
			double ym3 = pad3->GetUymax();
			TText *htitle3 = new TText( xm3, 1.02*ym3, "1neutralpion" );
			htitle3->SetTextSize(0.08);
			htitle3->SetTextAlign(31);
			htitle3->SetTextFont(52);
			htitle3->Draw();

			pad4->cd();
			mnvPlotter.DrawErrorSummary(multi,"N",includeStat,solidLinesOnly,0.0,covAreaNormalize,"",asfrac);
			double xm4 = pad4->GetUxmax();
			double ym4 = pad4->GetUymax();
			TText *htitle4 = new TText( xm4, 1.02*ym4, "multipion" );
			htitle4->SetTextSize(0.08);
			htitle4->SetTextAlign(31);
			htitle4->SetTextFont(52);
			htitle4->Draw();

			pad5->cd();
			mnvPlotter.DrawErrorSummary(other,"N",includeStat,solidLinesOnly,0.0,covAreaNormalize,"",asfrac);
			double xm5 = pad5->GetUxmax();
			double ym5 = pad5->GetUymax();
			TText *htitle5 = new TText( xm5, 1.02*ym5, "other" );
			htitle5->SetTextSize(0.08);
			htitle5->SetTextAlign(31);
			htitle5->SetTextFont(52);
			htitle5->Draw();
			
			pad6->cd();
			
			std::vector<TH1*>   hists;
			std::vector<string> names;
			std::vector<string> opts;

			bool useDifferentLineStyles = !solidLinesOnly;

			// Total Error
			TH1D *hTotalErr = (TH1D*)qe->GetTotalError( includeStat, asfrac, covAreaNormalize ).Clone( Form("h_total_err_errSum_%d", __LINE__) );
			mnvPlotter.ApplyNextLineStyle( hTotalErr, true, useDifferentLineStyles );
			std::string totalName = ( includeStat ? "Total Uncertainty" : "Total Sys. Uncertainty" );
			hists.push_back( hTotalErr );
			names.push_back( totalName );
			opts.push_back( "l" );
    	
			// Statistical Error
			TH1D *statErr = (TH1D*)qe->GetStatError(asfrac).Clone( Form("this_stat_err_%d", __LINE__) );
			statErr->SetLineColor( 12 );//dark gray
			statErr->SetLineStyle( 2 ); //dashed
			statErr->SetLineWidth( 3 );
			hists.push_back( statErr );
			names.push_back( stat_error_name );
			opts.push_back( "l" );
      
			// Error Bands
			std::map<string,TH1D*> errGroupHists;

			bool drawn_already = (errorGroupName == "") ? true : false;
			std::vector<std::string> errNames = qe->GetVertErrorBandNames();
			std::vector<std::string> otherNames = qe->GetLatErrorBandNames();
			errNames.insert( errNames.end(), otherNames.begin(), otherNames.end() );
			otherNames = qe->GetUncorrErrorNames();
			errNames.insert( errNames.end(), otherNames.begin(), otherNames.end() );
			for ( std::vector<std::string>::const_iterator it_name = errNames.begin(); it_name != errNames.end(); ++it_name ) {
				TH1D * hErr = NULL;
      	
				if (qe->HasVertErrorBand(*it_name)) {
					hErr = dynamic_cast<TH1D*>(qe->GetVertErrorBand(*it_name)->GetErrorBand( asfrac, covAreaNormalize ).Clone( Form("tmp_vertError_%s", (*it_name).c_str()) ));
				}
				else if (qe->HasLatErrorBand(*it_name)) {
					hErr = dynamic_cast<TH1D*>(qe->GetLatErrorBand(*it_name)->GetErrorBand( asfrac, covAreaNormalize ).Clone( Form("tmp_latError_%s", (*it_name).c_str()) ));
				}
				else if (qe->HasUncorrError(*it_name)) {
					hErr = dynamic_cast<TH1D*>(qe->GetUncorrErrorAsHist( *it_name, asfrac ).Clone(Form("tmp_uncorr_error_%s", (*it_name).c_str()) ));
				}
				else {
					throw std::runtime_error( Form("MnvPlotter::DrawErrorSummary(): Couldn't determine error band type for error name '%s'", (*it_name).c_str()) );
				}
		     
				bool inGroup = false;
				for (MnvPlotter::ErrorSummaryGroupMap::const_iterator itGroup = mnvPlotter.error_summary_group_map.begin(); 
					 itGroup != mnvPlotter.error_summary_group_map.end(); ++itGroup ) {
					const std::string& errName           = itGroup->first;
					const std::vector<std::string>& histNames = itGroup->second;
		  		
					if ( find( histNames.begin(), histNames.end(), *it_name) == histNames.end() ) continue;
		  		
					if (errorGroupName==errName) {
						inGroup=true;
						break;
					}
					else if (errorGroupName == "") {
						std::map<std::string,TH1D*>::iterator itGroupHist = errGroupHists.find(errName);
						if ( errGroupHists.end() == itGroupHist ) {
							errGroupHists[ errName ] = hErr;
						}
						else {
							MnvHist::AddInQuadrature( itGroupHist->second, hErr );
							delete hErr;
						}
						inGroup = true;
						break;
					}
				}
      	
				if ( errorGroupName == "" ) {
					if (inGroup) continue;
					if (ignoreUngrouped) continue;
				}
				else if ( errorGroupName != "" && !inGroup ) continue;
		  	
				mnvPlotter.ApplyNextLineStyle( hErr, false, useDifferentLineStyles);
				hErr->GetXaxis()->SetTitle(qe->GetXaxis()->GetTitle());
		  	
				std::map<string,int>::const_iterator itErrCol = mnvPlotter.error_color_map.find( *it_name );
				if ( mnvPlotter.error_color_map.end() != itErrCol ) hErr->SetLineColor( itErrCol->second );
					
				hErr->SetLineWidth( mc_line_width );
								
				hists.push_back( hErr );
				names.push_back( *it_name );
				opts.push_back( "l" );
				
			}
      
			for ( std::map<std::string,TH1D*>::iterator itGroup = errGroupHists.begin(); itGroup != errGroupHists.end(); ++itGroup ) {
				const string& name = itGroup->first;
				TH1* hist = itGroup->second;

				if ( 0 < ignoreThreshold && hist->GetBinContent( hist->GetMaximumBin() ) < ignoreThreshold ) continue;

				mnvPlotter.ApplyNextLineStyle( hist, false, useDifferentLineStyles);
				std::map<string,int>::const_iterator itErrCol = mnvPlotter.error_color_map.find( name );

				if ( mnvPlotter.error_color_map.end() != itErrCol ) hist->SetLineColor( itErrCol->second );

				hist->SetLineWidth( mc_line_width );
				if ( !asfrac ) hist->Scale(hist->GetBinWidth(1),"width");

				//hist->Draw( (histDrawOption + " SAME").c_str() );
				hists.push_back( hist );
				names.push_back( name );
				opts.push_back( "l" );
			}
		  
			TLegend *leg = new TLegend(0.11, 0.06, 0.92, 0.89);
			leg->SetFillColor(kWhite);
			for ( unsigned int i = 0; i < hists.size(); i++ )
			leg->AddEntry(hists[i],names[i].c_str(),opts[i].c_str());
			leg->Draw();
			
			c1->cd();
			c1->Print(Form("%s___%s___ErrorSummary.png",samp.c_str(),vars1D[i].c_str()));
			delete c1;
			
		}
	}
}








