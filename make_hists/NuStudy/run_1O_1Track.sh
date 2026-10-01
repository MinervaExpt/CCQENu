export MYPLAYLIST=1O
export DATALOC=local
export PRESCALE=1
export TRACKS=1
export MYMODEL=MnvTunev2
export MYSAMPLE=QElike_1Track
../sidebands_v2 Nu_p8_run_1Track $PRESCALE 
export MYSAMPLE=MichelSideBand_1Track
../sidebands_v2 Nu_p8_run_1Track $PRESCALE 
export MYSAMPLE=BlobSideBand_1Track
../sidebands_v2 Nu_p8_run_1Track $PRESCALE 
export MYSAMPLE=MicBlobSideBand_1Track
../sidebands_v2 Nu_p8_run_1Track $PRESCALE
rm Nu_p8_${MYPLAYLIST}_${MYMODEL}_1Track_${PRESCALE}.root
hadd Nu_p8_${MYPLAYLIST}_${MYMODEL}_1Track_${PRESCALE}.root v18_${MYPLAYLIST}_${MYMODEL}_*_${PRESCALE}.root