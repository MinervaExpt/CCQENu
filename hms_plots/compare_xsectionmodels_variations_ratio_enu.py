import ROOT
import os,sys
from PlotUtils import MnvH1D,MnvH2D,MnvPlotter

DRAWRATIO=False


mnv = MnvPlotter()
#ROOT.gROOT.SetBatch(ROOT.kTRUE)
def SetTotalError(hist):
    err_hist = hist.GetTotalError(True)
    xbins = hist.GetNbinsX()
    ybins = hist.GetNbinsY()
    for i in range(0,xbins+1):
        for j in range(0,ybins+1):
            hist.SetBinError(i,j,err_hist.GetBinContent(i,j))

#MnvKellycolors
colors = {
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

colorcode = {"NA":colors[0], "2p2hrpa":colors[3], "rpapiontune":colors[4], "2p2hpiontune":colors[5],"2p2h":colors[6], "CV":colors[5], "CV2":colors[10],"piontune":colors[1],"rpa":colors[9],"gen2p2h":colors[17]}
linecode = {"NA":1, "2p2hrpa":10, "rpapiontune":10, "2p2hpiontune":10,"2p2h":1, "CV":1, "CV2":1,"piontune":10,"rpa":1,"gen2p2h":1}
linewidth = {"NA":2, "2p2hrpa":2, "rpapiontune":2, "2p2hpiontune":2,"2p2h":2, "CV":3, "CV2":3,"piontune":2,"rpa":2,"gen2p2h":2}


dhist= "True_Xsection_data_tot"
mchist = "True_Xsection_mc_tot"
#file_prefix = "XS_q2_proj"#"XS_q2_proj"
file_prefix = "XS_enu"
suffix = "_corrected"
if "q2_proj" in file_prefix:
    suffix = "_rebinned"
path = "/pnfs/minerva/persistent/users/bashyal8/postNSFMigration/Nominal_nue_ver27/ver3/"

fmnv = ROOT.TFile(path+file_prefix+"_CV"+suffix+".root","READ")
fmnv2 = ROOT.TFile(path+file_prefix+"_CV2"+suffix+".root","READ")
fdefault =ROOT.TFile(path+file_prefix+"_NA"+suffix+".root","READ")
f2p2hrpa = ROOT.TFile(path+file_prefix+"_2p2hrpa"+suffix+".root","READ")
fptunerpa = ROOT.TFile(path+file_prefix+"_rpapiontune"+suffix+".root","READ")
fptune2p2h = ROOT.TFile(path+file_prefix+"_2p2hpiontune"+suffix+".root","READ")
frpa = ROOT.TFile(path+file_prefix+"_rpa"+suffix+".root","READ")
f2p2h = ROOT.TFile(path+file_prefix+"_2p2h"+suffix+".root","READ")
fptune = ROOT.TFile(path+file_prefix+"_piontune"+suffix+".root","READ")
ftot = ROOT.TFile(path+"XS_enu_CV_corrected_ver31.root","READ")
ftotmnv2 = ROOT.TFile(path+"XS_enu_CV2_corrected_ver31.root","READ")
#fgibu = ROOT.TFile("Rebinned_output_trial1.root","READ")
#now do the comparison of data and different MC's....



_xmcmnv = fmnv.Get(mchist)
_xmcmnv2 = fmnv2.Get(mchist)
_xd = fmnv.Get(dhist)
_xdS = fmnv.Get("True_Xsection_data_stat")
_xmcdefault = fdefault.Get(mchist)
_xmc2p2hrpa = f2p2hrpa.Get(mchist)
_xmcptunerpa = fptunerpa.Get(mchist)
_xmcptune2p2h = fptune2p2h.Get(mchist)
_xmc2p2h = f2p2h.Get(mchist)
_xmcrpa = frpa.Get(mchist)
_xmcptune = fptune.Get(mchist)
_xmctot = ftot.Get("Fid_Xsection_mc_tot")
_xmcmnv2tot = ftotmnv2.Get("Fid_Xsection_mc_tot")
_xdtot = ftot.Get("Fid_Xsection_data_tot")
_xdStat = ftot.Get("Fid_Xsection_data_stat")
#mcgibu = fgaibu.Get("enuq2_all")

_xcv_2p2h = fdefault.Get("True_Xsection_2p2h_tot")


_xd.Scale(1.0E39)
_xdS.Scale(1.0E39)
_xdtot.Scale(1.0e39)
_xdStat.Scale(1.0e39)
_xmctot.Scale(1.0e39)
_xmcmnv2tot.Scale(1.0e39)
_xmcmnv.Scale(1.0e39)
_xmcmnv2.Scale(1.0e39)
_xmcdefault.Scale(1.0e39)
_xmc2p2hrpa.Scale(1.0e39)
_xmcptunerpa.Scale(1.0e39)
_xmcptune2p2h.Scale(1.0e39)
_xmc2p2h.Scale(1.0e39)
_xmcptune.Scale(1.0e39)
#_xmcgibu.Scale(1.0e39,"width")
_xmcrpa.Scale(1.0e39)
_xcv_2p2h.Scale(1.0e39)

xcv_2p2h = _xcv_2p2h.Clone()

xdStat = _xdStat.Clone()

xd = _xd.Clone()
xdS = _xdS.Clone()
xdtot = _xdtot.Clone()
xdStat = _xdStat.Clone()
xmcmnv = _xmcmnv.Clone()
xmcmnv2 = _xmcmnv2.Clone()
xmcdefault = _xmcdefault.Clone()
xmc2p2hrpa = _xmc2p2hrpa.Clone()
xmcptunerpa = _xmcptunerpa.Clone()
xmcptune2p2h = _xmcptune2p2h.Clone()
xmc2p2h = _xmcptune2p2h.Clone()
xmcptune = _xmcptune2p2h.Clone()
#xmcgibu = _xmcgibu.Clone()
xmcrpa = _xmcrpa.Clone()

xmctot = _xmctot.Clone()
xmcmnv2tot = _xmcmnv2tot.Clone()
#lets subtract the 2p2h from the default GENIE

_xgen2p2h = _xmcdefault.Clone("genie_2p2hx")

xgen2p2h = _xgen2p2h.Clone()

_xmcdefault.Add(xcv_2p2h,-1)


print( "------------------")
_xmcmnv.Print("ALL")
_xmcdefault.Print("ALL")
print( "-----------------------")

if DRAWRATIO:
    xdS.Divide(_xdS,_xmcdefaultStat)
    xd.Divide(_xd,_xmcdefault)
    xdtot.Divide(_xdtot,_xmcdefault)
    xdStat.Divide(_xdStat,_xmcdefault)
    xgen2p2h.Divide(_xgen2p2h,_xmcdefault)
    xmcmnv2tot.Divide(_xmcmnv2tot,_xmcdefault)
    xmctot.Divide(_xmctot,_xmcdefault)
    xmcmnv.Divide(_xmcmnv,_xmcdefault)
    xmcmnv2.Divide(_xmcmnv2,_xmcdefault)
    xmcdefault.Divide(_xmcdefault,_xmcdefault)
    xmc2p2hrpa.Divide(_xmc2p2hrpa,_xmcdefault)
    xmcptunerpa.Divide(_xmcptunerpa,_xmcdefault)
    xmcptune2p2h.Divide(_xmcptune2p2h,_xmcdefault)
    xmc2p2h.Divide(_xmc2p2h,_xmcdefault)
    xmcptune.Divide(_xmcptune,_xmcdefault)
    #xmcgibu.Divide(_xmcgibu,_xmcdefault)
    xmcrpa.Divide(_xmcrpa,_xmcdefault)




"""
for i in range(0,ymcgibu.GetNbinsX()+1):
    _val = 0
    if _ymcdefault.GetBinContent(i)!=0:
        _val = _ymcgibu.GetBinContent(i)/_ymcdefault.GetBinContent(i)
    ymcgibu.SetBinContent(i,_val)

for i in range(0,xmcgibu.GetNbinsX()+1):
    _val = 0
    if _xmcdefault.GetBinContent(i)!=0:
        _val = _xmcgibu.GetBinContent(i)/_xmcdefault.GetBinContent(i)
    xmcgibu.SetBinContent(i,_val)
"""
#FIX THE LABELS ETC...
xd.GetYaxis().SetLabelSize(0.05);
xd.GetYaxis().SetTitleSize(0.05);
xd.GetYaxis().SetTitleOffset(1.2);

xd.GetXaxis().SetLabelSize(0.05);
xd.GetXaxis().SetTitleSize(0.06);
xd.GetXaxis().SetTitleOffset(1.1);


xmcmnv.SetLineColor(colorcode["CV"])
xmcmnv.SetLineWidth(linewidth["CV"])
xmcmnv.SetLineStyle(linecode["CV"])

xmcmnv2.SetLineColor(colorcode["CV2"])
xmcmnv2.SetLineWidth(linewidth["CV2"])
xmcmnv2.SetLineStyle(linecode["CV2"])

xmcdefault.SetLineColor(colorcode["NA"])
xmcdefault.SetLineWidth(linewidth["NA"])
xmcdefault.SetLineStyle(linecode["NA"])

xmc2p2hrpa.SetLineColor(colorcode["2p2hrpa"])
xmc2p2hrpa.SetLineWidth(linewidth["2p2hrpa"])
xmc2p2hrpa.SetLineStyle(linecode["2p2hrpa"])

xmcptunerpa.SetLineColor(colorcode["rpapiontune"])
xmcptunerpa.SetLineWidth(linewidth["rpapiontune"])
xmcptunerpa.SetLineStyle(linecode["rpapiontune"])

xmcptune2p2h.SetLineColor(colorcode["2p2hpiontune"])
xmcptune2p2h.SetLineWidth(linewidth["2p2hpiontune"])
xmcptune2p2h.SetLineStyle(linecode["2p2hpiontune"])


xmc2p2h.SetLineColor(colorcode["2p2h"])
xmc2p2h.SetLineWidth(linewidth["2p2h"])
xmc2p2h.SetLineStyle(linecode["2p2h"])

xmcptune.SetLineColor(colorcode["piontune"])
xmcptune.SetLineWidth(linewidth["piontune"])
xmcptune.SetLineStyle(linecode["piontune"])

xmcrpa.SetLineColor(colorcode["rpa"])
xmcrpa.SetLineWidth(linewidth["rpa"])
xmcrpa.SetLineStyle(linecode["rpa"])

xgen2p2h.SetLineColor(colorcode["gen2p2h"])
xgen2p2h.SetLineWidth(linewidth["gen2p2h"])
xgen2p2h.SetLineStyle(linecode["gen2p2h"])
"""
#NOW DRAW THE X PROJECTIONS
xmcmnv.SetLineColor(2)
xmcmnv.SetLineWidth(3)
xmcmnv2.SetLineColor(2)
xmcmnv2.SetLineWidth(3)
xmcmnv2.SetLineStyle(2)
xmcdefault.SetLineColor(colors[2])
xmc2p2hrpa.SetLineColor(colors[3])
xmcptunerpa.SetLineColor(colors[4])
xmcptune2p2h.SetLineColor(colors[5])
xmc2p2h.SetLineColor(colors[6])
xmcptune.SetLineColor(colors[7])
xmcrpa.SetLineColor(colors[8])
xgen2p2h.SetLineColor(colors[9])
#xmcgibu.SetLineColor(colors[9])
"""
xdStat.SetMarkerStyle(27)
xdStat.SetLineColor(ROOT.kBlack)
xdStat.SetLineWidth(2)






xproj_titley = ""
yproj_titley = ""
if DRAWRATIO:
    xproj_titley = "Ratio to GENIE 2.12.6"
else:
    xproj_titley = "#sigma(E_{#nu})^{QE}(#times 10^{-39}cm^{2}/nucleon)"
xproj_titlex = "E_{#nu} (GeV)"


xd.GetYaxis().SetTitle(xproj_titley)
xd.GetXaxis().SetTitle(xproj_titlex)
canvas = ROOT.TCanvas("c","c",750,750)
canvas.cd()




if DRAWRATIO:
    xd.SetMaximum(2.0)
    xd.SetMinimum(0.0)
else:
    xd.SetMaximum(16.0)
    xd.SetMinimum(0.0)
xd.Draw("PE")
xdS.Draw("E1 SAME")
if not DRAWRATIO:
    _xmctot.SetLineColor(ROOT.kGreen+3)
    _xmctot.SetLineWidth(3)
    #_xmctot.SetLineStyle(5)
    _xmcmnv2tot.SetLineColor(ROOT.kGreen+3)
    _xmcmnv2tot.SetLineStyle(2)
    _xmcmnv2tot.SetLineWidth(3)
    _xdtot.SetMarkerColor(ROOT.kGreen+3)
    _xdStat.SetMarkerColor(ROOT.kGreen+3)
    _xdStat.SetLineColor(ROOT.kGreen+3)
    _xdtot.SetLineColor(ROOT.kGreen+3)
    _xdStat.SetLineStyle(27)
    _xdtot.Draw("PE SAME")
    _xdStat.Draw("E1 SAME")
    _xmctot.Draw("hist Same")
    _xmcmnv2tot.Draw("hist Same")

xmcmnv.Print("ALL")
print(_xmctot.Integral(),_xmcmnv.Integral())
print ("******************")

xmcmnv2.Print("ALL")
xmcmnv.Draw("hist Same")
xmcmnv2.Draw("hist Same")
xmcdefault.Draw("hist Same")
xgen2p2h.Draw("hist Same")
xmc2p2h.Draw("hist Same")
xmcptune.Draw("hist Same")
xmcrpa.Draw("hist Same")
xmc2p2hrpa.Draw("hist Same")
xmcptunerpa.Draw("hist Same")
xmcptune2p2h.Draw("hist Same")
xmcmnv.Print("hist Same")
xmcmnv2.Draw("hist Same")

#ymcgibu.Print("ALL")
leg = ROOT.TLegend(0.1621622,0.1527778,0.4621622,0.3027778)
leg.SetFillStyle(0)
leg.SetBorderSize(0)
leg.SetTextSize(0.03)
leg.AddEntry(xd,"Data","lpe")
leg.AddEntry(xmcmnv,"MINERvA Tune v1","l")
leg.AddEntry(xmcmnv2,"MINERvA Tune v2","l")
leg.AddEntry(xmcdefault,"GENIE w/o 2p2h","l")
leg.AddEntry(xgen2p2h,"GENIE 2.12.6","l")
leg.AddEntry(xmcptune,"GENIE+#pi tune","l")
leg.AddEntry(xmcrpa,"GENIE+RPA","l")
leg.AddEntry(xmcptunerpa,"GENIE+#pi tune+RPA","l")
leg.AddEntry(xmc2p2h,"GENIE+Low Recoil Tune","l")
leg.AddEntry(xmc2p2hrpa,"GENIE+Low Recoil Tune+RPA","l")
leg.AddEntry(xmcptune2p2h,"GENIE+#pi tune+Low Recoil Tune","l")

if not DRAWRATIO:
    leg.AddEntry(_xmctot,"MINERvA Tune v1 (Full Fiducial)","l")
    leg.AddEntry(_xmcmnv2tot,"MINERva Tune v2 (Full Fiducial)","l")
    leg.AddEntry(_xdtot,"Data (Full Fiducial)","lpe")
    
#leg.AddEntry(xmcgibu,"GENIE+GIBUU","l")

leg.Draw("")
if DRAWRATIO:
    canvas.Print("xsectionmodels_variations_ProjectionX_ratio.png")
    canvas.Print("xsectionmodels_variations_ProjectionX_ratio.eps")
    canvas.Print("xsectionmodels_variations_ProjectionX_ratio.C")
else:
    canvas.Print("xsectionmodels_variations_ProjectionX.png")
    canvas.Print("xsectionmodels_variations_ProjectionX.eps")
    canvas.Print("xsectionmodels_variations_ProjectionX.C")    
#sys.exit()
  


