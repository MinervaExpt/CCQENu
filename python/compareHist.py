import os, sys
from ROOT import TFile, TH1D, TH2D, TText, TGraph, TLatex, gPad, TLegend
from ROOT import TCanvas, gStyle, gROOT, TPad
import numpy as np
from ROOT import gStyle
from ROOT import SetOwnership

from PlotUtils import MnvH1D

# this runs faster and prints more if true

DEBUG = False

# for now the input file names are hardwired in at the bottom but once that is done, it loops over histograms and plots a page for each. It ignores the ones with filter in their names'''

filter = ["response","types","resolution"]
filter = ["response","types"]
# these variables get log X scale
logX = ["Q2QE","ptmu","Enu","EnuCCQE"]
widthcorr = ["___","bkgsub","mc_tot","bkgsub_unfolded_effcorr_sigma","sigmaMC"]

def stringdiff(s1,s2):
    l1 = os.path.basename(s1).split("_")
    l2 = os.path.basename(s2).split("_")
    diff1 = ""
    diff2 = ""
    for i in range(0,len(l1)):
        print (l1[i],l2[i])
        if l1[i] != l2[i]:
            diff1 +="%s"%(l1[i]) 
            diff2 +="%s"%(l2[i]) 
    return (diff1,diff2)

def CCQELegend(xlow,ylow,xhigh,yhigh):
    ''' make a legend'''
    leg = TLegend(xlow,ylow,xhigh,yhigh)
    SetOwnership( leg, 1 )
    leg.SetFillStyle(0)
    leg.SetBorderSize(0)
    leg.SetTextSize(0.03)
    return leg

def CCQECanvas(name,title,xsize=750,ysize=750):
    ''' make a canvas '''
    c2 = TCanvas(name,title,xsize,ysize)
    c2.SetLeftMargin(0.20)
    c2.SetRightMargin(0.05)
    c2.SetBottomMargin(0.15)
    return c2

def text(canvas,h1):
    ''' not used right now'''
    if not h1.GetTitle(): 
        return
    if "" not in h1.GetTitle():
        h1.GetXaxis().SetTitle(h1.GetTitle())
        h1.GetYaxis().SetTitle("counts/bin")

def loop(outname,canvas,fname,gname,fkey,gkey):
    ''' open the files and loop over histograms - calls compare'''
    count = 0
    f = TFile.Open(fname,"READONLY")
    g = TFile.Open(gname,"READONLY")

    # fkey = os.path.basename(fname)[0:2]
    # gkey = os.path.basename(gname)[0:2]

    try:
        fpot = TH1D()
        fpot = f.Get("POT_summary")
        pot1 = fpot.GetBinContent(1)

        g = TFile.Open(gname,"READONLY")
        gpot = TH2D()
        gpot = g.Get("POT_summary")
        pot2 = gpot.GetBinContent(1)
        if pot2 > 0: 
            scaleData = pot1/pot2
            scaleMC = fpot.GetBinContent(3)/gpot.GetBinContent(3)
        print ("POT",pot1,pot2,scaleData,scaleMC)
    except:
        # if no POT, assume it is already normalized
        scaleData=1.0
        scaleMC=1.0
        print("POT rescaling discabled")
    
    for k in f.GetListOfKeys():
         
        key = k.GetName()
        key2 = key.replace("__QElike__","__Multiplicity1__")
        key2 = key2.replace("__qelikenot__","__qelikenot_np__")
        key2 = key2.replace("__qelike__","__qelike_np__")
        canvas = CCQECanvas(key,key)
        h1 = MnvH1D()
        h2 = MnvH1D()
        h1 = f.Get(key)
        h2 = g.Get(key2)
        if not h1:
            print("could not find",h1)
            continue
        
        if not h1.InheritsFrom("TH1D"):
            continue
        
        if h1.InheritsFrom("TH2D"):
            continue
        if h1.GetEntries() == 0: 
            continue
        if not h2:
            print("could not find",key2)
            continue
        
        # look for things that need width correctin
        for test in widthcorr:
            #if "sigma" in key and "Enu" not in key:
            #    break
            print ("test",test,key)
            if test in key:
                print ("width correction",key,test)
                                  
                h1.Scale(1., "width")
                h2.Scale(1., "width")
                               
                break
        # POT scale the original histograms
        if "___" in key2:
            if "data" in key2:
                h2.Scale(scaleData)
            else:
                h2.Scale(scaleMC)
        #h1.Print()
        #h2.Print()
        #print ("check",key)
        print ("look at",h1.GetName())
        compare(outname,canvas,h1,h2,fkey,gkey)

        
        #newPage(outname,canvas)
        count+=1
        if DEBUG and count>10: 
            break
        

def compare(outname,canvas, h1, h2, tag1, tag2):
    ''' compares 2 histograms, tag1 and tag2 are tags to use in the legend'''
    print ("compare", h1.GetName(),h2.GetName())
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
    resmax = 0.0
    for i in range(1,nbins+1):
        x[i-1]= h1.GetXaxis().GetBinCenter(i)
        if res[i-1] > resmax:
            resmax = res[i-1]
        if -res[i-1] > resmax:
            resmax = -res[i-1]

        #res[i-1] = h1.GetBinContent(i)
    
    #if chi2 < 0.2: 
    #    return
    leg = CCQELegend(0.65,0.40,1,0.60)
    leg.SetTextSize(0.06)
    #leg = TLegend(0.1,0.,0.48,0.9)
    for log in logX:
        if log in h1.GetName() and "resolution" not in h1.GetName():
            gPad.SetLogx()
    h1.GetXaxis().SetLabelSize(0.06)
    h1.GetYaxis().SetLabelSize(0.06)
    h1.GetXaxis().SetTitleSize(0.06)
    h1.GetYaxis().SetTitleSize(0.06)
    h1.GetYaxis().SetTitle("events/unit")
    h1.GetXaxis().CenterTitle(True)
    h1.GetYaxis().CenterTitle(True)
    h1.SetMarkerColor(4)
    h1.SetMarkerStyle(20)
    max = h1.GetMaximum()
    max2 = h2.GetMaximum()
    if max2 > max: 
        max = max2
    h1.SetMinimum(0.0)
    h2.SetMaximum(max*1.2)
    h1.Draw("PE")
    h2.SetMarkerColor(2)
    h2.SetMarkerStyle(21)
    h2.GetXaxis().SetLabelSize(0.1)
    h2.GetYaxis().SetLabelSize(0.1)
    h2.GetXaxis().SetTitleSize(0.1)
    h2.GetYaxis().SetTitleSize(0.1)
    h2.Draw("PE same")
    if DEBUG: print ("keys",tag1,tag2)
    leg.SetHeader("Version")
    leg.AddEntry(h1,tag1,"lp")
    leg.AddEntry(h2,tag2,"lp")
    #leg.Print("ALL")
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
    # leftover code from doing residuals
    resgr = TGraph(nbins,x,res)
    SetOwnership( resgr, 1 )
    resgr.GetYaxis().SetTitle("Normalized Residuals")
    resgr.GetXaxis().SetTitle(h1.GetTitle())
    resgr.SetMarkerStyle(21)
    resgr.SetMarkerColor(1)
    resgr.SetMarkerSize(.9)
    #resgr.SetTitle("Normalized Residuals")
    # if DEBUG:
    #     resgr.Print("ALL")
    #resgr.Draw("PE")
    #h1.Draw("")
    # you have to make something to plot the residuals onto
    frame = MnvH1D()
    frame = h1.Clone("ratio")
    frame.GetYaxis().SetTitle("%s/%s - 1 , residuals"%(tag1,tag2))
    frame.Divide(frame,h2,1.,1.,"B")
    # shift by 1
    for bin in range (1,nbins+1):
        if frame.GetBinContent(bin) != 0.0:
            frame.SetBinContent(bin,frame.GetBinContent(bin)-1.0)
    for log in logX:
        if log in h1.GetName() and "resolution" not in h1.GetName():
            gPad.SetLogx()
    min = (frame.GetMinimum() )
    max = frame.GetMaximum() 
    if -min > max: max = -min
    if resmax > max: max = resmax
    print ("max = ",min, max,resmax)
    max *=1.2
    frame.SetMaximum(max)
    frame.SetMinimum(-max)
    frame.GetXaxis().CenterTitle(True)
    frame.GetYaxis().CenterTitle(True)
    frame.Draw()
    gPad.SetGridy()
    resgr.Draw("same")
    canvas.cd()  
    pad5 =  TPad("all","all",0,.5,1,1)
    pad5.SetFillStyle(4000)  # transparent
    pad5.Draw()
    pad5.cd()
    lat = TLatex()

    
    label = h1.GetName().replace("___",", ")
    label2 = "#bf{#it{KSprob = %6.4f}}"%(kol)
   
    lat.DrawLatexNDC(.1,.95,label)
    lat.DrawLatexNDC(.6,.8,label2)

    canvas.cd(0)
    canvas.Update()

    # print out the page
    canvas.Print("pix/"+tag1+"_"+tag2+"."+h1.GetName()+".png")
    canvas.Print(outname+"_1D.pdf","pdf")

    if DEBUG:
        print ("residuals",res)
    
    
    

def startPDF(filename,canvas1D):
    ''' start a pdf '''
    pdfstart1D = filename + "_1D.pdf("
    
    canvas1D.Print(pdfstart1D, "pdf")
    print ("start pdf",filename)

def newPage(filename,canvas1D):
    canvas1D.Print(filename + "_1D.pdf","pdf")

def endPDF(filename,canvas1D):
    ''' end a pdf'''
    pdfend1D = filename + "_1D.pdf)"
    canvas1D.Print(pdfend1D, "pdf")


# start of main

gStyle.SetOptTitle(0)
gStyle.SetOptStat(0)



# fname = "/Users/schellma/Dropbox/CCQE/p6_test/P6_minervame6A_MnvTunev2_QElike_p6_run_1.root"

# gname = "/Users/schellma/Dropbox/CCQE/p6_test/P4_minervame6A_MnvTunev2_QElike_p4_run_1.root"

# fname = "/Users/schellma/Dropbox/newForge/CCQENu/make_hists/P6_inclusive_minervame5A_MnvTunev1_Inclusive_p6_inclusive_1_untuned_analyze9.root"

# gname = "/Users/schellma/Dropbox/newForge/CCQENu/make_hists/P6_inclusive_minervame5A_MnvTunev2_Inclusive_p6_inclusive_1_untuned_analyze9.root"

# fname = "/Users/schellma/Dropbox/newForge/CCQENu/make_hists/P6_inclusive_minervame5A_MnvTunev1_Inclusive_p6_inclusive_1_untuned_analyze9.root"

# gname = "/Users/schellma/Dropbox/newForge/CCQENu/make_hists/P4_inclusive_minervame5A_MnvTunev1_Inclusive_p4_inclusive_1_untuned_analyze9.root"

fname="/Users/schellma/Dropbox/newForge/CCQENu/make_hists/P6_minervame5A_MnvTunev2_QElike_p6_qelike_1.root"

gname="/Users/schellma/Dropbox/newForge/CCQENu/make_hists/P6_minervame5A_MnvTunev2_Multiplicity1_p6_mult1_1.root"

tag1,tag2 = stringdiff(fname,gname)
print (fname)
print (gname)
print (tag1,tag2)


if not os.path.exists(fname):
    print (fname," was not found")
    exit(1)

if not os.path.exists(gname):
    print (gname," was not found")
    exit(1)

# f = TFile.Open(fname,"READONLY")

# fpot = TH1D()
# fpot = f.Get("POT_summary")
# pot1 = fpot.GetBinContent(1)

# g = TFile.Open(gname,"READONLY")
# gpot = TH2D()
# gpot = g.Get("POT_summary")


# pot2 = gpot.GetBinContent(1)
# if pot1 > 0: 
#     scale = pot2/pot1
# print ("POT",pot1,pot2,scale)


# h1 = MnvH1D()
# h1name = "h___QElike___qelike___recoil___selected_truth" 
# h1 = f.Get(h1name)
# h1.Scale(1,"width")
# h2 = MnvH1D()
# h2name = "h___QElike___qelike___recoil___selected_truth"

# h2 = g.Get(h2name)
# h2.Scale(scale,"width")
# if DEBUG:
#     h1.Print()
#     h2.Print()
# c1 = CCQECanvas("c1","c1")
outname=tag1+"_"+tag2+"."+os.path.basename(fname.replace(".root",""))
print ("outname is ",outname)
# startPDF(outname,c1)
# compare(outname,c1,h1,h2,"a","b")
# endPDF(outname,c1)
# c1.Print("pix/test.png")
# f.Close()
# g.Close()
c2 = CCQECanvas("c2","c2")
startPDF(outname,c2)
loop(outname,c2,fname,gname,tag1,tag2)
endPDF(outname,c2)
