// File: RemoveUnphysical2p2hExtendedEventsReweighter.h
// Brief: A reweighter that finds and removes unphysical
//        2p2h events from the extended 2p2h special samples
//        if you're using the Valencia 2p2h tune. This is not
//        necessary if you're doing the SuSA 2p2h.
// Author: Noah Harvey Vaughan vaughann@oregonstate.edu

#ifndef PLOTUTILS_RemoveUnphysical2p2hExtendedEventsREWEIGHTER_H
#define PLOTUTILS_RemoveUnphysical2p2hExtendedEventsREWEIGHTER_H

// PlotUtils includes
#include "weighters/weightRemoveUnphysical2p2hExtendedEventsClass.h"

// Reweighter includes
#include "weighters/Reweighter.h"

namespace PlotUtils {
template <class UNIVERSE, class EVENT = PlotUtils::detail::empty>
class RemoveUnphysical2p2hExtendedEventsReweighter : public Reweighter<UNIVERSE, EVENT> {
   public:
    RemoveUnphysical2p2hExtendedEventsReweighter() : Reweighter<UNIVERSE, EVENT>() {}

    virtual ~RemoveUnphysical2p2hExtendedEventsReweighter() = default;

    double GetWeight(const UNIVERSE& univ, const EVENT& /*event*/) const override {
        if (univ.GetInt("mc_intType") == 8) {
            std::vector<int> mc_er_ID = univ.GetVecInt("mc_er_ID");
            std::vector<int> mc_er_status = univ.GetVecInt("mc_er_status");
            std::vector<double> mc_er_Px = univ.GetVecDouble("mc_er_Px");
            std::vector<double> mc_er_Py = univ.GetVecDouble("mc_er_Py");
            std::vector<double> mc_er_Pz = univ.GetVecDouble("mc_er_Pz");
            std::vector<double> mc_er_E = univ.GetVecDouble("mc_er_E");
            weightRemoveUnphysical2p2hExtendedEventsClass fWeighter;

            double weight = fWeighter.getWeight(
                univ.Getq0True() * 1.e-3,
                univ.GetInt("mc_intType"),
                univ.GetInt("mc_er_nPart"),
                mc_er_ID,
                mc_er_status,
                mc_er_Px,
                mc_er_Py,
                mc_er_Pz,
                mc_er_E
            );
            return weight;
        }
        return 1.0;
    }

    std::string GetName() const override { return "RemoveUnphysical2p2hExtendedEvents"; }
    bool DependsReco() const override { return false; }

    // When using extended samples, this is required for Valencia 2p2h, but not needed for SuSA.
    virtual bool IsCompatible(const Reweighter<UNIVERSE, EVENT>& other) const override { return other.GetName() != "SuSA2p2h"; }

   private:
    weightRemoveUnphysical2p2hExtendedEventsClass fWeighter;
};
}  // namespace PlotUtils

#endif  // PLOTUTILS_RemoveUnphysical2p2hExtendedEventsREWEIGHTER_H
