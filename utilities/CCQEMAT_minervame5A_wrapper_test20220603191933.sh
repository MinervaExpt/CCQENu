#!/bin/sh
#cmd: 	cd $INPUT_TAR_DIR_LOCAL

cd $INPUT_TAR_DIR_LOCAL

#cmd: 	ls

ls

#cmd: 	cd $INPUT_TAR_DIR_LOCAL

cd $INPUT_TAR_DIR_LOCAL

#cmd: 	echo "in code directory"

echo "in code directory"

#cmd: 	pwd

pwd

#cmd: 	ls -lt 

ls -lt 

#cmd: 	cd $INPUT_TAR_DIR_LOCAL/TOPMAT

cd $INPUT_TAR_DIR_LOCAL/TOPMAT

#cmd: 	export BASEDIR=$PWD

export BASEDIR=$PWD

#cmd: 	export RUNDIR=$BASEDIR/CCQENu/make_hists

export RUNDIR=$BASEDIR/CCQENu/make_hists

#cmd: 	ls

ls

#cmd: 	echo "set codelocation $BASEDIR";pwd

echo "set codelocation $BASEDIR";pwd

#cmd: 	ls -lt 

ls -lt 

#cmd: 	echo "setup"; cat $INPUT_TAR_DIR_LOCAL/TOPMAT/CCQENu/utilities/setup_batch_osx.sh

echo "setup"; cat $INPUT_TAR_DIR_LOCAL/TOPMAT/CCQENu/utilities/setup_batch_osx.sh

#cmd: 	source $INPUT_TAR_DIR_LOCAL/TOPMAT/CCQENu/utilities/setup_batch_osx.sh 

source $INPUT_TAR_DIR_LOCAL/TOPMAT/CCQENu/utilities/setup_batch_osx.sh 

#cmd: 	setup ifdhc

setup ifdhc

#cmd: 	echo "after setup";pwd

echo "after setup";pwd

#cmd: 	echo "go to scratch dir and run it"

echo "go to scratch dir and run it"

#cmd: 	cd $_CONDOR_SCRATCH_DIR

cd $_CONDOR_SCRATCH_DIR

#cmd: 	export CCQEMAT=$RUNDIR

export CCQEMAT=$RUNDIR

#cmd: 	echo "check on weights" $MPARAMFILESROOT;ls $MPARAMFILESROOT/data

echo "check on weights" $MPARAMFILESROOT;ls $MPARAMFILESROOT/data

#cmd: 	export MYPLAYLIST=minervame5A

export MYPLAYLIST=minervame5A

#cmd: 	$CCQEMAT/sidebands_v2 /Users/schellma/Dropbox/TOPMAT/CCQENu/make_hists/hms/testmac 1000 >& sidebands+test20220603191933.log

$CCQEMAT/sidebands_v2 /Users/schellma/Dropbox/TOPMAT/CCQENu/make_hists/hms/testmac 1000 >& sidebands+test20220603191933.log

#cmd: 	echo "run returned " $?

echo "run returned " $?

#cmd: 	ls -lrt

ls -lrt

#cmd: 	echo "ifdh cp -D ./*.root /Users/schellma/tmp//test/test20220603191933"

echo "ifdh cp -D ./*.root /Users/schellma/tmp//test/test20220603191933"

#cmd: 	ifdh cp -D ./*.root /Users/schellma/tmp//test/test20220603191933

ifdh cp -D ./*.root /Users/schellma/tmp//test/test20220603191933

#cmd: 	echo "ifdh returned " $?

echo "ifdh returned " $?

#cmd: 	echo "ifdh cp -D sidebands_test20220603191933.log /Users/schellma/tmp//test/test20220603191933"

echo "ifdh cp -D sidebands_test20220603191933.log /Users/schellma/tmp//test/test20220603191933"

#cmd: 	ifdh cp -D sidebands.log /Users/schellma/tmp//test/test20220603191933

ifdh cp -D sidebands.log /Users/schellma/tmp//test/test20220603191933

#cmd: 	echo "ifdh returned " $?

echo "ifdh returned " $?

