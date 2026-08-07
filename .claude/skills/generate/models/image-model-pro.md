# Nano Banana 2

The full-size sibling of the Lite model. Same reference-image
strength, higher fidelity, higher cost. Only run this after a draft
on `image-model.md` has been picked as the favourite, or when the
job needs a real face/logo reference and the extra accuracy matters
(never describe those in text — pass the file).

| Field | Value |
|---|---|
| Model ID | `gemini-3.1-flash-image-preview` |
| Provider | Google AI Studio (fallback: fal.ai) |
| Method | Sync (instant reply) |
| Type | Image |
| API key | `.env` → `GOOGLE_API_KEY` (fallback: `FAL_KEY`) |
| Docs | https://ai.google.dev/gemini-api/docs/image-generation |
| Cost | Higher than Lite's ~$0.034/image — check Google AI Studio's pricing page for the current rate before quoting |

## Endpoint (Google AI Studio)
```
POST https://generativelanguage.googleapis.com/v1beta/models/gemini-3.1-flash-image-preview:generateContent?key={GOOGLE_API_KEY}
```

## Request format
Same shape as the Lite model — see `image-model.md` — one
`inline_data` part per reference image, text prompt for everything
that isn't a face/logo.

## Response handling
Sync call — base64 image at
`candidates[0].content.parts[].inline_data.data`. Decode and write
to `generations/`.

## fal.ai request (fallback)
```
curl -X POST https://fal.run/{model-slug} \
  -H "Authorization: Key $FAL_KEY" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "<prompt>"}'
```
Verify the current fal.ai slug at fal.ai/models before running.

## When to use
Final hero shots, anything the client will pick as "the one,"
anything with a real face/logo reference where accuracy matters more
than cost. This is the paid/quality image tier — quote cost if
running more than a couple of variations.
