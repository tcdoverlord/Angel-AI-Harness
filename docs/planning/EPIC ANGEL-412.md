EPIC: ANGEL-412
Angel Nexus 4.2 — Unified Workspace

Epic Type: Product Experience & Workspace Integration
 Priority: High
 Depends On: Angel 4.1.1 Workspace Cohesion Release Candidate Approval
 Epic Owner: Product Owner
 Technical Owner: Engineering Lead

Executive Summary

Angel 4.1.1 focused on:

State correctness
Knowledge ownership
Workspace cohesion
Reliable data lifecycle behavior

Angel 4.2 shifts focus from correctness to experience integration.

The objective is not to add major new subsystems.

The objective is to make:

Chat
Projects
Knowledge
Memory
Files
Tools


feel like a single intelligent workspace.

Vision

Current experience:

Chat
+
Projects
+
Knowledge
+
Memory


Target experience:

                   ANGEL
                     │
          ┌──────────┴──────────┐
          │                     │
        CHAT                  WORK
          │                     │
          └──────────┬──────────┘
                     │
                  PROJECT
                     │
     ┌───────────────┼───────────────┐
     │               │               │
 KNOWLEDGE         FILES          MEMORY
     │               │               │
     └───────────────┼───────────────┘
                     │
              RETRIEVAL SCOPE
                     │
                  RAG RUN
                     │
                EVALUATION
                     │
                  EVIDENCE


The architecture already exists.

The goal is making it understandable.

Initiative A
Unified Navigation
Objective

Transform the sidebar into the primary organizational layer for Angel.

Current
Recent
Knowledge
Projects
Memory
Settings

Target
🏠 Home
💬 Chats
📁 Projects
🧠 Knowledge
🗂 Memory
🛠 Skills
⚙ Settings

Success Criteria
Consistent navigation hierarchy
Projects visible as first-class workspaces
Knowledge visible as part of Angel
Skills and tools discoverable
Stories
ANGEL-412-1 Sidebar Information Architecture
ANGEL-412-2 Project Grouping
ANGEL-412-3 Conversation Search
ANGEL-412-4 Navigation Consistency Pass
Initiative B
Project-Aware Workspaces
Objective

Projects become operational workspaces instead of containers.

Current
Project
    ↓
Open Project

Target
Project
    ↓
Workspace
    ↓
Chat
Knowledge
Files
Context

Workspace Layout
Angel Nexus

Chats      Knowledge      Files

12            184          37

Active Context
Angel Nexus

Retrieval Scope
Project Knowledge

Model
Qwen

Success Criteria
Project context visible
Retrieval scope visible
Project chat workflow simplified
Workspace feels persistent
Stories
ANGEL-412-10 Workspace Overview
ANGEL-412-11 Project Context Visibility
ANGEL-412-12 Workspace Metrics
ANGEL-412-13 Project Entry Experience
Initiative C
Chat Experience Modernization
Objective

Make Angel conversations feel cleaner and more assistant-like.

Current Problem

Engineering details are too prominent.

Target
Answer

▸ Evidence · 6 Sources


instead of:

EVIDENCE
Retrieval
Evaluation
Context


under every response.

Success Criteria
Cleaner responses
Less visual noise
Transparency preserved
Progressive disclosure
Stories
ANGEL-412-20 Collapsible Evidence
ANGEL-412-21 Simplified Message Layout
ANGEL-412-22 Response Action Refinement
ANGEL-412-23 Chat Visual Cleanup
Initiative D
Evidence & Retrieval Experience
Objective

Expose the RAG lifecycle without exposing engineering complexity.

Target
▸ Evidence · 6 Sources


Expanded:

Evidence

✓ architecture.md
✓ project-rag.md
✓ memory.md

Retrieval Scope
Angel Nexus

Evaluation
Pending

[ Inspect Retrieval ]

Success Criteria
Evidence available on demand
Retrieval visible
Evaluation visible
Chat remains uncluttered
Stories
ANGEL-412-30 Evidence Drawer
ANGEL-412-31 Retrieval Summary
ANGEL-412-32 Evaluation Visibility
ANGEL-412-33 Retrieval Inspection Entry
Initiative E
Chat / Work Mode Separation
Objective

Separate conversation from task execution.

Modes
Chat
Conversation
Question Answering
Brainstorming

Work
Repository Analysis
Knowledge Processing
Tool Execution
Project Tasks

Example
Working on Angel Nexus

✓ Retrieved Architecture
✓ Loaded Repository
● Analyzing OpenAPI

[ View Details ]

Success Criteria
Users understand what Angel is doing
Long-running work becomes visible
Future agent workflows have a home
Stories
ANGEL-412-40 Chat Mode
ANGEL-412-41 Work Mode
ANGEL-412-42 Work Timeline
ANGEL-412-43 Work Progress View
Initiative F
Model & Backend Transparency
Objective

Eliminate uncertainty around model selection and backend usage.

Target
LOCALAI

● Connected

Model
Qwen 27B

Context
8192

Success Criteria
Current model visible
Backend visible
Connection status visible
User understands who answered
Stories
ANGEL-412-50 Model Status Panel
ANGEL-412-51 Backend Status
ANGEL-412-52 Connection Health
ANGEL-412-53 Model Selection UX
Initiative G
Workspace Home Experience
Objective

Replace empty-chat screens with useful workspace entry points.

Target
What are we working on?

[ Ask Angel ]

[ Analyze Project ]
[ Search Knowledge ]

Recent Work
-------------
Angel Architecture
LocalAI Integration
RAG Contract

Success Criteria
Less empty space
Better workspace orientation
Faster task initiation
Stories
ANGEL-412-60 Home Experience
ANGEL-412-61 Quick Actions
ANGEL-412-62 Recent Work
ANGEL-412-63 Workspace Landing Page
Initiative H
Context Assembly
Objective

Make Angel's active context visible.

Target
Angel Context

Project
Angel Nexus

Conversation
Architecture Review

Knowledge
43 Documents

Memory
Architecture Decisions

Skills
Git, Docker, OpenAPI

Success Criteria
Context becomes understandable
Memory feels integrated
Tool usage becomes visible
Stories
ANGEL-412-70 Context Panel
ANGEL-412-71 Memory Integration
ANGEL-412-72 Skills Visibility
ANGEL-412-73 Active Knowledge Display
Deferred Dependencies

These remain dependent on successful workspace integration:

Contextual Continuity
        ↓
Event Bus Runtime
        ↓
Payload Validation
        ↓
Advanced Contextual Pills


No implementation should begin until 4.1.1 receives final approval.

Release Gate
Experience Validation
 Sidebar supports workspace model
 Projects feel like workspaces
 Knowledge feels integrated
 Evidence is discoverable but unobtrusive
 Chat feels conversation-first
 Work mode is understandable
 Context is visible
 Model/backend status is clear
Product Validation
 Chat
 Projects
 Knowledge
 Memory
 Files
 Skills

all feel like parts of one application.

Definition of Done

Angel 4.2 Unified Workspace is complete when:

Projects
Knowledge
Memory
Tools
Files
Chat


are experienced by users as:

One Assistant
One Workspace
One Context


rather than a collection of screens connected by a sidebar.

Release Theme:

Connect the pieces before adding new pieces.
 Turn Angel from a collection of features into a unified workspace.