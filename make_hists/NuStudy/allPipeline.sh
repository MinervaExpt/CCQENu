# pipeline for cross section extraction

export MYPLAYLIST=1O
export PRESCALE=1
export DATALOC=local
export MYMODEL=MnvTunev2
export RUNJSON=Nu_p8_run
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

export CCQEDIR="/Users/schellma/Dropbox/ccqe/p8/nu"

python combine.py # ${MYPLAYLIST}_${MYMODEL}_${MAINSAMPLE}_${TRACKS}Track_${RUNJSON}_${PRESCALE}.root >& combine${TRACKS}.log

# then hadd to make the full samples. 

${CCQEMAT}/ccqemadd scaled_1A-1P_${MYMODEL}_${MAINSAMPLE}_${TRACKS}Track_${RUNJSON}_${PRESCALE}.root ${CCQEDIR}/scaled/scaled_*_${MYMODEL}_All_${TRACKS}Track_${RUNJSON}_${PRESCALE}.root

export COMBINED=scaled_1A-1P_${MYMODEL}_${MAINSAMPLE}_${TRACKS}Track_${RUNJSON}_${PRESCALE}

../MnvFitDriver Fit_Nu.json >& fit${TRACKS}.log

export FITTED=${FITVAR}_Fit_${FITVAR}_${COMBINED} 

python ../fits/ApplyVariants.py ${FITTED}.root >& apply${TRACKS}.log

#python ../nu_extract/ExtractorClasses.py AntiNuCrossScaled.json >& cross.log






