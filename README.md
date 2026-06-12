# My-Skills

A small library of [Claude Code](https://docs.claude.com/en/docs/claude-code)
**skills** — reusable, **generalized** capabilities that can be pulled into any
of our codebases.

Each skill is a self-contained directory containing a `SKILL.md` (YAML
frontmatter + instructions). Skills here are written to be **project-agnostic**:
they describe a general practice and defer to a repository's own conventions
(`CONTRIBUTING.md`, lint config, existing style) when those exist. Keep them that
way — put repo-specific detail in the consuming project, not here.

The repo doubles as a **Claude Code plugin marketplace**, so the whole library
installs with one command (see [Install](#install)).

## Available skills

| Skill | What it does | Use it when |
| ----- | ------------ | ----------- |
| [modular-services](skills/modular-services/SKILL.md) | Structure code as small, single-responsibility units — each with one typed input, one typed output, and exactly one public entrypoint — so failures localize and the data flow reads as a graph. Language-agnostic. | Writing a new feature, adding a module/function of any real size, or refactoring tangled code; or when asked for "microservice-style", modular, or contract-first code. |
| [conventional-commits](skills/conventional-commits/SKILL.md) | Write commit messages that follow the [Conventional Commits 1.0.0](https://www.conventionalcommits.org/) spec, in any repository. | About to commit, choosing a type/scope, or fixing a commit message a commit-lint check rejected. |
| [conventional-branches](skills/conventional-branches/SKILL.md) | Name git branches per the [Conventional Branch](https://conventionalbranch.org/) spec — `<type>/<short-description>`, lowercase, hyphen-separated, optionally issue-numbered. | Creating a branch, cutting a branch for an issue, or renaming a branch that doesn't match the convention. |
| [create-github-issue](skills/create-github-issue/SKILL.md) | Turn a plan into tracked GitHub work — one issue per task (templated, labelled, assigned), a branch cut from the integration branch, a running comment log, pre-PR checks, and a PR back into the integration branch. | Creating issues for a set of tasks, tracking a plan as issues, or running the plan→issue→branch→PR workflow with a detailed work log. |
| [three-tier-git-flow](skills/three-tier-git-flow/SKILL.md) | Set up a three-trunk, promote-upward workflow — `dev → test → main` — with protected `test`/`main` that only accept the tier below, per-tier CI/CD (essential → full coverage + test release → release + deploy), and an auto-opened `test → main` promotion PR. | Designing or adopting a dev/test/main (staging/production) branching model, locking main/test, configuring three-trunk branch protection, or wiring release-tag automation. |

## Install

### Option A — plugin marketplace (recommended)

Installs all skills at once and keeps them updatable. In Claude Code:

```text
# 1. Register this repo as a marketplace (one-time)
/plugin marketplace add FurkanEdizkan/My-Skills

# 2. Install the bundle
/plugin install skills@furkanedizkan-skills
```

The skills then auto-activate by description, or you can invoke one explicitly as
`/skills:<skill-name>` (e.g. `/skills:conventional-commits`).

To update later: `/plugin marketplace update furkanedizkan-skills`.

### Option B — copy a single skill folder

For a quick, plugin-free install of just one skill, copy its folder into a
project's or your user-level `skills/` directory:

```bash
# project-scoped — available in one repo (run from that repo's root)
cp -r /path/to/My-Skills/skills/<skill-name> .claude/skills/

# user-scoped — available in every project on this machine
cp -r /path/to/My-Skills/skills/<skill-name> ~/.claude/skills/
```

Or pull straight from a clone of this repo:

```bash
git clone https://github.com/FurkanEdizkan/My-Skills ~/src/My-Skills
cp -r ~/src/My-Skills/skills/conventional-commits /path/to/project/.claude/skills/
```

Copied this way the skill is invoked by its bare name (e.g.
`/conventional-commits`). Reload Claude Code so it picks up the new skill.

## Layout

```text
.claude-plugin/
  marketplace.json   # marketplace "furkanedizkan-skills" → lists the bundle plugin
  plugin.json        # plugin "skills" → the bundle (source: repo root)
skills/
  <skill-name>/
    SKILL.md         # frontmatter (name, description) + instructions
README.md
LICENSE
```

The whole repo is one plugin (`source: "./"`) bundling every skill under
`skills/`. Each `skills/<name>/` folder is also self-contained, so a single skill
can be copied out as in [Option B](#option-b--copy-a-single-skill-folder).

## Adding a new skill

1. Create `skills/<skill-name>/SKILL.md` with `name` + `description` frontmatter.
   The skill's invocation name comes from the **directory name**, and the
   `description` is what Claude uses to decide when to auto-activate it — write it
   to cover the trigger situations.
2. Keep it **generalized** — describe the general practice and defer to the
   consuming repo's conventions for specifics.
3. Add a row to the [Available skills](#available-skills) table above.
4. Bump `version` in `.claude-plugin/plugin.json` (and the matching entry in
   `marketplace.json`) so installs pick up the change.
5. Commit it on its own: `feat: add <skill-name> skill`.

## License

[Apache-2.0](LICENSE).
