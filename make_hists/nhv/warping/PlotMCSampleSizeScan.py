import os,sys
import ROOT
import PlotUtils

ROOT.TH1.AddDirectory(False)

def sortInputFiles(filelist):
    newlist = []
    factors = []
    for f in filelist:
        fn = f.rstrip("\n")
        mcfactor = float(fn.split(".txt")[-2].split("_")[-1])
        factors.append(mcfactor)

    factors = sorted(factors)
    for f in factors:
        for fi in filelist:
            mcfactor = float(fi.split(".txt")[-2].split("_")[-1])
            if(f==mcfactor): newlist.append(fi)

    return newlist

colors = [1,20,30,40,50,60,70,80,90,100,51,1,20,30,40,50,60,70,80,90,100,51]#22 allowed inputs
styles = [1,1,1,1,1,1,1,1,1,1,1,2,2,2,2,2,2,2,2,2,2,2]#22 allowed inputs


var = sys.argv[1]
nbins = float(sys.argv[2])
uncfactor = sys.argv[3]

inputfiles = sys.argv[4:]
newlist = sortInputFiles(inputfiles)
# for el in newlist:
# print(el.rstrip("\n"))
legend = ROOT.TLegend(0.2,0.7,0.82,0.9)
legend.SetFillStyle(0)
legend.SetNColumns(3)
mnvPlotter = PlotUtils.MnvPlotter()
canvas = ROOT.TCanvas()

chi2_iter1_f1 = 0  # I will use this number to set y_max in the plot

chi2_by_iter_by_file = []
for f in newlist:
    fn = f.rstrip("\n")
    temp_file = open(fn,"r").readlines()
    n_uni = 0
    current_iter = 0
    chi2_by_iter = []
    for l in temp_file:
        temp_line = l.split()
        chi2 = float(temp_line[0])
        iteration = int(temp_line[1])
        universe = int(temp_line[2])
        if(universe>n_uni):
            n_uni=universe+1
        if(iteration!=current_iter):
            if(current_iter!=0):
                chi2_by_iter[-1][1]/=n_uni
            chi2_by_iter.append([iteration,chi2])
            current_iter=iteration
        else:
            chi2_by_iter[-1][1]+=chi2
        if l == temp_file[-1]:
            chi2_by_iter[-1][1]/=n_uni
    #            chi2_by_iter.append([iteration,chi2])

    # print(chi2_by_iter)
    chi2_by_iter_by_file.append(chi2_by_iter)
    if f == newlist[0]: chi2_iter1_f1 = chi2_by_iter[0][1]

print("len(chi2_by_iter_by_file) ",len(chi2_by_iter_by_file))

mygraphs = []
for i in range(0,len(chi2_by_iter_by_file)):
    # print(i)
    tmpgraph = ROOT.TGraph()
    for j,el in enumerate(chi2_by_iter_by_file[i]):
        tmpgraph.SetPoint(j,el[0],el[1])

    tmpgraph.SetLineColor(colors[i])
    tmpgraph.SetLineStyle(styles[i])
    tmpgraph.SetMarkerColor(colors[i])

    mygraphs.append(tmpgraph)

for i,g in enumerate(mygraphs):
    legend.AddEntry(g,"%s"%(float(newlist[i].split(".txt")[-2].split("_")[-1])),"l")
    if(i==0):
        g.Draw("ALP")
        g.GetXaxis().SetTitle("(Unfolded Data:True Data) #bf{# of Iterations}")
        g.GetYaxis().SetTitle("Average #chi^{2}" + "(ndf=" + str(nbins) + ")")
        g.GetXaxis().SetTitleOffset(1.15)
        g.GetXaxis().SetTitleSize(0.06)
        g.GetXaxis().SetTitleFont(62)
        g.GetXaxis().SetLabelFont(42)
        g.GetXaxis().SetLabelSize(0.05)
        g.GetYaxis().SetTitleOffset(1.2)
        g.GetYaxis().SetTitleSize(0.06)
        g.GetYaxis().SetTitleFont(62)
        g.GetYaxis().SetLabelFont(42)
        g.GetYaxis().SetLabelSize(0.05)
        g.GetYaxis().SetNdivisions(509)
        g.SetMinimum(0)
        g.GetXaxis().CenterTitle()
        # g.GetXaxis().SetLimits(2.0, 30.0)
        # g.GetYaxis().SetRangeUser(0.5, 15.0)
        g.GetXaxis().SetLimits(0.0, 11.0)
        g.GetYaxis().SetRangeUser(nbins * 0.6, 1.2 * chi2_iter1_f1)
        # g.GetYaxis().SetRangeUser(0.7 * float(sys.argv[2]), 1.2 * chi2_iter1_f1)
        # g.GetYaxis().SetRangeUser(0.7 * float(sys.argv[2]), float(sys.argv[4]))
        # g.GetYaxis().SetRangeUser(3.0, float(sys.argv[4]))
        g.SetLineWidth(3)

        t = ROOT.TLatex(
            0.5,
            1 - ROOT.gStyle.GetPadTopMargin() + 0.04,
            var + ", uncfactor = " + uncfactor,
        )
        t.SetNDC()
        # t.SetTextSize(0.06)
        t.SetTextSize(0.05)
        t.SetTextColor(1)
        t.SetTextFont(62)
        t.SetTextAlign(22)
        t.SetTextAngle(0)
        t.Draw()
    else:
        g.Draw("SAMELP")
mygraphs[4].Draw("SAMELP")
l = ROOT.TLine(
    0.0,
    nbins,
    11.0,
    nbins,
)
l.SetLineStyle(7)
l.SetLineWidth(3)
l.SetLineColor(36)
l.Draw()

legend.Draw("SAME")
canvas.Print("Extra_UncFactor_"+var+"_"+uncfactor+".png")
# raw_input("DONE")
