#!/usr/bin/env python3
"""Read, initialise and bump a repo-root VERSION file (MAJOR.MINOR.PATCH).

Run from anywhere inside the target git repository:

    version.py status                  # current/committed version, manual edit?, release tags
    version.py init [X.Y.Z]            # create VERSION (default 0.0.1) if missing
    version.py bump patch|minor|major  # bump and write VERSION, print the new version
    version.py set X.Y.Z               # write an explicit version
    version.py range [--major]         # git range for the changelog of the next release

Standard library only. Exits non-zero with a message on any error.
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

SEMVER = re.compile(r"^(\d+)\.(\d+)\.(\d+)$")
TAG = re.compile(r"^v(\d+)\.(\d+)\.(\d+)$")
DEFAULT = "0.0.1"


def git(*args: str) -> str:
    out = subprocess.run(["git", *args], capture_output=True, text=True)
    if out.returncode != 0:
        raise RuntimeError(out.stderr.strip() or f"git {' '.join(args)} failed")
    return out.stdout.strip()


def repo_root() -> Path:
    return Path(git("rev-parse", "--show-toplevel"))


def version_file() -> Path:
    return repo_root() / "VERSION"


def parse(text: str) -> tuple[int, int, int]:
    m = SEMVER.match(text.strip())
    if not m:
        raise ValueError(f"not a MAJOR.MINOR.PATCH version: {text.strip()!r}")
    return int(m[1]), int(m[2]), int(m[3])


def fmt(v: tuple[int, int, int]) -> str:
    return "%d.%d.%d" % v


def read_current() -> tuple[int, int, int] | None:
    f = version_file()
    return parse(f.read_text()) if f.exists() else None


def read_committed() -> tuple[int, int, int] | None:
    try:
        return parse(git("show", "HEAD:VERSION"))
    except (RuntimeError, ValueError):
        return None


def write(v: tuple[int, int, int]) -> None:
    version_file().write_text(fmt(v) + "\n")


def release_tags() -> list[tuple[int, int, int]]:
    tags = []
    for t in git("tag", "--list", "v*").splitlines():
        m = TAG.match(t.strip())
        if m:
            tags.append((int(m[1]), int(m[2]), int(m[3])))
    return sorted(tags)


def bump(v: tuple[int, int, int], part: str) -> tuple[int, int, int]:
    major, minor, patch = v
    if part == "patch":
        return major, minor, patch + 1
    if part == "minor":
        return major, minor + 1, 0
    if part == "major":
        return major + 1, 0, 0
    raise ValueError(f"unknown part {part!r}; use patch, minor or major")


def cmd_status() -> None:
    cur, com = read_current(), read_committed()
    tags = release_tags()
    print(f"VERSION file      : {fmt(cur) if cur else 'missing'}")
    print(f"committed (HEAD)  : {fmt(com) if com else 'none'}")
    manual = cur is not None and com is not None and cur != com
    print(f"edited since HEAD : {'yes' if manual else 'no'}")
    print(f"latest tag        : {'v' + fmt(tags[-1]) if tags else 'none'}")
    if cur and tags and cur < tags[-1]:
        print("WARNING: VERSION is lower than the latest tag")


def cmd_init(args: list[str]) -> None:
    if version_file().exists():
        print(f"VERSION already exists: {fmt(read_current())}")
        return
    v = parse(args[0]) if args else parse(DEFAULT)
    write(v)
    print(fmt(v))


def cmd_bump(args: list[str]) -> None:
    if not args:
        raise ValueError("usage: bump patch|minor|major [--force]")
    cur, com = read_current(), read_committed()
    if cur is None:
        raise ValueError("VERSION is missing; run init first")
    if "--force" not in args:
        if com is None:
            # VERSION is new in this commit — it ships as written (0.0.1 by default).
            print(f"{fmt(cur)}  (kept: VERSION not committed yet)")
            return
        if cur != com:
            # VERSION was already changed for this commit (by hand or an earlier bump).
            print(f"{fmt(cur)}  (kept: changed since HEAD {fmt(com)})")
            return
    new = bump(cur, args[0])
    write(new)
    print(fmt(new))


def cmd_set(args: list[str]) -> None:
    if not args:
        raise ValueError("usage: set X.Y.Z")
    v = parse(args[0])
    write(v)
    print(fmt(v))


def cmd_range(args: list[str]) -> None:
    """Print the git revision range covering the release being prepared.

    Default: since the latest release tag (any vX.Y.Z).
    --major : since the latest vN.0.0 tag below the current major (whole history if none).
    """
    cur = read_current()
    tags = [t for t in release_tags() if cur is None or t < cur]
    if "--major" in args and cur is not None:
        tags = [t for t in tags if t[1] == 0 and t[2] == 0 and t[0] < cur[0]]
    # No earlier tag: "HEAD" makes `git log HEAD` cover the whole history.
    print(f"v{fmt(tags[-1])}..HEAD" if tags else "HEAD")


def main(argv: list[str]) -> int:
    if not argv or argv[0] in {"-h", "--help"}:
        print(__doc__)
        return 0
    cmd, rest = argv[0], argv[1:]
    try:
        {"status": lambda: cmd_status(),
         "init": lambda: cmd_init(rest),
         "bump": lambda: cmd_bump(rest),
         "set": lambda: cmd_set(rest),
         "range": lambda: cmd_range(rest)}[cmd]()
    except KeyError:
        print(f"unknown command {cmd!r}\n{__doc__}", file=sys.stderr)
        return 2
    except (RuntimeError, ValueError, OSError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
