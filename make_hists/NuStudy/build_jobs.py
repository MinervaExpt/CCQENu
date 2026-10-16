# build jobs

import os, sys

DEBUG=True
PRESCALE = os.getenv("PRESCALE")
RUNJSON = os.getenv("RUNJSON")
MYMODEL = os.getenv("MYMODEL")
FHCplaylists = ["1A","1B","1C","1D","1E","1F","1G","1L","1M","1N","1O","1P"]

FHCsamples = ["QElike","BlobSideBand","MichelSideBand","MicBlobSideBand"]

if DEBUG:
    PRESCALE=1
    MYMODEL="MnvTunev2"
    RUNJSON="Nu_p8_run"
    #FHCplaylists = ["1D","1E","1F","1G"]

for playlist in FHCplaylists:
    name = f"batch_{playlist}.sh" 
    f = open(name,'w')
    outdir = os.path.join(os.getenv("SCRATCH"),"p8",playlist)
    if not os.path.exists(outdir):
        os.path.mkdir(outdir)

    for sample in FHCsamples:
        for tracks in range(1,3):
            f.write(f"export MYPLAYLIST={playlist}\n")
            f.write(f"export MYSAMPLE={sample}_{tracks}Track\n")
            f.write(f"export PRESCALE={PRESCALE}\n")
            f.write(f"export MYMODEL={MYMODEL}\n")
            f.write(f"export RUNJSON={RUNJSON}\n")
            f.write(f"export TRACKS={tracks}\n")
            
            command = "python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/p8/${MYPLAYLIST} \
    --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=${MYPLAYLIST} --model=MnvTunev2 --tag=p8-$MYPLAYLIST-${MYSAMPLE} \
    --prescale=${PRESCALE} --config=NuStudy/${RUNJSON} --exe=sidebands_v2 --sample=${MYSAMPLE} --setup=CCQENu/utilities/setup_batch_al9_proto.sh \
    --tmpdir=/exp/minerva/data/users/$USER/tmp --expected-lifetime=36h --memory=2000 \n"

            f.write(command)
    f.close()
