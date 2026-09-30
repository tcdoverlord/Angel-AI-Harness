Angel 4.1.1 Dependency-Based Rollout Plan
Workspace State & Knowledge Management Fixes

This rollout plan is ordered by dependency and risk, not by feature importance.

The goal is to avoid building features on top of unstable state management.

Critical Path
Project Context Isolation
          │
          ▼
Knowledge Pack Selection Fix
          │
          ▼
Stale Selection Cleanup
          │
          ▼
Workspace State Validation
          │
────────── RELEASE STABILITY LINE ──────────
          │
          ▼
Remove Document
          │
          ▼
Remove Pack
          │
          ▼
Knowledge Lifecycle Validation
          │
          ▼
Workspace Cohesion Validation
          │
────────── 4.1.1 RC LINE ──────────
          │
          ▼
Contextual Continuity
          │
          ▼
Event Bus Runtime
          │
          ▼
Payload Validation
          │
          ▼
UX Refinements

Wave 1
State Correctness

Goal: Eliminate context leakage and invalid UI state.

1. Project Context Isolation

Dependencies: None

Deliverables
Separate project selection from conversation context
New Chat always creates global conversations
Existing project conversations preserve project context
RagRuns record correct context
Risk

High

If this is wrong:

Project
    ↓
Conversation
    ↓
RagRun


becomes unreliable.

Exit Criteria
 Project selection does not affect New Chat
 Project conversations preserve scope
 Context leakage eliminated
 QA approved
2. Knowledge Pack Selection Fix

Depends On: None

Can run in parallel with Project Context Isolation.

Deliverables
Selected pack always matches clicked pack
Selected document always matches clicked document
Remove default pack fallback logic
Eliminate "261" behavior
Exit Criteria
 Pack switching works
 Document switching works
 No stale rendering
 QA approved
3. Stale Selection Cleanup

Depends On:

Knowledge Pack Selection Fix

Deliverables
Auto-clear invalid selections
Safe navigation fallback
Recovery after deletion
Exit Criteria
 Deleted pack clears selection
 Deleted document clears selection
 No orphaned state
 QA approved
Stability Gate A

Proceed only when:

✓ Project Context Isolation Complete

✓ Knowledge Selection Complete

✓ Stale Selection Cleanup Complete


At this point:

Projects
Knowledge
Chat


all operate with correct state.

Wave 2
Knowledge Ownership

Goal: Users gain real control over stored knowledge.

4. Remove Document

Depends On:

Knowledge Pack Selection Fix

Deliverables
Remove Document UI
Confirmation dialog
Backend deletion
Index update
Exit Criteria
 Document removed from persistence
 Chunks removed
 Retrieval references removed
 UI refreshed
5. Remove Pack

Depends On:

Remove Document


because pack removal uses the same deletion infrastructure.

Deliverables
Remove Pack workflow
Cascade deletion
Refresh behavior
Exit Criteria
 Pack deleted
 Documents deleted
 Index entries deleted
 Conversations preserved
Stability Gate B

Proceed only when:

✓ Remove Document Complete

✓ Remove Pack Complete

✓ Knowledge Lifecycle Validation Complete


At this point users actually own their knowledge library.

Wave 3
Workspace Cohesion

Goal: Make Angel feel like one application.

6. Workspace Cohesion Validation

Depends On:

Project Context Isolation

Knowledge Ownership

Selection Fixes

Validation Areas
Projects
Project switching
Project conversations
Project context visibility
Knowledge
Pack navigation
Document navigation
Deletion workflows
Chat
Context boundaries
Knowledge references
Retrieval behavior
Exit Criteria
 User can move between Projects and Chat naturally
 User can move between Knowledge and Chat naturally
 No state confusion remains
Release Candidate Gate

Angel 4.1.1 becomes a release candidate when:

✓ Wave 1 Complete

✓ Wave 2 Complete

✓ Workspace Validation Passed

Wave 4
Runtime Integration

These items are intentionally deferred.

The recording indicates they are valuable but not currently blocking.

7. Contextual Continuity

Depends On:

Project Context Isolation
Workspace Cohesion Validation

Deliverables
Project
    ↓
Retrieval
    ↓
Answer


becomes visible to the user.

8. Event Bus Runtime

Depends On:

Contextual Continuity

Deliverables
emit()
on()
unsubscribe()
safe dispatch

Reason Deferred

The event bus improves plumbing.

The current problems are state-management problems.

9. Payload Validation

Depends On:

Event Bus Runtime

Deliverables
Runtime schema validation
Event safety
Error reporting
10. UX Refinements

Depends On:

All Prior Work


Includes:

Sidebar cleanup
Space utilization improvements
Contextual pill tuning
Information hierarchy improvements
Team Parallelization Plan
Backend Track
Project Context Isolation
         │
         ▼
Remove Document
         │
         ▼
Remove Pack

Frontend Track
Pack Selection Fix
         │
         ▼
Stale Selection Cleanup
         │
         ▼
Workspace Cohesion Updates

QA Track
Context Tests
         │
         ▼
Selection Tests
         │
         ▼
Deletion Tests
         │
         ▼
Workspace Validation

Final Rollout Decision Tree
Project Context Fixed?
        │
        ├─ No → Stop
        │
        ▼
Pack Selection Fixed?
        │
        ├─ No → Stop
        │
        ▼
Stale Selection Fixed?
        │
        ├─ No → Stop
        │
        ▼
Remove Document Working?
        │
        ├─ No → Stop
        │
        ▼
Remove Pack Working?
        │
        ├─ No → Stop
        │
        ▼
Workspace Validation Passed?
        │
        ├─ No → Stop
        │
        ▼
4.1.1 Release Candidate
        │
        ▼
Runtime Integration Work
        │
        ▼
Event Bus
        │
        ▼
Payload Validation

Rollout Principle

Build state correctness first.

Build knowledge ownership second.

Build workspace cohesion third.

Build infrastructure fourth.

That sequence minimizes risk and ensures Angel 4.1.1 solves the user-visible problems exposed in the recording before investing in additional runtime architecture.