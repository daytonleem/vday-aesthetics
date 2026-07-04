#!/usr/bin/env python3
"""
router.py — one small, readable engine that routes each task to the open model
that wins it, all through a single OpenRouter key.

Three commands:

  python3 router.py routes                 # show the routing table
  python3 router.py ask "prompt"           # one-shot: classify -> call -> cost
  python3 router.py serve                  # local OpenAI-compatible proxy for
                                           # Hermes (model "auto" = routed)

No dependencies beyond Python 3.11+ stdlib. Configuration lives in
router.toml next to this file; the API key in $OPENROUTER_API_KEY or ./.env.
Every call is logged to logs/usage.jsonl with the model used and the exact
cost OpenRouter billed (fetched from its /generation endpoint).
"""

import argparse
import json
import os
import re
import sys
import threading
import time
import tomllib
import urllib.error
import urllib.request
from datetime import date
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CONFIG_PATH = ROOT / "router.toml"
LOG_PATH = ROOT / "logs" / "usage.jsonl"


# ---------------------------------------------------------------- config ---

def load_config() -> dict:
    with open(CONFIG_PATH, "rb") as f:
        return tomllib.load(f)


def load_api_key() -> str:
    key = os.environ.get("OPENROUTER_API_KEY", "").strip()
    if not key:
        env_file = ROOT / ".env"
        if env_file.exists():
            for line in env_file.read_text().splitlines():
                line = line.strip()
                if line.startswith("OPENROUTER_API_KEY="):
                    key = line.split("=", 1)[1].strip().strip('"').strip("'")
    if not key:
        sys.exit(
            "No API key. Put OPENROUTER_API_KEY=sk-or-... in the environment "
            f"or in {ROOT / '.env'} (copy .env.example)."
        )
    return key


# --------------------------------------------------------------- routing ---

def classify(text: str, cfg: dict) -> str:
    """Pick a route for a prompt. Deliberately simple and inspectable:
    1. an oversized prompt is forced onto the long-context route;
    2. otherwise the route whose keywords score the most hits wins;
    3. otherwise 'general'."""
    routes = cfg["routes"]
    lowered = text.lower()

    force = routes.get("longdoc", {}).get("force_above_chars")
    if force and len(text) > force:
        return "longdoc"

    best_route, best_score = "general", 0
    for name, route in routes.items():
        score = sum(1 for kw in route.get("keywords", []) if kw in lowered)
        if score > best_score:
            best_route, best_score = name, score
    return best_route


def model_chain(route: str, cfg: dict) -> list[str]:
    return list(cfg["routes"][route]["models"])


def check_frontier(models: list[str], cfg: dict, allow: bool) -> None:
    """'Route, don't escalate': refuse frontier models unless explicitly asked."""
    if allow:
        return
    for m in models:
        for prefix in cfg["limits"]["blocked_prefixes"]:
            if m.startswith(prefix):
                sys.exit(
                    f"Refusing to auto-route to frontier model '{m}'. "
                    "Re-run with --frontier if you really want it."
                )


# ---------------------------------------------------------------- budget ---

def spent_today() -> float:
    """Sum today's logged costs. Best-effort second line of defense —
    the hard credit cap on the OpenRouter key is the real backstop."""
    if not LOG_PATH.exists():
        return 0.0
    today = date.today().isoformat()
    total = 0.0
    for line in LOG_PATH.read_text().splitlines():
        try:
            rec = json.loads(line)
            if rec.get("date") == today:
                total += float(rec.get("cost_usd") or 0)
        except (json.JSONDecodeError, ValueError):
            continue
    return total


def budget_check(cfg: dict) -> None:
    budget = cfg["limits"]["daily_budget_usd"]
    spent = spent_today()
    if spent >= budget:
        sys.exit(
            f"Daily budget hit: ${spent:.4f} spent >= ${budget:.2f} limit "
            "(see logs/usage.jsonl; raise limits.daily_budget_usd to continue)."
        )


def log_usage(record: dict) -> None:
    LOG_PATH.parent.mkdir(exist_ok=True)
    record["date"] = date.today().isoformat()
    record["ts"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    with open(LOG_PATH, "a") as f:
        f.write(json.dumps(record) + "\n")


# ------------------------------------------------------- OpenRouter calls ---

def or_request(path: str, key: str, cfg: dict, payload: dict | None = None):
    url = cfg["openrouter"]["base_url"] + path
    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
        "X-Title": cfg["openrouter"].get("app_name", "ai-stack-router"),
    }
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(url, data=data, headers=headers)
    return urllib.request.urlopen(req, timeout=600)


def fetch_cost(gen_id: str, key: str, cfg: dict) -> dict | None:
    """The exact billed numbers for one generation. The record is written
    asynchronously on OpenRouter's side, so retry briefly."""
    for _ in range(6):
        time.sleep(1.0)
        try:
            with or_request(f"/generation?id={gen_id}", key, cfg) as resp:
                d = json.load(resp)["data"]
                return {
                    "cost_usd": d.get("total_cost"),
                    "tokens_in": d.get("tokens_prompt"),
                    "tokens_out": d.get("tokens_completion"),
                    "model": d.get("model"),
                }
        except urllib.error.HTTPError as e:
            if e.code != 404:  # 404 = not indexed yet, keep retrying
                return None
    return None


def chat(models: list[str], prompt: str, key: str, cfg: dict) -> dict:
    """Non-streaming completion with OpenRouter's native fallback chain:
    `model` is the primary, `models` the ordered fallback list — if the
    primary errors or is rate-limited, OpenRouter retries the next one and
    the response tells us which model actually answered."""
    payload = {
        "model": models[0],
        "models": models,
        "messages": [{"role": "user", "content": prompt}],
    }
    with or_request("/chat/completions", key, cfg, payload) as resp:
        return json.load(resp)


# ------------------------------------------------------------- commands ---

def cmd_routes(_args) -> None:
    cfg = load_config()
    print(f"{'route':<10} {'primary model':<32} fallback")
    print("-" * 78)
    for name, route in cfg["routes"].items():
        models = route["models"]
        fallback = ", ".join(models[1:]) or "-"
        print(f"{name:<10} {models[0]:<32} {fallback}")
    print(f"\nfrontier (manual only): {cfg['limits']['frontier_compare_model']}")
    print(f"daily budget: ${cfg['limits']['daily_budget_usd']:.2f}"
          f"  (spent today: ${spent_today():.4f})")


def cmd_ask(args) -> None:
    cfg = load_config()
    key = load_api_key()
    budget_check(cfg)

    if args.model:
        models = [args.model]
        route = "manual"
    else:
        route = args.route or classify(args.prompt, cfg)
        models = model_chain(route, cfg)
    check_frontier(models, cfg, args.frontier)

    t0 = time.time()
    try:
        resp = chat(models, args.prompt, key, cfg)
    except urllib.error.HTTPError as e:
        sys.exit(f"OpenRouter error {e.code}: {e.read().decode(errors='replace')[:500]}")
    except (urllib.error.URLError, OSError) as e:
        sys.exit(f"Network error reaching OpenRouter: {e}")
    elapsed = time.time() - t0

    answer = resp["choices"][0]["message"]["content"]
    model_used = resp.get("model", models[0])
    cost = fetch_cost(resp.get("id", ""), key, cfg) or {}

    log_usage({
        "route": route,
        "model": cost.get("model") or model_used,
        "cost_usd": cost.get("cost_usd"),
        "tokens_in": cost.get("tokens_in"),
        "tokens_out": cost.get("tokens_out"),
        "gen_id": resp.get("id"),
    })

    if args.json:
        print(json.dumps({
            "route": route,
            "model": cost.get("model") or model_used,
            "cost_usd": cost.get("cost_usd"),
            "tokens_in": cost.get("tokens_in"),
            "tokens_out": cost.get("tokens_out"),
            "seconds": round(elapsed, 1),
            "answer": answer,
        }, indent=2))
    else:
        print(answer)
        cost_str = (f"${cost['cost_usd']:.6f}"
                    if cost.get("cost_usd") is not None else "pending")
        print(f"\n--- route={route} model={cost.get('model') or model_used} "
              f"cost={cost_str} "
              f"tokens={cost.get('tokens_in')}/{cost.get('tokens_out')} "
              f"time={elapsed:.1f}s", file=sys.stderr)


# ---------------------------------------------------------------- server ---
# A tiny OpenAI-compatible proxy. Point Hermes (or anything OpenAI-shaped)
# at http://127.0.0.1:5720/v1 with model "auto": every request is classified
# from its last user message, rewritten to the winning open model (with its
# cheap fallback), forwarded to OpenRouter, and streamed straight back.

class Handler(BaseHTTPRequestHandler):
    server_version = "ai-stack-router/1.0"

    def log_message(self, fmt, *a):  # quieter default logging
        sys.stderr.write("[%s] %s\n" % (time.strftime("%H:%M:%S"), fmt % a))

    def _json(self, code: int, obj: dict) -> None:
        body = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path.rstrip("/").endswith("/models"):
            cfg = load_config()
            names = ["auto"] + list(cfg["routes"].keys())
            self._json(200, {"object": "list", "data": [
                {"id": n, "object": "model", "owned_by": "ai-stack-router"}
                for n in names
            ]})
        else:
            self._json(404, {"error": "not found"})

    def do_POST(self):
        if not self.path.rstrip("/").endswith("/chat/completions"):
            self._json(404, {"error": "not found"})
            return
        cfg = load_config()
        key = load_api_key()

        budget = cfg["limits"]["daily_budget_usd"]
        if spent_today() >= budget:
            self._json(429, {"error": {
                "message": f"ai-stack daily budget (${budget:.2f}) exhausted"}})
            return

        length = int(self.headers.get("Content-Length", 0))
        try:
            payload = json.loads(self.rfile.read(length))
        except json.JSONDecodeError:
            self._json(400, {"error": {"message": "invalid JSON"}})
            return

        # --- route selection -------------------------------------------
        requested = payload.get("model", "auto")
        if requested in cfg["routes"]:                # explicit route name
            route = requested
        elif requested.startswith("auto"):            # "auto" -> classify
            last_user = next(
                (m.get("content", "") for m in reversed(payload.get("messages", []))
                 if m.get("role") == "user"), "")
            if not isinstance(last_user, str):        # multimodal content list
                last_user = json.dumps(last_user)
            route = classify(last_user, cfg)
        else:                                         # explicit model id
            route = None

        if route:
            models = model_chain(route, cfg)
        else:
            models = [requested]
        # The proxy has no --frontier flag on purpose: nothing automated
        # ever escalates. Frontier runs go through `ask --frontier` by hand.
        for m in models:
            if any(m.startswith(p) for p in cfg["limits"]["blocked_prefixes"]):
                self._json(403, {"error": {
                    "message": f"frontier model '{m}' blocked by router policy"}})
                return
        payload["model"] = models[0]
        payload["models"] = models

        # --- forward to OpenRouter, relay bytes back as-is ---------------
        try:
            upstream = or_request("/chat/completions", key, cfg, payload)
        except urllib.error.HTTPError as e:
            self._json(e.code, {"error": {
                "message": e.read().decode(errors="replace")[:500]}})
            return
        except (urllib.error.URLError, OSError) as e:
            self._json(502, {"error": {
                "message": f"network error reaching OpenRouter: {e}"}})
            return

        self.send_response(upstream.status)
        ctype = upstream.headers.get("Content-Type", "application/json")
        self.send_header("Content-Type", ctype)
        self.end_headers()

        first_chunk = b""
        try:
            while True:
                chunk = upstream.read(8192)
                if not chunk:
                    break
                if not first_chunk:
                    first_chunk = chunk
                self.wfile.write(chunk)
                self.wfile.flush()
        except (BrokenPipeError, ConnectionResetError):
            pass
        finally:
            upstream.close()

        # --- cost accounting in the background ---------------------------
        m = re.search(rb'"id"\s*:\s*"(gen-[^"]+)"', first_chunk)
        gen_id = m.group(1).decode() if m else None
        route_name = route or "manual"

        def account():
            cost = fetch_cost(gen_id, key, cfg) if gen_id else None
            log_usage({
                "route": route_name,
                "model": (cost or {}).get("model") or models[0],
                "cost_usd": (cost or {}).get("cost_usd"),
                "tokens_in": (cost or {}).get("tokens_in"),
                "tokens_out": (cost or {}).get("tokens_out"),
                "gen_id": gen_id,
                "via": "serve",
            })

        threading.Thread(target=account, daemon=True).start()


def cmd_serve(args) -> None:
    load_config()   # fail fast on config errors
    load_api_key()  # fail fast on missing key
    addr = (args.host, args.port)
    print(f"ai-stack router listening on http://{addr[0]}:{addr[1]}/v1")
    print('point Hermes at it:  provider: custom, '
          f'base_url: "http://{addr[0]}:{addr[1]}/v1", model: "auto"')
    ThreadingHTTPServer(addr, Handler).serve_forever()


# ------------------------------------------------------------------ main ---

def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("routes", help="show the routing table")

    ask = sub.add_parser("ask", help="one-shot routed request")
    ask.add_argument("prompt")
    ask.add_argument("--route", choices=["coding", "agents", "web", "longdoc",
                                         "general"],
                     help="force a route instead of auto-classifying")
    ask.add_argument("--model", help="force an exact OpenRouter model id")
    ask.add_argument("--frontier", action="store_true",
                     help="explicitly allow a frontier (blocked-prefix) model")
    ask.add_argument("--json", action="store_true",
                     help="machine-readable output (used by the proof script)")

    srv = sub.add_parser("serve", help="run the local OpenAI-compatible proxy")
    srv.add_argument("--host", default="127.0.0.1")
    srv.add_argument("--port", type=int, default=5720)

    args = p.parse_args()
    {"routes": cmd_routes, "ask": cmd_ask, "serve": cmd_serve}[args.cmd](args)


if __name__ == "__main__":
    main()
