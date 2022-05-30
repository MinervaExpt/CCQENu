import os,sys,time,datetime
from optparse import OptionParser
import datetime

###########################################################
#  Script: JobSubmission python script for submitting
#          analysis jobs to the grid
###########################################################

# HMS - modify to use dropbox and do cleaner tar

tmpdir = "/minerva/app/users/$USER/"

def timeform():
  now = datetime.datetime.now()
  timeFormat = "%Y%m%d%H%M%S"
  nowtime = now.strftime(timeFormat)
  return nowtime
  
# Write the command you used to run your analysis
def writeEventLoop(mywrapper,config,theoutdir,playlist,prescale):
    mywrapper.write("echo \"go to scratch dir and run it\"\n")
    mywrapper.write("cd $_CONDOR_SCRATCH_DIR\n")
    mywrapper.write("pwd;ls -lrt \n")
    mywrapper.write("echo \"check on weights\" $MPARAMFILESROOT;ls $MPARAMFILESROOT/data\n")
    #mywrapper.write("pwd;ls -lrt \n")
    mywrapper.write("export MYPLAYLIST="+opts.playlist+"\n")
    mywrapper.write("$CCQEMAT/sidebands_v2 $CCQEMAT/"+config+" "+prescale+" >& sidebands.log\n")
    mywrapper.write("echo \"run returned \" $?\n")
    mywrapper.write("ls -lrt\n")
    mywrapper.write("echo \"ifdh cp -D ./*.root "+theoutdir+"\"\n")
    mywrapper.write("ifdh cp -D ./*.root "+theoutdir+"\n")
    mywrapper.write("echo \"ifdh returned \" $?\n")
    mywrapper.write("echo \"ifdh cp -D sidebands.log "+theoutdir+"\"\n")
    mywrapper.write("ifdh cp -D sidebands.log "+theoutdir+"\n")
    mywrapper.write("echo \"ifdh returned \" $?\n")
    mywrapper.write("env | grep -v ups\n")
    
def writeSetups(mywrapper,basedir):
    
    mywrapper.write("cd $INPUT_TAR_DIR_LOCAL\n")
    mywrapper.write("echo \"in code directory\"\n")
    mywrapper.write("pwd\n")
    mywrapper.write("ls -lt \n")
    
    topdir = "$INPUT_TAR_DIR_LOCAL/" + basedir
    mywrapper.write("cd "+topdir+"\n")
    mywrapper.write("export WHEREIPUTMYCODE=$PWD\n")
    mywrapper.write("ls\n")
    mywrapper.write("echo \"set codelocation $WHEREIPUTMYCODE\";pwd; env|grep WHERE\n")
    mywrapper.write("ls -lt \n")
    #mywrapper.write("cd Ana/PlotUtils/cmt\n")
    #mywrapper.write("cmt config\n")

    #mywrapper.write("echo \"setup.sh\"; cat $WHEREIPUTMYCODE/opt/build/setup.sh\n")
    mywrapper.write("echo \"setup_batch.sh\"; cat $WHEREIPUTMYCODE/CCQENu/make_hists/setup_batch.sh\n")
    mywrapper.write("source $WHEREIPUTMYCODE/CCQENu/make_hists/setup_batch.sh\n")
    mywrapper.write("setup ifdhc\n")
    mywrapper.write("echo \"after setup_batch.sh $CCQEMAT\";pwd;env | grep MAT\n")
    #mywrapper.write("cd $CCQEMAT\n")
    #mywrapper.write("cd Ana/Minerva101/MAT_Tutorial\n")
    #mywrapper.write("echo Rint.Logon: ./rootlogon_grid.C > ./.rootrc\n")

# Define function to create tarball
def createTarball(tardir,tag,basedir):
    
    found = os.path.isfile("%s/myareatar_%s.tar.gz"%(tardir,tag))
    if(not found):
        #cmd = "tar -czf /minerva/app/users/$USER/myareatar_%s.tar.gz %s"%(tag,basedir)
        cmd = "tar --exclude={*.git,*.png,*.pdf,*.gif} -zcf  %s/myareatar_%s.tar.gz %s"%(tmpdir,tag,basedir)
        print ("Making tar",cmd)
        os.system(cmd)
        cmd2 = "cp %s/myareatar_%s.tar.gz %s/"%(tmpdir,tag,tardir)
        print ("Copying tar",cmd2)
        
        os.system(cmd2)
        return "myareatar_%s.tar.gz"%(tag)
# Define function to unpack tarball
def writeTarballProceedure(mywrapper,tag,basedir):
    print ("I will be making the tarball upacking with this version")
    print ("Path is",basedir)
    #mywrapper.write("source /cvmfs/minerva.opensciencegrid.org/minerva/software_releases/v22r1p1/setup.sh\n")
    mywrapper.write("cd $INPUT_TAR_DIR_LOCAL\n")
    #mywrapper.write("env\n")
    mywrapper.write("ls\n")
    #mywrapper.write("tar -xvzf myareatar_%s.tar.gz\n"%tag)
    #mywrapper.write("cd $CONDOR_DIR_INPUT\n")
    writeSetups(mywrapper,basedir)

def writeOptions(parser):
    print ("Now write options to the parser")
    # Directory to write output
    parser.add_option('--outdir', dest='outdir', help='Directory to write output to', default = "/pnfs/minerva/scratch/users/"+_user_+"/default_analysis_loc/")
    parser.add_option('--config', dest='config', help='json config file name', default = "test_v9")
    
    parser.add_option('--tardir', dest='tardir', help='Tarball location', default = "/pnfs/minerva/scratch/users/"+_user_+"/default_analysis_loc/")
    parser.add_option('--basedir', dest='basedir', help='Base directory for making tarball', default = "NONE")
    parser.add_option('--rundir', dest='rundir', help='relative path in basedir for the directory you run from, if different', default = ".")
    parser.add_option('--stage', dest='stage', help='Process type', default="NONE")
    parser.add_option('--sample', dest='sample', help='Sample type', default="NONE")
    parser.add_option('--playlist', dest='playlist', help='Playlist type', default="NONE")
    parser.add_option('--prescale', dest='prescale', help='Prescale MC by this factor (CCQEMAT)', default="1")
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
    print ("############################################")
    print ("You have opted to Get mails once the jobs are finished of failed.")
    print ("#############################################")

##############################################
#  TODO: Here I want to put the tag scheme...
##############################################
tag_name = str(opts.tag)
time_stamp = int(time.time())
if tag_name=="tag_":
    print ("YOU DIDNT SPECIFY ANY ANY TAG...SO I WILL USE MY OWN TAGGING SCHEME" )
    # You can add in your own tagging scheme
    tag_name += "default_" 

print ("Is everything fine till here*********")
# Add the time stamp to tag
if not opts.notimestamp:
    tag_name += timeform()
#    tag_name += str(time_stamp)

print ("Tag for this version is ",tag_name)
print ("******************************************************")

# This is the output directory after the job is finished
output_dir = "$CONDOR_DIR_HISTS/" 

theoutdir = os.path.join(opts.outdir,tag_name)
print ("output dir",theoutdir)
# Make outdir if not exist
if(not os.path.isdir(theoutdir)):
    print ("make a new output dir",theoutdir)
    os.makedirs(theoutdir)

memory = 2000

# Check the stage is valid or not
if opts.stage not in valid_stages:
    print (opts.stage,"Selected stage is not valid. Here are the valid options",valid_stages)
    sys.exit()

##############################################
#  Create wrapper
##############################################

wrapper_name = "%s_%s_wrapper_%s.sh"%(opts.stage,opts.playlist,tag_name)

mywrapper = open(wrapper_name,"w")
mywrapper.write("#!/bin/sh\n")
# Now create tarball
if (opts.sametar==False):
    tarname = createTarball(opts.tardir,tag_name,opts.basedir)
else:
    tarname = str(opts.tarfilename)
    if not os.path.exists(opts.tardir+opts.tarfilename):
        print ("Tar File "+opts.tardir+opts.tarfilename+" doesn't Exist!")
        sys.exit()
    #change the tag to the current one...
    cmd="cp "+opts.tardir+opts.tarfilename+" "+opts.tardir+"myareatar_"+tag_name+".tar.gz"
    os.system(cmd)

# This will unpack the tarball we just made above
writeTarballProceedure(mywrapper,tag_name,opts.basedir)

# Now the add the command to run event loop 
if(opts.stage=="eventLoop"):
    writeEventLoop(mywrapper,opts.config,theoutdir,opts.playlist,opts.prescale)

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
#cmd += "--cmtconfig "+gccstring+" " #Setup minerva soft release built with minerva configuration
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
cmd += "--tar_file_name dropbox://"+opts.tardir+"myareatar_"+tag_name+".tar.gz  --use-cvmfs-dropbox "
#cmd += "-i /cvmfs/minerva.opensciencegrid.org/minerva/software_releases/v22r1p1"+" "
cmd += "file://"+os.environ["PWD"]+"/"+wrapper_name
print (cmd)

os.system(cmd)

print ("Deleting the app area tar..... ")
os.system("rm  "+tmpdir+"myareatar_"+tag_name+".tar.gz")
print ("Sleeping" )

time.sleep(1)
