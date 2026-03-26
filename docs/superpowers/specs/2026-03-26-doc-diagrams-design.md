# Tutorial Diagram Design

## Goal

Add three lightweight teaching diagrams to the tutorial so readers can grasp the main abstractions faster without changing the current chapter structure.

## Scope

This design only covers:

- a `System Prompt` composition diagram in `02-soul.md`
- a three-layer Skill loading diagram in `03-skills.md`
- a message path diagram in `04-deploy.md`

This design does not cover:

- new screenshots
- image assets
- chapter reordering
- large rewrites of the surrounding prose

## Approaches Considered

### Option A: Mermaid diagrams in Markdown

Keep diagrams inline with the chapters as Mermaid blocks.

Pros:

- easiest to maintain alongside the text
- no separate asset pipeline
- good fit for MkDocs and repo-local editing

Cons:

- less visually polished than custom images

### Option B: ASCII diagrams

Keep everything plain text.

Pros:

- zero tooling dependency
- guaranteed readable in raw Markdown

Cons:

- harder to scan
- weaker visual hierarchy
- duplicates patterns already explained in prose

### Option C: Static image assets

Create exported diagrams and embed them as images.

Pros:

- strongest visual polish

Cons:

- highest maintenance cost
- introduces extra asset management
- easiest to let drift from the text

## Decision

Use Option A: Mermaid diagrams in Markdown.

This keeps the diagrams close to the paragraphs they explain, matches the repo's documentation-first workflow, and minimizes maintenance overhead.

## Diagram Design

### 1. `02-soul.md`

Place the diagram inside the "System Prompt 是怎么组装的？" section.

It should show:

- fixed identity
- bootstrap files: `AGENTS.md`, `SOUL.md`, `USER.md`, `TOOLS.md`
- memory
- skills summary / loaded skill content
- final combined system prompt

The explanation after the diagram should stay short and emphasize that the four Markdown files are only one layer inside the assembled prompt.

### 2. `03-skills.md`

Place the diagram inside the "Skill 的触发机制" section after the three-layer explanation.

It should show:

- layer 1: all Skill summaries always injected
- layer 2: matched `SKILL.md` loaded on demand
- layer 3: `scripts/` and `references/` loaded only when needed
- user question triggering the path

The explanation after the diagram should stress why this design saves context window space.

### 3. `04-deploy.md`

Place the diagram inside the "整体架构" subsection of the MessageBus explanation.

It should show the shortest happy path:

- channel receives message
- channel converts to `InboundMessage`
- `MessageBus`
- `AgentLoop`
- `OutboundMessage`
- message routed back to the original channel

The explanation after the diagram should reinforce that platform-specific logic stays in channels, while agent logic stays centralized.

## Constraints

- Keep each diagram single-purpose and easy to read in raw Markdown.
- Do not add more than a few sentences of new prose per diagram.
- Preserve existing file paths and section ordering.

## Verification

- Re-read the changed sections for conceptual consistency.
- Run `python3 -m mkdocs build --strict`.
