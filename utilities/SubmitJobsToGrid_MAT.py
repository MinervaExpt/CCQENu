import os,sys,time,datetime
from optparse import OptionParser
import datetime

###########################################################
#  Script: JobSubmission python script for submitting
#          analysis jobs to the grid
###########################################################

# HMS - modify to use dropbox and do cleaner tar
# June 2022

# make a time stamp in local time for jobs
def timeform():
  now = datetime.datetime.now()
  timeFormat = "%Y%m%d%H%M%S"
  nowtime = now.strftime(timeFormat)
  return nowtime
  
# write a line to the wrapper, make certain it is properly terminated
def writewrap(mywrapper,text):
  mywrapper.write("#cmd: \t%s\n"%(text))
  mywrapper.write("%s\n"%(text))
  
# Write the command you used to run your analysis

# this is for the tutorial, not recently tested
def writeEventLoop(mywrapper,outdir):
    writewrap(mywrapper,"echo Rint.Logon: ./rootlogon_grid.C > ./.rootrc\n")
    writewrap(mywrapper,"root -l -b load.C+ runEventLoop.C+\n")
    writewrap(mywrapper,"ifdh cp -D ./*.root "+outdir)

# this is for CCQEMAT
def writeCCQEMAT(mywrapper,opts,theoutdir,tag):
     
    writewrap(mywrapper,"echo \"go to scratch dir and run it\"\n")
    writewrap(mywrapper,"cd $_CONDOR_SCRATCH_DIR\n")
    # tell it where to find the code to run
    writewrap(mywrapper,"export CCQEMAT=$RUNDIR\n")
    writewrap(mywrapper,"echo \"check on weights\" $MPARAMFILESROOT\n")
    writewrap(mywrapper,"echo \" check on CCQEMAT\" $CCQEMAT")
    writewrap(mywrapper,"export MYPLAYLIST="+opts.playlist+"\n")
    writewrap(mywrapper,"export MYSAMPLE="+opts.sample+"\n")
    theexe = opts.theexe
    writewrap(mywrapper,os.path.join("time $RUNDIR",opts.theexe)+" "+os.path.join("$RUNDIR",opts.config)+" "+opts.prescale+" >& %s_%s_%s.log\n"%(os.path.basename(opts.theexe),opts.config,tag))
    writewrap(mywrapper,"echo \"run returned \" $?\n")
    writewrap(mywrapper,"ls -lrt\n")
    if not opts.debug:
        writewrap(mywrapper,"echo \"ifdh cp -D ./*.root "+theoutdir+"\"\n")
        writewrap(mywrapper,"ifdh cp -D ./*.root "+theoutdir+"\n")
        writewrap(mywrapper,"echo \"ifdh returned \" $?\n")
        writewrap(mywrapper,"echo \"ifdh cp -D sidebands_"+tag+".log "+theoutdir+"\"\n")
        writewrap(mywrapper,"ifdh cp -D sidebands_"+tag+".log "+theoutdir+" \n")
        writewrap(mywrapper,"echo \"ifdh returned \" $?\n")
    #writewrap(mywrapper,"env | grep -v ups\n")
    
# do generic setup of code

def writeSetups(mywrapper,basedirname,setup):
    
    writewrap(mywrapper,"cd $INPUT_TAR_DIR_LOCAL\n")
    writewrap(mywrapper,"echo \"in code directory\"\n")
    writewrap(mywrapper,"pwd\n")
    writewrap(mywrapper,"ls -lt \n")
    topdir = "$INPUT_TAR_DIR_LOCAL/" + basedirname
    writewrap(mywrapper,"cd "+topdir+"\n")
    writewrap(mywrapper,"export BASEDIR=$PWD\n")
    writewrap(mywrapper,"export RUNDIR=$BASEDIR/"+opts.rundir+"\n")
    writewrap(mywrapper,"ls\n")
    writewrap(mywrapper,"echo \"set codelocation $BASEDIR\";pwd\n")
    writewrap(mywrapper,"ls -lt \n")
    # on the remote node the path is shorter.
    setuppath =  os.path.join("$INPUT_TAR_DIR_LOCAL",basedirname,opts.setup)
    if not os.path.exists(os.path.join(opts.basedirpath,opts.setup)):
        print ("setup path ",setuppath," does not exist")
        sys.exit(1)
    writewrap(mywrapper,"echo \"setup\"; cat "+setuppath+"\n")
    writewrap(mywrapper,"source "+setuppath+" \n")
    #writewrap(mywrapper,"setup ifdhc\n")
    writewrap(mywrapper,"echo \"after setup\";pwd\n")
    

# Define function to create tarball
def createTarball(tmpdir,tardir,tag,basedirname):
    
    found = os.path.isfile("%s/myareatar_%s.tar.gz"%(tardir,tag))

    if(not found):
        #cmd = "tar -czf /minerva/app/users/$USER/myareatar_%s.tar.gz %s"%(tag,basedir)
        print (" in directory",os.getcwd())
        tarpath = os.path.join(tmpdir,"myareatar_%s.tar.gz"%(tag))
        cmd = "tar --exclude={*.git,*.png,*.pdf,*.gif} -zcf  %s ./%s"%(tarpath,basedirname)
        print ("Making tar",cmd)
        os.system(cmd)
       
        cmd2 = "cp %s %s/"%(tarpath,tardir)
        print ("Copying tar",cmd2)
        
        os.system(cmd2)
        return "myareatar_%s.tar.gz"%(tag)

# Define function to unpack tarball
# it is now unpacked for you but is in cvmfs which is readonly
def writeTarballProceedure(mywrapper,tag,basedir):
    print ("I will be making the tarball upacking with this version")
    print ("Path is",basedir)
    writewrap(mywrapper,"cd $INPUT_TAR_DIR_LOCAL\n")
    writewrap(mywrapper,"ls\n")
    

def writeOptions(parser):
    print ("Now write options to the parser")
    # Directory to write output
    parser.add_option('--outdir', dest='outdir', help='Directory to write tagged output directory to', default = "/pnfs/minerva/scratch/users/"+_user_+"/default_analysis_loc/")
    parser.add_option('--tardir', dest='tardir', help='Tarball location', default = "/pnfs/minerva/scratch/users/"+_user_+"/default_analysis_loc/")
    parser.add_option('--basedir', dest='basedirpath', help='Base directory for making tarball (full path)', default = "NONE")
    parser.add_option('--rundir', dest='rundir', help='relative path in basedir for the directory you run from, if different', default = ".")
    parser.add_option('--setup', dest='setup', help='relative path in basedir to the setup script', default = ".")
    parser.add_option('--config', dest='config', help='relative path in rundir for json config file (CCQEMAT)', default = "./test_v9")
    parser.add_option('--stage', dest='stage', help='Processing type [CCQEMAT or (future) EventLoop]', default="NONE")
    parser.add_option('--sample', dest='sample', help='[OPTIONAL] Sample type to set $MYSAMPLE when doing 1 sample/job otherwise you can still use a hardcoded list of samples ', default="QElike")
    parser.add_option('--playlist', dest='playlist', help='Playlist type', default="NONE")

    parser.add_option('--prescale', dest='prescale', help='Prescale MC by this factor (CCQEMAT)', default="1")
    ##########################################################################
    #  Options for making tar files....Basically you can make tarfiles 
    #######################################################################
    parser.add_option('--tag', dest='tag', help="Tag your release",default="tag_")
    parser.add_option('--mail',dest='mail',help="Want mail after job completion or failure",default=False,action="store_true")
    parser.add_option('--sametar',dest='sametar',help="Recycle the same tar file for jobsubmission",default=False,action="store_true")
    parser.add_option('--tarfilename',dest='tarfilename',help='Name of the tarfile you want to use',default="NA")
    parser.add_option('--memory',dest='memory',help='memory request in MB',default="2000")
    parser.add_option('--notimestamp',dest='notimestamp',help='Flag to TURN OFF time stamp in the tag',default=False,action="store_true")
    parser.add_option('--debug',dest='debug',help='debug script locally so no ifdh',default=False,action="store_true")
    parser.add_option('--tmpdir',dest='tmpdir',help='temporary local directory to store tarfile during this script',default=".")
    parser.add_option('--exe',dest='theexe',help='relative path for the executable (CCQEMAT)',default='$CCQEMAT/sidebands_v2')
    parser.add_option('--expected-lifetime',dest='lifetime',help='job lifetime in format like 12h, 1d, 60m',default='12h')

# Valid stages for the neutrinos (you can add more for your own analysis)
valid_stages=["eventLoop","CCQEMAT"]
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
    tag_name += "_"
    tag_name += timeform()
#    tag_name += str(time_stamp)

print ("Tag for this version is ",tag_name)
print ("******************************************************")

# This is the output directory after the job is finished
#output_dir = "$CONDOR_DIR_HISTS/"  (this doesn't work right now)
if(not os.path.exists(opts.outdir)):
    print ("Looks like opts.outdir doesn't exist",opts.outdir)
    sys.exit(1)
theoutdir = os.path.join(opts.outdir,opts.playlist+"_"+opts.sample+"_"+tag_name)
print ("output dir",theoutdir)
# Make outdir if not exist
if(not os.path.isdir(theoutdir) and not opts.debug):
    print ("make a new output dir",theoutdir)
    os.makedirs(theoutdir)

memory = opts.memory

# Check the stage is valid or not
if opts.stage not in valid_stages:
    print (opts.stage,"Selected stage is not valid. Here are the valid options",valid_stages)
    sys.exit()

##############################################
#  Create wrapper
##############################################

wrapper_name = "%s_%s_wrapper_%s.sh"%(opts.stage,opts.playlist,tag_name)

mywrapper = open(wrapper_name,"w")
mywrapper.write("#!/bin/sh\n") # don't wrap this one
# Now create tarball
print ("basedirpath",opts.basedirpath)
if not os.path.exists(opts.basedirpath):
    print ("--basedir seems not to exist", opts.basedirpath)
    sys.exit(1)
basedirpath=os.path.dirname(opts.basedirpath)
basedirname=os.path.basename(opts.basedirpath)

pathtoexe=os.path.join(opts.basedirpath,opts.rundir,opts.theexe)
print (" check the executable path structure",pathtoexe,os.path.exists(pathtoexe))
pathtoconfig=os.path.join(opts.basedirpath,opts.rundir,opts.config)+".json"
print (" check the configfile structure",pathtoconfig,os.path.exists(pathtoconfig))
if not (os.path.exists(pathtoconfig) and os.path.exists(pathtoexe)):
  print ("config or exe not where it should be in BASEDIR>RUNDIR>localpath")
  print ("BASEDIR=",opts.basedirpath)
  print ("RUNDIR=",os.path.join(opts.basedirpath,opts.rundir))
  sys.exit(1)
else:
  print ("config and exe seem to be in the right place relative to tarball")
if (not opts.debug):
    if (opts.sametar==False):
    # some tar voodoo to get a tarball that has the name of the directory the code is in but not the rest of the path.  Go into the directory above, tar up just that name.
        here = os.getenv("PWD")
        
        os.chdir(basedirpath)
        print (" move to directory",basedirpath,os.getcwd())
        if (not os.path.exists(opts.tmpdir)):
            print ("--tmpdir=",opts.tmpdir," seems not to exist, making it")
            os.makedirs(opts.tmpdir)
        tarname = createTarball(opts.tmpdir,opts.tardir,tag_name,basedirname)
        # and then go back to where we were.
        os.chdir(here)
        print (" move to directory",here,os.getcwd())
    else:
        tarname = str(opts.tarfilename)
        if not os.path.exists(opts.tardir+opts.tarfilename):
            print ("Tar File "+opts.tardir+opts.tarfilename+" doesn't Exist!")
            sys.exit()
    #change the tag to the current one...
        cmd="cp "+opts.tardir+opts.tarfilename+" "+opts.tardir+"myareatar_"+tag_name+".tar.gz"
        os.system(cmd)

# This will unpack the tarball we just made above
    writeTarballProceedure(mywrapper,tag_name,basedirname)

if (".json" in opts.config):
    print ("stripping .json from ",opts.config)
    opts.config = opts.config.replace(".json","")
    
# write an environment setup

writeSetups(mywrapper,basedirname,opts.setup)

# Now the add the command to run event loop
if(opts.stage=="eventLoop"):
    writeEventLoop(mywrapper,theoutdir)
if(opts.stage=="CCQEMAT"):
    writeCCQEMAT(mywrapper,opts,theoutdir,tag_name)


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
#cmd += "--OS sl7 " #Operating system #Not needed in SL7

if opts.mail:
    cmd += " -M " #this option to make decide if you want the mail or not
#cmd += "--subgroup=Nightly " #This is only for high priority jobs
cmd += " --resource-provides=usage_model=DEDICATED,OPPORTUNISTIC " # remove OFFSITE
# make a very complicated thing to tell it to use a singularity image
cmd += " --lines='+SingularityImage=\\\"/cvmfs/singularity.opensciencegrid.org/fermilab/fnal-wn-sl7:latest\\\"' "
cmd += " --role=Analysis "
cmd += " --expected-lifetime  " + opts.lifetime
cmd += " --memory "+str(memory)+"MB "
cmd += configstring+" " #the environments for the tunes to bee applied
#cmd += "-f "+opts.outdir+"/myareatar_"+tag_name+".tar.gz "
cmd += " --tar_file_name dropbox://"+opts.tardir+"myareatar_"+tag_name+".tar.gz  --use-cvmfs-dropbox "
#cmd += "-i /cvmfs/minerva.opensciencegrid.org/minerva/software_releases/v22r1p1"+" "
cmd += "file://"+os.environ["PWD"]+"/"+wrapper_name
print (cmd)


if not opts.debug:
    sf = open(wrapper_name.replace(".sh",".log"),'w')
    sf.write(cmd)
    #os.system(cmd)
    answer="failed"
    try:
        answer = os.popen(cmd).read()
        
    except:
        print ("could not submit")
    print ("answer was",answer)
    sf.write(answer)
    sf.close()
    print ("Deleting the app area tar..... ")
    localtar = os.path.join(opts.tmpdir,"myareatar_"+tag_name+".tar.gz")
    os.system("rm  "+localtar)
localscript = os.path.join(opts.tmpdir,wrapper_name)
os.system("cp "+wrapper_name+" "+ localscript)

    
print ("Sleeping" )

time.sleep(1)
