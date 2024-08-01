New script that submits a job to the grid.   

This is intended for CCQEMAT, which has an executable a config file and a prescale

Your MAT distribution should be in the base directory ($BASEDIR) and the whole thing gets tarred up and sent.

On Unix, you need to (ONCE)

```cp -r /exp/minerva/app/users/schellma/MNV9/jsoncpp-build $BASEDIR # where BASEDIR is where MAT and MAT-MINERvA and CCQENu live```

And at each session you need to 

```setup jobsub_client```  # and whatever you need to get root. 

Your executable should be in a subdirectory which is RELATIVE to `$BASEDIR` - ie `CCQENu/make_hists` or something similar. 

you then invoke `SubmitJobsToGrid_MAT.py` with your config and playlists and the results come back in a tagged subdirectory of `--outdir`

Here is an example how it works.  You can find this in file `testp4.sh`

My whole MAT setup is in `$APP/NEWMAT` so that needs to go into the tarball.
The directory I run the MAT from is `$APP/NEWMAT/CCQENu/make_hists` so I set RUNDIR to that

```
export APP=/exp/minerva/app/users/$USER
export SCRATCH=/pnfs/minerva/scratch/users/$USER
export BLUE=/exp/minerva/data/users/$USER   

export BASEDIR=$APP/MNV9    #  YOU NEED TO CHANGE THIS TO WHERE YOUR MAT CODE IS !!!!!!!!! 

python $BASEDIR/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/test \
 --basedir=$BASEDIR --rundir=CCQENu/make_hists --playlist=minervame5A --model=MnvTunev2 --tag=testP4 \
 --mail --prescale=1 --config=p4_test --exe=sidebands_v2 --sample=QElike --setup=CCQENu/utilities/setup_batch_mat9.sh \
 --tmpdir=$SCRATCH/tmp --expected-lifetime=24h --memory=3000   #--debug --notimestamp


```

`setup_batch_mat9.sh` is the setup script that runs on the remote node. This is for Alma9.  If you need to run on SL7, use the old `setup_batch_mat.sh`



You will want to measure the memory and time for a job, memory is pretty constant from playlist to playlist but expect to use time of about 5 x the 5A time for the longest.

The script bigsub.sh can make your submit file (like the above) into a full expt submit for AntiNeutrino. 

`./bigsub.sh testp4.sh `  

creates `bigtestp4.sh.sh`   

Here is the help file

`python SubmitJobsToGrid_MAT.py --help`

```Usage: SubmitJobsToGrid_MAT.py[opts]

Options:
  -h, --help            show this help message and exit
  --outdir=OUTDIR       Directory to write tagged output directory to
  --tardir=TARDIR       Tarball location
  --basedir=BASEDIRPATH
                        Base directory for making tarball (full path)
  --rundir=RUNDIR       relative path in basedir for the directory you run
                        from, if different
  --setup=SETUP         relative path in basedir to the setup script
  --config=CONFIG       relative path in rundir for json config file (CCQEMAT)
  --stage=STAGE         Process type
  --sample=SAMPLE       Sample type
  --playlist=PLAYLIST   Playlist type
  --playlist=PLAYLIST   Playlist type
  --model=MODEL         [OPTIONAL] Model tune type to set $MYMODEL for
                        MinervaModel. Defaults to MnvTunev1
  --prescale=PRESCALE   Prescale MC by this factor (CCQEMAT)
  --tag=TAG             Tag your release
  --mail                Want mail after job completion or failure
  --sametar             Recycle the same tar file for jobsubmission
  --tarfilename=TARFILENAME
                        Name of the tarfile you want to use
  --memory=MEMORY       memory request in MB
  --notimestamp         Flag to TURN OFF time stamp in the tag
  --debug               debug script locally so no ifdh
  --tmpdir=TMPDIR       temporary local directory to store tarfile during this
                        script
  --exe=THEEXE          relative path for the executable (CCQEMAT)
  --expected-lifetime=LIFETIME
                        job lifetime in format like 12h, 1d, 60m
```
