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
    return "https://github.com/MinervaExpt/CCQENu/commit/e604a4b16b8b4651d2bab3910f3273890fb24daa";
  }
}

#endif //GIT_GITVERSION_H
