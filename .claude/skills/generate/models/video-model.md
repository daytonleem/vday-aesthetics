# Kling 3.0

General video. The sensible default: good motion, fair price. Every
run through this recipe is a PAID VIDEO RUN — compute the quote
(seconds × rate) and get explicit go-ahead before calling the API.
One approval = one run; re-quote if the prompt or duration changes.

## Providers (cheapest first — compare before running)
| Provider | Model ID | ~Cost | API key | Method |
|---|---|---|---|---|
| fal.ai | `fal-ai/kling-video/v3/standard/text-to-video` (pro: `.../v3/pro/text-to-video`) | reported as low as ~$0.03/sec std, ~$0.08-0.11/sec std/pro elsewhere — figures conflict, verify at fal.ai/pricing | `.env` → `FAL_KEY` | Async (queue) |
| Kie AI | `kling-3.0/video` | ~$0.07/sec std (std=720p, pro=1080p), 3-15s clips | `.env` → `KIE_API_KEY` | Async (poll) |
| WaveSpeed AI | check wavespeed.ai/collections/kling for current slug | ~$0.15/sec | `.env` → `WAVESPEED_API_KEY` | Async (poll) |

Kling pricing is reported inconsistently across sources — this is
the one model where you should actually check the live pricing page
before quoting, not just trust the table above. WaveSpeed has
consistently priced highest for Kling specifically (it's the better
route for other models like WAN, just not this one).

## fal.ai request (default)
```
curl -X POST https://queue.fal.run/fal-ai/kling-video/v3/standard/text-to-video \
  -H "Authorization: Key $FAL_KEY" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "<prompt>", "duration": "5", "image_url": "<reference frame URL, for image-to-video>"}'
```
Returns a queue handle — poll the `status_url` until `COMPLETED`,
then fetch `response_url` for the video URL. Download immediately;
result URLs often expire in hours.

## Kie AI request (fallback)
```
POST https://api.kie.ai/api/v1/jobs/createTask
Authorization: Bearer {KIE_API_KEY}
Content-Type: application/json
```
```json
{
  "model": "kling-3.0/video",
  "input": {
    "prompt": "<prompt>",
    "duration": 5,
    "quality": "std",
    "image_url": "<reference frame URL, for image-to-video>"
  }
}
```
Poll `https://api.kie.ai/api/v1/jobs/recordInfo?taskId={taskId}`
every 10-15 seconds until complete, then download the result URL.

For image-to-video on either provider, pass the real reference frame
via `image_url` — never describe a face/logo in the prompt text
instead.

## When to use
Default video model for everything: before/after animations, social
clips, procedure explainer motion. For higher quality from a start
frame (client-facing hero video), escalate to Veo 3.1 (Google AI
Studio) — quote the higher cost explicitly and get separate approval
before switching models.
