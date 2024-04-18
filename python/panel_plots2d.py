# program to plot stacked histograms produced by the sidebands program in CCQENu
# assumes the plots have tag type_mcint_type as the 5th field in their name
# does tuned histograms if there is a 2nd argument - any second argument
# hms 9-10-2023



import sys,os,math
import ROOT
from ROOT import gROOT,gStyle, TFile,THStack,TH1D,TCanvas,TColor,TObjArray,TH2F,THStack,TFractionFitter,TLegend,TLatex, TString
import PlotUtils
import math
# from PlotUtils import HyperDimLinearizer, GridCanvas

TEST=False
noData=False  # use this to plot MC only types
sigtop=True # use this to place signal on top of background

frac_max = 0.7

pzmuHDbins = [1.5, 3., 6., 10., 15.]
ptmuHDbins = [0.0,0.1,0.3,0.7,1.25,2.5]
recoilHDbins = [0.0,0.05,0.1,0.15,0.2,0.25,0.3,0.35,0.4,0.45,0.5]
global_bins3d = [recoilHDbins,ptmuHDbins,pzmuHDbins]
analysistype = 1 # for 1D full linear
IncludeSysBool = False
pzmu_ptmu_recoil_bins3d = [pzmuHDbins,ptmuHDbins,recoilHDbins]
recoil_ptmu_pzmu_bins3d = [recoilHDbins,ptmuHDbins,pzmuHDbins]
ptmu_pzmu_recoil_bins3d = [ptmuHDbins,pzmuHDbins,recoilHDbins]
global_bins_dict = {"pzmu_ptmu_recoil":[pzmuHDbins,ptmuHDbins,recoilHDbins], "recoil_ptmu_pzmu":[recoilHDbins,ptmuHDbins,pzmuHDbins], "ptmu_pzmu_recoil": [ptmuHDbins,pzmuHDbins,recoilHDbins]}
# Plotting and canvas stuff

vars_todo = ["pzmu_ptmu"]
samples_todo = ["QElike"]
order_signal = list(["other","multipion","neutralpion","chargedpion","qelike","data"])
order_sideband = list(["qelike","other","multipion","neutralpion","chargedpion","data"])

catscolors = {
"data":ROOT.kBlack, 
"qelike":ROOT.kBlue-6,
"chargedpion":ROOT.kMagenta-6,
"neutralpion":ROOT.kRed-6,
"multipion":ROOT.kGreen-6,
"other":ROOT.kYellow-6}

catsnames = {
"data":"data", 
"qelike":"QElike",
"chargedpion":"1#pi^{+/-}",
"neutralpion":"1#pi^{0}",
"multipion":"N#pi",
"other":"Other"}

y_axis_label = "p_{||}"
x_axis_label = "p_{T}"
panel_title = "p_{T} vs p_{||}"
def CCQECanvas(name,title,xsize=750,ysize=750):
    c2 = ROOT.TCanvas(name,title,xsize,ysize)
    c2.SetLeftMargin(0.20)
    c2.SetRightMargin(0.05)
    c2.SetBottomMargin(0.15)
    return c2

def CCQELegend(xlow,ylow,xhigh,yhigh):
    leg = ROOT.TLegend(xlow,ylow,xhigh,yhigh)
    leg.SetFillStyle(0)
    leg.SetBorderSize(0)
    leg.SetTextSize(0.03)
    leg.SetNColumns(3)
    return leg

def PanelCanvas(name, n_xbins, n_ybins, x_size=1000, y_size=750):
    """name is the name for the canvas
    title is the title for the canvas
    n_xbins and n_ybins are number of x and y bins of each 2D hist
    x_size and y_size is the dimensions of the canvas
    returns a grid canvas with the correct number of pads"""

    # TODO: These might need the n_xbins swapped for n_ybins (currently set up basically how it is in Dan's), maybe just hard code these for now?
    grid_x = int(math.sqrt(n_ybins)+1)
    grid_y = int(n_ybins/(grid_x-1))

    if grid_x*grid_y-n_ybins==grid_x:
        grid_y-=1
    
    print("PanelCanvas: Making a grid canvas named "+name+" with a grid of ",n_xbins,"    ",n_ybins,"    ",grid_x,"    ",grid_y)

    # gc2 = PlotUtils.GridCanvas(name, grid_x, grid_y, x_size, y_size)
    gc2 = PlotUtils.GridCanvas(name, grid_x, grid_y, x_size, y_size)
    gc2.SetRightMargin(0.01)
    gc2.SetLeftMargin(0.1)
    gc2.ResetPads()

    return gc2

def GetBinVolumeList(hyperdim, n_ybins, zbin):
    yz_binvol_list = []
    for ybin in range(n_ybins):
        binvol = hyperdim.GetBinVolume([1,ybin,zbin], False)
        yz_binvol_list.append(binvol)
    return yz_binvol_list

def MakeDataMCStackLists(hist_dict, stack_name,sample="QElike",multipliers=[]):
    n_ybins = hist_dict["data"]["reconstructed"].GetNbinsY()
    stack_list = []
    data_list = []

    order = []
    if sample=="QElike":
        order = order_signal
    else:
        order = order_sideband

    for i in range(n_ybins):
        stack = THStack(stack_name+"_"+str(i),"")
        data = TH1D()
        for cat in order:
            h2d = hist_dict[cat]["reconstructed"].Clone()
            tmp_proj_name = "proj_"+cat+"_"+str(i)
            proj = h2d.ProjectionY(tmp_proj_name, i+1, i+1)
            proj = MakeHistPretty(proj, cat)

            if len(multipliers)>0:
                proj.Scale(multipliers[i])
            if cat!="data":
                stack.Add(proj)
                # print("adding stack: ",tmp_proj_name)
            else: 
                data=proj
                # print("made data: ",tmp_proj_name)
        stack_list.append(stack)
        data_list.append(data)

    return data_list, stack_list

def GetBinRangeStringList(h2d_template, varname):
    n_ybins = h2d_template.GetNbinsX()
    out_string_list = []
    for bin in range(1,n_ybins+1):
        bin_low = h2d_template.GetXaxis().GetBinLowEdge(bin)
        bin_hi = h2d_template.GetXaxis().GetBinUpEdge(bin)
        tmp_string = "{min} < {var} < {max}".format(min = bin_low, var = varname, max = bin_hi)
        out_string_list.append(tmp_string)
    return out_string_list

def GetMaxList(data_list,mc_list):
    # Returns the max between data or mc for each hist in a y bin panel
    max_list = []
    for i in range(len(data_list)):
        datamax = data_list[i].GetMaximum()        
        mcmax = mc_list[i].GetMaximum()

        max_list.append(max(datamax, mcmax))
    return max_list

def GetPanelMultipliers(data_list,mc_list,total_max=False):
    panel_maxes_list = GetMaxList(data_list, mc_list) 
    print(panel_maxes_list)
    panel_max = max(panel_maxes_list) # max for the given panel, used if total_max not defined
    print(panel_max) 
    multipliers = []
    for histmax in panel_maxes_list:
        scale = 1.
        if histmax != 0.:
            if total_max:
                print("scaling total_max")
                scale = total_max/histmax # if you have a max for the overall 3d hist, use that instead
            else:
                scale = panel_max/histmax 
            
            if scale > 10.:
                tmp_scale = math.floor(scale)
                scale = tmp_scale
            elif scale > 1.:
                tmp_scale = math.floor(scale*10.)
                scale = tmp_scale/10.
            else:
                tmp_scale = math.ceil(scale*10.)
                scale = tmp_scale/10.
        multipliers.append(scale)
    return multipliers

def ScaleStack(stack_list, multipliers=None):
    out_stack_list = []
    for i in range(len(stack_list)):
        if multipliers[i]!=1.:
            tmp_stack_name = stack_list[i].GetName()
            tmp_new_stack = THStack(tmp_stack_name,"")
            tmp_hist_list = stack_list[i].GetHists()
            for hist in tmp_hist_list:
                hist.Scale(multipliers[i])
                tmp_new_stack.Add(hist)
            out_stack_list.append(tmp_new_stack)
        else: 
            out_stack_list.append(stack_list[i])

    return out_stack_list




def PlotDataMCOnGrid(grid_canvas, title, data_list, stack_list, multipliers = None, plotmax = None, bin_range_string_list = None):
    n_ybins = len(data_list)
    for i in range(n_ybins):
        pad = grid_canvas.cd(i+1)

        if multipliers and multipliers[i]!=1.:
            # print("doing multipliers")
            data_list[i].Scale(multipliers[i])

        if plotmax:
            data_list[i].SetMaximum(plotmax)
        data_list[i].SetMinimum(0.)

        data_list[i].SetTitle(title)

        data_list[i].GetXaxis().SetNdivisions(505)
        data_list[i].GetYaxis().SetNdivisions(505)
        data_list[i].Draw("PE")
        stack_list[i].Draw("HIST same")
        data_list[i].Draw("PE same")
        data_list[i].Draw("AXIS same")
        if bin_range_string_list:
            ybinrange_la = ROOT.TLatex()
            ybinrange_la.SetTextAlign(33) # middle? right
            ybinrange_la.SetNDC()
            ybinrange_la.SetTextFont(42)
            ybinrange_la.SetTextSize(0.03)
            ybinrange_la.DrawLatex((1.-(pad.GetRightMargin())-0.01),(1.-(pad.GetTopMargin())-0.03),bin_range_string_list[i])
        if multipliers and multipliers[i]!=1.:
            multip_la = ROOT.TLatex()
            multip_la.SetTextAlign(32) # top right
            multip_la.SetNDC()
            multip_la.SetTextFont(42)
            multip_la.SetTextSize(0.035)
            multip_la.DrawLatex((1.-(pad.GetRightMargin())-0.01),(1.-(pad.GetTopMargin())-0.16),"#times {scale:.1f}".format(scale = multipliers[i]))



    grid_canvas.SetYTitle("Counts/unit")
    grid_canvas.SetXTitle(x_axis_label)
    grid_canvas.SetTitleSize(20.0)
    grid_canvas.ResetPads()
    grid_canvas.Draw()

def GetHistDict(rfile):
    """Make a dictionary of relevant hists
    rfile is input rootfile
    output is hist_dict dictionary of hists"""
    hist_dict ={}
    
    keys = rfile.GetListOfKeys()

    for key in keys:
        name = key.GetName()
        if "___" not in name:
            continue
        parse = name.split("___")
        if len(parse) < 5: 
            continue
        #print (parse)
        # names look like : hist___Sample___category__variable___types_0;
        hist = parse[0]
        sample = parse[1]
        cat = parse[2]
        variable = parse[3]
        type = parse[4]
        # Only take in hyperd hists
        if hist != "h2D": 
            continue
        if variable not in vars_todo:
            continue
        if sample not in samples_todo:
            continue
        hist = rfile.Get(name).Clone()
        # if hist.GetEntries() <= 0:
        #     continue
        if sample not in hist_dict.keys():
            hist_dict[sample] = {}
        if variable not in hist_dict[sample].keys():
            hist_dict[sample][variable] = {}
        if cat not in hist_dict[sample][variable].keys():
            hist_dict[sample][variable][cat] = {}
        if type not in hist_dict[sample][variable][cat].keys():
            hist_dict[sample][variable][cat][type] = hist

    
    return hist_dict

def MakeHistPretty(hist,category):
    # hist.Scale(1., "width")

    if category=="data":
        hist.SetMarkerStyle(20)
        # hist.SetMarkerSize(0.55)
        hist.SetLineColor(ROOT.kBlack)
        hist.SetLineWidth(2)
    else:
        hist.SetFillColor(catscolors[category])
        hist.SetLineColor(catscolors[category])
        hist.SetFillStyle(1001)
    return hist


def main():
    ROOT.TH1.AddDirectory(ROOT.kFALSE)

    if len(sys.argv) == 1:
        print ("python panel_plots2d.py <rootfile> <option>")
    flag = "types_"
    filename = sys.argv[1]
    if len(sys.argv)> 2:
        flag = "tuned_type_"

    print("Getting started...")

    f = ROOT.TFile.Open(filename,"READONLY")
    dirname = filename.replace(".root","_PanelPlots2D")
    if not os.path.exists(dirname):
        os.mkdir(dirname)

    hist_pot = f.Get("POT_summary").Clone()
    dataPOT = hist_pot.GetBinContent(1)
    mcPOTprescaled = hist_pot.GetBinContent(3)
    POTScale = dataPOT / mcPOTprescaled

    # print("NLinBins: ",myHyperDim.GetNLinBins())


    ROOT.gStyle.SetOptStat(0)
    template = "%s___%s___%s___%s"

    # structred like hist_dict[sample][variable][cat][type] = hist
    hist_dict = GetHistDict(f)

    for a_sample in hist_dict.keys():
        print(">>>> looking at sample "+a_sample)
        order = []
        if a_sample=="QElike":
            order = order_signal
        else:
            order = order_sideband

        for b_var in hist_dict[a_sample].keys():
            if not os.path.exists(dirname+"/"+b_var):
                os.mkdir(dirname+"/"+b_var)
            print(">>>>>>>> looking at var "+b_var)
            total_max = None
            plot_dict = {}
            for c_cat in hist_dict[a_sample][b_var].keys():

                # hHD = hist_dict[a_sample][b_var][c_cat]["reconstructed"]
                h2d = hist_dict[a_sample][b_var][c_cat]["reconstructed"]
                if c_cat!="data":
                    print("POTScaling...")
                    # hHD.Scale(POTScale)
                    h2d.Scale(POTScale,"width")
                else:
                    h2d.Scale(1.,"width")

                    # total_max = 5*hHD.GetMaximum() 
                    total_max = 5*h2d.GetMaximum() # TODO: figure out what to do here 
                # tmp_h2D_list = myHyperDim.Get2DHistos(hHD,IncludeSysBool)
                # n_zbins = len(tmp_h2D_list)
                # for z_bin in range(n_zbins):
                #     # if z_bin in [0,n_zbins+1]: # skip the first and last z bin, these are under/overflow
                #     #     continue
                #     if z_bin not in h2D_dict.keys():
                #         h2D_dict[z_bin] = {}
                #     if c_cat not in h2D_dict[z_bin].keys():
                #         h2D_dict[z_bin][c_cat]=tmp_h2D_list[z_bin]

            # n_xbins = h2D_dict[1]["data"].GetNbinsX()
            # n_ybins = h2D_dict[1]["data"].GetNbinsY()
            n_xbins = hist_dict[a_sample][b_var]["data"]["reconstructed"].GetNbinsX()
            n_ybins = hist_dict[a_sample][b_var]["data"]["reconstructed"].GetNbinsY()

            print("n x bins: ",n_xbins,",\t n y bins: ",n_ybins)
            
            # h2d_max_list = []
            # for z_bin in h2D_dict.keys():
            #     if z_bin==0 or z_bin==5:
            #         continue
            #     tmptmp_h2d = h2D_dict[z_bin]["data"].Clone()
            #     tmptmp_h2d.Print()
            #     tmp_h2d = tmptmp_h2d.Scale(1./0.05)
            #     tmp_h2d.Print()
            #     max = tmp_h2d.GetMaximum()
            #     h2d_max_list.append(max)
            # total_max = max(h2d_max_list)
            plot_dict = hist_dict[a_sample][b_var]
            # for z_bin in h2D_dict.keys():
            # \t
            canvas_name = "%s_%s"%(a_sample,b_var)
            canvas_title = "%s %s"%(a_sample,b_var)
            gc2 = PanelCanvas(canvas_name, n_xbins, n_ybins)
            legend = CCQELegend(0.7, 0.1, .9, 0.25)

            # zbins = global_bins_dict[b_var][2]
            # zbin_title = ""
            # if z_bin==0:
            #     zbin_title = "underflow"
            # elif z_bin==len(zbins):
            #     zbin_title = "overflow"
            # else: 
            #     zbin_lo = zbins[z_bin-1]
            #     zbin_hi = zbins[z_bin]
            #     zvarname = "p_{||} (GeV/c)"
            #     zbin_title = "{min} < {var} < {max}".format(min = zbin_lo, var = zvarname, max = zbin_hi)
            
            stack_name = "mc_stack"

            # binvol_list = GetBinVolumeList(myHyperDim,n_ybins,z_bin)
            # data_list, tmp_stack_list = MakeDataMCStackLists(h2D_dict[z_bin],stack_name,a_sample)
            data_list, tmp_stack_list = MakeDataMCStackLists(plot_dict,stack_name,a_sample)
            
            # bin_range_list = GetBinRangeStringList(h2D_dict[z_bin]["data"],"p_{T} (GeV/c)")
            bin_range_list = GetBinRangeStringList(plot_dict["data"]["reconstructed"],y_axis_label)
            
            multipliers = GetPanelMultipliers(data_list, tmp_stack_list, total_max)
            # panel_max = max(GetMaxList(data_list, tmp_stack_list))
            plot_max = total_max/frac_max
            stack_list = ScaleStack(tmp_stack_list,multipliers)
            
            # PlotDataMCOnGrid(gc2,zbin_title,data_list,stack_list,multipliers,plot_max,bin_range_list)
            PlotDataMCOnGrid(gc2,panel_title,data_list,stack_list,multipliers,plot_max,bin_range_list)
            for cat in order:
                style = ""
                hist = MakeHistPretty(plot_dict[cat]["reconstructed"], cat)
                if cat=="data":
                    style = "pe"
                else: 
                    style = "f"
                legend.AddEntry(hist, catsnames[cat], style)
            legend.Draw("same")
            ofilename = str(dirname+"/"+str(b_var)+"/"+canvas_name+"_FinalStates.pdf")
            gc2.Print(ofilename)

    print(dirname)
    print("Done")


if __name__ == "__main__":
    main()
