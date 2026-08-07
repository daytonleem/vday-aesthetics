# GPT Image 2

Text inside images: signs, posters, menus, packaging, UI mockups.
Reach for this the first time a generation needs readable text —
the Nano Banana models are not reliable for in-image text. Pricier
and slower than the defaults, so don't use it out of habit.

| Field | Value |
|---|---|
| Model ID | `openai/gpt-image-2` |
| Provider | fal.ai |
| Method | Sync (instant reply) |
| Type | Image |
| API key | `.env` → `FAL_KEY` |
| Docs | https://fal.ai/models/openai/gpt-image-2 |
| Cost | ~$0.05 per image at medium quality |

Prices/quality tiers drift — confirm on fal.ai's model page before a
large batch.

## Endpoint
```
POST https://fal.run/openai/gpt-image-2
Authorization: Key {FAL_KEY}
Content-Type: application/json
```
To edit an existing image instead of generating fresh, the same
model has an `/edit` variant:
```
POST https://fal.run/openai/gpt-image-2/edit
```

## Request format
```json
{
  "prompt": "<prompt — spell out any exact text that must render>",
  "quality": "medium"
}
```
For `/edit`, add the source image:
```json
{
  "prompt": "<what to change>",
  "image_url": "<source image URL>",
  "quality": "medium"
}
```
If a face or logo appears anywhere in the source image, that's the
reference file — don't describe it in the prompt.

## Response handling
Sync call — the image URL comes back in the same response, at
`images[0].url`. Download and write to `generations/`.

## Notes
- If a call returns "model not found," the slug may have moved —
  check fal.ai/models and update this file.
- `quality` also accepts `low` / `high`; cost scales with it — quote
  before running `high` on a batch.
