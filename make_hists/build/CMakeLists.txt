# Almost all CMake files should start with this
# You should always specify a range with the newest
# and oldest tested versions of CMake. This will ensure
# you pick up the best policies.

cmake_minimum_required(VERSION 3.1...3.14)

# This is your project statement. You should always list languages;
# Listing the version is nice here since it sets lots of useful variables

project(CCQEMAT VERSION 1.0 LANGUAGES CXX)

# If you set any CMAKE_ variables, that can go here.
# (But usually don't do this, except maybe for C++ standard)

# You need to tell CMake where to find the ROOT installation. This can be done in a number of ways:
#   - ROOT built with classic configure/make use the provided $ROOTSYS/etc/cmake/FindROOT.cmake
#   - ROOT built with CMake. Add in CMAKE_PREFIX_PATH the installation prefix for ROOT
list(APPEND CMAKE_PREFIX_PATH $ENV{ROOTSYS} $ENV{BOOSTDIR} $ENV{JSONCPP_DIR})
#list(APPEND CMAKE_PREFIX_PATH $ENV{ROOTSYS} $ENV{BOOSTDIR})

set(CMAKE_CXX_FLAGS "-Wformat=0 " )

#---Locate the ROOT package and defines a number of variables (e.g. ROOT_INCLUDE_DIRS)
find_package(ROOT REQUIRED COMPONENTS RIO Net)

#---Define useful ROOT functions and macros (e.g. ROOT_GENERATE_DICTIONARY)
include(${ROOT_USE_FILE})

include_directories($ENV{PWD} $ENV{PWD}/include $ENV{ROOTSYS}/include)

link_directories(${ROOT_LIBRARY_DIR})

MESSAGE("ROOT_LIBRARY_DIR:${ROOT_LIBRARY_DIR}")

# put some special flags here forgot what the DBUILD_SHARED_LIBS=OFF does..

add_definitions( -DFORM -DMNVROOT6 -DPLOTUTILS_STANDALONE -DCOMPILED "-DBUILD_SHARED_LIBS=OFF  ")

# do this or mac will make it dylib
set(CMAKE_SHARED_LIBRARY_SUFFIX ".so")


# tell it about the source files
set(SRC_FILES
include/Get2DVariablesFromConfig.cxx
include/GetVariablesFromConfig.cxx
include/CVUniverse.cxx
)

# tell it about the header files

set(H_FILES
include/CutFromConfig.h
include/CVFunctions.h
include/CVUniverse.h
include/GetCCQECutsFromConfig.h
include/GetVariablesFromConfig.h
include/Get2DVariablesFromConfig.h
include/GetXSec.h
include/Hist2DWrapperMap.h
include/HistWrapperMap.h
include/Systematics.h
include/Variable2DFromConfig.h
include/VariableFromConfig.h
include/plotting_pdf.h
PlotUtils/SystCalcs/MuonFunctions.h
PlotUtils/SystCalcs/RecoilEnergyFunctions.h
PlotUtils/SystCalcs/TruthFunctions.h
PlotUtils/SystCalcs/WeightFunctions.h
)

# need to know about Boost on macs so check that you know where it is.

MESSAGE("boost:$ENV{BOOSTDIR}")



include_directories($ENV{CCQEMAT} $ENV{CCQEMAT}/include   $ENV{UNFOLDUTILSROOT} $ENV{PLOTUTILSROOT} $ENV{PLOTUTILSROOT}/PlotUtils $ENV{BOOSTDIR}/include $ENV{BOOSTDIR} $ENV{JSONCPP_DIR}/include $ENV{BOOSTDIR}/include/boost)

# now generate the dictionary

ROOT_GENERATE_DICTIONARY(G__${PROJECT_NAME} ${H_FILES} LINKDEF ${CMAKE_SOURCE_DIR}/CCQEMAT_LinkDef.h)

# and then the shared library
# Output libname matches target name, with the usual extensions on your system

add_library(${PROJECT_NAME} SHARED ${SRC_FILES} G__${PROJECT_NAME}.cxx )

MESSAGE("ROOT_LIBRARIES:${ROOT_LIBRARIES} ")

MESSAGE("PROJECT:${PROJECT_NAME}")

target_link_libraries(${PROJECT_NAME} ${ROOT_LIBRARIES} Unfold MathCore -L$ENV{PLOTUTILSROOT} -lplotutils -L$ENV{UNFOLDUTILSROOT} -lunfoldutils -L$ENV{JSONCPP_DIR}/lib -ljsoncpp)
#target_link_libraries(${PROJECT_NAME} ${ROOT_LIBRARIES} Unfold MathCore -L$ENV{PLOTUTILSROOT} -lplotutils -L$ENV{UNFOLDUTILSROOT} -lunfoldutils)

# Link each target with other targets or add options, etc.

# Adding something we can run - Output name matches target name
#add_executable(myExample simple_example.cpp)

# Make sure you link your targets with this command. It can also link libraries and
# even flags, so linking a target that does not exist will not give a configure-time error.
#target_link_libraries(MyExample PRIVATE MyLibExample)

# Link each target with other targets or add options, etc.

# Adding something we can run - Output name matches target name


#add_executable(eventloop eventloop.C)
add_executable(sidebands sidebands.C)
add_executable(OldWeightsidebands OldWeightsidebands.C)
#add_executable(analyze_v3 analyze_v3.C)
add_executable(analyze_v4 analyze_v4.C)
add_executable(getCSVs getCSVs.C)
add_executable(analyze_v5 analyze_v5.C)
add_executable(v1_ratio v1_ratio.C)
add_executable(color_test color_test.C)

# Make sure you link your targets with this command. It can also link libraries and
# even flags, so linking a target that does not exist will not give a configure-time error.

#target_link_libraries(eventloop  PRIVATE ${PROJECT_NAME} )
target_link_libraries(sidebands  PRIVATE ${PROJECT_NAME} )
target_link_libraries(OldWeightsidebands  PRIVATE ${PROJECT_NAME} )
#target_link_libraries(analyze_v3  PRIVATE ${PROJECT_NAME} )
target_link_libraries(analyze_v4  PRIVATE ${PROJECT_NAME} )
target_link_libraries(getCSVs  PRIVATE ${PROJECT_NAME} )
target_link_libraries(analyze_v5  PRIVATE ${PROJECT_NAME} )
target_link_libraries(v1_ratio  PRIVATE ${PROJECT_NAME} )
target_link_libraries(color_test  PRIVATE ${PROJECT_NAME} )
