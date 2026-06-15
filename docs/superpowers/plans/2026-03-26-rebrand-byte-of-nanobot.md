# byte-of-nanobot Rebrand Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rename the tutorial branding and stored documentation URLs from `nanobot-playbook` to `byte-of-nanobot`.

**Architecture:** Keep the repository structure unchanged and only update user-facing names and config values that affect the docs site metadata and public links. Avoid unrelated doc rewrites.

**Tech Stack:** Markdown documentation, MkDocs Material, repository text search

---

### Task 1: Update the visible tutorial title

**Files:**
- Modify: `README.md`

- [x] Change the Chinese tutorial title to `简明 NanoBot 教程`.
- [x] Preserve the rest of the landing-page structure.

### Task 2: Update site metadata and public URLs

**Files:**
- Modify: `mkdocs.yml`
- Modify: `README.md`

- [x] Change the site name to `byte-of-nanobot`.
- [x] Change the site description to `简明 NanoBot 教程`.
- [x] Update the stored `site_url` and `repo_url` values to the new `byte-of-nanobot` paths.

### Task 3: Remove old-name leftovers

**Files:**
- Verify: repository text matches

- [x] Search for remaining `nanobot-playbook`, `Nanobot Playbook`, and old title references.
- [x] Update any remaining occurrences that belong to the tutorial brand.

### Task 4: Verify docs build

**Files:**
- Verify: `README.md`
- Verify: `mkdocs.yml`

- [x] Run `python3 -m mkdocs build --strict`.
