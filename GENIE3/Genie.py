from ROOT import *
import sys,os,string
import particle
from particle import Particle
from ROOT import TGenPhaseSpace
from ROOT import TLorentzVector
from array import *
# code to explore particles in a GENIE tuple

TUPLEDUMP=False
ProtonCut = 0.120

def makehist(ntuple,var,select):
    print (var)
    ntuple.Draw(var,select)
    htemp = TH1D()
    htemp = gPad.GetPrimitive("htemp")
    if "TH" not in str(type(htemp)):
        return None
    thehist = TH1F()
    thehist = htemp.Clone(var)
    htemp.Delete()
    return thehist
    
def npions(pdglist,npdg):
    npion = 0
    for part in pdglist:
        both = abs(part)
        if both == 111 or both == 211 :
            npion += 1
    return npion
    
def nphotons(pdglist,elist,npdg):  # of photons above 10 MeV
    n = 0
    for i in range(0,npdg):
        if pdglist[i] == 22 and elist[i] > 0.01:
            n += 1
    return n
    
def nprotons(pdglist,elist,npdg):
    n = 0
    for i in range(0,npdg):
        if pdglist[i] == 2212 and elist[i]-.9382 > ProtonCut:
            n += 1
    return n
 
def RecoilCut(recoil,Q2):
      
     offset=0.05;
     if( Q2 < 0.175 ): return ( recoil <= 0.08+offset);
     if( Q2 < 1.4 ): return (recoil <= 0.03 + 0.3*Q2+offset);
     return (recoil <= 0.45+offset); #antinu
    
d_filename = "flat_GENIE_1000k_tune_G18_02a_02_11a_50MCombined_RHC.root"
filename = d_filename
ofilename = "pdg_"+filename
inputfile = TFile.Open(filename,'READONLY')

ntuple = inputfile.Get("FlatTree_VARS")
outputfile = TFile.Open(ofilename,"RECREATE")
print (ntuple.GetListOfBranches())
select = "Enu_true > 1.5 && Enu_true < 20. && ELep > 1.5 && CosLep > 0.939693 && PDGnu == -14 && PDGLep < 0"
notinteresting = []
if TUPLEDUMP:
    print ("dump the variables")
    count = 0
    for p in ntuple.GetListOfBranches():
        count +=1

        branchLength = ntuple.GetLeaf(p.GetName()).GetLen()
        branch = p.GetName()
        if "flag" in branch:
            break
        if branchLength > 1:
            continue

        if branch in notinteresting:
            continue
        ahist = makehist(ntuple,branch,select)
        ahist.Print()
        outputfile.cd()
        ahist.Write()


nEntries = ntuple.GetEntries()
maxcount = 100000
parts = {}
partT = {}
partTs = {}
icount = 0
pions = TH1F("nPi","number of pions",10,0.,10.)
photons = TH1F("nPhoton","number of photons > 10 MeV",10,0.,10.)
baryons = ["Lambda","Sigmaminus","Sigma0"]
hyperP={}
hypercharged = {}
hyperzero = {}
hypertotC = {}
hypertot0 = {}
hyperpassC = {}
hyperpass0 = {}
for baryon in baryons:
    hyperP[baryon] = TH1F("T_p_%s"%baryon,"T of p from %s, GeV"%baryon,100,0.,0.5)
    hypercharged[baryon] = TH1F("T_pipm_%s"%baryon,"T of charge pion from %s, GeV"%baryon,100,0.,0.5)
    hyperzero[baryon] = TH1F("E_pizero_%s"%baryon,"E of neutral pion from %s, GeV"%baryon,100,0.,0.5)
    hyperpassC[baryon] = TH1F("E_passC_%s"%baryon,"Visible E from %s charged, GeV, passes cut"%baryon,100,0.,0.5)
    hyperpass0[baryon] = TH1F("E_pass0_%s"%baryon,"Visible E from %s neutral, GeV, passes cut"%baryon,100,0.,0.5)
    hypertotC[baryon] = TH1F("E_visC_%s"%baryon,"Visible E from %s charged, GeV"%baryon,100,0.,0.5)
    hypertot0[baryon] = TH1F("E_vis0_%s"%baryon,"Visible E from %s neutral, GeV"%baryon,100,0.,0.5)


for i in range(0, nEntries):
    ntuple.GetEntry(i)
    if icount > maxcount:
        break
    icount +=1
    if icount%1000 == 0 : print ("count",icount)
    if not (ntuple.Enu_true > 1.5 and ntuple.Enu_true < 20.): continue
    if not (ntuple.ELep > 1.5 and ntuple.CosLep > 0.939693): continue
    if not (ntuple.PDGnu == -14 and ntuple.PDGLep == -13):
        continue
    Q2 = ntuple.Q2_QE
    npi = npions(ntuple.pdg,ntuple.nfsp)
    ngamma = nphotons(ntuple.pdg,ntuple.E,ntuple.nfsp)
    nproton = nprotons(ntuple.pdg,ntuple.E,ntuple.nfsp)
    pions.Fill(npi)
    photons.Fill(ngamma)
    if npi>0 or ngamma>0 or nproton>0:
        #print ("veto",npi,ngamma)
        continue
    for p in range(0,ntuple.nfsp):
        thepart = ntuple.pdg[p]
        
        aname = (Particle.from_pdgid(thepart))
        themass = aname.mass/1000.
        thename=aname.name.replace("+","plus").replace("-","minus").replace("~","_")
        #print (thepart,thename,themass)
        if thepart not in parts.keys():
            parts[thepart] = TH1F("%s_E"%thename,"%s_E in GeV"%thename,100,0,20.)
            partT[thepart] = TH1F("%s_T"%thename,"%s_T in GeV"%thename,100,0,5.)
            partTs[thepart] = TH1F("pass_%s_T"%thename,"Recoilcut %s_T in GeV"%thename,100,0,0.5)
        parts[thepart].Fill(ntuple.E[p],ntuple.Weight)
        partT[thepart].Fill(ntuple.E[p]-themass,ntuple.Weight)
        partTs[thepart].Fill(ntuple.E[p]-themass,ntuple.Weight)
        if thename in baryons:
            
            #print (ntuple.px[p],ntuple.py[p],ntuple.pz[p],ntuple.E[p])
            vBaryon =  TLorentzVector(ntuple.px[p],ntuple.py[p],ntuple.pz[p],ntuple.E[p])
           
           
            decay = TGenPhaseSpace()
            themasses = [0.938, 0.139]
            masses = array('d',themasses)
            decay.SetDecay(vBaryon, 2, masses)
            nthrow = 100
            baryon = thename
            for i in range(0,nthrow):
                weight = decay.Generate()/double(nthrow);
                pProton = decay.GetDecay(0);
                pPi    = decay.GetDecay(1);
#                print ("Event")
#                vLambda.Print()
#                pProton.Print()
#                new = pProton+pPi
#                pPi.Print()
#                new.Print()
                
                if baryon == "Sigmaminus":
                    
                    hypercharged[thename].Fill(pPi.E()-masses[1],weight)
                    recoil = pPi.E()-masses[1]
                    hypertot0[thename].Fill(pPi.E()-masses[1],weight)
                    if RecoilCut(recoil,Q2):
                        hyperpass0[thename].Fill(pPi.E()-masses[1],weight)   # just a pi-
                if baryon == "Lambda" or baryon == "Sigma0":
                # charge mode
                    hyperP[thename].Fill(pProton.E()-masses[0],weight*.64)
                    hypercharged[thename].Fill(pPi.E()-masses[1],weight*.64)
                    recoil = pProton.E()-masses[0]+pPi.E()-masses[1]
                    hypertotC[thename].Fill(recoil,weight*.64)
                    if RecoilCut(recoil,Q2): hyperpassC[thename].Fill(recoil,weight*.64)
                     
                # neutral mode
                    hyperzero[thename].Fill(pPi.E(),weight*.36)
                    recoil = pPi.E()
                    hypertot0[thename].Fill(recoil,weight*.36)
                    if RecoilCut(recoil,Q2): hyperpass0[thename].Fill(recoil,weight*.36)
                    
               
                   
   
         
outputfile.cd()
for baryon in baryons:
    hyperP[baryon].Print()
    hyperP[baryon].Write()
    hypercharged[baryon].Write()
    hyperzero[baryon].Write()
    hypertot0[baryon].Write()
    hypertotC[baryon].Write()
    hyperpass0[baryon].Write()
    hyperpassC[baryon].Write()
    hypertot0.Draw("hist")
    hyperpass0.SetLineStyle(2)
    hyperpass0.Draw("hist same")
    print (hyperP[baryon].GetTitle(),"\t total ", hyperP[baryon].Integral(),"\t n<120 MeV ",hyperP[baryon].Integral(1,24))
    print (hypercharged[baryon].GetTitle(),"\t total ", hypercharged[baryon].Integral(),"\t n<120 MeV ",hypercharged[baryon].Integral(1,24))
    print (hyperzero[baryon].GetTitle(),"\t total ", hyperzero[baryon].Integral(),"\t n<120 MeV ",hyperzero[baryon].Integral(1,24))
    print (hypertot0[baryon].GetTitle(),"\t total ", hypertot0[baryon].Integral(),"\t n<120 MeV ",hypertot0[baryon].Integral(1,24))
    print (hypertotC[baryon].GetTitle(),"\t total ", hypertotC[baryon].Integral(),"\t n<120 MeV ",hypertotC[baryon].Integral(1,24))
    print (hyperpass0[baryon].GetTitle(),"\t total ", hyperpass0[baryon].Integral(),"\t n<120 MeV ",hyperpass0[baryon].Integral(1,24))
    print (hyperpassC[baryon].GetTitle(),"\t total ", hyperpassC[baryon].Integral(),"\t n<120 MeV ",hyperpassC[baryon].Integral(1,24))


for h in parts:
    parts[h].Write()
    partT[h].Write()
    partTs[h].Write()
    print ((Particle.from_pdgid(h)),"\t total ", parts[h].Integral(),"\t n<120 MeV ",partTs[h].Integral(1,24))
pions.Write()
photons.Write()
outputfile.Close()
inputfile.Close()

# variables from MakeClass on flat_GENIE_1000k_tune_G18_02a_02_11a_50MCombined_RHC.root for the MINERvA tracker
 #  Int_t           Mode;
 #  Char_t          cc;
 #  Int_t           PDGnu;
 #  Float_t         Enu_true;
 #  Int_t           tgt;
 #  Int_t           tgta;
 #  Int_t           tgtz;
 #  Int_t           PDGLep;
 #  Float_t         ELep;
 #  Float_t         CosLep;
 #  Float_t         Q2;
 #  Float_t         q0;
 #  Float_t         q3;
 #  Float_t         Enu_QE;
 #  Float_t         Q2_QE;
 #  Float_t         W_nuc_rest;
 #  Float_t         W;
 #  Float_t         W_genie;
 #  Float_t         x;
 #  Float_t         y;
 #  Float_t         Eav;
 #  Float_t         EavAlt;
 #  Float_t         CosThetaAdler;
 #  Float_t         PhiAdler;
 #  Float_t         dalphat;
 #  Float_t         dpt;
 #  Float_t         dphit;
 #  Float_t         pnreco_C;
 #  Int_t           nfsp;
 #  Float_t         px[30];   //[nfsp]
 #  Float_t         py[30];   //[nfsp]
 #  Float_t         pz[30];   //[nfsp]
 #  Float_t         E[30];   //[nfsp]
 #  Int_t           pdg[30];   //[nfsp]
 #  Int_t           pdg_rank[30];   //[nfsp]
 #  Int_t           ninitp;
 #  Float_t         px_init[7];   //[ninitp]
 #  Float_t         py_init[7];   //[ninitp]
 #  Float_t         pz_init[7];   //[ninitp]
 #  Float_t         E_init[7];   //[ninitp]
 #  Int_t           pdg_init[7];   //[ninitp]
 #  Int_t           nvertp;
 #  Float_t         px_vert[23];   //[nvertp]
 #  Float_t         py_vert[23];   //[nvertp]
 #  Float_t         pz_vert[23];   //[nvertp]
 #  Float_t         E_vert[23];   //[nvertp]
 #  Int_t           pdg_vert[23];   //[nvertp]
 #  Float_t         Weight;
 #  Float_t         InputWeight;
 #  Float_t         RWWeight;
 #  Double_t        fScaleFactor;
 #  Float_t         CustomWeight;
 #  Float_t         CustomWeightArray[6];
 #  Bool_t          flagCCINC;
 #  Bool_t          flagNCINC;
 #  Bool_t          flagCCQE;
 #  Bool_t          flagCC0pi;
 #  Bool_t          flagCCQELike;
 #  Bool_t          flagNCEL;
 #  Bool_t          flagNC0pi;
 #  Bool_t          flagCCcoh;
 #  Bool_t          flagNCcoh;
 #  Bool_t          flagCC1pip;
 #  Bool_t          flagNC1pip;
 #  Bool_t          flagCC1pim;
 #  Bool_t          flagNC1pim;
 #  Bool_t          flagCC1pi0;
 #  Bool_t          flagNC1pi0;
 #  Bool_t          flagCC0piMINERvA;
 #  Bool_t          flagCC0Pi_T2K_AnaI;
 #  Bool_t          flagCC0Pi_T2K_AnaII;
