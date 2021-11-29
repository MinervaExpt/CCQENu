import ROOT
from ROOT import TH1D, TH2D, TObject, TString, TAttMarker,gStyle
import os,sys
from PlotUtils import MnvH1D,MnvH2D,MnvPlotter
from CCQEPlotUtils import *
import array as array

 
gStyle.SetEndErrorSize(10)
ratio = True
reference="CV"
sratio = ""
if ratio:
  sratio = "ratio_"
version = "nue_v27"
scale = 1.0
var = "q2"
if len(sys.argv)>1:
  var = sys.argv[1]
else:
  print ("arg 1 needs to be enu, q2 or pzmu")
  sys.exit(1)
  
if var != "q2" and var != "pzmu" and var != "enu":
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
colors = CCQEColors()

print ("Chi2",chi2vals)
dhist= "h_%s_dataCrossSection"%hvar
mchist = "h_%s_qelike_recoCrossSection"%hvar
#file_prefix = "minervame5A6A6B6C6D6E6F6G6H6I6J_Nominal_nue_"
#fCV = ROOT.TFile.Open("XS_%_proj_CV.root"%var,"READ")
#f2p2hrpa = ROOT.TFile.Open("XS_%s_proj_2p2hrpa.root"%var,"READ")
#f2p2h = ROOT.TFile.Open("XS_%s_proj_2p2h.root"%var,"READ")


#now do the comparison of data and different MC's....

#models = ["2p2hrpa","2p2h","CV","piontune","rpapiontune","CV2","rpa"] # "CV goes last because it should be the last plotted
modelnames = {"CV":"MINERvA Tune v1","2p2h":"GENIE+2p2h","2p2hrpa":"GENIE+2p2h+RPA","rpa":"GENIE+RPA","CV2":"MINERvA Tune v2","2p2hrpa":"GENIE+2p2h+RPA","piontune":"GENIE+#pi tune","rpapiontune":"GENIE+#pi tune+RPA","NA":"GENIE default"}
models = list(modelnames.keys())
print ("models",models)
#xmcdefault.SetLineColor(colors[2])
#compare_xsectionmodels_variations_ratio.py:xmc2p2hrpa.SetLineColor(colors[3])
#compare_xsectionmodels_variations_ratio.py:xmcptunerpa.SetLineColor(colors[4])
#compare_xsectionmodels_variations_ratio.py:xmcptune2p2h.SetLineColor(colors[5])
#compare_xsectionmodels_variations_ratio.py:ymcdefault.SetLineColor(colors[2])
#compare_xsectionmodels_variations_ratio.py:ymc2p2hrpa.SetLineColor(colors[3])
#compare_xsectionmodels_variations_ratio.py:ymcptunerpa.SetLineColor(colors[4])
#compare_xsectionmodels_variations_ratio.py:ymcptune2p2h.SetLineColor(colors[5])
colorcode = {"NA":2, "2p2hrpa":3, "rpapiontune":4, "piontune2p2h":5,"2p2h":6, "CV":2, "CV2":7,"piontune":8,"rpa":9}

linecode = {"NA":10, "2p2hrpa":9, "rpapiontune":10, "2p2hpiontune":9,"2p2h":9, "CV":1, "CV2":1,"piontune":2,"rpa":10}
file = {}
mc = {}

if version == "nue_v27":
  path = "/Users/schellma/Dropbox/ccqe/v27/"
if version == "nue_v14":
  path = ""
validmodels = []
for m in models:
  if var == "q2":
    filename = "%sXS_%s_proj_%s.root"%(path,var,m)
  if var == "enu":
    filename = "%sXS_%s_%s.root"%(path,var,m)
  if var == "pzmu":
    filename = "%sXS_%s_%s.root"%(path,var,m)
  if not os.path.exists(filename):
    print ("Skipping this model as no input file",m,filename)
    continue
  else:
    print ("reading ",filename)
  file[m] = ROOT.TFile.Open(filename,"READ")
  mc[m] = MnvH2D()
  mc[m] = file[m].Get(mchist)
  validmodels.append(m)
print ("models",models,validmodels)
models=validmodels
data = MnvH2D()
data = file["CV"].Get(dhist)



# make projections of data

xme = data.ProjectionX()
yme = data.ProjectionY()

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
yd.Print()
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
  y[m].Print()
  y[m].Scale(1.0,"width")
  

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
    ydn.SetMaximum(10.E-38/scale)
  if (var == "enu"):
    xdn.SetMinimum(0.0/scale)
    xdn.SetMaximum(1.E-38/scale)
   # ydn.SetMinimum(1.E-41/scale)
   # ydn.SetMaximum(2.E-38/scale)
  if (var == "pzmu"):
    xdn.SetMinimum(0.0/scale)
    xdn.SetMaximum(0.2E-38/scale)
    ydn.SetMinimum(5.E-42/scale)
    ydn.SetMaximum(2.E-37/scale)
else:
  xdn.SetMinimum(0.5)
  xdn.SetMaximum(2.5)
  ydn.SetMinimum(0.5)
  ydn.SetMaximum(2.5)


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
  #xn[m].Print("ALL")
  


#NOW DRAW THE X PROJECTIONS
canvas = CCQECanvas("c1","c1",750,500)
canvas.cd()

#canvas.SetLogx()
#canvas.SetLogy()


for m in models:
  xn[m].SetLineWidth(5)
  yn[m].SetLineWidth(5)
  xn[m].SetLineColor(colors[colorcode[m]])
  xn[m].SetLineStyle(linecode[m])
  yn[m].SetLineColor(colors[colorcode[m]])
  yn[m].SetLineStyle(linecode[m])
  
normx = xn["CV"].Clone()
normy = yn["CV"].Clone()

if ratio:
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
else:
  print ()
leg = CCQELegend(0.25,0.6,0.9,0.9)

leg.SetHeader("MINERvA Preliminary","")
#leg.SetNColumns(2)
leg.AddEntry(xdn,"MINERvA #bar{#nu}_{#mu} data","pe")

#leg.AddEntry(xmcdefault,"GENIE 2.12.6","l")
for m in models:
  leg.AddEntry(xn[m],"%s  #chi^{2}/dof.=%4.1f/%d"%(modelnames[m],chi2vals[m][0],chi2vals[m][1]),"l")
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
  ydn.GetXaxis().SetTitle("Q^{2}_{QE}  (GeV)")
else:
  ydn.GetYaxis().SetTitle("d#sigma/dp_{#perp}  (cm^{2}/GeV/c/nucleon)");
  ydn.GetXaxis().SetTitle("p_{#perp}  (GeV/c)")
  xdn.GetYaxis().SetTitle("d#sigma/dp_{||}  (cm^{2}/GeV/c/nucleon)");
  xdn.GetXaxis().SetTitle("p_{||}  (GeV/c)")

if (ratio):
  if var == "q2" or var == "enu":
    xdn.GetYaxis().SetTitle("#sigma(E_{#nu}^{QE})/%s"%modelnames[reference])
    
    ydn.GetYaxis().SetTitle("d#sigma/dQ^{2}/%s"%modelnames[reference]);
   
  else:
    ydn.GetYaxis().SetTitle("d#sigma/dp_{#perp}/%s"%modelnames[reference])
    
    xdn.GetYaxis().SetTitle("d#sigma/dp_{||}/%s"%modelnames[reference])
    

#yd.Print("ALL")
#yds.Print("ALL")
#ydn.Print("ALL")
#ydsn.Print("ALL")

if ratio:
  xdn.SetMaximum(2.5)
  ydn.SetMaximum(2.5)
  xdn.SetMinimum(0.5)
  ydn.SetMinimum(0.5)
xdn.Draw("P E1")
xdsn.Draw("P E1 SAME")
for m in models:
  xn[m].Draw("hist Same")

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
  yn[m].Draw("hist Same")


leg.Draw("")
#raw_input()

if var !="enu":
  c2.Print("XS_%s_variations_%s%s_ProjectionY.png"%(var,sratio,version))
  c2.Print("XS_%s_variations_%s%s_ProjectionY.eps"%(var,sratio,version))
  c2.Print("XS_%s_variations_%s%s_ProjectionY.C"%(var,sratio,version))

if var == "enu":
  hfile = ROOT.TFile.Open("ratio.root","READONLY")
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
    
  

