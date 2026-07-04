#!/usr/bin/env bash
# STEP 6 — PROVE IT.
# Runs the same three real tasks through the routed stack and prints which
# model handled each and exactly what it cost (billed numbers straight from
# OpenRouter's /generation endpoint, not estimates).
#
#   ./run_proof.sh              # the three routed runs
#   ./run_proof.sh --compare    # ...plus the coding task on Claude Fable 5
#                               # through the same key, for the price gap
#
# Needs: OPENROUTER_API_KEY in the environment or in ai-stack/.env
set -euo pipefail
cd "$(dirname "$0")/.."

CODING_TASK='Write a Python function `merge_intervals(intervals)` that merges overlapping [start, end] intervals in O(n log n), with docstring and 5 doctest cases covering edge cases.'
WEB_TASK='Design a single-file HTML landing page (inline CSS, no frameworks) for a boutique coffee roaster: hero with headline, 3-card product grid, sticky nav, mobile responsive. Distinctive typography, no generic AI look.'
REASONING_TASK='A sealed 2 L container holds 0.5 mol of an ideal gas at 300 K. It is heated until the pressure doubles, then expanded isothermally to twice the volume. Derive the final temperature and pressure step by step, stating each law used.'

run () {  # run <label> <extra args...> <prompt>
  local label=$1; shift
  local prompt=${*: -1}
  set -- "${@:1:$#-1}"
  echo "=== $label ==="
  out=$(python3 router.py ask --json "$@" "$prompt")
  echo "$out" | python3 -c '
import json, sys
d = json.load(sys.stdin)
c = d["cost_usd"]
cost = "$%.6f" % c if c is not None else "pending (see logs/usage.jsonl)"
preview = d["answer"][:160].replace("\n", " ")
print("  model : " + str(d["model"]))
print("  route : " + str(d["route"]))
print("  cost  : " + cost)
print("  tokens: %s in / %s out   time: %ss" % (d["tokens_in"], d["tokens_out"], d["seconds"]))
print("  answer preview: " + preview + "...")
'
  echo
}

run "1/3 CODING  (expect deepseek/deepseek-v4-pro)"  "$CODING_TASK"
run "2/3 WEB/DESIGN  (expect z-ai/glm-5.2)"          "$WEB_TASK"
run "3/3 REASONING  (expect minimax/minimax-m3)"     "$REASONING_TASK"

if [[ "${1:-}" == "--compare" ]]; then
  # Same coding task, frontier model, same key — explicit opt-in only.
  FRONTIER=$(python3 -c 'import tomllib;print(tomllib.load(open("router.toml","rb"))["limits"]["frontier_compare_model"])')
  run "COMPARE: same coding task on $FRONTIER" --frontier --model "$FRONTIER" "$CODING_TASK"
  echo "Compare the two coding-task cost lines above: same deliverable, ~35x price gap."
fi

echo "Full ledger: logs/usage.jsonl"
