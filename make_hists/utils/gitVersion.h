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
    return "https://github.com/MinervaExpt/CCQENu/commit/8c70c1d253a5887d0b38c407a0e6ed8c2b0414fa";
  }
}

#endif //GIT_GITVERSION_H
