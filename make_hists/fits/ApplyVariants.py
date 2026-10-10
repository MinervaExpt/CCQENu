from string import Template
import os,sys
from ROOT import TFile, TH1D, TH2D, TMatrixDSym, TVectorD,BindObject, AddressOf
from PlotUtils import MnvH1D, MnvH2D, MnvVertErrorBand
import commentjson as json
from MatrixUtils import SyncBands, copyThings
from MatrixUtils import ToMatrixDSym, ToVectorD, extrabands
                # have done the fit, now rescale all histograms by the appropriate scale factors

DEBUG=False

def nameToTag(histname):
    ''' make a tag from a histogram name '''
    fields = histname.split("___")
    if len(fields)< 5: return None
    # this should be variable sample category datatype
    tag = (fields[3],fields[1],fields[2],fields[4])
    return tag

def ClassifyHists(f):
    ''' read in histograms '''
    Hists1D = {}
    Hists2D = {}
    list1D = []
    list2D = []
    for key in f.GetListOfKeys():
        obj = key.ReadObj()
        name = obj.GetName()
        if "types" in name: continue
        #obj.Print()
        if "h___" in name:
            list1D.append(name)
        if "h2d__" in name:
            list2D.append(name)

    print ("try to classify")
    for name in list1D:
        tag = nameToTag(name)   
        if tag == None: continue
        category = tag[2]
        if "h___"  in name: 
            hist = MnvH1D()
            hist = f.Get(name)            
            Hists1D[tag] = hist
            hist.Print()
            
    
        if "h2D__" in name:

            tag = nameToTag(name)       
            if tag == None: continue
            hist = MnvH2D()
            hist = f.Get(name)
            Hists2D[tag] = hist
            hist.Print()
        
    return (Hists1D,Hists2D)






def driver(filename):

    f = TFile(filename, "READONLY")

    fconfig = json.loads(f.Get("Fit").GetTitle())
    fitvar = fconfig["Variable"]
    categories = fconfig["Categories"]
    fithists = {}
    if DEBUG: f.ls()
    samples = fconfig["Sidebands"]
    print ("samples",samples)
    mconfig = json.loads(f.Get("main").GetTitle())
    if DEBUG: print (list(mconfig.keys()))
    variables = mconfig["AnalyzeVariables"]
    parametersHist = MnvH1D()
    covarianceHist = MnvH2D()
    npars = 0
    variants = TVectorD(npars)

    # have to find the parameters as fitter stores alphabetically

    for sample in samples:
        parametername=f"parameters_h___{sample}___data___{fitvar}___reconstructed"
        if DEBUG: print (parametername)
        #parametersHist = MnvH1D()
        #covarianceHist = MnvH2D()
        #   correlationhist = MnvH2D()
        tmphist = f.Get(parametername)
        print ("type",tmphist)
        if not tmphist: 
            print (" not the right sample", sample, parametersHist)
            continue
        parametersHist = tmphist
        print ("type",parametersHist)
        parametersHist.SetDirectory(0)
        if DEBUG: print ("parameters",parametersHist)
        covarianceHist = f.Get(parametername.replace("parameters","covariance"))
        covarianceHist.SetDirectory(0)
        npars = parametersHist.GetNbinsX()
        covarianceMatrix = TMatrixDSym(npars,npars)
        covarianceMatrix = ToMatrixDSym(covarianceHist)
        #variants = TVectorD(npars) # this stores the fit variations orthogonally
        variants = extrabands(covarianceMatrix)
        if DEBUG: print ("variants",variants)

    template = fconfig["Template"]
    parameters = {}
    covariance = {}
    correlation = {}
    universes = ["CV"]+list(parametersHist.GetVertErrorBandNames())
    if DEBUG:
        universes = universes[0:3]
        variables = variables[0:2]
    parameters = {}
    NDim= 0
    cattoint = {}
    inttocat = {}
    i = 0
    for cat in categories:
        cattoint[cat] = i
        inttocat[i] = cat
        i+=1
    #print (cattoint)
    #if DEBUG: print (universes)

    for univ in universes:     
        ahist = TH1D()
        if univ == "CV":
            nuniv = 1
            ahist = parametersHist.Clone()
            ahist.SetDirectory(0)
        else:
            nuniv = parametersHist.GetVertErrorBand(univ).GetNHists() 
        for i in range(nuniv):
            if univ != "CV":
                ahist = parametersHist.GetVertErrorBand(univ).GetHist(i)
            NDim= ahist.GetNbinsX()
            tag = (univ,i)
            parameters[tag]={}
            for j in range(NDim):    
                parameters[tag][j] = ahist.GetBinContent(j + 1)
            if DEBUG: print (tag,parameters[tag])
    unfitHists = {}
    fitHists = {}
    signal = "QElike"
    signalcat = "qelike"

    h_pot = TH1D()
    h_pot = f.Get("POT_summary")
    h_pot.Print("ALL")

    # dataPOT = h_pot.GetBinContent(1)
    # mcPOTprescaled = h_pot.GetBinContent(3)
    # POTScale = dataPOT / mcPOTprescaled

    #unfitHists,twoD = ClassifyHists(f,POTScale)

    for variable in variables:
        for sample in samples:
            for category in fconfig["Categories"]+["data"]:
                
                htag = (variable,sample,category,"reconstructed")
                data_type = "reconstructed"
                name = (template%(sample,category,variable))
                ahist = MnvH1D()
                if DEBUG: print ("look for",name)
                
                ahist = f.Get(name)
                ahist.SetDirectory(0)
                
                    
                if not ahist:
                    if DEBUG: print("Could not find histogram " , name )
                    continue
                # if category != "data":
                #     ahist.Scale(POTScale)
                # ahist.SetName(ahist.GetName()+"___POTScaled")
                unfitHists[htag] = ahist
    
    newHists = ApplyVariants(fitvar,unfitHists, parameters, covariance, correlation, cattoint, variants)
    # try background substraction for reconstructed data without a fit first
    noscale = BkgSub(unfitHists,variables,samples,categories,signalcat,"reconstructed")
    scale = BkgSub(unfitHists,variables,samples,categories,signalcat,"scaled")
    
    
    g = TFile(filename.replace(".root","_scaled.root"), "RECREATE")
    f.cd()
    copyThings(f,g,["types"])
    if DEBUG: print ("output = ",g.GetName())
    g.cd()

    for ntag in unfitHists.keys():
        print ("write",ntag,unfitHists[ntag].GetName(),unfitHists[ntag].GetEntries(),unfitHists[ntag].Integral())
        unfitHists[ntag].Write()
    for ntag in newHists.keys():
        print ("write",ntag,newHists[ntag].GetName(),newHists[ntag].GetEntries(),newHists[ntag].Integral())
        newHists[ntag].Write()
    for ntag in noscale.keys():
        print ("write",ntag,noscale[ntag].GetName(),noscale[ntag].GetEntries(),noscale[ntag].Integral())
        noscale[ntag].Write()
    for ntag in scale.keys():
        print ("write",ntag,scale[ntag].GetName(),scale[ntag].GetEntries(),scale[ntag].Integral())
        scale[ntag].Write()
    print ("wrote it out")
    #g.ls()
    g.Close()
    #f.Close()

def BkgSub(Hists,variables,samples,categories,signalcat,type="scaled"):
    moreHists = {}
    for variable in variables:
        for sample in samples:
            stag = (variable,sample,signalcat,type)
            if stag not in Hists.keys():
                print (" could not find ",stag)
                continue

            ## make and store the total background

            bkgname = Hists[stag].GetName().replace(signalcat,"bkg").replace("reconstructed","scaled")
            btag = (variable,sample,"bkg",type)
            # make an empty histogram to sum things up. 
            bkgHist = Hists[stag].Clone(bkgname)
            bkgHist.SetDirectory(0)
            bkgHist.Reset()

            for category in categories:
                if category == signalcat:
                    continue
                ctag = (variable,sample,category,type)
                bkgHist.Add(Hists[ctag],1.0)
            moreHists[btag] = bkgHist

            ## add in the signal to get the total 
            totname = bkgHist.GetName().replace("bkg","tot")
            ttag = (variable,sample,"tot",type)
            totHist = bkgHist.Clone(totname)
            totHist.SetDirectory(0)
            totHist.Add(Hists[stag],1.0)
            moreHists[ttag] = totHist

            ## substract the background from the data
            dtag = (variable,sample,"data","reconstructed")
            bkgsubname = Hists[dtag].GetName().replace("data","bkgsub").replace("reconstructed","scaled")
            bkgsubHist = Hists[dtag].Clone(bkgsubname)
            bkgsubHist.SetDirectory(0)
            bkgsubHist.Add(bkgHist,-1.)
            bkgtag = (variable,sample,"bkgsub",type)
            moreHists[bkgtag] = bkgsubHist
            if DEBUG:
                bkgHist.Print()
                totHist.Print()
                bkgsubHist.Print()
    return moreHists
            
def ApplyVariants(fitvar, unfitHists, parameters, covariance, correlation, cattoint, variants):
    newHists = {}
    for htag in unfitHists.keys(): 
        unfitHists[htag].SetDirectory(0)  
        variable = htag[0]     
        sample = htag[1] 
        category = htag[2]
        if category == "data": continue
        icat = cattoint[category]
        ntag = (variable,sample,category,"scaled")
        newname =  unfitHists[htag].GetName()
        newHists[ntag] = MnvH1D()
        newHists[ntag] = MnvH1D(unfitHists[htag].GetCVHistoWithStatError())
        newHists[ntag].SetDirectory(0)
        newHists[ntag].SetName(unfitHists[htag].GetName().replace("_reconstructed","_scaled"))
        #nbins = ahist.GetNbinsX()
        universes = ["CV"] + list(unfitHists[htag].GetVertErrorBandNames())
        if DEBUG: 
            universes = universes[0:3] 
        for univ in universes:
            if (univ == "CV"): 
                nuniv = 1
                for iuniv in range(nuniv): 
                    ptag = (univ,iuniv)
                    if (ptag in parameters):
                        scale = parameters[ptag][icat]
                    else:
                        print ("ptag does not exist",ptag)
                    
                    if DEBUG: print("scale CV" , newname , " " , iuniv , " " , scale )
                        #fitHists[myname][i].Print()
                        #unfitHists[myname][i].Print()
                    newHists[ntag].Scale(scale)
                    # for j in range(1,nbins+1):
                    #     fitHists[htag].SetBinContent(j, unfitHists[sample][i].GetBinContent(j) * scale)
                    #     fitHists[htag].SetBinError(j, unfitHists[sample][i].GetBinError(j) * scale)
                        
                    if DEBUG:
                        newHists[ntag].Print()
                        unfitHists[htag].Print()
                     
            else:   # not CV
                if DEBUG: print(" non CV Universe" , univ )
                # scale the error bands appropriately and record the changes in fcn, parameter, covariance
                # fcnhist = TH1D()
                # fcnhist = fcn.GetVertErrorBand(univ).GetHist(iuniv)
                # fcnhist.SetBinContent(1, mini2.MinValue())
                # phist = TH1D()
                # chist = TH2D()
                # corhist = TH2D()
                # phist = parameters.GetVertErrorBand(univ).GetHist(iuniv)
                # chist = covariance.GetVertErrorBand(univ).GetHist(iuniv)
                # corhist = correlation.GetVertErrorBand(univ).GetHist(iuniv)
                # for i in range(ncat): 
                #     phist.SetBinContent(i + 1, ScaleResults[i])
                #     for j in range(ncat): 
                #         chist.SetBinContent(i + 1, j + 1, mini2.CovMatrix(i, j))
                    
                
                # for i in range(Ndim):
                #     erri = phist.GetBinError(i + 1)
                #     for j in range(NDim):: 
                #         errj = phist.GetBinError(j + 1)
                #         corhist.SetBinContent(i + 1, j + 1, chist.GetBinContent(i + 1, j + 1) / erri / errj)
                    
                
                errorband = unfitHists[htag].GetVertErrorBand(univ)
                #newerrorband = fitHists[htag].GetVertErrorBand(univ)
                bands = []
                for iuniv in range(errorband.GetNHists()):
                     
                    newhist = TH1D()
                    ptag = (univ,iuniv)
                    if (ptag in parameters):
                        scale = parameters[ptag][icat]
                    else:
                        print ("ptag does not exist",ptag, parameters.keys())
                        continue
                    
                    scale = parameters[ptag][icat]
                    if DEBUG:
                        if DEBUG: print ("rescale",htag,scale)
                    
                    newhist = errorband.GetHist(iuniv).Clone()
                    newhist.SetDirectory(0)
                    if DEBUG: 
                        print ("before scaling")
                        newhist.Print()
                    newhist.Scale(scale)
                    if DEBUG:
                        print ("rescaled")
                        newhist.Print()
                    bands.append(newhist)
                test = newHists[ntag].AddVertErrorBand(univ,bands)

                if DEBUG:
                    if DEBUG: print ("did I add new bands",test)
                    oldband = unfitHists[htag].GetVertErrorBand(univ)
                    newband = newHists[ntag].GetVertErrorBand(univ)
                    nuniv = newband.GetNHists()
                    for iuniv in range(nuniv):
                        ahist = newband.GetHist(iuniv)
                        if DEBUG: print ("new")
                        ahist.Print()
                        if DEBUG: print ("old")
                        bhist = oldband.GetHist(iuniv)
                        bhist.Print()
        
                    # end of nuniv loop
        
            # end of universes loop
        # add in fit variations 
        if DEBUG: print ("Try doing fit variations",htag)

        neigen = 3
        fitscale = 10
        ncat = variants.GetNrows()
        variantsname = "FitVariations"
        newHists[ntag].PopVertErrorBand(variantsname)
        if fitscale != 1:
            variantsname = f"FitVariations_x{fitscale}"
        vhists = []
        ptag = ("CV",0) # use the CV fit variations
        for i in range(ncat):  # loop over categories for that sample
             for var in range (neigen):
                for k in range(2):
                    iuniv = var*2+k    
                    hist = newHists[ntag].GetCVHistoWithStatError().Clone()
                    hist.SetDirectory(0)
                    sign = (2*k)-1
                    # central value already scaled by the fit parameter so have to back it off. 
                    variation = (1. + variants[var][i] * sign/parameters[ptag][i]*fitscale)
                    hist.Scale(variation)    
                    vhists.append(hist)
                    #hist.Print("ALL")
                    print("varied by " , htag , " " , i , " " , iuniv , " " , parameters[ptag][i]*fitscale , " " , variants[var][i] , " " , variation , " " , parameters[ptag][i]*variation )
        print ("vhists",vhists)
        newHists[ntag].AddVertErrorBand(variantsname, vhists)  # only need neigen*2 HMS 2025-07-07
                                                
        if sample == "QElike":
            newHists[ntag].MnvH1DToCSV(newHists[ntag].GetName(),"./csv",1.,False)
            unfitHists[htag].MnvH1DToCSV(unfitHists[htag].GetName(),"./csv",1.,False)
        SyncBands(newHists[ntag],True)
        print ("made scaled ",ntag)

    return newHists


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python ApplyVariants.py <filename>")
        filename = "ptmu_Fit_minervame5A_MnvTunev2.root"
    else:
        filename = sys.argv[1]

    driver(filename)
