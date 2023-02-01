#include <iostream>
#include <string>
#include <fstream>
#include <sys/stat.h>
#include <algorithm>
#include "PlotUtils/MnvH1D.h"
#include "PlotUtils/MnvH2D.h"
#include "PlotUtils/MnvH1DToCSV.h"
#include "TFile.h"
#include "TROOT.h"
#include "TStyle.h"
#include "TTree.h"
#include "TKey.h"
#include "TCanvas.h"

// To use this type "./getCSVs [filename]" without ".root" for any root file with MnvH1Ds.

std::vector<std::string> split (std::string s, std::string delimiter) {
  size_t pos_start = 0, pos_end, delim_len = delimiter.length();
  std::string token;
  std::vector<std::string> res;
  
  while ((pos_end = s.find (delimiter, pos_start)) != std::string::npos) {
    token = s.substr (pos_start, pos_end - pos_start);
    pos_start = pos_end + delim_len;
    res.push_back (token);
  }
  
  res.push_back (s.substr (pos_start));
  return res;
}

int main(const int argc, const char *argv[]){

    // Read in root file
    std::string rootFile = std::string(argv[1])+".root";
    std::cout << std::endl;
    std::cout << "Reading in\n\n\t\033[1;34m./\033[1;33m" << rootFile << "\033[0m\n";
    std::cout << std::endl;
    TFile *file = new TFile(rootFile.c_str(),"READONLY");

    // Make directory for storying outputs
    std::cout << "Creating directory\n\n\t\033[1;34m./" << argv[1] << "/\033[0m\n" << std::endl;
    mkdir(argv[1], 0777);

    /////////////////////////////////////////////////////////////////////////////////////////
    //////////////// Extracting information on every object in the root file ////////////////
    /////////////////////////////////////////////////////////////////////////////////////////

    // Declare empty containers for objects and their information
    std::vector<std::string> keys;
    std::map<std::string, std::string> classes;
    std::map<std::string, std::string> titles;
    std::map<std::string, std::string> cycles;
    std::map<std::string, std::vector<std::string>> parsekey;

    // Cycle through objects in root file
    std::cout << "Extracting object information..." << std::endl;
    for(TObject* keyAsObj : *file->GetListOfKeys())
    { 
        // Get object key
        auto key = dynamic_cast<TKey*>(keyAsObj);
        std::string name = key->GetName();

        // Fill information containers
        keys.push_back(name);
        classes[name] = key->GetClassName();
        titles[name] = key->GetTitle(); 
        cycles[name] = key->GetCycle();
    }

    /////////////////////////////////////////////////////////////////////////////////////////
    ////////// Creating csv file to externally store information about each object //////////
    /////////////////////////////////////////////////////////////////////////////////////////

    // Due to commas in collected data, items separated with a semi-colons

    // Initiate object list output file
    std::string listFile = std::string(argv[1])+"_Objects.csv";
    std::cout << "Putting object information in\n\n\t\033[1;34m./" << argv[1] << "/";
    std::cout << "\033[1;33m" << listFile << "\033[0m\n" << std::endl;
    std::ofstream keyfile;
    keyfile.open(("./"+std::string(argv[1])+"/"+listFile).c_str());
    keyfile << "Key;Class;Title" << std::endl; // Column headers

    // Loop over keys to add info to file
    for(auto name : keys)
    {
        // Write information to object list file
        if(classes[name] == "PlotUtils::MnvH1D" ||
           classes[name] == "PlotUtils::MnvH2D"   ) {
		    keyfile << name << ";";
		    keyfile << classes[name] << ";";
		    keyfile << titles[name] << std::endl;
		}
    }

    // Close object list output file
    keyfile.close();

    /////////////////////////////////////////////////////////////////////////////////////////
    /////////////////////// Creating csv file to store parsekey stuff ///////////////////////
    /////////////////////////////////////////////////////////////////////////////////////////

    // Initiate  output file
    std::string parseFile = std::string(argv[1])+"_ParseKey.csv";
    std::cout << "Parsing keys..." << std::endl;
    std::cout << "Putting parsed keys in" << std::endl;
    std::cout << "\n\t\033[1;34m./" << argv[1] << "/\033[1;33m" << parseFile << "\033[0m\n";
    std::cout << std::endl;
    std::ofstream parsefile;
    parsefile.open(("./"+std::string(argv[1])+"/"+parseFile).c_str());
    parsefile << "key,size,[0],[1],[2]";
    parsefile << ",[3],[4]" << std::endl; // Column headers

    // Loop over keys to add info to file
    for(auto name : keys)
    {
        // Split Key
        parsekey[name] = split(name,"___");
        parsefile << name << "," << parsekey[name].size() << ",";
        // print splitted key
        for(int i = 0; i < parsekey[name].size(); i++){
            parsefile << parsekey[name][i] << ",";
        }
        parsefile << std::endl;
    }

    // Close object list output file
    parsefile.close();

    /////////////////////////////////////////////////////////////////////////////////////////
    ////////////////////// Retrieving histogram objects from root file //////////////////////
    /////////////////////////////////////////////////////////////////////////////////////////

    // Create empty containers for histograms
    std::map<std::string, PlotUtils::MnvH1D*> hists_1d;
    std::map<std::string, PlotUtils::MnvH2D*> hists_2d;
    std::vector<std::string> hists_1d_keys;
    std::vector<std::string> hists_2d_keys;

    // Looping over keys to fill histogram containers
    std::cout << "Extracting histograms..." << std::endl;
    for(auto name : keys)
    {
        if(classes[name] == "PlotUtils::MnvH1D")
        {
            hists_1d_keys.push_back(name);
            hists_1d[name] = (PlotUtils::MnvH1D*)file->Get(name.c_str());
            hists_1d[name]->SetDirectory(0);
        }
        else if(classes[name] == "PlotUtils::MnvH2D")
        {
            hists_2d_keys.push_back(name);
            hists_2d[name] = (PlotUtils::MnvH2D*)file->Get(name.c_str());
            hists_2d[name]->SetDirectory(0);
        }
    }

    // Closing root file
    file->Close();

    /////////////////////////////////////////////////////////////////////////////////////////
    ////////////////////// Creating pdf to print each histogram object //////////////////////
    /////////////////////////////////////////////////////////////////////////////////////////
    
    // Initializing pdf file and TCanvas
    std::string pdfFileName = "hists_"+std::string(argv[1])+".pdf";
    std::cout << "Drawing histograms to\n\n\t\033[1;34m./" << argv[1] << "/";
    std::cout << "\033[1;33m" << pdfFileName << "\033[0m\n" << std::endl;
    TCanvas canvas(pdfFileName.c_str());
    canvas.SetLeftMargin(0.15);
    canvas.SetBottomMargin(0.15);
    canvas.cd();
    //canvas.Print(Form("%s(",pdfFileName.c_str()));
    canvas.Print(Form("%s(",("./"+std::string(argv[1])+"/"+pdfFileName).c_str()));

    // Looping over keys to draw histograms
    for(auto name : hists_1d_keys){
        hists_1d[name]->Draw("pe");
        canvas.Print(("./"+std::string(argv[1])+"/"+pdfFileName).c_str());
    }
    for(auto name : hists_2d_keys){
        hists_2d[name]->Draw("h");
        canvas.Print(("./"+std::string(argv[1])+"/"+pdfFileName).c_str());
    }

    //canvas.Print(Form("%s)",pdfFileName.c_str()));
    canvas.Print(Form("%s)",("./"+std::string(argv[1])+"/"+pdfFileName).c_str()));
    std::cout << std::endl;

    /////////////////////////////////////////////////////////////////////////////////////////
    //////////////////// Rework of MnvH1DToCSV to make useable csv files ////////////////////
    /////////////////////////////////////////////////////////////////////////////////////////

    std::cout << std::endl;
    // directory.csv describes the organization of the generated csv files
    std::ofstream *f_directory = new std::ofstream();
    f_directory->open(("./"+std::string(argv[1])+"/directory.csv").c_str());
    *f_directory << "variable,event,source,histogram" << std::endl;//covariance,";
    //*f_directory << ",sysdump,sysdump_meta" << std::endl;//,sysdump_covariance" << std::endl;

    // Keep track of variable use instances
    std::vector<std::string> variablesUsed;

    // loop over each 1D histogram name
    for(auto name : hists_1d_keys){
		
        if(parsekey[name][3] == titles[name]){
            int timesUsed = 0;
            if(variablesUsed.size() > 0) {
		        for(auto vars : variablesUsed){
		            if(vars == parsekey[name][3]){
		                timesUsed++;
		            }
				}
            }
            variablesUsed.push_back(parsekey[name][3]);

            // Fill directory.csv with names and descriptors
            *f_directory << parsekey[name][3]+","+parsekey[name][1]+","+parsekey[name][2]+",";
            *f_directory << parsekey[name][3]+"_"+parsekey[name][1]+"_"+parsekey[name][2]+"_1d.csv,";
            *f_directory << std::endl;
            //*f_directory << parsekey[name][1]+"_"+parsekey[name][3]+"_covariance.csv,";
            /*if(parsekey[name][2] != "data"){
                *f_directory << parsekey[name][3]+"_"+parsekey[name][1]+"_"+parsekey[name][2]+"_sysdump.csv,";
                *f_directory << parsekey[name][3]+"_"+parsekey[name][1]+"_"+parsekey[name][2]+"_sysdump_meta.csv,";
            } else{ // data does not have systematic universes
                *f_directory << "NA,NA" << std::endl;//,NA" << std::endl;
            }*/
            
            // Identify variable folder. Make folder if first showing of variable.
            std::string folderName = std::string("./"+std::string(argv[1])+"/"+parsekey[name][1]);
            if(timesUsed == 0){
                std::cout << std::endl << "Creating directory\n" << std::endl;
                std::cout << "\t\033[1;34m" << folderName << "/\033[0m" << std::endl;
                mkdir(folderName.c_str(), 0777);
            }

            double scale = 1.0; // Gets used by coorelation matrix

            std::cout << "\n\tConverting MnvH1D " << name << " to CSV files\n" << std::endl;
            std::cout << "\t\t\033[1;34m" << folderName << "/\033[1;33m" << parsekey[name][3];
            std::cout << "_"+parsekey[name][1]+"_"+parsekey[name][2]+"_1d.csv\033[0m\n";
            //std::cout << "\t\t\033[1;34m" << folderName << "/\033[1;33m" << parsekey[name][1];
            //std::cout << "_" << parsekey[name][3] << "_covariance.csv\033[0m\n";

            std::ofstream *f_hist = new std::ofstream();
            //std::ofstream *f_corr = new std::ofstream();

            f_hist->open((folderName+"/"+parsekey[name][3]+"_"+parsekey[name][1]+"_"+parsekey[name][2]+"_1d.csv").c_str());
            //f_corr->open((folderName+"/"+parsekey[name][1]+"_"+parsekey[name][3]+"_covariance.csv").c_str());

            TH1D stat = hists_1d[name]->GetStatError(); //stat error
            TH1D total = hists_1d[name]->GetCVHistoWithError(); // CV with total error
            TH1D sys = hists_1d[name]->GetTotalError(false); //sys error only

            // fill histogram info - includes bin info, counts, and errors
            *f_hist << "binLow,binHigh,Counts,totalError,statError,sysError" << std::endl;
            for(int i=1; i <= hists_1d[name]->GetXaxis()->GetNbins(); i++){
                if(i>1){
                    *f_hist << std::endl;
                }
                // Currently not bin width normalizing
                *f_hist << hists_1d[name]->GetXaxis()->GetBinLowEdge(i) << ",";
                *f_hist << hists_1d[name]->GetXaxis()->GetBinUpEdge(i) << ",";
                *f_hist << Form("%.17e",total.GetBinContent(i)) << ",";
                *f_hist << Form("%.17e",total.GetBinError(i)) << ",";///(hists_1d[name]->GetXaxis()->GetBinWidth(i))*scale);
                *f_hist << Form("%.17e",stat.GetBinContent(i)) << ",";///(hists_1d[name]->GetXaxis()->GetBinWidth(i))*scale);
                *f_hist << Form("%.17e",sys.GetBinContent(i));///(hists_1d[name]->GetXaxis()->GetBinWidth(i))*scale);
            }
            *f_hist << std::endl;
            f_hist->close();

            // TMatrixD correlation_matrix= hist->GetTotalCorrelationMatrix();
            //TMatrixD correlation_matrix = hists_1d[name]->GetTotalErrorMatrix();
            //correlation_matrix *= (scale*scale); // scale by factor of 10^41

            int nbins_x = hists_1d[name]->GetNbinsX();
            int totalbins = (nbins_x+2);

            for (int x=0; x<totalbins; x++){
                double binwidcorri;
                binwidcorri = hists_1d[name]->GetXaxis()->GetBinWidth(x);
                if(x==0 || x==nbins_x+1) continue;
                for(int this_x=0; this_x<totalbins; this_x++){
                    if  (this_x==0 || this_x==nbins_x+1 ) continue;
                    double binwidcorrj;
                    binwidcorrj = hists_1d[name]->GetXaxis()->GetBinWidth(this_x);
                    //if (this_x > 1) *f_corr<< ","; 
                    //*f_corr<<Form("%.17e ",correlation_matrix[x][this_x]);///binwidcorri/binwidcorrj);
                    // need to include bin widths
                }
                //*f_corr<<std::endl;
            }
            //f_corr->close();

            // Systematics only for MC
            if(parsekey[name][2] == "data") continue;

            // Systematics
            std::cout << "\t\t\033[1;34m" << folderName << "/\033[1;33m" << parsekey[name][3];
            std::cout << "_" << parsekey[name][1] << "_" << parsekey[name][2] << "_sysdump.csv\033[0m\n";
            std::cout << "\t\t\033[1;34m" << folderName << "/\033[1;33m" << parsekey[name][3];
            std::cout << "_" << parsekey[name][1] << "_" << parsekey[name][2] << "_sysdump_meta.csv\033[0m\n";

            std::ofstream * f_errors = new std::ofstream();
            std::ofstream * f_errors_meta = new std::ofstream();

            //f_errors->open((folderName+"/"+parsekey[name][3]+"_"+parsekey[name][1]+"_"+parsekey[name][2]+"_sysdump.csv").c_str());
            //f_errors_meta->open((folderName+"/"+parsekey[name][3]+"_"+parsekey[name][1]+"_"+parsekey[name][2]+"_sysdump_meta.csv").c_str());

            std::vector<std::string> vert_errBandNames = hists_1d[name]->GetVertErrorBandNames();
            std::vector<std::string> lat_errBandNames  = hists_1d[name]->GetLatErrorBandNames();
            std::vector<std::string> uncorr_errBandNames  = hists_1d[name]->GetUncorrErrorNames();
            //std::vector<std::string> cov_errNames = hists_1d[name]->GetCovMatricesNames();

            // Finish directory input based on if cov_errNames is needed
            /*if(cov_errNames.size() > 0){
                *f_directory << parsekey[name][1]+"_"+parsekey[name][3]+"_sysdump_covariance.csv";
                *f_directory << std::endl;
            } else{
                *f_directory << "NA" << std::endl;
            }*/

            // Create matrix to store row sorted data -> column sort for CSV file entry  
            std::map<int,std::map<int,std::string>> sys_matrix;
            // Counter for keeping track of matrix indexing across vert/lat
            int sys_counter = 1;

            *f_errors << "binLow,binHigh";
            *f_errors_meta << "vert," << vert_errBandNames.size() <<  std::endl;

            if(vert_errBandNames.size() > 0){
                for(std::vector<std::string>::iterator bname=vert_errBandNames.begin(); bname!=vert_errBandNames.end(); ++bname ){
                    PlotUtils::MnvVertErrorBand* v = hists_1d[name]->GetVertErrorBand(*bname);
                    unsigned int nunis = v->GetNHists();
                    for(int i = 0; i < nunis; i++){
                        *f_errors << Form(",%s_%d",bname->c_str(),i); //<< std::endl;
                        TH1* h = v->GetHist(i);
                        for(int j=1; j <= h->GetXaxis()->GetNbins(); j++){
                            sys_matrix[j][sys_counter] = Form("%.17e",h->GetBinContent(j));///(h->GetXaxis()->GetBinWidth(j))*scale);
                            //*f_errors << Form("%.17e,",h->GetBinContent(j));///(h->GetXaxis()->GetBinWidth(j))*scale);
                        }
                        //*f_errors << std::endl;
                        sys_counter++;
                    }
                }
            }
            
            *f_errors_meta << "Lat," << lat_errBandNames.size() <<  std::endl;
            if(lat_errBandNames.size() > 0){
                for(std::vector<std::string>::iterator bname=lat_errBandNames.begin(); bname!=lat_errBandNames.end(); ++bname ){
                    PlotUtils::MnvLatErrorBand* v = hists_1d[name]->GetLatErrorBand(*bname);
                    unsigned int nunis = v->GetNHists();
                    for(int i = 0; i < nunis; i++){
                        //*f_errors << Form(",%s_%d",bname->c_str(),i); //<< std::endl;
                        TH1* h = v->GetHist(i);
                        for(int j=1; j <= h->GetXaxis()->GetNbins(); j++){
                            sys_matrix[j][sys_counter] = Form("%.17e",h->GetBinContent(j));///(h->GetXaxis()->GetBinWidth(j))*scale);
                            //*f_errors << Form("%.17e,",h->GetBinContent(j));///(h->GetXaxis()->GetBinWidth(j))*scale);
                        }
                        //*f_errors << std::endl;
                        //sys_counter++;
                    }
                }
            }
            
            /**f_errors_meta << "covariance," << cov_errNames.size() <<  std::endl;
            // Currently not modifying this much, but putting in its own csv file.
            if(cov_errNames.size() > 0){

                std::cout << "\t\t\033[1;34m" << folderName << "/\033[1;33m" << parsekey[name][1];
                std::cout << "_" << parsekey[name][3] << "_sysdump_covariance.csv\033[0m\n";

                std::ofstream * f_errors_corr = new std::ofstream();
                f_errors_corr->open((folderName+"/"+parsekey[name][1]+"_"+parsekey[name][3]+"_sysdump_covariance.csv").c_str());

                for( std::vector<std::string>::iterator cname=cov_errNames.begin(); cname!=cov_errNames.end(); ++cname ){
                    TMatrixD  v = hists_1d[name]->GetSysErrorMatrix(*cname);
                    *f_errors_corr << Form("%s",cname->c_str()) << std::endl;
                    int nbins_x = hists_1d[name]->GetXaxis()->GetNbins();
                    int totalbins=(nbins_x+2);
                    for (int x=0;x<totalbins;x++){
                        double binwidcorri;
                        binwidcorri = hists_1d[name]->GetXaxis()->GetBinWidth(x);
                        if (x==0 ||  x==nbins_x+1 ) continue; // Do not print overflow and underflow
                        for (int this_x=0; this_x<totalbins; this_x++){
                            if  (this_x==0 || this_x==nbins_x+1 ) continue; // Do not print overflow and underflow
                            double binwidcorrj;
                            binwidcorrj = hists_1d[name]->GetXaxis()->GetBinWidth(this_x);
                            if (this_x > 1) *f_errors_corr<< ",";
                            *f_errors_corr<<Form("%.17e ",v[x][this_x]/binwidcorri/binwidcorrj*scale*scale);
                            // need to include bin widths
                        }

                        *f_errors_corr<<std::endl;

                    }
                }

                f_errors_corr->close();

            }*/
            
            // Cycles through the matrix and fills the CSV file
            *f_errors << std::endl;
            for(int i=1; i <= hists_1d[name]->GetXaxis()->GetNbins(); i++){
               *f_errors << hists_1d[name]->GetXaxis()->GetBinLowEdge(i);
               *f_errors << "," << hists_1d[name]->GetXaxis()->GetBinUpEdge(i);
               for(int j=1; j < sys_counter; j++){
                   *f_errors << "," << sys_matrix[i][j];
               }
               *f_errors << std::endl;
           }

            f_errors->close();
            f_errors_meta->close();
            
        }
    }
    f_directory->close();

    std::cout << std::endl;

    return 0;
}


/*


hist->GetEntries()
hist->GetEffectiveEntries()????????????


hist->GetNbinsX()
hist->GetXaxis()->GetBinLowEdge(i)
hist->GetXaxis()->GetBinUpEdge(i)
hist->GetBinContent(i)

hist->GetBinContent(i,j)








*/
