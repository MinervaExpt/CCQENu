# build jobs

import os, sys

DEBUG=True
PRESCALE = os.getenv("PRESCALE")
RUNJSON = os.getenv("RUNJSON")
MYMODEL = os.getenv("MYMODEL")
VERSION = os.getenv("VERSION")
RHCplaylists = ["5A","6A","6B","6C","6D","6E","6F","6G","6H","6I","6J"]

RHCsamples = ["QElike","BlobSideBand","TrackSideBand"]


HOME = os.getenv("HOME")
if DEBUG:
    PRESCALE=1
    MYMODEL="MnvTunev2"
    #RHCplaylists=["5A","6A"]
    RUNJSON=f"AntiNu_run"
    #RHCplaylists = ["1D","1E","1F","1G"]

for sample in RHCsamples:
    name = f"batch_{sample}_{RUNJSON}_P{VERSION}.sh" 
    f = open(name,'w')    
    for playlist in RHCplaylists:
        outdir = os.path.join(os.getenv("SCRATCH"),"P"+VERSION,playlist)
        if not os.path.exists(outdir) and "/Users" not in HOME:
            os.mkdir(outdir)  
        name = f"batch_{sample}_{RUNJSON}_P{VERSION}.sh" 
        
        f.write(f"export MYPLAYLIST={playlist}\n")
        f.write(f"export MYSAMPLE={sample}\n")
        f.write(f"export PRESCALE={PRESCALE}\n")
        f.write(f"export MYMODEL={MYMODEL}\n")
        f.write(f"export RUNJSON={RUNJSON}\n")
        f.write(f"export TRACKS=1\n") # not used here but required for Nu
        f.write(f"export VERSION={VERSION}\n")
        
        command = "python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir=$SCRATCH/${VERSION}/${MYPLAYLIST} \
--basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist=${MYPLAYLIST} --model=MnvTunev2 --tag=P${VERSION}-${MYPLAYLIST}-${MYSAMPLE} \
--prescale=${PRESCALE}  --config=AntiNuStudy/${RUNJSON} --exe=sidebands_v2 --sample=${MYSAMPLE} --setup=CCQENu/utilities/setup_batch_al9_proto.sh \
--tmpdir=/exp/minerva/data/users/$USER/tmp --expected-lifetime=36h --memory=2000 \n"

        f.write(command)
    f.close()
