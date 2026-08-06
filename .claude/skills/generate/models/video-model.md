# Video (default) — WAN 2.2 Ultra Fast

Every run through this recipe is a PAID VIDEO RUN. Compute the quote
(seconds × rate) and get explicit go-ahead before calling the API.
One approval = one run — re-quote if the prompt or duration changes.

## Providers, cheapest first
1. **WaveSpeed AI** — WAN 2.2 Ultra Fast — ~$0.01/second of output.
   Cheapest broad video option; verify the exact model slug (e.g.
   `wavespeed-ai/wan-2.2/t2v-ultra-fast` or the current i2v variant)
   at wavespeed.ai/models before running.
2. **Kie AI** — fallback, or deliberate upgrade — aggregates
   Kling/Veo/Seedance too, at a premium vs WAN. Use if WAN is down
   or the shot needs higher fidelity than Ultra Fast delivers.
3. **fal.ai** — fallback if both above fail.

## WaveSpeed AI request
```
curl -X POST https://api.wavespeed.ai/api/v3/wavespeed-ai/wan-2.2/t2v-ultra-fast \
  -H "Authorization: Bearer $WAVESPEED_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "<prompt>",
    "duration": 5,
    "size": "1280*720"
  }'
```
Returns a request id; poll the task-status endpoint until complete,
then download the result URL.

## Kie AI request (fallback / quality upgrade)
```
curl -X POST https://api.kie.ai/api/v1/jobs/createTask \
  -H "Authorization: Bearer $KIE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "wan/t2v",
    "input": {"prompt": "<prompt>", "duration": 5}
  }'
```

## Params worth setting
- `prompt` (required)
- `duration` — seconds; this is what the cost quote is based on, so
  confirm it before running
- `size` — match the target placement (social clip vs site hero)
- for image-to-video, pass the real reference frame — never
  describe a face/logo in the prompt

## When to use
Short before/after animations, social clips, procedure explainer
motion. For client-facing hero video or paid ad creative, escalate
to Kling or Veo via Kie AI — quote the higher cost explicitly and
get separate approval before switching models.
