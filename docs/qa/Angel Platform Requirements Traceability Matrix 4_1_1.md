This traceability matrix consolidates the approved ANGEL-411/412 requirements, the executable QA cases, identified risks, and release gates. It also adds the later 4.2.1 P0 regression coverage for conversation selection/copy and single-instance Read Aloud.

Angel Platform Requirements Traceability Matrix

Version: 1.1
 Scope: Angel 4.1.1 Workspace Cohesion and Angel 4.2.1 Unified Workspace
 Status: Proposed QA baseline
 Traceability chain: Objective → Requirement → Acceptance criteria → Test case → Risk control → Release gate

The original governance model defines eight program objectives, six ANGEL-411 requirements, 18 original ANGEL-412 stories, 22 original QA entries, 14 risks, and seven release gates.

1. Status Definitions
Status	MeaningPlanned	Approved but implementation evidence has not been reviewed
Implemented	Code or release notes indicate implementation
Test Ready	Test steps and expected results are defined
Passed	Objective evidence confirms the test passed
Failed	Test execution produced a nonconforming result
Blocked	A dependency or defect prevents testing
Deferred	Explicitly moved outside the current release
Not Verified	Implementation may exist, but sufficient execution evidence is unavailable

Important: A release-note claim does not by itself set a test to Passed. Passing status requires attributable test evidence.

2. Program Objective Traceability
Objective	Program outcome	Requirements	Primary verification	Release impactOBJ-001	Eliminate Project-context leakage	A411-1, ANGEL-412-11	QA-001, QA-111	Release blocker
OBJ-002	Ensure exact knowledge-pack and document selection	A411-2	QA-002	Release blocker
OBJ-003	Recover safely from deleted selections	A411-3	QA-003	Release blocker
OBJ-004	Give users ownership of stored knowledge	A411-4, A411-5	QA-004, QA-005	Required
OBJ-005	Preserve immutable historical engineering records	A411-5	QA-005	Required
OBJ-006	Provide a unified workspace experience	A411-6, ANGEL-412-1, 10, 70	QA-006, QA-101, QA-103, QA-107	Required
OBJ-007	Preserve conversation-first interaction	ANGEL-412-20, 21, 22, 30, 40	QA-102, QA-108, QA-109, QA-110, QA-115	Required
OBJ-008	Make Context and model/backend usage understandable	ANGEL-412-11, 31, 32, 50, 53, 70	QA-103, QA-111, QA-112, QA-113, QA-117, QA-118	Required
OBJ-009	Restore efficient conversation copying	ANGEL-412-24	QA-119	Release blocker
OBJ-010	Restore reliable single-instance Read Aloud	ANGEL-412-25	QA-120	Release blocker
OBJ-011	Integrate Memory into Context without removing governance	ANGEL-412-28, 29, 71	QA-114, QA-121	Required
OBJ-012	Ensure Context scales within the viewport	ANGEL-412-26, 27, 70	QA-103, QA-122	Required

The first eight objectives come from Angel-Requirements-Traceability-Matrix.md. The final four incorporate the subsequently approved 4.2.1 requirements.

3. ANGEL-411 Workspace Cohesion Matrix
Requirement	Priority	Acceptance criteria	Test cases	Risks	Evidence source	Gate	StatusA411-1 Project Context Isolation	P0	New Chat is global; Project selection does not rewrite conversation ownership; Project conversations preserve scope; RAG Runs use persisted conversation scope	QA-001-01 through 04; QA-111	RISK-001	Conversation, Project, and RAG Run records	4.1.1 P0	Test Ready
A411-2 Exact Knowledge Pack Selection	P0	Selected pack resolves by exact ID; only its documents display; no fixed-pack fallback	QA-002-01 through 03	RISK-007	UI state and Knowledge API results	4.1.1 P0	Test Ready
A411-3 Stale Selection Recovery	P0	Deleted or missing selected objects clear state and return the user to a safe view	QA-003-01 through 03	RISK-008	Browser state and post-refresh UI	4.1.1 P0	Test Ready
A411-4 Remove Document	P1	Document is removed from storage and future retrieval; current index is reconciled	QA-004-01 and 02	RISK-009	Filesystem, Knowledge API, and search results	4.1.1 P1	Test Ready
A411-5 Remove Knowledge Pack	P1	Pack and current retrieval content are removed; conversations, Projects, RAG Runs, and Evidence remain	QA-005-01 through 03	RISK-009, RISK-010	Storage, retrieval, and historical-record checks	4.1.1 P1	Test Ready
A411-6 Workspace Cohesion Validation	P1	Project, Chat, Knowledge, deletion, retrieval, and recovery operate as one coherent experience	QA-006-01 through 03	All ANGEL-411 risks	End-to-end and UAT evidence	4.1.1 P1	Test Ready

The Workspace Cohesion release notes report that project isolation, exact pack selection, stale-selection recovery, document removal, and pack removal were implemented, with historical engineering records preserved. They also report 42 passing tests, syntax validation, and HTTP smoke checks, while leaving manual QA and approvals pending.

4. ANGEL-412 Unified Workspace Matrix
4.1 Workspace and Navigation
Story	Priority	Acceptance criteria	Test cases	Risk	Gate	StatusANGEL-412-1 Sidebar Information Architecture	P1	Home, Chats, Projects, Knowledge, Skills, and Settings use a consistent hierarchy	QA-101-01 through 03	RISK-004	Workspace UX	Test Ready
ANGEL-412-2 Project Grouping	P2	Project conversations group under Projects; global conversations appear under General; groups collapse	QA-105	RISK-004	Sprint 1	Test Ready
ANGEL-412-3 Conversation Search	P2	Search by title; Project affiliation visible; direct conversation navigation	QA-106-01 and 02	RISK-011	Sprint 1	Test Ready
ANGEL-412-10 Project Workspace Overview	P2	Project identity, chat summary, knowledge, files, retrieval scope, and model summary display	QA-107	RISK-001	Sprint 3	Test Ready
ANGEL-412-34 Workspace Identity/Header Refinement	P1	Workspace name, Project context, and current mode are visible without clutter	QA-123	RISK-004	Workspace UX	Planned
ANGEL-412-35 General vs Project Chat Distinction	P1	Users can distinguish General Chat from Project Chat at a glance	QA-111, QA-124	RISK-001	Context gate	Test Ready

The original sprint material promoted Memory to primary navigation, but the later approved 4.2.1 direction removes Memory from that location and exposes it through Context and Settings. The current matrix follows the later decision. The earlier navigation model remains documented in the original epic and sprint plan.

4.2 Conversation Experience
Story	Priority	Acceptance criteria	Test cases	Risk	Gate	StatusANGEL-412-20 Evidence Experience	P2	Evidence collapsed by default; source count visible; expand/collapse supported	QA-102-01 through 03	RISK-002	Sprint 2	Test Ready
ANGEL-412-21 Simplified Message Layout	P2	Answer remains primary; technical detail is secondary; long responses remain readable	QA-108	RISK-002	Sprint 2	Test Ready
ANGEL-412-22 Response Action Refinement	P2	Universal and contextual actions remain distinct, usable, and accessible	QA-109	RISK-002, RISK-004	Sprint 2	Test Ready
ANGEL-412-24 Conversation Range Selection and Copy	P0	Native selection preserved; Shift-click selects ranges; Ctrl/Cmd+C serializes clean transcript; Ctrl/Cmd+A supported	QA-119	RISK-015	4.2.1 P0	Test Ready
ANGEL-412-25 Single-Instance Read Aloud	P0	One global reader; Play/Stop UI; switching messages or conversations cancels previous playback	QA-120	RISK-016	4.2.1 P0	Test Ready
ANGEL-412-30 Evidence Drawer	P2	Drawer shows sources, retrieval scope, evaluation state, and Inspector entry	QA-110	RISK-002	Sprint 2	Test Ready
4.3 Context, Memory, Retrieval, and Skills
Story	Priority	Acceptance criteria	Test cases	Risk	Gate	StatusANGEL-412-11 Project Context Visibility	P1	Active persisted Project and retrieval scope remain visible through refresh	QA-111	RISK-001	Sprint 3	Test Ready
ANGEL-412-26 Context Panel Scrolling	P1	Independent vertical scrolling, sticky header, no normal horizontal overflow	QA-103-02, QA-122-01	RISK-005	Context gate	Test Ready
ANGEL-412-27 Collapsible Context Sections	P1	Sections expand/collapse; behavior works with scrolling and keyboard input	QA-103-03, QA-122-02	RISK-005	Context gate	Test Ready
ANGEL-412-28 Remove Memory from Primary Navigation	P1	Memory is removed from top-level navigation without removing its functionality	QA-101, QA-121-01	RISK-013	Navigation gate	Test Ready
ANGEL-412-29 Memory Management in Context	P1	View and Manage Memory are reachable from Context; Settings retains management access	QA-114-03, QA-121-02	RISK-013	Context gate	Test Ready
ANGEL-412-31 Retrieval Summary	P2	Candidate, selected, source, and scope summaries use understandable language	QA-112	RISK-002	Sprint 3	Test Ready
ANGEL-412-32 Evaluation Visibility	P2	Pending, Complete, Not Evaluated, and failure states remain accurate	QA-113	RISK-012	Sprint 3	Test Ready
ANGEL-412-70 Context Panel	P1	Project, Conversation, Knowledge, Memory, Skills, Tools, Retrieval, and Model display from authoritative state	QA-103	RISK-005	Sprint 3	Test Ready
ANGEL-412-71 Memory Integration	P1	Relevant approved memory appears in Context with privacy filtering	QA-114	RISK-013	Sprint 3	Test Ready
ANGEL-412-72 Skills Visibility	P1	Context displays only currently active skills, not every installed skill	QA-125	RISK-017	Skills gate	Planned
ANGEL-412-30A Skill Library and Management	P1	Installed skills can be viewed, searched, enabled, disabled, configured, and assigned	QA-126	RISK-017	Skills gate	Planned
4.4 Chat, Work, and Model Transparency
Story	Priority	Acceptance criteria	Test cases	Risk	Gate	StatusANGEL-412-40 Chat Mode	P2	Existing conversation, persistence, streaming, and evidence behavior is preserved	QA-115	RISK-014	Sprint 4	Test Ready
ANGEL-412-41 Work Mode	P2	Work status and progress are visible without introducing an orchestration framework	QA-104	RISK-003	Sprint 4	Test Ready
ANGEL-412-42 Work Timeline	P2	Completed, current, pending, and failed steps display accurately	QA-116	RISK-003, RISK-005	Sprint 4	Test Ready
ANGEL-412-50 Model Status Panel	P2	Backend, actual model, connection state, and known context capacity display accurately	QA-117	RISK-006	Sprint 4	Test Ready
ANGEL-412-53 Model Selection UX	P2/Deferred	Selected and actual model remain aligned; unsupported switching is not presented	QA-118	RISK-006	Conditional	Deferred
ANGEL-412-36 Empty Workspace/Quick Actions	P2	Empty state gives useful, scope-safe entry points	QA-127	RISK-004	Post-P1	Planned
ANGEL-412-37 Model/Backend Status Refinement	P2	Runtime attribution remains accurate during connected, unavailable, and fallback states	QA-117, QA-128	RISK-006	Post-P1	Test Ready
ANGEL-412-38 Knowledge-to-Workspace Integration	P2	Users can move from Knowledge to the correct Chat/Project context without duplicated state	QA-006, QA-129	RISK-001, RISK-005	Post-P1	Planned

The consolidated 4.2 build plan limits Work Mode to status, progress, and visibility; it explicitly excludes autonomous workflow engines and permits deferring model-selection controls until runtime support is stable.

5. QA Test-to-Requirement Matrix
QA ID	Test area	Requirements covered	Type	Automation	Required resultQA-001	Project Context Isolation	A411-1, ANGEL-412-11, 35	Functional, integration, regression	Required	100% pass
QA-002	Exact Pack Selection	A411-2	Functional, regression	Required	100% pass
QA-003	Stale Selection Recovery	A411-3	Functional, recovery	Required	100% pass
QA-004	Remove Document	A411-4	Integration, data integrity	Required	100% pass
QA-005	Remove Pack	A411-5	Integration, data integrity	Required	100% pass
QA-006	Workspace Cohesion	A411-6, ANGEL-412-38	End-to-end, UAT	Partial	Approved
QA-101	Sidebar Navigation	ANGEL-412-1, 28	UX, functional, responsive	Partial	Approved
QA-102	Evidence Disclosure	ANGEL-412-20, 30	UX, accessibility	Partial	Approved
QA-103	Context Panel	ANGEL-412-26, 27, 70	Functional, performance, accessibility	Partial	Within budget
QA-104	Work Mode	ANGEL-412-41	Scope, functional	Partial	Approved
QA-105	Project Grouping	ANGEL-412-2	Functional	Required	Pass
QA-106	Conversation Search	ANGEL-412-3	Functional, performance	Required	Pass
QA-107	Project Overview	ANGEL-412-10	Functional, UX	Partial	Approved
QA-108	Message Layout	ANGEL-412-21	Visual, regression	Partial	Approved
QA-109	Response Actions	ANGEL-412-22	Functional, accessibility	Partial	Pass
QA-110	Evidence Drawer	ANGEL-412-30	Functional, accessibility	Partial	Pass
QA-111	Project Context Visibility	ANGEL-412-11, 35	Functional, regression	Required	Pass
QA-112	Retrieval Summary	ANGEL-412-31	Functional, UX	Partial	Approved
QA-113	Evaluation Visibility	ANGEL-412-32	State coverage	Required	Pass
QA-114	Memory Integration	ANGEL-412-29, 71	Integration, privacy	Required	Pass
QA-115	Chat Mode	ANGEL-412-40	Regression, UAT	Required	Approved
QA-116	Work Timeline	ANGEL-412-42	Functional	Required	Pass
QA-117	Model Status	ANGEL-412-50, 37	Integration	Required	Pass
QA-118	Model Selection	ANGEL-412-53	Functional, failover	Conditional	Approved if shipped
QA-119	Range Selection and Copy	ANGEL-412-24	Functional, accessibility, performance	Required	100% pass
QA-120	Single-Instance Read Aloud	ANGEL-412-25	Functional, state, error recovery	Required	100% pass
QA-121	Memory Navigation Relocation	ANGEL-412-28, 29	Functional, UX	Required	Pass
QA-122	Context Scrolling and Collapse	ANGEL-412-26, 27	Functional, responsive, accessibility	Required	Pass
QA-123	Workspace Header	ANGEL-412-34	Visual, functional	Partial	Approved
QA-124	General versus Project Chat	ANGEL-412-35	Functional, UX	Required	Pass
QA-125	Active Skills Visibility	ANGEL-412-72	Functional, transparency	Required	Pass
QA-126	Skill Library Management	ANGEL-412-30A	Functional, permission, UX	Required	Pass
QA-127	Empty Workspace	ANGEL-412-36	UX, functional	Partial	Approved
QA-128	Runtime Attribution	ANGEL-412-37	Integration, failure-state	Required	Pass
QA-129	Knowledge/Workspace Flow	ANGEL-412-38	End-to-end	Required	Pass

The original QA catalog contains QA-001 through QA-104 in abbreviated form, while the original traceability matrix extends the catalog through QA-118.

6. Risk-to-Control Matrix
Risk	Severity	Affected requirements	Preventive control	Detective test	Contingency	Release impactRISK-001 Project Context Leakage	Critical	A411-1; 412-10, 11, 35, 38	Persisted conversation scope remains authoritative	QA-001, QA-111, QA-124	Revert selected Project to navigation-only state	Blocks release
RISK-002 Evidence Becomes Developer UI	High	412-20, 21, 22, 30, 31	Progressive disclosure	QA-102, 108, 109, 110, 112	Compact “Evidence · N sources” control	Feature-level block
RISK-003 Work Mode Scope Expansion	High	412-41, 42	Freeze scope to status and progress	QA-104, QA-116	Defer Work Mode or ship read-only timeline	Non-blocking
RISK-004 Sidebar Complexity	Medium	412-1, 2, 34, 36	Navigation-only hierarchy	QA-101, 105, 123, 127	Simplified navigation	Non-blocking
RISK-005 Context Performance	Medium	412-26, 27, 42, 70, 71	Lazy detail and cached summaries	QA-103, QA-122	Summary-only Context panel	Non-blocking
RISK-006 Model Confusion	Medium	412-37, 50, 53	Status before selection	QA-117, 118, 128	Read-only actual-model indicator	Non-blocking
RISK-007 Wrong Pack Rendered	High	A411-2	Exact-ID resolution	QA-002	Disable detail view until exact pack loads	Blocks P0
RISK-008 Deleted Object Remains Selected	High	A411-3	Selection invalidation	QA-003	Clear identifiers and return to list	Blocks P0
RISK-009 Incomplete Knowledge Deletion	High	A411-4, A411-5	Rebuild and reconcile active index	QA-004, QA-005	Restore and rebuild	Blocks P1
RISK-010 Historical Records Deleted	High	A411-5	Explicit preservation boundary	QA-005	Restore from backup	Blocks P1
RISK-011 Search Degrades at Scale	Medium	412-3	Bounded or indexed lookup	QA-106	Limit initial results	Non-blocking if scoped
RISK-012 Evaluation Misrepresented	High	412-32	Explicit state enum	QA-113	Display Not Evaluated	Blocks feature
RISK-013 Memory Privacy/Navigation	High	412-28, 29, 71	Approved-memory and scope filtering	QA-114, QA-121	Hide Context details, retain management	Blocks feature
RISK-014 Chat Regression	Critical	412-40	Preserve current Chat behavior	QA-115	Disable mode split	Blocks release
RISK-015 Copy Corrupts or Captures UI	High	412-24	Dedicated transcript serializer	QA-119	Retain native text copying	Blocks 4.2.1
RISK-016 Duplicate Audio/Stale Reader	High	412-25	Single global reader state	QA-120	Disable Read Aloud until stable	Blocks 4.2.1
RISK-017 Skills Misrepresent Capability	Medium	412-72, 30A	Separate installed, enabled, assigned, and active states	QA-125, QA-126	Context shows only verified active skills	Blocks Skills feature

The original risk register establishes RISK-001 through RISK-014 and the principle that scope should be reduced before correctness.

7. Release-Gate Matrix
Gate A: 4.1.1 State Correctness

Required:

QA-001 passed
QA-002 passed
QA-003 passed
No Project-context leakage
No stale Pack selection
No stale Document selection
Engineering Lead approval
Gate B: 4.1.1 Knowledge Ownership

Required:

QA-004 passed
QA-005 passed
QA-006 approved
Deleted content absent from current retrieval
Historical records preserved
Product Owner approval
Gate C: 4.2.1 Functional Regression

Required:

QA-119 passed
QA-120 passed
Native browser selection preserved
Only one audio reader active globally
Conversation changes cancel playback
Large copy selections remain usable
Gate D: Context and Memory

Required:

QA-103 passed
QA-114 passed
QA-121 passed
QA-122 passed
Memory removed from primary navigation
Memory management remains reachable
Context header, scrolling, and collapse behavior approved
Gate E: Unified Workspace

Required:

All implemented P1 stories accepted
QA-101 through QA-118 pass where applicable
Zero open critical defects
Zero open high-severity defects
Conversation-first UX approved
Model/backend attribution verified
No duplicate source of truth introduced

The original release model requires all sprint gates, zero open critical and high-severity defects, no unresolved Project-context regressions, Context-panel approval, verified model attribution, and QA, Engineering, and Product approvals before the 4.2 release candidate.

8. Coverage Summary
Coverage area	Items	Test coverage	Current verification stateANGEL-411 requirements	6	6 mapped	Test Ready
Original ANGEL-412 stories	18	18 mapped	Test Ready or Deferred
Additional 4.2.1 stories	12	12 mapped	Test Ready or Planned
QA cases	29	29 mapped	Execution evidence pending
Risks	17	17 controlled	Verification pending
Release gates	5 consolidated gates	5 mapped	Approval pending
Traceability completeness rule

A requirement is complete only when it can be followed in both directions:

Objective
  → Requirement
  → Acceptance criteria
  → Test case
  → Test evidence
  → Risk control
  → Release gate


and:

Test failure
  → Defect
  → Requirement
  → Objective
  → Risk
  → Release impact

Matrix note

This matrix separates planned traceability from verified delivery. The available release notes report implementation and automated validation for the Workspace Cohesion release, but they also explicitly leave manual QA and formal approvals pending.