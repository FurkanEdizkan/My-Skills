---
name: create-github-issue
description: >-
  Turn a plan into tracked GitHub work, in any repository. For each task in the
  plan, create an issue (filled from the repo's bug/feature template if one
  exists, with the repo's labels and the current user as assignee), cut a
  conventionally-named branch from the repo's integration branch, log progress
  as issue comments, run the repo's pre-PR checks, and open a PR back into the
  integration branch when done. Use whenever the user types
  /create-github-issue, asks to "create issues for these tasks", "track this
  plan as issues", "open an issue and start working on it", or wants the
  plan→issue→branch→PR workflow with a detailed work log. If the repo defines
  its own issue/branch/PR conventions (CONTRIBUTING.md, .github/ templates,
  established label set), follow those — this skill is the general baseline.
---

# create-github-issue

Convert a plan into tracked, logged GitHub work. The lifecycle for **each task** is:

```
plan ─▶ issue (labelled, assigned, on board) ─▶ branch (from integration) ─▶ work + comment log ─▶ checks ─▶ PR ─▶ summary comment
```

The **issue is the single source of truth**: it accumulates a detailed log of completed parts and
solved problems as comments while the work proceeds, so anyone reading it later sees the full story.

This skill is the general baseline. Always check the repo's actual conventions first
(`CONTRIBUTING.md`, `.github/ISSUE_TEMPLATE/*`, `.github/PULL_REQUEST_TEMPLATE.md`,
`.github/rulesets/*.json`, `gh label list`, `git log`); if they differ from the defaults below,
the repo wins.

## 0. Preconditions

Run these read-only checks first:

1. `gh auth status` — confirm the GitHub CLI is authenticated (else stop: user runs `gh auth login`).
2. `gh api user -q .login` — the current user's login. **This is the assignee** for every issue and PR (`@me`).
3. `git fetch origin` — sync refs.
4. **Identify the integration branch** (the PR target). In order of preference:
   - If the repo follows a two-trunk model (e.g. `test` + `main`, see the project's
     `docs/BRANCHING.md` or `CONTRIBUTING.md`), the integration branch is `test`.
   - Otherwise it's the default branch (usually `main`).
   - If the two-trunk model is documented but `test` is missing on origin, surface that to the user
     rather than silently creating it — branch creation is a maintainer decision.

State one line back to the user: assignee, integration branch, then continue.

## 1. Plan → tasks

Reuse the plan already in the conversation, or work with the user to break the goal into **discrete,
independently shippable tasks** — one issue per task, each small enough to map to one branch and one
PR. **Confirm the task list with the user before creating issues** (creating issues is outward-facing).

## 2. Create one issue per task

For each task, use the repo's matching issue template if one exists in `.github/ISSUE_TEMPLATE/`,
then apply the repo's label conventions.

- **Kind → template + type label.** Run `ls .github/ISSUE_TEMPLATE/` and `gh label list` to see what
  the repo actually has. Typical mapping (adjust to the repo):
  - bug → template `bug_report.yml`, label like `type:fix` / `bug`
  - feature/improvement → template `feature_request.yml`, label like `type:feat` / `enhancement`
  - other → label like `type:chore` / `type:docs` / `type:refactor` as the repo defines.
- **Area / component label** — many repos have an `area:*` or `component:*` label set for the part of
  the codebase touched. Pick the right one; ask the user if unclear.
- **Phase / milestone / priority labels** — apply whatever scheme the repo uses.
- **Title:** concise, imperative, Conventional-Commit-flavoured, e.g. `feat(api): add retry backoff`.
- **Body:** fill **every required template field** with real detail from the plan. End with an
  acceptance-criteria checklist of sub-steps — the skeleton the work log hangs off.
- **Assignee:** `@me`.

```bash
gh issue create \
  --title "feat(api): add retry backoff" \
  --body-file <(cat <<'EOF'
### Problem / motivation
...
### Proposed solution
...
### Area
api
### Alternatives considered
...

### Acceptance criteria
- [ ] ...
- [ ] ...
EOF
) \
  --label "type:feat" --label "area:api" \
  --assignee "@me"
```

Capture each issue number/URL and report the created issues to the user.

## 3. Take on an issue → branch + board

Do one issue at a time unless told to batch.

1. If the repo uses a GitHub Project board, add the issue and move it to **In Progress**:
   ```bash
   gh issue edit <n> --add-project "<Project name>"
   # Status field/option ids vary per board; discover once:
   #   gh project list --owner <owner>
   #   gh project field-list <project-number> --owner <owner>
   #   gh project item-edit --id <item-id> --field-id <status-field-id> \
   #       --single-select-option-id <in-progress-id> --project-id <project-id>
   ```
   If the board can't be reached non-interactively, note it and continue — don't block the work on it.
2. Cut the branch **from the integration branch**, named per the repo's branch convention
   (Conventional Branches as the baseline: `<type>/<short-description>` or `<type>/<issue#>-<slug>`,
   types: `feat fix chore docs refactor test ci perf`):
   ```bash
   git switch -c feat/142-retry-backoff origin/<integration-branch>
   ```
3. Post a **"work started"** comment so the log opens with a start marker:
   ```bash
   gh issue comment <n> --body "🚧 Started on branch \`feat/142-retry-backoff\` (from \`<integration-branch>\`)."
   ```

## 4. Work the task → log as you go

The issue comments are the **detailed log**. Comment at every meaningful boundary — don't wait for the end:

- **Major step done** → what was done and why (e.g. "✅ Added exponential backoff to `Client.request`; covered by `test_retry_backoff`").
- **Problem hit & solved** → symptom, root cause, fix. These solved-issue notes are the most valuable part of the log.
- **Decision / scope change** → the choice and the reasoning.

```bash
gh issue comment <n> --body "✅ <step>"    # or "🐛 <problem> → <fix>"
```

Commit with **Conventional Commits** — invoke the `conventional-commits` skill for this repo's exact
format. Reference the issue in the summary/body (`(#142)`). Keep commits focused so history mirrors
the comment log. Tick the issue checklist as sub-steps land (`gh issue edit <n> --body ...`).

## 5. Pre-PR checks (must pass)

Run the same checks CI requires before opening the PR; fix red before proceeding. Look up what CI
actually runs:

```bash
cat .github/workflows/*.yml   # or `gh workflow list` + `gh workflow view <id>`
```

Typical patterns by stack — adapt to what's actually wired up:

- **Node** — `npm install && npm run lint && npm test && npm run build`
- **Python (uv)** — `uv sync && uv run ruff check . && uv run pytest`
- **Python (pip)** — `pip install -e ".[dev]" && pytest`
- **Go** — `go build ./... && go test ./...`
- **Rust** — `cargo check && cargo test`
- **C++ (cmake)** — `cmake -B build && cmake --build build && ctest --test-dir build`

If the repo regenerates code (OpenAPI schema, GraphQL types, protobufs, …), regenerate and commit
the result so CI's drift check passes. If it ships a migration system (Alembic, Prisma, Diesel, …),
include the migration for any schema change.

Required status checks: read the branch protection rules (`.github/rulesets/*.json` or repo
settings) and make sure the equivalents pass locally.

## 6. Complete → PR to the integration branch

1. Push: `git push -u origin <branch>`.
2. Open the PR **with base = integration branch**, body reproducing **every section** of
   `.github/PULL_REQUEST_TEMPLATE.md`, assignee `@me`:
   ```bash
   gh pr create --base <integration-branch> --head <branch> \
     --title "feat(api): add retry backoff" \
     --body-file <(cat <<'EOF'
## Summary
...
## Type of change
- [x] feat — new feature
## Testing
<what you ran; expected results>
## Checklist
- [x] Tests and lint pass locally
- [x] Docs / README updated if behaviour changed
- [x] PR title follows Conventional Commits

Closes #142
EOF
) \
     --assignee "@me"
   ```
   - Fill the checklist **honestly** (only tick what's true).
   - ⚠️ **Auto-close caveat:** `Closes #142` only auto-closes the issue when the PR merges into the
     **default branch** (usually `main`). If the integration branch is *not* the default branch
     (two-trunk model where PRs target `test` and `main` is the default), the issue will **not**
     auto-close on merge — close it manually (`gh issue close 142`) once merged, after posting the
     summary comment.
3. Post a **final summary comment** on the issue: a tidy recap of completed parts and every problem
   solved, plus the PR link — this closes the log:
   ```bash
   gh issue comment <n> --body "🎉 Completed in #<pr-number>. Summary: …"
   ```

Report each PR URL to the user. **Do not merge** without explicit instruction — that's a maintainer
action. Follow the repo's merge style (merge commit vs squash vs rebase) — check
`CONTRIBUTING.md` or recent merged PRs on the integration branch.

## Conventions checklist (per task)

- [ ] Issue from the right template; type/area/phase labels per the repo; assigned to user
- [ ] Issue on the project board (if one exists), moved to In Progress
- [ ] Branch named per the repo's convention, cut from the integration branch
- [ ] "Started" comment posted
- [ ] Major steps + solved problems logged as comments
- [ ] Conventional commits referencing the issue
- [ ] Pre-PR checks pass (the same commands CI runs)
- [ ] PR against the integration branch, template filled honestly, assigned, `Closes #<n>`
- [ ] Final summary comment posted with the PR link; issue closed manually if PR doesn't auto-close it

## Notes

- **Non-destructive:** never merges, force-pushes, or deletes branches without an explicit ask.
- If a repo rule conflicts with these steps, **the repo file wins** — surface the conflict and follow it.
- Default to creating all issues up front, then taking them on one branch/PR at a time; follow the
  user's stated preference if different.
- Pairs naturally with `conventional-commits` (commit format), `conventional-branches` (branch naming),
  and `modular-services` (unit-of-work shape) from this same plugin.
