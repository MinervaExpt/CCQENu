# pipeline for cross section extraction

# export MYPLAYLIST=1O
# export PRESCALE=1
# export DATALOC=local
# export MYMODEL=MnvTunev2
# export RUNJSON=Nu_p8_run

# export FITVAR="ptmu"
# export TRACKS=$1
# export MAINSAMPLE=QElike

export TRACKS=$1

# export MYSAMPLE=QElike_${TRACKS}Track
# ../sidebands_v2 ${RUNJSON} $PRESCALE >&qelike${TRACKS}.log
# export MYSAMPLE=MichelSideBand_${TRACKS}Track
# ../sidebands_v2 ${RUNJSON} $PRESCALE >&michel${TRACKS}.log
# export MYSAMPLE=BlobSideBand_${TRACKS}Track
# ../sidebands_v2 ${RUNJSON} $PRESCALE >&blob${TRACKS}.log
# export MYSAMPLE=MicBlobSideBand_${TRACKS}Track
# ../sidebands_v2 ${RUNJSON} $PRESCALE >&mic${TRACKS}.log

# this actually scales the MC and does not do the hadd

python combine.py v3_${MYPLAYLIST}_${MYMODEL}_${MAINSAMPLE}_${TRACKS}Track_${RUNJSON}_${PRESCALE}.root >& combine${TRACKS}_P${VERSION}.log

if [ $? -ne 0 ]; then
    echo "combine.py failed"
    exit 1
fi

export CCQEDIR=$PWD

#${CCQEMAT}/ccqemadd scaled_1O_${MYMODEL}_${MAINSAMPLE}_${TRACKS}Track_${RUNJSON}_${PRESCALE}.root ${CCQEDIR}/scaled/scaled_*_${MYMODEL}_All_${TRACKS}Track_${RUNJSON}_${PRESCALE}.root

# then hadd to make the full samples. 

ln -s scaled/* .

export COMBINED=scaled_v3_${MYPLAYLIST}_${MYMODEL}_All_${TRACKS}Track_${RUNJSON}_${PRESCALE}


#export COMBINED=scaled/scaled_v3_${MYPLAYLIST}_${MYMODEL}_${MAINSAMPLE}_${TRACKS}Track_${RUNJSON}_${PRESCALE}
echo $COMBINED

if [ ! -f ${COMBINED}.root ]; then
    echo "Combined file ${COMBINED}.root does not exist"
    exit 1
fi

../MnvFitDriver Fit_Nu.json >& fit${TRACKS}_P${VERSION}.log

status=$?

if [ $status -ne 129 ]; then
    echo "MnvFitDriver failed " $status
    exit 1
fi

export FITTED=${FITVAR}_Fit_${FITVAR}_${COMBINED} 

python ../fits/ApplyVariants.py ${FITTED}.root >& apply${TRACKS}_P${VERSION}.log

#python ../nu_extract/ExtractorClasses.py AntiNuCrossScaled.json >& cross.log






