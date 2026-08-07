# GPT Image 2

Text inside images: signs, posters, menus, packaging, UI mockups.
Reach for this the first time a generation needs readable text —
the Nano Banana models are not reliable for in-image text. Pricier
and slower than the defaults, so don't use it out of habit.

## Providers (cheapest first — compare before running)
| Provider | Model ID | ~Cost | API key |
|---|---|---|---|
| fal.ai | `openai/gpt-image-2` | $0.01 (low) to $0.41 (4K high); ~$0.05 at medium | `.env` → `FAL_KEY` |
| Kie AI | `gpt-image-2` (verify exact id at kie.ai) | $0.04 (low) / $0.09 (medium) / $0.23 (high) pay-as-you-go | `.env` → `KIE_API_KEY` |

fal.ai's pay-as-you-go tiers run cheaper than Kie AI's at every
quality level on our plan (Kie AI only undercuts fal.ai on a $199/mo
committed plan, which we're not on). Default to fal.ai; Kie AI is a
fallback if fal.ai errors or lacks the model.

## fal.ai request (default)
```
POST https://fal.run/openai/gpt-image-2
Authorization: Key {FAL_KEY}
Content-Type: application/json
```
```json
{
  "prompt": "<prompt — spell out any exact text that must render>",
  "quality": "medium"
}
```
To edit an existing image instead of generating fresh:
```
POST https://fal.run/openai/gpt-image-2/edit
```
```json
{
  "prompt": "<what to change>",
  "image_url": "<source image URL>",
  "quality": "medium"
}
```
Sync call — image URL comes back at `images[0].url`.

If a face or logo appears anywhere in the source image, that's the
reference file — don't describe it in the prompt.

## Kie AI request (fallback)
```
curl -X POST https://api.kie.ai/api/v1/jobs/createTask \
  -H "Authorization: Bearer $KIE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model": "gpt-image-2", "input": {"prompt": "<prompt>", "quality": "medium"}}'
```
Async — poll `https://api.kie.ai/api/v1/jobs/recordInfo?taskId={taskId}`
until complete, then download the result URL.

## Notes
- If a call returns "model not found," the slug may have moved —
  check fal.ai/models or kie.ai and update this file.
- `quality` also accepts `low` / `high`; cost scales with it — quote
  before running `high` on a batch.
