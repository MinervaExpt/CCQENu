# build jobs

import os, sys

DEBUG=True
PRESCALE = os.getenv("PRESCALE")
RUNJSON = os.getenv("RUNJSON")
MYMODEL = os.getenv("MYMODEL")
FHCplaylists = ["1A","1B","1C","1D","1F","1G","1L","1M","1N","1O","1P"]

FHCsamples = ["QElike","BlobSideband","MichelSideBand","MicBlobSideBand"]

if DEBUG:
    PRESCALE=1
    MYMODEL="MnvTunev2"
    RUNJSON="Nu_p8_run"
    FHCplaylists = ["1B"]

for playlist in FHCplaylists:
    name = f"batch_{playlist}.sh" 
    f = open(name,'w')

    for sample in FHCsamples:
        for tracks in range(1,3):
            f.write(f"export MYPLAYLIST={playlist}\n")
            f.write(f"export MYSAMPLE={sample}_{tracks}Track\n")
            f.write(f"export PRESCALE={PRESCALE}\n")
            f.write(f"export MYMODEL={MYMODEL}\n")
            f.write(f"export RUNJSON={RUNJSON}\n")
            f.write(f"export TRACKS={tracks}\n")
            
            command = "python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/p8 \
    --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=${MYPLAYLIST} --model=MnvTunev2 --tag=AL9-p8 \
    --prescale=${PRESCALE} --config=NuStudy/${RUNJSON} --exe=sidebands_v2 --sample=${MYSAMPLE} --setup=CCQENu/utilities/setup_batch_al9_proto.sh \
    --tmpdir=/exp/minerva/data/users/$USER/tmp --expected-lifetime=24h --memory=3000 \n"

            f.write(command)
    f.close()
