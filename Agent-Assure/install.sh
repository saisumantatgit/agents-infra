#!/bin/bash
# Agent-Assure installer — provisions the Python env the grounding engine and the
# PostToolUse capture hook both run under (.venv/bin/python), then points you at
# plugin registration. Claude-Code-first (v1).

set -e

echo "🔎  Agent-Assure Installer"
echo "=========================="
echo ""

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# 1. Python env — the hook (pure stdlib, needs >=3.11) and the gate (needs
#    syntok + pyyaml) both run under this single .venv/bin/python.
if ! command -v uv >/dev/null 2>&1; then
    echo "ERROR: 'uv' is required but not found."
    echo "Install it, then re-run:  curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

echo "Provisioning virtual environment (.venv) and installing runtime deps..."
# `uv sync` creates and manages .venv itself and installs [project.dependencies]
# (syntok, pyyaml) per the lockfile. Do NOT pre-create the venv with an explicit
# `uv venv --python ...` — that desyncs the interpreter uv resolves for the
# project and leaves `uv run` pointing at a different, empty environment.
# (Developers run `uv sync --extra dev` to add pytest; end users don't need it.)
uv sync >/dev/null 2>&1 || uv pip install syntok pyyaml >/dev/null 2>&1

# 2. Sanity check — the engine, the hook, and the gate's deps all import.
echo "Verifying the engine, hook, and dependencies import..."
.venv/bin/python -c "import sys; sys.path.insert(0, '.'); \
import syntok.segmenter, yaml; \
from scripts.ground_check import score_report; \
from scripts.capture_core import make_record, assign_and_append; \
print('  engine + hook + deps: OK')"

echo ""
echo "✅ Agent-Assure environment ready:  $SCRIPT_DIR/.venv"
echo ""
echo "Use as a Claude Code plugin:"
echo "  1. Make this directory discoverable as a plugin (add to your plugin"
echo "     marketplace, or symlink/copy into your Claude Code plugins path)."
echo "  2. The PostToolUse capture hook (.claude-plugin/hooks.json) then records"
echo "     every retrieved source into .assure/evidence-store.jsonl automatically."
echo "  3. After research, run:   /assure-verify <draft-file>"
echo ""
echo "Manual usage (no plugin):"
echo "  .venv/bin/python scripts/ground_check.py \\"
echo "      --draft DRAFT.md --store .assure/evidence-store.jsonl --json"
echo ""
