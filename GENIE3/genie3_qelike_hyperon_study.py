import ROOT
import array
import sys

# Stolen from Amit's area. Used to do extraction of cross sections from raw GENIE v3 files for the purpose of comaprison.
# Changes made by NHV to fit new QElike nubar analysis
setRHC = True
hyplite = True
# def isPhaseSpace(mytree):
#     nfsp = mytree.nfsp
#     pdg = mytree.pdg
#     for p in range(0,nfsp):
#     if(pdg[p]==-13): n_muon+=1 # doesn't this need to be mu plus?

hyperon_mass_dict = {
    3112: 1197.449 ,
    3122: 1115.683,
    3212: 1192.642,
    3222: 1189.37,
    3224: 1382.8,
    3214: 1383.7,
    3114: 1387.2,
    3322: 1314.86,
    3312: 1321.71,
    3324: 1531.80,
    3314: 1535.0,
    3334: 1672.45
}

def isHyperon(mytree):
    nfsp  = mytree.nfsp
    pdg = mytree.pdg
    Efsp = mytree.E
    ishyperon = False
    proton_mass  = 938.28
    hyp_energy = 0.0
    for i in range(0,nfsp):
        if 3000<abs(pdg[i])<4000:
            energy = Efsp[i]
            ishyperon = True
            hyp_energy = energy - proton_mass
    return [ishyperon,hyp_energy]

def isCCQELikeHyp(mytree, RHC=False):

    #need 1 muon and no mesons and photons > 10 MeV in final state
    # This looks at events that would otherwise be considered qelike with hyperons in them
    nfsp = mytree.nfsp
    Efsp = mytree.E
    pdg  = mytree.pdg

    n_muon   = 0
    n_meson  = 0
    n_baryon = 0
    n_gamma  = 0
    genie_protons = 0
    n_hyperon = 0
    # proton_mass = 938.28
    # proton_E = 1058.272 # this is mass energy plus ke threshold

    # proton_KE_cut = 120.00

    badMesons = [211,321,323,111,130,310,311,313,411,421]
    #probably addd the pi0 as well....
    #this also has hyperons (as bad baryons) in the signal)
    # badBaryons = [3112,3122,3212,3222,4112,4122,4212,4222,411,421,111]
    # Looking for hyperons
    badBaryons = [4112,4122,4212,4222,411,421,111]
    hyperons = [3112,3122,3212,3222,3224,3214,3114,3322,3312,3324,3314,3334]

    for p in range(0,nfsp):
        energy = Efsp[p]
        # don't need proton Ke anymore
        # proton_KE = energy-proton_mass 
        if(abs(pdg[p])==13): n_muon+=1 # doesn't this need to be mu plus?
        if(abs(pdg[p]) in badMesons): n_meson+=1
        if(abs(pdg[p]) in badBaryons): n_baryon+=1
        if(pdg[p]==22 and Efsp[p] > 0.010): n_gamma+=1
        if(abs(pdg[p]) in hyperons): n_hyperon+=1
        # don't want proton KE stuff anymore
        # if(pdg[p]==2212 and proton_KE>proton_KE_cut ): genie_protons+=1 
    if not RHC:
        if n_muon == 1 and n_meson==0 and n_gamma==0 and n_baryon==0 and n_hyperon == 1: return True
        else: return False
    else:
        # if n_muon == 1 and n_meson==0 and n_gamma==0 and n_baryon==0 and genie_protons==0 : return True
        # we do want protons now
        if n_muon == 1 and n_meson==0 and n_gamma==0 and n_baryon==0 and n_hyperon == 1: return True
        else: return False

def isCCQELike(mytree,RHC=False):
    #need 1 muon and no mesons and photons > 10 MeV in final state

    nfsp = mytree.nfsp
    Efsp = mytree.E
    pdg  = mytree.pdg

    n_muon   = 0
    n_meson  = 0
    n_baryon = 0
    n_gamma  = 0
    genie_protons = 0
    # proton_mass = 938.28
    # proton_E = 1058.272 # this is mass energy plus ke threshold

    # proton_KE_cut = 120.00

    badMesons = [211,321,323,111,130,310,311,313,411,421]
    #probably addd the pi0 as well....
    #this also has hyperons (as bad baryons) in the signal)
    badBaryons = [3112,3122,3212,3222,3224,3214,3114,3322,3312,3324,3314,3334,4112,4122,4212,4222,411,421,111]
    
    for p in range(0,nfsp):
        energy = Efsp[p]
        # don't need proton Ke anymore
        # proton_KE = energy-proton_mass 
        if(abs(pdg[p])==13): n_muon+=1 # doesn't this need to be mu plus?
        if(abs(pdg[p]) in badMesons): n_meson+=1
        if(abs(pdg[p]) in badBaryons): n_baryon+=1
        if(pdg[p]==22 and Efsp[p] > 0.010): n_gamma+=1
        # don't want proton KE stuff anymore
        # if(pdg[p]==2212 and proton_KE>proton_KE_cut ): genie_protons+=1 
        if(pdg[p]==2212): genie_protons+=1 

    if not RHC:
        if n_muon == 1 and n_meson==0 and n_gamma==0 and n_baryon==0 : return True
        else: return False
    else:
        # if n_muon == 1 and n_meson==0 and n_gamma==0 and n_baryon==0 and genie_protons==0 : return True
        # we do want protons now
        if n_muon == 1 and n_meson==0 and n_gamma==0 and n_baryon==0: return True
        else: return False

def getHyperons(mytree):
    nfsp  = mytree.nfsp
    pdg = mytree.pdg
    Efsp = mytree.E
    hyp_type = 0
    hyp_energy = 0.0
    for i in range(0,nfsp):
        if 3000<abs(pdg[i])<4000:
            energy = Efsp[i]
            hyp_type = abs(pdg[i])
            # hyp_energy = energy - (hyperon_mass_dict[abs(pdg[i])]*.0001)
            hyp_energy = energy
    return hyp_type,hyp_energy

def getProtonMomentum(mytree):
    nfsp = mytree.nfsp
    Efsp = mytree.E
    pdg  = mytree.pdg
    px = mytree.px
    py = mytree.py
    pz = mytree.pz
    
    prot_mom = ROOT.TVector3()
    prot_e = 0

    for p in range(0,nfsp):
        if(pdg[p]==2212 and Efsp[p]>prot_e):#highest energy proton
            prot_mom.SetX(px[p])
            prot_mom.SetY(py[p])
            prot_mom.SetZ(pz[p])
            # Doesn't prot_e need to be reset to get the leading proton? Adding that here:
            prot_e = Efsp[p]
    return prot_mom

def getMuonMomentum(mytree):
    muon_mom = ROOT.TVector3()

    nfsp = mytree.nfsp
    Efsp = mytree.E
    pdg  = mytree.pdg
    px = mytree.px
    py = mytree.py
    pz = mytree.pz
    
    for p in range(0,nfsp):
        if(pdg[p]==13):
            muon_mom.SetX(px[p])
            muon_mom.SetY(py[p])
            muon_mom.SetZ(pz[p])
            break
    return muon_mom

def isInclusiveFHC(mytree):
    nu_pdg = mytree.PDGnu
    lep_pdg = mytree.PDGLep

    if(nu_pdg == 14 and lep_pdg == 13):
        return True
    
    return False

def isTKI(mytree):
    #<70 degree proton
    #<20 degree muon
    #1.5 to 10 muon mom
    #0.45 to 1.2 proton mom

    muonmom = getMuonMomentum(mytree)
    protonmom = getProtonMomentum(mytree)

    goodProtonMom = protonmom.Mag()>0.45 and protonmom.Mag()<1.2
    goodMuonMom   = muonmom.Mag()>1.5 and muonmom.Mag()<10

    goodProtonAngle = protonmom.Theta()*180/3.1415
    goodMuonAngle = muonmom.Theta()*180/3.1415

    if goodProtonMom and goodMuonMom and goodProtonAngle and goodMuonAngle: return True
    
    return False

def getPn(e):

    promom = getProtonMomentum(e)
    mumom = getMuonMomentum(e)

    protonPtVect = getProtonMomentum(e)
    muonPtVect = getMuonMomentum(e)

    protonPtVect.SetZ(0)
    muonPtVect.SetZ(0)


    pn = -99;
    Mn = 939.5654133/1000;
    Mp = 938.2720813/1000;
    Mmu = 105.6583745/1000;
    MA = 6*Mn + 6*Mp - 92.162/1000;
    Bin=27.13/1000;
    MAstar = MA - Mn + Bin;
    
    Epprim = ROOT.TMath.Sqrt(Mp*Mp + promom.Mag2());
    kprimL = mumom.Z();
    pprimL = promom.Z();
    Eprim = ROOT.TMath.Sqrt(Mmu*Mmu+mumom.Mag2());
    
    factor = MA - Eprim - Epprim + kprimL + pprimL;
    pT = (protonPtVect+muonPtVect).Mag();
    pL = -(MAstar*MAstar + pT*pT-factor*factor)/2.0/factor;
    

    pn = ROOT.TMath.Sqrt(pL*pL + pT*pT);
    return pn



print("Print Start of The Code")
inputFile = ROOT.TFile(sys.argv[1])

mytree = inputFile.Get("FlatTree_VARS")

ofilename = sys.argv[2]

# Bins from 3d analysis (might change)
pzbins = [1.5, 2., 2.5, 3., 3.5, 4., 4.5, 5., 5.5, 6., 7., 8., 9., 10., 15.]
ptbins = [0., 0.075, 0.15, 0.25, 0.325, 0.4, 0.475, 0.55, 0.7, 0.85, 1., 1.25, 1.5, 2.5]
recoilbins = [0.0, 0.05, 0.10, 0.15, 0.30, 0.50, 1.0]

# myptpz = ROOT.TH2D("ptpz","ptpz",len(pzbins)-1, array.array("d",pzbins),len(ptbins)-1,array.array("d",ptbins))
mypt = ROOT.TH1D("pt","pt",len(ptbins)-1,array.array("d",ptbins))
mypz = ROOT.TH1D("pz","pz",len(pzbins)-1,array.array("d",pzbins))
myrecoil = ROOT.TH1D("recoil","recoil",len(recoilbins)-1,array.array("d",recoilbins))

mypt_qelike = ROOT.TH1D("pt_qelike","pt_qelike",len(ptbins)-1,array.array("d",ptbins))
mypz_qelike = ROOT.TH1D("pz_qelike","pz_qelike",len(pzbins)-1,array.array("d",pzbins))
myrecoil_qelike = ROOT.TH1D("recoil_qelike","recoil_qelike",len(recoilbins)-1,array.array("d",recoilbins))

mypt_qelikehyp = ROOT.TH1D("mypt_qelikehyp","mypt_qelikehyp",len(ptbins)-1,array.array("d",ptbins))
mypz_qelikehyp = ROOT.TH1D("mypz_qelikehyp","mypz_qelikehyp",len(pzbins)-1,array.array("d",pzbins))
myrecoil_qelikehyp = ROOT.TH1D("myrecoil_qelikehyp","myrecoil_qelikehyp",len(recoilbins)-1,array.array("d",recoilbins))
print("Done making histograms")

# myptpz_rate = ROOT.TH2D("ptpz_rate","ptpz_rate",len(pzbins)-1, array.array("d",pzbins),len(ptbins)-1,array.array("d",ptbins))
# mytheta = ROOT.TH1D("theta","theta",360,0,180)

myhyptype_hist = ROOT.TH1D("myhyptype_hist","Hyperon types", 12,0,12)
myLambdaE_hist = ROOT.TH1D("myLambdaE_hist","Lambda Energy", 100,0.,10.0)
mySigmaMinusE_hist = ROOT.TH1D("mySigmaMinusE_hist","Sigma- Energy", 100,0.,10.0)
mySigmaZeroE_hist = ROOT.TH1D("mySigmaZeroE_hist","Sigma0 Energy", 100,0.,10.0)

hyperons = [3112,3122,3212,3222,3224,3214,3114,3322,3312,3324,3314,3334]
bin_pid = { 
    3112: "#Sigma^{-}",
    3122: "#Lambda",
    3212: "#Sigma^{0}",
    3222: "#Sigma^{+}",
    3224: "#Sigma^{*+}",
    3214: "#Sigma^{*0}",
    3114: "#Sigma^{*-}",
    3322: "#Xi^{0}",
    3312: "#Xi^{-}",
    3324: "#Xi^{*0}",
    3314: "#Xi^{*-}",
    3334: "#Omega^{-}"
}

hyp_index_dict = { 
    3112: 1,
    3122: 2,
    3212: 3,
    3222: 4,
    3224: 5,
    3214: 6,
    3114: 7,
    3322: 8,
    3312: 9,
    3324: 10,
    3314: 11,
    3334: 12
}

print("Entering event loop")
counter = 0
qelike_counter = 0
hyp_counter = 0
qelikehyp_counter = 0
maxhypE = 0.0

for e in mytree:
    coslep = e.CosLep
    #20 degree cut
    elep= e.ELep
    fScaleFactor = e.fScaleFactor
  
    P = ROOT.TMath.Sqrt(elep*elep-0.105*0.105)
    Pl = coslep*P
    Pt = ROOT.TMath.Sqrt(1-coslep*coslep)*P
    if coslep<0.93969262078: continue
    counter+=1
    Eav = e.Eav

    if isHyperon(e)[0]:
        hyp_counter +=1

    if isCCQELike(e,setRHC):
        qelike_counter+=1
        mypz_qelike.Fill(Pl)
        mypt_qelike.Fill(Pt)
        myrecoil_qelike.Fill(Eav)

    hyp_type = 0
    hypE = 0
    if isCCQELikeHyp(e,setRHC):
        qelikehyp_counter+=1
        mypz_qelikehyp.Fill(Pl)
        mypt_qelikehyp.Fill(Pt)
        myrecoil_qelikehyp.Fill(Eav)
        hyp_type,hypE = getHyperons(e)
        # print("hyp_type: ",hyp_type)
        hyp_index = hyp_index_dict[hyp_type]
        myhyptype_hist.Fill(hyp_index-.0001)
        # myhypE_hist.Fill(hypE)
        if hypE > maxhypE:
            maxhypE = hypE
            print("tmpmaxhypE: ",maxhypE)
        if hyp_index==3122:
            myLambdaE_hist.Fill(hypE)
        if hyp_index==3112:
            mySigmaMinusE_hist.Fill(hypE)
        if hyp_index==3212:
            mySigmaZeroE_hist.Fill(hypE)
        # hyp_counter +=1

    # if hyplite & qelikehyp_counter==10000:
    #     break

    # if counter%10000==0:
    #     print(counter/1000, "k", end='\r')


print("Done with event loop")
print("qelike counter: ", qelike_counter)
print("hyperon counter: ", hyp_counter)
print("qelikehyp counter: ", qelikehyp_counter)
print("Total Events: ", counter)
print("maxhypE: ",maxhypE)
# hypbin = 1
for pid in bin_pid.keys():
    myhyptype_hist.GetXaxis().SetBinLabel(hyp_index_dict[pid], bin_pid[pid])
    # hypbin+=1

myhyptype_hist.GetXaxis().SetTitle("Hyperons")
myhyptype_hist.GetYaxis().SetTitle("N events")
myLambdaE_hist.GetXaxis().SetTitle("Lambda Energy")
myLambdaE_hist.GetYaxis().SetTitle("arbitrary N events")
mySigmaMinusE_hist.GetXaxis().SetTitle("SigmaMinus Energy")
mySigmaMinusE_hist.GetYaxis().SetTitle("arbitrary N events")
mySigmaZeroE_hist.GetXaxis().SetTitle("Sigma0 Energy")
mySigmaZeroE_hist.GetYaxis().SetTitle("arbitrary N events")

mypz.GetXaxis().SetTitle("Muon p_{||} (GeV)")
mypz.GetYaxis().SetTitle("d#sigma/dp_{||} cm^{2}/GeV/nucleon")
mypt.GetXaxis().SetTitle("Muon p_{t} (GeV)")
mypt.GetYaxis().SetTitle("d#sigma/dp_{t} cm^{2}/GeV/nucleon")
myrecoil.GetXaxis().SetTitle("E_{Avail} (GeV)")
myrecoil.GetYaxis().SetTitle("d#sigma/dE_{Avail} cm^{2}/GeV/nucleon")

mypz_qelike.GetXaxis().SetTitle("Muon p_{||} (GeV)")
mypz_qelike.GetYaxis().SetTitle("d#sigma/dp_{||} cm^{2}/GeV/nucleon")
mypt_qelike.GetXaxis().SetTitle("Muon p_{t} (GeV)")
mypt_qelike.GetYaxis().SetTitle("d#sigma/dp_{t} cm^{2}/GeV/nucleon")
myrecoil_qelike.GetXaxis().SetTitle("E_{Avail} (GeV)")
myrecoil_qelike.GetYaxis().SetTitle("d#sigma/dE_{Avail} cm^{2}/GeV/nucleon")

mypz_qelikehyp.GetXaxis().SetTitle("Muon p_{||} (GeV)")
mypz_qelikehyp.GetYaxis().SetTitle("d#sigma/dp_{||} cm^{2}/GeV/nucleon")
mypt_qelikehyp.GetXaxis().SetTitle("Muon p_{t} (GeV)")
mypt_qelikehyp.GetYaxis().SetTitle("d#sigma/dp_{t} cm^{2}/GeV/nucleon")
myrecoil_qelikehyp.GetXaxis().SetTitle("E_{Avail} (GeV)")
myrecoil_qelikehyp.GetYaxis().SetTitle("d#sigma/dE_{Avail} cm^{2}/GeV/nucleon")

print("Making output file")
myoutput = ROOT.TFile(ofilename,"RECREATE")

mypz_qelike.Write()
mypt_qelike.Write()
myrecoil_qelike.Write()

mypz_qelikehyp.Write()
mypt_qelikehyp.Write()
myrecoil_qelikehyp.Write()

myhyptype_hist.Write()
myLambdaE_hist.Write()
mySigmaMinusE_hist.Write()
mySigmaZeroE_hist.Write()

print("Done writing hists to ", ofilename)

# """
# myptpz_bymode = []
# for i in range(0,60):
#     tmphist = ROOT.TH2D("ptpz-%d"%i,"ptpz-%d"%i,len(pzbins)-1, array.array("d",pzbins),len(ptbins)-1,array.array("d",ptbins))
#     myptpz_bymode.append(tmphist)
# """

# myptpz_qelike = ROOT.TH2D("ptpz_qelike","ptpz_qelike",len(pzbins)-1, array.array("d",pzbins),len(ptbins)-1,array.array("d",ptbins))
# myptpz_qelike = ROOT.TH2D("ptpz_qelike","ptpz_qelike",len(pzbins)-1, array.array("d",pzbins),len(ptbins)-1,array.array("d",ptbins))
# # myq2_qelike = ROOT.TH1D("q2","q2",len(q2bins)-1,array.array("d",q2bins))
# # myenu_qelike = ROOT.TH1D("enu","enu",len(enubins)-1,array.array("d",enubins))
# # myenuq2_qelike = ROOT.TH2D("enuq2","enuq2",len(enubins)-1,array.array("d",enubins),len(q2bins)-1,array.array("d",q2bins))
# print ("Done Creating Histograms")
# counter = 0
# hyp_counter = 0
# for e in mytree:
#     if isHyperon(e)[0]:
#         hyp_counter +=1
#     # filling multiple things, this gets rid of them before hand
#     # if not isCCQELike(e,setRHC): continue
#     coslep = e.CosLep
#     #20 degree cut
#     elep= e.ELep
#     q2 = e.Q2_QE
#     enu_true = e.Enu_true
#     fScaleFactor = e.fScaleFactor
  
#     P = ROOT.TMath.Sqrt(elep*elep-0.105*0.105)
#     Pl = coslep*P
#     Pt = ROOT.TMath.Sqrt(1-coslep*coslep)*P
#     # if isCCQELike(e,True):
#     #     if(enu_true>2.0 and enu_true<15.0 and Pl<15.0):
#     #         myq2_qelike.Fill(q2,fScaleFactor)
#     if coslep<0.93969262078: continue
    
# #    print P,Pl,Pt,ROOT.TMath.Sqrt(Pl*Pl+Pt*Pt)/P,e.Mode
#     """
#     myptpz.Fill(Pl,Pt,fScaleFactor)
#     mypt.Fill(Pt,fScaleFactor)
#     mypz.Fill(Pl,fScaleFactor)
#     myptpz_rate.Fill(Pl,Pt)
#     myptpz_bymode[e.Mode].Fill(Pl,Pt,fScaleFactor)
#     if(Pl>1.5 and Pl<60 and Pt>0 and Pt<4.5): mytheta.Fill(ROOT.TMath.ACos(coslep)*180.0/3.14159,fScaleFactor)
#     """
    
#     # need to fix this part to speed things up
#     if isCCQELike(e,setRHC):
#         myptpz_qelike.Fill(Pl,Pt,fScaleFactor)
#         # Not doing enu or q2 for now
#         # if(Pl>15):continue
#         # myenu_qelike.Fill(enu_true,fScaleFactor)
#         # myenuq2_qelike.Fill(enu_true,q2,fScaleFactor)
#     counter+=1
#     """
#     if counter%1001==0:
#         print("tot entries ",counter," hyperon  ",hyp_counter," hyperon energy ",isHyperon(e)[1])
#     """
#    # print("Reading Entry ",counter)
#    # if(counter==1000000):break
    
# #myptpz.Scale(1,"width")
# #mypt.Scale(1,"width")
# #mypz.Scale(1,"width")
# print("Total Events ",counter)
# myptpz.GetXaxis().SetTitle("Muon p_{||} (GeV)")
# myptpz.GetYaxis().SetTitle("Muon p_{t} (GeV)")

# mypz.GetXaxis().SetTitle("Muon p_{||} (GeV)")
# mypz.GetYaxis().SetTitle("d#sigma/dp_{||} cm^2/GeV/nucleon")

# mypt.GetXaxis().SetTitle("Muon p_{t} (GeV)")
# mypt.GetYaxis().SetTitle("d#sigma/dp_{t} cm^2/GeV/nucleon")

# # Dont need q2 or enu
# # myenu_qelike.GetXaxis().SetTitle("E_{#nu} (GeV)")
# # myenu_qelike.GetYaxis().SetTitle("#sigma{E_#nu}^{QE} (cm^{2}/nucleon)")


# # myenuq2_qelike.GetXaxis().SetTitle("E_{#nu} (GeV)")
# # myenuq2_qelike.GetYaxis().SetTitle("Q^{2}_{QE} (GeV^{2})")


# myoutput = ROOT.TFile(sys.argv[2],"RECREATE")

# myptpz.Write();
# mypz.Write()
# mypt.Write()
# myptpz_rate.Write()
# mytheta.Write()
# # myenu_qelike.Write()
# # myq2_qelike.Write()
# myptpz_qelike.Write()
# # myenuq2_qelike.Write()

# #for i in range(60):
# #    myptpz_bymode[i].Write()
# #can = ROOT.TCanvas()
# #myptpz.Draw("COLZ")
# #can2 = ROOT.TCanvas()
# #mypt.Draw()
# #can3 = ROOT.TCanvas()
# #mypz.Draw()
# #raw_input("done")

    
