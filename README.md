# CCQENUMAT - MAT implementation of CCCQENU

here is how to build CCQEMAT using the new MAT

setup root, CVSROOT and get the MAT code installed using the documentation in [github.com/MinervaExpt/MAT-MINERvA](https://github.com/MinervaExpt/MAT-MINERvA)

then... 

```
export WHEREMATPUTSITSCODE=<directory where MAT code is> 
source $WHEREMATPUTSITSCODE/opt/build/setup.sh

# now get the CCQEMAT code out of CVS
cd $WHEREMATPUTSITSCODE
export WHEREIPUTMYCODE=$WHEREMATPUTSITSCODE
cvs co Ana/PickledCCQENu
export CCQEMAT=$WHEREIPUTMYCODE/Ana/PickledCCQENu/ana/make_hists

cd $CCQEMAT
# I haven't figured out how to do Andrew style builds yet so this builds on the source directory. But there is a MAT compatible cmake now.  

cmake mat  
make
```
