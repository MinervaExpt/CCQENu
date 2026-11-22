# pipeline for cross section extraction

export MYPLAYLIST=5A
export PRESCALE=1
export DATALOC=local
export MYMODEL=MnvTunev2
export RUNJSON=AntiNu_run
export MAINSAMPLE=QElike
export MYSAMPLE=QElike
export FITVAR="ptmu"
export VERSION=9
# ../sidebands_v3 ${RUNJSON} 1 >& qelike_v3_P${VERSION}.log
# export MYSAMPLE=TrackSideband  
# ../sidebands_v3 ${RUNJSON} 1 >& track_v3_P${VERSION}.log
# export MYSAMPLE=BlobSideband
# ../sidebands_v3 ${RUNJSON} 1 >& blob_v3_P${VERSION}.log
export CCQEDIR=$HOME/Dropbox/ccqe/P9/AntiNu
cd $CCQEDIR

export EXAMPLE=P${VERSION}_${MYPLAYLIST}_${MYMODEL}_${MYSAMPLE}_${RUNJSON}_1.root

python $CCQEMAT/AntiNuStudy/combine.py P${VERSION}_${MYPLAYLIST}_${MYMODEL}_${MAINSAMPLE}_${RUNJSON}_1.root >& combine_v3_P${VERSION}.log

cd $CCQEMAT/AntiNuStudy

export COMBINED=scaled_P${VERSION}_5A-6I_${MYMODEL}_${MAINSAMPLE}_${RUNJSON}_${PRESCALE}

#scaled_P9_5A_MnvTunev2_QElike_AntiNu_run_1.root
${CCQEMAT}/ccqemadd $COMBINED.root ${CCQEDIR}/scaled_P${VERSION}_*_${MYMODEL}_${MAINSAMPLE}_${RUNJSON}_${PRESCALE}.root

echo "Now do the fit"

../MnvFitDriver FitAntiNu.json >& fit_v3_P${VERSION}.log

export FITTED=${FITVAR}_Fit_${FITVAR}_${COMBINED} 

echo "Now do variants"

python ../fits/ApplyVariants.py ${FITTED}.root >& apply_v3_P${VERSION}.log

#ln -s AntiNuCrossScaled.json v3_AntiNuCrossScaled.json

echo "Now do the cross section"

python ../nu_extract/ExtractorClasses.py P${VERSION}_AntiNuCrossScaled.json >& cross_v3_P${VERSION}.log






