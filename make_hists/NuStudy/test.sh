# pipeline for cross section extraction

if [ $# -ne 1 ]; then
    echo "Usage: $0 <number of tracks>"
    exit 1
fi
export MYPLAYLIST=1O
export PRESCALE=1
export DATALOC=local
export VERSION=8
export MYMODEL=MnvTunev2
export RUNJSON=Nu_p${VERSION}_run
export MAINSAMPLE=All
export FITVAR="ptmu"
export TRACKS=$1


# these happen using batch

#export MYSAMPLE=QElike
export MYSAMPLE=QElike_${TRACKS}Track
../sidebands_v3 ${RUNJSON} $PRESCALE >&qelike${TRACKS}.log &
export MYSAMPLE=MichelSideBand_${TRACKS}Track
../sidebands_v3 ${RUNJSON} $PRESCALE >&michel${TRACKS}.log &
export MYSAMPLE=BlobSideBand_${TRACKS}Track
../sidebands_v3 ${RUNJSON} $PRESCALE >&blob${TRACKS}.log &
export MYSAMPLE=MicBlobSideBand_${TRACKS}Track
../sidebands_v3 ${RUNJSON} $PRESCALE >&mic${TRACKS}.log &

 # this actually scales the MC and does not do the hadd
