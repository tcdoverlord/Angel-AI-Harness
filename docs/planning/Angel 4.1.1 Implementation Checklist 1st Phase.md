Angel 4.1.1 Implementation Checklist
Workspace State & Knowledge Management Fixes

Release: Angel 4.1.1
 Milestone: Workspace Cohesion Pass

Phase 1 — Project Context Isolation
Backend
Conversation Context Rules
 Separate selectedProjectId from conversation.projectId
 Ensure project selection does not modify global chat state
 Ensure new conversations default to projectId = null
 Ensure project conversations retain stored project context
 Ensure RagRun records conversation project context
 Add unit tests for project context resolution
Acceptance
 Selecting a project does not affect existing chats
 Selecting a project does not affect future global chats
 Existing project conversations continue using project scope
 RagRun records correct project scope
UI
Sidebar
 Clicking a project activates project workspace view
 Clicking a conversation restores that conversation's context
 Clicking + New Chat creates a global conversation
 Project selection visually indicates active workspace
Acceptance
 User can switch projects without affecting New Chat
 User can switch between projects and conversations safely
 Context never "leaks" between chats
Phase 2 — Knowledge Pack Selection Fix
State Management
Pack Selection
 Replace stale selection logic
 Resolve pack from clicked pack ID
 Load pack data using selected pack ID
 Clear previous pack data before loading new pack
 Prevent fallback to previously viewed pack
Document Selection
 Resolve document from selected document ID
 Refresh document content when selection changes
 Prevent stale document rendering
Debugging
Selection Tracking
 Log selected pack ID during development
 Log selected document ID during development
 Verify clicked ID equals rendered ID
 Verify route state matches UI state
Acceptance
Pack Switching
 Pack A opens Pack A contents
 Pack B opens Pack B contents
 Pack C opens Pack C contents
 No pack displays stale content
 No hardcoded default pack remains
Document Switching
 Document selection updates immediately
 Document content matches selected item
 No stale document display
Phase 3 — Remove Document
UI
Document Actions
 Add document action menu
 Add Remove Document option
 Add destructive confirmation dialog
Confirmation Dialog
 Show document name
 Explain removal consequences
 Provide Cancel action
 Provide Remove action
 Require explicit confirmation
Backend
Deletion
 Delete document record
 Delete document sections
 Delete document chunks
 Delete embeddings
 Delete retrieval references
 Update search index
Refresh
 Reload pack contents
 Update document counts
 Update chunk counts
 Refresh retrieval metadata
Acceptance
 Document removed from UI
 Document removed from persistence
 Chunks removed
 Index updated
 Counts refreshed
 Knowledge Center remains stable
Phase 4 — Remove Knowledge Pack
UI
Pack Actions
 Add pack action menu
 Add Remove Pack
 Add destructive confirmation dialog
Confirmation Dialog
 Show pack name
 Show document count
 Explain removal scope
 Clarify conversations remain intact
 Require explicit confirmation
Backend
Cascade Deletion
 Delete pack
 Delete associated documents
 Delete sections
 Delete chunks
 Delete embeddings
 Delete retrieval references
 Delete index entries
Preservation
 Preserve conversations
 Preserve projects
 Preserve RagRuns
 Preserve evidence records
Refresh
 Refresh pack list
 Refresh counts
 Refresh recent activity
 Refresh retrieval metadata
Acceptance
 Pack disappears immediately
 Documents removed
 Chunks removed
 Search index updated
 Knowledge Center refreshes correctly
Phase 5 — Stale Selection Cleanup
Pack Cleanup
Logic
 Detect deleted selected pack
 Clear selectedPackId
 Return user to pack list
Validation
 No orphaned pack view
 No stale pack content
Document Cleanup
Logic
 Detect deleted selected document
 Clear selectedDocumentId
 Return user to document list
Validation
 No orphaned document view
 No stale document content
Acceptance
 Deleted pack clears selection
 Deleted document clears selection
 No "stuck on 261" behavior
 UI safely recovers from deletions
 No runtime errors
Phase 6 — Workspace Cohesion Validation
Project → Chat
 Open project
 Start conversation
 Verify project context behavior
 Verify global chat behavior
 Verify RagRun context
Knowledge Navigation
 Open pack
 Open document
 Navigate back
 Open different pack
 Open different document
Removal Workflows
 Remove document
 Remove pack
 Verify index update
 Verify refreshed UI
State Recovery
 Delete selected pack
 Delete selected document
 Verify UI returns to safe state
Release Gate
Must Complete Before Event Bus Work
Project Context
 Project isolation implemented
 Context leakage eliminated
 Acceptance tests passing
Knowledge Selection
 Pack selection fixed
 Document selection fixed
 Acceptance tests passing
Knowledge Removal
 Remove Document implemented
 Remove Pack implemented
 Persistence deletion verified
State Recovery
 Stale selections cleared
 Safe recovery verified
Workspace Cohesion
 Projects feel connected to conversations
 Knowledge navigation works correctly
 No state corruption discovered
 Manual QA complete
Next Milestone
Workspace State Fixes
        ↓
Workspace Acceptance Tests
        ↓
Contextual Continuity
        ↓
Event Bus Runtime
        ↓
Payload Validation
        ↓
UX Refinement

Success Definition

Angel 4.1.1 succeeds when Projects, Knowledge Center, and Chat behave as a single coherent workspace, with correct context boundaries, reliable knowledge navigation, and complete ownership of stored knowledge.