export CVSROOT=minervacvs@cdcvs.fnal.gov:/cvs/mnvsoft
export WHEREIPUTTHEMAT=$PWD
#export FLUX_FILE_DIR=$PWD/opt/etc
export FLUX_FILE_DIR=$BLUE/FluxFiles
export FLUX_FILE_DIR=/cvmfs/minerva.opensciencegrid.org/minerva/CentralizedFluxAndReweightFiles
#/MATFluxAndReweightFiles
mkdir -p opt/build && cd opt/build
cmake ../../MAT-MINERvA/bootstrap -DCMAKE_INSTALL_PREFIX=`pwd`/.. -DCMAKE_BUILD_TYPE=Release -DCMAKE_VERBOSE_MAKEFILE:BOOL=ON -DFLUX_FILE_DIR=$FLUX_FILE_DIR
#kinit #Fermilab Kerberos ticket for getting flux and reweight files
make install >& bad.log
cd $WHEREIPUTTHEMAT
