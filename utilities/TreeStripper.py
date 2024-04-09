################################################################################
# TreeStripper.py
# Noah Harvey Vaughan
# vaughann@oregonstate.edu
#
# 6 July 2020
#
# Adapted from Amit Bashyal's C++ code to strip ntuples of branches not used in
# analysis. Test this with one root file first and make sure each tree gets cop-
# -ied over, especially in the case of trees like Truth that get split up.
#
# It takes in single root files or playlists. It uses default branches hardcoded
# below or reads in a text file with a list of the branches in it that you want
# to keep.
#
# It creates a root file with '_strip.root' at the end of the original file name
# in the same location as the original. If given a playlist, it will make a new
# playlist with the '_strip.txt' at the end of the original name, put in the or-
# -iginal location.
################################################################################

import sys,os
import ROOT
import datetime
import socket
import json

# Will automatically be set to true if running on a minervagpvm
fnal = False
# Set to true to manually add some branches from DefaultCVUniverse.cxx
add_DefaultCV_random = False
if add_DefaultCV_random:
    defaultCVBranches = ['CCQENu_leptonE','muon_thetaX','muon_thetaY','CCQENu_minos_trk_p']

if len(sys.argv) < 2:
    print 'TreeStripper.py </path/to/data/file.root or /path/to/play/list.txt> <optional_goodbranches_list.txt>'
    sys.exit()

print '\n>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>TreeStripper.py<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<'
print 'Stripping unneeded branches from your Trees'
print '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'

#f = open(sys.argv[1])
#config = json.load(f)
#f.close()

#goodbranchesfile = config["goodbranchesfile"]
#oldplaylistfile = config["oldplaylistfile"]
#newplaylistdirectory = config["newplaylistdirectory"]
#newfiledirectory = config["newfiledirectory"]

now = datetime.datetime.now()
timestamp = '_'+str(now.strftime('%Y%m%d'))
datestriptxt = '_strip'+timestamp+'.txt'
datestriproot = '_strip'+timestamp+'.root'


# Reading a .txt file with a list of branches needed.
if len(sys.argv) == 3:
    goodbranchesfile = str(sys.argv[2])
    goodbranches = []
    counter = 0
    with open(goodbranchesfile, 'r') as f:
        for line in f:
            if len(line)==0:
                continue
            else:
                branch = line.replace('\n','')
                goodbranches.append(str(branch))
                counter += 1
        print counter, 'branches found in', os.path.basename(goodbranchesfile)
        f.close()
        # overlap = [branch for branch in defaultCVBranches if branch not in goodbranches]
        # print overlap
    if add_DefaultCV_random:
        print 'Manually adding',len(defaultCVBranches),'branches used in DefaultCVUniverse.cxx'
        goodbranches = list(set(goodbranches + defaultCVBranches))
        print 'Found',len(goodbranches),'branches to keep.'



# Default branches. Only in CCQENu trees, not Truth.
elif len(sys.argv) == 2:
    print 'Setting default good branches'
    goodbranches = ['nonvtx_iso_blobs_start_position_z_in_prong_sz', 'CCQENu_E', 'vtx_blobs_iso_distance_in_prong_sz', 'phys_n_dead_discr_pair_upstream_prim_track_proj', 'CCQENu_proton_score1','event_extra_track_PID_sz', 'CCQENu_nuHelicity','vtx_blobs_iso_energy_in_prong', 'vtx_blobs_iso_distance_in_prong', 'nonvtx_iso_blobs_start_position_z_in_prong', 'improved_michel_vertex_type', 'CCQENu_sec_protons_proton_scores', 'CCQENu_Q2','has_michel_category_sz', 'x', 'has_michel_ndigits', 'n_nonvtx_iso_blobs', 'CCQENu_proton_score', 'has_michel_energy', 'has_interaction_vertex', 'vtx', 'CCQENu_sec_protons_proton_scores1', 'has_michel_vertex_type', 'improved_michel_vertex_type_sz', 'event_extra_track_PID', 'has_michel_slice_energy', 'CCQENu_muon_T', 'CCQENu_leptonE', 'muon_theta', 'multiplicity', 'nonvtx_iso_blobs_energy', 'CCQENu_sec_protons_proton_scores1_sz', 'phys_n_dead_discr_pair', 'muon_theta_allNodes', 'has_michel_category', 'dis_id_energy', 'has_michel_vertex_type_sz']

cwd = os.getcwd()
# Sets up so it will write to data if on a minerva gpvm
if 'minervagpvm' in str(socket.gethostname()):
    fnaluser = os.environ.get('USER')
    datadir = os.path.join('/exp/minerva/data/users',fnaluser)
    if not os.path.exists(datadir):
        print 'ERROR: Cannot find your area:',datadir,' Exiting...'
        sys.exit()
    else:
        print 'Found your data area:', datadir
        fnal = True

oldplaylistfile = sys.argv[1]
infilelist = []
# Opening a single .root file.
if '.root' in str(oldplaylistfile):
    playlist = False
    print 'Added one file'
    infilelist.append(str(oldplaylistfile))
    playlistfiledir=''
# Adding the lines of a playlist to a list to open.
elif '.txt' in str(oldplaylistfile):
    playlist = True
    if not fnal:
        newplaylistdirectory = os.path.join(cwd,'strippedplaylists')
    else:
        newplaylistdirectory = os.path.join(datadir,'strippedplaylists')
    if not os.path.exists(newplaylistdirectory):
        os.makedirs(newplaylistdirectory)
    with open(str(oldplaylistfile), 'r') as f:
        counter = 0
        for line in f:
            line = line.replace('\n','')
            if line not in ['']:
                infilelist.append(str(line))
                counter += 1
        print 'Added',counter, 'files\n'
        f.close()
    oldbase = os.path.basename(oldplaylistfile)
    playlistfiledir = oldbase.replace('.txt','/')
    newplaylistfile = os.path.join(newplaylistdirectory,oldbase.replace('.txt',datestriptxt))
    if os.path.exists(newplaylistfile):
        print 'WARNING: The playlist', os.path.basename(newplaylistfile),'already exists. It will be overwritten...'
        open('newplaylistfile', 'w').close()
    print 'The new playlist will be ',newplaylistfile
else:
    print 'ERROR: Please enter a single file to strip as a .root file, or a playlist as a .txt file. \n'
    sys.exit()
# Setting up the directory for the stripped files to live in. Will automatically
# go to your /minerva/data area if on a minervagpvm
if not fnal:
    outpath = os.path.join(cwd,'strippedfiles',playlistfiledir)
else:
    outpath = os.path.join(datadir,'strippedfiles',playlistfiledir)

if not os.path.exists(outpath):
    os.makedirs(outpath)
print 'The stripped versions of the files will be here:'
print outpath

# Looping over each file
strippedfilelist = []
for file in infilelist:
    infile = ROOT.TFile.Open(file,'r')
    oldfilebasename = os.path.basename(file)
    print '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'
    print 'Opened the original file', oldfilebasename
# Preserves progeny of files
    if 'pnfs' in file:
        head,split,filename = file.partition('CCQENu_Anatuples/')
        filebasename = filename.replace('/','_')
    else:
        filebasename = oldfilebasename
    strippedbasename = filebasename.replace('.root',datestriproot)
    strippedname = os.path.join(outpath,strippedbasename)
    strippednameeol = strippedname + '\n'
    strippedfilelist.append(strippednameeol)
# I do it this way so playlist will have every file processed, even if it fails
    if playlist:
        with open(newplaylistfile, 'a') as f:
            f.write(strippednameeol)
            f.close()

    newfile = ROOT.TFile(strippedname, 'RECREATE')
    newfile.cd()
# Counters so trees that are split up don't get cloned more than once.
    truthcounter=0
    ccqecounter=0
    for key in infile.GetListOfKeys():
        ntuple = key.GetName()
        oldtree = infile.Get(ntuple)
# Stripping CCQENu. In there for both data and mc.
        if ntuple == 'CCQENu':
            if ccqecounter==0:
                print 'Stripping the CCQENu tree'
                for branch in oldtree.GetListOfBranches():
                    branch = branch.GetName()
                    if branch not in goodbranches:
                        oldtree.SetBranchStatus(str(branch),0)
                newtree = oldtree.CloneTree()
                newtree.Write()
                print 'Finished', ntuple
                ccqecounter+=1
                continue
            elif ccqecounter!=0:
                continue
# Stripping Truth, if it's in there. Usually split in two in the root files.
        if ntuple == 'Truth':
            if truthcounter==0:
                print 'Stripping the Truth tree'
                for branch in oldtree.GetListOfBranches():
                    branch = branch.GetName()
                    if branch not in goodbranches:
                        oldtree.SetBranchStatus(str(branch),0)
                newtree = oldtree.CloneTree()
                newtree.Write()
                print 'Finished', ntuple
                truthcounter+=1
                continue
            elif truthcounter!=0:
                continue
# Just need to copy Meta trees, no stripping needed
        if ntuple == 'Meta':
            newtree = oldtree.CloneTree()
            newtree.Write()
            print 'Copied over the Meta tree'
            continue
    print 'Finished', strippedbasename
    newfile.Close()
    infile.Close()

print '>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>The End!<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<'
