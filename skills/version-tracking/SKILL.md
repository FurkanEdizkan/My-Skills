---
name: version-tracking
description: >-
  Track a project's version in a repo-root VERSION file (MAJOR.MINOR.PATCH).
  Creates VERSION with 0.0.1 if it is missing, bumps the patch on every commit,
  detects changes significant enough for a minor or major release and suggests
  the jump (0.0.7 → 0.1.0, 0.9.3 → 1.0.0 once the project is mature, 1.4.2 →
  2.0.0 for breaking changes), respects versions the user edits by hand, and on
  each minor/major release writes a templated CHANGELOG.md entry and a detailed
  annotated git tag covering everything since the previous release (or the
  previous major). Use whenever you commit in a repo that has a VERSION file,
  or when the user asks to set up versioning, bump/check/set the version,
  decide whether a change is minor/major or whether the project is ready for
  1.0.0, cut or tag a release, or write release notes or a changelog.
---

# Version Tracking

The project's version lives in one place: a **`VERSION` file at the repository
root** containing a single line, `MAJOR.MINOR.PATCH` (e.g. `0.4.12`).

- **Every commit** bumps `PATCH` automatically, and the new `VERSION` goes into
  that same commit.
- **Minor and major bumps are suggested, never applied silently.** When a change
  or the project's state warrants one, propose it with your reasons and let the
  user decide.
- **The user can edit `VERSION` by hand at any time.** A hand edit wins: you don't
  bump on top of it, and later bumps continue from it.
- **Minor and major bumps are releases.** Each one gets a `CHANGELOG.md` entry
  and an annotated tag `vX.Y.Z` that summarize everything since the previous
  release.

## Helper script

`scripts/version.py` (Python 3, standard library only) does the mechanical work
so the version arithmetic is always right. Run it from inside the target repo,
using the path to this skill's folder:

```bash
python3 <skill-dir>/scripts/version.py status          # VERSION, HEAD's VERSION, hand-edited?, latest tag
python3 <skill-dir>/scripts/version.py init            # create VERSION = 0.0.1 if missing
python3 <skill-dir>/scripts/version.py bump patch      # or minor / major; prints the new version
python3 <skill-dir>/scripts/version.py set 0.3.0       # write an explicit version
python3 <skill-dir>/scripts/version.py range           # git range since the last release tag
python3 <skill-dir>/scripts/version.py range --major   # git range since the last vN.0.0 tag
```

`bump` leaves `VERSION` alone, and says so, when it is already different from
the committed one (hand-edited, or bumped earlier for this same commit) or when
`VERSION` has never been committed. That makes a retry after a failed commit
safe: it won't double-bump. `--force` overrides this. If Python isn't
available, do the same steps by hand. The rules are simple enough.

## 1. Set up (first use in a repo)

1. Run `status`. If `VERSION` exists, use it as it is. Never reset an existing
   version.
2. If it is missing:
   - If the user asked for versioning, or this is clearly their project, run
     `init` to create `VERSION` with `0.0.1`.
   - If you only got here because you are committing in a repo that never opted
     in, ask once before adding the file.
   - If the repo already declares a version elsewhere (`package.json`,
     `pyproject.toml`, `Cargo.toml`, an existing `vX.Y.Z` tag), start `VERSION`
     from that value instead of `0.0.1`, and tell the user.
3. If `CHANGELOG.md` doesn't exist, create it from
   `assets/CHANGELOG.template.md`.
4. Commit `VERSION` (and `CHANGELOG.md`) as part of the current change or on
   their own, e.g. `chore: start version tracking at 0.0.1`. The first commit
   ships `0.0.1` as it is, with no bump.

## 2. On every commit

Before creating any commit in a repo that has `VERSION`:

1. **Classify the change** from the staged diff and the commit message (see §3).
2. **Patch-level** (the default): run `bump patch`, `git add VERSION`, and
   commit. Mention the new version in your reply, e.g. "committed as 0.0.8".
3. **Minor- or major-level**: stop before committing. Propose the bump with
   your evidence (see §4) and let the user choose:
   - **accept** → `bump minor` / `bump major`, then run the release steps (§5);
   - **decline** → `bump patch` and commit normally;
   - **a different number** → `set X.Y.Z`.
4. **`VERSION` already changed in the staged diff**: the user set it by hand.
   Keep it, don't bump. If the new value is a minor or major jump, offer the
   release steps (§5).

Check that the version only moves forward. If a hand-edited value is lower
than the latest tag or the committed version, point it out and ask before
committing.

## 3. Classifying a change

Judge by what someone **using** the project can observe, not by diff size.

| Level | Signals |
| ----- | ------- |
| **patch** | bug fix, refactor with no behavior change, docs, tests, CI, formatting, dependency bump with no behavior change, small internal tweak |
| **minor** | new user-visible capability: a new command, endpoint, public function or class, option, config key, screen or module; a significant behavior improvement; a deprecation; Conventional Commit `feat:` |
| **major** | breaking change: removed or renamed public API/command/option/config key, changed signature or defaults, changed output or data format, incompatible storage/schema migration, dropped platform or runtime support; Conventional Commit `!` or a `BREAKING CHANGE:` footer |

When unsure whether something breaks consumers, treat it as breaking and say
why. A behavior change that consumers relied on is breaking even when the diff
is one line.

### Before 1.0.0, a breaking change is a minor bump

`0.y.z` means "not stable yet", so a breaking change in `0.x` bumps the
**minor** (`0.3.4 → 0.4.0`), not the major. The move to `1.0.0` is a decision
about maturity (§4), not something a single commit triggers.

## 4. Suggesting minor and major releases

Show the user the proposal in this format:

```text
Version suggestion: 0.0.9 → 0.1.0 (minor)
Why:
- adds the `export` command (new user-visible capability)        ← from the diff
- 9 patch commits since 0.0.1, first end-to-end flow now works   ← from history
Checks: ✔ README usage  ✔ tests pass  ✘ no CHANGELOG yet (will create)
Options: accept 0.1.0 · keep patch (0.0.10) · set another version
```

### First minor: `0.0.x → 0.1.0`

Suggest it once the project first does something useful end to end:

- a core feature or flow works from start to finish
- it can be installed or run by following the README
- there are tests for the main path, and they pass

### Later minors: `0.x.y → 0.(x+1).0` and `X.y.z → X.(y+1).0`

Suggest one on any minor-level change from §3, or on a breaking change while
still in `0.x`.

### First stable release: `0.x.y → 1.0.0`

`1.0.0` promises a stable public interface. Suggest it only when most of
these hold, and list each one as met or unmet:

- [ ] the public interface (API, CLI, config, file/data formats) has been
      stable through the last several releases, with no breaking changes recently
- [ ] it is used for real work (in production, by other people, or as a
      dependency)
- [ ] the main features are complete; no known feature gaps or open blocker
      issues
- [ ] tests cover the main behavior and CI is green
- [ ] the documentation covers installing, using and configuring it
- [ ] there is a migration path, or none is needed, for anything still marked
      deprecated

If most of the list is unmet, say so instead of suggesting `1.0.0`, and name
what is missing. The user can still choose `1.0.0` themselves.

### Next major: `X.y.z → (X+1).0.0`

Suggest one on any major-level change from §3 once at `1.0.0` or above.
Include the migration the user's consumers will need, and offer a deprecation
period first (ship the replacement in a minor, remove the old one in the
major) when that's feasible.

## 5. Cutting a release (minor or major bump)

1. **Find the range.**
   - **Minor release:** `range`, which covers everything since the previous
     release tag.
   - **Major release:** `range --major`, which covers everything since the
     previous major (`vN.0.0`), or the whole history for `1.0.0`.

   Read the commits with `git log --no-merges --format='%h %s%n%b' <range>` and
   `git diff --stat <range>`.
2. **Write the changelog entry.** Fill `assets/release-entry.template.md` and
   insert it into `CHANGELOG.md` directly under `## [Unreleased]`, newest first.
   Curate the commits rather than pasting them:
   - group them by user impact
   - merge related commits into one line
   - drop internal chores
   - every breaking change gets a migration note

   Move anything already listed under `Unreleased` into the new entry.
3. **Commit** `VERSION` and `CHANGELOG.md` together with the change, or as
   their own commit: `chore(release): v0.1.0`.
4. **Tag.** Fill `assets/tag-message.template.md` and create an **annotated**
   tag on that commit:

   ```bash
   git tag -a v0.1.0 -F <filled-tag-message-file>
   git show v0.1.0 --no-patch   # check the message
   ```

   Keep the filled message in a temporary file outside the repo.
5. **Push only when the user says so**: `git push origin v0.1.0` (plus the
   branch). Pushing a tag publishes it, so confirm first.

Patch commits are not tagged. Only minor and major releases are, which keeps
the tag list readable.

## Rules that keep the version trustworthy

- **One source of truth:** `VERSION`. If the repo also has a manifest version
  (`package.json`, `pyproject.toml`, …), update it to match in the same commit,
  or tell the user they differ. Never let the two disagree silently.
- **Never move, delete or reuse a published tag.** If a release was wrong, fix
  it with the next version.
- **Versions only go up.** Check every hand edit and every `set` against the
  latest tag.
- **Follow the repo's own rules when they exist.** If CONTRIBUTING.md, CI or an
  existing tag scheme defines versioning differently (e.g. `release-please`,
  `semantic-release`, pre-release tags), follow that and adapt these steps to it.

## Quick checklist

Every commit:

- [ ] `VERSION` exists, or the user agreed to create it
- [ ] change classified; patch bumped, or a minor/major bump proposed with reasons
- [ ] a hand-edited `VERSION` was kept, not bumped on top of
- [ ] `VERSION` staged in the same commit; new version reported to the user

Every release:

- [ ] range picked: since the last release (minor) or the last major (major)
- [ ] `CHANGELOG.md` entry filled from the template, curated, breaking changes
      first with migrations
- [ ] annotated `vX.Y.Z` tag with the filled tag-message template
- [ ] tag pushed only after the user confirmed

## Credits

The SemVer and changelog guidance is adapted from
[`git-workflow-and-versioning`](https://github.com/addyosmani/agent-skills/tree/main/skills/git-workflow-and-versioning)
in addyosmani/agent-skills (MIT, © 2025 Addy Osmani). See `LICENSE-MIT` in
this folder.
