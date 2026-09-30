# Angel Platform Roadmap & Governance Pack

## Program Overview

This document combines:

- ANGEL-411 Workspace Cohesion Release Candidate
- ANGEL-412 Unified Workspace Epic
- Sprint Breakdown
- Dependencies
- RACI Ownership Model
- Release Gates
- Risk Register
- Mitigation Plans
- Contingency Plans

---

# ANGEL-411
## Angel 4.1.1 Workspace Cohesion Release Candidate

### Objective

Stabilize state management, knowledge ownership, and workspace cohesion.

### P0 Release Blockers

#### 1. Project Context Isolation

Success Criteria:

- Project selection != conversation ownership
- New Chat always starts global
- Existing conversations retain project context
- RagRuns use conversation context
- No context leakage

#### 2. Knowledge Pack Selection Fix

Success Criteria:

- Pack A -> Pack A
- Pack B -> Pack B
- Pack C -> Pack C
- No stale selection
- No fallback behavior
- Eliminate 'stuck on 261'

#### 3. Stale Selection Recovery

Success Criteria:

- Deleted pack clears selection
- Deleted document clears selection
- Safe fallback views
- No orphaned state

### P1 Required Features

#### 4. Remove Document

Deletion chain:

Document -> Sections -> Chunks -> Embeddings -> Retrieval References -> Index

#### 5. Remove Knowledge Pack

Deletion chain:

Pack -> Documents -> Sections -> Chunks -> Embeddings -> Retrieval References -> Index Entries

Preserve:

- Conversations
- Projects
- RagRuns
- Evidence

#### 6. Workspace Cohesion Validation

Validate:

- Projects
- Knowledge
- Chat
- Deletion
- Recovery

---

# ANGEL-411 Release Gate

## P0 Complete

- [ ] Project Context Isolation
- [ ] Knowledge Pack Selection Fix
- [ ] Stale Selection Cleanup

## P1 Complete

- [ ] Remove Document
- [ ] Remove Knowledge Pack
- [ ] Workspace Cohesion Validation

## Approval Sequence

Backend
-> Frontend
-> UX
-> QA
-> Engineering Lead
-> Product Owner
-> Release

---

# RACI Summary

| Area | Responsible | Accountable |
|--------|--------|--------|
| Project Context Isolation | Backend + Frontend | Engineering Lead |
| Pack Selection Fix | Frontend | Engineering Lead |
| Stale Selection Cleanup | Frontend | Engineering Lead |
| Remove Document | Backend + Frontend | Product Owner |
| Remove Pack | Backend + Frontend | Product Owner |
| Workspace Cohesion Validation | QA | Product Owner |

---

# ANGEL-412
## Unified Workspace

### Vision

One Assistant.

One Workspace.

One Context.

```text
ANGEL
  |
CHAT / WORK
  |
PROJECT
  |
KNOWLEDGE + FILES + MEMORY
  |
RETRIEVAL SCOPE
  |
RAG RUN
  |
EVIDENCE
```

---

# Sprint 1
## Workspace Foundation

### Stories

- ANGEL-412-1 Sidebar Information Architecture
- ANGEL-412-2 Project Grouping
- ANGEL-412-3 Conversation Search
- ANGEL-412-10 Project Workspace Overview

### Exit Criteria

- Sidebar hierarchy complete
- Projects feel like workspaces
- Conversation discovery improved

---

# Sprint 2
## Conversation Experience

### Stories

- ANGEL-412-20 Collapsible Evidence
- ANGEL-412-21 Simplified Message Layout
- ANGEL-412-22 Response Action Refinement
- ANGEL-412-30 Evidence Drawer

### Exit Criteria

- Cleaner conversations
- Progressive disclosure
- Evidence preserved

---

# Sprint 3
## Context-Aware Workspace

### Stories

- ANGEL-412-11 Project Context Visibility
- ANGEL-412-31 Retrieval Summary
- ANGEL-412-32 Evaluation Visibility
- ANGEL-412-70 Context Panel
- ANGEL-412-71 Memory Integration

### Exit Criteria

- Context transparency
- Retrieval visibility
- Project awareness

---

# Sprint 4
## Chat + Work Experience

### Stories

- ANGEL-412-40 Chat Mode
- ANGEL-412-41 Work Mode
- ANGEL-412-42 Work Timeline
- ANGEL-412-50 Model Status Panel
- ANGEL-412-53 Model Selection UX

### Exit Criteria

- Distinct Chat and Work modes
- Backend visibility
- Workspace assistant experience

---

# Dependency Chain

```text
4.1.1 Release
      ↓
Sidebar Information Architecture
      ↓
Project Workspace Overview
      ↓
Evidence Drawer
      ↓
Project Context Visibility
      ↓
Context Panel
      ↓
Chat Mode
      ↓
Work Mode
      ↓
Model Status
      ↓
Angel 4.2 RC
```

---

# Risk Register

| ID | Risk | Severity | Owner | Due |
|----|------|----------|-------|-----|
| RISK-001 | Project Context Leakage | Critical | Engineering Lead | Before Sprint 3 |
| RISK-002 | Evidence Drawer Becomes Developer UI | High | UX Lead | Sprint 2 Midpoint |
| RISK-003 | Work Mode Scope Expansion | High | Product Owner | Sprint 4 Planning |
| RISK-004 | Sidebar Complexity Growth | Medium | UX Lead | Sprint 1 Completion |
| RISK-005 | Context Panel Performance | Medium | Frontend Lead | Sprint 3 Completion |
| RISK-006 | Model Selection Confusion | Medium | Product Owner | Sprint 4 Completion |

---

# Contingency Plans

## RISK-001

Fallback:

```text
Selected Project
    ↓
Navigation Only

Conversation Context
    ↓
Persisted projectId Only
```

Release Impact: Blocks RC

## RISK-002

Fallback:

```text
▸ Evidence · N Sources
```

Hide advanced diagnostics.

## RISK-003

Fallback:

```text
Status
Progress
Current Step
```

No orchestration platform.

## RISK-004

Fallback:

```text
Home
Chats
Projects
Knowledge
Memory
Skills
Settings
```

## RISK-005

Fallback:

Summary-only Context Panel.

Lazy load details.

## RISK-006

Fallback:

```text
Answered By
LocalAI · Qwen
```

Read-only model indicator.

---

# Deferred Until Post-4.2

- Event Bus Runtime
- Payload Validation
- Advanced Contextual Pills
- Telemetry Enhancements
- Advanced Agent Workflows
- Autonomous Orchestration

---

# Guiding Principles

1. Fix state correctness before adding infrastructure.
2. Connect existing features before creating new ones.
3. Preserve conversation-first UX.
4. Use progressive disclosure for engineering detail.
5. Prefer scope reduction over correctness reduction.

---

# Definition of Success

```text
Projects
Knowledge
Memory
Files
Tools
Chat
```

are experienced as:

```text
One Assistant
One Workspace
One Context
```
