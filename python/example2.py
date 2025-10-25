import ROOT

import numpy as np
class chi2fct3d_angles:
    def __init__( self ):
        #ROOT.TPyMultiGenFunction.__init__( self, self )
        self.samplesize = 0
        self.points = np.zeros(12)
        self.errors = np.zeros(12)

    def NDim( self ): # total number of variables
        return 4.0

    def SetVals(self, samplesizet, pointst, errorst):
        self.samplesize = samplesizet
        self.points = pointst
        self.errors = errorst
    
    def DoEval( self, pars):
        chisq = []   
        #print ("DoEval pars", pars)
        for i in range(0,self.samplesize):
            errsx = self.errors[i][0]**2
            errsy = self.errors[i][1]**2
            errsz = self.errors[i][2]**2

            xvalue = self.points[i][0]
            yvalue = self.points[i][1]
            zvalue = self.points[i][2]
            distx = xvalue - pars[0]
            disty = yvalue - pars[1]
            distz = zvalue - pars[2]
            
            distx = distx**2
            disty = disty**2
            distz = distz**2       
            chisq.append((distx + disty + distz)/(errsx + errsy + errsz)) # add chisq of point i

        chisq = np.sum(np.array(chisq))
        print ("chisq", chisq)
        return chisq 
    
    def to_root_math_functor( self ):
        self._do_eval_callable = self.DoEval
        functor = ROOT.Math.Functor(self._do_eval_callable, int(self.NDim()))
        return functor


minimizer = ROOT.Minuit2.Minuit2Minimizer(0) 

# print errors etc during the minimisation
minimizer.SetPrintLevel(3) 
       
errorfct = chi2fct3d_angles() # define the function to minimise
samplesize = 25
points = np.zeros((samplesize, 3)) # points to fit
errors = np.zeros((samplesize, 3)) # errors of the points
for i in range(0, samplesize):
    points[i][0] = i * 0.1
    points[i][1] = i * 0.2
    points[i][2] = i * 0.3
    errors[i][0] = 0.01 + i * 0.001
    errors[i][1] = 0.02 + i * 0.001
    errors[i][2] = 0.03 + i * 0.001
print("points", points)
errorfct.SetVals(samplesize, points, errors)
errorfunctor = errorfct.to_root_math_functor()
minimizer.SetFunction(errorfunctor)
        
minimizer.SetMaxFunctionCalls(500)
minimizer.SetMaxIterations(500)
minimizer.SetTolerance(0.001)
                
pars = np.ones(4) # initial parameters
step = np.ones(4) * 0.1 # steps for the parameters
#adding variables without limited range:
minimizer.SetVariable(0,"px", pars[0], step[0])
minimizer.SetVariable(1,"pz", pars[1], step[1])
minimizer.SetVariable(2,"phi", pars[2], step[2])
minimizer.SetVariable(3,"theta", pars[3], step[3]) 
                 
retval_min = minimizer.Minimize() # start the minimiser
        
minval = minimizer.MinValue() # minvalue of the function to minimise (chi2fct3d_angles() in this case)
        
stat = minimizer.Status()
print(stat)
        
covar_stat = minimizer.CovMatrixStatus()

temp_cov = []

ret_params = minimizer.X() # parameters of the fit
ret_errors = minimizer.Errors() # errors of the fit
final_lines_params = [] # list to save all the parameters of the track
covar_mat_status = [] # list to save the covariance matrix 
chisq = [] 
conv_status = [] # list to save the status of the minimisation             
final_params = []
for i in range(0,pars.size):
    final_params.append(ret_params[i])
    for j in range(0,pars.size):
        #print minimizer.CovMatrix(i,j)
        temp_cov.append(minimizer.CovMatrix(i,j))
cov_matrices=[]
cov_matrices.append(temp_cov)
covar_mat_status.append(covar_stat)
        
final_lines_params.append(final_params)                   
chisq.append(minval)
conv_status.append(stat)