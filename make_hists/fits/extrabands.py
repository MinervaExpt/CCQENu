import os,sys
from ROOT import *
from PlotUtils import *
TMatrixD  extrabands(TMatrixDSym cov) 
    #n = parameters.size()
    #n = 5
    n = cov.GetNrows()

    TMatrixDSymEigen E = TMatrixDSymEigen(cov)
    TVectorD  e = E.GetEigenValues()
    TMatrixD  m = E.GetEigenVectors()

    e.Print()
    m.Print()
    TMatrixD results(n,n)
    count = 0
    forvi = 0 vi < n  vi++:
        count++
        if (count > 100): return results
        if (vi > n): return results
        forj = 0 j < n  j++:
            results[vi][j] = 0.0
        
        forj = 0 j < n  j++:
           # print("eigen " , vi , " " , j , " " , results[vi][j] , " " , e[vi][vi] ,  " " , m[vi][j] )
            results[vi][j] += std.sqrt(e[vi]) * m[j][vi]
        
    
    
    results.Print()
    return results
