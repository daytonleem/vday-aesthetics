---
name: generate
description: Generate images and videos via AI model APIs for the vday-aesthetics site (before/after visuals, hero banners, social clips). Triggers on /generate, generate image, generate video, create image, thumbnail, animate.
---
# /generate

## Models
| Task | Default model | Recipe |
|---|---|---|
| Image (default) | Nano Banana 2 Lite (Google AI Studio) | models/image-model.md |
| Image (quality) | Nano Banana 2 (Google AI Studio) | models/image-model-pro.md |
| Image (text-in-image) | GPT Image 2 (fal.ai) | models/image-model-text.md |
| Video (default) | Kling 3.0 (Kie AI) | models/video-model.md |

Use GPT Image 2 instead of the defaults whenever the image needs
legible text baked in — signs, posters, menus, packaging, UI
mockups. Nano Banana isn't reliable for in-image text.

Read the recipe file before every generation.

## Provider routing
1. Each recipe lists every provider you hold a key for that can run
   that model, cheapest-known-first. Use the top one by default.
2. Those prices are ballparks and drift — for anything beyond a
   quick draft (a paid video run, or a batch), verify current price
   at the provider's pricing page before running, since ordering can
   flip between tiers (e.g. fal.ai is cheaper than Google AI Studio
   for the default image tier, but Google is cheaper for the quality
   tier — don't assume one provider wins across the board).
3. If the cheapest route lacks the model, fails auth, or errors,
   fall back to the next one down the list.
4. Never hide a provider swap or a cheaper-alternative check. Say
   which route ran and why.

## Output
- Save every file FLAT into `generations/` at the repo root.
- No subfolders. Reference images live in `generations/refs/`.
- Naming: `{project}_{description}_{timestamp}.{ext}` — project is
  `vday` unless told otherwise, timestamp is `YYYYMMDD-HHMMSS`.

## Credentials
- Keys load from `.env` at the repo root (see `.env.example` for the
  variable names): `KIE_API_KEY`, `FAL_KEY`, `WAVESPEED_API_KEY`,
  `GOOGLE_API_KEY`.
- Never commit `.env`, never print a key value, never paste one into
  a prompt or log.
- Each provider authenticates differently — get this right once per
  provider and every model on it works:
  - **Google AI Studio** — key goes in the URL: `...?key={GOOGLE_API_KEY}`
  - **fal.ai** — header `Authorization: Key {FAL_KEY}`
  - **Kie AI** — header `Authorization: Bearer {KIE_API_KEY}`
  - **WaveSpeed AI** — header `Authorization: Bearer {WAVESPEED_API_KEY}`

## Rules
- Quote the cost and wait for my explicit go before any paid
  video run. One approval = one run.
- Draft on the cheap image model first. Only rerun on a quality
  model when I pick a favourite.
- Never describe a logo or face in text. Pass the real image
  file as a reference. If it's missing, stop and ask me for it.
- Run multiple generations one at a time to avoid rate limits.
- Sync models (Nano Banana, GPT Image, Seedance) return the result
  in one call. Async models (Kling, Veo) return a task id — poll the
  status endpoint every 10-15 seconds until it says done, then
  download immediately (result URLs often expire in hours). Check
  each recipe's Method field before assuming which one a model uses.
- After every save, write the sidecar log (see Logging).

## Ballpark costs
Draft image: $0.01-$0.03. Quality image: $0.05-$0.15. Video: $0.20-
$0.35/second (a 10s clip is $2-$3.50 — this is why the video cost
gate exists). Prices move fast — check the provider's pricing page
before relying on these.

## Logging
For every file saved to `generations/`, write a sidecar JSON log
next to it with the same basename: `generations/{basename}.json`.

```json
{
  "model": "the-model-id",
  "provider": "kie-ai | fal-ai | wavespeed | google-ai-studio",
  "prompt": "the full text prompt that was sent to the API",
  "refs": ["refs/logo.png", "refs/headshot.jpg"],
  "params": { "aspect": "16:9", "size": "2K" },
  "cost_usd": 0.03,
  "created": "2026-08-07T09:41:00Z"
}
```

This is the audit trail for spend and provenance. Check it before
re-running a generation so you don't pay twice for the same output.
