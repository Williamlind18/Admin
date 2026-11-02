#!/bin/bash
# Cloud sessions: make the vmake-skill ready (Python deps) and report whether its keys are set.
set -euo pipefail

if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

VMAKE="$CLAUDE_PROJECT_DIR/.claude/skills/vmake-skill/scripts/vmake_ai.py"
[ -f "$VMAKE" ] || exit 0

# Idempotent: only pip-installs when requests / alibabacloud-oss-v2 are missing.
python3 "$VMAKE" install-deps >/dev/null 2>&1 || echo "vmake-skill: install-deps failed; run it manually before using Vmake."

# preflight prints only ok/missing, never the keys.
if [ "$(python3 "$VMAKE" preflight 2>/dev/null || true)" = "ok" ]; then
  echo "vmake-skill: ready (deps installed, MT_AK/MT_SK set)."
else
  echo "vmake-skill: deps installed, but MT_AK/MT_SK are missing. Ask the user to add them as environment variables in the cloud environment settings."
fi
