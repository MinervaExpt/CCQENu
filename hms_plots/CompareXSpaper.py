import ROOT
from ROOT import TH1D, TH2D, TObject, TString, TAttMarker,gStyle
import os,sys
from PlotUtils import MnvH1D,MnvH2D,MnvPlotter
from CCQEPlotUtils import *
import array as array

 
gStyle.SetEndErrorSize(10)
ROOT.TH1.AddDirectory(ROOT.kFALSE)
ratio = False
ratio = True
corrected = False
reference="NA"
sratio = ""
if ratio:
  sratio = "ratio_"
version = "v27b"
scale = 1.0
var = "q2"
if len(sys.argv)>1:
  var = sys.argv[1]
else:
  print ("arg 1 needs to be enu, q2 or pzmu")
  sys.exit(1)
 
if var == "enu":
    ratio = False
    corrected = True
    version = "ver3"
if var != "q2" and var != "pzmu" and var != "enu" and var != "ptmu":
  print ("arg 1 needs to be enu, q2 or pzmu")
  sys.exit(1)
mnv = MnvPlotter()
hvar = "pzmu_ptmu"
if var == "q2" or var == "enu":
  hvar = "enu_q2"

if var == "q2":
    from q2_chi2list import *
if var == "enu":
    from enu_chi2list import *
if var == "ptmu":
    from ptmu_chi2list import *
if var == "pzmu":
    from pzmu_chi2list import *
#MnvKellycolors
#colors = CCQEColors()
colors = {
    # ROOT.TColor.GetColor("#f2f3f4"), # white,
    0:ROOT.TColor.GetColor("#222222"),  # black,
    1:ROOT.TColor.GetColor("#f3c300"),  # yellow,
    2:ROOT.TColor.GetColor("#875692"),  # purple,
    3: ROOT.TColor.GetColor("#f38400"),  # orange,
    4:ROOT.TColor.GetColor("#a1caf1"),  # lightblue,
    5:ROOT.TColor.GetColor("#be0032"),  # red,
    6:ROOT.TColor.GetColor("#c2b280"),  # buff,
    7:ROOT.TColor.GetColor("#848482"),  # gray,
    8:ROOT.TColor.GetColor("#008856"),  # green,
    9:ROOT.TColor.GetColor("#e68fac"),  # purplishpink,
    10:ROOT.TColor.GetColor("#0067a5"),  # blue,
    11:ROOT.TColor.GetColor("#f99379"),  # yellowishpink,
    12:ROOT.TColor.GetColor("#604e97"),  # violet,
    13:ROOT.TColor.GetColor("#f6a600"),  # orangeyellow,
    14:ROOT.TColor.GetColor("#b3446c"),  # purplishred,
    15:ROOT.TColor.GetColor("#dcd300"),  # greenishyellow,
    16:ROOT.TColor.GetColor("#882d17"),  # reddishbrown,
    17:ROOT.TColor.GetColor("#8db600"),  # yellowgreen,
    18:ROOT.TColor.GetColor("#654522"),  # yellowishbrown,
    19:ROOT.TColor.GetColor("#e25822"),  # reddishorange,
    20:ROOT.TColor.GetColor("#2b3d26")   # olivegreen
}

print ("Chi2",chi2vals)
dhist= "h_%s_dataCrossSection"%hvar
mchist = "h_%s_qelike_recoCrossSection"%hvar
#file_prefix = "minervame5A6A6B6C6D6E6F6G6H6I6J_Nominal_nue_"
#fCV = ROOT.TFile.Open("XS_%_proj_CV.root"%var,"READ")
#f2p2hrpa = ROOT.TFile.Open("XS_%s_proj_2p2hrpa.root"%var,"READ")
#f2p2h = ROOT.TFile.Open("XS_%s_proj_2p2h.root"%var,"READ")


#now do the comparison of data and different MC's....

#models = ["2p2hrpa","2p2h","CV","piontune","rpapiontune","CV2","rpa"] # "CV goes last because it should be the last plotted
modelnames = {"CV":"MINERvA Tune v1","2p2h":"GENIE+Low Recoil Tune ","2p2hpiontune":"GENIE+Low Recoil Tune+#pi tune","2p2hrpa":"GENIE+Low Recoil Tune+RPA","rpa":"GENIE+RPA","CV2":"MINERvA Tune v2","2p2hrpa":"GENIE+Low Recoil Tune+RPA","piontune":"GENIE+#pi tune","rpapiontune":"GENIE+#pi tune+RPA","NA":"GENIE 2.12.6","GENIE_no2p2h":"GENIE w/o 2p2h"}
modelnames = {"CV":"MINERvA Tune v1","2p2h":"GENIE+Low Recoil Tune ","2p2hrpa":"GENIE+Low Recoil Tune+RPA","rpa":"GENIE+RPA","CV2":"MINERvA Tune v2","2p2hrpa":"GENIE+Low Recoil Tune+RPA","NA":"GENIE 2.12.6","GENIE_no2p2h":"GENIE w/o 2p2h"}
models = list(modelnames.keys())
models = ["CV", "CV2", "NA",  "rpa", "2p2h", "2p2hrpa",  \
"GENIE_no2p2h"]
print ("models",models)
#xmcdefault.SetLineColor(colors[2])
#compare_xsectionmodels_variations_ratio.py:xmc2p2hrpa.SetLineColor(colors[3])
#compare_xsectionmodels_variations_ratio.py:xmcptunerpa.SetLineColor(colors[4])
#compare_xsectionmodels_variations_ratio.py:xmcptune2p2h.SetLineColor(colors[5])
#compare_xsectionmodels_variations_ratio.py:ymcdefault.SetLineColor(colors[2])
#compare_xsectionmodels_variations_ratio.py:ymc2p2hrpa.SetLineColor(colors[3])
#compare_xsectionmodels_variations_ratio.py:ymcptunerpa.SetLineColor(colors[4])
#compare_xsectionmodels_variations_ratio.py:ymcptune2p2h.SetLineColor(colors[5])
colorcode = {"NA":0, "2p2hrpa":3, "rpapiontune":4, "2p2hpiontune":5,"2p2h":6, "CV":10, "CV2":5,"piontune":1,"rpa":9,"GENIE_no2p2h":6}

linecode = {"NA":1, "2p2hrpa":10, "rpapiontune":10, "2p2hpiontune":10,"2p2h":1, "CV":1, "CV2":1,"piontune":10,"rpa":1,"GENIE_no2p2h":10}

linewidth = {"NA":6, "2p2hrpa":4, "rpapiontune":4, "2p2hpiontune":4,"2p2h":6, "CV":6, "CV2":6,"piontune":4,"rpa":6,"GENIE_no2p2h":4}

# copied from Amit
colorcode = {"NA":colors[0], "2p2hrpa":colors[3], "rpapiontune":colors[4], "2p2hpiontune":colors[5],"2p2h":colors[6], "CV":colors[10], "CV2":colors[5],"piontune":colors[1],"rpa":colors[9],"gen2p2h":colors[6],"GENIE_no2p2h":colors[6]}
linecode = {"NA":1, "2p2hrpa":10, "rpapiontune":10, "2p2hpiontune":10,"2p2h":1, "CV":1, "CV2":1,"piontune":10,"rpa":1,"gen2p2h":1,"GENIE_no2p2h":1}
linewidth = {"NA":3, "2p2hrpa":3, "rpapiontune":3, "2p2hpiontune":3,"2p2h":3, "CV":4, "CV2":4,"piontune":3,"rpa":3,"gen2p2h":3,"GENIE_no2p2h":3}



file = {}
mc = {}

if version == "nue_v27":
  path = "/Users/schellma/Dropbox/ccqe/v27/"
if version == "nue_v14":
  path = ""
if version == "v27b":
  path = "/Users/schellma/Dropbox/ccqe/v27b/"
if version == "v27":
  path = "/Users/schellma/Dropbox/ccqe/v27/CrossSection/"
if version == "ver3":
  path = "/Users/schellma/Dropbox/ccqe/v27/ver3/"
validmodels = []
for m in models:
  if var == "q2":
    filename = "%sXS_%s_proj_%s_rebinned.root"%(path,var,m)
  if var == "enu" :
    filename = "%sXS_%s_%s.root"%(path,"enu",m)
  if var == "pzmu":
    filename = "%sXS_%s_%s.root"%(path,var,m)
  if var == "ptmu":
    filename = "%sXS_%s_%s.root"%(path,"pzmu",m)
  if not os.path.exists(filename):
    print ("Skipping this model as no input file",m,filename)
    continue
  else:
    print ("reading ",filename)
  file[m] = ROOT.TFile.Open(filename,"READ")
  mc[m] = MnvH2D()
  mc[m] = file[m].Get(mchist)
  
  validmodels.append(m)
  if m == "NA":
    #xgen2p2h = mc["NA"].Clone("genie_2p2hx")
    xcv_2p2h = MnvH2D()
    file["NA"].ls()
    xcv_2p2h = file["NA"].Get("h_enu_q2_qelike_2p2h_crossSection")
    xcv_2p2h.Print()
    mc["GENIE_no2p2h"] = mc["NA"].Clone()
    mc["GENIE_no2p2h"].Add(xcv_2p2h,-1)
    validmodels.append("GENIE_no2p2h")
  mc[m].SetName(m+"_"+mc[m].GetName())
   
  
print ("models",models,validmodels)

models=validmodels
data = MnvH2D()
data = file["CV"].Get(dhist)

print ("check data from ",file["CV"].GetName())

 

# make projections of data

xme = data.ProjectionX()
yme = data.ProjectionY()
#yme.Print("ALL")

xd = TH1D()
xd = (data.ProjectionX()).GetCVHistoWithError()
xds = (data.ProjectionX()).GetCVHistoWithStatError()

#xd.Print("ALL")
xd.Scale(1.,"width")
xds.Scale(1.,"width")
xbins = GetXbinList(xd)
yd = TH1D()
yd = (data.ProjectionY()).GetCVHistoWithError()
yds = (data.ProjectionY()).GetCVHistoWithStatError()
yd.Print("ALL")
yd.Scale(1.,"width")
yds.Scale(1.,"width")

ybins = GetXbinList(yd)

# now do the models
x = {}
y = {}
for m in models:
  x[m]=TH1D()
  y[m]=TH1D()
  x[m] = mc[m].ProjectionX().GetCVHistoWithError()
  x[m].Scale(1.0,"width")
  
  y[m] = mc[m].ProjectionY().GetCVHistoWithError()
  print(" check model ",m)
  y[m].Print("ALL")
  
  y[m].Scale(1.0,"width")
  

if var=="q2":
  y["NA"].Print("ALL")
  yd.Print("ALL")
#if ratio:
#  normx  = x["CV"].Clone()
#  normy  = y["CV"].Clone()
#  for m in models:
#
#    x[m] = x[m].Divide(x[m],normx)
#    y[m] = y[m].Divide(y[m],normy)
#
#  xd = xd.Divide(xd,normx)
#  yd = yd.Divide(yd,normy)
print (xbins)
print (ybins)

# change ybins
if "q2" in dhist:
  ybins[0] = 0.001

# transfer bins to a new histogram could rebin here but generally this lets you fix bin edges.

xoffset = 0
if var == "enu" or var == "pzmu":
  xoffset = 1
xt = NewBins(xd,xbins,xoffset)
yt = NewBins(yd,ybins)

xdn = TransferBins(xd,xt,xoffset)
ydn = TransferBins(yd,yt)
xdsn = TransferBins(xds,xt,xoffset)
ydsn = TransferBins(yds,yt)

if not ratio:
  if (var == "q2"):
    #xdn.SetMinimum(5.E-41/scale)
    #xdn.SetMaximum(2.E-38/scale)
    ydn.SetMinimum(5.E-41/scale)
    ydn.SetMaximum(10.E-37/scale)
  if (var == "enu"):
    xdn.SetMinimum(0.0/scale)
    xdn.SetMaximum(1.E-38/scale)
   # ydn.SetMinimum(1.E-41/scale)
   # ydn.SetMaximum(2.E-38/scale)
  if (var == "pzmu" or var == "ptmu"):
    xdn.SetMinimum(0.0/scale)
    xdn.SetMaximum(0.3E-38/scale)
    ydn.SetMinimum(5.E-42/scale)
    ydn.SetMaximum(20.E-37/scale)
 
else:
  xdn.SetMinimum(0.6)
  xdn.SetMaximum(2.5)
  ydn.SetMinimum(0.4)
  ydn.SetMaximum(2.0)


#xdn.Print("ALL")
#ydn.Print("ALL")

xdn.SetLineColor(ROOT.kBlack)
ydn.SetLineColor(ROOT.kBlack)
xn = {}
yn = {}
for m in models:
  xn[m] = TransferBins(x[m],xt,xoffset)
  yn[m] = TransferBins(y[m],yt)
  xn[m] = SetZeroError(xn[m])
  yn[m] = SetZeroError(yn[m])
  xn[m].Print()
  


#NOW DRAW THE X PROJECTIONS
canvas = CCQECanvas("c1","c1",750,500)
canvas.cd()

#canvas.SetLogx()
#canvas.SetLogy()
if var == "q2":
  yme.Print("ALL")
  yn["NA"].Print("ALL")

for m in models:
  xn[m].SetLineWidth(linewidth[m])
  yn[m].SetLineWidth(linewidth[m])
  xn[m].SetLineColor(colorcode[m])
  xn[m].SetLineStyle(linecode[m])
  yn[m].SetLineColor(colorcode[m])
  yn[m].SetLineStyle(linecode[m])
  
normx = xn[reference].Clone()
normy = yn[reference].Clone()

if ratio:
  if var == "q2":
    ydn.Print("ALL")
    yn["NA"].Print("ALL")
  xdn.Divide(xdn,normx)
  ydn.Divide(ydn,normy)
  xdsn.Divide(xdsn,normx)
  ydsn.Divide(ydsn,normy)
  for m in models:
    print (m,type(xn[m]),type(normx))
    xn[m].Divide(xn[m],normx)
    yn[m].Divide(yn[m],normy)
  
if (not ratio):
  if var == "q2":
    leg = CCQELegend(0.25,0.25,0.4,0.55)
  else:
    leg = CCQELegend(0.6,0.6,0.8,0.9)
  if var == "enu":
    leg = CCQELegend(0.35,0.175,0.9,0.375)
    leg.SetNColumns(2)
else:
  print ()
  leg = CCQELegend(0.20,0.6,0.9,0.9)

leg.SetHeader("MINERvA Preliminary","")
#leg.SetNColumns(2)
leg.AddEntry(xdn,"MINERvA #bar{#nu}_{#mu} data","pe")

#leg.AddEntry(xmcdefault,"GENIE 2.12.6","l")
for m in models:
  #leg.AddEntry(xn[m],"%s  #chi^{2}/dof.=%4.1f/%d"%(modelnames[m],chi2vals[m][0],chi2vals[m][1]),"l")
  leg.AddEntry(xn[m],"%s"%(modelnames[m]),"l")
#leg.AddEntry(xn["2p2h"],"GENIE+RPA","l")
#leg.AddEntry(xn["CV"],"MINERvA Tune v1","l")
#leg.AddEntry(xmcptune2p2h,"GENIE+#pi tune+2p2h","l")

xdn.GetXaxis().SetLabelSize(0.04)
xdn.GetYaxis().SetLabelSize(0.04)
ydn.GetXaxis().SetLabelSize(0.04)
ydn.GetYaxis().SetLabelSize(0.04)

xdn.GetXaxis().SetTitleSize(0.04)
xdn.GetYaxis().SetTitleSize(0.04)
ydn.GetXaxis().SetTitleSize(0.04)
ydn.GetYaxis().SetTitleSize(0.04)


xdn.GetYaxis().SetTitleOffset(1.0)
ydn.GetYaxis().SetTitleOffset(1.8)
xdn.GetXaxis().SetTitleOffset(1.4)
ydn.GetXaxis().SetTitleOffset(1.4)

if var == "q2" or var == "enu":
  xdn.GetYaxis().SetTitle("#sigma(E_{#nu}^{QE})  (cm^{2}/nucleon)");
  xdn.GetXaxis().SetTitle("E_{#nu}^{QE}  (GeV)")
  ydn.GetYaxis().SetTitle("d#sigma/dQ^{2}  (cm^{2}/GeV^{2}/nucleon)");
  ydn.GetXaxis().SetTitle("Q^{2}_{QE}  (GeV^{2})")
else:
  ydn.GetYaxis().SetTitle("d#sigma/dp_{#perp}  (cm^{2}/GeV/c/nucleon)");
  ydn.GetXaxis().SetTitle("p_{#perp}  (GeV/c)")
  xdn.GetYaxis().SetTitle("d#sigma/dp_{||}  (cm^{2}/GeV/c/nucleon)");
  xdn.GetXaxis().SetTitle("p_{||}  (GeV/c)")

if (ratio):
  if var == "q2" or var == "enu":
    xdn.GetYaxis().SetTitle("Ratio of #sigma(E_{#nu}^{QE}) to %s"%modelnames[reference])
    
    ydn.GetYaxis().SetTitle("Ratio of d#sigma/dQ^{2}_{QE} to %s"%modelnames[reference]);
   
  else:
    ydn.GetYaxis().SetTitle("Ratio of d#sigma/dp_{#perp} to %s"%modelnames[reference])
    
    xdn.GetYaxis().SetTitle("Ratio of d#sigma/dp_{||} to %s"%modelnames[reference])
    

#yd.Print("ALL")
#yds.Print("ALL")
#ydn.Print("ALL")
#ydsn.Print("ALL")

if ratio:
  xdn.SetMaximum(2.0)
  ydn.SetMaximum(2.0)
  xdn.SetMinimum(0.6)
  ydn.SetMinimum(0.6)
xdn.Draw("P E1")
xdsn.Draw("P E1 SAME")
for m in models:
  xn[m].Draw("hist ][ Same")

leg.Draw("")
#raw_input()
if var != "q2":
  canvas.Print("XS_%s_variations_%s%s_ProjectionX.png"%(var,sratio,version))
  canvas.Print("XS_%s_variations_%s%s_ProjectionX.eps"%(var,sratio,version))
  canvas.Print("XS_%s_variations_%s%s_ProjectionX.C"%(var,sratio,version))


c2 = CCQECanvas("c2","c2",750,750)
if var == "q2":
  c2.SetLogx()
  
if not ratio:
  c2.SetLogy()

#if var == "q2":
#  ydn.GetYaxis().SetTitle("d#sigma/dQ^{2} (cm^{2}/GeV^{2}/nucleon)");
#  ydn.GetXaxis().SetTitle("Q^{2}_{QE} (GeV)")
ydn.Draw("PE1")
ydsn.Draw("E1 SAME")
for m in models:
  yn[m].Draw("hist ][ Same")


leg.Draw("")
#raw_input()

if var !="enu":
  c2.Print("XS_%s_variations_%s%s_ProjectionY.png"%(var,sratio,version))
  c2.Print("XS_%s_variations_%s%s_ProjectionY.eps"%(var,sratio,version))
  c2.Print("XS_%s_variations_%s%s_ProjectionY.C"%(var,sratio,version))

if var == "enu":
  hfile = ROOT.TFile.Open("enu_ratios.root","READONLY")
  hfile.ls()
  ratioraw = (hfile.Get("ratio"))
  #ration=TransferBins(ratioraw,xt,1)
  ration  = ratioraw
  ration.Print("ALL")
  xd.Print("ALL")
  hackin = xd.Clone()
  print (type(hackin))
  hackin.Divide(hackin,ration)
  canvas.cd()
  hackin.SetLineColor(ROOT.kRed)
  hackin.SetMarkerColor(ROOT.kRed)
  hackin.Draw()
  xd.Draw("same")
  canvas.Print("vsEnu.png")
    
  

