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
    return "https://github.com/MinervaExpt/CCQENu/commit/bf92fa00fa9355f4cd704c2f343f353158315def";
  }
}

#endif //GIT_GITVERSION_H
