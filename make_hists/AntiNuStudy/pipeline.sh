# pipeline for cross section extraction

export MYPLAYLIST=5A
export PRESCALE=1
export DATALOC=local
export MYMODEL=MnvTunev2
export RUNJSON=AntiNu_run
export MAINSAMPLE=QElike
export MYSAMPLE=QElike
export FITVAR="ptmu"
../sidebands_v2 ${RUNJSON} 1 >& qelike_v2.log
export MYSAMPLE=TrackSideband  
../sidebands_v2 ${RUNJSON} 1 >& track_v2.log
export MYSAMPLE=BlobSideband
../sidebands_v2 ${RUNJSON} 1 >& blob_v2.log

python combine.py P6_${MYPLAYLIST}_${MYMODEL}_${MAINSAMPLE}_${RUNJSON}_1.root >& combine_v2_v2.log

export COMBINED=scaled_P6_${MYPLAYLIST}_${MYMODEL}_${MAINSAMPLE}_${RUNJSON}_1

../MnvFitDriver FitAntiNu.json >& fit_v2.log

export FITTED=${FITVAR}_Fit_${FITVAR}_${COMBINED} 

python ../fits/ApplyVariants.py ${FITTED}.root >& apply_v2.log

python ../nu_extract/ExtractorClasses.py AntiNuCrossScaled.json >& cross_v2.log






