# Noah's code

import ROOT
from PlotUtils import *



def RunFractionFitter(i_mctot_hist, i_qelike_hist, i_qelikenot_hist, i_data_hist):
    mctot_hist = i_mctot_hist.Clone()
    qelike_hist = i_qelike_hist.Clone()
    qelikenot_hist = i_qelikenot_hist.Clone()
    data_hist = i_data_hist.Clone()

    # Get some info for some calculations
    min_bin = 6
    max_bin = mctot_hist.GetNbinsX()

    print(">>>>>>>>>max_bin ", max_bin)

    # Calculate & store pre-fit fractions of MC samples.
    #prefit_sig_frac, prefit_bkg_frac = GetSigBkgFrac(
     #   mctot_hist, qelike_hist, qelikenot_hist)
    prefit_sig_frac = qelike_hist.Integral(min_bin,max_bin)/mctot_hist.Integral(min_bin,max_bin)
    prefit_bkg_frac = qelikenot_hist.Integral(min_bin,max_bin)/mctot_hist.Integral(min_bin,max_bin)
    # Make a list of the MC hists for the fitter...
    mc_list = ROOT.TObjArray(2)
    mc_list.append(qelike_hist)
    mc_list.append(qelikenot_hist)

    # Get bin width for "step size" of fit
    x_max = mctot_hist.GetXaxis().GetXmax()
    x_min = mctot_hist.GetXaxis().GetXmin()
    binwid = (x_max-x_min) / ((max_bin-min_bin)+1)
    print(">>>>>>>>>binwid ",binwid)
    # Set up fitter in verbose mode
    fit = ROOT.TFractionFitter(data_hist, mc_list, "V")
    virtual_fitter = fit.GetFitter()
    # Configure the fit for the qelike hist
    # virtual_fitter.Config().ParSettings(0).Set('qelike', prefit_sig_frac, binwid, 0.0, 1.0)
    virtual_fitter.Config().ParSettings(0).Set('qelike', prefit_sig_frac, 0.02, 0.0, 1.0) #Switched step size to be the bin width of 25 recoil bins
    # Confgure the fit for the qelikenot hist
    # virtual_fitter.Config().ParSettings(1).Set('qelikenot', prefit_bkg_frac, binwid, 0.0, 1.0)
    virtual_fitter.Config().ParSettings(1).Set('qelikenot', prefit_bkg_frac, 0.02, 0.0, 1.0)
    # Constrain the fit to between [0,1], since they are fracs and area-normed
    # fit.Constrain(0, 0.0, 1.0)
    fit.Constrain(1, 0.0, 1.0)
    fit.SetRangeX(min_bin, max_bin)
    # Do the fit
    status = fit.Fit()

    # Clean up
    del mctot_hist, qelike_hist, qelikenot_hist, data_hist

    if status != 0:
        print("WARNING: Fit did not converge...")
        return fit
    if status == 0:
        print("Fit converged.")
        return fit
        
input = ROOT.TFile.Open("../make_hists/Bkg_minervame5A_MnvTunev2_Background_Recoil_1.root","READONLY")

input.ls()

h = {}
h["qelike"] = MnvH1D()
h["data"] = MnvH1D()
h["qelikenot"] = MnvH1D()
h["mctot"] = MnvH1D()
for it in ["qelike","qelikenot","data"]:
    h[it] = input.Get("h___Background___"+it+"___recoil___reconstructed")
    
h["mctot"] = h["qelike"].Clone("mctot")
h["mctot"].Add(h["qelikenot"])

for it in h:
    h[it].Print()

minbin = 6
maxbin = h["data"].GetNbinsX()

norm = h["data"].Integral(minbin,maxbin)/ h["mctot"].Integral(minbin,maxbin)

sfrac = h["qelike"].Integral(minbin,maxbin)/h["mctot"].Integral(minbin,maxbin)

bfrac = h["qelike"].Integral(minbin,maxbin)/h["mctot"].Integral(minbin,maxbin)

for it in ["mctot","qelike","qelikenot"]:
    h[it].Scale(norm)
    h[it].Print()
    
fit = RunFractionFitter(h["mctot"],h["qelike"],h["qelikenot"],h["data"])
    
