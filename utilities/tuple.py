import os, sys, time, ROOT
from ROOT import TH1D,TH2D,TFile,TTree,TCanvas, gROOT, gStyle

# simple program to read in two trees and compare 1 variable.

# ========== initialization ==================
dFile = TFile("data_tuple.root", "READ")
dTree = dFile.Get("CCQE")
mFile = TFile("mc_tuple.root", "READ")
mTree = mFile.Get("CCQE")



# see what is in the tree
dTree.Print()

# make histograms.
dHist = TH1D("Data Enu","E_{#nu} in GeV",40,0.,20.)
mHist = TH1D("MC Enu","E_{#nu} in GeV",40,0.,20.)

#=============== Loop over the data ================
nEntries = dTree.GetEntries()
for i in range(0, nEntries):
  dTree.GetEntry(i)
  dHist.Fill(dTree.EnuQE,dTree.wgt)
dHist.Print()
  
#================ Loop over the simulation =============
nEntries = mTree.GetEntries()
for i in range(0, nEntries):
  mTree.GetEntry(i)
  mHist.Fill(mTree.EnuQE,mTree.wgt)
mHist.Print()

#===============Normalize to each other for now =============
norm = dHist.Integral()/mHist.Integral()

mHist.Scale(norm)

# set up the graphics
c1 = TCanvas("c", "c", 600, 600)
gROOT.Reset()
gStyle.SetScreenFactor(1)
gStyle.SetOptFit(111111)

# draw them together
dHist.Draw("PE")
mHist.Draw("same hist")

# write histograms out to a file

hFile = TFile.Open("histout.root","RECREATE")
dHist.Write()
mHist.Write()
hFile.Close()

# sleep 30 seconds with plot up?
c1.SaveAs("EnuQE.png")

c1.Update()
ROOT.gROOT.SaveContext()


## wait for input to keep the GUI (which lives on a ROOT event dispatcher) alive
if __name__ == '__main__':
   rep = ''
   while not rep in [ 'q', 'Q' ]:
      rep = input( 'enter "q" to quit: ' )
      if 1 < len(rep):
         rep = rep[0]

