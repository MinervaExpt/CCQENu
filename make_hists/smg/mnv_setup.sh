# unix version


export CVSROOT=minervacvs@cdcvs.fnal.gov:/cvs/mnvsoft

#source /cvmfs/fermilab.opensciencegrid.org/products/common/etc/setups
#setup cmake v3_14_3 -z /cvmfs/larsoft.opensciencegrid.org/products
#setup root v6_16_00 -q e17:prof -z /cvmfs/larsoft.opensciencegrid.org/products
#setup python v3_7_2 -z /cvmfs/larsoft.opensciencegrid.org/products
#setup gdb  v8_2_1 -z /cvmfs/larsoft.opensciencegrid.org/products

source /cvmfs/minerva.opensciencegrid.org/minerva/hep_hpc_products/setups
setup root v6_10_04d -q e14:prof
setup cmake v3_7_1

#source /home/physics/gilligas/conda.sh

export WHEREIPUTMYCODE=/minerva/app/users/$USER/minerva
source $WHEREIPUTMYCODE/opt/build/setup.sh

export JSONCPP_DIR=/minerva/app/users/$USER/LocalApps/jsoncpp-build

export CCQEMAT=$WHEREIPUTMYCODE/CCQENu/make_hists

#export DYLD_LIBRARY_PATH=${PLOTUTILSROOT}

export THEDATA=/minerva/data/ME/MuonKludge_ProtonLLR_UpdatedNeutron
