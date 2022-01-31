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
list(APPEND CMAKE_PREFIX_PATH $ENV{ROOTSYS}  $ENV{JSONCPP_DIR})
#list(APPEND CMAKE_PREFIX_PATH $ENV{ROOTSYS} )

set(CMAKE_CXX_FLAGS "-Wformat=0 -Wno-unused-variable")
 

#---Locate the ROOT package and defines a number of variables (e.g. ROOT_INCLUDE_DIRS)
find_package(ROOT REQUIRED COMPONENTS RIO Net)

#---Define useful ROOT functions and macros (e.g. ROOT_GENERATE_DICTIONARY)
include(${ROOT_USE_FILE})
#include_directories($ENV{CCQEMAT} $ENV{CCQEMAT}/include $ENV{PLOTUTILSROOT}/../include $ENV{PLOTUTILSROOT}/../include/PlotUtils $ENV{PLOTUTILSROOT}/../include/UnfoldUtils $ENV{PLOTUTILSROOT}/../include/RooUnfold)
include_directories($ENV{CCQEMAT} $ENV{CCQEMAT}/include $ENV{PLOTUTILSROOT}/../include $ENV{PLOTUTILSROOT}/../include/PlotUtils $ENV{PLOTUTILSROOT}/../include/UnfoldUtils $ENV{PLOTUTILSROOT}/../include/RooUnfold $ENV{JSONCPP_DIR}/include)

link_directories(${ROOT_LIBRARY_DIR})

MESSAGE("ROOT_LIBRARY_DIR:${ROOT_LIBRARY_DIR}")

# put some special flags here forgot what the DBUILD_SHARED_LIBS=OFF does..

add_definitions( -DFORM -DHAZMAT -DMNVROOT6 -DPLOTUTILS_STANDALONE -DCOMPILED "-DBUILD_SHARED_LIBS=OFF ")

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
include/Sample.h
include/CutFromConfig.h
include/CVFunctions.h
include/CVUniverse.h
include/GetCCQECutsFromConfig.h
include/GetVariablesFromConfig.h
include/Get2DVariablesFromConfig.h
include/Hist2DWrapperMap.h
include/HistWrapperMap.h
include/Systematics.h
include/Variable2DFromConfig.h
include/VariableFromConfig.h
include/plotting_pdf.h
)

include_directories($ENV{CCQEMAT} $ENV{CCQEMAT}/include   $ENV{UNFOLDUTILSROOT} $ENV{PLOTUTILSROOT} $ENV{PLOTUTILSROOT}/PlotUtils)

# now generate the dictionary

ROOT_GENERATE_DICTIONARY(G__${PROJECT_NAME} ${H_FILES} LINKDEF ${CMAKE_SOURCE_DIR}/CCQEMAT_LinkDef.h)

# and then the shared library
# Output libname matches target name, with the usual extensions on your system

add_library(${PROJECT_NAME} SHARED ${SRC_FILES} G__${PROJECT_NAME}.cxx )

MESSAGE("ROOT_LIBRARIES:${ROOT_LIBRARIES} ")

MESSAGE("PROJECT:${PROJECT_NAME}")

target_link_libraries(${PROJECT_NAME} ${ROOT_LIBRARIES} Unfold MathCore -L$ENV{PLOTUTILSROOT}  -lMAT-MINERvA -lMAT -lMATDict -lMAT-MINERvADict -L$ENV{UNFOLDUTILSROOT}  -lUnfoldUtils -L$ENV{UNFOLDUTILSROOT} -lUnfoldUtilsDict -L$ENV{JSONCPP_DIR}/lib  -ljsoncpp) #-L$ENV{JSONCPP_DIR}/lib
#target_link_libraries(${PROJECT_NAME} ${ROOT_LIBRARIES} Unfold MathCore -L$ENV{PLOTUTILSROOT} -lplotutils -L$ENV{UNFOLDUTILSROOT} -lunfoldutils -l$ENV{UNFOLDUTILSROOT} -lG__UnfoldUtilsDict.so)



# Link each target with other targets or add options, etc.

# Adding something we can run - Output name matches target name
#add_executable(myExample simple_example.cpp)

# Make sure you link your targets with this command. It can also link libraries and
# even flags, so linking a target that does not exist will not give a configure-time error.
#target_link_libraries(MyExample PRIVATE MyLibExample)

# Link each target with other targets or add options, etc.

# Adding something we can run - Output name matches target name

#add_executable(runsamples runsamples.C)
add_executable(sidebands_v2 sidebands_v2.C)
add_executable(analyze_v8 analyze_v8.C)



# Make sure you link your targets with this command. It can also link libraries and
# even flags, so linking a target that does not exist will not give a configure-time error.

#target_link_libraries(runsamples  PRIVATE ${PROJEC_NAME} )
target_link_libraries(sidebands_v2  PRIVATE ${PROJECT_NAME} )
target_link_libraries(analyze_v8  PRIVATE ${PROJECT_NAME} )
