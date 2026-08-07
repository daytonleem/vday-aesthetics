# Kling 3.0

General video. The sensible default: good motion, fair price. Every
run through this recipe is a PAID VIDEO RUN — compute the quote
(seconds × rate) and get explicit go-ahead before calling the API.
One approval = one run; re-quote if the prompt or duration changes.

| Field | Value |
|---|---|
| Model ID | `kling-3.0/video` |
| Provider | Kie AI |
| Method | Async (submit, then poll) |
| Type | Video |
| API key | `.env` → `KIE_API_KEY` |
| Docs | https://docs.kie.ai/market/kling/text-to-video |
| Cost | std = 720p, pro = 1080p; 3-15 second clips. Ballpark $0.20-$0.35/second — check kie.ai/pricing for the exact current rate before quoting |

## Endpoint
```
POST https://api.kie.ai/api/v1/jobs/createTask
Authorization: Bearer {KIE_API_KEY}
Content-Type: application/json
```

## Request format
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
For image-to-video, pass the real reference frame via `image_url` —
never describe a face/logo in the prompt text instead.

## Response handling — the async pattern
1. POST the job → the reply contains a `taskId`.
2. Poll the status endpoint every 10-15 seconds, patiently:
   `GET https://api.kie.ai/api/v1/jobs/recordInfo?taskId={taskId}`
3. Status says complete → the reply now contains a result video URL.
4. Download immediately — result URLs often expire in hours.
5. Save into `generations/`, then write the sidecar log.

Getting sync vs. async backwards is the most common reason a first
attempt appears to hang — this model is async, don't wait for an
instant reply.

## When to use
Default video model for everything: before/after animations, social
clips, procedure explainer motion. For higher quality from a start
frame (client-facing hero video), escalate to Veo 3.1 (Google AI
Studio) — quote the higher cost explicitly and get separate approval
before switching models.
