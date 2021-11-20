import ROOT
from ROOT import TH1D, TH2D
import os,sys
from PlotUtils import MnvH1D,MnvH2D,MnvPlotter
import array as array

 

def GetXbinList(h):
  local = h.GetXaxis().GetXbins().GetArray()
  result = []
  for i in range(0,h.GetNbinsX()+1):
    result.append(local[i])
  return result
    
def NewBins(h,bins,offset=0):
  if offset == 1:
    bins = [0]+bins
  hn = ROOT.TH1D(h.GetName()+"_newbins",h.GetTitle(),len(bins)-1,array.array('d',bins))
  return hn
  
def TransferBins(hin, htemplate, offset = 0):
  if hin.GetNbinsX() + offset != htemplate.GetNbinsX() :
    print ("can't TransferBins from %s to %s, numbers don't match"%(hin.GetName(),htemplate().GetName()))
  hout = htemplate.Clone(hin.GetName()+"_newbins")
  hout.SetTitle(hin.GetTitle())
  for i in range(0,offset+1):
    hout.SetBinContent(i,0.0)
    hout.SetBinContent(i,0.0)
    hout.SetBinError(i,0.0)
    hout.SetBinError(i,0.0)
  for i in range(1,hin.GetNbinsX()+1+offset):
    hout.SetBinContent(i+offset,hin.GetBinContent(i))
    hout.SetBinContent(i+offset,hin.GetBinContent(i))
    hout.SetBinError(i+offset,hin.GetBinError(i))
    hout.SetBinError(i+offset,hin.GetBinError(i))
  #hout.SetMinimum(0.)
  return hout
  
def SetTotalError(hist):
    err_hist = hist.GetCVHistoWithError()
    return err_hist
    
def SetZeroError(hist):
    for i in range(0,hist.GetNbinsX()+2):
      hist.SetBinError(i,0)
    return hist

def integrator( h, binwid):
  inte = 0;
  for i in range(1, h.GetXaxis().GetNbins()+1):
    val = h.GetBinContent(i);
    wid = 1
    if binwid:
      wid = h.GetBinWidth(i)
    inte+=val*wid;
  
  return inte

#MnvKellycolors
def CCQEColors():
  return {
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
  
def CCQECanvas(name,title,xsize=750,ysize=750):
  c2 = ROOT.TCanvas(name,title,xsize,ysize)
  c2.SetLeftMargin(0.20);
  c2.SetRightMargin(0.05);
  c2.SetBottomMargin(0.15);
  return c2

def CCQELegend(xlow,ylow,xhigh,yhigh):
  leg = ROOT.TLegend(xlow,ylow,xhigh,yhigh)
  leg.SetFillStyle(0)
  leg.SetBorderSize(0)
  leg.SetTextSize(0.03)
  return leg
