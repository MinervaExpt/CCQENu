import ROOT

class POTCounter:
    def __init__(self):
        pass

    def init_chain(self, playlist):
        fChain = ROOT.TChain("Meta")
        with open(playlist, "r") as input_pl:
            for filename in input_pl:
                filename = filename.strip()
                if filename and filename[0] == '/' or filename.startswith('root'):
                    fChain.Add(filename)
        return fChain

    def get_pot_from_playlist(self, playlist, get_total, batch_number, use_fast):
        fChain = self.init_chain(playlist)
        if not fChain or fChain.GetEntries() == 0:
            print("PlotUtils::POTCounter -- Can NOT find TChain from input playlist! -- Returning -1")
            return -1
        else:
            print("PlotUtils::POTCounter -- Initialized fChain using the Input playlist!")
        print (fChain.GetEntries())

        if use_fast:
            return self.get_pot_from_tchain_fast(fChain, get_total, batch_number)
        else:
            return self.get_pot_from_tchain(fChain, get_total, batch_number)

    def get_pot_from_tchain(self, ch, get_total, batch_number):
        sumPOTUsed = 0
        if batch_number == -1:
            print("PlotUtils::POTCounter -- Counting POT")
            leafName = "POT_Total" if get_total else "POT_Used"
        elif 1 <= batch_number <= 6:
            print(f"PlotUtils::POTCounter -- Counting POT from batch {batch_number}")
            if get_total:
                print("PlotUtils::POTCounter -- for getPOTfromTChain, there is no POT_Total for a batch")
                print("PlotUtils::POTCounter -- Please use batch number -1")
                return sumPOTUsed
            leafName = f"POT_Used_batch{batch_number}"
        else:
            print("PlotUtils::POTCounter -- for getPOTfromTChain, batch number is 1 through 6")
            print(f"PlotUtils::POTCounter -- inputted batch number: {batch_number}")
            return sumPOTUsed

        fileElements = ch.GetListOfFiles()
        print("PlotUtils::POTCounter -- It can take some time depending on the size of the TChain")
        for chEl in fileElements:
            f = ROOT.TFile.Open(chEl.GetTitle())
            t = f.Get("Meta")
            if not t:
                print(f"PlotUtils::POTCounter -- No Meta tree in file {chEl.GetTitle()}")
                continue
            n_entries = t.GetEntries()
            for i in range(n_entries):
                t.GetEntry(i)
                POT_Used = t.GetLeaf(leafName)
                if POT_Used:
                    sumPOTUsed += POT_Used.GetValue()
                    print (sumPOTUsed)
            f.Close()
        return sumPOTUsed

    def get_pot_from_tchain_fast(self, ch, get_total, batch_number):
        sumPOTUsed = 0
        print("PlotUtils::POTCounter -- Called getPOTfromTChain_Fast()")
        print("PlotUtils::POTCounter -- This method works only for non-merged files, if your playlist includes merged ROOT files,use getPOTfromPlaylist(playlist, false)")
        print("PlotUtils::POTCounter -- This can't get batch POT")
        print("PlotUtils::POTCounter -- Counting POT Fast")
        print("PlotUtils::POTCounter -- It can take some time depending on the size of the TChain")

        nentries = ch.GetEntriesFast()
        for jentry in range(nentries):
            ientry = ch.GetEntry(jentry)
            if ientry == 0:
                print(f"\tGetEntry failure {jentry}")
                break

            if batch_number == -1:
                if get_total:
                    sumPOTUsed += ch.POT_Total
                else:
                    sumPOTUsed += ch.POT_Used
            elif 1 <= batch_number <= 6:
                if get_total:
                    print("PlotUtils::POTCounter -- for getPOTfromTChain, there is no POT_Total for a batch")
                    print("PlotUtils::POTCounter -- Please use batch number -1")
                    return sumPOTUsed
                sumPOTUsed += getattr(ch, f"POT_Used_batch{batch_number}")
            else:
                print("PlotUtils::POTCounter -- for getPOTfromTChain, batch number is 1 through 6")
                print(f"PlotUtils::POTCounter -- inputted batch number: {batch_number}")
                return sumPOTUsed

            if jentry % 10000 == 0:
                print(f"\tCurrent Total POT = {sumPOTUsed}")
        return sumPOTUsed
