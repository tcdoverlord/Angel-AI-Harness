# Angel Platform Requirements Traceability Matrix
## ANGEL-411 Workspace Cohesion and ANGEL-412 Unified Workspace

**Version:** 1.0  
**Status:** Program Governance Artifact  
**Purpose:** Trace business objectives, epics, stories, risks, acceptance criteria, QA tests, owners, dependencies, and release gates.

---

# 1. Traceability Model

```text
Program Objective
      ↓
Epic
      ↓
Story / Requirement
      ↓
Acceptance Criteria
      ↓
QA Test Case
      ↓
Risk Control
      ↓
Release Gate
```

## Status Legend

| Status | Meaning |
|---|---|
| Planned | Approved but not started |
| In Progress | Implementation or validation underway |
| Passed | Acceptance and QA complete |
| Blocked | Dependency or defect prevents completion |
| Deferred | Explicitly moved outside the current release |

## Priority Legend

| Priority | Meaning |
|---|---|
| P0 | Release blocker |
| P1 | Required for release |
| P2 | Planned enhancement |
| P3 | Future backlog |

---

# 2. Program Objective Traceability

| Objective ID | Program Objective | Epic | Primary Evidence | Release Gate |
|---|---|---|---|---|
| OBJ-001 | Eliminate project-context leakage | ANGEL-411 | Context-isolation tests and RAG Run inspection | 4.1.1 P0 Gate |
| OBJ-002 | Ensure exact knowledge-pack and document selection | ANGEL-411 | Pack and document switching tests | 4.1.1 P0 Gate |
| OBJ-003 | Provide safe recovery from deleted selections | ANGEL-411 | Stale-selection recovery tests | 4.1.1 P0 Gate |
| OBJ-004 | Give users real ownership of stored knowledge | ANGEL-411 | Document and pack deletion validation | 4.1.1 P1 Gate |
| OBJ-005 | Preserve immutable historical engineering records | ANGEL-411 | Historical conversation, RAG Run, and evidence checks | 4.1.1 P1 Gate |
| OBJ-006 | Make Chat, Projects, Knowledge, Memory, Files, and Tools feel unified | ANGEL-412 | End-to-end workspace UX validation | 4.2 RC Gate |
| OBJ-007 | Preserve conversation-first interaction | ANGEL-412 | Message hierarchy and evidence progressive-disclosure tests | 4.2 RC Gate |
| OBJ-008 | Make active context and model/backend usage understandable | ANGEL-412 | Context-panel and model-status tests | 4.2 RC Gate |

---

# 3. ANGEL-411 Requirements Traceability

| Requirement ID | Story / Requirement | Priority | Owner | Dependencies | Acceptance Criteria | QA Test | Risk | Gate | Status |
|---|---|---:|---|---|---|---|---|---|---|
| A411-1 | Project Context Isolation | P0 | Backend + Frontend | Existing conversation persistence | New Chat uses `projectId = null`; project conversations retain stored context; RAG Runs use conversation scope | QA-001 | RISK-001 | 4.1.1 P0 | Planned |
| A411-2 | Exact Knowledge Pack Selection | P0 | Frontend | Knowledge Center state model | Pack A opens A; Pack B opens B; Pack C opens C; no fallback to pack 261 | QA-002 | RISK-007 | 4.1.1 P0 | Planned |
| A411-3 | Stale Selection Cleanup | P0 | Frontend | A411-2 | Deleting the selected pack or document clears selection and returns to a safe view | QA-003 | RISK-008 | 4.1.1 P0 | Planned |
| A411-4 | Remove Document | P1 | Backend + Frontend | A411-2, A411-3 | Document, sections, chunks, embeddings, retrieval references, and index entries removed | QA-004 | RISK-009 | 4.1.1 P1 | Planned |
| A411-5 | Remove Knowledge Pack | P1 | Backend + Frontend | A411-4 | Pack deletion cascades through current knowledge while preserving historical records | QA-005 | RISK-009, RISK-010 | 4.1.1 P1 | Planned |
| A411-6 | Workspace Cohesion Validation | P1 | QA + Product | A411-1 through A411-5 | Projects, Knowledge, Chat, deletion, and recovery operate coherently | QA-006 | All ANGEL-411 risks | 4.1.1 P1 | Planned |

---

# 4. ANGEL-412 Sprint and Story Traceability

## Sprint 1: Workspace Foundation

| Story ID | Story | Priority | Owner | Depends On | Acceptance Criteria | QA Test | Risk | Exit Gate | Status |
|---|---|---:|---|---|---|---|---|---|---|
| ANGEL-412-1 | Sidebar Information Architecture | P2 | UX + Frontend | Angel 4.1.1 final approval | Home, Chats, Projects, Knowledge, Memory, Skills, and Settings are consistently organized | QA-101 | RISK-004 | Sprint 1 | Planned |
| ANGEL-412-2 | Project Grouping | P2 | Frontend | ANGEL-412-1 | Conversations grouped by project; global conversations remain distinguishable; groups are collapsible | QA-105 | RISK-004 | Sprint 1 | Planned |
| ANGEL-412-3 | Conversation Search | P2 | Frontend | ANGEL-412-1 | Search returns matching chats with project affiliation and direct navigation | QA-106 | RISK-011 | Sprint 1 | Planned |
| ANGEL-412-10 | Project Workspace Overview | P2 | Frontend + Product | A411-1, ANGEL-412-1 | Project overview shows chats, knowledge, files, retrieval scope, and model summary | QA-107 | RISK-001 | Sprint 1 | Planned |

## Sprint 2: Conversation Experience

| Story ID | Story | Priority | Owner | Depends On | Acceptance Criteria | QA Test | Risk | Exit Gate | Status |
|---|---|---:|---|---|---|---|---|---|---|
| ANGEL-412-20 | Collapsible Evidence | P2 | Frontend + UX | Existing RAG Run and evidence records | Evidence is collapsed by default; source count is visible; answer remains dominant | QA-102 | RISK-002 | Sprint 2 | Planned |
| ANGEL-412-21 | Simplified Message Layout | P2 | Frontend + UX | Existing conversation UI | Answer is primary; technical details are visually secondary; existing actions remain available | QA-108 | RISK-002 | Sprint 2 | Planned |
| ANGEL-412-22 | Response Action Refinement | P2 | Frontend + UX | Existing contextual actions | Maximum three quiet contextual actions; universal message actions remain separate | QA-109 | RISK-002, RISK-004 | Sprint 2 | Planned |
| ANGEL-412-30 | Evidence Drawer | P2 | Frontend + UX | ANGEL-412-20 | Drawer shows supporting sources, retrieval scope, evaluation status, and Inspector entry point | QA-102, QA-110 | RISK-002 | Sprint 2 | Planned |

## Sprint 3: Context-Aware Workspace

| Story ID | Story | Priority | Owner | Depends On | Acceptance Criteria | QA Test | Risk | Exit Gate | Status |
|---|---|---:|---|---|---|---|---|---|---|
| ANGEL-412-11 | Project Context Visibility | P2 | Frontend + Backend | A411-1, ANGEL-412-10 | Active project and retrieval scope are shown without changing conversation ownership | QA-111 | RISK-001 | Sprint 3 | Planned |
| ANGEL-412-31 | Retrieval Summary | P2 | Frontend | ANGEL-412-30 | Retrieved, selected, and source summary is understandable without debug terminology | QA-112 | RISK-002 | Sprint 3 | Planned |
| ANGEL-412-32 | Evaluation Visibility | P2 | Frontend | ANGEL-412-31 | Pending, Complete, and Not Evaluated states display consistently | QA-113 | RISK-012 | Sprint 3 | Planned |
| ANGEL-412-70 | Context Panel | P2 | Frontend | ANGEL-412-11, ANGEL-412-71 | Project, conversation, knowledge, memory, skills, and tools display incrementally | QA-103 | RISK-005 | Sprint 3 | Planned |
| ANGEL-412-71 | Memory Integration | P2 | Frontend + Backend | Existing Memory system | Relevant memory appears in context without redesigning the memory subsystem | QA-114 | RISK-005, RISK-013 | Sprint 3 | Planned |

## Sprint 4: Chat and Work Experience

| Story ID | Story | Priority | Owner | Depends On | Acceptance Criteria | QA Test | Risk | Exit Gate | Status |
|---|---|---:|---|---|---|---|---|---|---|
| ANGEL-412-40 | Chat Mode | P2 | Frontend | ANGEL-412-70 | Existing conversational behavior is retained in a clear Chat mode | QA-115 | RISK-014 | Sprint 4 | Planned |
| ANGEL-412-41 | Work Mode | P2 | Product + Frontend | ANGEL-412-40, ANGEL-412-70 | Work mode shows task status and progress without becoming an orchestration framework | QA-104 | RISK-003 | Sprint 4 | Planned |
| ANGEL-412-42 | Work Timeline | P2 | Frontend | ANGEL-412-41 | Completed, current, and pending work steps display correctly | QA-116 | RISK-003, RISK-005 | Sprint 4 | Planned |
| ANGEL-412-50 | Model Status Panel | P2 | Frontend + Backend | Existing model-status APIs | Actual backend, model, connection state, and context capacity are visible | QA-117 | RISK-006 | Sprint 4 | Planned |
| ANGEL-412-53 | Model Selection UX | P2 | Product + Frontend | ANGEL-412-50 | Local, Cloud, and Auto are understandable; selected and actual model remain aligned | QA-118 | RISK-006 | Sprint 4 | Planned |

---

# 5. QA Test Catalog Traceability

| Test ID | Test Name | Traces To | Priority | Test Type | Owner | Required Result |
|---|---|---|---:|---|---|---|
| QA-001 | Project Context Isolation | OBJ-001, A411-1 | P0 | Functional + Regression | QA | 100% pass |
| QA-002 | Knowledge Pack Selection | OBJ-002, A411-2 | P0 | Functional + Regression | QA | 100% pass |
| QA-003 | Stale Selection Recovery | OBJ-003, A411-3 | P0 | Functional + Recovery | QA | 100% pass |
| QA-004 | Remove Document | OBJ-004, A411-4 | P1 | Integration + Data Integrity | QA | 100% pass |
| QA-005 | Remove Pack | OBJ-004, OBJ-005, A411-5 | P1 | Integration + Data Integrity | QA | 100% pass |
| QA-006 | Workspace Cohesion | OBJ-006, A411-6 | P1 | End-to-End + UAT | QA + Product | Approved |
| QA-101 | Sidebar Navigation | ANGEL-412-1 | P2 | UX + Functional | QA + UX | Approved |
| QA-102 | Evidence Progressive Disclosure | ANGEL-412-20, ANGEL-412-30 | P2 | UX + Accessibility | QA + UX | Approved |
| QA-103 | Context Panel | ANGEL-412-70 | P2 | Performance + Functional | QA + Frontend | Within budget |
| QA-104 | Work Mode | ANGEL-412-41 | P2 | Scope + Functional | QA + Product | Approved |
| QA-105 | Project Grouping | ANGEL-412-2 | P2 | Functional | QA | Pass |
| QA-106 | Conversation Search | ANGEL-412-3 | P2 | Functional + Performance | QA | Pass |
| QA-107 | Project Workspace Overview | ANGEL-412-10 | P2 | Functional + UX | QA + Product | Approved |
| QA-108 | Simplified Message Layout | ANGEL-412-21 | P2 | Visual + Regression | QA + UX | Approved |
| QA-109 | Response Actions | ANGEL-412-22 | P2 | Functional + Accessibility | QA | Pass |
| QA-110 | Evidence Drawer Details | ANGEL-412-30 | P2 | Functional + Accessibility | QA | Pass |
| QA-111 | Project Context Visibility | ANGEL-412-11 | P2 | Regression + Functional | QA | Pass |
| QA-112 | Retrieval Summary | ANGEL-412-31 | P2 | Functional + UX | QA + UX | Approved |
| QA-113 | Evaluation Visibility | ANGEL-412-32 | P2 | State Coverage | QA | Pass |
| QA-114 | Memory Integration | ANGEL-412-71 | P2 | Integration + Privacy | QA | Pass |
| QA-115 | Chat Mode | ANGEL-412-40 | P2 | Regression + UAT | QA + Product | Approved |
| QA-116 | Work Timeline | ANGEL-412-42 | P2 | Functional | QA | Pass |
| QA-117 | Model Status | ANGEL-412-50 | P2 | Integration | QA | Pass |
| QA-118 | Model Selection | ANGEL-412-53 | P2 | Functional + Failover | QA + Product | Approved |

---

# 6. Risk-to-Control Traceability

| Risk ID | Risk | Affected Stories | Preventive Control | Detective Control | Contingency | Owner | Due |
|---|---|---|---|---|---|---|---|
| RISK-001 | Project context leakage | A411-1, ANGEL-412-10, ANGEL-412-11 | Persisted conversation context remains authoritative | QA-001 and QA-111 | Revert to navigation-only project selection | Engineering Lead | Before Sprint 3 |
| RISK-002 | Evidence becomes developer UI | ANGEL-412-20, 21, 22, 30, 31 | Progressive disclosure and UX review | QA-102, 108, 109, 110, 112 | Ship compact `Evidence · N sources` control | UX Lead | Sprint 2 midpoint |
| RISK-003 | Work Mode scope expansion | ANGEL-412-41, 42 | Freeze scope to status and progress | QA-104 and scope review | Defer Work Mode or ship read-only timeline | Product Owner | Sprint 4 planning |
| RISK-004 | Sidebar complexity | ANGEL-412-1, 2, 22 | Navigation-only information architecture | QA-101 and QA-105 | Ship simplified top-level navigation | UX Lead | Sprint 1 completion |
| RISK-005 | Context-panel performance | ANGEL-412-70, 71, 42 | Lazy loading and cached summaries | QA-103 performance checks | Summary-only context panel | Frontend Lead | Sprint 3 completion |
| RISK-006 | Model-selection confusion | ANGEL-412-50, 53 | Status panel before selector | QA-117 and QA-118 | Read-only actual-model indicator | Product Owner | Sprint 4 completion |
| RISK-007 | Wrong pack rendered | A411-2 | Exact ID resolution and stale-state reset | QA-002 | Disable detail view until exact pack loads | Frontend Lead | 4.1.1 P0 gate |
| RISK-008 | Deleted object remains selected | A411-3 | Selection invalidation | QA-003 | Return to list view and clear IDs | Frontend Lead | 4.1.1 P0 gate |
| RISK-009 | Incomplete current-knowledge deletion | A411-4, A411-5 | Transactional cascade and index reconciliation | QA-004 and QA-005 | Roll back deletion and rebuild index | Backend Lead | 4.1.1 P1 gate |
| RISK-010 | Historical records deleted with pack | A411-5 | Explicit preservation constraints | QA-005 historical checks | Restore from backup and block release | Engineering Lead | 4.1.1 P1 gate |
| RISK-011 | Search degrades with large history | ANGEL-412-3 | Pagination and indexed lookup | QA-106 performance case | Limit initial result set | Frontend Lead | Sprint 1 completion |
| RISK-012 | Evaluation state misrepresented | ANGEL-412-32 | Explicit state enum | QA-113 | Display Not Evaluated when uncertain | Engineering Lead | Sprint 3 completion |
| RISK-013 | Memory exposed outside intended context | ANGEL-412-71 | Scope and privacy filtering | QA-114 | Hide memory section | Product Owner | Sprint 3 completion |
| RISK-014 | Chat regression during mode split | ANGEL-412-40 | Preserve existing Chat behavior | QA-115 | Disable mode switch and retain Chat only | Engineering Lead | Sprint 4 completion |

---

# 7. Release-Gate Traceability

## Angel 4.1.1 P0 Gate

- [ ] A411-1 complete
- [ ] A411-2 complete
- [ ] A411-3 complete
- [ ] QA-001 passed
- [ ] QA-002 passed
- [ ] QA-003 passed
- [ ] RISK-001 controlled
- [ ] RISK-007 controlled
- [ ] RISK-008 controlled
- [ ] Engineering Lead approval

## Angel 4.1.1 P1 Gate

- [ ] A411-4 complete
- [ ] A411-5 complete
- [ ] A411-6 complete
- [ ] QA-004 passed
- [ ] QA-005 passed
- [ ] QA-006 approved
- [ ] RISK-009 controlled
- [ ] RISK-010 controlled
- [ ] Product Owner approval

## Angel 4.2 Sprint Gates

### Sprint 1

- [ ] ANGEL-412-1, 2, 3, and 10 accepted
- [ ] QA-101, 105, 106, and 107 passed
- [ ] RISK-004 and RISK-011 controlled

### Sprint 2

- [ ] ANGEL-412-20, 21, 22, and 30 accepted
- [ ] QA-102, 108, 109, and 110 passed
- [ ] RISK-002 controlled

### Sprint 3

- [ ] ANGEL-412-11, 31, 32, 70, and 71 accepted
- [ ] QA-103 and QA-111 through QA-114 passed
- [ ] RISK-001, 005, 012, and 013 controlled

### Sprint 4

- [ ] ANGEL-412-40, 41, 42, 50, and 53 accepted
- [ ] QA-104 and QA-115 through QA-118 passed
- [ ] RISK-003, 006, and 014 controlled

## Angel 4.2 Release Candidate Gate

- [ ] All sprint gates passed
- [ ] Zero open critical defects
- [ ] Zero open high-severity defects
- [ ] No unresolved project-context regressions
- [ ] Conversation-first UX approved
- [ ] Context-panel performance approved
- [ ] Model/backend attribution verified
- [ ] QA Lead approval
- [ ] Engineering Lead approval
- [ ] Product Owner approval

---

# 8. Coverage Summary

| Coverage Area | Planned Items | Traced Items | Target Coverage |
|---|---:|---:|---:|
| Program objectives | 8 | 8 | 100% |
| ANGEL-411 requirements | 6 | 6 | 100% |
| ANGEL-412 stories | 18 | 18 | 100% |
| QA tests | 22 | 22 | 100% |
| Identified risks | 14 | 14 | 100% |
| Release gates | 7 | 7 | 100% |

> Counts in this matrix represent the planned traceability model. Actual delivery status must be updated as implementation and QA evidence become available.

---

# 9. Change-Control Rules

1. Every new story must trace to at least one program objective.
2. Every release-bound story must have at least one QA test.
3. Every critical or high risk must have an owner, due point, mitigation, and contingency.
4. Every failed release-gate item must link to a defect or approved waiver.
5. Deferred items must retain their original requirement and traceability links.
6. Historical delivery evidence must not be overwritten when a requirement changes.

---

# 10. Approval Record

| Role | Name | Decision | Date | Notes |
|---|---|---|---|---|
| Product Owner |  |  |  |  |
| Engineering Lead |  |  |  |  |
| UX Lead |  |  |  |  |
| QA Lead |  |  |  |  |

---

# Definition of Complete Traceability

The traceability matrix is complete when every release requirement can be followed in both directions:

```text
Objective → Epic → Story → Acceptance Criteria → Test → Risk Control → Release Gate
```

and:

```text
Test Failure → Story → Requirement → Objective → Release Impact
```
