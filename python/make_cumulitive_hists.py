# This just turns all the hists in a root file into cumulitive plots

import sys
from PlotUtils import MnvH1D, MnvH2D
import ROOT
from ROOT import gROOT,gStyle, TFile,THStack,TH1D,TCanvas,TColor,TObjArray,TH2F,THStack,TFractionFitter,TLegend,TLatex, TString

target_n_bins = 10

def GetEqualBinning(hist, n_bins):
    """ 
    Function to return binning from cumulitive histogram hist, with target number of bins n_bins
    """
    i_n_bins = hist.GetNbinsX()
    # print("i_n_bins: ",i_n_bins)
    total = hist.GetBinContent(i_n_bins)
    # print(hist.GetName())
    # print(total)
    base_target_bincont = total/n_bins # target total for each bin
    # print("target_bincont: ",base_target_bincont)
    binning = [hist.GetXaxis().GetBinLowEdge(1)] # binning to be returned, with lowest edge put in already
    target_bincont = base_target_bincont
    for bin in range(1,i_n_bins): # loop over all the bins
        bincont = hist.GetBinContent(bin)
        if bincont < target_bincont: # if it's less than the target, keep going
            # print("here, bincont, ",bincont,"\ttarget bincont. ",target_bincont)
            continue
        # if it's not less than the target, record the bin edges
        else:
            binning.append(round(hist.GetXaxis().GetBinUpEdge(bin),5))
            target_bincont += base_target_bincont
    if len(binning)>n_bins: #sometimes it makes things one longer if the last bin is really close to the max
        del binning[-1]
    binning.append(0.5) # tack on the maximum (hardcoded for now for recoil with a 0.5gev max cut)
    return binning

def main():
    # XYZ
    ROOT.TH1.AddDirectory(ROOT.kFALSE)

    if len(sys.argv) == 1:
        print ("python make_cumulitive_hists.py <rootfile> <option>")
    filename = sys.argv[1]
    # if len(sys.argv) == 3:
    #     target_n_bins = sys.argv[2]

    print("Getting started...")

    f = ROOT.TFile.Open(filename,"READONLY")
    outname = filename.replace(".root","_cumulitive.root")

    keys = f.GetListOfKeys()

    hist_dict = {}
    for key in keys:
        name = key.GetName()
        # print("\tlooking at hist ", name)
        hist = f.Get(name).Clone()
        if name in ["POT_summary","pot"]:
            hist_dict[name] = hist
            continue
        if "___" not in name:
            print(name," not a valid hist")
            continue
        parse = name.split("___")
        hist_type = parse[0]
        category = parse[4]
        if hist_type!="h" or "response" in category:
            print(name, " is not 1D or is response. No change")
            hist_dict[name] = hist
            continue

        cumul_hist = hist.GetCumulative()
        hist_dict[cumul_hist.GetName()] = cumul_hist

    f.Close()
    print("Warning: making new out file. This may overwrite ",outname)
    of = ROOT.TFile.Open(outname, "RECREATE")
    of.cd()

    binning_dict = {}
    for hist in hist_dict.keys():
        # print(hist)
        hist_dict[hist].Write()
        if "___" not in hist: 
            # print("Not parseable\t",hist)
            continue
        parse = hist.split("___")
        if parse[2]!="qelike":
            # print("Not qelike\t",hist)
            continue
        if parse[4] not in ["reconstructed_cumulative","selected_truth_cumulative"]:
            # print("Not reco or truth\t",hist)
            continue
        binning = GetEqualBinning(hist_dict[hist],target_n_bins)
        binning_dict[hist] = binning
        # print("Binning for hist ", hist)
        # print(binning)

    for key in binning_dict.keys():
        parse = key.split("___")
        # key looks like h___QElike___qelike___EAvail___selected_truth_cumulative
        if parse[4]=="reconstructed_cumulative":
            cat_key = key.replace("reconstructed_cumulative","selected_truth_cumulative")
            avg_binning = []

            print("len reco: ",len(binning_dict[key]))
            print("Binning for reco hist ", key)
            print(binning_dict[key])
            print("len true: ",len(binning_dict[cat_key]))
            print("Binning for selected true hist ", cat_key)
            print(binning_dict[cat_key])
            for bin in range(len(binning_dict[key])):
                avg = round(((binning_dict[key][bin] + binning_dict[cat_key][bin]) / 2.), 5)
                avg_binning.append(avg)
            print("Binning for average ")
            print(avg_binning)
            


    of.Close()

    
    print("Done!")



if __name__ == "__main__":
    main()
