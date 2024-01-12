#include <cstdlib>
#include <iostream>
#include <map>


#include "TChain.h"
#include "TFile.h"
#include "TTree.h"
#include "TString.h"
#include "TObjString.h"
#include "TSystem.h"
#include "TROOT.h"


#include "TMVA/Factory.h"
#include "TMVA/DataLoader.h"
#include "TMVA/Tools.h"
#include "TMVA/TMVAGui.h"


int CCQENu_TMVAClassification(TString myMethodList = ""){
  //for now just copy paste everything....
   // Default MVA methods to be trained + tested
   std::map<std::string,int> Use;

   // Cut optimisation
   Use["Cuts"]            = 1;
   Use["CutsD"]           = 1;
   Use["CutsPCA"]         = 0;
   Use["CutsGA"]          = 0;
   Use["CutsSA"]          = 0;
   //
   // 1-dimensional likelihood ("naive Bayes estimator")
   Use["Likelihood"]      = 1;
   Use["LikelihoodD"]     = 0; // the "D" extension indicates decorrelated input variables (see option strings)
   Use["LikelihoodPCA"]   = 1; // the "PCA" extension indicates PCA-transformed input variables (see option strings)
   Use["LikelihoodKDE"]   = 0;
   Use["LikelihoodMIX"]   = 0;
   //
   // Mutidimensional likelihood and Nearest-Neighbour methods
   Use["PDERS"]           = 1;
   Use["PDERSD"]          = 0;
   Use["PDERSPCA"]        = 0;
   Use["PDEFoam"]         = 1;
   Use["PDEFoamBoost"]    = 0; // uses generalised MVA method boosting
   Use["KNN"]             = 1; // k-nearest neighbour method
   //
   // Linear Discriminant Analysis
   Use["LD"]              = 1; // Linear Discriminant identical to Fisher
   Use["Fisher"]          = 0;
   Use["FisherG"]         = 0;
   Use["BoostedFisher"]   = 0; // uses generalised MVA method boosting
   Use["HMatrix"]         = 0;
   //
   // Function Discriminant analysis
   Use["FDA_GA"]          = 1; // minimisation of user-defined function using Genetics Algorithm
   Use["FDA_SA"]          = 0;
   Use["FDA_MC"]          = 0;
   Use["FDA_MT"]          = 0;
   Use["FDA_GAMT"]        = 0;
   Use["FDA_MCMT"]        = 0;
   //
   // Neural Networks (all are feed-forward Multilayer Perceptrons)
   Use["MLP"]             = 0; // Recommended ANN
   Use["MLPBFGS"]         = 0; // Recommended ANN with optional training method
   Use["MLPBNN"]          = 1; // Recommended ANN with BFGS training method and bayesian regulator
   Use["CFMlpANN"]        = 0; // Depreciated ANN from ALEPH
   Use["TMlpANN"]         = 0; // ROOT's own ANN
   Use["DNN_GPU"]         = 0; // CUDA-accelerated DNN training.
   Use["DNN_CPU"]         = 0; // Multi-core accelerated DNN.
   //
   // Support Vector Machine
   Use["SVM"]             = 1;
   //
   // Boosted Decision Trees
   Use["BDT"]             = 1; // uses Adaptive Boost
   Use["BDTG"]            = 0; // uses Gradient Boost
   Use["BDTB"]            = 0; // uses Bagging
   Use["BDTD"]            = 0; // decorrelation + Adaptive Boost
   Use["BDTF"]            = 0; // allow usage of fisher discriminant for node splitting
   //
   // Friedman's RuleFit method, ie, an optimised series of cuts ("rules")
   Use["RuleFit"]         = 1;
   // ---------------------------------------------------------------

   TFile *input(0);
   //TString fname = "./files/For_TMVA_small_1.root";
   TString fname = "files/For_TMVA_small_1.root";
   input = TFile::Open(fname);

   if(!input){
     std::cout<<"ERROR::File Not Found "<<fname<<std::endl;
     exit(1);
   }
   TTree *signalTree = (TTree*)input->Get("QELike");
   TTree *background = (TTree*)input->Get("QELikeNot");

   TString outputfileName("CCQENu_TMVA_small_1.root");
   TFile* outputFile = TFile::Open( outputfileName,"RECREATE");

   //Create the factor object. Later you can choose the methods whose performance
   //you'd like to investigate. The factory is the only object you have to interact
   //


   //Basically we want to investigate the various methods and compare their
   //performances.....

   TMVA::Factory *factory = new TMVA::Factory("CCQENu_TMVAClassification",outputFile,"!V:Silent:Color:DrawProgressBar::Transformations=I;D;P;G,D:AnalysisType=Classification");

   //now use the data loader...
   TMVA::DataLoader *dataloader = new TMVA::DataLoader("dataset");
   // If you wish to modify default settings
   // (please check "src/Config.h" to see all available global options)
   //
   //    (TMVA::gConfig().GetVariablePlotting()).fTimesRMS = 8.0;
   //    (TMVA::gConfig().GetIONames()).fWeightFileDir = "myWeightDirectory";

   // Define the input variables that shall be used for the MVA training
   // note that you may also use variable expressions, such as: "3*var1/var2*abs(var3)"
   // [all types of expressions that can also be parsed by TTree::Draw( "expression" )]

    dataloader->AddVariable("cos_theta","theta","units",'F');
    dataloader->AddVariable("phi","phi","units",'F');
    dataloader->AddVariable("Q2","4 Mom transfer","GeV2",'F');
   dataloader->AddVariable("recoil_E","Recoil Energy","GeV",'F');
   dataloader->AddVariable("muon_p","tot mom","GeV",'F');
    dataloader->AddVariable("pion_score","pion score","units",'F');
    //  dataloader->AddVariable("multiplicity","tracks","units",'I');
   //I will add the intype as the spectator.....
   dataloader->AddSpectator("mcIntType","mc type","units",'I');
   dataloader->AddSpectator("weight"," weight ","units",'F');

   Double_t signalWeight = 1.0;
   Double_t backgroundWeight = 1.0;

   dataloader->AddSignalTree(signalTree,signalWeight);
   dataloader->AddBackgroundTree(background,backgroundWeight);

   dataloader->SetBackgroundWeightExpression("weight");

   TCut mycuts = "pion_score>0.0&&muon_p<20.0&&recoil_E<0.4&&Q2<2.0";
   TCut mycutb = "pion_score>0.0&&muon_p<20.0&&recoil_E<0.4&&Q2<2.0";
   //use half sample for signal and half sample for bkg
   dataloader->PrepareTrainingAndTestTree(mycuts,mycutb,"SplitMode=random:!V");


   // ### Book MVA methods
   //
   // Please lookup the various method configuration options in the corresponding cxx files, eg:
   // src/MethoCuts.cxx, etc, or here: http://tmva.sourceforge.net/optionRef.html
   // it is possible to preset ranges in the option string in which the cut optimisation should be done:
   // "...:CutRangeMin[2]=-1:CutRangeMax[2]=1"...", where [2] is the third input variable

   // Cut optimisation
 
   // Likelihood ("naive Bayes estimator")
   if (Use["Likelihood"])
      factory->BookMethod( dataloader, TMVA::Types::kLikelihood, "Likelihood",
                           "H:!V:TransformOutput:PDFInterpol=Spline2:NSmoothSig[0]=20:NSmoothBkg[0]=20:NSmoothBkg[1]=10:NSmooth=1:NAvEvtPerBin=50" );

   // Decorrelated likelihood
   if (Use["LikelihoodD"])
      factory->BookMethod( dataloader, TMVA::Types::kLikelihood, "LikelihoodD",
                           "!H:!V:TransformOutput:PDFInterpol=Spline2:NSmoothSig[0]=20:NSmoothBkg[0]=20:NSmooth=5:NAvEvtPerBin=50:VarTransform=Decorrelate" );
   std::cout<<" USED THE LIKELIHOOD" <<std::endl;
   // PCA-transformed likelihood
    if (Use["BDT"])  // Adaptive Boost  
      factory->BookMethod( dataloader, TMVA::Types::kBDT, "BDT",
                           "!H:!V:NTrees=850:MinNodeSize=2.5%:MaxDepth=3:BoostType=AdaBoost:AdaBoostBeta=0.5:UseBaggedBoost:BaggedSampleFraction=0.5:SeparationType=GiniIndex:nCuts=20" );

   // For an example of the category classifier usage, see: TMVAClassificationCategory
   //
   // --------------------------------------------------------------------------------------------------
   //  Now you can optimize the setting (configuration) of the MVAs using the set of training events
   // STILL EXPERIMENTAL and only implemented for BDT's !
   //
   //     factory->OptimizeAllMethods("SigEffAt001","Scan");
   //     factory->OptimizeAllMethods("ROCIntegral","FitGA");
   //
   // --------------------------------------------------------------------------------------------------

   factory->TrainAllMethods();

   factory->TestAllMethods();

   factory->EvaluateAllMethods();
   outputFile->Close();
 
   auto c1 = factory->GetROCCurve(dataloader);  

   delete factory;
   delete dataloader;

   if (!gROOT->IsBatch()) TMVA::TMVAGui( outputfileName );
   
   return 0;
   
}
