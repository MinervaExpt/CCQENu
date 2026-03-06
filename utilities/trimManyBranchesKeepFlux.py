import ROOT
from ROOT import  TFile, TTree
import os 


#  an example of copytree.C

#  I had trouble getting this to work on the latest versions of root
#  but didn't try hard to diagnose the problem
#  I run on a recent (c. 2024) version of root.

# updated and translated to python by HMS March 2026

# method todrop branches and do some minimal selection 

def trimManyBranchesKeepFlux(infile, outfile, reco_cut, truth_cut):   
    f = TFile.Open(infile,"READONLY")

    name = f.GetName()
    DATA = "Data" in name
    MC = "mc" in name
    T = f.Get("MasterAnaDev")
    if MC: TT = f.Get("Truth")
    TM = f.Get("Meta")


    #  Needed to oversome some limitation
    # T.SetMaxVirtualSize(size=1E9)
    # if MC: TT.SetMaxVirtualSize(size=2E9)
    # TM.SetMaxVirtualSize(size=1E9)


    #T.SetBranchStatus("mc_wgt_*",1)
    if MC: TT.SetBranchStatus("mc_wgt_*",1)

    #  deactivate select branches
    T.SetBranchStatus("lattice*",0)
    T.SetBranchStatus("Signal*",0)
    T.SetBranchStatus("overlay*",0)
    T.SetBranchStatus("odlattice*",0)
    T.SetBranchStatus("recoil_summed_energy*",0)
    T.SetBranchStatus("recoil_data_fraction*",0)
    T.SetBranchStatus("slice_hit_*",0)
    T.SetBranchStatus("recoil*time_limit*",0)
    T.SetBranchStatus("event_track_hit*",0) 
    T.SetBranchStatus("cluster_*",0)
    T.SetBranchStatus("EnergyPoints*",0)
    T.SetBranchStatus("VetoWall*",0)
    T.SetBranchStatus("part_response*",1)
    T.SetBranchStatus("part_response_total_recoil_passive_allNonMuonClusters_id",1)
    T.SetBranchStatus("part_response_total_recoil_passive_allNonMuonClusters_od",1)
    T.SetBranchStatus("*ichel*",0)
    if MC: TT.SetBranchStatus("*ichel*",0)
    T.SetBranchStatus("dEdX*",0)
    T.SetBranchStatus("ExtraEnergyClusters*",0)

    T.SetBranchStatus("prong_part*",0)
    T.SetBranchStatus("proton_prong*",0)
    T.SetBranchStatus("proton_track*",0)
    T.SetBranchStatus("seco_prot*",0)
    T.SetBranchStatus("sec_prot*",0)
    T.SetBranchStatus("iso_prong*",0)
    T.SetBranchStatus("gamma*",0)
    T.SetBranchStatus("pi0*",0)
    T.SetBranchStatus("disp*",0)
    T.SetBranchStatus("blob_nuefuzz*",0)
    T.SetBranchStatus("hadron_em*",0)
    T.SetBranchStatus("proton_em*",0)
    T.SetBranchStatus("phys_energy*",0)
    T.SetBranchStatus("recoil_energy_*vtx*",1)
    T.SetBranchStatus("clusters_found*",0)
    T.SetBranchStatus("number_clusters*",0)
    T.SetBranchStatus("shower_*",0)
    T.SetBranchStatus("calibE_*",0)
    T.SetBranchStatus("hadron_track_*",0)
    T.SetBranchStatus("nonvtx_iso*",0)
    T.SetBranchStatus("visE_*",0)

    T.SetBranchStatus("Signal*",0)
    T.SetBranchStatus("ConeEnergyVis",0)
    T.SetBranchStatus("ExtraEnergyVis",0)
    T.SetBranchStatus("Psi",0)

    #  One of the main neutron branches
    #  Notice I am adding back branches here in some cases
    #  after using a wildcard above
    T.SetBranchStatus("MasterAnaDev_Blob*",1)
    T.SetBranchStatus("MasterAnaDev_RecoPattern",1)
    T.SetBranchStatus("MasterAnaDev_MCEnergyFrac*",0)

    T.SetBranchStatus("MasterAnaDev_hadron*",0)
    T.SetBranchStatus("MasterAnaDev_sec_prot*",0)
    T.SetBranchStatus("MasterAnaDev_pi*",0)
    T.SetBranchStatus("MasterAnaDev_prot*",0)

    T.SetBranchStatus("MasterAnaDev_prot*",0)
    T.SetBranchStatus("MasterAnaDev_sys*",0)

    T.SetBranchStatus("numi*",0)
    if MC: TT.SetBranchStatus("numi*",0)
    T.SetBranchStatus("numi_pot*",1)
    if MC: TT.SetBranchStatus("numi_pot*",1)

    if MC: T.SetBranchStatus("truth_neutronInelast*",1)
    if MC: TT.SetBranchStatus("truth_neutronInelastic*",1)

    if MC:T.SetBranchStatus("truth_hadronReweight*",1)
    if MC: TT.SetBranchStatus("truth_hadronReweight*",1)

    # T.SetBranchStatus("truth_muon_track_cluster*",0)
    # if MC: TT.SetBranchStatus("truth_muon_track_cluster*",0)

    # T.SetBranchStatus("truth_fuzz*",0)
    # if MC: TT.SetBranchStatus("truth_fuzz*",0)


    # T.SetBranchStatus("truth_gamma*",0)
    # T.SetBranchStatus("truth_prot*",0)
    # T.SetBranchStatus("truth_pi*",0)
    # T.SetBranchStatus("truth_muon_off_track*",0)
    # if MC: TT.SetBranchStatus("truth_gamma*",0)
    # if MC: TT.SetBranchStatus("truth_prot*",0)
    # if MC: TT.SetBranchStatus("truth_pi*",0)
    # if MC: TT.SetBranchStatus("truth_muon_off_track*",0)

    T.SetBranchStatus("muon_track_cluster*",0)
    T.SetBranchStatus("muon_fuzz_per_plane_r150*",0)


    # T.SetBranchStatus("mc_fr*",0)
    # if MC: TT.SetBranchStatus("mc_fr*",0)
    

    # T.SetBranchStatus("latticeEnergyIndices",0)
    # T.SetBranchStatus("latticeNormEnergySums",0)
    # T.SetBranchStatus("latticeRelativeTimes",0)
    # T.SetBranchStatus("neutronlist*",0)
    # T.SetBranchStatus("neutronblob*",0)

    T.SetBranchStatus("muon_thetaX_allNodes",0)
    T.SetBranchStatus("muon_thetaY_allNodes",0)
    T.SetBranchStatus("muon_theta_allNodes",0)
    T.SetBranchStatus("muon_iso_blobs*",0)

    file =  TFile(outfile,"recreate")
    # T.SetTreeIndex(0)  if MC: TT.SetTreeIndex(0)  TM.SetTreeIndex(0)
    file.cd()
    print ("copying tree with cut ", reco_cut)
    newtree = T.CopyTree(reco_cut)
    if MC: newtruth = TT.CopyTree(truth_cut) 
    meta = TM.CloneTree()
    newtree.Write()
    if MC: newtruth.Write()
    meta.Write()
    #if MC:truth.Write()
    #meta.Write()
    #tree.Write()
    #if MC: truth.Print()
    meta.Scan()
    file.Write() #0,ROOT.TObject.kOverwrite)
    file.Close()

    # fLeaves().Remove(l1)
    # T.GetListOfLeaves().Remove(l2)
    # T.GetListOfLeaves().Remove(l3)
    # T.Write()

def test( ):
    infile = "/Users/schellma/data/public/Data/Playlist1N/MasterAnaDev_data_AnaTuple_run00020329_Playlist.root"
    reco_cut = "vtx[2] > 5000 && vtx[2] < 9000"
    truth_cut = "mc_vtx[2] > 5000 && mc_vtx[2] < 9000"
    dirname = os.path.dirname(infile)
    outdir = dirname + "_trimmed"
    if not os.path.exists(outdir):
        os.mkdir(outdir)
    #infile = "/Users/schellma/data/public/StandardMC/Playlist1N/MasterAnaDev_mc_AnaTuple_run00113270_Playlist.root"
    outfile = os.path.join(outdir, os.path.basename(infile).replace(".root","_trimmed.root"))
    print ("writing to ", outfile )
    trimManyBranchesKeepFlux(infile, outfile, reco_cut, truth_cut)

def loop(dirname, helicity=1):
    reco_cut = "vtx[2] > 5000 && vtx[2] < 9000 && isMinosMatchTrack && MasterAnaDev_nuHelicity == %d"%(helicity)
    truth_cut = "mc_vtx[2] > 5000 && mc_vtx[2] < 9000" 
    outdir = os.path.dirname(dirname) + "_trimmed2"
    if not os.path.exists(outdir):
        os.mkdir(outdir)
    for filename in os.listdir(dirname):
        if filename.endswith("Playlist.root"):
            print ("trimming ", filename)
            infile = os.path.join(dirname, filename)
            outfile = os.path.join(outdir, filename.replace(".root","_trimmed2.root"))
            trimManyBranchesKeepFlux(infile, outfile, reco_cut, truth_cut)

if __name__ == "__main__":



    #test()
    loop("/Users/schellma/data/public/Data/Playlist1N/",1)

    loop("/Users/schellma/data/public/StandardMC/Playlist1N/",1)
    



