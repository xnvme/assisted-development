#!/usr/bin/env python3
# SPDX-FileCopyrightText: Simon A. F. Lund <os@safl.dk>
#
# SPDX-License-Identifier: BSD-3-Clause

"""Install assisted-development into a user's agent configuration.

Everything is a symlink back into this checkout, in the spirit of stow, so a
`git pull` updates every tool at once and uninstalling leaves nothing behind.

Not stow itself, for three reasons. Stow mirrors a package tree one-to-one,
and this needs one source at two targets plus a rename, which would mean
committing a tree of tool-specific paths and symlinks: the thing the installer
exists to avoid. Stow also folds trees, linking `~/.claude/skills` itself when
it does not exist yet, which would force every skill you later write to live in
this repository. And it is a dependency, absent on Windows, for a page of
Python.

    ./install.py              link into $HOME
    ./install.py --dry-run    show what would change, touch nothing
    ./install.py --uninstall  remove the links that point at this checkout

What gets linked, relative to $HOME:

    .claude/rules/assisted-development.md -> AGENTS.md      (Claude Code)
    .pi/agent/AGENTS.md                   -> AGENTS.md      (pi)
    .claude/skills/<name>                 -> skills/<name>  (Claude Code)
    .agents/skills/<name>                 -> skills/<name>  (Codex, Cursor, pi)

Nothing is ever overwritten. A path that already exists and is not a link into
this checkout is reported and left alone, because it is someone else's file.

Broken links into this checkout, left behind by anything renamed or removed
here, are cleaned up by both actions, in the directories listed above. A link
to a skill that no longer exists is a broken skill directory to whichever agent
reads it, and only this checkout can know the skill is gone. Links that still
resolve are left alone whoever made them.
"""

import argparse
import os
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent

# Where each tool looks for skills. Claude Code reads only .claude; Codex,
# Cursor, and pi read .agents. One link per skill per directory covers all.
SKILL_DIRS = [".claude/skills", ".agents/skills"]

# Where each tool looks for instructions that load every session. Claude Code
# does not read AGENTS.md at all, so its copy arrives as a user-level rule; pi
# reads a global AGENTS.md directly. Links rather than edits to a file the user
# wrote, so uninstalling is a deletion.
CONVENTION_LINKS = [
    ".claude/rules/assisted-development.md",
    ".pi/agent/AGENTS.md",
]


def skills():
    """Every skill directory in this checkout, sorted for stable output."""
    root = REPO / "skills"
    return sorted(d for d in root.iterdir() if (d / "SKILL.md").is_file())


def links(home):
    """The (target, source) pairs this installer manages."""
    for target in CONVENTION_LINKS:
        yield home / target, REPO / "AGENTS.md"
    for skill in skills():
        for skill_dir in SKILL_DIRS:
            yield home / skill_dir / skill.name, skill


def scanned(home):
    """The directories this installer puts links in, so it can find its own."""
    roots = {home / skill_dir for skill_dir in SKILL_DIRS}
    roots.update((home / target).parent for target in CONVENTION_LINKS)
    return sorted(roots)


def strays(home):
    """Broken links into this checkout that `links()` does not account for.

    Rename or drop a skill and its old link stays behind, pointing at a path
    that no longer exists. Nothing records the old name, so the only way to
    find it is by where it points.

    Broken is part of the test, not an incidental detail. A link into this
    checkout that still resolves is someone's own alias, and deleting a
    working file the installer did not create is the thing it never does.
    """
    managed = {target for target, _ in links(home)}
    for root in scanned(home):
        if not root.is_dir():
            continue
        for entry in sorted(root.iterdir()):
            if entry in managed or not entry.is_symlink():
                continue
            if entry.exists():
                continue
            if Path(os.path.realpath(entry)).is_relative_to(REPO):
                yield entry


def sweep(home, dry_run):
    """Remove the strays. Reported as removals, not as problems."""
    for stray in strays(home):
        print(f"  stale    {stray.relative_to(home)}")
        if not dry_run:
            stray.unlink()


def status(target, source):
    """What is at `target` right now, from this installer's point of view."""
    if target.is_symlink():
        # Ours if it points where we would point it, whoever created it.
        if os.path.realpath(target) == str(source):
            return "linked"
        return "other-link"
    if target.exists():
        return "occupied"
    return "absent"


def install(home, dry_run):
    problems = 0
    for target, source in links(home):
        state = status(target, source)
        shown = target.relative_to(home)
        if state == "linked":
            print(f"  ok       {shown}")
            continue
        if state in ("occupied", "other-link"):
            print(f"  SKIP     {shown} exists and is not ours ({state})")
            problems += 1
            continue
        print(f"  link     {shown} -> {source}")
        if dry_run:
            continue
        try:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.symlink_to(source)
        except OSError as err:
            # Windows refuses without Developer Mode or Administrator.
            print(f"  FAILED   {shown}: {err}")
            print(
                "           copy the directory instead, and re-copy to update"
            )
            problems += 1
    sweep(home, dry_run)
    return problems


def uninstall(home, dry_run):
    """Remove our links.

    Always succeeds. A path skipped here was never ours to remove, so there is
    nothing for the caller to resolve and nothing to report in the exit status.
    """
    for target, source in links(home):
        state = status(target, source)
        shown = target.relative_to(home)
        if state == "linked":
            print(f"  remove   {shown}")
            if not dry_run:
                target.unlink()
        elif state == "absent":
            print(f"  ok       {shown} not present")
        else:
            print(f"  SKIP     {shown} is not ours ({state})")
    sweep(home, dry_run)
    return 0


def main():
    parser = argparse.ArgumentParser(
        description="Install assisted-development into an agent configuration."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="report what would change without changing it",
    )
    parser.add_argument(
        "--uninstall",
        action="store_true",
        help="remove links pointing at this checkout",
    )
    parser.add_argument(
        "--home",
        type=Path,
        default=Path.home(),
        help="act on somewhere other than $HOME, for testing",
    )
    args = parser.parse_args()

    home = args.home.expanduser().resolve()
    action = uninstall if args.uninstall else install
    verb = "uninstall {} from {}" if args.uninstall else "install {} into {}"
    print(f"{'would ' if args.dry_run else ''}{verb.format(REPO, home)}")

    problems = action(home, args.dry_run)
    if problems:
        print(f"\n{problems} target(s) need attention.")
        print("Nothing was overwritten; resolve them and run again.")
        return 1
    if not args.uninstall and not args.dry_run:
        print(
            "\nStart your agent in any repository. The conventions load every"
        )
        print("session and the skills are available by name.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
