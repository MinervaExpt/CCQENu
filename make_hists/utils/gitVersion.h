//File: gitVersion.cpp.in
//Brief: Template for access to git version control information.  Filled in to create a .cpp file by CMake.
//Author: Andrew Olivier aolivier@ur.rochester.edu

//c++ includes
#include <string>

#ifndef GIT_GITVERSION_H
#define GIT_GITVERSION_H

namespace git
{
  std::string commitHash()
  {
    return "https://github.com/MinervaExpt/CCQENu/commit/be06a6de4f9c7e7ed768537d40cab550994d29f6";
  }
}

#endif //GIT_GITVERSION_H
