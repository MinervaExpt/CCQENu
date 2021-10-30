# Real quick background fit code
import ROOT
from PlotUtils import MnvH1D
import os,sys,math
import ctypes
import json

# Filename
_filename = "BkgStudy_BkgStudy_10.root"
# names associated with each sample: data for full data, qelike for MC signal, qelikenot for MC bkg
sample_list = ["data","qelike","qelikenot"]
# Main config
_mainconfig = "main"
# Vars config
_varsconfg = "varsFile"
# Which variable you want to look at?
_variable = "recoil"
# Fit variable
_fit_variable = "Q2QE"

stack_plot_name = "OutHistsTest"

DO_SYSTEMATICS=False



# This is based off of how fitbins are made (i.e. making sidebands that have cuts on binedges of the variable you're making), and the histogram naming convention CCQENuMAT
def CleanUpHists(hist_dict):
    print("Cleaning up...")
    for fitbin in hist_dict.keys():
        for sample in hist_dict[fitbin].keys():
            # del hist_dict[fitbin][sample]['MnvH1D']
            hist_dict[fitbin][sample]['MnvH1D']=None
            hist_dict[fitbin][sample]['hists']=None
    print("Done")

def MakeHistDict(rfile,sample_list):
    histname_dict = {}
    hist_dict = {}
    histkeys_list = rfile.GetListOfKeys()
    for histkey in histkeys_list:
        histname = histkey.GetName()
        if histname.find("___") != -1:
            print("Checking the histogram: ", histname)
            splitnames_list = histname.split('___')
            print(splitnames_list)
            histotype = str(splitnames_list[0]) # h or h2D
            histosample = str(splitnames_list[1]) # QELike, QELikeAll, sidebands, fitbin names, etc.
            histocategory = str(splitnames_list[2]) # MC: qelike, qelikenot; Data: data
            histovariable = str(splitnames_list[3]) # Q2QE and Recoil are of particular interest for now 9/21
            # Get rid of 2D histos
            if histotype=='h2D':
                # print("Found h2D. Continuing...")
                continue
            # Get rid of non-sideband/fitbin samples
            if histosample in ['QELike','QElike','QELikeALL','QElikeALL']:
                # print("Not sideband. Continuing...")
                continue
            # Get rid of variables you're not interested in, configured at the top of the script
            if histovariable!=_variable:
                # print("Not right variable. Continuing...")
                continue
            # Only add categories that you're interested in, configured at the top of the script
            if not histocategory in sample_list:
                # print("Not right category. Continuing...")
                continue
            else:
                if histosample in hist_dict:
                    if histocategory in hist_dict[histosample]:
                        print('Category ',histocategory,' for the fitbin ',histosample,' already in dictionary.\nSomething wrong for histo ',histname,'?')
                    else:
                        hist_dict[histosample][histocategory] = {'name':histname,'MnvH1D':None,'hists':None}
                        # hist_dict[histosample][histocategory] = {'name':histname,'MnvH1D':None}
                    print("Added it to the list")
                else:
                    hist_dict[histosample] = {histocategory:{'name':histname,'MnvH1D':None,'hists':None}}
                    # hist_dict[histosample] = {histocategory:{'name':histname,'MnvH1D':None}}
                    print("Added it to the list")
    # print(hist_dict)
    return hist_dict

def GetMnvHists(rfile,infitbin_dict,sample_list):
    fitbin_dict = infitbin_dict

    for sample in sample_list:
        hist_name = fitbin_dict[sample]['name']
        hist = rfile.Get(hist_name).Clone()
        print("Found ",sample," histogram...")
        fitbin_dict[sample]['MnvH1D'] = hist
    print("Making the MC total...")
    mc_hist = fitbin_dict['qelike']['MnvH1D'].Clone()
    mc_hist.Add(fitbin_dict['qelikenot']['MnvH1D'],1.0)
    fitbin_dict['mc'] = {'MnvH1D':mc_hist,'hists':None}

    data_hist= fitbin_dict['data']['MnvH1D'].Clone()
    area_scale = data_hist.Integral()/mc_hist.Integral()

    print("Scaling MC's to data...")
    for sample in fitbin_dict.keys():
        if sample != 'data':
            fitbin_dict[sample]['MnvH1D'].Scale(area_scale)
    return fitbin_dict

def GetUniverseHists(infitbin_dict,mcuniverse_names,DO_SYSTEMATICS=False):
    fitbin_dict = infitbin_dict
    for sample in fitbin_dict.keys():
        temp_dict = {}
        # Put CV universe in dict
        temp_dict['cv'] = [fitbin_dict[sample]['MnvH1D'].GetCVHistoWithStatError()]
        # Set if you want to do systematics at the top
        print("Before sys...")
        if sample!='data' and DO_SYSTEMATICS==True:
            names_list = mcuniverse_names
            # Get Systematic Universes
            # print(names_list)
            for name in names_list:
                print(name)
                n_universes = fitbin_dict[sample]['MnvH1D'].GetVertErrorBand(name).GetNHists()
                # print("n_universes ",n_universes)
                universehist_list = []
                for i in range(0,n_universes):
                    universehist_list.append(fitbin_dict[sample]['MnvH1D'].GetVertErrorBand(name).GetHist(i))
                temp_dict[name] = universehist_list
                # print("Added ",len(universehist_list))
            print(temp_dict.keys())
            print("Done with sys. Added ",len(temp_dict.keys())-1," sys universes...")
        fitbin_dict[sample]['hists'] = temp_dict
    return fitbin_dict

def RunFractionFitter(mc_hist,qelike_hist,qelikenot_hist,data_hist):
    # mc_int = [mc_hist.Integral()]
    # qelike_int = [qelike_hist.Integral()]
    # qelikenot_int = [qelikenot_hist.Integral()]
    converge_bool = False
    mc_error = ctypes.c_double(0)
    qelike_error = ctypes.c_double(0)
    qelikenot_error = ctypes.c_double(0)
    mc_int = mc_hist.IntegralAndError(0,mc_hist.GetNbinsX(),mc_error)
    qelike_int = qelike_hist.IntegralAndError(0,mc_hist.GetNbinsX(),qelike_error)
    qelikenot_int = qelikenot_hist.IntegralAndError(0,mc_hist.GetNbinsX(),qelikenot_error)


    qelike_frac = qelike_int/mc_int
    qelike_fracerr = math.sqrt((mc_error.value/mc_int)*(mc_error.value/mc_int)+(qelike_error.value/qelike_int)*(qelike_error.value/qelike_int))*qelike_frac
    # print(qelike_frac)
    qelikenot_frac = qelikenot_int/mc_int
    qelikenot_fracerr = math.sqrt((mc_error.value/mc_int)*(mc_error.value/mc_int)+(qelikenot_error.value/qelikenot_int)*(qelikenot_error.value/qelikenot_int))*qelikenot_frac
    # print(qelikenot_frac)

    frac_dict = {'qelike':[qelike_frac,qelike_fracerr],'qelikenot':[qelikenot_frac,qelikenot_fracerr]}
    mc_list = ROOT.TObjArray(2) # 3 for qelike, qelikenot, plus one
    mc_list.append(qelike_hist)
    mc_list.append(qelikenot_hist)

    fit = ROOT.TFractionFitter(data_hist,mc_list)
    virtual_fitter = fit.GetFitter()
    virtual_fitter.Config().ParSettings(0).Set('qelike',frac_dict['qelike'][0],0.02,0.0,1.0)
    virtual_fitter.Config().ParSettings(1).Set('qelikenot',frac_dict['qelikenot'][0],0.02,0.0,1.0)
    # Constrain background to go from zero to 1 only, first argument is the 'parameter number' corresponding to 'qelikenot'
    fit.Constrain(0,0.0,1.0)
    # fit.Constrain(1,0.0,1.0)
    # Only go up to 0.5 GeV recoil bin
    max_bin = qelike_hist.GetXaxis().FindBin(0.5)
    fit.SetRangeX(0,25)

    status = fit.Fit()
    if status !=0:
        print("WARNING: Fit did not converge...")
        # converge_bool = False # defaults to false
        return converge_bool, fit, frac_dict

    # chisq2 = fit.GetChisquare()
    # print("Chisquared from fit: ",chisq2,", NDF: ",fit.GetNDF())
    if status==0:
        converge_bool = True
        return converge_bool, fit, frac_dict

def GetFitResults(fit,data_hist):
    fit_chi2 = fit.GetChisquare()
    fit_ndf = fit.GetNDF()


    # calc_chi2, calc_ndf = GetChi2NDF(fit_plot,data_hist)

    print("fit's chi2, ndf: ", fit_chi2, fit_ndf)
    # print("calculated chi2, ndf: ",calc_chi2,calc_ndf)
    result_hist = fit.GetPlot()
    # data_hist.Draw("EP")
    # result_hist.Draw("SAME")

    return result_hist,fit_chi2,fit_ndf

def CalculateScaleFactor(fit,frac_dict,in_sample_list = ['qelike','qelikenot']):
    scalefactor_list = []
    for i in range(len(in_sample_list)):
        sample = sample_list[i]
        prefit_frac = frac_dict[sample][0]
        prefit_err = frac_dict[sample][1]
        fit_frac = ctypes.c_double(0)
        fit_err = ctypes.c_double(0)
        fit.GetResult(i,fit_frac,fit_err)
        fit_frac = fit_frac.value
        fit_err = fit_err.value

        # TODO: How will systematics work here? Find scale factor for all universes, then combine to make a scale factor MnvH1D? Only need to find stat error for just CV, not for the systematic universes.
        scalefactor = fit_frac/prefit_frac
        # scalefactor_err = fit_err/prefit_frac # Idk if this is right...
        scalefactor_err = scalefactor*math.sqrt(((fit_err*fit_err)/(fit_frac*fit_frac))+((prefit_err*prefit_err)/(prefit_frac*prefit_frac))) # Adding fractional stat uncertainty
        # print("Scale factor: ",scalefactor," err ",scalefactor_err)
        scalefactor_tuple = (scalefactor,scalefactor_err)
        scalefactor_list.append(scalefactor_tuple)
    return scalefactor_list

def GetFitBinning(rfile):
    varsFile = rfile.Get("varsFile").GetTitle()
    vars_dict = json.loads(varsFile)
    binning = vars_dict['1D'][_fit_variable]['bins']
    return binning

def GetDummyHistCV(rfile):
    histkeys_list = rfile.GetListOfKeys()
    for histkey in histkeys_list:
        histname = histkey.GetName()
        if histname.find("___Q2QE___")==-1:
            continue
        else:
            dummyhist_cv = rfile.Get(histname).GetCVHistoWithStatError().Clone()
            print("Found hist to copy as dummy: ",histname)
            return dummyhist_cv
    print("No suitable hist to make a dummy with. Exiting...")
    sys.exit()

def MakeScaleFactorHist(rfile,scalefactor_dict):
    scalefactor_hist = GetDummyHistCV(rfile)
    bin=1
    for fitbin in scalefactor_dict.keys():
        scalefactor_hist.SetBinContent(bin,scalefactor_dict[fitbin][0])
        scalefactor_hist.SetBinError(bin,scalefactor_dict[fitbin][1])
        bin+=1
    scalefactor_hist.SetName("ScaleFactor_Q2QE")
    scalefactor_hist.SetTitle("Background scale factor in Q2QE")
    scalefactor_hist.GetYaxis().SetTitle("Scale Factor")
    return scalefactor_hist

def InitializeCanvas(canvas, canvas_name):
    canvas.cd()
    canvas.SetLeftMargin(0.15)
    canvas.SetRightMargin(0.15)
    canvas.SetBottomMargin(0.15)
    canvas.SetTopMargin(0.15)

def InitializeLegend():
    legend = ROOT.TLegend(0.55,0.54,0.9,0.89)
    legend.SetNColumns(2)
    legend.SetBorderSize(1)
    return legend

def MakeStackPlot(hist_list,hist_name_list,legend,fill_bool,color_list=[]):
    stack = ROOT.THStack("stack",str(hist_name_list[0]+"_"+hist_name_list[1]))
    if len(hist_list)!=len(color_list):
        ROOT.gStyle.SetPalette(ROOT.kRainBow)
    for i in range(len(hist_name_list)):
        if fill_bool==True:
            hist_list[i].SetFillStyle(3224+i)
        elif fill_bool==False:
            hist_list[i].SetFillStyle(0)
            hist_list[i].SetLineWidth(2)
        if len(hist_list)==len(color_list):
            hist_list[i].SetLineColor(color_list[i])
            if fill_bool:
                hist_list[i].SetFillColor(color_list[i])
        legend.AddEntry(hist_list[i],hist_name_list[i])
        stack.Add(hist_list[i])
    return stack

def MakeDataMCPlot(canvas,title,data_hist,mc_tot_hist,qelike_hist,qelikenot_hist,fit_bool=False):
    # TODO: initialize fit, title, name, data_hist, qelike(not)_hist before, frac
    stack_name_list = ['QElike','QElikenot']
    legend = InitializeLegend()

    name = title.replace(" ","_")
    # Somethings are different if working on fits
    if fit_bool:
        stack_name_list = ['QElike After Fit','QElikenot After Fit']

        title+=" After Fit"
        name+="_After_Fit"

        mc_tot_hist.SetLineColor(ROOT.kGreen)
        legend.AddEntry(mc_tot_hist,"Prefit MC Total")

    data_hist.SetLineColor(ROOT.kBlack)
    legend.AddEntry(data_hist,"Total Data")

    stack = MakeStackPlot([qelike_hist,qelikenot_hist],stack_name_list,legend,True,[ROOT.kBlue,ROOT.kRed])

    # stack.Draw("HIST, pfc") # If you want to use the color palette to color the stacked hist
    stack.Draw("HIST")
    data_hist.Draw("PE,same")
    if fit_bool:
        mc_tot_hist.Draw("HIST,same")
    legend.Draw("same")

    canvas.Print(canvas.GetName(),str("Title: "+name))

def MakeBeforeAfterPlot(canvas, title, data_hist, nofit_qelike_hist, nofit_qelikenot_hist, fit_qelike_hist, fit_qelikenot_hist):
    # TODO: initialize fit, title, name, data_hist, qelike(not)_hist before, frac
    legend = InitializeLegend()

    name = title.replace(" ","_")
    # Somethings are different if working on fits

    data_hist.SetLineColor(ROOT.kBlack)
    legend.AddEntry(data_hist,"Total Data")

    fit_name_list = ['QElike After Fit','QElikenot After Fit']
    fit_stack = MakeStackPlot([fit_qelike_hist,fit_qelikenot_hist], fit_name_list, legend, True, [ROOT.kBlue,ROOT.kRed])

    nofit_name_list = ['QElike','QElikenot']
    nofit_stack = MakeStackPlot([nofit_qelike_hist,nofit_qelikenot_hist], nofit_name_list, legend, False, [ROOT.kTeal,ROOT.kViolet])

    # stack.Draw("HIST, pfc") # If you want to use the color palette to color the stacked hist
    fit_stack.Draw("HIST")
    data_hist.Draw("PE,same")
    nofit_stack.Draw("HIST,NOCLEAR,same")
    legend.Draw("same")

    canvas.Print(canvas.GetName(),str("Title: "+name))



def main():
    # DO_SYSTEMATICS = True

    # Read in a file
    if len(sys.argv)<1:
        filename = _filename
    else:
        filename = sys.argv[1]
    infile = ROOT.TFile(filename,"READONLY")
    # GetFitBinning(infile)

    # Make dictionary from the inputs
    emptyhist_dict = MakeHistDict(infile,sample_list)
    hist_dict = {} # Doing this outside, since it makes clean up easier
    scalefactor_dict = {}
    fit_dict = {} # fit_dict = {fitbin:{universe_name:{'converges':[converge_bool,...],'fit':[fit,...],'frac':[{'qelike':[frac,staterr],'qelikenot':[frac,staterr]},...]}}}
    print("Making stacked plots...")
    stack_canvas = ROOT.TCanvas(str(stack_plot_name+".pdf"))
    InitializeCanvas(stack_canvas,stack_plot_name)
    stack_canvas.Print(str(stack_plot_name+".pdf["),"pdf")

    for fitbin in emptyhist_dict.keys():
        # fitbin_dict = {}
        print("Getting hists for fitbin:",fitbin,"...")
        hist_dict[fitbin] = GetMnvHists(infile,emptyhist_dict[fitbin],sample_list)

        # TODO: Get list of systematic universes with number of hists in each
        # TODO: RunFRactionFitter over CV's, then systematics (This may affect how scale factor is calculated...)
        print("Pulling out universe hists...")
        mcuniverse_names = hist_dict[fitbin]['mc']['MnvH1D'].GetVertErrorBandNames()
        hist_dict[fitbin] = GetUniverseHists(hist_dict[fitbin],mcuniverse_names,DO_SYSTEMATICS)

        print("Running Fraction fitter...")
        uni_fit_dict = {}
        data_cv_hist = hist_dict[fitbin]['data']['hists']['cv'][0] # No systematic universes for data, so no universes to loop over
        # print(hist_dict[fitbin]['mc']['hists'].keys())
        for mcuni_name in hist_dict[fitbin]['mc']['hists'].keys():
            # print("MC Universe name",mcuni_name)
            temp_converge_list = []
            temp_fit_list = []
            temp_frac_list = []
            temp_scale_list = []
            for mc_uni in range(0,len(hist_dict[fitbin]['mc']['hists'][mcuni_name])):

                mc_hist = hist_dict[fitbin]['mc']['hists'][mcuni_name][mc_uni].Clone()
                qelike_hist = hist_dict[fitbin]['qelike']['hists'][mcuni_name][mc_uni].Clone()
                qelikenot_hist = hist_dict[fitbin]['qelikenot']['hists'][mcuni_name][mc_uni].Clone()

                # fit is type TFractionFitter, will be the output of the fit. frac_dict is a dictionary of the fractions (with stat error) before the fit
                converge_bool,fit,frac_dict = RunFractionFitter(mc_hist,qelike_hist,qelikenot_hist,data_cv_hist)
                scalefactor_list = CalculateScaleFactor(fit,fit_dict[fitbin][universe]['frac'][i],'qelike')[0]
                temp_converge_list.append(converge_bool)
                temp_fit_list.append(fit)
                temp_frac_list.append(frac_dict)
                temp_scale_list.append(scalefactor_list)

                data_hist = data_cv_hist.Clone()
                mc_tot_hist = mc_hist.Clone()

                # fit_qelike_hist = qelike_hist.Clone()
                # qelike_scale = scalefactor_list[0][0]
                # qelike_scale_err = scalefactor_list[0][1]
                # fit_qelike_hist.Scale(qelike_scale)
                fit_qelike_hist = fit.GetMCPrediction(0)

                # fit_qelikenot_hist = qelikenot_hist.Clone()
                # qelikenot_scale = scalefactor_list[1][0]
                # qelikenot_scale_err = scalefactor_list[1][1]
                # fit_qelikenot_hist.Scale(qelikenot_scale)
                fit_qelikenot_hist = fit.GetMCPrediction(1)

                title = fitbin+" "+mcuni_name+" "+str(mc_uni)
                ba_title = title+" Before After"
                MakeBeforeAfterPlot(stack_canvas, ba_title, data_hist.Clone(), qelike_hist.Clone(), qelikenot_hist.Clone(), fit_qelike_hist.Clone(), fit_qelikenot_hist.Clone())
                MakeDataMCPlot(stack_canvas,title,data_hist.Clone(),mc_tot_hist.Clone(),qelike_hist.Clone(),qelikenot_hist.Clone(),False)
                MakeDataMCPlot(stack_canvas,title,data_hist.Clone(),mc_tot_hist.Clone(),fit_qelike_hist.Clone(),fit_qelikenot_hist.Clone(),True)


            uni_fit_dict[mcuni_name] = {'fit':temp_fit_list,'converges':temp_converge_list,'frac':temp_frac_list,'scale':temp_scale_list}
        fit_dict[fitbin] = uni_fit_dict

        print("Done running fraction fitter...")

        print("Done with fitbin ", fitbin)
    stack_canvas.Print(str(stack_plot_name+".pdf]"),"pdf")


    # outfile.Close()

    # print(scalefactor_dict)
    # Get your fits made
    # fit_dict = {}
    # # print(scalefactor_dict)
    # scalefactor_hist = MakeScaleFactorHist(infile,scalefactor_dict)
    # outfilename = filename.replace(".root","ScaleFactorHist.root")
    # outfile = ROOT.TFile(outfilename,"RECREATE")
    # outfile.cd()
    # scalefactor_hist.Write()
    # outfile.Close()

    CleanUpHists(hist_dict)


if __name__=="__main__":
    main()
