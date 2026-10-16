# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

A library of Claude Code **skills** (Markdown only — no build, no tests) that is also a **Claude Code plugin marketplace**. Each skill is `skills/<name>/SKILL.md`: YAML frontmatter (`name`, `description`) plus instructions. The skill's invocation name comes from the **directory name**; the `description` is what triggers auto-activation, so it must enumerate the situations the skill applies to.

## Validation

```bash
claude plugin validate .    # validates .claude-plugin/marketplace.json (and the plugin it references)
```

## How the pieces fit

- `.claude-plugin/marketplace.json` defines marketplace `furkanedizkan-skills`, listing a single plugin `skills` with `source: "./"` — the whole repo is one plugin bundling every folder under `skills/`.
- `.claude-plugin/plugin.json` is that plugin's manifest.
- **`version`, `description`, and `keywords` are duplicated** between `plugin.json` and the plugin entry in `marketplace.json`. Keep them in sync; bump `version` in both whenever a skill is added or changed so installs pick up the update.
- Installed via the marketplace, skills are invoked as `/skills:<name>`; copied as a single folder, as `/<name>`. Every skill folder must therefore stay self-contained (no cross-folder file references).

## Rules for skill content

- Skills must stay **generalized / project-agnostic**: describe the general practice and explicitly defer to the consuming repo's own conventions (`CONTRIBUTING.md`, lint/commitlint config, existing style) when present. Repo-specific detail belongs in the consuming project, not here.
- Skills cross-reference each other conceptually (e.g. `create-github-issue` uses `three-tier-git-flow`'s `dev`/`test` integration branch, plus conventional branch/commit naming) — when changing one workflow skill, check the related ones for consistency.

## Adding or changing a skill

1. Create/edit `skills/<skill-name>/SKILL.md`.
2. Add/update its row in the **Available skills** table in `README.md`.
3. Bump `version` in both `.claude-plugin/plugin.json` and `marketplace.json`; update the shared `description`/`keywords` if the skill set changed.
4. Commit using Conventional Commits, one skill per commit — e.g. `feat: add <skill-name> skill`, `docs: ...` for content tweaks, `refactor: ...` for restructuring.
