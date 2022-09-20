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
    return "https://github.com/MinervaExpt/CCQENu/commit/9b4c4c92c2a44156edf03d12ea29cef24e9fbf32";
  }
}

#endif //GIT_GITVERSION_H
