#include "TROOT.h"
#include "TKey.h"
#include "TFile.h"
#include "TSystem.h"
#include "TTree.h"
void CopyDir(TDirectory *source) {
   //copy all objects and subdirs of directory source as a subdir of the current directory
   source->ls();
   TDirectory *savdir = gDirectory;
   TDirectory *adir = savdir->mkdir(source->GetName());
   adir->cd();
   //loop on all entries of this directory
   TKey *key;
   TIter nextkey(source->GetListOfKeys());
   while ((key = (TKey*)nextkey())) {
      const char *classname = key->GetClassName();
      TClass *cl = gROOT->GetClass(classname);
      if (!cl) continue;
      if (cl->InheritsFrom(TDirectory::Class())) {
         source->cd(key->GetName());
         TDirectory *subdir = gDirectory;
         adir->cd();
         CopyDir(subdir);
         adir->cd();
      } else if (cl->InheritsFrom(TTree::Class())) {
         TTree *T = (TTree*)source->Get(key->GetName());
         adir->cd();
         TTree *newT = T->CloneTree(-1,"fast");
         newT->Write();
      } else {
         source->cd();
         TObject *obj = key->ReadObj();
         adir->cd();
         obj->Write();
         delete obj;
     }
  }
  adir->SaveSelf(kTRUE);
  savdir->cd();
}
void CopyFile(const char *fname) {
   //Copy all objects and subdirs of file fname as a subdir of the current directory
   TDirectory *target = gDirectory;
   TFile *f = TFile::Open(fname);
   if (!f || f->IsZombie()) {
      printf("Cannot copy file: %s\n",fname);
      target->cd();
      return;
   }
   target->cd();
   CopyDir(f);
   delete f;
   target->cd();
}
void copyFiles() {
   //prepare files to be copied
   if(gSystem->AccessPathName("tot100.root")) {
      gSystem->CopyFile("hsimple.root", "tot100.root");
      gSystem->CopyFile("hsimple.root", "hs1.root");
      gSystem->CopyFile("hsimple.root", "hs2.root");
   }
   //main function copying 4 files as subdirectories of a new file
   TFile *f = new TFile("result.root","recreate");
   CopyFile("tot100.root");
   CopyFile("hsimple.root");
   CopyFile("hs1.root");
   CopyFile("hs2.root");
   f->ls();
   delete f;
}
