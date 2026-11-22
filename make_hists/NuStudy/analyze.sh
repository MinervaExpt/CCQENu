# pipeline for cross section extraction

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

# export MYSAMPLE=QElike
# export MYSAMPLE=QElike_${TRACKS}Track
# ../sidebands_v2 ${RUNJSON} $PRESCALE >&qelike${TRACKS}.log
# export MYSAMPLE=MichelSideBand_${TRACKS}Track
# ../sidebands_v2 ${RUNJSON} $PRESCALE >&michel${TRACKS}.log
# export MYSAMPLE=BlobSideBand_${TRACKS}Track
# ../sidebands_v2 ${RUNJSON} $PRESCALE >&blob${TRACKS}.log
# export MYSAMPLE=MicBlobSideBand_${TRACKS}Track
# ../sidebands_v2 ${RUNJSON} $PRESCALE >&mic${TRACKS}.log

# this actually scales the MC and does not do the hadd

export CCQEDIR="/Users/schellma/Dropbox/ccqe/p${VERSION}/Nu"

echo "CCQEDIR is ${CCQEDIR}"
export HERE=$PWD
ls ${CCQEDIR}

cd ${CCQEDIR}
mkdir -p scaled
python $CCQEMAT/NuStudy/combine.py #${CCQEDIR}/${MYPLAYLIST}_${MYMODEL}_${MAINSAMPLE}_${TRACKS}Track_${RUNJSON}_${PRESCALE}.root >& ${HERE}/combine_p${VERSION}_${TRACKS}Track.log
if [ $? -ne 0 ]; then
    echo "combine.py failed"
    exit 1
fi
cd ${HERE}
# then hadd to make the full samples. 

${CCQEMAT}/ccqemadd scaled_1A-1P_${MYMODEL}_${MAINSAMPLE}_${TRACKS}Track_${RUNJSON}_${PRESCALE}.root ${CCQEDIR}/scaled/scaled_*_${MYMODEL}_All_${TRACKS}Track_${RUNJSON}_${PRESCALE}.root

if [ $? -ne 0 ]; then
    echo "ccqemadd failed"
    exit 1
fi
export COMBINED=scaled_1A-1P_${MYMODEL}_${MAINSAMPLE}_${TRACKS}Track_${RUNJSON}_${PRESCALE}

../MnvFitDriver Fit_Nu.json >& fit_${VERSION}_${TRACKS}.log

# fails in destructors, but still produces the fit file.  So don't fail on this.
# if [ $? -ne 0 ]; then
#     echo "MnvFitDriver failed"
#     exit 1
# fi
export FITTED=${FITVAR}_Fit_${FITVAR}_${COMBINED} 

python ../fits/ApplyVariants.py ${FITTED}.root >& apply${TRACKS}.log


# if [ $? -ne 0 ]; then
#     echo "ApplyVariants.py failed"
#     exit 1
# fi
#python ../nu_extract/ExtractorClasses.py AntiNuCrossScaled.json >& cross.log






