from ROOT import TFile, TH1D, gPad, TCanvas, TText, gStyle, TLegend
import PlotUtils
import plotting_pdf
import commentjson

aconfig = commentjson.load(open("AntiNuUnTuned_p6.json"))

variables = aconfig["Variables"]
scales = aconfig["Scales"]
versions = ["p8","p7","p6"]

mnvplotter = PlotUtils.MnvPlotter()

files = {}
colors = [2,4,6,8,9,12,14,16]
for ver in versions:

    files[ver] = TFile.Open(f"AntiNuUnTuned_{ver}.root")
    if ver == versions[0]:
        print ("opened file", files[ver].GetName())
        files[ver].ls()

for types in ["data","qelike","qelikenot"]:

    for var in variables:
        hists = {}
        i = 1
        legend = TLegend(0.6, 0.7, 0.9, 0.9)
        legend.SetFillStyle(0)
        canvas = TCanvas(var, var, 800, 600)

        for ver in versions:
            i+=1
            #histname = f"h___merged___{types}___{var}___reconstructed_reconstructed_unfolded_effcorr_sigma"
            histname = f"h___merged___{types}___{var}___reconstructed"

            hists[ver] = files[ver].Get(histname)
            if ver == versions[0]:
                norm = hists[ver].Clone("norm_"+var)
            #hists[ver].Scale(1.0, "width")
            hists[ver].SetLineColor(colors[i])
            hists[ver].SetLineWidth(4)
            hists[ver].Divide(hists[ver],norm,1,1,"B")
            hists[ver].SetMinimum(0.97)
            hists[ver].SetMaximum(1.03)
            legend.AddEntry(hists[ver], f"{ver}/{versions[0]}", "l")
            hists[ver].GetXaxis().SetTitle(var)
            hists[ver].GetYaxis().SetTitle(f"Ratio to {versions[0]}")
            #gPad.SetLogy(scales[var] > 1)
            gPad.SetLogx(scales[var]%2)
            if ver == versions[0]:
                hists[ver].Draw("")
            else:
                hists[ver].Draw("PE same")
        legend.Draw()    
        canvas.Print(f"{types}_{var}.png")
        