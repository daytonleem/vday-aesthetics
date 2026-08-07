# Nano Banana 2 Lite

Everyday images. Cheap, fast, strong with reference images. Use this
first for every image request; only escalate to `image-model-pro.md`
once a direction is picked.

## Providers (cheapest first — compare before running)
| Provider | Model ID | ~Cost | API key |
|---|---|---|---|
| fal.ai | `fal-ai/nano-banana-2` (verify the Lite variant slug at fal.ai/models — likely `fal-ai/gemini-3.1-flash-lite-image`) | ~$0.0225/image | `.env` → `FAL_KEY` |
| Google AI Studio | `gemini-3.1-flash-lite-image` | ~$0.034/image | `.env` → `GOOGLE_API_KEY` |

fal.ai has been running cheaper than Google's direct rate for this
model family. Default to fal.ai; fall back to Google AI Studio if
fal.ai errors, lacks the model, or its price has moved. Verify both
before a large batch — these numbers drift.

## fal.ai request (default)
```
curl -X POST https://fal.run/fal-ai/nano-banana-2 \
  -H "Authorization: Key $FAL_KEY" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "<prompt>", "image_urls": ["<reference image URL, if any>"]}'
```
Sync call — the image URL comes back in the same response.

## Google AI Studio request (fallback)
Key goes in the URL, not a header — the one provider here that
works this way.
```
POST https://generativelanguage.googleapis.com/v1beta/models/gemini-3.1-flash-lite-image:generateContent?key={GOOGLE_API_KEY}
```
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
Sync call — base64 image at
`candidates[0].content.parts[].inline_data.data`. Decode and write
to `generations/`.

Add one reference part/URL per logo, face, or style shot instead of
describing it in the prompt text.

## Notes
- If a call returns "model not found," the slug has probably moved
  — check the provider's model list and update this file.
- Not for final faces/logos with tight brand accuracy — use the
  quality tier (`image-model-pro.md`) for anything the client will
  actually pick.
