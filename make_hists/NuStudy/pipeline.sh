# pipeline for cross section extraction

export MYPLAYLIST=1O
export PRESCALE=10
export DATALOC=local
export MYMODEL=MnvTunev2
export RUNJSON=Nu_p8_test
export MAINSAMPLE=QElike
export FITVAR="ptmu"
export TRACKS=$1


export MYSAMPLE=QElike
export MYSAMPLE=QElike_${TRACKS}Track
../sidebands_v2 ${RUNJSON} $PRESCALE >&qelike${TRACKS}.log
export MYSAMPLE=MichelSideBand_${TRACKS}Track
../sidebands_v2 ${RUNJSON} $PRESCALE >&michel${TRACKS}.log
export MYSAMPLE=BlobSideBand_${TRACKS}Track
../sidebands_v2 ${RUNJSON} $PRESCALE >&blob${TRACKS}.log
export MYSAMPLE=MicBlobSideBand_${TRACKS}Track
../sidebands_v2 ${RUNJSON} $PRESCALE >&mic${TRACKS}.log

# this actually scales the MC and does not do the hadd

python combine.py ${MYPLAYLIST}_${MYMODEL}_${MAINSAMPLE}_${TRACKS}Track_${RUNJSON}_${PRESCALE}.root >& combine${TRACKS}.log

# then hadd to make the full samples. 

export COMBINED=scaled_${MYPLAYLIST}_${MYMODEL}_${MAINSAMPLE}_${TRACKS}Track_${RUNJSON}_${PRESCALE}

../MnvFitDriver Fit_Nu.json >& fit${TRACKS}.log

export FITTED${TRACKS}=${FITVAR}_Fit_${FITVAR}_${COMBINED} 

python ../fits/ApplyVariants.py ${FITTED}${TRACKS}.root >& apply${TRACKS}.log

#python ../nu_extract/ExtractorClasses.py AntiNuCrossScaled.json >& cross.log






