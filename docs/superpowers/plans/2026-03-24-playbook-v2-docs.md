# Playbook V2 Docs Refactor Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Clarify the tutorial's audience split and add the missing bridge chapters so V2 better serves both nanobot users and programmers.

**Architecture:** Keep the existing `新手村 / 进阶营` structure and stable file paths, then tighten copy where promises are too broad and add one capstone chapter to each track. This avoids churn while making the learning paths explicit and closing the biggest teaching gaps.

**Tech Stack:** Markdown documentation, relative links, repository navigation references

---

### Task 1: Rewrite the top-level landing page

**Files:**
- Modify: `README.md`

- [x] Replace the opening positioning with a more accurate audience statement.
- [x] Add explicit reading paths for "use nanobot", "understand the architecture", and "build your own bot".
- [x] Expand both chapter tables to include the new capstone chapters.
- [x] Add a clear "scope and boundaries" section so the repo does not over-promise production readiness.

### Task 2: Tighten 新手村 chapter framing

**Files:**
- Modify: `02-soul.md`
- Modify: `03-skills.md`
- Modify: `04-deploy.md`
- Modify: `01-quick-start.md`

- [x] Rename chapter 2 in-place to emphasize Markdown-driven bot customization.
- [x] Retitle chapter 4 to a Telegram-first deployment story that matches the actual walkthrough.
- [x] Update previous/next navigation labels so chapter names stay consistent across 新手村.
- [x] Preserve existing file paths to avoid unnecessary link churn.

### Task 3: Add the 新手村 capstone

**Files:**
- Create: `05-first-real-bot.md`
- Modify: `04-deploy.md`

- [x] Write a capstone chapter that combines workspace files, one Skill, and Telegram deployment into a complete bot.
- [x] Include a concrete scenario, a full sample workspace setup, a validation checklist, and a short architecture recap.
- [x] Link chapter 4 forward to the new capstone and give the capstone clear return links.

### Task 4: Add the 进阶营 bridge to real projects

**Files:**
- Create: `build/06-from-mini-agent-to-real-bot.md`
- Modify: `build/README.md`
- Modify: `build/05-skills-and-beyond.md`

- [x] Add a chapter that explains the gap between the teaching implementation and a maintainable real-world bot.
- [x] Cover structure, configuration, security, retries, concurrency, observability, and testing at a practical level.
- [x] Update the build track index and next/previous links to include the new final chapter.

### Task 5: Verify documentation integrity

**Files:**
- Verify: `README.md`
- Verify: `01-quick-start.md`
- Verify: `02-soul.md`
- Verify: `03-skills.md`
- Verify: `04-deploy.md`
- Verify: `05-first-real-bot.md`
- Verify: `build/README.md`
- Verify: `build/05-skills-and-beyond.md`
- Verify: `build/06-from-mini-agent-to-real-bot.md`

- [x] Check that all new and updated relative links resolve.
- [x] Re-read the changed chapters for claim consistency, especially audience promises and deployment scope.
- [x] Review the final diff to confirm the refactor stays documentation-only and keeps the repository coherent.
