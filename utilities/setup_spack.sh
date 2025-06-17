# setup spack
# worked on May 20, 2025
source /cvmfs/larsoft.opensciencegrid.org/spack-fnal-develop/spack_env/setup-env.sh
source /cvmfs/larsoft.opensciencegrid.org/spack-v0.22.0-fermi/setup-env.sh
export CVSROOT=minervacvs@cdcvs.fnal.gov:/cvs/mnvsoft

# get the packages you need to run this - this is a total hack of guesswork
echo "ROOT"
#spack load root@6.28.12
spack load root@6.28.12%gcc@12.2.0 arch=linux-almalinux9-x86_64_v3
echo "CMAKE"
#spack load cmake@3.20.2 arch=linux-almalinux9-x86_64_v2 %gcc@11.5.0
spack load cmake@3.27.9%gcc@11.4.1 arch=linux-almalinux9-x86_64_v3
echo "GCC"
#spack load gcc@12.4.0
spack load gcc@12.2.0
echo "IFDHC"
#spack load ifdhc@2.8.0
spack load ifdhc@2.8.0%gcc@12.2.0 arch=linux-almalinux9-x86_64_v3
#spack load ifdhc-config   
spack load ifdhc-config@2.6.20%gcc@11.4.1 arch=linux-almalinux9-x86_64_v3
echo "PY-PIP"                       
#spack load py-pip
spack load py-pip@23.1.2%gcc@11.4.1 arch=linux-almalinux9-x86_64_v3
