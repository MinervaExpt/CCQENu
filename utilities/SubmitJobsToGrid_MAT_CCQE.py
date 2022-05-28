import os,sys,time
from optparse import OptionParser
import datetime

###########################################################
#  Script: JobSubmission python script for submitting
#          analysis jobs to the grid
###########################################################

# HMS - modify to use dropbox and do cleaner tar

# Write the command you used to run your analysis
def writeEventLoop(mywrapper,outdir):
    mywrapper.write("./sidebands_v2 "+"config "\n")
    mywrapper.write("ifdh cp ./*.root "+outdir)
def writeSetups(mywrapper,basedir):
    topdir = "$CONDOR_DIR_INPUT" + basedir
    mywrapper.write("cd "+topdir+"\n")
    #mywrapper.write("cd Ana/PlotUtils/cmt\n")
    #mywrapper.write("cmt config\n")
    mywrapper.write("source setup.sh\n")
    mywrapper.write("cd "+topdir+"\n")
    #mywrapper.write("cd Ana/Minerva101/MAT_Tutorial\n")
    #mywrapper.write("echo Rint.Logon: ./rootlogon_grid.C > ./.rootrc\n")

# Define function to create tarball
def createTarball(tardir,tag,basedir):
    tmpdir = "/minerva/data/users/$USER/"
    found = os.path.isfile("%s/myareatar_%s.tar.gz"%(tardir,tag))
    if(not found):
        #cmd = "tar -czf /minerva/app/users/$USER/myareatar_%s.tar.gz %s"%(tag,basedir)
        cmd = "tar --exclude={*.git,*.root,*.png,*.pdf,*.gif} -zcf  %s/myareatar_%s.tar.gz %s"(tmpdir,tag,basedir)
        print "Making tar",cmd
        os.system(cmd)
        cmd2 = "cp /minerva/app/users/$USER/myareatar_%s.tar.gz %s/"%(tmpdir,tag,tardir)
        print "Copying tar",cmd2
        os.system(cmd2)
# Define function to unpack tarball
def writeTarballProceedure(mywrapper,tag,basedir):
    print "I will be making the tarball upacking with this version" 
    print "Path is",basedir
    #mywrapper.write("source /cvmfs/minerva.opensciencegrid.org/minerva/software_releases/v22r1p1/setup.sh\n")
    mywrapper.write("cd $CONDOR_DIR_INPUT\n")
    mywrapper.write("env\n")
    mywrapper.write("tar -xvzf myareatar_%s.tar.gz\n"%tag)
    mywrapper.write(
    mywrapper.write("cd $CONDOR_DIR_INPUT\n")
    writeSetups(mywrapper,basedir)

def writeOptions(parser):
    print "Now write options to the parser" 
    # Directory to write output
    parser.add_option('--outdir', dest='outdir', help='Directory to write output to', default = "/pnfs/minerva/scratch/users/"+_user_+"/default_analysis_loc/")
    parser.add_option('--tardir', dest='tardir', help='Tarball location', default = "/pnfs/minerva/scratch/users/"+_user_+"/default_analysis_loc/")
    parser.add_option('--basedir', dest='basedir', help='Base directory for making tarball', default = "NONE")
    parser.add_option('--stage', dest='stage', help='Process type', default="NONE")
    parser.add_option('--sample', dest='sample', help='Sample type', default="NONE")
    parser.add_option('--playlist', dest='playlist', help='Playlist type', default="NONE")
    ##########################################################################
    #  Options for making tar files....Basically you can make tarfiles 
    #######################################################################
    parser.add_option('--tag', dest='tag', help="Tag your release",default="tag_")
    parser.add_option('--mail',dest='mail',help="Want mail after job completion or failure",default=False,action="store_true")
    parser.add_option('--sametar',dest='sametar',help="Recycle the same tar file for jobsubmission",default=False,action="store_true")
    parser.add_option('--tarfilename',dest='tarfilename',help='Name of the tarfile you want to use',default="NA")
    parser.add_option('--notimestamp',dest='notimestamp',help='Flag to TURN OFF time stamp in the tag',default=False,action="store_true")

# Valid stages for the neutrinos (you can add more for your own analysis)
valid_stages=["eventLoop"]
avail_playlists=["minervame1A, minervame5A"]
# Get user's name
_user_ = os.getenv("USER")
usage = "usage: %prog[opts]" 
parser = OptionParser(usage=usage)
writeOptions(parser)
(opts,args) = parser.parse_args()

# Now print some information for user's selected options
if opts.mail:
    print "############################################" 
    print "You have opted to Get mails once the jobs are finished of failed." 
    print "#############################################" 

##############################################
#  TODO: Here I want to put the tag scheme...
##############################################
tag_name = str(opts.tag)
time_stamp = int(time.time())
if tag_name=="tag_":
    print "YOU DIDNT SPECIFY ANY ANY TAG...SO I WILL USE MY OWN TAGGING SCHEME" 
    # You can add in your own tagging scheme
    tag_name += "default_" 

print "Is everything fine till here*********" 
# Add the time stamp to tag
if not opts.notimestamp:
    tag_name += str(time_stamp)

print "Tag for this version is ",tag_name
print "******************************************************" 

# This is the output directory after the job is finished
output_dir = "$CONDOR_DIR_HISTS/" 

# Make outdir if not exist
if(not os.path.isdir(opts.outdir)):
    os.makedirs(opts.outdir)

memory = 2000

# Check the stage is valid or not
if opts.stage not in valid_stages:
    print opts.stage,"Selected stage is not valid. Here are the valid options",valid_stages
    sys.exit()

##############################################
#  Create wrapper
##############################################

wrapper_name = "%s_%s_wrapper_%s.sh"%(opts.stage,opts.playlist,tag_name)

mywrapper = open(wrapper_name,"w")
mywrapper.write("#!/bin/sh\n")
# Now create tarball
if (opts.sametar==False):
    createTarball(opts.tardir,tag_name,opts.basedir)
else:
    tarname = str(opts.tarfilename)
    if not os.path.exists(opts.tardir+opts.tarfilename):
        print "Tar File "+opts.tardir+opts.tarfilename+" doesn't Exist!"
        sys.exit()
    #change the tag to the current one...
    cmd="cp "+opts.tardir+opts.tarfilename+" "+opts.outdir+"myareatar_"+tag_name+".tar.gz"
    os.system(cmd)

# This will unpack the tarball we just made above
writeTarballProceedure(mywrapper,tag_name,opts.basedir)

# Now the add the command to run event loop 
if(opts.stage=="eventLoop"):
    writeEventLoop(mywrapper,opts.outdir)

mywrapper.close()

# Making the wrapper we just created readable, writable and executable by everyone
os.system("chmod 777 %s"%(wrapper_name))

# TODO: not sure if this is needed
configstring = "" 
# Get gcc release
gccstring = "x86_64-slc7-gcc49-opt" 
# Now add the execute command
cmd = "" 
cmd += "jobsub_submit --group minerva " #Group of experiment
cmd += "--cmtconfig "+gccstring+" " #Setup minerva soft release built with minerva configuration
cmd += "--OS sl7 " #Operating system #Not needed in SL7

if opts.mail:
    cmd += "-M " #this option to make decide if you want the mail or not
#cmd += "--subgroup=Nightly " #This is only for high priority jobs
cmd += "--resource-provides=usage_model=DEDICATED,OPPORTUNISTIC " 
cmd += "--role=Analysis " 
cmd += "--expected-lifetime 12h " 
cmd += "--memory "+str(memory)+"MB " 
cmd += configstring+" " #the environments for the tunes to bee applied
#cmd += "-f "+opts.outdir+"/myareatar_"+tag_name+".tar.gz "
cmd += "--tar_file_name dropbox://"+opts.tardir+opts.tarfilename" --use-cvmfs-dropbox"
cmd += "-i /cvmfs/minerva.opensciencegrid.org/minerva/software_releases/v22r1p1"+" " 
cmd += "file://"+os.environ["PWD"]+"/"+wrapper_name
print cmd

os.system(cmd)

print "Deleting the app area tar..... " 
os.system("rm -rf /minerva/app/users/$USER/myareatar_"+tag_name+".tar.gz")
print "Sleeping" 

time.sleep(1)
