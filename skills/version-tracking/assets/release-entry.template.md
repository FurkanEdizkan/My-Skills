## [{{VERSION}}] - {{DATE}}

**Release type:** {{minor | major}} · **Previous release:** {{PREVIOUS_TAG or "initial release"}} · **Range:** `{{RANGE}}` ({{N}} commits)

{{ONE_OR_TWO_SENTENCE_SUMMARY — what this release means for users, not a list of commits}}

### ⚠ Breaking changes
- {{What broke}} — **Migration:** {{what users must change}}

### Added
- {{New capability, phrased by user impact}}

### Changed
- {{Behavior that works differently now}}

### Deprecated
- {{Still works, scheduled for removal}} — use {{replacement}} instead (removed in {{VERSION}})

### Removed
- {{Feature or API that is gone}}

### Fixed
- {{Bug that no longer happens}}

### Security
- {{Vulnerability fixed, with severity/CVE if known}}

<!--
Rules:
- Delete every section that has no entries; never leave a heading empty.
- "Breaking changes" goes first and is required for a major release.
- One line per user-visible change. Merge many small commits into one entry;
  leave out pure refactors, CI, formatting and internal chores.
- Link issues/PRs when the repo uses them, e.g. (#42).
-->
