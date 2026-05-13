# Script to run over nuisance files for cross section model comparisons 
# Noah Harvey Vaughan, vaughann@oregonstate.edu, April 2026
# 
# Loosely based on several other MINERvAn's scripts

import ROOT
import XRootD
import sys, os
# from PlotUtils import MnvH1D, MnvH2D
# import PlotUtils
import math
import array 
import json, re
import datetime

# from tqdm import trange
# import tqdm
# import time

mydate = datetime.datetime.now()
month = mydate.strftime("%B")
year = mydate.strftime("%Y")

dosmalltest = False

varstodo = [
    "EAvail",
    "ptmu",
    "EAvail_ptmu",
    # "Q2QE"
]

# varstodo2d = [
#     "ptmu_EAvail"
# ]

samplestodo = [
    "QElike",
    "QElikeHyp"
]

setRHC = True

def MakeOutputDir(subdir=""):
    """
    Subdir is the one for all plots that this script should ouptut. You will need to add
    any other subdirs in the script itself (e.g. based off input file name)
    """
    outdir = ""
    base_outdir = os.environ.get("OUTPUTLOC")
    if base_outdir != None:
        outdir = os.path.join(base_outdir, month + year)
    else:
        outdir = os.path.join("/Users/nova/git/output/", month + year)
    if not os.path.exists(outdir):
        print("Can't find output dir. Making it now... ", outdir)
        os.mkdir(outdir)
    else:
        print("found dir ", outdir)
    if subdir == "":
        return outdir
    if not os.path.exists(os.path.join(outdir, subdir)):
        print("Can't find output dir. Making it now... ", os.path.join(outdir, subdir))
        os.mkdir(os.path.join(outdir, subdir))
    else:
        print("found dir ", outdir)

    return os.path.join(outdir, subdir)

def getMuonMomentum(mytree, RHC = True):
    muonpdg = 13
    if RHC:
        muonpdg = -13
    muon_mom = ROOT.TVector3()

    nfsp = mytree.nfsp
    Efsp = mytree.E
    pdg  = mytree.pdg
    px = mytree.px
    py = mytree.py
    pz = mytree.pz
    
    for p in range(0,nfsp):
        if(pdg[p] == muonpdg):
            muon_mon.SetXYZ(px[p],py[p],pz[p])
            # muon_mom.SetX(px[p])
            # muon_mom.SetY(py[p])
            # muon_mom.SetZ(pz[p])
            break
    return muon_mom

def isCCQELike(mytree, RHC=True):
    # This checks the particle content and muon kinematics to check if it's qelike
    # It has options for FHC or RHC, and it excludes hyperons

    nfsp = mytree.nfsp
    Efsp = mytree.E
    pdg  = mytree.pdg

    badMesons = [
        111,
        211,
        321,
        323,
        111,
        130,
        310,
        311,
        313,
        411,
        421,
    ]
    #probably addd the pi0 as well....
    #this also has hyperons (as bad baryons) in the signal)
    badBaryons = [
        3112,
        3122,
        3212,
        3222,
        3224,
        3214,
        3114,
        3322,
        3312,
        3324,
        3314,
        3334,
        4112,
        4122,
        4212,
        4222,
    ]
    
    # Counting up different important particles
    n_muminus = 0
    n_muplus = 0
    n_baryon = 0
    n_meson = 0
    n_gamma = 0
    n_proton = 0
    n_neutron = 0
    n_electrons = 0 # do i need this?

    # Index for the muon to find it later
    i_muon = -1 

    good_muon = 13
    if RHC:
        good_muon=-13
    n_goodmu = 0
    n_badmu = 0
    for i in range(0,nfsp):
        energy = Efsp[i]
        # don't need proton Ke anymore
        # proton_KE = energy-proton_mass 
        tmp_pdg = pdg[i]
        # want a mu-
        if tmp_pdg == good_muon:
            n_goodmu += 1
            i_muon = i
            # print("inside", i_muon)
            continue
        if tmp_pdg == -good_muon:
            n_badmu += 1
            # break
            return False

        # if tmp_pdg == -13:
        #     n_muplus += 1
        #     i_muon = i
        #     print("inside ", i_muon)
        #     continue
        
        # # don't want these
        # if tmp_pdg == 13:
        #     n_muminus += 1
        #     # break
        #     return False
        if abs(tmp_pdg) in badMesons:
            n_meson += 1
            # break
            return False
        if abs(tmp_pdg) in badBaryons:
            n_baryon += 1
            # break
            return False
        # Only deexcitation photons allowed
        if tmp_pdg == 22 and energy > 0.010:
            n_gamma += 1
            # break
            return False
        if abs(tmp_pdg) == 11:
            n_electrons += 1
            # break
            return False

        # can have any number of these
        if tmp_pdg == 2212:
            n_proton += 1
            continue
        if tmp_pdg == 2112:
            n_neutron += 1
            continue
    # Check particle content first
    if n_goodmu != 1:
        return False
    # print("n muminus: %s\tn muplus: %s\tn meson: %s\tn gamma: %s\tn baryon: %s\tn electrons: %s\t"%(n_muminus,n_muplus,n_meson,n_gamma,n_baryon,n_electrons))
    # if RHC:
    #     if not (n_muminus == 1 and n_muplus == 0 and n_meson == 0 and n_gamma == 0 and n_baryon == 0 and n_electrons == 0):
    #     #     print("True")
    #     # else:
    #     #     # print("False")
    #         return False
    # else: # FHC
    #     if not (n_muminus == 0 and n_muplus == 1 and n_meson == 0 and n_gamma == 0 and n_baryon == 0 and n_electrons == 0):
    #         return False
   
    # Now check muon kinematics
    if i_muon < 0:
        print(i_muon)
        print("WARNING: isCCQELike: muon not found, got negative index, returning False")
        return False
    
    pz = mytree.pz[i_muon]
    
    pzmingev = 1.5
    pzmaxgev = 15.0
    
    if pz < pzmingev or pz > pzmaxgev:
        return False
    
    # px = mytree.px[i_muon]
    # py = mytree.py[i_muon]
    pmu_vec = ROOT.TVector3()
    pmu_vec.SetX(mytree.px[i_muon])
    pmu_vec.SetY(mytree.py[i_muon])
    pmu_vec.SetZ(pz)

    thetamu = pmu_vec.Theta()*180.0/3.1415

    if thetamu > 20.0:
        return False

    # Everything checked out at this point, so this is a qelike event
    return True

def isCCQELikeHyp(mytree, RHC = True):
    # This checks the particle content and muon kinematics to check if it's 
    # qelike hyperon production (with |dS| = 1). This process is only numubar
    # so only RHC, and it does not include other non hyperon qelike events
    if not RHC:
        return False
    nfsp = mytree.nfsp
    Efsp = mytree.E
    pdg  = mytree.pdg

    badMesons = [
        111,
        211,
        321,
        323,
        111,
        130,
        310,
        311,
        313,
        411,
        421,
    ]
    #probably addd the pi0 as well....
    badBaryons = [
        4112,
        4122,
        4212,
        4222,
    ]
    
    # We want one hyperon in the final state, listed here
    goodHyperons = [
        3112,
        3122,
        3212,
        3222,
        3224,
        3214,
        3114,
        3322,
        3312,
        3324,
        3314,
        3334,
    ]

    # Counting up different important particles
    n_muminus = 0
    n_muplus = 0
    n_baryon = 0
    n_hyperon = 0
    n_meson = 0
    n_gamma = 0
    n_proton = 0
    n_neutron = 0
    n_electrons = 0 # do i need this?

    # Index for the muon to find it later
    i_muon = -1 


    # good_muon = 13
    # if RHC:
    #     good_muon=-13
    # n_goodmu = 0
    # n_badmu = 0
    
    for p in range(0,nfsp):
        energy = Efsp[p]
        # don't need proton Ke anymore
        # proton_KE = energy-proton_mass 
        tmp_pdg = pdg[p]
        # want a mu+
        if tmp_pdg == -13:
            n_muplus += 1
            i_muon = p
            continue
        
        # don't want these
        if tmp_pdg == 13:
            n_muminus += 1
            # break
            return False
        if abs(tmp_pdg) in badMesons:
            n_meson += 1
            # break
            return False
        if abs(tmp_pdg) in badBaryons:
            n_baryon += 1
            # break
            return False
        # Only deexcitation photons allowed
        if tmp_pdg == 22 and Efsp[p] > 0.010:
            n_gamma += 1
            # break
            return False
        if abs(tmp_pdg) == 11:
            n_electrons += 1
            # break
            return False

        # can have any number of these
        if tmp_pdg == 2212:
            n_proton += 1
            continue
        if tmp_pdg == 2112:
            n_neutron += 1
            continue
        if abs(tmp_pdg) in goodHyperons:
            n_hyperon += 1
            continue
    # Check particle content first
    # if not (n_muminus == 1 and n_hyperon == 1 and n_muplus == 0 and n_meson == 0 and n_gamma == 0 and n_baryon == 0 and n_electrons == 0):
    #     return False   
    # Now check muon kinematics
    if n_hyperon != 1:
        return False
    if n_muplus != 1:
        return False

    if i_muon < 0:
        print("WARNING: isCCQELikeHyp: muon not found, got negative index, returning False")
        return False


    pz = mytree.pz[i_muon]
    
    pzmingev = 1.5
    pzmaxgev = 15.0
    
    if pz < pzmingev or pz > pzmaxgev:
        return False
    
    # px = mytree.px[i_muon]
    # py = mytree.py[i_muon]
    pmu_vec = ROOT.TVector3()
    pmu_vec.SetX(mytree.px[i_muon])
    pmu_vec.SetY(mytree.py[i_muon])
    pmu_vec.SetZ(pz)

    thetamu = pmu_vec.Theta()*180.0/3.1415

    if thetamu > 20.0:
        return False

    # Everything checked out at this point, so this is a qelike event
    return True


def getEAvailGeV(mytree):
    # Eavail based on truth definition in CVUniverse
    # Some trees might just have this as Eav
    eavail = 0.0

    nfsp  = mytree.nfsp
    pdg = mytree.pdg
    Efsp = mytree.E

    for i in range(0, nfsp):
        energy = Efsp[i]
        if pdg[i] == 2212:
            eavail += energy - 0.93827 # T_p for protons
            continue
        if pdg[i] == 2112:
            continue # skip neutrons
        if pdg[i] > 1E9:
            continue # ignore nuclear frags
        if abs(pdg[i]) in [11, 13]:
            continue # skip leptons
        if abs(pdg[i]) == 211:
            eavail += energy - 0.13957 # T_pi for charged pions
            continue
        if abs(pdg[i]) == 111:
            eavail += energy # E_pi for neutral pions
            continue
        if pdg[i] == 22:
            eavail += energy # add gammas
            continue
        if pdg[i] >= 2000:
            eavail += energy - 0.93827 # any other baryons add the energy minus proton mass
        if pdg[i] <= -2000:
            eavail += energy + 0.93827 # weirdness for antibaryons?
        else:
            eavail += energy
    return eavail

def getptmuGeV(mytree, RHC = True):
    muon_pt = -9999
    nfsp  = mytree.nfsp
    pdg = mytree.pdg
    muonpdg = 13
    if RHC:
        muonpdg = -13

    i_muon = -1
    for i in range(0,nfsp):
        if pdg[i] == muonpdg: 
            i_muon = i
            break
    
    px = mytree.px[i_muon]
    py = mytree.py[i_muon]

    # pz = mytree.pz[i_muon]
    # pmu_vec = ROOT.TVector3()
    # pmu_vec.SetX(px)
    # pmu_vec.SetY(py)
    # pmu_vec.SetZ(pz)
    
    muon_pt = math.sqrt(px*px + py*py)
    return muon_pt

def GetHistToFill(var, sample, varconfig_dict):
    # Makes a histogram to be filled later, uses NuConfig variable system
    name = "h___%s___%s"%(sample,var) 
    title = "%s %s"%(sample,var)
    # Make the name
    if "_" in var:
        name.replace("h___","h2D___")
        xbins = []
        ybins = []
        xtitle = ""
        ytitle = ""
        xvar = var.split("_")[0]
        yvar = var.split("_")[1]
        if xvar not in varconfig_dict["1D"]:
            print("Error: cannot find var %s for 2D var %s in config. Exiting...")%(xvar,var)
            sys.exit(1)
        if yvar not in varconfig_dict["1D"]:
            print("Error: cannot find var %s for 2D var %s in config. Exiting...")%(yvar,var)
            sys.exit(1)
        for tmpvar in [xvar, yvar]:
            tmpbins = []
            if "bins" in varconfig_dict["1D"][tmpvar]:
                tmpbins = [float(tmpbin) for tmpbin in varconfig_dict["1D"][tmpvar]["bins"]]
            elif "nbins" in varconfig_dict["1D"][tmpvar]:
                mini = float(varconfig_dict["1D"][tmpvar]["min"])
                maxi = float(varconfig_dict["1D"][tmpvar]["max"])
                width = (mini - maxi) / float(varconfig_dict["1D"][tmpvar]["nbins"])
                tmpbins = [mini + tmpbin * width for tmpbin in range(0, varconfig_dict["1D"][tmpvar]["nbins"])]
            else:
                print("Error: cannot find bins in var %s for 2D var %s in config. Exiting...")%(tmpvar,var)
                sys.exit(1)
            tmptitle = ""
            if "title" in varconfig_dict["1D"][tmpvar]:
                tmptitle = varconfig_dict["1D"][tmpvar]["title"]
            else:
                title = tmpvar
            if tmpvar == xvar: 
                xbins = tmpbins
                xtitle = tmptitle
            else: 
                ybins = tmpbins
                ytitle = tmptitle 
        hist = ROOT.TH2D(name, "%s %s"%(xtitle, ytitle), len(xbins)-1, array.array("d",xbins), len(ybins)-1, array.array("d",ybins))
        hist.GetXaxis().SetTitle(xtitle)
        hist.GetYaxis().SetTitle(ytitle)
        return hist

    # Now just do it for 1D
    
    tmpbins = []
    if "bins" in varconfig_dict["1D"][var]:
        tmpbins = [float(tmpbin) for tmpbin in varconfig_dict["1D"][var]["bins"]]
    elif "nbins" in varconfig_dict["1D"][var]:
        mini = float(varconfig_dict["1D"][var]["min"])
        maxi = float(varconfig_dict["1D"][var]["max"])
        width = (mini - maxi) / float(varconfig_dict["1D"][var]["nbins"])
        tmpbins = [mini + tmpbin * width for tmpbin in range(0, varconfig_dict["1D"][var]["nbins"])]
    else:
        print("Error: cannot find bins in var %s Exiting...")%(var)
        sys.exit(1)
    title = ""
    if "title" in varconfig_dict["1D"][var]:
        title = varconfig_dict["1D"][var]["title"]
    else:
        title = var

    hist = ROOT.TH1D(name, title, len(tmpbins)-1, array.array("d", tmpbins))
    hist.GetXaxis().SetTitle(title)
    return hist
    

# The script
def main():
    print("Starting script")
    # First check the file is loaded
    if len(sys.argv) < 2:
        print("ERROR: try python3 modelcomparison.py <Flattree root file>")
        sys.exit(1)
    fname = sys.argv[1]
    if "root://fndca1.fnal.gov:" in fname:
        print("looks like you're using a xrd path...")
        tchainname = "FlatTree_VARS"
        mychain = ROOT.TChain(tchainname)
        mychain.AddFile(fname)
        mytree = mychain
        # This is to get the file name in a useable format to make the output file and output location
        fname.replace("root://fndca1.fnal.gov:1094","")
        fname.replace("fnal.gov//","")
    else:
        print("You gave me a raw path. WARNING: if you're looking at a file in pnfs you're doing something bad, use xrd instead")
        f = ROOT.TFile(fname, "READ")
        mytree = f.Get("FlatTree_VARS")

    print(fname)
    # Make an output director
    ofiletag = "xseccomp_"+ fname
    outputdirbase = MakeOutputDir("modelxsec")
    outputdir = os.path.join(outputdirbase, os.path.basename(fname).replace(".root",""))
    if not os.path.exists(outputdir):
        print("Can't find output dir. Making it now...", outputdir)
        os.mkdir(outputdir)
    else:
        print("found output dir ", outputdir) 
    ofilename_tail = "_"
    for sample in samplestodo:
        ofilename_tail += "_"+sample
    for var in varstodo:
        ofilename_tail += "_"+var
    if dosmalltest:
        ofilename_tail += "_PRESCALE100"

    ofilename = os.path.basename(fname).replace(".root","%s.root"%(ofilename_tail))
    # Get the tree from the file, will use this later
    # Set up the hists for output
    # Get the var config from the json, this is hardcoded
    bigvarconfig_dict = {}
    varConfig_path = os.path.join(os.environ.get("CCQEMAT"), "nhv/config/variables/Variables_v15_neutronnuisance.json")
    print("\tI am looking at variable config file ", varConfig_path)
    with open(varConfig_path, "r") as varConfig_file:
        bigvarconfig_string = varConfig_file.read()
        bigvarconfig_dict = json.loads(re.sub("//.*", "", bigvarconfig_string, flags = re.MULTILINE))
    
    # Make a dict of histograms for output
    hist_dict = {"raw":{},"fluxnorm":{}}
    for norm in hist_dict.keys():
        for sample in samplestodo:
            if sample not in hist_dict[norm]: hist_dict[norm][sample] = {}
            sample_name = sample
            if norm == "raw":
                sample_name+="_raw"
            for var in varstodo:
                hist_dict[norm][sample][var] = GetHistToFill(var, sample_name, bigvarconfig_dict)
                hist_dict[norm][sample][var].Print()
        



    # Now loop over events
    # these are counters that are useful to troubleshooting
    counter = 0
    phasespace_counter = 0
    qelike_counter = 0
    hyp_counter = 0
    qelikehyp_counter = 0

    print("entering loop")
    for e in mytree:
    # for e in tqdm(mytree, desc="Processing"):
        counter += 1
        if counter%100 != 0 and dosmalltest:
            continue
        
        if counter%100000==0:
            print("%d00k"%(counter/100000))

        
        coslep = e.CosLep
        elep = e.ELep
        fScaleFactor = e.fScaleFactor
        pdglep = e.PDGLep
        # TODO: check if this is okay to do... calc is diff from how I handle it in the qelike def
        P = ROOT.TMath.Sqrt(elep*elep-0.105*0.105)
        Pl = coslep*P
        Pt = ROOT.TMath.Sqrt(1-coslep*coslep)*P

        if coslep < 0.93969262078 or abs(pdglep) != 13: continue
        phasespace_counter += 1
        Eav = e.Eav
        eavail = getEAvailGeV(e)
        scalefactor = e.fScaleFactor

        if isCCQELike(e, setRHC):
            qelike_counter += 1
            if "QElike" in samplestodo:
                if "EAvail" in varstodo:
                    # print("Filling eavail")
                    hist_dict["raw"]["QElike"]["EAvail"].Fill(eavail)
                    hist_dict["fluxnorm"]["QElike"]["EAvail"].Fill(eavail,scalefactor)
                if "ptmu" in varstodo:
                    # print("Filling ptmu")
                    hist_dict["raw"]["QElike"]["ptmu"].Fill(Pt)
                    hist_dict["fluxnorm"]["QElike"]["ptmu"].Fill(Pt,scalefactor)
                if "EAvail_ptmu" in varstodo:
                    hist_dict["raw"]["QElike"]["EAvail_ptmu"].Fill(eavail,Pt)
                    hist_dict["fluxnorm"]["QElike"]["EAvail_ptmu"].Fill(eavail,Pt,scalefactor)
        
        if isCCQELikeHyp(e, setRHC): 
            qelikehyp_counter += 1
            if "QElikeHyp" in samplestodo:
                if "EAvail" in varstodo:
                    hist_dict["raw"]["QElikeHyp"]["EAvail"].Fill(eavail)
                    hist_dict["fluxnorm"]["QElikeHyp"]["EAvail"].Fill(eavail,scalefactor)
                if "ptmu" in varstodo:
                    hist_dict["raw"]["QElikeHyp"]["ptmu"].Fill(Pt)
                    hist_dict["fluxnorm"]["QElikeHyp"]["ptmu"].Fill(Pt,scalefactor)
                if "EAvail_ptmu" in varstodo:
                    hist_dict["raw"]["QElikeHyp"]["EAvail_ptmu"].Fill(eavail,Pt)
                    hist_dict["fluxnorm"]["QElikeHyp"]["EAvail_ptmu"].Fill(eavail,Pt,scalefactor)

    print("qelike evts: ", qelike_counter)
    full_ofilename = os.path.join(outputdir, ofilename)
    myoutput = ROOT.TFile(full_ofilename, "RECREATE")
    

    print("writing hists...")
    for norm in hist_dict:
        for sample in hist_dict[norm]:
            for var in hist_dict[norm][sample]:
                print("\tWriting hist %s"%(hist_dict[norm][sample][var].GetName()))
                hist_dict[norm][sample][var].Write()
                hist_dict[norm][sample][var].Print()
    
    print("done writing hists to %s"%(full_ofilename))





    # for sample in samplestodo:
    #     ofiletag += sample + "_"
    # for var in varstodo:
    #     ofiletag += var + "_"
    

    



# # root://fndca1.fnal.gov:1094/pnfs/fnal.gov/usr/minerva/persistent/Models/GENIE/Medium_Energy/RHC/v3_0_6/tracker/G18_10a_02_11a/tracker/flat_GENIE_1000k_tune_G18_10a_02_11a_50Mcombined_rhc.root
# /pnfs/minerva/persistent/Models/GENIE/Medium_Energy/RHC/v3_0_6/tracker/G18_10a_02_11a/tracker/flat_GENIE_1000k_tune_G18_10a_02_11a_50Mcombined_rhc.root


if __name__=="__main__":
    main()

