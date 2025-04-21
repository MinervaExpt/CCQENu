import os
import sys
import getopt
from PlotUtils import MnvH1D, MnvH2D
from ROOT import TFile

# This is a script to run transwarp based off RunTransWarp_antinu.py that comes
# with UnfoldUtils. It has been modified for use in my CCQENuMAT based 3D antinu
# analysis. 
# 
# It takes one argument at the command line if you're using hists from a single 
# file. If using hists from multiple files, that can be hardcoded in here (maybe
# will make it smarter in the future though). Goal is to run multiple transwarps
# for different permutations of input hists as desired.
# 
#   Noah Harvey Vaughan
#   vaughann@oregonstate.edu
#   noah.vaughan31@gmail.com
#   Oregon State University, 2025

samplestodo = [
    "QElike" #,
]
# should not need data
catstodo = [
    "qelike" #,
]

varstodo = [
    "pzmu"
]

DoPOTScale = True

def GetVarsListFromFile(rfile):
    varslist = []
    histkeys_list = rfile.GetListOfKeys()
    for histkey in histkeys_list:
        histname = histkey.GetName()
        if hist_name.find("___") == -1:
            continue
        var = hist_name.split("___")[3]
        varslist.append(var)
    return varslist
    

# TODO this needs to return something still.
def GetHistsFromFile(rfile, varname, fakedata=True, migration=True, POTScale = -1.):
    # Get the histograms from a file needed for study. Can set if you want to
    # use this file as fake data or for migration stuff, both default to true.
    # With my hist filling operation, the default value is really only valid for
    # a closure test or stat error test. A warp will require two separate files,
    # for which this operation will need to be used twice with the respective values set.
    # Also have the option to POT scale things at this step.

    found_fakedata, found_migration = False
    found_fakereco, found_faketruth = False
    found_migmatrix, found_migreco, found_migtruth = False

    fakedata_reco_hist,fakedata_truth_hist = MnvH1D()
    migration_matrix = MnvH2D()
    migration_reco_hist,migration_truth_hist = MnvH1D()


    histkeys_list = rfile.GetListOfKeys()
    for histkey in histkeys_list:
        hist = MnvH1D()
        tmp_name = ""
        hist_name = histkey.GetName()
        # Get rid of non-hist branches.
        if hist_name.find("___") == -1:
            continue
        parse = hist_name.split('___')

        # If not sample or category you're looking for, then don't do it
        if parse[1] not in samplestodo or parse[2] not in catstodo:
            continue
        if parse[3]!=varname:
            continue

        if fakedata:
            # tmp_name = "fakedata___"
            if parse[4]=="reconstructed":
                found_fakereco = True
                # tmp_name += "reconstructed___"+parse[3]
                # fakedata_reco_hist = rfile.Get(hist_name).Clone(tmp_name)
                fakedata_reco_hist = rfile.Get(hist_name).Clone()
                found_fakereco = True

                if POTScale>0.:
                    fakedata_reco_hist.Scale(POTScale)
                continue
            if parse[4]=="selected_truth":
                # tmp_name += "selected_truth___"+parse[3]
                # fakedata_truth_hist = rfile.Get(hist_name).Clone(tmp_name)
                fakedata_truth_hist = rfile.Get(hist_name).Clone()
                found_faketruth = True
                if POTScale>0.:
                    fakedata_truth_hist.Scale(POTScale)
                continue
        if migration:
            # tmp_name = "migration___"
            if parse[4]=="response_migration":
                # tmp_name += "migration_matrix___"+parse[3]
                # migration_matrix = rfile.Get(hist_name).Clone(tmp_name)
                migration_matrix = rfile.Get(hist_name).Clone()
                found_migmatrix = True
                fakedata_truth_hist = hist.Clone()
                # TODO need to POT scale this?
                continue
            if parse[4]=="reconstructed":
                # tmp_name += "migration_reco___"+parse[3]
                # migration_reco_hist = rfile.Get(hist_name).Clone(tmp_name)
                migration_reco_hist = rfile.Get(hist_name).Clone()
                found_migreco = True

                if POTScale>0.:
                    migration_reco_hist.Scale(POTScale)
                continue
            if parse[4]=="selected_truth":
                # tmp_name += "migration_truth___"+parse[3]
                # migration_truth_hist = rfile.Get(hist_name).Clone(tmp_name)
                migration_truth_hist = rfile.Get(hist_name).Clone()
                found_migtruth = True

                if POTScale>0.:
                    migration_truth_hist.Scale(POTScale)
                continue

        if found_fakereco and found_faketruth:
            found_fakedata = True
        if found_migreco and found_migtruth and found_migmatrix:
            found_migration = True
        
        if found_fakedata and fakedata and not migration:
            return fakedata_reco_hist, fakedata_truth_hist
        elif found_migration and migration and not fakedata:
            return migration_matrix, migration_reco_hist, migration_truth_hist
        elif fakedata and migration and found_fakedata and found_migration:
            return fakedata_reco_hist, fakedata_truth_hist, migration_matrix, migration_reco_hist, migration_truth_hist
    
    if migration and not found_migration:
        print("ERROR cannot find migration hists for the variable ",varname," from input file ", rfile.GetName())
        return -1, -1
    
    if fakedata and not found_fakedata:
        print("ERROR cannot find fake data hists for the variable ",varname," from input file ", rfile.GetName())
        return -1, -1, -1


def GetPOTScale(rfile):
    # Get the POT scale from a file

    h_pot = rfile.Get("POT_summary")
    dataPOT = h_pot.GetBinContent(1)
    mcPOTprescaled = h_pot.GetBinContent(2)
    POTScale = dataPOT / mcPOTprescaled
    print("POTScale: ",POTScale)
    return POTScale

# TODO figure out how this will fit in
def SumPlaylists():
    # Sum hists from all playlists. 
    # TODO should this be all hists in a set of input files or a subset of hists input here
    return 0


def main():
    # TOOD: Here's where the script will go
    if len(sys.argv) < 2:
        print("python3 RunTransWarp_CCQEMAT_antinu.py <fakedatafile>.root <optional_migrationfile>.root\n"\
        "OR\n"\
        "python3 RunTransWarp_CCQEMAT_antinu.py <warpfileconfig>.json")
        sys.exit()
    
    else:
        fakedata_file = sys.argv[1]
        migration_file = sys.argv[2]

    # Where the input root file will live
    base_dir = os.getenv("CCQEMAT")

    # where the output from transwarp will go
    output_basedir = os.path.join(os.getenv("OUTPUTLOC"),"transwarp")

    varslist = GetVarsListFromFile(fakedata_file)

    for varname in varslist:
        # input_histdict = {
        #     "fakedata_reco":MnvH1D(), 
        #     "fakedata_truth":MnvH1D(),
        #     "migration_matrix":MnvH2D(),
        #     "migration_reco":MnvH1D(),
        #     "migration_truth":MnvH1D()
        # }

        fakedata_POTScale, migration_POTScale = -1.0
        if DoPOTScale:
            fakedata_POTScale = GetPOTScale(fakedata_file)
            migration_POTScale = GetPOTScale(migration_file)

        fakedata_reco_hist,fakedata_truth_hist = GetHistsFromFile(fakedata_file, varname, True, False, fakedata_POTScale)
        migration_matrix,migration_reco_hist,migration_truth_hist = GetHistsFromFile(migration_file, varname, False, True, migration_POTScale)
        
        # Check that those hists actually are there. If they're not, skip to next variable in the list
        if -1 in [fakedata_reco_hist,fakedata_truth_hist,migration_matrix,migration_reco_hist,migration_truth_hist]:
            print("WARNING: missing a hist for variable ",varname,"\n\tskipping to next var..")
            continue

        # TODO: get info about the hists like number of bins to get an idea for the chi2 calculations
        num_dim = str(1)
        n_xbins = fakedata_reco_hist.GetNbinsX()
        n_ybins = 1 # default
        hist_dimname = fakedata_reco_hist.GetName().split("___")[0]
        if hist_dimname in ["h1D", "hHD"]:
            # This assumes you're using k1D or k1D_lite for a hyperdim hist
            num_dim = str(1)
        elif hist_dimname in ["h2D"]:
            num_dim = str(2)
            n_ybins = fakedata_reco_hist.GetNbinsY()
        
        nbins = n_xbins*n_ybins
        print("Number of bins for var ",varname, ": ", nbins)
        max_chi2 = 5*nbins
        step_chi2 = str(round(max_chi2/100))
        max_chi2 = str(step_chi2*100)
        print("max chi2: ", max_chi2,"\tstep_chi2: ",step_chi2)
        num_iter = "1,2,3,4,5,6,10,15,25"
        print("num_iter: ",num_iter)
        # Make a file with all the input histograms for TransWarp
        # TODO make this file name a bit more descriptive?
        inputhist_file_basename = "inputhists.root"
        inputhist_file_name= os.path.join(output_basedir, inputhist_file_basename)
        inputhist_outfile = TFile(inputhist_file_name, "RECREATE")
        inputhist_outfile.cd()
        fakedata_reco_hist.Write()
        fakedata_truth_hist.Write()
        migration_matrix.Write()
        migration_reco_hist.Write()
        migration_truth_hist.Write()
        inputhist_outfile.Close()

        # Now make the command:
        cmd = "../TransWarpExtraction -o "+output_file\
            + " --data_file "+inputhist_file_name \
            + " --data "+fakedata_reco_hist.GetName() \
            + " --data_truth_file "+inputhist_file_name \
            + " --data_truth "+fakedata_truth_hist.GetName() \
            + " --reco_file "+inputhist_file_name \
            + " --reco "+migration_reco_hist.GetName() \
            + " --truth_file "+inputhist_file_name \
            + " --truth "+migration_truth_hist.GetName() \
            + " --migration_file "+inputhist_file_name \
            + " --migration "+migration_matrix.GetName() \
            + " --num_dim "+num_dim \
            + " --num_uni "+num_uni \
            + " --num_iter "+num_iter \
            + " --max_chi2 "+max_chi2 \
            + " --step_chi2 "+step_chi2 
            #    + " --exclude_bin "






if __name__ == "__main__":
    main()



# This can be closure (same model for fake data and migration), stat (same as
# closure, but different data/MC ratios), or warp (different models)
studytype = "closure"

vars_todo = []
fakedata_model = "MnvTunev1"
migmatrix_model = "MnvTunev1"

# The way I fill histograms, I only need two files at a time.
fakedata_file = ""
migration_file = ""

# TOOD: automate this based off what's in a file?
# Fakedata reco, should be reconstructed MC, it will be varied
fakedatareco_hist = "h___QElike___qelike___recoil___reconstructed"
# Fakedata truth, should be the corresponding truth histo to the reco "fake data"
fakedatatruth_hist = "h___QElike___qelike___recoil___selected_truth"

# migration hists, should basically be the same as above, but come from a diff file
# TODO: should these be from the projections (e.g., "response_reconstructed") or the normal hists? Right now going with the normal hists (same names as above)
mcreco_hist = fakedatareco_hist
mctruth_hist = fakedatatruth_hist 
migmatrix_hist = "h___QElike___qelike___recoil___response_migration"

# POT for scaling the fake data
pot_hist_name = ""

# TODO: automate this by cycling over hists in a file?
# Figure out the number of dimensions based on input hists. Hyperdim hists are assumed to be k1D type
hist_parse = fakedatareco_hist.split("___")
hdim = hist_parse[0]
if hdim in ["h","hHD"]:
    num_dim = 1
elif hdim=="h2D":
    num_dim = 2   
# Figure out the variable you're doing
var = hist_parse[2]

num_iter = "1,2,3,4,5,6,10"

# TODO automate these based off the number of bins in the input hists?
num_uni = str(25)
max_chi2 = str(1000)
step_chi2 = str(10)

output_file_name = "transwarp_"+var+"_"+fakedata_model+"vs"+migmatrix_model+"_"+num_uni+"univs.root"

cmd = "../TransWarpExtraction -o "+output_file\
    + " --data_file "+dat_file \
    + " --data "+fakedatareco_hist \
    + " --data_truth_file "+dat_file \
    + " --data_truth "+fakedatatruth_hist \
    + " --reco_file "+mc_file \
    + " --reco "+mcreco_hist \
    + " --truth_file "+mc_file \
    + " --truth "+mctruth_hist \
    + " --migration_file "+migration_file \
    + " --migration "+migmatrix_hist \
    + " --num_dim "+num_dim \
    + " --num_uni "+num_uni \
    + " --num_iter "+num_iter \
    + " --max_chi2 "+max_chi2 \
    + " --step_chi2 "+step_chi2 
    #    + " --exclude_bin "










base_dir_prefix = os.path.join(os.getenv("HOME"),"data","UnfoldingStudies","MigrationMatrix")
variations = ["_CV","_piontune","_2p2h","_rpa","_default","_rpapiontune","_2p2hrpa"]
#variatons = ["_CV","rpa"]
#_infile = "Migration_MakeFlux-1_ApplyFlux-1_Multiplicity-0_CombinedPlaylists-me1A.root"
#_infile = "Merged_MigrationMatrix_optimized_minervame5A_6A_6B.root"
#target_dir = "/minerva/data/users/bashyal8/UnfoldingStudies/pzpt_unfolding/"
#target_dir = "/minerva/data/users/"+os.getenv("USER")+"/UnfoldingStudies"
target_dir = os.path.join(os.getenv("HOME"),"data","UnfoldingStudies_hms")
reco_hist = "h_q2_enu_qelike_reco"  #"h_pzmu_ptmu_qelike_reco"
truth_hist = "h_q2_enu_qelike_truth"#"h_pzmu_ptmu_qelike_truth"
migration_hist = "h_q2_enu_qelike_migration"#"h_pzmu_ptmu_qelike_migration"
_output_prefix = reco_hist.replace("qelike_reco","")
output_prefix = _output_prefix.replace("h","stat_universe")
#variation = variations[2]
_infile = "MigrationMatrix_enu.root"
num_dim = str(2)
num_uni = str(25)
num_iter = "1,2,3,4,5,6,10"
#num_iter = "20"
#num_iter = "1,3,4,5,10"
max_chi2 = str(1000)
step_chi2 = str(10)


#needed hists
##########
# --data --> Data to be unfolded
# --data_truth -->True Data Distribution
# --reco -->Reconstructed MC distribution
# --truth -->Truth MC distribution
# --migration -->Migration matrix for Reconstructed MC to True MC
#########

for variation in variations:
    output_file = target_dir+"/"+output_prefix+variation+"_"+num_uni+".root"
    dat_file = base_dir_prefix+variation+"/"+_infile
    mc_file = base_dir_prefix+variations[0]+"/"+_infile #should be 0 mostly....
    mc_file = base_dir_prefix+variations[0]+"/"+_infile #should be 0 mostly....
    migration_file = mc_file #I think migration matrix is only constructed from MC info...

    cmd = "../TransWarpExtraction -o "+output_file\
        + " --data_file "+dat_file \
        + " --data "+reco_hist \
        + " --data_truth_file "+dat_file \
        + " --data_truth "+truth_hist \
        + " --reco_file "+mc_file \
        + " --reco "+reco_hist \
        + " --truth_file "+mc_file \
        + " --truth "+truth_hist \
        + " --migration_file "+migration_file \
        + " --migration "+migration_hist \
        + " --num_dim "+num_dim \
        + " --num_uni "+num_uni \
        + " --num_iter "+num_iter \
        + " --max_chi2 "+max_chi2 \
        + " --step_chi2 "+step_chi2 
    #    + " --exclude_bin "

    print cmd

    os.system(cmd)
