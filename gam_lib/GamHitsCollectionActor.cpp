/* --------------------------------------------------
   Copyright (C): OpenGATE Collaboration
   This software is distributed under the terms
   of the GNU Lesser General  Public Licence (LGPL)
   See LICENSE.md for further details
   -------------------------------------------------- */


#include <vector>
#include <iostream>
#include "G4VProcess.hh"
#include "G4GenericAnalysisManager.hh"
#include "G4RunManager.hh"
#include "GamHitsCollectionActor.h"
#include "GamDictHelpers.h"

G4Mutex GamHitsActorMutex = G4MUTEX_INITIALIZER; // FIXME

GamHitsCollectionActor::GamHitsCollectionActor(py::dict &user_info)
    : GamVActor(user_info) {
    fActions.insert("StartSimulationAction");
    fActions.insert("EndSimulationAction");
    //fActions.insert("BeginOfRunAction");
    //fActions.insert("EndOfRunAction");
    fActions.insert("PreUserTrackingAction");
    fActions.insert("EndOfEventAction");
    fActions.insert("SteppingAction");
    for (const auto &a:fActions) { // FIXME
        DDD(a);
    }
    fOutputFilename = DictStr(user_info, "output");
    GamBranches::BuildAllBranches(); //FIXME
    // Create main instance of the analysis manager
    fAnalysisManager = G4RootAnalysisManager::Instance();
}

GamHitsCollectionActor::~GamHitsCollectionActor() {
}

// Called when the simulation start
void GamHitsCollectionActor::StartSimulationAction() {
    // create the file
    // FIXME --> to put in a function (PhaseSpace)
    fAnalysisManager->OpenFile(fOutputFilename);
    //fAnalysisManager->SetNtupleMerging(true);
    fAnalysisManager->CreateNtuple("Hits", "Hits collection");
    fStepSelectedBranches.clear();
    GamBranches::GetSelectedBranches(fStepFillNames, fAnalysisManager, fStepSelectedBranches);
    fAnalysisManager->FinishNtuple(); // needed to indicate the tuple is finished

    fTree.SetName("Hits");
    fTree.SetTitle("Hits collection");

    BranchRootStruct b;
    b.name = "KineticEnergy";
    b.type = 'D';
    b.fill = [=](TTree &tree,
                 BranchRootStruct &b,
                 G4Step *step,
                 G4TouchableHistory *h) {
        b.dvalue = step->GetPostStepPoint()->GetKineticEnergy();
        DDD(b.dvalue);
    };

    fTFile = TFile::Open("a.root","RECREATE");
    fTree.Branch(b.name.c_str(), &(b.dvalue), "Energy/F");
    fRootBranches.push_back(b);
}

// Called when the simulation end
void GamHitsCollectionActor::EndSimulationAction() {
    DD("EndSimulationAction");
    //fAnalysisManager->Write();
    //fAnalysisManager->CloseFile();
    fTFile->Write();
    fTFile->Close();
}

// Called every time a Run starts
void GamHitsCollectionActor::BeginOfRunAction(const G4Run * /*run*/) {
    //DDD("not yet");
}

// Called every time a Run ends
void GamHitsCollectionActor::EndOfRunAction(const G4Run * /*run*/) {
    DDD("end run");

}

void GamHitsCollectionActor::BeginOfEventAction(const G4Event */*event*/) {
    //fBeginOfEventTime = event->Get
}

void GamHitsCollectionActor::EndOfEventAction(const G4Event *) {
    //fBeginOfEventTime = event->Get
    //auto n = fAnalysisManager->GetNofNtuples();
    //DDD(n);
    //auto t = fAnalysisManager->GetNtuple(0);
    //DDD(t->entries());
    //t->print_columns(std::cout);
    //auto bs = t->branches();
    //DD(bs.size());
    /*for (auto b:bs) {
        DDD(b->name());
        DDD(b->entries());
        DDD(b->basket_size());
        DDD(b->tot_bytes());
        auto ll = b->leaves();
        DDD(ll.size());
        for (auto l:ll) {
            DDD(l->name());
            DDD(l->length());
        }}*/
    DDD(" end event");
    //auto &branch = fRootBranches[0];
    std::vector<double> *vpx = 0;
    auto branch = fTree.GetBranch("KineticEnergy");
    fTree.SetBranchAddress("KineticEnergy",&vpx,&branch);
    branch->GetEntry();
    DDD(vpx->size());
}

// Called every time a Track starts
void GamHitsCollectionActor::PreUserTrackingAction(const G4Track *track) {

}

// Called every time a batch of step must be processed
void GamHitsCollectionActor::SteppingAction(G4Step *step, G4TouchableHistory *touchable) {
    G4AutoLock mutex(&GamHitsActorMutex);
    for (auto element:fStepSelectedBranches) {
        element.fill(fAnalysisManager, element, step, touchable);
    }
    // this is needed to stop current tuple fill (for vector for example)
    fAnalysisManager->AddNtupleRow();
    auto &b = fRootBranches[0];
    b.fill(fTree, b, step, touchable);
    fTree.Fill();
}
