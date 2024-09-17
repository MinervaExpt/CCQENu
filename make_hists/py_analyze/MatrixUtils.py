import os,sys
from ROOT import TMatrixD,TMatrixDSym,TVectorD,TFile,TMatrixDSymEigen, TH1D, TH2D, TObjArray
from PlotUtils import MnvH1D,MnvVertErrorBand
import math

def map2TObjArray(thing):
    #print (thing)
    r = TObjArray()
    for it,val in thing.items():
        
        val.SetTitle(it)
        #print ("add to stack",it,val.GetTitle())
        r.Add(val)
    return r

def extrabands(cov):
    n = cov.GetNrows()
    E = TMatrixDSymEigen()
    E = TMatrixDSymEigen(cov)
    e = TVectorD()
    e = E.GetEigenValues()
    m = TMatrixD()
    m = E.GetEigenVectors()

    #e.Print()
    #m.Print()
    results = TMatrixD(n,n)
    count = 0
    for vi in range(0,n):
        if (vi > n): return results
        for j in range(0,n): 
            results[vi][j] = 0.0
        
        for j in range(0,n): 
            results[vi][j] += math.sqrt(e[vi]) * m[j][vi]
        
    
    #print ("uncertainty vectors")
    #results.Print()
    return results


def ToMatrixDSym(hist):
    n = hist.GetXaxis().GetNbins()
    m = hist.GetYaxis().GetNbins()
    print (n,m)
    matrix = TMatrixDSym()
    matrix.ResizeTo(n,m)
    for ii in range(0,n):
        i = ii+1
        for jj in range(0,m):
            j = jj + 1
            matrix[ii][jj] = hist.GetBinContent(i,j)
            #print (ii,jj,hist.GetBinContent(i,j))
    return matrix

def ToVectorD(hist):
    n = hist.GetXaxis().GetNbins()
     
    vector = TVectorD(n)
    for i in range(1,n+1):
        ii = i-1
        vector[ii] = hist.GetBinContent(i)
    return vector

def SyncBands(thehist):
  print (thehist.GetName())
  theCVHisto = thehist.GetCVHistoWithStatError()
  theCVHisto.SetDirectory(0);
  bandnames = thehist.GetErrorBandNames();
 
  for bandname in bandnames:
  
    band = MnvVertErrorBand()
    band = thehist.GetVertErrorBand(bandname)
   
    for i in range(0,band.GetNbinsX()+2):
      if(i < 4 and i != 0):
        #print ("Sync band ", thehist.GetName(), bandname, i, theCVHisto.GetBinContent(i), theCVHisto.GetBinContent(i)-band.GetBinContent(i))
        band.SetBinContent(i,theCVHisto.GetBinContent(i))
        band.SetBinError(i,theCVHisto.GetBinError(i))

def scaleHist(oldhist,index, parameters,covariance, newname):
    ncat = len(parameters)
    if oldhist.InheritsFrom("MnvH1D"):
        newhist = MnvH1D()
        #print ("rescale by",index,parameters[index])
        newhist = oldhist.Clone(newname)
        newhist.Scale(parameters[index])
        # newband = MnvVertErrorBand("FitVariations", newhist, varhists) 
        # newhist.AddVertErrorBandAndFillWithCV("FitVariations", ncat * 2)
        # errorband = MnvVertErrorBand()
        # errorband = newhist.GetVertErrorBand("FitVariations")

        variants = extrabands(covariance)
        varhists = []
        for var in range (0,ncat): #{ // loop over variations
            for k in range(0,2): 
                iuniv = var*2+k
                hist = TH1D()
                hist = newhist.GetCVHistoWithStatError() 
                sign = (2*k)-1
                # central value already scaled by the fit parameter so have to back it off. 
                variation = (1. + variants[var][index] * sign/parameters[index])
                hist.Scale(variation)
                varhists.append(hist)
        hist = TH1D()
        hist = newhist.GetCVHistoWithStatError() 
        #newband = MnvVertErrorBand()
        #newband = MnvVertErrorBand("FitVariations", hist, varhists) 
        newhist.AddVertErrorBand("FitVariations",varhists)
        return newhist
    else:
        
        if oldhist.InheritsFrom("TH2D"):
            newhist = TH2D()
        else:
            newhist = TH1D()
        #print ("rescale by",index,parameters[index])
        newhist = oldhist.Clone(newname)
        newhist.Scale(parameters[index])
        return newhist
    
def TexFigure(name,caption,label=None):
        if label is None: label = name
        label = label.replace(" ","-")
        s = "\\begin{figure}[ht]\n\\centering"
        s += "\\includegraphics[height=0.33\\textwidth]{%s}"%((name))
        #s += "\\caption{%s}\n"%caption
        #s += "\\label{fig:%s}\n"%label
        s += "\\end{figure}\n"
        return s

def TexFigure3(name1,name2,name3,name4,caption,label=None):
    if label is None: label = name1
    label = label.replace(" ","-")
   
    s = "\\begin{figure}[ht]\n\\centering\n"
    s += "\\includegraphics[height=0.4\\textwidth]{%s}\n"%((name1))
    s += "\\includegraphics[height=0.4\\textwidth]{%s}\n"%((name2))
    s += "\\includegraphics[height=0.4\\textwidth]{%s}\n"%((name3))
    s += "\\includegraphics[height=0.4\\textwidth]{%s}\n"%((name4))
    s += "\\caption{%s}\n"%caption.replace("_","\\_")
    #s += "\\label{fig:%s}\n"%label
    s += "\\end{figure}\n"
    s += "\\pagebreak\n"
    return s




if __name__ == "__main__":

    f = TFile.Open("../BDT_3.root")
    h_covariance = f.Get("covariance_h___1track___data___bdtgQELike___reconstructed")
    h_covariance.Print()
    new = ToMatrixDSym(h_covariance)
    new.Print()

def checktag(keys, tag) :
    count = 0
    for x in keys:
        if tag in x: count += 1
    return count
    #return std.count(keys.begin(), keys.end(), tag) > 0

def ZeroDiagonal(m):
    print(" TRACE: enter ZeroDiagonal  " )
    newm = TMatrixD(m)
    n = newm.GetNrows()
    for i in range(0,n): 
        newm[i][i] = 0
    return newm