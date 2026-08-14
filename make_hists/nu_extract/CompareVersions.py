from ROOT import TFile, TH1D, gPad, TCanvas, TText, gStyle, TLegend
import PlotUtils
import plotting_pdf
import commentjson

aconfig = commentjson.load(open("AntiNuUnTuned_p6.json"))

variables = aconfig["Variables"]
scales = aconfig["Scales"]
versions = ["p8","p7","p6","p4"]

mnvplotter = PlotUtils.MnvPlotter()

files = {}
colors = [1,2,4,6,8,9,12,14,16,18,20]
for ver in versions:

    files[ver] = TFile.Open(f"AntiNuUnTuned_{ver}.root")
    if ver == versions[0]:
        print ("opened file", files[ver].GetName())
        #files[ver].ls()

summaries ={}
icolor = 1

hists = {}
local = {}
for types in ["data","qelike","qelikenot","mc"]:
    summaries[types] = TH1D(f"summary_{types}", f"summary_{types}", 6, 3., 9.)
    t = TText(.3, .95, f"{types} ratio")
    t.SetNDC(1)
    t.SetTextSize(.03)
    
    hists[types] = {}
    local[types] = {}
    for var in variables:
        hists[types][var]={} 
        local[types][var]={}
        i = 1
        legend = TLegend(0.6, 0.7, 0.9, 0.9)
        legend.SetFillStyle(0)
        legend.SetBorderSize(0)
        canvas = TCanvas(var, var, 800, 600)

        for ver in versions:
            
            i+=1
            #histname = f"h___merged___{types}___{var}___reconstructed_reconstructed_unfolded_effcorr_sigma"
            histname = f"h___merged___{types}___{var}___reconstructed"

            if types != "mc":
                hists[types][var][ver] = files[ver].Get(histname)
                
            else:
                
                hists[types][var][ver] = hists["qelike"][var][ver].Clone(histname)
                hists[types][var][ver].Print()
                hists["qelike"][var][ver].Print()
                hists["qelikenot"][var][ver].Print()
                hists["mc"][var][ver].Add(hists["qelikenot"][var][ver])
                hists[types][var][ver].Print()

            print ("whereami", types,var,ver,hists[types][var][ver])
            
            if ver == versions[0]:
                norm = hists[types][var][ver].Clone("norm_"+var)
            i = int(ver[1])    
            hists[types][var][ver].SetLineColor(colors[i-4])
            hists[types][var][ver].SetLineWidth(4)
        
            if var == "ptmu":
                tot = hists[types][var][ver].Integral()
                i = int(ver[1]) - 2
                summaries[types].SetBinContent(i, tot)
                print ("types, ver, var", types, ver, var, i,  tot)
            local[types][var][ver] = hists[types][var][ver].Clone(histname+"_tmp")
            local[types][var][ver].Divide(hists[types][var][ver],norm,1,1,"B")
            print ("local",types,var,ver,local[types][var][ver].GetName())
            local[types][var][ver].Print()
            local[types][var][ver].SetMinimum(0.97)
            local[types][var][ver].SetMaximum(1.03)
            legend.AddEntry(local[types][var][ver], f"{ver}/{versions[0]}", "l")
            local[types][var][ver].GetXaxis().SetTitle(var)
            local[types][var][ver].GetYaxis().SetTitle(f"Ratio to {versions[0]}")
            gPad.SetLogx(scales[var]%2)

            if ver == versions[0]:
                local[types][var][ver].Draw("")
            else:
                local[types][var][ver].Draw("PE same")
            
        t.Draw()
        legend.Draw()    
        print (f"{types}_{var}.png")
        canvas.Print(f"{types}_{var}.png")

sumcanvas = TCanvas("summary","summary")

sumleg = TLegend(0.6, 0.7, 0.9, 0.9)
sumleg.SetBorderSize(0)
sumleg.SetFillStyle(0)

for types in ["data","mc","qelike","qelikenot"]:
    t = TText(.3, .95, f"{types} - versions")
    t.SetNDC(1)
    t.SetTextSize(.03)
    sumleg = TLegend(0.6, 0.7, 0.9, 0.9)
    sumleg.SetFillStyle(0)
    summaries[types].SetMarkerColor(1)
    summaries[types].SetLineColor(1)
    summaries[types].SetMarkerStyle(22)
    summaries[types].SetMarkerSize(2)
    sumleg.AddEntry(summaries[types],types,"pe")
    summaries[types].Print("ALL")
    summaries[types].SetMinimum(summaries[types].GetMaximum()*.97)
    summaries[types].SetMaximum(summaries[types].GetMaximum()*1.02)

    if types == "data":
        summaries[types].Draw("PE")
    else:
        summaries[types].Draw("PE")
        
    summaries[types].GetYaxis().SetTitle("total number of events")
    summaries[types].GetXaxis().SetTitle("code version")
    sumleg.Draw()
    t.Draw()
    sumcanvas.Print(f"{types}_summary.png")

