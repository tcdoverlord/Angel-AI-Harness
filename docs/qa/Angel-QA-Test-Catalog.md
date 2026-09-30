# QA Test Catalog Addendum

## Purpose
This catalog supplements the ANGEL-411 and ANGEL-412 program handbook.

---

# QA-001 Project Context Isolation

## Objective
Verify project selection never changes conversation ownership.

### Test Cases
- Select project, start New Chat
- Switch projects while chat is open
- Reload browser
- Restore historical project conversation

### Expected
- New Chat uses projectId=null
- Existing project chats preserve project scope
- RagRuns match conversation scope

Priority: P0

---

# QA-002 Knowledge Pack Selection

## Objective
Verify exact pack resolution.

### Test Cases
- Pack A -> A
- Pack B -> B
- Pack C -> C
- Rapid pack switching

### Expected
- Correct content displayed
- No stale content
- No fallback to previous pack

Priority: P0

---

# QA-003 Stale Selection Recovery

### Test Cases
- Delete selected pack
- Delete selected document
- Refresh after deletion

### Expected
- Selection cleared
- Safe view shown
- No runtime exceptions

Priority: P0

---

# QA-004 Remove Document

### Verify
- Document removed from UI
- Document removed from persistence
- Chunks removed
- Index rebuilt
- Retrieval fails for deleted document

Priority: P1

---

# QA-005 Remove Pack

### Verify
- Pack removed
- Documents removed
- Index rebuilt
- Conversations preserved
- RagRuns preserved
- Evidence preserved

Priority: P1

---

# QA-006 Workspace Cohesion

### Verify
- Project -> Chat flow
- Knowledge -> Chat flow
- Context visibility
- Retrieval visibility

Priority: P1

---

# QA-101 Sidebar Navigation

### Verify
- Home, Chats, Projects, Knowledge, Memory, Skills, Settings
- Navigation remains usable on desktop and mobile

Priority: P2

---

# QA-102 Evidence Drawer

### Verify
- Collapsed by default
- Answer remains primary focus
- Expansion shows evidence

Priority: P2

---

# QA-103 Context Panel

### Verify
- Project context
- Memory context
- Knowledge context
- Performance budget

Priority: P2

---

# QA-104 Work Mode

### Verify
- Progress tracking
- Status visibility
- No workflow-engine behavior introduced

Priority: P2

---

# Exit Criteria

P0 Tests: 100% Pass
P1 Tests: 100% Pass
Critical Defects: 0 Open
High Defects: 0 Open
