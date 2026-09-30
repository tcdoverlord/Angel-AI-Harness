# ANGEL-412 Risk Register Addendum
## Mitigation Owners, Due Dates & Contingency Plans

### Contingency Principles

1. Preserve the stable Angel 4.1.1 behavior.
2. Disable or defer the affected feature rather than weakening state correctness.
3. Use feature flags for high-risk workspace changes.
4. Do not reopen the canonical architecture to solve a UI delivery problem.
5. Do not advance to Release Candidate while a critical risk remains uncontrolled.
6. Record every contingency decision in the release log.

---

## RISK-001: Project Context Leakage Reintroduced

**Severity:** Critical  
**Mitigation Owner:** Engineering Lead  
**Due:** Before Sprint 3 begins  
**Decision Owner:** Engineering Lead  
**Escalation:** Product Owner

### Trigger Conditions

- A global New Chat inherits the selected project.
- A conversation opens with the wrong projectId.
- A RAG Run records a project scope different from its conversation.
- Switching projects changes an existing conversation's ownership.
- Context-isolation regression tests fail.

### Immediate Response

- Stop rollout of Project Context Visibility.
- Disable project-context hydration in the new workspace UI.
- Preserve the Angel 4.1.1 context resolver as the only authoritative resolver.
- Revert affected context-selection changes.
- Mark the affected build as not eligible for Release Candidate.
- Capture reproduction data.

### Fallback Behavior

```text
Selected Project
      ↓
Workspace Navigation Only

Conversation Context
      ↓
Persisted conversation.projectId Only
```

### Recovery Plan

- Add a regression test for the discovered leakage path.
- Verify New Chat isolation.
- Verify existing project conversations.
- Verify refresh and deep-link behavior.
- Inspect resulting RAG Run context.
- Obtain Engineering Lead approval before re-enabling.

### Release Impact

**Release Blocking:** Yes

---

## RISK-002: Evidence Drawer Becomes Developer UI

**Severity:** High  
**Mitigation Owner:** UX Lead  
**Due:** Sprint 2 Midpoint

### Contingency

If evidence clutter harms the conversation experience:

```text
Ship:
▸ Evidence · N sources

Defer:
Advanced retrieval diagnostics
```

### Release Impact

Block the feature, not the release.

---

## RISK-003: Work Mode Scope Expansion

**Severity:** High  
**Mitigation Owner:** Product Owner  
**Due:** Sprint 4 Planning

### Contingency

Reduce Work Mode to:

```text
Status
Progress
Current Step
Completed Steps
```

Defer workflow engines, autonomous orchestration, and automation frameworks.

### Release Impact

Work Mode may be deferred without blocking Unified Workspace.

---

## RISK-004: Sidebar Complexity Growth

**Severity:** Medium  
**Mitigation Owner:** UX Lead  
**Due:** Sprint 1 Completion

### Contingency

Fallback navigation:

```text
Home
Chats
Projects
Knowledge
Memory
Skills
Settings
```

Remove advanced grouping until usability is validated.

---

## RISK-005: Context Panel Performance Issues

**Severity:** Medium  
**Mitigation Owner:** Frontend Lead  
**Due:** Sprint 3 Completion

### Contingency

Use summary-only mode:

```text
Project: Available
Knowledge: Available
Memory: Available
```

Load detailed context lazily.

---

## RISK-006: Model Selection Confusion

**Severity:** Medium  
**Mitigation Owner:** Product Owner  
**Due:** Sprint 4 Completion

### Contingency

Ship a read-only indicator:

```text
Answered By
LocalAI · Qwen
```

Defer manual model switching.

---

## Consolidated Contingency Matrix

| Risk | Primary Contingency | Release Impact |
|------|--------------------|----------------|
| RISK-001 | Revert to persisted conversation context only | Blocks RC |
| RISK-002 | Ship compact evidence control | Feature-level impact |
| RISK-003 | Reduce Work Mode to status/progress only | Non-blocking |
| RISK-004 | Ship simplified navigation | Non-blocking |
| RISK-005 | Use lazy-loaded summary panel | Non-blocking |
| RISK-006 | Use read-only model indicator | Non-blocking |

---

## Release Principle

**Reduce scope before reducing correctness.**
