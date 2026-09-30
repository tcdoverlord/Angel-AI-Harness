EPIC: ANGEL-411
Angel 4.1.1 Workspace Cohesion Release Candidate

Epic Type: Platform Stability & UX Cohesion
 Priority: Critical
 Target Release: Angel 4.1.1
 Epic Owner: Product Owner
 Technical Owner: Engineering Lead
 Status: Ready for Implementation

Epic Summary

Angel 4.1.1 focuses on workspace correctness, knowledge ownership, and state reliability.

This epic addresses user-visible issues discovered during workflow validation, including:

Project context leakage
Incorrect knowledge pack selection
Stale UI selection state
Missing document deletion
Missing pack deletion
Workspace cohesion gaps between Chat, Projects, and Knowledge Center

This is not a feature-expansion release.

This is a platform-stability and workspace-cohesion release.

Epic Goal

Create a reliable Angel workspace where:

Projects
      │
      ▼
Knowledge
      │
      ▼
Conversation
      │
      ▼
RagRun


behaves predictably and consistently.

Business Value
Users gain
Reliable project behavior
Predictable knowledge navigation
Real ownership of knowledge assets
Safe deletion workflows
Trustworthy workspace state
Platform gains
Correct context boundaries
Stable selection management
Consistent knowledge lifecycle handling
Reduced UX confusion
Stronger release discipline
Success Criteria

Angel 4.1.1 is successful when:

No project context leakage exists
No stale knowledge-pack selection exists
No stale document selection exists
Documents can be permanently removed
Packs can be permanently removed
Historical records remain preserved
Workspace cohesion validation passes
Engineering Lead and Product Owner approve release
In Scope
P0 Release Blockers
Story A411-1

Project Context Isolation

Objective

Ensure project selection and conversation ownership are independent.

Requirements
selectedProjectId
        ≠
conversation.projectId

Acceptance Criteria
New Chat always creates global conversations
Project selection does not change existing conversations
Project conversations retain stored project context
RagRuns record correct conversation scope
No context leakage detected
Owner

Backend + Frontend

Story A411-2

Knowledge Pack Selection Fix

Objective

Ensure selected packs and documents always match user choice.

Acceptance Criteria
Pack A → Pack A
Pack B → Pack B
Pack C → Pack C

Selected pack matches clicked pack
Selected document matches clicked document
No fallback behavior exists
No hardcoded pack references exist
"Stuck on 261" defect eliminated
Owner

Frontend

Story A411-3

Stale Selection Cleanup

Objective

Ensure deleted content cannot remain selected.

Acceptance Criteria

When a selected pack is deleted:

selectedPackId = null


When a selected document is deleted:

selectedDocumentId = null

UI returns to safe state
No orphaned views
No invalid rendering
No runtime errors
Owner

Frontend

P1 Required Features
Story A411-4

Remove Document

Objective

Allow permanent removal of stored knowledge documents.

Deletion Chain
Document
  ↓
Sections
  ↓
Chunks
  ↓
Embeddings
  ↓
Retrieval References
  ↓
Index

Acceptance Criteria
Document removed from UI
Document removed from persistence
Chunks removed
Retrieval entries removed
Index updated
Content no longer retrievable
Owner

Backend + Frontend

Story A411-5

Remove Knowledge Pack

Objective

Allow permanent removal of knowledge packs.

Deletion Chain
Pack
  ↓
Documents
  ↓
Sections
  ↓
Chunks
  ↓
Embeddings
  ↓
Retrieval References
  ↓
Index Entries

Preservation Rules

Must preserve:

Conversations
Projects
RagRuns
Evidence

Acceptance Criteria
Pack removed
Documents removed
Retrieval index updated
Historical records preserved
Conversations unaffected
Owner

Backend + Frontend

Story A411-6

Workspace Cohesion Validation

Objective

Validate end-to-end workspace behavior.

Test Areas
Projects
Open Project
  ↓
Start Conversation
  ↓
Verify Context

Knowledge
Open Pack
  ↓
Open Document
  ↓
Switch Pack

Deletion
Delete Document
Delete Pack
Verify Index
Verify UI

Recovery
Delete Selected Pack
  ↓
Safe State

Delete Selected Document
  ↓
Safe State

Acceptance Criteria
All workflows pass
No state corruption
Workspace behaves as one application
Owner

QA + Product

Dependencies
A411-1 Project Context Isolation
         │
         ├────┐
         │    │
         ▼    ▼
A411-2  A411-4
         │
         ▼
A411-3 Stale Selection Cleanup
         │
         ▼
A411-5 Remove Knowledge Pack
         │
         ▼
A411-6 Workspace Cohesion Validation
         │
         ▼
Release Candidate

Out of Scope

The following are explicitly deferred until after the Angel 4.1.1 release gate:

P2
Contextual Continuity enhancements
Event Bus Runtime
Payload Validation
Contextual Pill Telemetry
Additional UX Refinements
New engineering dashboards
New architectural subsystems
Release Gate
P0 Complete
 A411-1 complete
 A411-2 complete
 A411-3 complete
 P0 QA passed

Sign-off: Engineering Lead

P1 Complete
 A411-4 complete
 A411-5 complete
 A411-6 complete
 Manual QA complete

Sign-off: Product Owner

Definition of Done

Angel 4.1.1 may be released only when all of the following are true:

✓ No Project Context Leakage

✓ No Stale Pack Selection

✓ No Stale Document Selection

✓ Real Document Deletion

✓ Real Pack Deletion

✓ Historical Records Preserved

✓ Workspace Cohesion Validation Passed

✓ Engineering Lead Approved

✓ Product Owner Approved

Release Theme

Fix state correctness before adding infrastructure.

Angel 4.1.1 is a workspace reliability release focused on context correctness, knowledge ownership, safe deletion, and end-to-end cohesion across Projects, Knowledge Center, and Chat.