# from ROOT import TH1D, TH2D,TLorentzVector, TVector3, TFile
import ROOT
import math
import numpy as np
from os import path, mkdir
# Script to boost a lorentz vector

# In GeV
m_Lambda = 1.115683 
m_SigmaMinus = 1.197449
m_proton = 0.93827203
m_pi = .13957061
m_neutron = 0.9395654133


n_theta_bins = 1001
# n_thyp_bins = 100

proton_threshold = .120
pion_threshold = 0.050

def me2CM(input):
    # input.Print()
    beta = input.Beta()
    gamma = input.Gamma()
    print ("beta","gamma",beta,gamma)
    newvector = input.Clone()
    boostVector = ROOT.TVector3(0,0,-beta) 
    newvector.Boost(boostVector)
    newvector.Print()
    return newvector, boostVector

def decayme(input, m1, m2, cost):
    mass = input.M()
    E1 = (mass*mass + m1*m1 - m2*m2)/(2*mass)
    E2 = mass - E1
    # print (mass*mass,m1*m1, m2*m2,-2.*mass*m1,-2.*mass*m2,- 2.*m1*m2)
    triangle = mass*mass*mass*mass + m1*m1*m1*m1 + m2*m2*m2*m2 -2.*mass*m1*mass*m1 -2.*mass*m2*mass*m2 - 2.*m1*m2*m1*m2
    # print (triangle)
    Q = math.sqrt(triangle)/2./mass
    # print ("decay",mass,E1,E2,Q)
    V1 = Q*ROOT.TVector3(math.sqrt(1-cost*cost),0,cost)
    P1 = ROOT.TLorentzVector()
    P1.SetVectM(V1,m1)
    V2 = Q*ROOT.TVector3(-math.sqrt(1-cost*cost),0,-cost)
    P2 = ROOT.TLorentzVector()
    P2.SetVectM(V2,m2)
    check = P1 + P2
    # check.Print()
    # P1.Print()
    # P2.Print()
    return P1, P2

def CCQECanvas(name,title,xsize=1100,ysize=720):
    c2 = ROOT.TCanvas(name,title,xsize,ysize)
    # c2.SetLeftMargin(0.1)
    c2.SetRightMargin(0.04)
    c2.SetLeftMargin(0.1)
    c2.SetTopMargin(0.1)
    c2.SetBottomMargin(0.12)
    return c2

def CCQELegend(xlow,ylow,xhigh,yhigh):
    leg = ROOT.TLegend(xlow,ylow,xhigh,yhigh)
    leg.SetFillStyle(0)
    leg.SetBorderSize(0)
    leg.SetTextSize(0.042)
    return leg


hyp_cm = ROOT.TLorentzVector()
hyp_cm.SetVectM(ROOT.TVector3(0,0,0),m_Lambda)


# Make a list of sample thetas and lambda KEs
theta_list = [math.pi*i/(n_theta_bins-1) for i in range(0,n_theta_bins)]
tlambda_list = [0.01+i*2/100 for i in range(0,100)]
# print(theta_list)
print(tlambda_list)

# Make a list of the boost vectors given lambda KE
cmboost_list = []
for tlambda in tlambda_list:
    E_lambda = m_Lambda + tlambda
    print(E_lambda)
    # print(E_lambda)
    tmp_beta = math.sqrt(1 - m_Lambda*m_Lambda/E_lambda/E_lambda)
    print(tmp_beta)


    tmp_cmboost = ROOT.TVector3(0.,0.,tmp_beta)
    cmboost_list.append(tmp_cmboost)
# Setting up some histograms, these 2D ones might not be useful
# t_proton_hist = ROOT.TH2D("t_proton_hist","t_proton_hist",100,0,2,n_theta_bins,0,math.pi)
# t_pion_hist = ROOT.TH2D("t_pion_hist","t_pion_hist",100,0,2,n_theta_bins,0,math.pi)

# proton_tracked_hist = ROOT.TH2D("proton_tracked_hist","proton_tracked_hist",100,0,2,n_theta_bins,0,math.pi)
# pion_tracked_hist = ROOT.TH2D("pion_tracked_hist","pion_tracked_hist",100,0,2,n_theta_bins,0,math.pi)

# for the next few lists, first index is angle, second index is tlambda

# Raw output of KEs
t_proton_list = []
t_pion_list = []

# List if FS part is tracked (1 is above threshold, 0 is not)
proton_tracked_list2d = []
pion_tracked_list2d = []
justpion_list2d = []
justproton_list2d = []
both_list2d = []

nothing_list2d = []
for i in range(len(theta_list)):
    cost = math.cos(theta_list[i])
    proton, pion = decayme(hyp_cm,m_proton,m_pi,cost)
    tmp_proton_tracked_list = []
    tmp_pion_tracked_list = []   
    tmp_justpion_list = []
    tmp_justproton_list = []
    tmp_both_list = []

    tmp_t_proton_list = []
    tmp_t_pion_list = []

    tmp_nothing_list = []
    for j in range(len(cmboost_list)):
        tmp_proton = proton.Clone()
        tmp_pion = pion.Clone()
        tmp_proton.Boost(cmboost_list[j])
        tmp_pion.Boost(cmboost_list[j])
        t_proton = tmp_proton.E() - m_proton
        t_pion = tmp_pion.E() - m_pi
        # print(t_proton, t_pion)
        tmp_t_proton_list.append(t_proton)
        tmp_t_pion_list.append(t_pion)

        if t_proton - proton_threshold > 0:
            tmp_proton_tracked_list.append(1)
        else:
            tmp_proton_tracked_list.append(0)
        if t_pion - pion_threshold > 0:
            tmp_pion_tracked_list.append(1)
        else:
            tmp_pion_tracked_list.append(0)
        
        if t_proton - proton_threshold > 0 and t_pion - pion_threshold > 0:
            tmp_both_list.append(1)
        else:
            tmp_both_list.append(0)

        if t_proton - proton_threshold > 0 and t_pion - pion_threshold <= 0:
            tmp_justproton_list.append(1)
        else: 
            tmp_justproton_list.append(0)

        if t_proton - proton_threshold <= 0 and t_pion - pion_threshold > 0:
            tmp_justpion_list.append(1)
        else: 
            tmp_justpion_list.append(0)

        if t_proton - proton_threshold <= 0 and t_pion - pion_threshold <= 0:
            tmp_nothing_list.append(1)
        else:
            tmp_nothing_list.append(0)
        # print(tmp_t_proton_list)
    # t_proton_list.append(tmp_t_proton_list)
    # t_pion_list.append(tmp_t_pion_list)

    proton_tracked_list2d.append(tmp_proton_tracked_list)
    pion_tracked_list2d.append(tmp_pion_tracked_list)
    justpion_list2d.append(tmp_justpion_list)
    justproton_list2d.append(tmp_justproton_list)
    both_list2d.append(tmp_both_list)
    nothing_list2d.append(tmp_nothing_list)

# Now want to sum over angles for each tlambda
proton_tracked_list1d = np.array(proton_tracked_list2d[0])
pion_tracked_list1d = np.array(pion_tracked_list2d[0])

justpion_list1d = np.array(justpion_list2d[0])
justproton_list1d = np.array(justproton_list2d[0])
both_list1d = np.array(both_list2d[0])

nothing_list1d = np.array(nothing_list2d[0])
# Loop over angles
for i in range(1,len(proton_tracked_list2d)):
    proton_tracked_list1d = np.add(proton_tracked_list1d, proton_tracked_list2d[i])
    pion_tracked_list1d = np.add(pion_tracked_list1d, pion_tracked_list2d[i])

    justpion_list1d = np.add(justpion_list1d,justpion_list2d[i])
    justproton_list1d = np.add(justproton_list1d,justproton_list2d[i])
    both_list1d = np.add(both_list1d,both_list2d[i])

    nothing_list1d = np.add(nothing_list1d, nothing_list2d[i])


proton_tracked_prob = proton_tracked_list1d/len(proton_tracked_list2d)
pion_tracked_prob = pion_tracked_list1d/len(pion_tracked_list2d)

justpion_prob = justpion_list1d/len(justpion_list2d)
justproton_prob = justproton_list1d/len(justproton_list2d)
both_prob = both_list1d/len(both_list2d)

nothing_prob = nothing_list1d/len(nothing_list2d)

proton_tracked_hist = ROOT.TH1D("proton_tracked_hist", "proton_tracked_hist", 100, 0., 2.)
pion_tracked_hist = ROOT.TH1D("pion_tracked_hist", "pion_tracked_hist", 100, 0., 2.)

justpion_hist = ROOT.TH1D("justpion_hist", "justpion_hist", 100, 0., 2.)
justproton_hist = ROOT.TH1D("justproton_hist", "justproton_hist", 100, 0., 2.)
both_hist = ROOT.TH1D("both_hist", "both_hist", 100, 0., 2.)

nothing_hist = ROOT.TH1D("nothing_hist", "nothing_hist", 100, 0., 2.)

for i in range(len(proton_tracked_prob)):
    proton_tracked_hist.SetBinContent(i+1, proton_tracked_prob[i])
    pion_tracked_hist.SetBinContent(i+1, pion_tracked_prob[i])
    justpion_hist.SetBinContent(i+1, justpion_prob[i])
    justproton_hist.SetBinContent(i+1, justproton_prob[i])
    both_hist.SetBinContent(i+1, both_prob[i])
    nothing_hist.SetBinContent(i+1, nothing_prob[i])


proton_tracked_hist.SetTitle("Fraction with protons above threshold")
proton_tracked_hist.GetXaxis().SetTitle("T_{#Lambda}")

pion_tracked_hist.SetTitle("Fraction with #pi^- above threshold")
pion_tracked_hist.GetXaxis().SetTitle("T_{#Lambda}")

justpion_hist.SetTitle("Fraction with #pi^- above threshold with no protons")
justpion_hist.GetXaxis().SetTitle("T_{#Lambda}")

justproton_hist.SetTitle("Fraction with protons above threshold with no #pi^-")
justproton_hist.GetXaxis().SetTitle("T_{#Lambda}")

both_hist.SetTitle("Fraction with both protons and #pi^- above threshold")
both_hist.GetXaxis().SetTitle("T_{#Lambda}")

nothing_hist.SetTitle("Fraction with nothing above threshold")
nothing_hist.GetXaxis().SetTitle("T_{#Lambda}")

total_nopass1track = justpion_hist.Clone()
total_nopass1track.Add(justproton_hist)
total_nopass1track.Add(both_hist)

total_nopass2track = justpion_hist.Clone()
total_nopass2track.Add(both_hist)

# Now make a hist convoluted with the lambda energies

ifilename = "/Users/nova/git/CCQENu/GENIE3/output/hypT_g18_10a_02_11a.root"

# lambdaT_histname = "myLambdaE_hist"

ifile = ROOT.TFile(ifilename,"READ")
# I'm only worried about the lambdaT hist for now, but I'm gonna grab everything else I need for plotting later
lambdaT_hist = ifile.Get("myLambdaE_hist").Clone()

sigmaminT_hist = ifile.Get("mySigmaMinusE_hist").Clone()
sigmazeroT_hist = ifile.Get("mySigmaZeroE_hist").Clone()
hyptype_hist = ifile.Get("myhyptype_hist").Clone()

# # area norm it <- Not necessary
# lambdaT_hist.Scale(lambdaT_hist.Integral())

convolveproton_hist = lambdaT_hist.Clone()
convolvepion_hist = lambdaT_hist.Clone()
convolnothing_hist = lambdaT_hist.Clone()
convolnopass1track_hist = lambdaT_hist.Clone()
convolnopass2track_hist = lambdaT_hist.Clone()
convolboth_hist = lambdaT_hist.Clone()

convolveproton_hist.Multiply(proton_tracked_hist)
convolvepion_hist.Multiply(pion_tracked_hist)
convolnothing_hist.Multiply(nothing_hist)
convolnopass1track_hist.Multiply(total_nopass1track)
convolnopass2track_hist.Multiply(total_nopass2track)
convolboth_hist.Multiply(both_hist)

print("probability tracking proton: ", convolveproton_hist.Integral()/lambdaT_hist.Integral())
print("probability tracking pion: ", convolvepion_hist.Integral()/lambdaT_hist.Integral())
print("probability tracking nothing: ", convolnothing_hist.Integral()/lambdaT_hist.Integral())
print("probability nopass1track: ", convolnopass1track_hist.Integral()/lambdaT_hist.Integral())
print("probability nopass2track: ", convolnopass2track_hist.Integral()/lambdaT_hist.Integral())
print("probability both track: ", convolboth_hist.Integral()/lambdaT_hist.Integral())
plotdir = "/Users/nova/git/plots/Winter2025MinervaCollab"
outdirname = path.join(plotdir,"lambdadecay_50MeVPions_10a")
if not path.exists(outdirname): mkdir(outdirname)
ofilename = path.join(outdirname,"lambdadecay_50MeVPions.root")
myoutput = ROOT.TFile(ofilename,"RECREATE")

proton_tracked_hist.Write()
pion_tracked_hist.Write()
justpion_hist.Write()
justproton_hist.Write()
both_hist.Write()
nothing_hist.Write() 

print("Done writing hists to: ", ofilename)

# Actually making pretty plots?
ROOT.gStyle.SetOptStat(0)

# Make plot from the genie processing file
# hyptypes plot
canvas = CCQECanvas("hyptype_hist","Types of hyperons")
hyptype_hist.Scale(1./hyptype_hist.Integral(),"nosw2")
hyptype_hist.GetXaxis().SetTitle("")
hyptype_hist.GetXaxis().CenterTitle()
hyptype_hist.GetXaxis().SetLabelSize(0.07)
hyptype_hist.GetYaxis().SetTitle("Fraction of QElike Hyperons")
hyptype_hist.GetYaxis().CenterTitle()
hyptype_hist.SetBarWidth(0.6)
hyptype_hist.SetBarOffset(0.2)
hyptype_hist.Draw("BAR")
# canvas.Draw()
canvas.Print(path.join(outdirname,"hyptype_hist.png"))

# various T plots
# sigmaminT_hist
# sigmazeroT_hist

canvas = CCQECanvas("lambdaT_plot","T_{#Lambda}")
# canvas.SetLogy()
lambdaT_hist.GetXaxis().CenterTitle()
lambdaT_hist.GetYaxis().SetTitle("N_{events}")
lambdaT_hist.GetYaxis().CenterTitle()
lambdaT_hist.SetTitle("T_{#Lambda}")
lambdaT_hist.Draw("H")
lambdaT_hist.Draw("H,same")
# canvas.Draw()
canvas.Print(path.join(outdirname,"lambdaT.png"))

canvas = CCQECanvas("sigmaminT_plot","T_{#Sigma^{-}}")
sigmaminT_hist.GetXaxis().CenterTitle()
sigmaminT_hist.GetYaxis().SetTitle("N_{events}")
sigmaminT_hist.GetYaxis().CenterTitle()
sigmaminT_hist.SetTitle("T_{#Sigma^{-}}")
sigmaminT_hist.Draw("H")
sigmaminT_hist.Draw("H,same")
# canvas.Draw()
canvas.Print(path.join(outdirname,"sigmaminT.png"))

canvas = CCQECanvas("sigmazeroT_plot","T_{#Sigma^{0}}")
sigmazeroT_hist.GetXaxis().CenterTitle()
sigmazeroT_hist.GetYaxis().SetTitle("N_{events}")
sigmazeroT_hist.GetYaxis().CenterTitle()
sigmazeroT_hist.SetTitle("T_{#Sigma^{0}}")
sigmazeroT_hist.Draw("H")
sigmazeroT_hist.Draw("H,same")
# canvas.Draw()
canvas.Print(path.join(outdirname,"sigmazeroT.png"))

# Make plots of the hists we made a minute ago
hist_dict = {
    "pion_tracked": pion_tracked_hist,
    "proton_tracked": proton_tracked_hist,
    "justpion": justpion_hist,
    "justproton": justproton_hist,
    "both": both_hist,
    "nothing": nothing_hist
}

for hist in hist_dict.keys():
    hist_dict[hist].GetXaxis().CenterTitle()
    hist_dict[hist].GetXaxis().SetTitleSize(0.05)
    hist_dict[hist].GetYaxis().SetTitle("Fraction")
    hist_dict[hist].GetYaxis().CenterTitle()
    hist_dict[hist].GetYaxis().SetTitleSize(0.05)

# Make a plot of the straight proton and pion fractions
canvas = CCQECanvas("protonpion_tracked","Fraction of tracked Protons and Pions")
leg = CCQELegend(0.7,0.2,1.0,0.4)
hist_dict["proton_tracked"].SetLineColor(ROOT.kRed)
hist_dict["proton_tracked"].SetLineWidth(7)
hist_dict["proton_tracked"].SetTitle("Fraction at tracking threshold vs. T_{#Lambda}")

hist_dict["pion_tracked"].SetLineColor(ROOT.kBlue)
hist_dict["pion_tracked"].SetLineWidth(7)
leg.AddEntry(hist_dict["proton_tracked"],"proton","l")
leg.AddEntry(hist_dict["pion_tracked"],"#pi^{-}","l")

hist_dict["proton_tracked"].Draw("hist")
hist_dict["pion_tracked"].Draw("hist,Same")
leg.Draw()

# canvas.Draw()
canvas.Print(path.join(outdirname,"protonpion_tracked.png"))

# Make a plot of only pion and only proton fractions
canvas = CCQECanvas("justproton_justpion","Fraction of just protons and just pions")
leg = CCQELegend(0.7,0.2,1.0,0.4)
hist_dict["justproton"].SetLineColor(ROOT.kRed+2)
hist_dict["justproton"].SetLineWidth(7)
hist_dict["justproton"].SetMaximum(1.05)
hist_dict["justproton"].SetTitle("Fraction above tracking threshold vs. T_{#Lambda}")

hist_dict["both"].SetLineColor(ROOT.kOrange+2)
hist_dict["both"].SetLineWidth(7)

hist_dict["justpion"].SetLineColor(ROOT.kBlue+2)
hist_dict["justpion"].SetLineWidth(7)
leg.AddEntry(hist_dict["proton_tracked"],"proton only","l")
leg.AddEntry(hist_dict["justpion"],"#pi^{-} only","l")
leg.AddEntry(hist_dict["both"],"Both at threshold","l")

hist_dict["justproton"].Draw("hist")
hist_dict["justpion"].Draw("hist,Same")
hist_dict["both"].Draw("hist,Same")
leg.Draw()

# canvas.Draw()
canvas.Print(path.join(outdirname,"justproton_justpion.png"))

# Make a plot of fraction that would pass 2track cuts
canvas = CCQECanvas("fraction_lambda_passcuts","Fraction that would pass cuts")
leg = CCQELegend(0.6,0.2,1.0,0.6)

hist_dict["justproton"].SetLineColor(ROOT.kRed+2)
hist_dict["justproton"].SetLineWidth(7)
hist_dict["justproton"].SetMaximum(1.05)
hist_dict["justproton"].SetTitle("Fraction not vetoed by cuts vs. T_{#Lambda}")

hist_dict["nothing"].SetLineColor(ROOT.kGreen+3)
hist_dict["nothing"].SetLineWidth(7)

total_pass = hist_dict["justproton"].Clone()
total_pass.Add(hist_dict["nothing"])
total_pass.SetLineColor(ROOT.kBlack)
total_pass.SetLineWidth(7)
total_pass.SetLineStyle(10)

leg.AddEntry(hist_dict["proton_tracked"],"proton only","l")
leg.AddEntry(hist_dict["nothing"],"None above threshold","l")
leg.AddEntry(total_pass,"Total not vetoed by cuts","l")

hist_dict["justproton"].Draw("hist")
# hist_dict["justproton"].Draw("hist,same")
hist_dict["nothing"].Draw("hist,Same")
total_pass.Draw("hist,same")

leg.Draw()

# canvas.Draw()
canvas.Print(path.join(outdirname,"fraction_lambda_passcuts.png"))

# Make plot of fraction that would not pass 2 track cuts
canvas = CCQECanvas("fraction_lambda_notpasscuts_2track","Fraction that would not pass cuts (2-track)")
leg = CCQELegend(0.6,0.2,1.0,0.4)

hist_dict["justpion"].SetLineColor(ROOT.kBlue+2)
hist_dict["justpion"].SetLineWidth(7)
hist_dict["justpion"].SetMaximum(1.05)
hist_dict["justpion"].SetTitle("Fraction vetoed by cuts (2-track) vs. T_{#Lambda}")

hist_dict["both"].SetLineColor(ROOT.kOrange+2)
hist_dict["both"].SetLineWidth(7)

total_nopass = hist_dict["justpion"].Clone()
total_nopass.Add(hist_dict["both"])
total_nopass.SetLineColor(ROOT.kBlack)
total_nopass.SetLineWidth(7)
total_nopass.SetLineStyle(10)

leg.AddEntry(hist_dict["justpion"],"#pi^{-} only","l")
leg.AddEntry(hist_dict["both"],"Both at threshold","l")
leg.AddEntry(total_nopass,"Total vetoed by cuts","l")

hist_dict["justpion"].Draw("hist")
# hist_dict["justproton"].Draw("hist,same")
hist_dict["both"].Draw("hist,Same")
total_nopass.Draw("hist,same")

leg.Draw()

# canvas.Draw()
canvas.Print(path.join(outdirname,"fraction_lambda_notpasscuts_2track.png"))

# Make plot of fraction that would not pass 1 track cuts
canvas = CCQECanvas("fraction_lambda_notpasscuts_1track","Fraction that would not pass cuts (1-track)")
leg = CCQELegend(0.6,0.2,1.0,0.4)

hist_dict["justpion"].SetLineColor(ROOT.kBlue+2)
hist_dict["justpion"].SetLineWidth(7)
hist_dict["justpion"].SetMaximum(1.05)
hist_dict["justpion"].SetTitle("Fraction not passing cuts (1-track) vs. T_{#Lambda}")
hist_dict["justproton"].SetLineColor(ROOT.kRed+2)
hist_dict["justproton"].SetLineWidth(7)
hist_dict["both"].SetLineColor(ROOT.kOrange+2)
hist_dict["both"].SetLineWidth(7)

total_nopass1track = hist_dict["justpion"].Clone()
total_nopass1track.Add(hist_dict["justproton"])
total_nopass1track.Add(hist_dict["both"])
total_nopass1track.SetLineColor(ROOT.kBlack)
total_nopass1track.SetLineWidth(7)
total_nopass1track.SetLineStyle(10)

leg.AddEntry(hist_dict["justpion"],"#pi^{-} only","l")
leg.AddEntry(hist_dict["justproton"],"proton only","l")
leg.AddEntry(hist_dict["both"],"Both at threshold","l")
leg.AddEntry(total_nopass1track,"Total not passing cuts","l")

hist_dict["justpion"].Draw("hist")
hist_dict["justproton"].Draw("hist,same")
hist_dict["both"].Draw("hist,Same")
total_nopass1track.Draw("hist,same")

leg.Draw()

# canvas.Draw()
canvas.Print(path.join(outdirname,"fraction_lambda_notpasscuts_1track.png"))

# test = ROOT.TLorentzVector()
# test.SetVectM(ROOT.TVector3(0,0,1),1.115)
# print("test.Print(): ")
# test.Print()
# new,cmboost = me2CM(test)
# proton,pion = decayme(new,.938,.135,0)
# proton.Print()
# pion.Print()
# proton.Boost(-cmboost)
# pion.Boost(-cmboost)
# proton.Print()
# pion.Print()
# back = pion+proton
# back.Print()

# vhyp = ROOT.TLorentzVector()
# vhyp.SetVectM(ROOT.TVector3(0,0,1),m_Lambda)
# vhyp.Print()

# vhyp_new, vhyp_boost = me2CM(vhyp)
# vproton,vpion = decayme(vhyp_new, m_proton, m_pi)
# vproton.Print()
# vpion.Print()
# proton.Boost

# t_lambda = 0.
# E_lambda = m_Lambda + t_lambda
# hyp_beta = math.sqrt(1-m_Lambda*m_Lambda/E_lambda/E_lambda)
# cmboost = ROOT.TVector3(0.,0.,-hyp_beta)

# hyp_cm = ROOT.TLorentzVector()
# hyp_cm.SetVectM(ROOT.TVector3(0,0,0),1.115)

# cost = 0.0 # This is with proton ecactly forward, pion exactly backward
# proton, pion = decayme(hyp_cm,m_proton,m_pi,cost)
# proton.Boost(-cmboost)
# pion.Boost(-cmboost)

# t_proton = proton.E() - m_proton
# t_pion = pion.E() - m_pi

# print( t_proton )
# print( t_pion )
