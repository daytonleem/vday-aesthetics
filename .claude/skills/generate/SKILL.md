---
name: generate
description: Generate images and videos via AI model APIs for the vday-aesthetics site (before/after visuals, hero banners, social clips). Triggers on /generate, generate image, generate video, create image, thumbnail, animate.
---
# /generate

## Models
| Task | Default model | Recipe |
|---|---|---|
| Image (default) | FLUX.1 [schnell] (fal.ai) | models/image-model.md |
| Image (quality) | Nano Banana Pro (Kie AI) | models/image-model-pro.md |
| Video (default) | WAN 2.2 Ultra Fast (WaveSpeed AI) | models/video-model.md |

Read the recipe file before every generation.

## Provider routing
1. Default to the LOWEST COST provider that runs the model well
   (check Kie AI, fal.ai, WaveSpeed AI).
2. If the cheapest route lacks the model, fails auth, or errors,
   fall back to the next provider.
3. Never hide a provider swap. Say which route ran and why.

## Output
- Save every file FLAT into `generations/` at the repo root.
- No subfolders. Reference images live in `generations/refs/`.
- Naming: `{project}_{description}_{timestamp}.{ext}` — project is
  `vday` unless told otherwise, timestamp is `YYYYMMDD-HHMMSS`.

## Credentials
- Keys load from `.env` at the repo root (see `.env.example` for the
  variable names): `KIE_API_KEY`, `FAL_API_KEY`, `WAVESPEED_API_KEY`.
- Never commit `.env`, never print a key value, never paste one into
  a prompt or log.

## Rules
- Quote the cost and wait for my explicit go before any paid
  video run. One approval = one run.
- Draft on the cheap image model first. Only rerun on a quality
  model when I pick a favourite.
- Never describe a logo or face in text. Pass the real image
  file as a reference. If it's missing, stop and ask me for it.
- Run multiple generations one at a time to avoid rate limits.
- After every save, write the sidecar log (see Logging).

## Logging
For every file saved to `generations/`, write a sidecar JSON log
next to it with the same basename: `generations/{basename}.json`.

Fields:
- `file` — the generated filename
- `prompt` — the exact prompt sent
- `model` / `provider` — which recipe and route ran
- `cost_usd` — the quoted/actual cost
- `timestamp` — ISO 8601
- `refs` — reference image paths used, if any (empty list otherwise)

This is the audit trail for spend and provenance. Check it before
re-running a generation so you don't pay twice for the same output.
