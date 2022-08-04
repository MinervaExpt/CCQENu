New script that submits a job to the grid.   

This is intended for CCQEMAT, which has an executable a config file and a prescale

Your MAT distribution should be in the base directory ($BASEDIR) and the whole thing gets tarred up and sent.

On Unix, you need to 

```cp -r /minerva/app/users/schellma/NEWMAT/jsoncpp-build $BASEDIR # where BASEDIR is where MAT and MAT-MINERvA and CCQENu live```

Your executable should be in the run directory which is RELATIVE to $BASEDIR - ie CCQENu/make_hists or something similar. 

you then invoke `SubmitJobsToGrid_MAT.py` with your config and playlists and the results come back in a tagged subdirectory of `--outdir`

Here is an example how it works.  You can find this in file testbatch.sh

My whole MAT setup is in $APP/NEWMAT so that needs to go into the tarball.
The directory I run from is $APP/NEWMAT/CCQENu/make_hists so I set RUNDIR to that

```
export APP=/minerva/app/users/$USER
export SCRATCH=/pnfs/minerva/scratch/users/$USER
export BLUE=/minerva/data/users/$USER   

export BASEDIR=$APP/NEWMAT    #  YOU NEED TO CHANGE THIS TO WHERE YOUR MAT CODE IS !!!!!!!!! 

python $BASEDIR/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/test \
--basedir=$BASEDIR --rundir=CCQENu/make_hists --playlist=minervame5A --tag=test --mail \
--prescale=1 --config=testme --sample=QElike --exe=sidebands_v2 --setup=CCQENu/utilities/setup_batch_mat.sh \
--tmpdir=$BLUE/tmp --expected-lifetime=12h --memory=2000  #--debug --notimestamp 
```

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
  --exe=THEEXE          relative path from $CCQEMAT for the executable (CCQEMAT)
  --expected-lifetime=LIFETIME
                        job lifetime in format like 12h, 1d, 60m
```
