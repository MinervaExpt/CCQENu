# pipeline for cross section extraction

export MYPLAYLIST=5A
export PRESCALE=1
export DATALOC=local
export MYMODEL=MnvTunev2
export RUNJSON=v20_test
export MAINSAMPLE=QElike
export MYSAMPLE=QElike
export FITVAR="ptmu"
../sidebands_v2 ${RUNJSON} 1 >& qelike.log
export MYSAMPLE=TrackSideband  
../sidebands_v2 ${RUNJSON} 1 >& track.log
export MYSAMPLE=BlobSideband
../sidebands_v2 ${RUNJSON} 1 >& blob.log

python combine.py ${MYPLAYLIST}_${MYMODEL}_${MAINSAMPLE}_${RUNJSON}_1.root >& combine.log

export COMBINED=scaled_${MYPLAYLIST}_${MYMODEL}_${MAINSAMPLE}_${RUNJSON}_1

../MnvFitDriver FitAntiNu.json >& fit.log

export FITTED=${FITVAR}_Fit_${FITVAR}_${COMBINED} 

python ../fits/ApplyVariants.py ${FITTED}.root >& apply.log

python ../nu_extract/ExtractorClasses.py AntiNuCrossScaled.json >& cross.log






