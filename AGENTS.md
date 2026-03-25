# Repository Guidelines

## Project Structure & Module Organization
This repository is a Markdown tutorial set, not an application codebase. Top-level chapters (`01-quick-start.md` through `04-deploy.md`) form Part 1 and explain how to use nanobot. The [`build/`](./build) directory contains Part 2, a step-by-step reconstruction of nanobot internals, with one chapter per topic plus [`build/README.md`](./build/README.md). [`README.md`](./README.md) is the entry point and should stay aligned with chapter titles and ordering.

## Build, Test, and Development Commands
This repository includes an optional MkDocs setup for local reading and verification. Use lightweight local checks instead:

- `rg --files -g '*.md'` lists all documentation files.
- `python3 -m venv .venv && . .venv/bin/activate && python -m pip install -r requirements-docs.txt` prepares the local docs site environment.
- `python -m mkdocs serve` starts a local documentation server at `http://127.0.0.1:8000`.
- `python -m mkdocs build --strict` verifies that the documentation site builds cleanly.
- Pushing to `main` triggers `.github/workflows/pages.yml`, which builds the MkDocs site and deploys it to GitHub Pages.
- `markdownlint-cli2 "**/*.md"` is a useful optional lint pass if you have it installed; no formatter is enforced in-repo.

## Coding Style & Naming Conventions
Write in clear instructional prose and preserve the repository’s teaching-oriented tone. Keep filenames ordered with numeric prefixes and lowercase kebab-case slugs, for example `05-new-topic.md`. Use ATX headings (`#`, `##`), fenced code blocks with language tags, and inline code for commands, paths, and module names such as `nanobot/agent/context.py`. When updating existing chapters, keep examples incremental and explicit rather than overly compressed.

## Testing Guidelines
There is no automated test suite. Verify changes by checking Markdown rendering, confirming internal links and relative paths still resolve, and rerunning any shell snippets you modify when practical. When changing navigation or docs-site behavior, run `python -m mkdocs build --strict` from the project venv. For tutorial edits, ensure chapter references in [`README.md`](./README.md) and [`build/README.md`](./build/README.md) remain correct.

## Commit & Pull Request Guidelines
The current history uses short imperative subjects (`Initial commit`, `Add files via upload`). Continue with concise, action-first commit messages, but prefer specific summaries such as `Add deployment troubleshooting notes`. Pull requests should state which chapter(s) changed, why the edit was needed, and whether any commands, paths, or screenshots in the docs were updated. Link related issues when available.

## Content Scope
This repo teaches nanobot concepts through simplified examples. Keep that contract clear: document when code is pedagogical rather than production-exact, and avoid introducing repo-level tooling instructions that are not actually used here.
