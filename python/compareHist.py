import os
from ROOT import TFile, TH1D, TH2D, TText, TGraph, TLatex, gPad, TLegend
from ROOT import TCanvas, gStyle, gROOT, TPad
import numpy as np
from ROOT import gStyle
from ROOT import SetOwnership

from PlotUtils import MnvH1D
DEBUG = True

filter = ["response","types","resolution"]

def CCQELegend(xlow,ylow,xhigh,yhigh):
  leg = TLegend(xlow,ylow,xhigh,yhigh)
  SetOwnership( leg, 1 )
  leg.SetFillStyle(0)
  leg.SetBorderSize(0)
  leg.SetTextSize(0.03)
  return leg

def CCQECanvas(name,title,xsize=750,ysize=750):
    c2 = TCanvas(name,title,xsize,ysize)
    c2.SetLeftMargin(0.20)
    c2.SetRightMargin(0.05)
    c2.SetBottomMargin(0.15)
    return c2

def text(canvas,h1):
    if not h1.GetTitle(): 
        return
    if "" not in h1.GetTitle():
        h1.GetXaxis().SetTitle(h1.GetTitle())
        h1.GetYaxis().SetTitle("counts/bin")

def loop(outname,canvas,fname,gname):
    count = 0
    f = TFile.Open(fname,"READONLY")
    fkey = os.path.basename(fname)[0:2]
    gkey = os.path.basename(gname)[0:2]
    fpot = TH1D()
    fpot = f.Get("POT_summary")
    pot1 = fpot.GetBinContent(1)

    g = TFile.Open(gname,"READONLY")
    gpot = TH2D()
    gpot = g.Get("POT_summary")
    pot2 = gpot.GetBinContent(1)
    if pot1 > 0: 
        scaleData = pot1/pot2
        scaleMC = fpot.GetBinContent(3)/gpot.GetBinContent(3)
    print ("POT",pot1,pot2,scaleData,scaleMC)
    
    for k in f.GetListOfKeys():
        
        key = k.GetName()
        badkey = False
        for fil in filter:
            if fil in key:
                badkey = True
        if badkey: continue
        canvas = CCQECanvas(key,key)
        h1 = MnvH1D()
        h2 = MnvH1D()
        h1 = f.Get(key)
        h2 = g.Get(key)
        
        if not h1.InheritsFrom("TH1D"):
            continue
        if not h1:
            print("could not find",h1)
            continue
        if h1.InheritsFrom("TH2D"):
            continue
        if not h2:
            print("could not find",h2)
            continue
        if h1.GetEntries() == 0: 
            continue
        if "data" in h1.GetName():
            h2.Scale(scaleData, "width")
            h1.Scale(1., "width")
        else:
            h2.Scale(scaleMC, "width")
            h1.Scale(1., "width")
        #h1.Print()
        #h2.Print()
        #print ("check",key)

        compare(outname,canvas,h1,h2,fkey,gkey)

        
        #newPage(outname,canvas)
        count+=1
        if DEBUG and count>10: 
            break
        

def compare(outname,canvas, h1, h2, key1, key2):
    canvas.Divide(1,2,0.01,0.01)
    canvas.cd()
    #pad1 =  TPad("COMP","COMP",0,.5,1,1)
    #pad1.cd()
    #text(canvas,h1)
    #canvas.SetLogy()
    canvas.cd(1)
    gPad.SetTopMargin(0.1)
    gPad.SetBottomMargin(0.2)
    gPad.SetLeftMargin(0.2)
    nbins = h1.GetXaxis().GetNbins()
    res = np.zeros(nbins+1)
    x = np.zeros(nbins+1)
    kol = h1.KolmogorovTest(h2,"N")
    chi2 = h1.Chi2Test(h2,"WW P CHI2",res)
    for i in range(1,nbins+1):
        x[i-1]= h1.GetXaxis().GetBinCenter(i)
        #res[i-1] = h1.GetBinContent(i)
    
    #if chi2 < 0.2: 
    #    return
    leg = CCQELegend(0.65,0.40,1,0.60)
    leg.SetTextSize(0.06)
    #leg = TLegend(0.1,0.,0.48,0.9)
    h1.GetXaxis().SetLabelSize(0.06)
    h1.GetYaxis().SetLabelSize(0.06)
    h1.GetXaxis().SetTitleSize(0.06)
    h1.GetYaxis().SetTitleSize(0.06)
    h1.GetYaxis().SetTitle("events/unit")
    h1.GetXaxis().CenterTitle(True)
    h1.GetYaxis().CenterTitle(True)
    h1.SetMarkerColor(4)
    h1.SetMarkerStyle(20)
    h1.Draw("PE")
    h2.SetMarkerColor(2)
    h2.SetMarkerStyle(21)
    h2.GetXaxis().SetLabelSize(0.1)
    h2.GetYaxis().SetLabelSize(0.1)
    h2.GetXaxis().SetTitleSize(0.1)
    h2.GetYaxis().SetTitleSize(0.1)
    h2.Draw("PE same")
    print ("keys",key1,key2)
    leg.SetHeader("Version")
    leg.AddEntry(h1,key1,"lp")
    leg.AddEntry(h2,key2,"lp")
    leg.Print("ALL")
    leg.Draw()
    #canvas.Modified()
    #canvas.Update()
    if DEBUG:
        print ("x",x)
        print ("res",res)
    #pad1.cd()
    #pad1.Draw()
    canvas.Update()
    #pad2 =  TPad("pad2","pad2",0,.3,1,.4)
    #pad2.cd()
    canvas.cd(2)
    gPad.SetTopMargin(0.1)
    gPad.SetBottomMargin(0.2)
    gPad.SetLeftMargin(0.2)
    #gPad.SetPad(0,0,1,.4)
    resgr = TGraph(nbins,x,res)
    SetOwnership( resgr, 1 )
    resgr.GetYaxis().SetTitle("Normalized Residuals")
    resgr.GetXaxis().SetTitle(h1.GetTitle())
    resgr.SetMarkerStyle(21)
    resgr.SetMarkerColor(1)
    resgr.SetMarkerSize(.9)
    #resgr.SetTitle("Normalized Residuals")
    if DEBUG:
        resgr.Print("ALL")
    #resgr.Draw("PE")
    #h1.Draw("")
    frame = MnvH1D()
    frame = h1.Clone("ratio")
    frame.GetYaxis().SetTitle("%s/%s"%(key1,key2))
    frame.Divide(frame,h2,1.,1.,"B")
    frame.SetMaximum(1.05)
    frame.SetMinimum(0.95)
    frame.GetXaxis().CenterTitle(True)
    frame.GetYaxis().CenterTitle(True)
    frame.Draw()
    #resgr.GetXaxis().SetRangeUser(4,16)
    #resgr.GetYaxis().SetRangeUser(-3.5,3.5)
    gPad.SetGridy()
    resgr.Draw("same")
    #Pad.Update()
    #pad2.Draw()
    #resgr.Print()
    #canvas.Modified()
    #canvas.Update()
    canvas.cd()  
    pad5 =  TPad("all","all",0,.5,1,1)
    pad5.SetFillStyle(4000)  # transparent
    pad5.Draw()
    pad5.cd()
    lat = TLatex()
    #lat.DrawLatexNDC(.4,.95,"My Title")
    
    label = h1.GetName().replace("___",", ")
    label2 = "#bf{#it{KSprob = %6.4f}}"%(kol)
   
    lat.DrawLatexNDC(.1,.95,label)
    lat.DrawLatexNDC(.6,.8,label2)

    # t =  TText(.3, .95, h1.GetName()+" \\Chi^2=%6.2f"%chi2)
    # t.SetNDC(1)
    # t.SetTextSize(.03)
    # t.Draw()
    canvas.cd(0)
    canvas.Update()

    canvas.Print("pix/"+h1.GetName()+".png")
    canvas.Print(outname+"_1D.pdf","pdf")

    if DEBUG:
        print ("residuals",res)
    #canvas.Draw()
    #canvas.Update()
    
    

def startPDF(filename,canvas1D):
    ''' start a pdf '''
    pdfstart1D = filename + "_1D.pdf("
    
    canvas1D.Print(pdfstart1D, "pdf")

def newPage(filename,canvas1D):
    canvas1D.Print(filename + "_1D.pdf","pdf")

def endPDF(filename,canvas1D):
    pdfend1D = filename + "_1D.pdf)"
    canvas1D.Print(pdfend1D, "pdf")

    
gStyle.SetOptTitle(0)
gStyle.SetOptStat(0)

fname = "/Users/schellma/Dropbox/CCQE/p6_test/P6_minervame6A_MnvTunev2_QElike_p6_run_1.root"
f = TFile.Open(fname,"READONLY")
gname = "/Users/schellma/Dropbox/CCQE/p6_test/P4_minervame6A_MnvTunev2_QElike_p4_run_1.root"


fpot = TH1D()
fpot = f.Get("POT_summary")
pot1 = fpot.GetBinContent(1)

g = TFile.Open(gname,"READONLY")
gpot = TH2D()
gpot = g.Get("POT_summary")
pot2 = gpot.GetBinContent(1)
if pot1 > 0: 
    scale = pot2/pot1
print ("POT",pot1,pot2,scale)

h1 = MnvH1D()
h1name = "h___QElike___qelike___recoil___selected_truth" 
h1 = f.Get(h1name)
h1.Scale(1,"width")
h2 = MnvH1D()
h2name = "h___QElike___qelike___recoil___selected_truth"

h2 = g.Get(h2name)
h2.Scale(scale,"width")
if DEBUG:
    h1.Print()
    h2.Print()
c1 = CCQECanvas("c1","c1")
outname=os.path.basename(fname.replace(".root",""))
startPDF(outname,c1)
compare(outname,c1,h1,h2,"a","b")
endPDF(outname,c1)
c1.Print("pix/test.png")
f.Close()
g.Close()
c2 = CCQECanvas("c2","c2")
startPDF("a_"+outname,c2)
loop("a_"+outname,c2,fname,gname)
endPDF("a_"+outname,c2)
