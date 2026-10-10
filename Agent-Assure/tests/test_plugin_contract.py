"""J-52 — the plugin contract, pinned.

α4 proved `install.sh`, the engine, the hook and the CLI work in an unrelated
repo. What it could not prove was the PLUGIN path: the manifest, the hook
registration, and the command/skill discovery that Claude Code relies on.

Those four things have a common property that makes them worth a test rather
than a one-off check: **they break SILENTLY.** Nothing fails loudly if the
manifest loses a required key, if a file moves, or — the dangerous one — if a
retrieval tool is added to `capture_core._RETRIEVAL_TOOLS` and NOT to
`hooks/hooks.json`'s matcher. In that last case the hook simply never fires for
that tool, no error appears anywhere, and every claim citing a source from it is
silently uncited. A capture gap is invisible by construction, which is this
estate's signature defect: a control correct about what it examines and silent
about what it does not.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT / "scripts"))

import capture_core  # noqa: E402


def _manifest() -> dict:
    return json.loads((_ROOT / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))


def _hooks() -> dict:
    return json.loads((_ROOT / "hooks" / "hooks.json").read_text(encoding="utf-8"))


# --- (1) the manifest is discoverable --------------------------------------

@pytest.mark.parametrize("key", ["name", "description", "version"])
def test_manifest_has_the_keys_discovery_needs(key):
    assert _manifest().get(key), f"plugin.json is missing {key!r}"


def test_manifest_name_matches_the_directory_convention():
    assert _manifest()["name"] == "agent-assure"


# --- (2) THE ONE THAT MATTERS: matcher vs the real tool list ---------------

def test_every_retrieval_tool_is_matched_by_the_hook_matcher():
    """THE SILENT-GAP GUARD.

    `capture_core._RETRIEVAL_TOOLS` is what the hook will CAPTURE. The matcher in
    hooks.json is what Claude Code will INVOKE the hook for. If a tool is in the
    first and not the second, the hook never runs for it — silently — and every
    claim citing a source retrieved by that tool is uncited with no error
    anywhere. Add a tool to one and this test makes you add it to both.
    """
    matcher = _hooks()["hooks"]["PostToolUse"][0]["matcher"]
    pattern = re.compile(matcher)
    unmatched = sorted(t for t in capture_core._RETRIEVAL_TOOLS
                       if not pattern.fullmatch(t))
    assert not unmatched, (
        f"these retrieval tools are NOT matched by hooks.json, so the hook will "
        f"never fire for them and their sources will be silently absent from the "
        f"store: {unmatched}")


def test_the_matcher_does_not_claim_tools_the_hook_cannot_handle():
    """SIBLING, the other direction. A matcher entry with no handler means the
    hook is invoked and does nothing useful — wasted invocations, and a reader of
    hooks.json is misled about what is captured."""
    matcher = _hooks()["hooks"]["PostToolUse"][0]["matcher"]
    declared = {a for a in matcher.split("|") if a and a.isidentifier() or a}
    unknown = sorted(a for a in matcher.split("|")
                     if a not in capture_core._RETRIEVAL_TOOLS)
    assert not unknown, (
        f"hooks.json matches tools capture_core does not recognise: {unknown}")


# --- (3) the hook command line ---------------------------------------------

def test_the_hook_command_uses_the_plugin_root_and_its_own_interpreter():
    """It must use CLAUDE_PLUGIN_ROOT (the plugin can live anywhere) and the
    plugin's OWN .venv (the user's python will not have syntok)."""
    command = _hooks()["hooks"]["PostToolUse"][0]["hooks"][0]["command"]
    assert "${CLAUDE_PLUGIN_ROOT}" in command, (
        "the hook hardcodes a path; it must resolve CLAUDE_PLUGIN_ROOT")
    assert ".venv/bin/python" in command, (
        "the hook must use the plugin's own interpreter, not the user's")
    assert "capture_hook.py" in command


def test_the_paths_the_hook_command_names_actually_exist():
    """A moved file is a silent plugin failure: the hook is registered, invoked,
    and dies before it can capture anything."""
    command = _hooks()["hooks"]["PostToolUse"][0]["hooks"][0]["command"]
    for rel in re.findall(r"\$\{CLAUDE_PLUGIN_ROOT\}/([^\"']+)", command):
        if rel.endswith(".py"):
            assert (_ROOT / rel).is_file(), f"hook names a missing file: {rel}"


# --- (4) command and skill discovery ---------------------------------------

@pytest.mark.parametrize("rel,expected_name", [
    ("commands/assure-verify.md", "assure-verify"),
    ("skills/verify-grounding/SKILL.md", "verify-grounding"),
])
def test_command_and_skill_frontmatter_is_discoverable(rel, expected_name):
    text = (_ROOT / rel).read_text(encoding="utf-8")
    assert text.startswith("---\n"), f"{rel} has no frontmatter block"
    assert "\n---" in text[4:], f"{rel} frontmatter is unterminated"
    name = re.search(r"^name:\s*(\S+)\s*$", text, re.M)
    assert name and name.group(1) == expected_name, (
        f"{rel} declares name={name.group(1) if name else None!r}, "
        f"expected {expected_name!r}")
