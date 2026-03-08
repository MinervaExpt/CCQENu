from PlotUtils import TargetUtils

def GetTarget(type,ismc):
    t = TargetUtils()
    minZ = 5980
    maxZ = 8422
    # isdata = (not ismc)
    # AtomsData = t.GetTrackerNAtoms(minZ,  maxZ, isdata)
    # AtomsMC = t.GetTrackerNAtoms(minZ, maxZ, ismc)
    # ProtonsData = t.GetTrackerNProtons(minZ, maxZ, isdata)
    # ProtonsMC = t.GetTrackerNProtons(minZ, maxZ, ismc)
    # NeutronsData = t.GetTrackerNNeutrons(minZ, maxZ, isdata)
    # NeutronsMC = t.GetTrackerNNeutrons(minZ, maxZ, ismc)
    # print ( "Atoms" , AtomsData , " " , AtomsMC )
    # print ( "Nucleons" , ProtonsData+NeutronsData , " " , ProtonsMC + NeutronsMC )
    # print ( "targets" , targets )
    if type == "Neutrons":
        return t.GetTrackerNNeutrons(minZ, maxZ, ismc)
    elif type == "Protons":
        return t.GetTrackerNProtons(minZ, maxZ, ismc)
    else:
        return t.GetTrackerNNeutrons(minZ, maxZ, ismc)+ t.GetTrackerNProtons(minZ, maxZ, ismc)


        
