# Image (quality) — Nano Banana Pro

Reference-faithful hero/final model. Only run this after a draft on
the cheap model has been picked as the favourite, or when the job
requires a real face/logo reference (never describe those in text —
pass the file).

## Providers, cheapest first
1. **Kie AI** — aggregates Nano Banana Pro at a discount vs Google's
   direct pricing. Check kie.ai/pricing for the current per-image
   rate before quoting cost.
2. **fal.ai** — `fal-ai/nano-banana-pro` fallback if Kie AI errors
   or lacks the model. Verify the exact model slug at fal.ai/models
   before running — these get renamed.
3. **WaveSpeed AI** — last-resort fallback if both above fail.

## Why this model for this project
Best-in-class reference-image fidelity: feed it a real before/after
photo, logo, or face and it preserves identity instead of
hallucinating a new one. That's the only acceptable way to handle
faces/logos under the project rules.

## Kie AI request
```
curl -X POST https://api.kie.ai/api/v1/jobs/createTask \
  -H "Authorization: Bearer $KIE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "google/nano-banana-pro",
    "input": {
      "prompt": "<prompt>",
      "image_urls": ["<reference image URL(s)>"]
    }
  }'
```
Returns a `taskId`; poll the get-task-detail endpoint
(`https://api.kie.ai/api/v1/jobs/recordInfo?taskId=...`) until the
state is complete, then download the result URL.

## fal.ai request (fallback)
```
curl -X POST https://queue.fal.run/fal-ai/nano-banana-pro \
  -H "Authorization: Key $FAL_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "<prompt>", "image_urls": ["<reference image URL>"]}'
```

## Params worth setting
- `prompt` (required)
- `image_urls` — the real reference file(s); upload to a reachable
  URL first if the provider needs one rather than a raw upload
- keep batches to 1 at a time per the rate-limit rule

## When to use
Final hero shots, anything the client will pick as "the one,"
anything with a real face/logo reference. This is the paid/quality
tier for images — quote cost if running more than a couple of
variations, though it doesn't need the video approval gate.
