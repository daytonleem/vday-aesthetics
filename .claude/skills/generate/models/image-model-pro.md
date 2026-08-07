# Nano Banana 2

The full-size sibling of the Lite model. Same reference-image
strength, higher fidelity, higher cost. Only run this after a draft
on `image-model.md` has been picked as the favourite, or when the
job needs a real face/logo reference and the extra accuracy matters
(never describe those in text — pass the file).

## Providers (cheapest first — compare before running)
| Provider | Model ID | ~Cost | API key |
|---|---|---|---|
| Google AI Studio | `gemini-3.1-flash-image-preview` | ~$0.134/image (1K/2K), ~$0.24/image at 4K | `.env` → `GOOGLE_API_KEY` |
| fal.ai | `fal-ai/nano-banana-2` | ~$0.15/image | `.env` → `FAL_KEY` |

Unlike the Lite tier, Google's direct rate tends to be cheaper here
than fal.ai's markup. Default to Google AI Studio; fall back to
fal.ai if it errors or the price has flipped. Verify both before a
large batch.

## Google AI Studio request (default)
Key goes in the URL, not a header.
```
POST https://generativelanguage.googleapis.com/v1beta/models/gemini-3.1-flash-image-preview:generateContent?key={GOOGLE_API_KEY}
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
`candidates[0].content.parts[].inline_data.data`.

## fal.ai request (fallback)
```
curl -X POST https://fal.run/fal-ai/nano-banana-2 \
  -H "Authorization: Key $FAL_KEY" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "<prompt>", "image_urls": ["<reference image URL, if any>"]}'
```
Sync call — image URL comes back in the same response.

## When to use
Final hero shots, anything the client will pick as "the one,"
anything with a real face/logo reference where accuracy matters more
than cost. This is the paid/quality image tier — quote cost if
running more than a couple of variations.
