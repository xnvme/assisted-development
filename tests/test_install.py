# SPDX-FileCopyrightText: Simon A. F. Lund <os@safl.dk>
#
# SPDX-License-Identifier: BSD-3-Clause

"""Tests for install.py, run against a throwaway home directory.

The installer writes into $HOME and is the only executable code here, so it is
exercised the way a user runs it: as a process, through --home, checking what
is on disk afterwards rather than what the functions returned.
"""

import subprocess
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
INSTALL = REPO / "install.py"

# One of each link, enough to tell the wiring is right without restating the
# whole layout.
RULE = ".claude/rules/assisted-development.md"


def run(home, *args):
    return subprocess.run(
        [str(INSTALL), "--home", str(home), *args],
        capture_output=True,
        text=True,
    )


class InstallTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.home = Path(self.tmp.name)

    def links(self):
        """Every managed link that currently exists under the fake home."""
        return sorted(
            p
            for p in self.home.rglob("*")
            if p.is_symlink() and str(REPO) in str(p.readlink())
        )

    def test_dry_run_changes_nothing(self):
        result = run(self.home, "--dry-run")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("would install", result.stdout)
        self.assertEqual(self.links(), [])

    def test_install_links_and_is_idempotent(self):
        first = run(self.home)
        self.assertEqual(first.returncode, 0, first.stderr)
        for name in [RULE, ".pi/agent/AGENTS.md"]:
            self.assertTrue((self.home / name).is_symlink(), name)
        self.assertEqual((self.home / RULE).resolve(), REPO / "AGENTS.md")

        # A second run must report the links rather than fail on them, since
        # the documented way to update is to pull and run it again.
        again = run(self.home)
        self.assertEqual(again.returncode, 0, again.stderr)
        self.assertNotIn("link ", again.stdout)
        self.assertIn("ok ", again.stdout)

    def test_occupied_path_is_left_alone(self):
        target = self.home / RULE
        target.parent.mkdir(parents=True)
        target.write_text("someone else's file")

        result = run(self.home)
        self.assertEqual(result.returncode, 1)
        self.assertIn("SKIP", result.stdout)
        self.assertEqual(target.read_text(), "someone else's file")
        # The rest still got linked; one occupied path does not stop the run.
        self.assertTrue((self.home / ".pi/agent/AGENTS.md").is_symlink())

    def test_uninstall_removes_only_our_links(self):
        run(self.home)
        foreign = self.home / ".claude/skills/theirs"
        foreign.parent.mkdir(parents=True, exist_ok=True)
        foreign.symlink_to("/somewhere/else")

        result = run(self.home, "--uninstall")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.links(), [])
        self.assertTrue(foreign.is_symlink())

    def test_stale_link_is_swept(self):
        """A dropped skill leaves a link that nothing owns."""
        run(self.home)
        stale = self.home / ".claude/skills/old-name"
        stale.parent.mkdir(parents=True, exist_ok=True)
        stale.symlink_to(REPO / "skills/old-name")
        self.assertFalse(stale.exists())  # broken, as it would be in practice

        result = run(self.home)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("stale", result.stdout)
        self.assertFalse(stale.is_symlink())
        # The live links survived the sweep.
        self.assertTrue((self.home / RULE).is_symlink())

    def test_uninstall_sweeps_a_stale_link(self):
        run(self.home)
        stale = self.home / ".claude/skills/old-name"
        stale.parent.mkdir(parents=True, exist_ok=True)
        stale.symlink_to(REPO / "skills/old-name")

        result = run(self.home, "--uninstall")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("stale", result.stdout)
        self.assertFalse(stale.is_symlink())

    def test_stale_convention_link_is_swept(self):
        """The rules directory is scanned too, not only the skills ones."""
        run(self.home)
        stale = self.home / ".claude/rules/old-name.md"
        stale.parent.mkdir(parents=True, exist_ok=True)
        stale.symlink_to(REPO / "OLD-AGENTS.md")

        result = run(self.home)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(stale.is_symlink())
        self.assertTrue((self.home / RULE).is_symlink())

    def test_working_alias_is_left_alone(self):
        """A link the user made themselves is not the installer's to remove."""
        run(self.home)
        alias = self.home / ".claude/skills/selfreview"
        alias.parent.mkdir(parents=True, exist_ok=True)
        alias.symlink_to(REPO / "AGENTS.md")

        result = run(self.home)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn("stale", result.stdout)
        self.assertTrue(alias.is_symlink())

    def test_stale_link_survives_a_dry_run(self):
        run(self.home)
        stale = self.home / ".agents/skills/old-name"
        stale.parent.mkdir(parents=True, exist_ok=True)
        stale.symlink_to(REPO / "skills/old-name")

        result = run(self.home, "--dry-run")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("stale", result.stdout)
        self.assertTrue(stale.is_symlink())


if __name__ == "__main__":
    unittest.main()
