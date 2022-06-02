bool DEBUG=1;

#include <iostream>
#include <string>
#include "PlotUtils/MnvH1D.h"
#include "PlotUtils/MnvH2D.h"
#include "MinervaUnfold/MnvResponse.h"
#include "MinervaUnfold/MnvUnfold.h"
#include "utils/RebinFlux.h"
// #include "utils/RebinFluxTest.h"
#include "utils/SyncBands.h"
#include "TFile.h"
#include "TROOT.h"
#include "TStyle.h"
#include "TError.h"
#include "TH2D.h"
#include "TF2.h"
#include <stdlib.h>
//s#include "PlotUtils/ChainWrapper.h"
#include "TCanvas.h"
#include "utils/NuConfig.h"
#include "PlotUtils/FluxReweighter.h"
#include "GetXSec.h"
//#include "utils/POTCounter.h"
//#define LOCAL  // this is for local  data samples


double targets = 3.23478E30; //nucleons - is this the same for MC or different



#ifndef __CINT__
#include "include/plotting_pdf.h"
#endif

#include <sstream>

// code to split on any delimiter thanks to stackoverflow
//
// std::vector<std::string> split (std::string s, std::string delimiter) {
//   size_t pos_start = 0, pos_end, delim_len = delimiter.length();
//   std::string token;
//   std::vector<std::string> res;
//
//   while ((pos_end = s.find (delimiter, pos_start)) != std::string::npos) {
//     token = s.substr (pos_start, pos_end - pos_start);
//     pos_start = pos_end + delim_len;
//     res.push_back (token);
//   }
//
//   res.push_back (s.substr (pos_start));
//   return res;
// }


// Main  - this will do set up, loop over events and then make some plots

bool checktag(std::vector<std::string> keys, std::string tag){
  return std::count(keys.begin(), keys.end(), tag)>0;
}

int main(const int argc, const char *argv[] ) {

  gROOT->ProcessLine("gErrorIgnoreLevel = kWarning;");
  //++++++++++++++++++=  Initialization +++++++++++++++++++++++++

  std::string inputtag = "";
  if (argc > 1){
    inputtag  = std::string(argv[1]);
  }
  else{
    std::cout << " arguments are:\n analyze <config>_<prescale> " << std::endl;
    exit(0);
  }
  int prescale = 100;
  if (argc > 2){
    inputtag+= "_"+std::string(argv[2]);
  }
  std::string asample;
  bool singlesample;
  if (argc > 3){
      asample = std::string(argv[3]);
      singlesample = 1;
  }
  else{
      singlesample = 0;
  }
  if (DEBUG) std::cout << " test NuConfig" << std::endl;
  NuConfig config;
  config.Read(std::string(argv[1])+".json");
  config.Print();
  std::vector<std::string> AnalyzeVariables = config.GetStringVector("AnalyzeVariables");
  std::vector<std::string> AnalyzeVariables2D = config.GetStringVector("Analyze2DVariables");
  std::vector<std::string> SampleRequest;
    
  // either get sample from command line or from the list in the config
  if (!singlesample){
      SampleRequest = config.GetStringVector("runsamples");
  }
  else{
      SampleRequest.push_back(asample);
  }
  std::string playlist = config.GetString("playlist");
  std::string inputname = config.GetString("outRoot")+"_"+inputtag+".root";
  int m_fluxUniverses = config.GetInt("fluxUniverses");

  //========================================= Now do some analysis

  MnvH1D* h_flux_dewidthed = GetFlux(config);
  double flux = h_flux_dewidthed->Integral() ;
  // make containers for different analysis levels
  std::map<std::string, MnvH1D*> h_flux_ebins;

  // now loop over histograms, unsmear, efficiency correct and normalize

  // unfolding setup
  MinervaUnfold::MnvUnfold unfold;
  // MnvH2D* MigrationMatrix;
  double num_iter = 5;

  // input 4 D hist-map

  // arguments will be sample, variable, type, category
  // order in histogram name is sample___category___variable___type
  // type is reconstructed, truth...
  // category is qelike, qelikenot ...

  std::map<std::string, std::map< std::string, std::map< std::string, std::map <std::string, MnvH1D*> > > > hists1D;

  std::map<std::string, std::map< std::string, std::map< std::string, std::map <std::string, MnvH2D*> > > > hists2D;

  std::map<std::string, std::map< std::string, std::map< std::string, std::map <std::string, MnvH2D*> > > > response1D;

  std::map<std::string, std::map< std::string, std::map< std::string, std::map <std::string, MnvH2D*> > > > response2D;


  TFile* f = TFile::Open(inputname.c_str(),"READONLY");
  f->ls();

  std::vector<std::string> keys;

  MnvH1D* null = new MnvH1D("null","empty histogram",1,0.,1.);
  MnvH2D* null2 = new MnvH2D("null2","empty histogram",1,0.,1.,1,0.,1.);

  std::vector<std::string> samples;
  std::vector<std::string> variables;
  std::vector<std::string> categories;
  std::vector<std::string> types;

  // this is the old read in the POT.  They are also in a vector which Amit like having
  TH1D* h_pot = (TH1D*)f->Get("POT_summary");

  double dataPOT = h_pot->GetBinContent(1);
  double mcPOTprescaled = h_pot->GetBinContent(3);
  double POTScale = dataPOT/mcPOTprescaled;
  delete h_pot;
  double norm = 1./dataPOT/targets;
  std::cout << " integrated luminosity is " << 1/norm/1.E24 << "barns^-1" <<  std::endl;

  std::cout <<  " POT MC " <<  mcPOTprescaled  <<std::endl;
  std::cout <<  " POT DATA " << dataPOT << std::endl;

  for (auto k:*f->GetListOfKeys()){
    keys.push_back(k->GetName());
    std::string key = k->GetName();
    // see if 1 or 2 D  -- this is for 1 D
    std::cout << " key " << k->GetName() << std::endl;
    std::vector<std::string> parsekey;
    parsekey = split(k->GetName(),"___");
    if (parsekey.size()< 4){
      std::cout << " not parseable " << k->GetName() << std::endl;
      continue;
    }
    std::string hNd = parsekey[0];
    std::string sample = parsekey[1];
    std::string category = parsekey[2];
    std::string variable = parsekey[3];
    std::string type = parsekey[4];

    // build lists of all valid tags
    // only count sample that you requested
    if(! checktag(SampleRequest,sample)){
          std::cout << " skip a sample:" << sample << std::endl;
          continue;
    }
    // build lists of tags
    if (!checktag(samples,sample)){
      samples.push_back(sample);
      std::cout << " add a sample: " << sample << std::endl;
    }
    
    if (!checktag(categories,category)){
      categories.push_back(category);
      std::cout << " add a category: " << category << std::endl;
    }
    if (!checktag(variables,variable)){
      variables.push_back(variable);
      std::cout << " add a variable: " << variable << std::endl;
    }
    if (!checktag(types,type)){
      types.push_back(type);
      std::cout << " add a type: " << type << std::endl;
    }
    // get the histogram
    TNamed* me = f->GetKey(key.c_str());
    std::cout << " Done with parsing" << std::endl;

    // 1D hists
    if(key.find("h2D")==std::string::npos){
      // if response in name its a 2D so do a cast to MnvH2D
      if(key.find("response")!=std::string::npos){
        MnvH2D* hist = (MnvH2D*)(f->Get(key.c_str()));
        if (hist != 0){
          response1D[sample][variable][type][category] = hist->Clone();
          response1D[sample][variable][type][category]->Print();
          response1D[sample][variable][type][category]->SetDirectory(0);
          std::cout << " response " << sample << " " << variable << " " << type << " " << category << std::endl;
          delete hist;
        }
        else{
          std::cout << "could not read " << key << std::endl;
          response1D[sample][variable][type][category]=0;
        }
      }
      // it's normal so it's a 1D.
      else{
        MnvH1D* temp = (MnvH1D*)(f->Get(key.c_str()));
        if (temp != 0){
          hists1D[sample][variable][type][category] = temp->Clone();
          hists1D[sample][variable][type][category]->Print();
          hists1D[sample][variable][type][category]->SetDirectory(0);
          std::cout << " hist 1D " << sample << " " << variable << " " << type << " " << category << std::endl;
          delete temp;
        }
        else{
          std::cout << "could not read " << key << std::endl;
          hists1D[sample][variable][type][category]=0;
        }
      }
    }

    // 2D hists
    else if(hNd == "h2D" || key.find("h2D") != std::string::npos){
      std::vector<std::string> partsof2D = split(variable,"_");
      MnvH2D* hist = (MnvH2D*)(f->Get(key.c_str()));
      // Check if response is in its name
      if (hist != 0){
        if(key.find("response")!=std::string::npos){
          response2D[sample][variable][type][category] = hist->Clone();
          response2D[sample][variable][type][category]->Print();
          response2D[sample][variable][type][category]->SetDirectory(0);
          std::cout << " 2D response " << sample << " " << variable << " " << type << " " << category << std::endl;
          delete hist;
        }
        else{
          hists2D[sample][variable][type][category] = hist->Clone();
          hists2D[sample][variable][type][category]->Print();
          hists2D[sample][variable][type][category]->SetDirectory(0);
          std::cout << " hist 2D " << sample << " " << variable << " " << type << " " << category << std::endl;
          delete hist;
        }
      }
      else{
        std::cout << "could not read " << key << std::endl;
        if(key.find("response")!=std::string::npos){
          response2D[sample][variable][type][category]=0;
        }
        else{
          hists2D[sample][variable][type][category]=0;
        }
      }
    }
  }

  // define the output file
    std::string pdfname;
    std::string outroot;
    if (singlesample){
        outroot = "analyze8_"+asample+"_"+inputname;
        
        // set up the outputs
        pdfname = "analyze8_"+asample+"_"+inputname.replace(inputname.end()-5,inputname.end(),"");
    }
    else{
        outroot = "analyze8_"+inputname;
    
        // set up the outputs
        pdfname = "analyze8_"+inputname.replace(inputname.end()-5,inputname.end(),"");
    }
    TFile* o = TFile::Open(outroot.c_str(),"RECREATE");
  std::string pdffilename1D = pdfname + "_1D.pdf";
  std::string pdfstart1D = pdfname + "_1D.pdf(";
  std::string pdfend1D = pdfname + "_1D.pdf)";
  std::string pdffilename2D = pdfname + "_2D.pdf";
  std::string pdfstart2D = pdfname + "_2D.pdf(";
  std::string pdfend2D = pdfname + "_2D.pdf)";

  o->cd();

  // Set up pdf for 1D plots.
  TCanvas canvas1D(pdffilename1D.c_str());
  canvas1D.SetLeftMargin(0.15);
  canvas1D.SetRightMargin(0.15);
  canvas1D.SetBottomMargin(0.15);
  canvas1D.SetTopMargin(0.15);
  canvas1D.Print(pdfstart1D.c_str(),"pdf");

  // bool binwid = true;  // flag you need if MnvPlotter does not do binwid correction.  If it does not, you need to set this to true

  std::cout << " just before 1D loop" << std::endl;
  for (auto samples:hists1D){
    std::string sample=samples.first;
    std::cout << " Sample: " << sample << std::endl;
    for (auto variables:hists1D[sample]){  // only do this for a subset to save output time.
      
      std::string variable = variables.first;
        if(!checktag(AnalyzeVariables,variable)){
            std::cout << " don't do this variable for now" << variable << std::endl;
            continue;
        }
      std::cout << "  Variable: " << variable << std::endl;
      std::string basename = "h_"+sample+"_"+variable;
        if (singlesample){
            basename = "h_"+variable;
        }
        std::cout << "basename is " << basename << std::endl;
      int exit = GetCrossSection(sample,variable,basename,hists1D[sample][variable],response1D[sample][variable],config,canvas1D,norm,POTScale,h_flux_dewidthed,unfold,num_iter,DEBUG);
      if (DEBUG) std::cout << exit << std::endl;
    }
  }
  std::cout << " end of 1D loop" << std::endl;
  // Close pdf for 1D plots.
  canvas1D.Print(pdfend1D.c_str(),"pdf");

  // Set up pdf for 2D plots.
  TCanvas canvas2D(pdffilename2D.c_str());
  canvas2D.SetLeftMargin(0.15);
  canvas2D.SetRightMargin(0.15);
  canvas2D.SetBottomMargin(0.15);
  canvas2D.SetTopMargin(0.15);
  canvas2D.Print(pdfstart2D.c_str(),"pdf");

  std::cout << " just before 2D loop" << std::endl;
  for (auto samples:hists2D){
    std::string sample=samples.first;

    for (auto variables:hists2D[sample]){  // only do this for a subset to save output time.
      std::string variable = variables.first;
        if(!checktag(AnalyzeVariables2D,variable)){
            std::cout << " don't do this variable for now" << variable << std::endl;
            continue;
        }
      std::string basename = "h2D_"+sample+"_"+variable;
        if (singlesample){
            basename = "h_"+variable;
        }
      int exit = GetCrossSection(sample,variable,basename,hists2D[sample][variable],response2D[sample][variable],config,canvas2D,norm,POTScale,h_flux_dewidthed,unfold,num_iter,DEBUG);
      if (DEBUG) std::cout << exit << std::endl;
    }
  }
  std::cout << " end of 2D loop" << std::endl;
  canvas2D.Print(pdfend2D.c_str(),"pdf");
  // Close pdf for 2D plots.
  

  o->Close();
  exit(0);
}
