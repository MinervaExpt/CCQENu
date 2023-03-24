import sys,os

import ROOT
import PlotUtils

# HMS 3-23-23

# program to shrink vert error bands


def sumw2killer(h): # set Sumw2(0) for all bands
  print("test")
  names = h.GetVertErrorBandNames()
  for name in names:
     N = h.GetVertErrorBand(name).GetNHists()
     for n in range(0,N):
        h.GetVertErrorBand(name).GetHist(n).Sumw2(0)
  return h
  
def checker(h):  # check the contents by writing out all error bands
  print("test")
  names = h.GetVertErrorBandNames()
  for name in names:
     N = h.GetVertErrorBand(name).GetNHists()
     for n in range(0,N):
        h.GetVertErrorBand(name).GetHist(n).Write()

  
    
# test code

filename = "/Users/schellma/Dropbox/TOPMAT/CCQENu/make_hists/CCQENu_minervame5A_MnvTunev2_QElike_TestPzPt_1.root"

f = ROOT.TFile.Open(filename,"READONLY")
g1 = ROOT.TFile.Open("test1.root","RECREATE")
g2 = ROOT.TFile.Open("test2.root","RECREATE")
f1 = ROOT.TFile.Open("band1.root","RECREATE")
f2 = ROOT.TFile.Open("band2.root","RECREATE")

h = PlotUtils.MnvH2D()
h=f.Get("h2D___QElike___qelike___pzmu_ptmu___response_tuned_migration")
#h=f.Get("h___QElike___qelike___pzmu___reconstructed")

h1 = PlotUtils.MnvH2D()
h1 = h.Clone("h1")
g1.cd()
h1.Write()
f1.cd()
checker(h1)
h1.Delete()
g1.Close()
f1.Close()

# now shrink them
h2 = PlotUtils.MnvH2D()
h2 = h.Clone("h1") # give same name so can compare
h2 = sumw2killer(h)
g2.cd()
h2.Write()
f2.cd()
checker(h2)
h2.Delete()
g2.Close()
f1.Close()



