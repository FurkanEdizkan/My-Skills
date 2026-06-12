---
name: three-tier-git-flow
description: >-
  Set up and run a three-trunk, promote-upward git workflow — dev → test → main
  — where main and test are protected and only accept changes promoted from the
  branch below, each tier owns a distinct CI/CD responsibility (essential checks
  on dev, full coverage + a test/pre-release on test, release tagging + deploy on
  main), and a test → main promotion PR is opened automatically once test goes
  green. Use whenever you are asked to design or adopt a dev/test/main (or
  staging/production) branching model, lock main/test so they only accept code
  from the tier below, configure branch protection or rulesets for three trunks,
  wire release/tag automation and "test releases", or promote a change up the
  tiers. GitHub-flavoured examples; principles apply to any CI host. If the repo
  already defines its own branching/release convention (CONTRIBUTING.md,
  docs/BRANCHING.md, existing workflows/rulesets), follow that — this skill is the
  general baseline.
---

# Three-Tier Git Flow (dev → test → main)

Run three long-lived, **promote-upward** trunks. Work flows in one direction only;
each tier is more protected and more thoroughly verified than the one below it:

```text
feature/* ──PR──▶  dev  ──PR──▶  test  ──auto-PR──▶  main
 (work)         (integrate)   (stabilize)        (release)
                essential CI   full coverage      tag + GitHub
                               + test release     release + deploy
```

- **`dev`** — integration trunk. All day-to-day work lands here via short-lived
  branches. **Essential CI only** (lint, build, fast/unit tests) so iteration is quick.
- **`test`** — stabilization trunk. **Locked: only accepts PRs from `dev`.** Runs the
  **full test suite + coverage gate**; on merge it tags a release-candidate and publishes
  a **pre-release** ("test release") so a build can be validated before production.
- **`main`** — production trunk. **Locked: only accepts PRs from `test`.** On merge it
  tags the final release, publishes a **GitHub release**, and deploys.

The promotion `test → main` is **opened automatically** once `test` is green, but a
maintainer still merges it — `main` stays a human-gated lock.

## Check what the project expects first

Before changing any branch or workflow, match the repo's existing practice — **it overrides
the generic guidance here**:

- **`CONTRIBUTING.md` / `docs/BRANCHING.md`** — may already define the trunk names, who
  promotes, and the release cadence.
- **`git branch -a` and the default branch** — see which trunks exist and which is default.
- **`.github/workflows/*` and `.github/rulesets/*` (or repo settings)** — the CI jobs and
  protection already wired up. Extend these rather than duplicating them.
- **`git tag` / existing GitHub Releases** — the established tag/version scheme.

If none of these exist, the model below is a safe default.

## The three trunks

| Branch | Role | Protection | CI/CD responsibility |
| ------ | ---- | ---------- | -------------------- |
| `dev`  | Integration — all active development lands here | PR required; **essential** checks must pass; no direct push | Lint, build, **fast/unit tests** — quick signal |
| `test` | Stabilization / staging | **Locked**: PR required, source **must be `dev`**, **full** checks required, no direct push | **Full** test suite + coverage gate; on merge → RC tag `vX.Y.Z-rc.N` + **pre-release** |
| `main` | Production | **Locked**: PR required, source **must be `test`**, all checks required, no direct push, restricted pushers | On merge → final tag `vX.Y.Z` + **GitHub release** + deploy |

The mental model: **the higher the tier, the stricter the gate and the more complete the
verification.** Nothing skips a tier.

## The promotion path

Here the **integration branch is `dev`** — that's where feature branches are cut from and PR
back into (unlike a two-trunk `test`+`main` model, where the integration branch is `test`; see
`create-github-issue`).

1. **Cut a short-lived branch from `dev`** — `feat/…`, `fix/…`, etc. (see `conventional-branches`):

   ```bash
   git switch dev && git pull
   git switch -c feat/123-oauth-login
   ```

2. **Develop and iterate on `dev`.** Open a PR into `dev`; **essential CI** must pass; merge.
   Repeat until `dev` holds a coherent set of changes worth stabilizing.
3. **Promote `dev → test`.** Open a PR with **base `test`, head `dev`**. The **full** suite +
   coverage gate runs on this PR. Merge when green.
4. **`test` publishes a test release.** On merge to `test`, CI tags an RC (`vX.Y.Z-rc.N`) and
   publishes a **pre-release** to validate.
5. **`test → main` PR opens automatically** (see [Automating test → main](#automating-test--main)).
   A maintainer reviews and merges — `main` is never advanced unattended.
6. **`main` releases.** On merge to `main`, CI tags `vX.Y.Z`, publishes the **GitHub release**,
   and deploys.

## CI/CD per tier

Concrete examples use **GitHub Actions**; the stage split (essential → full → release) maps to any
CI host. Keep the per-tier jobs in separate workflow files keyed on the target branch.

### `dev` — essential checks (fast feedback)

```yaml
# .github/workflows/ci-dev.yml
name: ci-dev
on:
  pull_request:
    branches: [dev]
jobs:
  essential:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: <install>           # e.g. npm ci  /  uv sync  /  go mod download
      - run: <lint>              # e.g. npm run lint
      - run: <unit-tests>        # fast/unit subset only
      - run: <build>
```

### `test` — full coverage + publish a test (pre-)release

```yaml
# .github/workflows/ci-test.yml
name: ci-test
on:
  pull_request:
    branches: [test]            # full suite gates the dev → test PR
  push:
    branches: [test]            # on merge: tag RC + pre-release
jobs:
  full:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: <install>
      - run: <full-test-suite-with-coverage>   # enforce the coverage threshold here
  prerelease:
    needs: full
    if: github.event_name == 'push'
    runs-on: ubuntu-latest
    permissions:
      contents: write
    steps:
      - uses: actions/checkout@v4
      - run: gh release create "v${VERSION}-rc.${{ github.run_number }}" \
               --prerelease --target test --generate-notes
        env:
          GH_TOKEN: ${{ github.token }}
          VERSION: <derived-version>   # from tag, file, or release-please/semantic-release
```

### `main` — release tag + GitHub release + deploy

```yaml
# .github/workflows/release-main.yml
name: release-main
on:
  push:
    branches: [main]
jobs:
  release:
    runs-on: ubuntu-latest
    permissions:
      contents: write
    steps:
      - uses: actions/checkout@v4
      - run: gh release create "v${VERSION}" --target main --generate-notes
        env:
          GH_TOKEN: ${{ github.token }}
          VERSION: <derived-version>
      - run: <deploy>            # your production deploy step / environment
```

> Deriving `VERSION` is a repo decision — a committed version file, `git describe`, or a tool like
> **release-please** / **semantic-release** that reads Conventional Commit history. Defer to whatever
> the repo already uses.

## Enforcing the locks

"`test` only accepts from `dev`" and "`main` only accepts from `test`" take **two** mechanisms,
because branch protection alone can't express the second half:

**1. Branch protection / ruleset** (what rulesets *can* do) — for both `test` and `main`:

- Require a pull request before merging (block direct pushes).
- Require status checks to pass — list the **specific** check names that must be green.
- Restrict who can push / merge (maintainers, or an automation app).

```json
// .github/rulesets/main.json  (apply an equivalent for test)
{
  "name": "main-lock",
  "target": "branch",
  "enforcement": "active",
  "conditions": { "ref_name": { "include": ["refs/heads/main"], "exclude": [] } },
  "rules": [
    { "type": "deletion" },
    { "type": "non_fast_forward" },
    { "type": "pull_request",
      "parameters": { "required_approving_review_count": 1, "dismiss_stale_reviews_on_push": true } },
    { "type": "required_status_checks",
      "parameters": { "required_status_checks": [
        { "context": "full" },
        { "context": "guard-source" }
      ] } }
  ]
}
```

**2. A source-branch guard job** (what rulesets *can't* do). GitHub rulesets **cannot restrict the
source/head branch of a PR**, so add a tiny job that fails the PR when it isn't coming from the
allowed tier:

```yaml
# .github/workflows/guard-source.yml
name: guard-source
on:
  pull_request:
    branches: [test, main]
jobs:
  guard-source:                 # name must match the required-check context
    runs-on: ubuntu-latest
    steps:
      - name: Enforce promotion source
        run: |
          base="${{ github.base_ref }}"; head="${{ github.head_ref }}"
          # main only from test; test only from dev
          if [ "$base" = "main" ] && [ "$head" != "test" ]; then
            echo "::error::main only accepts PRs from test (got '$head')"; exit 1
          fi
          if [ "$base" = "test" ] && [ "$head" != "dev" ]; then
            echo "::error::test only accepts PRs from dev (got '$head')"; exit 1
          fi
```

> **The guard only locks anything if it is a *required status check*.** A guard job that runs but
> isn't listed under `required_status_checks` is cosmetic — a PR from the wrong branch can still
> merge. Guard job **+** required check = the lock.

## Automating `test → main`

Once `test` is green, open the promotion PR automatically; a maintainer merges it (no auto-merge —
`main` stays human-gated):

```yaml
# .github/workflows/promote-test-to-main.yml
name: promote-test-to-main
on:
  push:
    branches: [test]
permissions:
  pull-requests: write          # needed to open a PR
jobs:
  open-promotion-pr:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: |
          gh pr create --base main --head test \
            --title "promote: test → main" \
            --body "Automated promotion. Full suite passed on test; review and merge to release." \
            || echo "PR already open"
        env:
          GH_TOKEN: ${{ secrets.PROMOTION_TOKEN }}
```

**Three gotchas make this silently fail if you skip them:**

1. **Allow Actions to open PRs.** Enable repo/org setting *Settings → Actions → General →
   "Allow GitHub Actions to create and approve pull requests."* Off by default.
2. **Grant the permission.** The workflow (or job) needs `permissions: pull-requests: write`.
3. **Use a PAT or GitHub App token, not the default `GITHUB_TOKEN`.** A PR opened by the built-in
   `GITHUB_TOKEN` **does not trigger other workflows**, so the required checks on the `test → main`
   PR won't run and it can never satisfy its own gate. Open the PR with a PAT / App token
   (`secrets.PROMOTION_TOKEN` above) so the promotion PR's checks actually fire.

## Release & tagging convention

- **`test`** → release-candidate / **pre-release**: `vX.Y.Z-rc.N` (SemVer pre-release, marked
  *pre-release* in GitHub). This is the "test release" used to validate a build.
- **`main`** → final **release**: `vX.Y.Z` (SemVer), a normal GitHub Release.
- Keep version derivation in one place (version file, `git describe`, or release-please /
  semantic-release driven by Conventional Commit history). **Defer to the repo's existing scheme**
  if it has one. Pairs with `conventional-commits` (commit format) and `conventional-branches`
  (branch naming).

## Hotfixes (urgent production fix)

The strict lock means a normal change can't shortcut the tiers — but a production emergency can't
wait for `dev → test → main`. Document an explicit, audited exception rather than bypassing protection:

1. Cut **`hotfix/<slug>`** from **`main`**.
2. Fix + add a regression test; open a **fast-tracked PR straight to `main`** (still reviewed, still
   gated by checks — the source guard should allow `hotfix/*` into `main`).
3. After release, **back-merge `main` down into `test` and `dev`** (or PR the hotfix into `dev` and
   let it promote up) so the lower tiers don't regress on the next promotion.

If your team would rather never shortcut the lock, omit this and accept that every fix crawls the
tiers — but decide it deliberately.

## Adopting this in a repo

1. **Create the trunks.** `git switch -c dev` and `git switch -c test` off `main`, push both.
2. **Pick the default branch.** Usually `dev` (where contributors open PRs) — set it in repo settings.
3. **Add per-tier CI** — `ci-dev.yml` (essential), `ci-test.yml` (full + pre-release), `release-main.yml`.
4. **Add the guard** — `guard-source.yml`, and **list `guard-source` as a required check** on `test`
   and `main`.
5. **Lock `test` and `main`** with protection/rulesets (PR required, required checks incl. the guard,
   no direct push, restricted pushers).
6. **Wire the promotion** — `promote-test-to-main.yml`, with the setting enabled, the
   `pull-requests: write` permission, and a `PROMOTION_TOKEN` (PAT/App).
7. **Document it** in `CONTRIBUTING.md` / `docs/BRANCHING.md` so the model is discoverable.

```bash
# sketch: create + push the trunks, set default, then add rulesets
git switch main && git pull
git switch -c dev  && git push -u origin dev
git switch -c test && git push -u origin test
gh repo edit --default-branch dev
gh api -X POST repos/:owner/:repo/rulesets --input .github/rulesets/main.json
gh api -X POST repos/:owner/:repo/rulesets --input .github/rulesets/test.json
```

## Quick checklist

- [ ] Three trunks exist: `dev` (default), `test`, `main`
- [ ] `dev` runs **essential** CI on PRs; feature branches cut from and merged into `dev`
- [ ] `test` runs the **full** suite + coverage gate; on merge tags an RC and publishes a **pre-release**
- [ ] `main` on merge tags `vX.Y.Z`, publishes a **release**, and deploys
- [ ] `test` and `main` are protected: PR required, required checks, no direct push
- [ ] `guard-source` enforces PR source (`main`←`test`, `test`←`dev`) **and is a required check**
- [ ] `test → main` PR opens automatically (setting on, `pull-requests: write`, PAT/App token)
- [ ] `test → main` is merged by a maintainer, not auto-merged
- [ ] Hotfix exception is documented (or strict-only is a deliberate choice)
- [ ] The model is written down in `CONTRIBUTING.md` / `docs/BRANCHING.md`

## Notes

- **Non-destructive:** this skill plans and scaffolds; it never force-pushes, rewrites protected
  history, or merges to `main` without a maintainer.
- If a repo rule conflicts with these steps, **the repo file wins** — surface the conflict and follow it.
- Pairs with `conventional-branches` (branch naming), `conventional-commits` (commit/version format),
  and `create-github-issue` (under this model its "integration branch" is `dev`).
