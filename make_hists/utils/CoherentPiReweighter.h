// File: CoherentPiReweighter.h
// Brief: A Reweighter that changes the simulated FS particle model.
// Author: Noah Harvey Vaughan vaughann@oregonstate.edu

#ifndef PLOTUTILS_CoherentPiREWEIGHTER_H
#define PLOTUTILS_CoherentPiREWEIGHTER_H

// PlotUtils includes
// #include "PlotUtils/WeightFunctions.h"
#include "CVUniverse.h"
// Reweighter includes
#include "PlotUtils/Reweighter.h"
// #include "PlotUtils/weighters/weightCoherentPi.cxx"

template <class UNIVERSE, class EVENT = PlotUtils::detail::empty>
class CoherentPiReweighter : public Reweighter<UNIVERSE, EVENT> {
   public:
    CoherentPiReweighter() = default;
    virtual ~CoherentPiReweighter() = default;

    virtual double GetWeight(const UNIVERSE& univ, const EVENT& myevent /*event*/) const override {
        if (univ.GetInt("mc_intType") == 4) {
            double weight = univ.GetCoherentPiWeight();  // GetCoherentPiWeight(angle, KE); //PlotUtils::weightCoherentPi().get_combined_weight(angle, KE);
            return weight;
        } else
            return 1.0;
    };
    virtual std::string GetName() const override { return "COHPionReweighter"; }

    virtual bool DependsReco() const override { return false; }
    // virtual bool DependsTruth() const {return true;}; //Not needed as of time of writing.
    // PlotUtils::PionReweighter& PionReweighter();
    // virtual bool IsCompatible(const PionReweighter& /*other*/) const { return true; }
    // virtual std::vector<UNIVERSE*> GetRequiredUniverses() const { return std::vector<UNIVERSE*>{}; }
};


#endif  // PLOTUTILS_CoherentPiREWEIGHTER_H
