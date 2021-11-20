from ROOT import *
from PlotUtils import *

from PlotUtils import MnvH1D,MnvH2D,MnvPlotter
from CCQEPlotUtils import *
import array as array
gStyle.SetEndErrorSize(10)

import sys,os,string


  
if len(sys.argv)<2:
    print ("args are q2,enu,pzmu,ptmu")
    sys.exit(0)
var = sys.argv[1]

if not os.path.exists(var+"_ratios.root"):
    print(" no ratios file available, run the chi2 code to make it")
    sys.exit(0)
else:
    fname = var+"_ratios.root"
f = TFile.Open(fname,'READONLY')

models = [ "2p2h", "2p2hrpa", "CV2", "piontune", "rpapiontune", \
"2p2hpiontune", "NA", "rpa","CV"]

colorcode = {"NA":2, "2p2hrpa":3, "rpapiontune":4, "2p2hpiontune":5,"2p2h":6, "CV":2, "CV2":7,"piontune":8,"rpa":9}

linecode = {"NA":6, "2p2hrpa":10, "rpapiontune":6, "2p2hpiontune":10,"2p2h":10, "CV":1, "CV2":1,"piontune":6,"rpa":6}

modelnames = {"CV":"MINERvA Tune v1","2p2h":"GENIE+2p2h","2p2hrpa":"GENIE+2p2h+RPA","rpa":"GENIE+RPA","CV2":"MINERvA Tune v2","2p2hrpa":"GENIE+2p2h+RPA","piontune":"GENIE+#pi tune","2p2hpiontune":"GENIE+2p2h+#pi tune","rpapiontune":"GENIE+#pi tune+RPA","NA":"GENIE default"}

mnv = MnvPlotter()
colors = CCQEColors()
dhist = MnvH1D()
dhist = f.Get("data_mcnorm")
canvas = CCQECanvas("c1","c1",750,500)
canvas.cd()
xtitle = dhist.GetXaxis().GetTitle()
print (xtitle)
if (var == "q2"):
    xbins =  GetXbinList(dhist)
    xbins[0] = 0.001
    newq2bins = NewBins(dhist,xbins)
    dhist = TransferBins(dhist,newq2bins)
    canvas.SetLogx()
dhist.GetXaxis().SetLabelSize(0.04)
dhist.GetYaxis().SetLabelSize(0.04)
dhist.GetYaxis().SetTitle("ratio to MINERvA Tune v1")
dhist.GetXaxis().SetTitle(xtitle)

dhist.SetMaximum(2)
dhist.SetMinimum(0.5)
dhist.Draw("PE")
ratios = {}
leg = CCQELegend(0.25,0.7,0.9,0.9)
leg.SetHeader("MINERvA Preliminary","")
leg.SetNColumns(2)
leg.AddEntry(dhist,"MINERvA #bar{#nu}_{#mu} data","pe")

for m in models:
  ratios[m] = MnvH1D()
  ratios[m] = MnvH1D(f.Get("mc_"+m))
  ratios[m].SetLineWidth(3)
  ratios[m].SetLineColor(colors[colorcode[m]])
  ratios[m].SetLineStyle(linecode[m])
  ratios[m].Draw("SAME HIST")
  leg.AddEntry(ratios[m],modelnames[m],"l")
  
dhist.Draw("PE same")
leg.Draw("")
canvas.Print(var+"_ratios.png")




