# Image (default) — FLUX.1 [schnell]

Cheap, fast draft model. Use this first for every image request;
only escalate to `image-model-pro.md` once a direction is picked.

## Providers, cheapest first
1. **fal.ai** — `fal-ai/flux/schnell` — ~$0.003/megapixel (~$0.003
   for a 1024×1024 image). Cheapest and fastest option.
2. **WaveSpeed AI** — `wavespeed-ai/flux/schnell` fallback if fal
   errors or rate-limits — similar price band, verify at
   wavespeed.ai/models before running.
3. **Kie AI** — check kie.ai/pricing for current Flux availability;
   last resort if both above fail.

Prices drift — confirm on the provider's pricing page before a
large batch.

## fal.ai request
```
curl -X POST https://queue.fal.run/fal-ai/flux/schnell \
  -H "Authorization: Key $FAL_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "<prompt>",
    "image_size": "square_hd",
    "num_images": 1,
    "num_inference_steps": 4
  }'
```
Response is a queue handle; poll the returned `status_url` until
`status: COMPLETED`, then fetch `response_url` for the image URLs.

## WaveSpeed AI request (fallback)
```
curl -X POST https://api.wavespeed.ai/api/v3/wavespeed-ai/flux/schnell \
  -H "Authorization: Bearer $WAVESPEED_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "<prompt>", "size": "1024*1024"}'
```

## Params worth setting
- `prompt` (required)
- `image_size` / `size` — match the target placement (hero, card, etc.)
- `seed` — set it when iterating on one composition, so only the
  prompt changes between runs
- `num_images` — keep at 1; loop sequentially per the rate-limit rule

## When to use
Composition drafts, picking a direction, anything the client hasn't
approved yet. Not for final faces/logos — this model doesn't take a
reference image reliably; use the quality model for reference-based
edits.
