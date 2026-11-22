# build jobs

import os, sys
SCRATCH = os.getenv("SCRATCH")
DEBUG=True
PRESCALE = os.getenv("PRESCALE")
RUNJSON = os.getenv("RUNJSON")
MYMODEL = os.getenv("MYMODEL")
VERSION = sys.argv[1] if len(sys.argv) > 1 else "9"   

FHCplaylists = ["1A","1B","1C","1D","1E","1F","1G","1L","1M","1N","1O","1P"]

FHCsamples = ["QElike","BlobSideBand","MichelSideBand","MicBlobSideBand"]

if DEBUG:
    #VERSION = "9"
    PRESCALE=1
    #MYMODEL="MnvTunev2"
    RUNJSON=f"Nu_p{VERSION}_run"
    #FHCplaylists = ["1A","1B","1C","1D"]
    #FHCplaylists = ["1D","1E","1F","1G"]

for playlist in FHCplaylists:
    name = f"batch_p{VERSION}_{playlist}_{RUNJSON}.sh" 
    f = open(name,'w')
    outdir = os.path.join(os.getenv("SCRATCH"),f"P{VERSION}",playlist)
    if not os.path.exists(outdir):
        os.mkdir(outdir)

    for sample in FHCsamples:
        for tracks in range(1,3):
            mysample = f"{sample}_{tracks}Track"
            f.write(f"export MYPLAYLIST={playlist}\n")
            f.write(f"export MYSAMPLE={sample}_{tracks}Track\n")
            f.write(f"export PRESCALE={PRESCALE}\n")
            f.write(f"export MYMODEL={MYMODEL}\n")
            f.write(f"export RUNJSON={RUNJSON}\n")
            f.write(f"export TRACKS={tracks}\n")
            f.write(f"export VERSION={VERSION}\n")
            
            command = f"python $WHEREIPUTMYCODE/CCQENu/utilities/SubmitJobsToGrid_MAT.py --stage=CCQEMAT --outdir={SCRATCH}/P{VERSION}/{playlist} \
    --basedir=$WHEREIPUTMYCODE --rundir=CCQENu/make_hists --playlist={playlist} --model=MnvTunev2 --tag=P{VERSION}-{playlist}-{mysample} \
    --prescale={PRESCALE} --config=NuStudy/{RUNJSON} --exe=sidebands_v3 --sample={sample}_{tracks}Track --setup=CCQENu/utilities/setup_batch_al9_proto.sh \
    --tmpdir=/exp/minerva/data/users/$USER/tmp --expected-lifetime=36h --memory=2000 \n"

            f.write(command)
    f.close()
