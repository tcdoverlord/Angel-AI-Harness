# Angel Platform Program Handbook
## ANGEL-411 Workspace Cohesion & ANGEL-412 Unified Workspace

Version: 1.0
Status: Program Handbook
Audience: Product, Engineering, UX, QA, Leadership

---

# Executive Summary

This handbook defines the roadmap from Angel 4.1.1 Workspace Cohesion to Angel 4.2 Unified Workspace.

Objectives:

1. Fix workspace state correctness.
2. Establish knowledge ownership.
3. Create a cohesive user experience.
4. Transform Angel into a unified workspace.
5. Preserve conversation-first interaction.

---

# Strategic Vision

```text
ANGEL
  |
CHAT -------- WORK
  |             |
  +------ PROJECT ------+
          |             |
      KNOWLEDGE      FILES
          |
        MEMORY
          |
    RETRIEVAL SCOPE
          |
        RAG RUN
          |
       EVIDENCE
```

Guiding principle:

> One Assistant. One Workspace. One Context.

---

# Program Governance

## Product Owner

Responsible for:
- Product direction
- Scope control
- Release approval

## Engineering Lead

Responsible for:
- Technical quality
- Architecture compliance
- Release readiness

## UX Lead

Responsible for:
- Navigation
- Conversation experience
- Workspace usability

## QA Lead

Responsible for:
- Validation
- Regression testing
- Release certification

---

# ANGEL-411
## Workspace Cohesion Release Candidate

### Goal

Stabilize workspace behavior before introducing new infrastructure.

## P0 Release Blockers

### Project Context Isolation

Acceptance:

- New Chat always global
- Project conversations preserve context
- RagRuns use conversation scope
- No leakage

### Knowledge Pack Selection

Acceptance:

- Pack A -> A
- Pack B -> B
- Pack C -> C
- No fallback logic
- No stale state

### Stale Selection Recovery

Acceptance:

- Deleted pack clears selection
- Deleted document clears selection
- Safe fallback navigation

## P1 Features

### Remove Document

Deletes:
- Document
- Sections
- Chunks
- Embeddings
- Retrieval references
- Index entries

### Remove Pack

Deletes:
- Pack
- Documents
- Sections
- Chunks
- Embeddings
- Retrieval references
- Index entries

Preserves:
- Conversations
- Projects
- RagRuns
- Evidence

### Workspace Validation

Validate:
- Projects
- Knowledge
- Chat
- Recovery
- Deletion

---

# ANGEL-411 Release Gate

## Engineering Sign-Off

- [ ] Context isolation verified
- [ ] Selection correctness verified
- [ ] Recovery verified

## Product Sign-Off

- [ ] Knowledge deletion verified
- [ ] Workspace cohesion verified
- [ ] User workflows verified

---

# ANGEL-412
## Unified Workspace Epic

## Objective

Connect existing capabilities into a single coherent workspace.

Not:

```text
Chat
+
Projects
+
Knowledge
```

Instead:

```text
Unified Workspace
```

---

# Roadmap Overview

## Sprint 1
### Workspace Foundation

Stories:

- ANGEL-412-1 Sidebar Information Architecture
- ANGEL-412-2 Project Grouping
- ANGEL-412-3 Conversation Search
- ANGEL-412-10 Project Workspace Overview

Deliverables:

- Workspace navigation
- Project organization
- Search capability
- Project landing experience

Success:

- Projects feel first-class
- Navigation is simplified

---

## Sprint 2
### Conversation Experience

Stories:

- ANGEL-412-20 Collapsible Evidence
- ANGEL-412-21 Simplified Message Layout
- ANGEL-412-22 Response Action Refinement
- ANGEL-412-30 Evidence Drawer

Deliverables:

- Cleaner messages
- Progressive disclosure
- Minimal evidence controls

Success:

- Conversation remains primary focus

---

## Sprint 3
### Context-Aware Workspace

Stories:

- ANGEL-412-11 Project Context Visibility
- ANGEL-412-31 Retrieval Summary
- ANGEL-412-32 Evaluation Visibility
- ANGEL-412-70 Context Panel
- ANGEL-412-71 Memory Integration

Deliverables:

- Visible project context
- Context transparency
- Retrieval visibility

Success:

- Users understand why Angel answered

---

## Sprint 4
### Chat + Work Experience

Stories:

- ANGEL-412-40 Chat Mode
- ANGEL-412-41 Work Mode
- ANGEL-412-42 Work Timeline
- ANGEL-412-50 Model Status Panel
- ANGEL-412-53 Model Selection UX

Deliverables:

- Work tracking
- Backend visibility
- Model transparency

Success:

- Angel feels like an assistant workspace

---

# Story Dependency Map

```text
4.1.1 Release
      ↓
Sidebar IA
      ↓
Workspace Overview
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
Model Visibility
      ↓
4.2 Release Candidate
```

---

# RACI Matrix Summary

| Area | Responsible | Accountable |
|------|------|------|
| Context Isolation | Backend + Frontend | Engineering Lead |
| Knowledge Selection | Frontend | Engineering Lead |
| Recovery Logic | Frontend | Engineering Lead |
| Workspace UX | UX + Frontend | Product Owner |
| Context Panel | Frontend | Engineering Lead |
| Work Mode | Product + Frontend | Product Owner |
| Release QA | QA Team | QA Lead |

---

# Risk Register

| Risk | Severity | Owner | Due |
|------|----------|-------|-----|
| Context Leakage | Critical | Engineering Lead | Before Sprint 3 |
| Evidence Too Technical | High | UX Lead | Sprint 2 |
| Work Mode Scope Creep | High | Product Owner | Sprint 4 Planning |
| Sidebar Complexity | Medium | UX Lead | Sprint 1 |
| Context Performance | Medium | Frontend Lead | Sprint 3 |
| Model Confusion | Medium | Product Owner | Sprint 4 |

---

# Mitigation & Contingency Plans

## Context Leakage

Mitigation:
- Context boundary tests
- RagRun validation
- Regression suite

Contingency:

```text
Selected Project
    ↓
Navigation Only
```

Release Impact:
- Blocks Release Candidate

---

## Evidence UX Failure

Mitigation:
- UX review
- Progressive disclosure

Contingency:

```text
▸ Evidence · N Sources
```

Advanced diagnostics deferred.

---

## Work Mode Scope Creep

Mitigation:
- Feature freeze
- Scope review

Contingency:

Only provide:
- Status
- Progress
- Current step

---

## Sidebar Complexity

Contingency:

```text
Home
Chats
Projects
Knowledge
Memory
Skills
Settings
```

---

## Context Performance

Contingency:

Summary-only mode with lazy loading.

---

## Model Selection Confusion

Contingency:

```text
Answered By
LocalAI · Qwen
```

Read-only mode.

---

# Release Calendar

## Milestone 1
ANGEL-411 RC

## Milestone 2
ANGEL-411 Final Release

## Milestone 3
Sprint 1 Complete

## Milestone 4
Sprint 2 Complete

## Milestone 5
Sprint 3 Complete

## Milestone 6
Sprint 4 Complete

## Milestone 7
ANGEL-412 RC

## Milestone 8
ANGEL-412 Release

---

# KPIs

## Workspace Cohesion

- Project navigation success rate
- Conversation retrieval success rate
- Knowledge navigation success rate

## User Experience

- Time to start work
- Chat engagement
- Evidence expansion usage

## Reliability

- Context leakage incidents
- Selection-state errors
- Deletion failures

Target:

```text
0 context leakage incidents
0 stale selection incidents
100% successful deletion reconciliation
```

---

# Architecture Decision Record Summary

ADR-001
State correctness before infrastructure.

ADR-002
Conversation-first UX.

ADR-003
Progressive disclosure for retrieval.

ADR-004
Historical records are immutable.

ADR-005
Scope reduction preferred over correctness reduction.

---

# Deferred Backlog

Post-4.2:

- Event Bus Runtime
- Payload Validation
- Advanced Contextual Pills
- Telemetry Framework
- Multi-step Agents
- Background Orchestration
- Workflow Engine

---

# Final Definition of Success

Users should perceive:

```text
Projects
Knowledge
Memory
Files
Tools
Chat
```

as:

```text
One Assistant
One Workspace
One Context
```

rather than separate screens connected by navigation.
