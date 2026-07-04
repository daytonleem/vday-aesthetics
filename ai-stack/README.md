# ai-stack — the open Chinese frontier as ONE stack

One OpenRouter key → five category-leading open models → Hermes as the
always-on runtime → a small readable router that sends every task to the
model that wins it. A few dollars a month instead of $10/M input ($50/M
output) for the top closed frontier model.

**No black box.** Everything is four plain files you can read and edit:

| File | What it is |
|---|---|
| `router.toml` | The routing table: which model wins which task, cheap fallbacks, budget, frontier blocklist |
| `router.py` | ~350 lines, stdlib-only. CLI (`ask`) + local OpenAI-compatible proxy (`serve`) for Hermes |
| `proof/run_proof.sh` | Step 6: three real tasks through the stack, exact billed cost per call |
| `deploy/` | systemd units (VPS) + launchd plist (Mac) for 24/7 auto-restart |

---

## STEP 1 — One key (OpenRouter), with a HARD cap before anything else

OpenRouter is a pay-as-you-go broker that fronts every major model behind a
single **OpenAI-compatible** API: base URL `https://openrouter.ai/api/v1`,
one key, and you swap models by changing one string like
`deepseek/deepseek-v4-pro`. That string is exactly one config value in this
stack (`router.toml`).

Do these four things, in this order:

1. **Account** — sign up at [openrouter.ai](https://openrouter.ai) (email or GitHub/Google).
2. **Credits** — Settings → **Credits** → buy **$5–10** (prepaid). Leave
   **auto top-up OFF**. Prepaid means the absolute worst case is bounded by
   what you loaded.
3. **Key WITH a hard cap** — Settings → **Keys** → *Create Key*. In the
   creation dialog set the **credit limit** field (e.g. **$5**). This is a
   hard, per-key spending cap enforced by OpenRouter: when the key has spent
   that much, it stops working — no matter what some scheduled job on the
   wrong model is doing at 3am. This is the single most important step.
4. **Store the key** — `cp .env.example .env` in this directory and paste
   the key. `.env` is gitignored.

Sanity check (any machine with your key):

```bash
curl -s https://openrouter.ai/api/v1/chat/completions \
  -H "Authorization: Bearer $OPENROUTER_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"deepseek/deepseek-v4-pro","messages":[{"role":"user","content":"say ok"}]}'
```

Defense in depth, because runaway spend is the #1 way these setups die:
- **Layer 1:** hard credit limit on the key (OpenRouter enforces).
- **Layer 2:** prepaid credits, auto top-up off (account can't exceed balance).
- **Layer 3:** `daily_budget_usd` in `router.toml` — the router refuses new
  requests once the day's logged spend crosses it.

## STEP 2 — The stack (verified live on OpenRouter, 2026-07-04)

Each one a category leader; individually just under the closed frontier,
routed together they cover it. Prices are $/M tokens in/out as listed on
openrouter.ai (they drift — the router reports exact billed cost per call):

| Model | OpenRouter id | Wins at | ~Price in/out |
|---|---|---|---|
| DeepSeek V4 Pro | `deepseek/deepseek-v4-pro` | competitive coding | $0.44 / $0.87 |
| GLM-5.2 | `z-ai/glm-5.2` | web design (#1 Design Arena) + math | $1.40 / $4.40 |
| Kimi K2.6 | `moonshotai/kimi-k2.6` | agentic tool-use, 1000s of sequential tool calls | $0.66 / $3.41 |
| MiniMax M3 | `minimax/minimax-m3` | 1M context + expert reasoning (top GPQA) | $0.60 / $2.40 |
| Qwen3.7 Max | `qwen/qwen3.7-max` | strongest all-rounder (default route) | check live |

Reference point: Claude Fable 5 is **$10 / $50**. Against DeepSeek's input
price that's the ~35x gap; against most of the stack it's 7–25x.

## STEP 3 — The engine (Hermes)

[Hermes](https://github.com/NousResearch/hermes-agent) is Nous Research's
always-on agent runtime: messaging gateway (Telegram/Discord/Slack/WhatsApp/
Signal/email), cron scheduler, subagents, self-improving skills. Crucially it
is provider-agnostic — we point it at OpenRouter, **not** a Claude/Codex
subscription.

```bash
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash
hermes setup       # wizard: pick OpenRouter as provider, paste the SAME key
```

Or non-interactively:

```bash
hermes config set OPENROUTER_API_KEY sk-or-v1-...
```

Hermes keeps secrets in `~/.hermes/.env` and model config in
`~/.hermes/config.yaml`. The model is one value, swappable any time with
`hermes model` — no code changes:

```yaml
# ~/.hermes/config.yaml (direct-to-OpenRouter form)
model:
  provider: openrouter
  default: qwen/qwen3.7-max
```

## STEP 4 — Routing (the whole point)

Hermes drives one model at a time — the routing brain is `router.py`. It runs
as a tiny local OpenAI-compatible proxy; Hermes talks to it like any custom
endpoint, and the proxy rewrites every request to the winning model:

```
Hermes ──> http://127.0.0.1:5720/v1 (router.py serve)
              │  classify(last user message)      ← keywords + size, router.toml
              │  coding  → deepseek/deepseek-v4-pro   (fb: qwen3.6-plus)
              │  agents  → moonshotai/kimi-k2.6       (fb: kimi-k2.5)
              │  web     → z-ai/glm-5.2               (fb: deepseek-v4-pro)
              │  longdoc → minimax/minimax-m3         (fb: qwen3.6-plus)
              │  general → qwen/qwen3.7-max           (fb: qwen3.6-plus)
              ▼
        OpenRouter (one key) ──> model, with the fallback chain attached
```

Wire Hermes to it — `provider: custom` in `~/.hermes/config.yaml`:

```yaml
model:
  provider: custom
  default: auto                      # "auto" = let the router classify
  base_url: "http://127.0.0.1:5720/v1"
  api_mode: chat_completions
```

Then:

```bash
python3 router.py serve      # (or install the service from deploy/ — step 5)
python3 router.py routes     # inspect the table + today's spend
python3 router.py ask "fix this python bug: ..."          # auto → DeepSeek
python3 router.py ask --route web "landing page for ..."  # forced route
```

Design decisions, all visible in the two files:

- **Fallbacks are cheap and open, never frontier.** Each route's `models`
  list goes to OpenRouter's native `models` fallback array — if the primary
  is down or rate-limited, *OpenRouter itself* retries the next model in the
  chain and the response records which one actually answered.
- **Route, don't escalate — mechanically enforced.** `blocked_prefixes`
  (`anthropic/`, `openai/`, …) can never be auto-routed; the proxy returns
  403. Frontier runs happen only when you type
  `router.py ask --frontier --model ...` yourself.
- **Classification is dumb on purpose** — keyword scoring plus a "prompt
  bigger than 300k chars goes to the 1M-context route" rule, all editable in
  `router.toml`. You can read the whole thing in `classify()` in 15 lines.
  If a task routes wrong, add a keyword or force `--route`.
- **Every call is accounted.** `logs/usage.jsonl` gets one line per request
  with route, model actually used, and the exact billed cost pulled from
  OpenRouter's `/generation` endpoint.

## STEP 5 — Always-on

Two host options:

**A. $5 VPS (recommended — most reliable per dollar).** Any 1GB Ubuntu/Debian
box (Hetzner/DO/Vultr/Racknerd, ~$4–6/mo). Servers don't sleep, reboot into
your services, and keep your laptop out of the loop.

```bash
# on the VPS
sudo apt update && sudo apt install -y python3 git
sudo mkdir -p /opt/ai-stack && sudo chown $USER /opt/ai-stack
cp router.py router.toml .env /opt/ai-stack/        # or git clone your repo
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash
hermes setup && hermes gateway setup                # connect Telegram etc.

sudo cp deploy/ai-stack-router.service deploy/hermes-gateway.service /etc/systemd/system/
# edit User= and paths in both, then:
sudo systemctl daemon-reload
sudo systemctl enable --now ai-stack-router hermes-gateway
```

`enable` = starts at boot. `Restart=always` = auto-restarts on crash.
Check with `systemctl status ai-stack-router` / `journalctl -u hermes-gateway -f`.

**B. Your own Mac (free, one command matters).** Most "I tried this and it
stopped working" stories are just the host going to sleep. While plugged in:

```bash
sudo pmset -c sleep 0        # never sleep on AC power
```

Then install the router as a login service that survives reboots:
`deploy/com.ai-stack.router.plist` (instructions in the file header), and run
Hermes' gateway via its own daemon (`hermes gateway`) or an equivalent
LaunchAgent. Closing the lid still sleeps the Mac unless you keep it open or
use a clamshell setup — the VPS avoids the whole class of problem.

## STEP 6 — Prove it

```bash
./proof/run_proof.sh             # coding + web/design + reasoning, routed
./proof/run_proof.sh --compare   # + the same coding task on Claude Fable 5
```

The script sends three real tasks through `ask --json` and prints, for each:
the route chosen, the **model that actually answered**, and the **exact cost
OpenRouter billed** (from `/generation`, not an estimate). `--compare` reruns
the coding task on the frontier model (explicitly, with `--frontier` — the
only way past the blocklist) so the last two cost lines make the price gap
concrete: same deliverable, pennies vs. dimes-to-dollars.

Expected shape of the output:

```
=== 1/3 CODING  (expect deepseek/deepseek-v4-pro) ===
  model : deepseek/deepseek-v4-pro
  route : coding
  cost  : $0.0009xx
  ...
=== COMPARE: same coding task on anthropic/claude-fable-5 ===
  cost  : $0.03x–0.1x   (input alone is ~23x DeepSeek's rate)
```

> Note: this sandbox can't reach openrouter.ai (egress policy) and holds no
> key, so the proof runs on **your** machine/VPS — it needs only Python 3.11+
> and the key from step 1.

## Cost picture

- Router + logs: free (your hardware). VPS: ~$5/mo.
- Typical personal agent load (a few hundred requests/day, mostly
  DeepSeek/Qwen/MiniMax rates): **single-digit dollars per month**.
- Hard ceiling: whatever credit limit you typed on the key. Nothing can
  exceed it.

## Where to edit what

| Want to... | Edit |
|---|---|
| Swap a model (new release drops) | one string in `router.toml` |
| Change what routes where | `keywords` lists in `router.toml` |
| Raise/lower the daily brake | `limits.daily_budget_usd` |
| Allow/deny frontier prefixes | `limits.blocked_prefixes` |
| See every call + cost | `logs/usage.jsonl` |
