// File: DiffractiveReweighter.h
// Brief: A Reweighter changes the CV model into a different model using just a multiplicative
//        constant.  All vertical systematics are implemented by taking ratios to such weights.
//        Some Reweighters are mutually exclusive, and others are only needed for specific systematics.

#ifndef DIFFRACTIVE_REWEIGHTER_H
#define DIFFRACTIVE_REWEIGHTER_H

#if __cplusplus < 201103L
#define override
#endif

// c++ includes
#include <string>
#include <vector>

#include "PlotUtils/Reweighter.h"

namespace PlotUtils {

template <class UNIVERSE, class EVENT = PlotUtils::detail::empty>
class DiffractiveReweighter : public Reweighter<UNIVERSE, EVENT> {
   public:
    DiffractiveReweighter() = default;
    virtual ~DiffractiveReweighter() = default;

    virtual double GetWeight(const UNIVERSE& univ, const EVENT& myevent /*event*/) const override {
        return univ.GetDiffractiveWeight();
    };
    virtual std::string GetName() const override { return "DiffractiveReweighter"; }

    virtual bool DependsReco() const override { return false; }
    // virtual bool DependsTruth() const {return true;}; //Not needed as of time of writing.
    // PlotUtils::PionReweighter& PionReweighter();
    // virtual bool IsCompatible(const PionReweighter& /*other*/) const { return true; }
    // virtual std::vector<UNIVERSE*> GetRequiredUniverses() const { return std::vector<UNIVERSE*>{}; }
};
}  // namespace PlotUtils

#endif  // DIFFRACTIVE_REWEIGHTER_H