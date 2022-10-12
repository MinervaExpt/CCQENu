import sys,os,string
import math

# version 10 implement new low q2 error band from /minerva/data/users/drut1186/Mateus_Pub_Inputs/Modified_AddedLowQ2Suppression
from ROOT import *

from PlotUtils import *

from chi2utils import *



NOSYS = True  # I think this means don't look at systematic errors individually

BIN = False # do the chi2 without binwidth correcting things

debin = True

Ratio = True # this is just for plotting

FIXEDSCALE = 1.E39
SCALE = 1.

Mateus = False # no longer doing Mateus

Diagonal = False  # ignore offdiagonal terms in chi2

minb = 0

q2 = "q2"

nounfold = False

basemodel="CV"

extramodels= ""

varname = {"q2":"$Q^2$","ptmu":"$p_\perp$","pzmu":"p_\parallel","pzmu_ptmu":"$p_\parallel - p_#perp$","enu":"E_\nu"
}



dir = "/Users/schellma/Dropbox/ccqe/v27b"



#if Mateus:
#  #dir = dir.replace("/Users/schellma/Dropbox/ccqe/MT/","/pnfs/minerva/persistent/users/mateusc/")
#mcdir = mcdir.replace("/Users/schellma/Dropbox/ccqe/MT/","/pnfs/minerva/persistent/users/mateusc/")
#  dir = dir.replace("MT","FNAL")
  
#* CV/ (MinervaGENIE v1: +2p2h+recoil+RPA $\pi$tune)
#* default/  (+2p2h)
#* CV_RPA_Res_MINOS/ (+2p2h+recoil+RPA $\pi$tune+MINOS low q2 sup.)
#* CV_RPA_Res_Nieves/ (+2p2h+recoil+RPA $\pi$tune+Nieves low q2 sup.)
#* $\pi$tune/ (+2p2h $\pi$tune)
#* pion_2p2h/  (+2p2h+recoil fit $\pi$tune)
#* pion_rpa/  (+2p2h+RPA+ NonRES $\pi$tune)

#    For the record following are the root files and relevant histograms for the q2qe
#
#Nuwro:
#/pnfs/minerva/persistent/users/mateusc/CCQENu_v21r1p1_Pub_Sep2019ntuples_YESNue_Nov11_CV/QELike_ME_Mateus_Nuwro_v1902_600M.root
#> nuwroSF_kQsqQE_all
#> nuwroLFG_kQsqQE_all
#
#GIBUU:
#/pnfs/minerva/persistent/users/mateusc/CCQENu_v21r1p1_Pub_Sep2019ntuples_YESNue_Nov11_CV/MMECCQEGiBUU.root
#> q2qeall (inside folder MMECCQEGiBUUnu)
#
#Geniev3:
#/pnfs/minerva/persistent/users/mateusc/CCQENu_v21r1p1_Pub_Sep2019ntuples_YESNue_Nov11_CV/MMECCQEGENIEOOB_30000000Evts_20191003.root
#> q2qeall (inside folder MMECCQEGENIEOOBnu)
#
#We don't currently have text versions of the external results and they are not implemented in the scripts as they still look for the analysis name standards. i can try to add them to the scripts latter today.
var = "pzmu_ptmu"
norm = 1.0
full = False  # this switches to the full acceptance
if len(sys.argv)>= 2:
  var = sys.argv[1]
if len(sys.argv)>=3:
    full = (sys.argv[2] == "Full")

if var == "q2":
    dir += "/ver2"
if "enu" in var:
    dir += "/ver3"

mcdir = dir
#models = ["default","CV","piontune","pion_rpa","CV_RPA_Res_MINOS","CV_RPA_Res_Nieves","pion_2p2h","CV_minerva_joint_lowq2"]
#models = ["default","CV","CV_RPA_Res_MINOS","piontune","pion_2p2h","pion_rpa","CV_minerva_joint_lowq2"]
models = ["CV", "2p2h", "2p2hRPA", "CV2", "PionTune", "RPAPionTune", \
"2p2hPionTune", "NA", "RPA"]

models = ["CV", "CV2","NA", "piontune", "rpa","rpapiontune", "2p2h", "2p2hrpa",  \
"2p2hpiontune"]
if "enu" not in var:
    models.append("GENIE_no2p2h")
    
if full:
    models = ["CV","CV2"]
#models = ["CV","NA","GENIE_no2p2h"]
n = len(models)
bmodels = models
print (models)
models = []
#for model in bmodels[0:n]:
#  print "this is a model"
#  models.append(model+"-no-2p2h")
for model in bmodels:
  models.append(model)
  
#extramodels = ["GiBUU","NuWroSF","NuWroLFG","Geniev3"]
#if var != "enu":
#  models = models + extramodels

print (models)

if "mu" in var:
    models.append("G18_02a_02_11a")
    models.append("G18_02b_02_11a")
    models.append("G18_10a_02_11a")
    models.append("G18_10b_02_11a")

titles = {"pzmu":"p_{||}, GeV/c","ptmu":"p_{#perp}, GeV/c","enu":"E_{#nu}, GeV","enuQE":"E_{#nu QE}, GeV","q2":"Q^2_{QE}, GeV^2","pzmu_ptmu":":p_{||}, GeV/c;p_{#perp}, GeV/c"}
translate={
"2p2hrpa":"GENIE+recoil fit+RPA",
"rpapiontune":"GENIE+RPA+$\pi$tune",
"NA":"GENIE 2.12.6",
"CV2":"GENIE+recoil fit+RPA+$\pi$tune+MINOS low $Q^2$ sup. (MnvGENIEv2)",
"piontune":"GENIE+$\pi$tune",
"rpapiontune":"GENIE+RPA+$\pi$tune",
"2p2h":"GENIE+recoil fit ",
"2p2hpiontune":"GENIE+recoil fit+$\pi$tune",
"2p2hrpapiontune":"GENIE+recoil fit+RPA+$\pi$tune",
"rpa":"GENIE+RPA",
"CV":"GENIE+RPA+$\pi$tune+recoil fit (MnvGENIEv1)",
"CV_RPA_Res_MINOS":"\qquad+recoil fit+RPA+$\pi$tune+MINOS low $Q^2$ sup."
#"default":"GENIE + 2p2h",
#"piontune":"\qquad+$\pi$tune",
#"pion_rpa":"\qquad+RPA+$\pi$tune",
#"pion_2p2h":"\qquad+recoil fit+$\pi$tune",
#"CV_RPA_Res_Nieves":"\qquad+recoil fit+RPA+$\pi$tune+Nieves low $Q^2$ sup.",
#"CV-no-2p2h":"%+recoil fit+RPA+$\pi$tune",
#"CV_RPA_Res_MINOS-no-2p2h":"\qquad+RPA+$\pi$tune+MINOS low $Q^2$ sup.",
#"default-no-2p2h":"GENIE",
#"piontune-no-2p2h":"\qquad+$\pi$tune",
#"pion_rpa-no-2p2h":"\qquad+RPA+$\pi$tune",
#"pion_2p2h-no-2p2h":"%+recoil fit+$\pi$tune",
#"CV_RPA_Res_Nieves-no-2p2h":"%+recoil fit+RPA+$\pi$tune+Nieves low $Q^2$ sup.",
#"GiBUU":"GiBUU",
#"NuWroSF":"NuWro SF","NuWroLFG":"NuWro LFG",
#"Geniev3":"GENIE v3",
#"CV_minerva_joint_lowq2":"\qquad+recoil fit+RPA + $\pi$tune + MINERvA low $Q^2$ sup.",
#"CV_minerva_joint_lowq2-no-2p2h":"%+recoil fit + RPA + $\pi$tune  + MINERvA  low $Q^2$ sup.",
#"2p2h":"GENIE + 2p2h"
}

# from Amit 4-17-2022
#2p2h --> GENIE+2p2h+Low Recoil Tunes
#2p2hpion -->GENIE+2p2h+pion tune+ Low Recoil Tunes
#2p2hrpa --> GENIE+2p2h+RPA+Low Recoil Tunes
#CV -->MINERvA Tune v1
#CV2 -->MINERvA Tune v2
#NA -->GENIE +2p2h
#piontune -->GENIE +2p2h +pion tune
#rpa -->GENIE+2p2h+RPA
#rpapiontune --> GENIE+2p2h+RPA+piontune
translate={
"2p2hrpa":"GENIE+2p2h+Low Recoil Tune+RPA",
"rpapiontune":"GENIE+2p2h+RPA+$\pi$tune",
"NA":"GENIE 2.12.6 (Default)",
"GENIE_no2p2h":"GENIE 2.12.6 w/o 2p2h",
"CV2":"MINERvA Tune v2",
"piontune":"GENIE+$\pi$tune",
"rpapiontune":"GENIE+2p2h+RPA+$\pi$tune",
"2p2h":"GENIE+2p2h+Low Recoil Tune",
"2p2hpiontune":"GENIE+Low Recoil Tune+$\pi$tune",
"2p2hrpapiontune":"GENIE+Low Recoil Tune+RPA+$\pi$tune",
"rpa":"GENIE+2p2h+RPA",
"CV":"MINERvA Tune v1",
"CV_RPA_Res_MINOS":"\qquad+Low Recoil Tune+RPA+$\pi$tune+MINOS low $Q^2$ sup."
}
translate={
"2p2hrpa":"GENIE2+Low Recoil Tune+RPA",
"rpapiontune":"GENIE2+RPA+$\pi$tune",
"NA":"GENIE 2.12.6 (Default)",
"GENIE_no2p2h":"GENIE 2.12.6 w/o 2p2h",
"CV2":"MINERvA Tune v2",
"piontune":"GENIE2+$\pi$tune",
"2p2h":"GENIE2+Low Recoil Tune",
"2p2hpiontune":"GENIE2+Low Recoil Tune+$\pi$tune",
"2p2hrpapiontune":"GENIE2+Low Recoil Tune+RPA+$\pi$tune",
"rpa":"GENIE2+RPA",
"CV":"MINERvA Tune v1",
"CV_RPA_Res_MINOS":"\qquad+Low Recoil Tune+RPA+$\pi$tune+MINOS low $Q^2$ sup.",
"G18_02a_02_11a":"GENIE3 G18\_02a\_02\_11a",
"G18_02b_02_11a":"GENIE3 G18\_02b\_02\_11a",
"G18_10a_02_11a":"GENIE3 G18\_10a\_02\_11a",
"G18_10b_02_11a":"GENIE3 G18\_10b\_02\_11a"
}
#models = ["default"]
#models = ["$\pi$tune","pion_rpa","pion_2p2h"]

#if "mu" in var:
#  basehist = "Modified_Pzmu.root"
#else:
#  if "q2" in var:
#    basehist = "Modified_q2.root"
#  else:
#    print "no mod hist for this variable"
#    sys.exit(1)

#basehist = "h_pzmu_ptmu_data_nobck_unfold_effcor_cross_section"
#
#mcbasehist = "h_pzmu_ptmu_qelikecomp_cross_section"



basehist = "h_pzmu_ptmu_dataCrossSection"
mcbasehist = "h_pzmu_ptmu_qelike_crossSection"
geniehist = "ptpz_qelike"

if "enu" == var:
    basehist = "True_Xsection_data_stat"
    mcbasehist = "True_Xsection_data_stat"
    if full:
       basehist = "Fid_Xsection_data_stat"
       mcbasehist = "Fid_Xsection_data_stat"
      

if "enuQE" == var:
    basehist = "QE_Xsection_data_stat"
    mcbasehist = "QE_Xsection_data_stat"

if var not in ["q2","enu","pzmu","ptmu","pzmu_ptmu","enu_q2", "enuQE"]:
  print (" don't recognize input", var)
  sys.exit(0)

if var in ["q2","enu","enu_q2","enuQE"]:
  
  basehist = basehist.replace("pzmu_ptmu","enu_q2")
  mcbasehist = mcbasehist.replace("pzmu_ptmu","enu_q2")



proj = ""
if var in ["enu","pzmu","enuQE"]:
  proj = "_px"
if var in ["ptmu","q2"]:
  proj = "_py"



#thefile = "CrossSection_CombinedPlaylists-CombinedPlaylists-me1Bme1Cme1Dme1Eme1Fme1Gme1Lme1Mme1Nme1Ome1P_v3.root"
#path = "/Users/schellma/Dropbox/ccqe/v27b/"
#thefile = "%sXS_%s_proj_%s.root"%(path,var,model)
## datafile is for the fix
#if var == "q2":
#   datafile = "Modified_q2_ptmu_result_Feb2020.root"
#else:
#   datafile = "Modified_pzmu_ptmu_result_Feb2020.root"
##


#thefile = "CrossSection_CV_minervame5A6A6B6C6D6E6F6G_Nominal_ver33_pzmu.root"
thefile = "XS_pzmu_proj_%s.root"%("CV")


#if var in ["pzmu","pzmu_ptmu","ptmu"]:
  
if var in ["q2"]:
  thefile =  thefile.replace("pzmu","q2")
  thefile = thefile.replace(".root","_rebinned.root")
if var in ["enu","enuQE"]:
  thefile =  thefile.replace("pzmu","enu")
  
  thefile =  thefile.replace(".root","_corrected.root")
if var not in ["q2"]:
    thefile = thefile.replace("_proj_","_")
if full:
    thefile = thefile.replace("_corrected","_corrected_ver31")
datafile = thefile
print ("Datafile is ",datafile)
#
#
#
#dataname = "/Users/schellma/Dropbox/ccqe/PAPER6/lowq2syst/Modified_Pzmu.root"
#
#dataname = "/Users/schellma/Dropbox/ccqe/PAPER7/Modified_AddedLowQ2Suppression/Modified_DataXSecResults_pzptmu_December8th.root"
datadir =os.path.join(dir,"CV/CrossSection")
datadir = dir
print (datadir)
dataname = os.path.join(datadir, datafile)
print ("Datafile is ",dataname)
dataname = dataname.replace("CV_",basemodel+"_")
dataname = dataname.replace("CV/",basemodel+"/")



if not os.path.exists(dataname):
  print ("data file does not exist", dataname)
  sys.exit(0)

                              

rname = var+"_ratios.root"
if BIN:
    bin = "_bin"
else:
    bin = ""
outname = "chi2_"+var+".txt"
datafile = TFile.Open(os.path.join(dataname))

datafile.ls()

print (basehist)
#datafile.ls()
datahist = MnvH2D()

if "enu" not in var:
    datahist = datafile.Get(basehist).Clone()
else:
    datahist = MnvH1D()
    datahist = MnvH1D(datafile.Get(basehist).Clone())
    proj = ""
    
datahist.SetDirectory(0)
datahist.Scale(SCALE*norm)
dataname = "MINERvA_AntiNeutrino_CCQElike_"+var+"_Data_Meas"
if full:
    dataname = dataname.replace("Meas","MeasFull")
datahist.SetName(dataname)

xmin = 1
ymin = 1
xmax = datahist.GetXaxis().GetNbins()
ymax = datahist.GetYaxis().GetNbins()

if var == "q2" or "enu" in var:
  xmin = 0
  ymin = 0
  xmax = -1
  ymax = -1
    
dobinwidth = ("enu" not in var)
#datahist.Scale(norm)
if BIN and var != "enu":
    datahist.Scale(1.,"width")

print ("thevat",var,titles)
thetitle = titles[var]
print ("thetitle",thetitle)

datahist.SetTitle(thetitle)
# void MnvH2DToCSV(std::string name, std::string directory="", double scale=1.0, bool fullprecision=true, bool syserrors=true, bool percentage = true, bool binwidth =true);
if ("_" in var):
    datahist.MnvH2DToCSV( (datahist.GetName()),"./full",1.,True,True,True,True)
    datahist.MnvH2DToCSV( (datahist.GetName()),"./fixed",FIXEDSCALE,False,True,True,True)
if ("enu" in var):
    datahist.MnvH1DToCSV( (datahist.GetName()),"./full",1.,True,True,True,False)
    datahist.MnvH1DToCSV( (datahist.GetName()),"./fixed",FIXEDSCALE,False,True,True,False)
print ("var is ", var)
#datadraw=datahist.GetCVHistoWithError()
#datadraw.Scale(1.,"width")
rfile=TFile.Open(rname,"RECREATE")
if proj == "_px":
 
  oneDhist = datahist.ProjectionX(datahist.GetName()+"_px",ymin,ymax)
  datavals = readData1D(oneDhist)
  matrix = readMatrix1D(oneDhist.GetTotalErrorMatrix(),oneDhist)
  uncov = readMatrix(oneDhist.GetSysErrorMatrix("unfoldingCov"),oneDhist)
  #oneDhist.GetSysErrorMatrix("unfoldingCov").Print()
  #uncov.Print()
  if nounfold:
    matrix -=uncov
  matrix.Print()
  #oneDhist.SetName("data"+oneDhist.GetName())
  oneDhist.Write()
  print ("check binning")
  #dobinwidth = (var != "enu?")
  oneDhist.Print("ALL")
  test = MnvH1D()
  test = oneDhist.Clone("test")
  test.Scale(1.,"width")
  test.Print("ALL")
  print ("checked binning")
  oneDhist.MnvH1DToCSV((oneDhist.GetName()),"./full",1.,True,True,True,dobinwidth)
  oneDhist.MnvH1DToCSV((oneDhist.GetName()),"./fixed",FIXEDSCALE,False,True,True,dobinwidth)
  datadraw=oneDhist.GetCVHistoWithError()
  
  datadraw.Print("ALL")
  oneDhist.Delete()
if proj == "_py":
  nx = datahist.GetXaxis().GetNbins()
  oneDhist = datahist.ProjectionY(datahist.GetName()+"_py",xmin,xmax)
  datavals = readData1D(oneDhist)
  oneDhist.Print("ALL")
  matrix = readMatrix1D(oneDhist.GetTotalErrorMatrix(),oneDhist)
  uncov = readMatrix(oneDhist.GetSysErrorMatrix("unfoldingCov"),oneDhist)
  #uncov.Print()
  if nounfold:
    matrix -=uncov
  matrix.Print()
  #oneDhist.SetName("data"+oneDhist.GetName())
  datadraw=oneDhist.GetCVHistoWithError()
  oneDhist.Write()
  
  oneDhist.MnvH1DToCSV((oneDhist.GetName()),"./full",1.,True,True,True,dobinwidth)
  oneDhist.MnvH1DToCSV((oneDhist.GetName()),"./fixed",FIXEDSCALE,False,True,True,dobinwidth)
  oneDhist.Delete()
if proj == "":
  datavals = readData(datahist)
  matrix = readMatrix(datahist.GetTotalErrorMatrix(),datahist)
  datahist.Write()

#datavals.Print()

if Diagonal:
  for  i in range(0,matrix.GetNrows()):
    for  j in range(0,matrix.GetNrows()):
      if i == j:
        print ("error",datadraw.GetBinError(i+1),math.sqrt(matrix[i][j]))
        continue
      matrix[i][j] = 0.0
  matrix.Print()


#datavals.Print()

goodelements = {}
ok = 0
for i in range(0,len(datavals)):
  if datavals[i] != 0:
    goodelements[ok]=i
    ok += 1
#print goodelements


data = compressVector(datavals,goodelements)
logdata = TVectorD(data)
for i in range(0,len(goodelements)):
  if data[i] == 0:
    continue
  logdata[i] = math.log(data[i])



mchist = {}
mcdraw = {}
mc={}
mcstat = {}
mcerrs = {}
logmc = {}
logmcstat = {}
ofile = {}
mcfile = {}
  #
widthcorr = True
for model in models:
  
    #mcname = os.path.join(mcdir,model,"CrossSection",thefile)
    mcname = os.path.join(mcdir,thefile)
    if model != "GENIE_no2p2h":
      mcname = mcname.replace("CV_",model+"_")
      mcname = mcname.replace("CV.",model+".")
    if model == "GENIE_no2p2h":
      mcname = mcname.replace("CV_","NA_")
      mcname = mcname.replace("CV.","NA.")
    if "G18" in model:
        if model == "G18_10b_02_11a":
          thegeniefile = "xsection_XXX_50Mcombined_RHC_rebinned.root"
        else:
          thegeniefile = "xsection_XXX_50Mcombined_RHC.root"
        mcname = os.path.join(mcdir,"GENIE",thegeniefile)
        mcname = mcname.replace("XXX",model)
        print ("GENIE2", model,mcname)
    if not os.path.exists(mcname):
      print (mcname,"does not exist")
    #print "opening", mcname
    twoD = True
#    if model == "GiBUU":
#      mcname = "/Users/schellma/Dropbox/ccqe/PAPER6/MINERvAMEGiBUUMMECCQE_2D_20191114.root"
#      mcbasehist="MINERvAMEGiBUUMMECCQEnu/q2qeall"
#      if var != q2:
#        mcbasehist="MINERvAMEGiBUUMMECCQEnu/muonptVSmupz_all"
#        #/Users/schellma/Dropbox/ccqe/PAPER6/MINERvAMEGiBUUMMECCQE_2D_20191114.root
#
#    if model == "NuWroSF":
#      mcname = "/Users/schellma/Dropbox/ccqe/PAPER5/QELike_ME_Mateus_Nuwro_v1902_600M.root"
#      mcbasehist =  "nuwroSF_kQsqQE_all"
#      if var != q2:
#        mcbasehist = "nuwroSF_kMuonPtPz_all"
#
#    if model == "NuWroLFG":
#      mcname = "/Users/schellma/Dropbox/ccqe/PAPER5/QELike_ME_Mateus_Nuwro_v1902_600M.root"
#      mcbasehist =  "nuwroLFG_kQsqQE_all"
#      if var != q2:
#        mcbasehist = "nuwroLFG_kMuonPtPz_all"
#
#    if model == "Geniev3":
#      mcname = "/Users/schellma/Dropbox/ccqe/PAPER5/MMECCQEGENIEOOB_30000000Evts_20191003.root"
#      mcbasehist = "MMECCQEGENIEOOBnu/q2qeall"
#      if var != q2:
#        mcbasehist = "MMECCQEGENIEOOBnu/muonptVSmupzall"

   # if var == q2:
   #   twoD = False
    print ("Themodel",model, mcname,mcbasehist)
    try:
      mcfile[model] = TFile.Open(mcname)
    except:
      print ("mcfile does not exist ", mcfile[model])
      continue
    #print "mcfile is ",type(mcfile)
    if mcfile == None:
      print ("mcfile does not exist ", mcfile[model])
      continue
    mchist[model] = MnvH2D()
    print (" try to read in model ", model,mcbasehist)
    if "G18" not in model:  # is it the special genie?
        if "enu" not in var:
            mchist[model] = MnvH2D(mcfile[model].Get(mcbasehist).Clone())
        else:
            mchist[model] = MnvH1D()
            mchist[model] = MnvH1D(mcfile[model].Get(mcbasehist).Clone())
        
    else:
        mchist[model] = MnvH2D(mcfile[model].Get(geniehist).Clone())
    if model == "GENIE_no2p2h":
        xcv_2p2h = MnvH2D()
        if "mu" not in var:
          xcv_2p2h = mcfile[model].Get("h_enu_q2_qelike_2p2h_crossSection").Clone()
        else:
            xcv_2p2h = mcfile[model].Get("h_pzmu_ptmu_qelike_2p2h_crossSection").Clone()
        xcv_2p2h.Print()
        
        mchist["GENIE_no2p2h"].Add(xcv_2p2h,-1)
    #mchist[model].SetName(model+"_"+mchist[model].GetTitle())
    mcfilename = ("MINERvA_AntiNeutrino_CCQElike_"+var+"_MC_"+model).replace("_NA","_GENIE2.12.6").replace("_CV2","_MINERvA_v2").replace("_CV","_MINERvA_v1")
    if full:
        mcfilename=mcfilename.replace("_MC_","_MCFull_")
    mchist[model].SetName(mcfilename)
    mchist[model].SetTitle(titles[var])
    print (" read in model ", model)
    mchist[model].Scale(SCALE)
    if BIN and widthcorr and var != "enu":
      mchist[model].Scale(1.,"width")
    if debin and model in extramodels and not twoD:
      mchist[model] = Debinwidth(mchist[model])
    if debin and model in extramodels and twoD:
      print ("should I shrink it ", proj)
      mchist[model] = Debinwidth2(mchist[model])
    if "_" in var:
        dobinwidth=True
        mchist[model].MnvH2DToCSV((mchist[model].GetName()),"./full",1.,True,True,True,dobinwidth)
        mchist[model].MnvH2DToCSV((mchist[model].GetName()),"./fixed",FIXEDSCALE,False,True,True,dobinwidth)
    else:
        if "enu" in var:
            dobinwidth = False
            mchist[model].MnvH1DToCSV((mchist[model].GetName()),"./full",1.,True,True,True,dobinwidth)
            mchist[model].MnvH1DToCSV((mchist[model].GetName()),"./fixed",FIXEDSCALE,False,True,True,dobinwidth)
    mchist[model].Print()
    mchist[model].SetDirectory(0)
    
#    # remove 2p2h from the default model
#    if "no-2p2h" in model:
#        print "---- remove the 2p2h component ----",model,translate[model]
#        h2p2hcorr = MnvH2D()
#        h2p2hcorrname = "h_pzmu_ptmu_2p2hcomp_cross_section"
#        if var in ["q2","enu"]:
#          h2p2hcorrname= h2p2hcorrname.replace("pzmu",var)
#        print "TH1",h2p2hcorrname
#        h2p2hcorr = mcfile.Get(h2p2hcorrname).Clone()
#        h2p2hcorr.SetDirectory(0)
#        h2p2hcorr.Print()
#        mchist[model].Add(h2p2hcorr,-1.)
#        h2p2hcorr.Delete()
#
#
#        mchist[model].Print()
#        print model,"changed\n\n"
#
    #mcdraw[model]=mchist[model].GetCVHistoWithError()
    #mcdraw[model].Scale(1.,"width")
   
    rfile.cd()
    if proj == "_px":
      if not model in extramodels:
        ny = datahist.GetYaxis().GetNbins()
        oneDhist = mchist[model].ProjectionX(mchist[model].GetName()+"_px",ymin,ymax)
        mcdraw[model]=oneDhist.GetCVHistoWithError()
      
      else:
        oneDhist = mchist[model].Clone()
       
        mcdraw[model]=oneDhist.Clone()
      oneDhist.SetDirectory(0)
      mcdraw[model].SetDirectory(0)
#mcdraw[model].Print("ALL")
      mcvals = readData1D(oneDhist)
      mcerrs = readErrors1D(oneDhist)
      oneDhist.SetName((oneDhist.GetName()))

      
      for bin in range(0,datadraw.GetNbinsX()+1):
        mcdraw[model].SetBinError(bin,0.0)
      #dobinwidth = var != "enu?"
      oneDhist.MnvH1DToCSV(oneDhist.GetName(),"./full",1.,True,True,True,dobinwidth)
      oneDhist.MnvH1DToCSV(oneDhist.GetName(),"./fixed",FIXEDSCALE,False,True,True,dobinwidth)
  
      oneDhist.Write()
      oneDhist.Delete()
    if proj == "_py":
      print (" got to _py",model)
      if not model in extramodels:
        nx = mchist[model].GetXaxis().GetNbins()
        oneDhist = mchist[model].ProjectionY(mchist[model].GetName()+"_py",xmin,xmax)
      
        mcdraw[model]=oneDhist.GetCVHistoWithError()
        for bin in range(0,datadraw.GetNbinsX()+1):
            mcdraw[model].SetBinError(bin,0.0)
      else:
        if var == q2:
          oneDhist = mchist[model].Clone()
          mcdraw[model] = oneDhist.Clone()
        else:  #pt
          nx = mchist[model].GetXaxis().GetNbins()
          oneDhist = mchist[model].ProjectionY(mchist[model].GetName()+"_py",xmin,xmax)
          mcdraw[model] = oneDhist.Clone()
      mcdraw[model].SetDirectory(0)
      oneDhist.SetBinContent(0,0)
      oneDhist.SetDirectory(0)
      oneDhist.SetName((oneDhist.GetName()))
      mcvals = readData1D(oneDhist)
      oneDhist.Print("ALL")
      mcerrs = readErrors1D(oneDhist)
      
#print mcvals
      #oneDhist.Print("ALL")


      for bin in range(0,datadraw.GetNbinsY()+1):
        mcdraw[model].SetBinError(bin,0.0)
      #dobinwidth = var != "enu?"
      oneDhist.MnvH1DToCSV(oneDhist.GetName(),"./full",1.,True,True,True,dobinwidth)
      oneDhist.MnvH1DToCSV(oneDhist.GetName(),"./fixed",FIXEDSCALE,False,True,True,dobinwidth)
      oneDhist.Write()
      oneDhist.Delete()
    if proj == "":
      
      if not model in extramodels and "enu" not in var:
        
            mcvals = readData(mchist[model].GetCVHistoWithStatError())
            mcerrs = readErrors(mchist[model].GetCVHistoWithStatError())
      else:
        mcvals = readData(mchist[model])
        mcerrs = readErrors(mchist[model])
      mchist[model].Write()
    mc[model]=compressVector(mcvals,goodelements)
    mcstat[model]=compressVector(mcerrs,goodelements)
    logmc[model] = TVectorD(mc[model])
    logmcstat[model]=TVectorD(mc[model])
    for i in range(0,len(goodelements)):
      if mc[model][i] == 0:
        continue
      #print (mc[model][i])
      (logmc[model])[i] = math.log((mc[model])[i])
      (logmcstat[model])[i] = 1./(mc[model][i])*mcstat[model][i]
      
if "enu" in var:
    print (" can't do chi2 for enu variables as no error matrix")
    sys.exit(0)
#mchist[model].Delete()
#mc[model].Print()
    #mcfile[model].Close()
#
#type(mc["pion_rpa"])
#mc["double_rpa"]=TVectorD(mc["pion_rpa"])
#logmc["double_rpa"] = TVectorD(mc["double_rpa"])
#rpafactor = TVectorD(mc["pion_rpa"])
#for i in range(0,len(goodelements)):
#    rpafactor[i] /= mc["$\pi$tune"][i]
#    mc["double_rpa"][i]*=rpafactor[i]
#    logmc["double_rpa"][i] = math.log(mc["double_rpa"][i])
#rpafactor.Print()

#mc["pion_rpa"].Print()
#mc["double_rpa"].Print()

#models.append("double_rpa")
print (mcdraw)
maxb = len(data)
sysnames = datahist.GetSysErrorMatricesNames()

syscov = {}
print ("got here after reading input")
onames = {}
  #for model in models:
#ofile[model] = open(basemodel+var+"_"+model+".tex",'w')
oname =  "chi2-%s-%s-%f_v22.tex"%(basemodel,var,norm)
ofile["ALL"] = open(oname,'w')
out = ofile["ALL"]
top = "\\documentclass[12pt,landscape]{article}\n \\begin{document} \n"
top += "\\setlength{\\textwidth}{8.0in}\n"
top += "\\setlength{\\oddsidemargin}{-1in}\n"
begin = "\\begin{table}\n\\begin{tabular}{lrrrr}\n"
out.write(top)
out.write(begin)

InvertedErrorMatrix = {}
LogInvertedErrorMatrix = {}

sysnames=datahist.GetSysErrorMatricesNames()
#print sysnames
#cov = datahist.GetSysErrorMatrix("unfoldingCov")
#covx = datahist.ProjectionX().GetSysErrorMatrix("unfoldingCov")
#covx.Print()
sysnames.push_back("ALL")

if NOSYS:
    sysnames = ["ALL"]
    
covmx = {}
logcovmx = {}

for model in models:

    covmx[model] = compressMatrix(matrix,goodelements)
    
    fullsysmat = readMatrix(datahist.GetTotalErrorMatrix(),datahist)
    syscov[model] = compressMatrix(fullsysmat,goodelements)
    
  #
  #  if syst == "unfoldingCov":
  #    print "unfoldingCov"
  #    test = TMatrixD(fullsysmat)
  #    test.ResizeTo(10,10)
  #    test.Print()
  #
  #  if syst != "ALL" and not NOSYS:
  #    covmx -= syscov[syst]

    
      
    
    logcovmx[model] = compressMatrix(matrix,goodelements)

    for i in range(0,len(goodelements)):
      if data[i] == 0:
        continue
      for j in range(0,len(goodelements)):
        if data[j] == 0:
          continue
        logcovmx[model][i][j] = covmx[model][i][j]/data[i]/data[j]
        
    for i in range(0,len(goodelements)):
      if mc[model][i] == 0:
        continue
      covmx[model][i][i] += mcstat[model][i]*mcstat[model][i]
      logcovmx[model][i][i] += logmcstat[model][i]*logmcstat[model][i]

    InvertedError=TDecompSVD(covmx[model]);
    InvertedErrorMatrix[model]=TMatrixD(covmx[model]);
    InvertedError.Invert(InvertedErrorMatrix[model])

    LogInvertedError=TDecompSVD(logcovmx[model]);
    LogInvertedErrorMatrix[model]=TMatrixD(logcovmx[model]);
    LogInvertedError.Invert(LogInvertedErrorMatrix[model])




test = TMatrixD(LogInvertedErrorMatrix["CV"])
test.ResizeTo(5,5)
test.Print()

head = "%s &\t %s &\t %s  \\\\ \n"%("Model","$\chi^2$ - linear","$\chi^2$ - log")
print (head)

c1 = TCanvas("c1", "c1_n4"+model,0,0,900,750);
if not Ratio:
  c1.SetLogy()
c1.SetLeftMargin(0.15);
c1.SetRightMargin(0.15);
c1.SetBottomMargin(0.15);
c1.SetTopMargin(0.15);
if var in ["ptmu","q2"]:
  c1.SetLogx()

if var in ["q2","ptmu","pzmu"]:
   mcnorm = mcdraw["NA"].Clone()
   mcnorm.SetDirectory(0)
   mcdraw["CV"].Print()

   datadraw.Print()
   gStyle.SetOptStat(1)
  #data.SetOptStat(0)

   if Ratio:
    datadraw.Divide(mcnorm)
    datadraw.SetName("data_mcnorm")
   datadraw.SetDirectory(0)
   datadraw.Write()
 
ofile["ALL"].write(head)
h_chi2cont = {}
n  = covmx["CV"].GetNrows()
counter = 0
bfile = open(var+"_chi2list.py",'w')
bfile.write("chi2vals={")
for model in models:
  counter += 1
  h_chi2cont[model] = TH2D("cont"+model,"chi2 cont",n,1,n,n,1,n)
  if var in ["q2","enu","ptmu","pzmu"]:
    mcdraw[model].SetDirectory(0)
  chi2cont = TMatrixD(covmx[model])
  chi2cont.Zero()
  for syst in sysnames:
    totchi2 = 0.0
    totlogchi2 = 0.0
    dof = 0
    residual = TVectorD(data)
    logresidual = TVectorD(residual)
    for i in range(0,n):
      residual[i] = data[i]-mc[model][i]
      logresidual[i] = logdata[i] - logmc[model][i]
       
      #print ("compare",model,data[i],mc[model][i])
      #print i, data[i],mc[model][i],logdata[i],logmc[model][i]
      dof += 1
    chi2diag = TVectorD(residual)
    chi2diag.Zero()
    for i in range(minb,maxb):
      for j in range(minb,maxb):
        totchi2 += residual[i]*InvertedErrorMatrix[model][i][j]*residual[j]
        totlogchi2 += logresidual[i]*LogInvertedErrorMatrix[model][i][j]*logresidual[j]
        chi2cont[i][j] = residual[i]*InvertedErrorMatrix[model][i][j]*residual[j]
        h_chi2cont[model].Fill(i,j,chi2cont[i][j])
        if i == j:
          chi2diag[i] = chi2cont[i][j]
    
    #print "chi2", model, syst, totchi2, dof, totlogchi2
    outs =  "%s &\t %10.1f &\t %10.1f \t \\\\%%(%s)\n"%(translate[model],totchi2, totlogchi2,model)
    bfile.write('\"%s\":[%5.1f,%d],'%(model,totchi2,dof))
    print ("dump of contributions", model)
    print (outs)
    #chi2diag.Print()
    #chi2cont.Print()
    ofile["ALL"].write(outs)
    h_chi2cont[model].Write()
    print (" before pdf ", syst,var, model)
    if var != "pzmu_ptmu" and syst == "ALL":
      title = "%s ; %s %6.0f"%(model,var,totchi2)
      
      gStyle.SetTitleAlign(11)
      #datadraw.GetXaxis().SetRangeUser(0.001,10)
      mcdraw[model].Print()
      if Ratio:
        mcdraw[model].Divide(mcnorm)
      mcdraw[model].SetName("mc_"+model)
      print ("mctitle",model)
      if Ratio:
        mcdraw[model].SetMaximum(2.0)
        mcdraw[model].SetMinimum(0.0)
      else:
        mcdraw[model].SetMaximum(1.e-36)
      #mcdraw[model].Draw("PE")
      mcdraw[model].SetLineColor(counter)
      mcdraw[model].Draw("HIST same")
      datadraw.Draw("PE same")
  

      mcdraw[model].Write()
      pname =  basemodel+"%s-%s-v22.pdf" %(var,model)
    #  c1[model].SaveAs(pname,"pdf")
      print (" Try to save ",pname)
    #mchist[model].Delete()
      try:
        mcdraw[model].Delete()
      except:
        print ("failed to delete" ,model)

#ofile[model].close()
#    mchist[model].Delete()
#    mcfile.Close()

end = "\\end{tabular}\n"
out.write(end)
end = "\\caption{%s $\chi^2$  for  %d degrees of freedom }\n\\end{table}"%(varname[var],dof)
out.write(end)
out.write("\\end{document}\n")
out.close()
bfile.write("}")
bfile.close()
try:
  datadraw.Delete()
except:
  print ("failed in data delete")
  sys.exit(1)






