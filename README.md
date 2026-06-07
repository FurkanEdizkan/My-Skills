# My-Skills

A central library of [Claude Code](https://docs.claude.com/en/docs/claude-code)
**skills** — reusable, **generalized** capabilities that can be pulled into any
of our codebases.

Each skill is a self-contained directory containing a `SKILL.md` (YAML
frontmatter + instructions). Skills here are written to be **project-agnostic**:
they describe a general practice and defer to a repository's own conventions
(`CONTRIBUTING.md`, lint config, existing style) when those exist. Keep them that
way — put repo-specific detail in the consuming project, not here.

## Available skills

| Skill | What it does | Use it when |
| ----- | ------------ | ----------- |
| [modular-services](modular-services/SKILL.md) | Structure code as small, single-responsibility units — each with one typed input, one typed output, and exactly one public entrypoint — so failures localize and the data flow reads as a graph. Language-agnostic. | Writing a new feature, adding a module/function of any real size, or refactoring tangled code; or when asked for "microservice-style", modular, or contract-first code. |
| [conventional-commits](conventional-commits/SKILL.md) | Write commit messages that follow the [Conventional Commits 1.0.0](https://www.conventionalcommits.org/) spec, in any repository. | About to commit, choosing a type/scope, or fixing a commit message a commit-lint check rejected. |
| [conventional-branches](conventional-branches/SKILL.md) | Name git branches per the [Conventional Branch](https://conventionalbranch.org/) spec — `<type>/<short-description>`, lowercase, hyphen-separated, optionally issue-numbered. | Creating a branch, cutting a branch for an issue, or renaming a branch that doesn't match the convention. |

## Layout

```text
<skill-name>/
  SKILL.md      # frontmatter (name, description) + instructions
```

This maps 1:1 onto a project's `.claude/skills/` directory, so a skill is
installed by copying its folder.

## Using a skill in a project

Claude Code discovers skills under a project's `.claude/skills/` and your
user-level `~/.claude/skills/`. To use a skill from this library:

```bash
# project-scoped — available in one repo (run from that repo's root)
cp -r /path/to/My-Skills/<skill-name> .claude/skills/

# user-scoped — available in every project on this machine
cp -r /path/to/My-Skills/<skill-name> ~/.claude/skills/
```

Or pull straight from a clone of this repo:

```bash
git clone <this-repo-url> ~/src/My-Skills
cp -r ~/src/My-Skills/conventional-commits /path/to/project/.claude/skills/
```

Reload Claude Code so it picks up the new skill.

## Adding a new skill

1. Create `<skill-name>/SKILL.md` with `name` + `description` frontmatter.
2. Keep it **generalized** — describe the general practice and defer to the
   consuming repo's conventions for specifics.
3. Add a row to the table above.
4. Commit it on its own: `feat: add <skill-name> skill`.

## License

[Apache-2.0](LICENSE).
