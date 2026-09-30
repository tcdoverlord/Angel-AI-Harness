Angel 4.1.1 Release Checklist
Workspace State & Knowledge Management Fixes

Release Owner: Product Owner
 Engineering Lead: Engineering Lead
 Status: ☐ Not Started / ☐ In Progress / ☐ Complete

P0 Release Blockers
Project Context Isolation
Backend (Owner: Backend Engineer)
 Separate selectedProjectId from conversation.projectId
 Add conversation context resolver
 Prevent project selection from modifying global chat state
 Ensure New Chat defaults to projectId = null
 Ensure project conversations retain stored project context
 Ensure RagRun records conversation project scope only
 Add unit tests for project context resolution
Frontend (Owner: Frontend Engineer)
 Clicking a project opens project workspace
 Clicking a conversation restores conversation context
 Clicking New Chat always creates a global conversation
 Active project workspace clearly indicated
QA (Owner: QA)
 Selecting a project does not affect existing chats
 Selecting a project does not affect New Chat behavior
 Existing project conversations retain project scope
 RagRuns record correct project scope
 No project context leakage detected
Sign-off
 Backend complete
 Frontend complete
 QA passed
 Engineering Lead approval
Knowledge Pack Selection Fix
Frontend (Owner: Frontend Engineer)
 Audit current pack selection implementation
 Remove stale pack selection behavior
 Resolve pack using clicked pack ID
 Clear previous state before loading new pack
 Remove fallback-to-previous-pack behavior
 Remove hardcoded/default pack references
 Fix document selection state updates
 Fix document content refresh logic
Validation (Owner: Frontend Engineer)
 Verify clicked pack ID matches rendered pack
 Verify selected document matches rendered document
 Verify route state matches selection state
QA (Owner: QA)
 Pack A loads Pack A content
 Pack B loads Pack B content
 Pack C loads Pack C content
 No stale content remains
 No "261" fallback remains
 Document switching works reliably
Sign-off
 Frontend complete
 QA passed
 Engineering Lead approval
Stale Selection Cleanup
Frontend (Owner: Frontend Engineer)
 Detect deleted selected pack
 Clear invalid selectedPackId
 Return user to pack list
 Detect deleted selected document
 Clear invalid selectedDocumentId
 Return user to document list
 Add safe navigation fallback logic
QA (Owner: QA)
 Deleted pack clears selection
 Deleted document clears selection
 No stale content renders
 No runtime exceptions occur
 No "stuck on 261" behavior
Sign-off
 Frontend complete
 QA passed
 Engineering Lead approval
P1 Required Features
Remove Document
UX (Owner: UX)
 Design Remove Document experience
 Design confirmation dialog
 Design destructive-action styling
Frontend (Owner: Frontend Engineer)
 Add document action menu
 Add Remove Document action
 Add confirmation dialog flow
 Refresh pack view after deletion
Backend (Owner: Backend Engineer)
 Delete document record
 Delete sections
 Delete chunks
 Delete embeddings
 Delete retrieval references
 Trigger reindex/update
QA (Owner: QA)
 Document removed from UI
 Document removed from database
 Chunks removed
 Retrieval entries removed
 Index updated correctly
Sign-off
 UX complete
 Frontend complete
 Backend complete
 QA passed
 Product approval
Remove Knowledge Pack
UX (Owner: UX)
 Design Remove Pack experience
 Design confirmation dialog
 Design deletion warning text
Frontend (Owner: Frontend Engineer)
 Add pack action menu
 Add Remove Pack option
 Add confirmation flow
 Refresh Knowledge Center after removal
Backend (Owner: Backend Engineer)
 Delete pack
 Delete documents
 Delete sections
 Delete chunks
 Delete embeddings
 Delete retrieval references
 Delete index entries
Backend Validation (Owner: Backend Engineer)
 Preserve conversations
 Preserve projects
 Preserve RagRuns
 Preserve evidence records
QA (Owner: QA)
 Pack removed successfully
 Documents removed
 Index updated
 Knowledge Center refreshed
 Historical conversations preserved
Sign-off
 UX complete
 Frontend complete
 Backend complete
 QA passed
 Product approval
Workspace Cohesion Validation
QA (Owner: QA)
Project Context
 Open project
 Start conversation
 Verify project context behavior
 Verify New Chat isolation
 Verify RagRun context
Knowledge Navigation
 Open pack
 Open document
 Navigate back
 Switch packs
 Switch documents
Deletion Workflows
 Remove document
 Remove pack
 Verify refresh behavior
 Verify index updates
Recovery Testing
 Delete selected pack
 Delete selected document
 Validate state recovery
Product Review (Owner: Product Owner)
 Projects feel connected to conversations
 Knowledge navigation feels reliable
 Knowledge ownership is clear
 Knowledge Center behavior is predictable
 Angel feels like one application
Sign-off
 QA complete
 UX review complete
 Product approval
Release Gate
P0 Complete
 Project Context Isolation complete
 Knowledge Pack Selection Fix complete
 Stale Selection Cleanup complete
 All P0 QA tests passed

Engineering Lead Approval: ☐

P1 Complete
 Remove Document complete
 Remove Pack complete
 Workspace Cohesion Validation complete
 Manual QA complete

Product Owner Approval: ☐

Deferred Until After Release Gate (P2)
Event Bus Runtime
 Typed emit()
 Typed subscribe()
 Unsubscribe support
 Lifecycle-safe event dispatch
Payload Validation
 Runtime payload validation
 Event payload schemas
 Validation tests
Contextual Pill Enhancements
 Telemetry events
 Usage instrumentation
 Additional pill actions
UX Refinements
 Additional layout improvements
 Knowledge hierarchy enhancements
 Contextual continuity refinements
Final Release Approval
Engineering Lead
 State correctness verified
 No critical defects remain
 Release candidate approved
Product Owner
 Workspace cohesion goals met
 User experience goals met
 Angel 4.1.1 approved
Definition of Done
 No project context leakage
 No stale pack selection
 No stale document selection
 Document deletion fully functional
 Pack deletion fully functional
 Knowledge index remains consistent
 Workspace cohesion validation passed
 Release approvals completed

Release Theme: Fix state correctness before adding infrastructure.