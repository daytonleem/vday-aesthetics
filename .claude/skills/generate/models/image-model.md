# Nano Banana 2 Lite

Everyday images. Cheap, fast, strong with reference images. Use this
first for every image request; only escalate to `image-model-pro.md`
once a direction is picked.

| Field | Value |
|---|---|
| Model ID | `gemini-3.1-flash-lite-image` |
| Provider | Google AI Studio (fallback: fal.ai) |
| Method | Sync (instant reply) |
| Type | Image |
| API key | `.env` → `GOOGLE_API_KEY` (fallback: `FAL_KEY`) |
| Docs | https://ai.google.dev/gemini-api/docs/image-generation |
| Cost | ~$0.034 per image at 1K resolution |

Prices drift — confirm on the provider's pricing page before a
large batch.

## Endpoint (Google AI Studio)
```
POST https://generativelanguage.googleapis.com/v1beta/models/gemini-3.1-flash-lite-image:generateContent?key={GOOGLE_API_KEY}
```
Google AI Studio puts the key in the URL, not a header — the one
provider here that works this way.

## Request format
```json
{
  "contents": [{
    "parts": [
      { "text": "<prompt>" },
      { "inline_data": { "mime_type": "image/png", "data": "<base64 reference image, if any>" } }
    ]
  }]
}
```
Add one `inline_data` part per reference image (logo, face, style
shot) instead of describing it in the prompt text.

## Response handling
Sync call — the image comes back in the same response, base64-
encoded at `candidates[0].content.parts[].inline_data.data`. Decode
and write it straight to `generations/`.

## fal.ai request (fallback)
```
curl -X POST https://fal.run/{model-slug} \
  -H "Authorization: Key $FAL_KEY" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "<prompt>"}'
```
Look up the current fal.ai slug for this model at fal.ai/models
before running — verify it hasn't changed.

## Notes
- If a call returns "model not found," the id has probably been
  bumped — check Google AI Studio's model list and update this file.
- Not for final faces/logos with tight brand accuracy — use the
  quality tier (`image-model-pro.md`) for anything the client will
  actually pick.
