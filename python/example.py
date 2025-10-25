import ROOT

from array import array

class MyMultiGenFCN:

    def DoEval( self, x ):
        return (x[0] - 42) * (x[0] - 42)

    def to_root_math_functor(self):
        # keep the callable alive for the functor:
        self._do_eval_callable = self.DoEval
        functor = ROOT.Math.Functor(self._do_eval_callable, 1)
        return functor

def main():
    fitter = ROOT.Fit.Fitter()
    myMultiGenFCN = MyMultiGenFCN()
    functor = myMultiGenFCN.to_root_math_functor()

    params = array('d', [1.])
    fitter.FitFCN(functor, params)
    fitter.Result().Print(ROOT.std.cout, True)
    print (fitter.Result())
if __name__ == '__main__':
    main()