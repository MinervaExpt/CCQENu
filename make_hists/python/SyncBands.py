import ROOT
import PlotUtils

def SyncBands(thehist):
  print (thehist.GetName())
  theCVHisto = ROOT.TH1D(thehist);
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

