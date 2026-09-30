# ANGEL-412 Unified Workspace
## Build 4.2 — Consolidated Implementation Plan

**Status:** Sprint-ready planning build  
**Depends on:** Angel 4.1.1 Final Release Approval  
**Release Theme:** Connect the pieces before adding new pieces.

---

# 1. Product Objective

Angel 4.2 changes how existing capabilities are experienced rather than introducing major new subsystems.

The target experience is:

**One Assistant · One Workspace · One Context · One Source of Truth**

Existing 4.1.1 state ownership, project isolation, knowledge ownership, lifecycle behavior, and the 43-schema Project/RAG architecture remain authoritative.

---

# 2. Unified Workspace Model

```text
                         ANGEL
                           |
                  +--------+--------+
                  |                 |
                CHAT              WORK
                  |                 |
                  +--------+--------+
                           |
                        PROJECT
                           |
             +-------------+-------------+
             |             |             |
         KNOWLEDGE       FILES        MEMORY
             |             |             |
             +-------------+-------------+
                           |
                    RETRIEVAL SCOPE
                           |
                        RAG RUN
                           |
                      EVALUATION
                           |
                        EVIDENCE
```

The UI should communicate this architecture without exposing engineering complexity by default.

---

# 3. Sprint Plan

## Sprint 1 — Workspace Foundation

**Goal:** Establish project-aware navigation and conversation organization.

| Story | Description | Points |
|---|---|---:|
| ANGEL-412-1 | Sidebar Information Architecture | 5 |
| ANGEL-412-2 | Project Grouping | 8 |
| ANGEL-412-3 | Conversation Search | 5 |
| ANGEL-412-13 | Project Entry Experience | 5 |

### Acceptance

- Home, Chats, Projects, Knowledge, Memory, Skills, and Settings are consistently navigable.
- Projects are first-class workspaces.
- Conversations are grouped by project with General for unscoped conversations.
- Conversation search identifies project affiliation.
- Project entry does not create duplicate state.
- Existing functionality remains intact.

### Exit Gate

Sidebar remains navigation-focused and does not become an information dashboard.

---

# 4. Sprint 2 — Conversation Experience

**Goal:** Make conversations cleaner while preserving retrieval transparency.

| Story | Description | Points |
|---|---|---:|
| ANGEL-412-20 | Evidence Experience | 8 |
| ANGEL-412-21 | Simplified Message Layout | 5 |
| ANGEL-412-22 | Response Action Refinement | 3 |

### ANGEL-412-20 Evidence Experience

Evidence is one unified experience rather than separate competing components.

Acceptance:

- Evidence collapsed by default.
- Source count visible.
- Expand/collapse supported.
- Evidence drawer/panel available.
- Retrieved sources displayed.
- Retrieval scope displayed.
- Evaluation status displayed.
- Existing evidence preserved.

`ANGEL-412-30 Evidence Drawer` becomes an implementation subtask of 412-20 rather than a separate product story.

### Exit Gate

- Answer remains visually dominant.
- Evidence remains discoverable.
- Engineering details use progressive disclosure.
- UX and Product Owner approve evidence presentation.

---

# 5. Sprint 3 — Context-Aware Workspace

**Goal:** Connect projects, retrieval, conversations, memory, and workspace context.

| Story | Description | Points |
|---|---|---:|
| ANGEL-412-10 | Project Workspace Overview | 8 |
| ANGEL-412-11 | Project Context Visibility | 5 |
| ANGEL-412-31 | Retrieval Summary | 5 |
| ANGEL-412-32 | Evaluation Visibility | 3 |
| ANGEL-412-70 | Context Panel | 8 |
| ANGEL-412-71 | Memory Integration | 5 |

### Context Panel

Initial display:

```text
ACTIVE CONTEXT

Project
Angel Nexus

Conversation
Architecture Review

Knowledge
184 documents

Memory
Available

Skills
3 active

Tools
5 available
```

Use progressive disclosure rather than exposing all technical metadata immediately.

### Project Isolation Requirements

- Unscoped chats remain unscoped.
- Project chats retain project association.
- Refresh does not change project association.
- Switching projects updates visible context.
- Retrieval respects project scope.
- No project context leaks between projects.
- Existing 4.1.1 context-resolution logic remains authoritative.

### Exit Gate

- No project-context leakage.
- Context hydration meets performance budget.
- Retrieval scope is understandable.
- Context panel does not create a second state source.

---

# 6. Sprint 4 — Chat + Work Experience

**Goal:** Introduce the unified assistant workspace model.

| Story | Description | Points |
|---|---|---:|
| ANGEL-412-40 | Chat Mode | 5 |
| ANGEL-412-41 | Work Mode | 8 |
| ANGEL-412-42 | Work Timeline | 8 |
| ANGEL-412-50 | Model Status Panel | 5 |

### Chat Mode

Normal conversation, questions, answers, and brainstorming.

### Work Mode

Work Mode is limited to:

- Status
- Progress
- Visibility

It is not an autonomous workflow engine, orchestration framework, or tooling platform.

Example:

```text
WORKING ON

Angel Nexus Architecture

✓ Loaded project
✓ Retrieved architecture
✓ Inspected OpenAPI
● Analyzing workspace schema
○ Preparing analysis

[View Details]
```

### Model Status

Show:

- Backend
- Model
- Connection status
- Context capacity

### Model Selection

`ANGEL-412-53 Model Selection UX` remains deferred unless existing runtime support is already stable. Displaying model/backend state is in 4.2; changing routing between Local, Cloud, and Auto is a larger runtime concern.

---

# 7. Deferred 4.2.x Scope

Do not introduce these during the initial Unified Workspace rollout:

- Event Bus Runtime
- Payload Validation
- Advanced Contextual Pill Telemetry
- Advanced RAG Measurements UI
- Recommendation UI
- Snapshot UI
- Multi-step autonomous workflows
- Cross-project orchestration
- Background task scheduling
- New memory architecture
- New RAG architecture
- New project/context source of truth

---

# 8. Dependency Chain

```text
Angel 4.1.1 Final
        |
        v
Sidebar IA
        |
        v
Project Organization
        |
        v
Project Workspace
        |
        v
Evidence Experience
        |
        v
Project Context Visibility
        |
        v
Context Panel
        |
        v
Chat / Work Experience
        |
        v
Angel 4.2 RC
```

---

# 9. Risk Register

| ID | Risk | Severity | Owner | Checkpoint |
|---|---|---|---|---|
| RISK-001 | Project Context Leakage | Critical | Engineering Lead | Before Sprint 3 |
| RISK-002 | Evidence Becomes Developer UI | High | UX Lead | Sprint 2 Midpoint |
| RISK-003 | Work Mode Scope Expansion | High | Product Owner | Sprint 4 Planning |
| RISK-004 | Sidebar Complexity | Medium | UX Lead | Sprint 1 Completion |
| RISK-005 | Context Panel Performance | Medium | Frontend Lead | Sprint 3 Completion |
| RISK-006 | Model Selection Confusion | Medium | Product Owner | Sprint 4 Completion |

---

# 10. Risk Mitigations

## RISK-001 — Project Context Leakage

**Mitigation**

- Reuse 4.1.1 context-resolution layer.
- Run context regression suite.
- Execute dedicated context-boundary tests.
- Inspect RAG Run scope.

**Release condition:** No project scope leakage detected.

## RISK-002 — Evidence Becomes Developer UI

**Mitigation**

- Collapse by default.
- Show summaries first.
- Hide technical fields.
- UX review at Sprint 2 midpoint.

**Release condition:** Evidence approved as progressive-disclosure UX.

## RISK-003 — Work Mode Scope Expansion

**Mitigation**

- Lock Work Mode scope during Sprint 4 planning.
- Restrict to status, progress, and visibility.
- Explicitly prohibit autonomous workflow/orchestration expansion.

**Release condition:** Scope remains lightweight.

## RISK-004 — Sidebar Complexity

**Mitigation**

- Keep sidebar navigation-focused.
- Separate navigation from information display.
- UX review at Sprint 1 completion.

**Release condition:** Navigation hierarchy validated.

## RISK-005 — Context Panel Performance

**Mitigation**

- Profile context hydration.
- Measure rendering.
- Lazy-load secondary information.
- Cache summaries where appropriate.
- Incrementally render context.

**Release condition:** Context panel meets performance budget.

## RISK-006 — Model Selection Confusion

**Mitigation**

- Complete Model Status before model selection.
- Clearly distinguish Local, Cloud, and Auto.
- Verify backend status.

**Release condition:** User can understand the available modes without documentation.

---

# 11. Release Risk Gates

Before Angel 4.2 RC:

### Critical

- RISK-001 mitigated and approved.

### High

- RISK-002 mitigated and approved.
- RISK-003 mitigated and approved.

### Medium

- RISK-004 mitigated and approved.
- RISK-005 mitigated and approved.
- RISK-006 mitigated and approved.

---

# 12. Release Candidate Checklist

- [ ] Sprint 1 complete
- [ ] Sprint 2 complete
- [ ] Sprint 3 complete
- [ ] Sprint 4 complete
- [ ] No project-context regressions
- [ ] Evidence UX approved
- [ ] Work Mode scope controlled
- [ ] Context panel performance approved
- [ ] Model/backend status verified
- [ ] No duplicate source of truth introduced
- [ ] 4.1.1 state ownership remains authoritative

---

# 13. Definition of Done

Angel 4.2 Unified Workspace is complete when:

**Projects**

**Knowledge**

**Memory**

**Files**

**Tools**

**Chat**

are experienced as:

**One Workspace**

**One Context**

**One Assistant**

**One Source of Truth**

rather than a collection of screens connected by a sidebar.

The RAG lifecycle remains available when needed but does not dominate the user experience.

---

# 14. Governing Principle

> **State correctness was the foundation of 4.1.1.**
>
> **Workspace integration is the foundation of 4.2.**
>
> **Connect the pieces before adding new pieces.**

No Event Bus, Payload Validation, advanced agent workflow, or major new subsystem should be introduced merely to complete the Unified Workspace experience.
