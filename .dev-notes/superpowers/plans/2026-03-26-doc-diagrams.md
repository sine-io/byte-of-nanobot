# Tutorial Diagrams Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add three Mermaid diagrams that clarify the tutorial's core abstractions without changing the current lesson flow.

**Architecture:** Keep diagrams inline in the existing Markdown chapters so the visual explanation lives next to the prose it supports. Limit each change to one focused diagram plus a short follow-up explanation.

**Tech Stack:** Markdown documentation, Mermaid code blocks, MkDocs Material

---

### Task 1: Add the System Prompt composition diagram

**Files:**
- Modify: `02-soul.md`

- [x] Insert a Mermaid flow diagram in the "System Prompt 是怎么组装的？" section.
- [x] Show fixed identity, bootstrap files, memory, skills, and the final assembled prompt.
- [x] Add a short explanation that distinguishes the four Markdown files from the full prompt assembly.

### Task 2: Add the Skill loading diagram

**Files:**
- Modify: `03-skills.md`

- [x] Insert a Mermaid flow diagram in the "Skill 的触发机制" section.
- [x] Show the three loading layers and the on-demand transition from summary to full Skill content.
- [x] Add a short explanation that reinforces context-window efficiency.

### Task 3: Add the MessageBus message path diagram

**Files:**
- Modify: `04-deploy.md`

- [x] Insert a Mermaid flow diagram in the "整体架构" subsection.
- [x] Show the minimal message flow from channel to bus to agent and back.
- [x] Add a short explanation that clarifies the platform/agent boundary.

### Task 4: Verify the docs build

**Files:**
- Verify: `02-soul.md`
- Verify: `03-skills.md`
- Verify: `04-deploy.md`

- [x] Re-read the changed sections for clarity and duplication.
- [x] Run `python3 -m mkdocs build --strict`.
