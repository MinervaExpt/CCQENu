export MYPLAYLIST=1O
export DATALOC=local
export PRESCALE=1
export TRACKS=1
export MYMODEL=MnvTunev2
export MYSAMPLE=QElike_2Track
../sidebands_v2 Nu_p8_run_2Track $PRESCALE
export MYSAMPLE=MichelSideBand_2Track
../sidebands_v2 Nu_p8_run_2Track $PRESCALE
export MYSAMPLE=BlobSideBand_2Track
../sidebands_v2 Nu_p8_run_2Track $PRESCALE
export MYSAMPLE=MicBlobSideBand_2Track
../sidebands_v2 Nu_p8_run_2Track $PRESCALE
rm Nu_p8_${MYPLAYLIST}_${MYMODEL}_2Track_${PRESCALE}.root
hadd Nu_p8_${MYPLAYLIST}_${MYMODEL}_2Track_${PRESCALE}.root v18_${MYPLAYLIST}_${MYMODEL}_*_${PRESCALE}.root