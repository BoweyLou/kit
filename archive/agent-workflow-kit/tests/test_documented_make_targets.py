import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
COMMAND_RE = re.compile(r"(?:^\s*|`)make\s+(?P<target>[A-Za-z0-9_.-]+)")
TARGET_RE = re.compile(r"^([A-Za-z0-9_.-]+):(?:\s|$)")

ACTIVE_OPERATOR_DOCS = [
    ROOT / "docs" / "ops" / "agent-workflow.md",
    ROOT / "docs" / "ops" / "agent-instruction-hygiene.md",
    ROOT / "docs" / "ops" / "slash-command-grammar.md",
    ROOT / "docs" / "upgrade-flow.md",
]


def root_make_targets() -> set[str]:
    return {
        match.group(1)
        for line in (ROOT / "Makefile").read_text(encoding="utf-8").splitlines()
        for match in [TARGET_RE.match(line)]
        if match and not match.group(1).startswith(".")
    }


def documented_make_targets() -> dict[str, set[str]]:
    targets: dict[str, set[str]] = {}
    for path in ACTIVE_OPERATOR_DOCS:
        relpath = path.relative_to(ROOT).as_posix()
        for line in path.read_text(encoding="utf-8").splitlines():
            for match in COMMAND_RE.finditer(line):
                targets.setdefault(relpath, set()).add(match.group("target"))
    return targets


class DocumentedMakeTargetTests(unittest.TestCase):
    def test_active_operator_docs_match_root_makefile(self):
        available = root_make_targets()
        missing = {
            doc: sorted(target for target in targets if target not in available)
            for doc, targets in documented_make_targets().items()
        }
        missing = {doc: targets for doc, targets in missing.items() if targets}

        self.assertEqual(missing, {})


if __name__ == "__main__":
    unittest.main()
