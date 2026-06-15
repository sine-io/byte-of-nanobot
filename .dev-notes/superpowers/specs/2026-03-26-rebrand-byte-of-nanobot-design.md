# byte-of-nanobot Rebrand Design

## Goal

Rename the tutorial from the old `nanobot-playbook` naming to:

- English display name: `byte-of-nanobot`
- Chinese display name: `简明 NanoBot 教程`

## Scope

This rebrand covers:

- top-level tutorial title text
- MkDocs site metadata
- repository and pages URLs stored in repo files
- remaining textual references to the old name

This rebrand does not directly rename the GitHub repository or change GitHub Pages settings on the remote service. It only updates the repository contents to the new naming.

## Approaches Considered

### Option A: Full in-repo rebrand now

Update display names and stored URLs in the docs and MkDocs config.

Pros:

- brand is consistent inside the repository
- avoids mixed old/new naming in the published docs

Cons:

- if the remote repo or Pages path is not yet renamed, the new URLs may temporarily point to future locations

### Option B: Display-name-only rebrand

Change titles but keep old URLs.

Pros:

- least risky for current links

Cons:

- visibly inconsistent branding
- leaves old project identity in config

## Decision

Use Option A.

The user explicitly requested that both the display names and URLs be updated.

## Files

- Modify `README.md`
- Modify `mkdocs.yml`

## Verification

- Search the repo for old `nanobot-playbook` and old display-name references.
- Run `python3 -m mkdocs build --strict`.
