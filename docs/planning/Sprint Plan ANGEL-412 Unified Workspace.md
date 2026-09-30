Sprint Plan: ANGEL-412 Unified Workspace
Sprint-Ready Stories

The epic is too large for a single sprint. The natural breakdown is 4 sequential sprints, each delivering user-visible value while building toward the Unified Workspace vision.

Sprint 1
Workspace Foundation

Goal: Establish project-aware navigation and conversation organization.

ANGEL-412-1 Sidebar Information Architecture

Story

As an Angel user, I want the sidebar organized around workspaces so I can understand where everything belongs.

Acceptance Criteria

Home added
Chats added
Projects promoted to first-class navigation item
Knowledge promoted to first-class navigation item
Memory promoted to first-class navigation item
Settings remains accessible
Existing functionality preserved

Estimate: 5 points

ANGEL-412-2 Project Grouping in Sidebar

Story

As a user, I want conversations grouped by project so I can find related work easily.

Acceptance Criteria

Conversations grouped by project
Ungrouped conversations appear in General
Project headers collapsible
Existing conversation navigation preserved

Estimate: 8 points

ANGEL-412-3 Conversation Search

Story

As a user, I want to search conversations across projects.

Acceptance Criteria

Search box added
Search by title supported
Search results link directly to conversations
Project affiliation visible

Estimate: 5 points

ANGEL-412-10 Project Workspace Overview

Story

As a user, I want a meaningful project landing page.

Acceptance Criteria

Project overview page implemented
Displays chat count
Displays knowledge count
Displays file count
Shows active retrieval scope
Shows model information

Estimate: 8 points

Sprint 1 Exit Criteria
Sidebar hierarchy completed
Projects feel like workspaces
Conversation discovery improved
Sprint 2
Conversation Experience

Goal: Make Angel conversations cleaner and less technical.

ANGEL-412-20 Collapsible Evidence

Story

As a user, I want evidence available when needed without cluttering my conversation.

Acceptance Criteria

Evidence hidden by default
Expand/collapse functionality
Source count visible
Existing evidence preserved

Estimate: 8 points

ANGEL-412-21 Simplified Message Layout

Story

As a user, I want responses focused on the answer rather than engineering details.

Acceptance Criteria

Answer becomes primary visual element
Engineering details de-emphasized
Visual hierarchy improved

Estimate: 5 points

ANGEL-412-22 Response Action Refinement

Story

As a user, I want contextual actions that feel helpful instead of technical.

Acceptance Criteria

Pills visually simplified
Maximum three visible
Consistent spacing
Actions remain functional

Estimate: 3 points

ANGEL-412-30 Evidence Drawer

Story

As a user, I want to inspect retrieval evidence on demand.

Acceptance Criteria

Drawer component implemented
Displays retrieved sources
Displays retrieval scope
Displays evaluation status

Estimate: 8 points

Sprint 2 Exit Criteria
Chat feels cleaner
Evidence remains accessible
Engineering details become progressive disclosure
Sprint 3
Context-Aware Workspace

Goal: Connect projects, retrieval, and conversations.

ANGEL-412-11 Project Context Visibility

Story

As a user, I want to see what project context Angel is currently using.

Acceptance Criteria

Active project visible
Retrieval scope visible
Context survives refresh
Context updates correctly

Estimate: 5 points

ANGEL-412-31 Retrieval Summary

Story

As a user, I want to understand what Angel retrieved without opening debugging tools.

Acceptance Criteria

Retrieval count displayed
Knowledge sources summarized
Retrieval scope displayed

Estimate: 5 points

ANGEL-412-32 Evaluation Visibility

Story

As a user, I want evaluation status visible when available.

Acceptance Criteria

Pending shown
Complete shown
Not Evaluated shown
Consistent formatting

Estimate: 3 points

ANGEL-412-70 Context Panel

Story

As a user, I want to understand Angel's active context.

Acceptance Criteria

Displays:

Project
Conversation
Knowledge
Memory
Skills
Tools

Estimate: 8 points

ANGEL-412-71 Memory Integration

Story

As a user, I want memory visible as part of context rather than a separate page.

Acceptance Criteria

Memory references appear in Context panel
Existing memory system preserved

Estimate: 5 points

Sprint 3 Exit Criteria
Projects influence conversations visibly
Retrieval scope understandable
Context becomes transparent
Sprint 4
Chat + Work Experience

Goal: Introduce the unified assistant workspace model.

ANGEL-412-40 Chat Mode

Story

As a user, I want a dedicated conversation mode.

Acceptance Criteria

Chat mode implemented
Existing conversation behavior retained

Estimate: 5 points

ANGEL-412-41 Work Mode

Story

As a user, I want Angel to show task execution progress separately from chat.

Acceptance Criteria

Work mode implemented
Work status visible
Long-running operations supported

Estimate: 8 points

ANGEL-412-42 Work Timeline

Story

As a user, I want to see task progress as Angel works.

Acceptance Criteria

Timeline component implemented
Status updates supported

Estimate: 8 points

ANGEL-412-50 Model Status Panel

Story

As a user, I want to know which model is answering me.

Acceptance Criteria

Shows:

Backend
Model
Connection status
Context capacity

Estimate: 5 points

ANGEL-412-53 Model Selection UX

Story

As a user, I want to choose between local, cloud, and auto modes.

Acceptance Criteria

Local mode
Cloud mode
Auto mode

Estimate: 8 points

Sprint 4 Exit Criteria
Chat mode complete
Work mode complete
Backend/model visibility complete
Angel feels like a workspace assistant
Deferred to 4.2.x

These should remain outside the initial Unified Workspace rollout:

Infrastructure
Event Bus Runtime
Payload Validation
Advanced Contextual Pill Telemetry
Advanced RAG Features
Measurements UI
Recommendation UI
Snapshot UI
Advanced Agent Features
Multi-step autonomous workflows
Cross-project orchestration
Background task scheduling
Release Roadmap
4.1.1 Release Candidate
          ↓
4.1.1 Final Release
          ↓

Sprint 1
Workspace Foundation
          ↓

Sprint 2
Conversation Experience
          ↓

Sprint 3
Context-Aware Workspace
          ↓

Sprint 4
Chat + Work Experience
          ↓

Angel 4.2 Unified Workspace

Definition of Success

At the end of ANGEL-412:

Projects
Knowledge
Memory
Files
Tools
Chat


should no longer feel like separate pages.

They should feel like:

One Workspace
One Context
One Assistant


with the RAG lifecycle available when needed, but never dominating the user experience.