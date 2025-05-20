# setup spack
# worked on May 20, 2025
source /cvmfs/larsoft.opensciencegrid.org/spack-fnal-develop/spack_env/setup-env.sh
export CVSROOT=minervacvs@cdcvs.fnal.gov:/cvs/mnvsoft

# get the packages you need to run this - this is a total hack of guesswork
spack load root@6.28.12/rqkcbbm
spack load cmake@3.20.2 arch=linux-almalinux9-x86_64_v2 %gcc@11.5.0
spack load gcc@12.4.0
spack load ifdhc@2.8.0
spack load ifdhc-config                          
spack load py-pip