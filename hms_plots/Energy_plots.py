from ROOT import *
from PlotUtils import *

from PlotUtils import MnvH1D,MnvH2D,MnvPlotter
from CCQEPlotUtils import *
import array as array
gStyle.SetEndErrorSize(10)

import sys,os,string

if len(sys.argv)< 2:
    print ("arg is the input filen name")
    sys.exit(0)
    
fname = sys.argv[1]

if not os.path.exists(fname):
    print ("no file named", name)
    sys.exit(0)
    
f = TFile.Open(fname,'READONLY')

types = ["QElikeALLAngles", "QElikeNP" ,"QElike" ]
colors =  {"QElike":ROOT.kBlack ,"QElikeNP":ROOT.kRed ,"QElikeALLAngles":ROOT.kBlue }
names =  {"QElike":"no p > 120 MeV" ,"QElikeNP":"all p" ,"QElikeALLAngles":"all angles" }
palecolors =  {"QElike":ROOT.kGray ,"QElikeNP":ROOT.kRed-10 ,"QElikeALLAngles":ROOT.kBlue-10 }

template = "h_XXX_Enu_bkgsub_unfolded_effcorr_sigma"
templateMC = "h_XXX_Enu_sigmaMC"

canvas = CCQECanvas("c1","c1",750,500)
canvas.cd()
f.ls()
h_syst = {}
h_stat = {}
h_mc = {}
h_data = {}
first = True
leg = CCQELegend(0.5,0.2,0.9,0.4)
for type in types:
    
    data = template.replace("XXX",type)
    mc = templateMC.replace("XXX",type)
    print ("tags",data,mc)
    h_data[type] = MnvH1D()
    h_data[type] = f.Get(data)
    h_stat[type] = h_data[type].GetCVHistoWithStatError()
    h_syst[type] = h_data[type].GetCVHistoWithError()
    h_stat[type].Scale(1.0,"width")
    h_syst[type].Scale(1.0,"width")
    leg.AddEntry(h_stat[type],names[type],"pe")
    h_mc[type] = MnvH1D()
    h_mc[type] = MnvH1D(f.Get(mc))
    h_mc[type].Scale(1.0,"width")
    color = colors[type]
    palecolor = palecolors[type]
    h_stat[type].SetLineColor(color)
    h_stat[type].SetMarkerColor(color)
    h_stat[type].SetMarkerStyle(1)
    h_syst[type].SetLineColor(color)
    h_syst[type].SetMarkerColor(color)
    h_syst[type].SetMarkerStyle(20)
    h_syst[type].SetMarkerSize(1)
    h_mc[type].SetLineColor(color)
    #h_mc[type].SetLineStyle(2)
    h_stat[type].Print()
    h_stat[type].SetFillColor(palecolor)
    if first:
        h_syst[type].Draw("PE")
        h_syst[type].SetMinimum(0.)
        h_syst[type].SetMaximum(1.E-38)
    else:
        h_syst[type].Draw("same PE")
    first = False
    h_mc[type].Draw("hist same")
    h_stat[type].SetMarkerColor(color)
    h_stat[type].SetMarkerStyle(20)
    h_stat[type].Draw("PE2 same")
    h_stat[type].Draw("PE same")
leg.Draw()
canvas.Print("cross_section_vs_energy.png")
