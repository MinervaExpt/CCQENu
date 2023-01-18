#ifndef MNV_MnvHHyperD_H
#define MNV_MnvHHyperD_H 1

#include "PlotUtils/MnvH1D.h"

namespace PlotUtils
{
  /*
  An extension to the MnvH1D for doing higher dimensional analyses utilizing the
  HyperDimLineraizer to linearize multidimesional phase spaces to a 1D binspace.
  This object works the same as an MnvH1D, but includes some information storing
  the map from "bin-space" <-> "variable-phase-space".

  Noah Harvey Vaughan
  Oregon State University
  MINERvA Collaboration
  vaughann@oregonstate.edu
  */

  // Place holder for now, will flesh out more shortly - NHV 1/18/23


  class MnvHHyperD : public MnvH1D
  {
  public:
    // Default Constructor
    MnvHHyperD();

    MnvHHyperD()
  }


}
