from ROOT import TFile, TCanvas,TH1D
import os,sys
from PlotUtils import MnvH1D,MnvPlotter,MnvVertErrorBand
import PlotUtils

def SyncBands(thehist):
  print (thehist.GetName())
  theCVHisto = TH1D(thehist);
  theCVHisto.SetDirectory(0);
  bandnames = thehist.GetErrorBandNames();
 
  for bandname in bandnames:
  
    band = MnvVertErrorBand()
    band = thehist.GetVertErrorBand(bandname)
   
    for i in range(0,band.GetNbinsX()+2):
      if(i < 4 and i != 0):
        print ("Sync band ", thehist.GetName(), bandname, i, theCVHisto.GetBinContent(i), theCVHisto.GetBinContent(i)-band.GetBinContent(i))
      band.SetBinContent(i,theCVHisto.GetBinContent(i))
      band.SetBinError(i,theCVHisto.GetBinError(i))


f = TFile.Open("../BDT_3.root")

h = {}
categories = ["data",
              "qelike","1chargedpion",
                "1neutralpion",
             "multipion",
            "other"]
mnvPlotter = MnvPlotter()
cF = TCanvas()

h_pot = TH1D()
h_pot = f.Get("POT_summary")
h_pot.Print("ALL")

dataPOT = h_pot.GetBinContent(1)
mcPOTprescaled = h_pot.GetBinContent(3)
POTScale = dataPOT / mcPOTprescaled

print(" POT MC " , mcPOTprescaled )
print(" POT DATA " , dataPOT )



components = ["qelike","1chargedpion","1neutralpion","multipion","other"]
for category in categories:
    
    name = "h___1track___"+category+"___bdtgQELike___reconstructed"
    print (name)
    
    h[category] = MnvH1D()
    temp = f.Get(name)
    if not temp: continue
    h[category] = temp.Clone()
    if h[category].GetNbinsX() == 40:
        h[category].Rebin(4)
    if h[category]:
        if category != "data":
           h[category].Scale(POTScale)
        mnvPlotter.DrawErrorSummary(h[category])
        cF.Print(name+".png")
        #h[category].MnvH1DToCSV(name+".csv",".",1.0, False, True, False)

newname = "h___1track___total___bdtgQELike___reconstructed"
h["total"] = h["qelike"].Clone(newname)


for x in components:
    
    print ("add x",x)
    
    h[x].Print("ALL")
    if x == "qelike": continue
    print (type(h["total"]),type(h[x]))
    h["total"].Add(h[x])

SyncBands(h["total"])


mnvPlotter.DrawDataMCWithErrorBand(h["data"], h["total"], 1., "TR")
cF.Print("data"+".png")
h["total"].Print()
#h["total"].MnvH1DToCSV(newname,".",1.0, False, True, False)
mnvPlotter.DrawErrorSummary(h["total"])
cF.Print(newname+".png")
mnvPlotter.DrawDataMCRatio(h["data"],h["total"], 1. )

cF.Print("ratio.png")


