# Vday Carousel Production Handoff

## About This Document

Complete reference for carousel production. Vday Aesthetic Concierge is a Singapore-to-Shanghai hair transplant concierge run by Dayton (@daytonleem) and a Shanghai co-founder (@007cnd). They connect Singapore-based clients with specialist cosmetic surgery hospitals in Shanghai for FUE hair transplants at less than half the Singapore price.

**Business constraints -- never violate:**
- Do not mention follow-up care unless the client explicitly requests it.
- The clinic uses no robots. Never say "robotic" or imply automated procedures.
- The facility is a specialist cosmetic surgery hospital, not a hair transplant clinic or centre.
- Do not make it sound like a mass-production hair transplant factory.
- Do not use dashes as em/en dashes in copy. Write "to" or restructure.

---

## 1. Visual Rules

### Canvas
- Width: 1080px
- Height: 1440px (portrait, Meta carousel format)
- Background: #ffffff
- Overflow: hidden (clips decorative cartoons that bleed off-frame)

### Grid
- Padding: 80px top/bottom, 110px left/right
- Content max-width: 860px
- Layout: flex column, align-items center, justify-content center

### Fonts
- Typeface: Jost (loaded via `@import url('jost_embed.css')` at top of base.css)
- CSS variable: `--font` and `--font-sans` both point to `'Jost', system-ui, sans-serif`
- Font roles:
  - Display hook: 800wt, 58-64px, line-height 1.1, with italic `em` for emphasis
  - Headline: 800wt, 46-56px, line-height 1.1 to 1.15
  - Eyebrow: 700wt, 11-13px, uppercase, letter-spacing 0.10em, color var(--accent)
  - Body text: 400wt, 17-22px, line-height 1.7
  - Table/card label: 700wt, 13-15px
  - Caption/handle: 400-500wt, 13-15px, color var(--muted)
  - Price figure: 800wt, 26-32px, font-variant-numeric: tabular-nums
  - Footer: 500wt, 16px, letter-spacing 0.03em

### Colours

| Token | Hex | Usage |
|---|---|---|
| --bg | #ffffff | Slide ground |
| --bg-mist | #f0f7fb | Card backgrounds, table fills |
| --text | #2c2c2c | All primary text |
| --muted | #6b6b6b | Secondary text, captions |
| --accent | #6a9ab0 | Eyebrows, progress bar, CTA pill, table headers |
| --accent-lt | #b8cdd8 | Borders, dividers |
| --line | #e8e8e8 | Horizontal rules |
| #e03030 | (inline only) | Slide 1 hook price: "cost $12k-$16k." only |

### Corner Radius
- CSS variable: `--r: 14px`
- Cards: 14-16px
- CTA pill: 50px (fully rounded)
- Progress bar segments: 2px

### Shadow
- `--shadow: 0 8px 32px -8px rgba(42,60,80,.14)` -- applied to `.card` only

---

## 2. Components

### Progress Bar

```python
def progress_html(active_idx, total=TOTAL):
    segs = []
    for i in range(total):
        cls = "seg"
        if i < active_idx:    cls += " done"
        elif i == active_idx: cls += " active"
        segs.append(f'<div class="{cls}"><div class="fill"></div></div>')
    return f'<div class="progress">{"".join(segs)}</div>'
```

### CTA Pill (slide 5)

```html
<div class="rise d4" style="width:860px;background:var(--accent);border-radius:50px;padding:24px 36px;display:flex;align-items:center;justify-content:center;gap:20px;">
  <img src="{_arrow_green}" style="width:40px;flex-shrink:0;filter:brightness(0) invert(1);animation:bounce-x 1s ease-in-out 1.2s infinite;">
  <span style="font-family:var(--font-sans);font-size:22px;font-weight:700;color:#fff;letter-spacing:.02em;">Press Learn More below to get started</span>
  <img src="{_arrow_green}" style="width:40px;flex-shrink:0;filter:brightness(0) invert(1);animation:bounce-x-rev 1s ease-in-out 1.2s infinite;">
</div>
```

Keyframes injected as `<style>` block inside slide 5's HTML:

```css
@keyframes bounce-x {
  0%,100% { transform: translateX(0); }
  50% { transform: translateX(8px); }
}
@keyframes bounce-x-rev {
  0%,100% { transform: translateX(0); }
  50% { transform: translateX(-8px); }
}
```

### Mascot / Cartoon Placement (CRITICAL PATTERN)

**Never put `transform:rotate()` and the rise animation on the same element.** Use two nested elements:

```html
<div class="rise d5" style="position:absolute;bottom:Ypx;left:Xpx;">
  <img src="..." style="width:510px;display:block;transform:rotate(30deg);transform-origin:bottom center;">
</div>
```

The wrapper div handles position and rise animation only. The inner `img` handles rotation. If rotation is on the wrapper, `translateY` from the rise animation fights the rotation.

---

## 3. Animation System

### Rise Animation

```css
.rise {
  opacity: 0;
  transform: translateY(28px);
  animation: rise 0.65s cubic-bezier(.22,1,.36,1) forwards;
}
@keyframes rise {
  to { opacity: 1; transform: translateY(0); }
}
```

| Class | Delay |
|---|---|
| .d1 | 0.15s |
| .d2 | 0.35s |
| .d3 | 0.55s |
| .d4 | 0.75s |
| .d5 | 0.95s |

### Clip Duration

`DURATION = 3600 + 12000 = 15600ms`

- 3600ms: animation plays (last element finishes at ~1600ms)
- 12000ms: static hold with slide fully visible

### Screenshots -- IMPORTANT

Use **2500ms minimum** wait before screenshots. The d5 element finishes at 950ms delay + 650ms duration = 1600ms. Screenshots taken at 1200ms will miss it.

```javascript
await page.waitForTimeout(2500);
```

---

## 4. Render Scripts

### render_ad.js (5 slides)

```javascript
const { chromium } = require('playwright');
const path = require('path');
const fs   = require('fs');

const BASE     = '/tmp/vday_carousel';
const DURATION = 3600 + 12000;
const OUT_DIR  = path.join(BASE, 'mp4_ad');
fs.mkdirSync(OUT_DIR, { recursive: true });

(async () => {
  const browser = await chromium.launch({
    executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome',
    args: ['--no-sandbox','--disable-setuid-sandbox'],
  });

  for (let i = 1; i <= 5; i++) {
    const tmpDir = path.join(BASE, `_tmp_ad_${i}`);
    fs.mkdirSync(tmpDir, { recursive: true });

    const ctx = await browser.newContext({
      viewport: { width: 1080, height: 1440 },
      recordVideo: { dir: tmpDir, size: { width: 1080, height: 1440 } },
    });
    const page = await ctx.newPage();
    await page.goto(`file://${path.join(BASE, 'slides_ad', `slide${i}.html`)}`, { waitUntil: 'networkidle' });
    await page.waitForTimeout(DURATION);
    await ctx.close();

    const files = fs.readdirSync(tmpDir).filter(f => f.endsWith('.webm'));
    const webm  = path.join(tmpDir, files[0]);
    const mp4   = path.join(OUT_DIR, `slide${i}.mp4`);
    const { execSync } = require('child_process');
    execSync(`ffmpeg -y -i "${webm}" -c:v libx264 -pix_fmt yuv420p -crf 18 -preset medium -movflags +faststart "${mp4}"`, { stdio: 'inherit' });
    fs.rmSync(tmpDir, { recursive: true });
    console.log(`done: slide${i}.mp4`);
  }

  await browser.close();
  console.log('all 5 clips done');
})();
```

FFmpeg: CRF 18, libx264, yuv420p, faststart. Lower CRF = higher quality, larger file.

---

## 5. Ad Carousel Slide Map (5 slides -- FINAL STATE)

### Slide 1 -- Hook

- Eyebrow: "THE REAL NUMBERS"
- Headline d2 (58px): `Hair Transplants in SG` (non-italic, --text color) `<br>` then italic + #e03030: `cost $12k-$16k.`
- Headline d3 (46px): `In Shanghai,` then italic: `everything's included / at less than half the price.`
- Photos grid d4: 2 columns, before_after_male.webp + before_after_female.jpeg, height:530px, object-fit:cover, object-position:center top
- Body text d5: "Real results. Swipe to see why Shanghai makes sense."

**Note on headline styling:** "Hair Transplants in SG" = plain black (not italic, not red). "cost $12k-$16k." = italic em + inline color #e03030. These are two separate lines within the same headline div, split with `<br>`.

### Slide 2 -- Why SG Costs More

- Eyebrow: "WHY SINGAPORE COSTS MORE"
- Headline d2 (46px): `It's not the surgeon. <br><em>It's the overheads.</em>`
- Table d3: "What you're actually paying for in SG" header
  - Row: Orchard Road / CBD clinic rent | $$$
  - Row: Referral & marketing costs | $$
  - Row: Small patient volume, high fixed costs | $$$
  - Row: Consultation fee | Not included
  - Total row (bg-mist): $3-$4/graft x 4,000 grafts | $12,000-$16,000
- Body text d4: "The surgeon is the same quality. You're paying for the postcode."
- Doctor cartoon d5: `doc_thinking.png`, wrapper `bottom:-160px; left:-310px`, img `width:510px; transform:rotate(30deg); transform-origin:bottom center`

### Slide 3 -- Side by Side

- Eyebrow: "SAME PROCEDURE. DIFFERENT PRICE."
- Headline d2 (48px): `Here's what you <br> get for your money.`
- 2-col grid d3:
  - LEFT -- Singapore panel (bg-mist, accent-lt border):
    - Header: "SG Singapore" flag
    - Price section (min-height:66px, flex centered): $12,000-$16,000 (26px 800wt) / "Hair Grafts Only" (12px muted, below)
    - List: Hotel not included / Transfers not included / Medication not included / Consultation not included (all --muted)
  - RIGHT -- Shanghai panel (accent background, white text):
    - Header: "CN Shanghai" flag
    - Price section (min-height:66px, flex centered): TWO columns side by side:
      - Left: $4,888 (26px 800wt #fff) / "(Shaved)" (12px rgba(255,255,255,.7)) below
      - Dash: rgba(255,255,255,.4) 26px
      - Right: $6,688 (26px 800wt #fff) / "(Non-Shaved)" (12px rgba(255,255,255,.7)) below
      - NO "From" label above -- was removed per user request
    - List: Hotel included / Transfers included / Medication included / Consultation included (white)
- Headline d4 (32px, centered): `Less than half the price. <br><em>More included.</em>`
- Doctor cartoon d5: `doc_magnify.png`, wrapper `bottom:-140px; left:-310px`, img `width:510px; transform:rotate(30deg); transform-origin:bottom center`

### Slide 4 -- Trust / Credibility

- Eyebrow: "WHY YOU CAN TRUST THIS"
- Headline d2 (50px): `We flew to Shanghai and <br><em>vetted the clinics ourselves.</em>` (2 lines)
- 2-col photos d3:
  - LEFT: `proc_hairline.webp`, height:430px, object-fit:cover, object-position:center -20px, border-radius:14px, accent-lt border
    - Below: "@daytonleem , co-founder" (15px muted, centered, margin-top:10px)
  - RIGHT: `cofounder_female2.png`, height:430px, object-fit:cover, object-position:center -70px, same border
    - Below: "@007cnd , co-founder" (15px muted, centered, margin-top:10px)
- Trust cards d4 (3 stacked):
  - Hospital emoji + "Only specialist cosmetic surgery hospitals. Not beauty centres or general clinics."
  - Surgeon emoji + "Surgeon-led only. The lead surgeon performs your procedure, not a technician."
  - Plane emoji + "We coordinate everything end to end. You just show up."
- NO footer attribution line ("Dayton, Founder Singapore" was removed)

### Slide 5 -- CTA (Meta Lead Form)

- Inline `<style>` with bounce-x and bounce-x-rev keyframes (before progress bar)
- Eyebrow d1: "TAKES LESS THAN 1 MINUTE"
- Headline d2 (64px): `Find out if FUE <br><em>is right for you.</em>`
- Body text d3 (plain, no card/box): "Takes less than 1 minute. / No commitment. No hard sell." (22px muted, centered)
- CTA pill d4: See CTA Pill component above. Arrows bounce after animation settles.
- The Learn More button is NOT in the HTML. Meta's ad interface provides it. The carousel instructs viewers to press it.

---

## 6. Assets

All source images stored at: `/tmp/vday_carousel/uploaded_images/`
(This is ephemeral -- they must exist before running the generator)

| Filename | Type | Used in | Notes |
|---|---|---|---|
| vday_logo.png | PNG | base.css (embedded as base64) | Brand logo, bottom center every slide |
| before_after_male.webp | WebP | Ad slide 1 left | Before/after male |
| before_after_female.jpeg | JPEG | Ad slide 1 right | Before/after female |
| doc_thinking.png | PNG | Ad slide 2 | Doctor cartoon, hand on chin |
| doc_magnify.png | PNG | Ad slide 3 | Doctor cartoon with magnifying glass |
| proc_hairline.webp | WebP | Ad slide 4 left | Hairline procedure photo |
| cofounder_female2.png | PNG | Ad slide 4 right | Woman co-founder photo. Extracted from conversation JSONL. Must be re-uploaded if lost. |
| arrow_green.webp | WebP | Ad slide 5 | Green arrow, inverted to white via CSS filter |
| img_doctor.png | PNG | Why carousel slide 1 | Main doctor illustration |
| img_doctor2.webp | WebP | Why carousel | Second doctor pose |
| img_building.webp | WebP | Why carousel slide 4 | Hospital building |
| img_surgeon.webp | WebP | Why carousel slide 5 | Surgeon |
| img_plane.png | PNG | Why carousel slide 6 | Plane with fly-in animation |

**cofounder_female2.png recovery:** If lost, extract from the conversation JSONL at `/root/.claude/projects/-home-user-vday-aesthetics/3702fc5f-b2af-559c-b531-8103d82ed441.jsonl`. Parse the JSONL for the last image attachment, decode base64, save as cofounder_female2.png.

Font: `jost_embed.css` -- Jost typeface as a base64 @font-face data URI. Located at `/tmp/vday_carousel/slides_why/jost_embed.css`. Not committed to git. Must exist before generating slides. base.css imports it via `@import url('jost_embed.css')`.

The generator copies base.css from slides_why to slides_ad:
```python
shutil.copy("/tmp/vday_carousel/slides_why/base.css", os.path.join(SLIDES_DIR, "base.css"))
```

---

## 7. What Is Committed vs Final State

The committed `ad_carousel/gen_slides_ad.py` is an **older version**. The committed MP4s also reflect that older version.

### Differences: committed vs final

| Item | Committed | Final (correct) |
|---|---|---|
| Slide 1 headline line 1 | "Hair transplant in SG" | "Hair Transplants in SG" |
| Slide 1 headline line 2 | italic red "costs $12k-$16k." | italic red "cost $12k-$16k." |
| Slide 3 SG label | "Surgery only" | "Hair Grafts Only" |
| Slide 3 Shanghai pricing | "All-in" (single word) | $4,888 (Shaved) / $6,688 (Non-Shaved) with two columns |
| Slide 3 consultation | Not listed | "Consultation not included" (SG), "Consultation included" (Shanghai) |
| Slide 3 doctor | Not in committed | doc_magnify.png, bottom:-140px, left:-310px, 30deg rotation |
| Slide 4 right image | proc_surgery.jpeg | cofounder_female2.png |
| Slide 4 captions | None / "Dayton, Founder Singapore" footer | "@daytonleem , co-founder" and "@007cnd , co-founder" under photos |
| Slide 4 image positions | object-position default | left: center -20px, right: center -70px |
| Slide 5 arrows | Static | bounce-x / bounce-x-rev animation |
| Slide 5 body text | Card-wrapped | Plain body-text div, no card |

**Next step:** Re-generate all 5 slides using the final gen_slides_ad.py (see section 8), render to MP4, commit updated files to `claude/hopeful-cerf-01buv7`.

---

## 8. Final gen_slides_ad.py

The committed version is outdated. The correct final version is below. Save this to `ad_carousel/gen_slides_ad.py` and to `/tmp/vday_carousel/gen_slides_ad.py` before running.

```python
import os, base64, shutil

SLIDES_DIR = "/tmp/vday_carousel/slides_ad"
IMG_DIR    = "/tmp/vday_carousel/uploaded_images"
TOTAL      = 5

os.makedirs(SLIDES_DIR, exist_ok=True)

def _b64(fname):
    ext  = fname.split(".")[-1]
    mime = "image/jpeg" if ext in ("jpg","jpeg") else "image/webp" if ext=="webp" else "image/png"
    data = base64.b64encode(open(os.path.join(IMG_DIR, fname), "rb").read()).decode()
    return f"data:{mime};base64,{data}"

def progress_html(active_idx, total=TOTAL):
    segs = []
    for i in range(total):
        cls = "seg"
        if i < active_idx:    cls += " done"
        elif i == active_idx: cls += " active"
        segs.append(f'<div class="{cls}"><div class="fill"></div></div>')
    return f'<div class="progress">{"".join(segs)}</div>'

LOGO   = '<div class="brand-logo"></div>'
FOOTER = '<div class="footer">Vday Aesthetic Concierge&nbsp;&nbsp;&middot;&nbsp;&nbsp;Singapore &ndash; Shanghai</div>'

_before_after_male   = _b64('before_after_male.webp')
_before_after_female = _b64('before_after_female.jpeg')
_doc_thinking        = _b64('doc_thinking.png')
_doc_magnify         = _b64('doc_magnify.png')
_proc_hairline       = _b64('proc_hairline.webp')
_cofounder_female    = _b64('cofounder_female2.png')
_arrow_green         = _b64('arrow_green.webp')

def wrap(body, slide_cls=""):
    cls = f" {slide_cls}" if slide_cls else ""
    return f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><link rel="stylesheet" href="base.css"></head>
<body><div class="slide{cls}">{LOGO}{body}</div></body></html>"""


# Slide 1 -- Hook
slide1 = wrap(f"""
{progress_html(0)}
<div class="stack rise d1" style="max-width:860px;gap:18px;">
  <div class="eyebrow rise d1">THE REAL NUMBERS</div>
  <div class="headline rise d2" style="font-size:58px;line-height:1.1;">Hair Transplants in SG<br><em><span style="color:#e03030;">cost $12k&ndash;$16k.</span></em></div>
  <div class="headline rise d3" style="font-size:46px;line-height:1.15;">In Shanghai, <em>everything&rsquo;s included<br>at less than half the price.</em></div>
  <div style="display:grid;grid-template-columns:1fr 1fr;gap:14px;width:860px;" class="rise d4">
    <div style="border-radius:14px;overflow:hidden;border:1.5px solid var(--accent-lt);">
      <img src="{_before_after_male}" style="width:100%;display:block;object-fit:cover;height:530px;object-position:center top;">
    </div>
    <div style="border-radius:14px;overflow:hidden;border:1.5px solid var(--accent-lt);">
      <img src="{_before_after_female}" style="width:100%;display:block;object-fit:cover;height:530px;object-position:center top;">
    </div>
  </div>
  <div class="body-text rise d5" style="font-size:20px;color:var(--muted);text-align:center;">Real results. Swipe to see why Shanghai makes sense.</div>
</div>
{FOOTER}
""")


# Slide 2 -- Why SG is expensive
slide2 = wrap(f"""
{progress_html(1)}
<div class="stack rise d1" style="max-width:860px;gap:22px;">
  <div class="eyebrow rise d1">WHY SINGAPORE COSTS MORE</div>
  <div class="headline rise d2" style="font-size:46px;">It&rsquo;s not the surgeon.<br><em>It&rsquo;s the overheads.</em></div>
  <div style="width:860px;border-radius:16px;overflow:hidden;border:1.5px solid var(--accent-lt);" class="rise d3">
    <div style="background:var(--accent);color:#fff;font-family:var(--font-sans);font-size:13px;font-weight:600;letter-spacing:.08em;text-transform:uppercase;padding:16px 28px;">What you&rsquo;re actually paying for in SG</div>
    <div style="display:flex;flex-direction:column;">
      <div style="display:flex;justify-content:space-between;padding:18px 28px;border-bottom:1px solid var(--accent-lt);font-family:var(--font-sans);font-size:18px;color:var(--text);">
        <span>Orchard Road / CBD clinic rent</span><span style="color:var(--accent);font-weight:600;">$$$</span>
      </div>
      <div style="display:flex;justify-content:space-between;padding:18px 28px;border-bottom:1px solid var(--accent-lt);font-family:var(--font-sans);font-size:18px;color:var(--text);">
        <span>Referral &amp; marketing costs</span><span style="color:var(--accent);font-weight:600;">$$</span>
      </div>
      <div style="display:flex;justify-content:space-between;padding:18px 28px;border-bottom:1px solid var(--accent-lt);font-family:var(--font-sans);font-size:18px;color:var(--text);">
        <span>Small patient volume, high fixed costs</span><span style="color:var(--accent);font-weight:600;">$$$</span>
      </div>
      <div style="display:flex;justify-content:space-between;padding:18px 28px;border-bottom:1px solid var(--accent-lt);font-family:var(--font-sans);font-size:18px;color:var(--text);">
        <span>Consultation fee</span><span style="color:var(--accent);font-weight:600;">Not included</span>
      </div>
      <div style="display:flex;justify-content:space-between;padding:18px 28px;background:var(--bg-mist);font-family:var(--font-sans);font-size:19px;font-weight:700;color:var(--text);">
        <span>$3&ndash;$4/graft &times; 4,000 grafts</span><span style="color:var(--accent);">$12,000&ndash;$16,000</span>
      </div>
    </div>
  </div>
  <div class="body-text rise d4" style="font-size:20px;color:var(--muted);">The surgeon is the same quality. You&rsquo;re paying for the postcode.</div>
</div>
<div class="rise d5" style="position:absolute;bottom:-160px;left:-310px;">
  <img src="{_doc_thinking}" style="width:510px;display:block;transform:rotate(30deg);transform-origin:bottom center;">
</div>
{FOOTER}
""")


# Slide 3 -- Side by side
slide3 = wrap(f"""
{progress_html(2)}
<div class="stack rise d1" style="max-width:860px;gap:22px;">
  <div class="eyebrow rise d1">SAME PROCEDURE. DIFFERENT PRICE.</div>
  <div class="headline rise d2" style="font-size:48px;">Here&rsquo;s what you<br>get for your money.</div>
  <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;width:860px;" class="rise d3">
    <div style="border-radius:16px;border:1.5px solid var(--accent-lt);overflow:hidden;">
      <div style="background:var(--bg-mist);padding:16px 24px;text-align:center;font-family:var(--font-sans);font-size:15px;font-weight:700;letter-spacing:.06em;text-transform:uppercase;color:var(--muted);">&#127480;&#127468; Singapore</div>
      <div style="padding:16px 24px;display:flex;flex-direction:column;gap:10px;">
        <div style="text-align:center;min-height:66px;display:flex;flex-direction:column;align-items:center;justify-content:center;">
          <div style="font-family:var(--font-sans);font-size:26px;font-weight:800;color:var(--text);line-height:1.2;">$12,000&ndash;$16,000</div>
          <div style="font-family:var(--font-sans);font-size:12px;color:var(--muted);margin-top:3px;">Hair Grafts Only</div>
        </div>
        <div style="height:1px;background:var(--accent-lt);"></div>
        <div style="font-family:var(--font-sans);font-size:15px;color:var(--muted);line-height:1.8;">Hotel &mdash; not included<br>Transfers &mdash; not included<br>Medication &mdash; not included<br>Consultation &mdash; not included</div>
      </div>
    </div>
    <div style="border-radius:16px;background:var(--accent);overflow:hidden;">
      <div style="padding:16px 24px;text-align:center;font-family:var(--font-sans);font-size:15px;font-weight:700;letter-spacing:.06em;text-transform:uppercase;color:rgba(255,255,255,.7);">&#127464;&#127475; Shanghai</div>
      <div style="padding:16px 24px;display:flex;flex-direction:column;gap:10px;">
        <div style="text-align:center;min-height:66px;display:flex;flex-direction:column;align-items:center;justify-content:center;">
          <div style="display:flex;justify-content:center;gap:20px;">
            <div>
              <div style="font-family:var(--font-sans);font-size:26px;font-weight:800;color:#fff;line-height:1.2;">$4,888</div>
              <div style="font-family:var(--font-sans);font-size:12px;color:rgba(255,255,255,.7);margin-top:3px;">(Shaved)</div>
            </div>
            <div style="font-family:var(--font-sans);font-size:26px;font-weight:800;color:rgba(255,255,255,.4);line-height:1.2;">&ndash;</div>
            <div>
              <div style="font-family:var(--font-sans);font-size:26px;font-weight:800;color:#fff;line-height:1.2;">$6,688</div>
              <div style="font-family:var(--font-sans);font-size:12px;color:rgba(255,255,255,.7);margin-top:3px;">(Non-Shaved)</div>
            </div>
          </div>
        </div>
        <div style="height:1px;background:rgba(255,255,255,.25);"></div>
        <div style="font-family:var(--font-sans);font-size:15px;color:#fff;line-height:1.8;">Hotel included<br>Transfers included<br>Medication included<br>Consultation included</div>
      </div>
    </div>
  </div>
  <div class="headline rise d4" style="font-size:32px;text-align:center;">Less than half the price.<br><em>More included.</em></div>
</div>
<div class="rise d5" style="position:absolute;bottom:-140px;left:-310px;">
  <img src="{_doc_magnify}" style="width:510px;display:block;transform:rotate(30deg);transform-origin:bottom center;">
</div>
{FOOTER}
""")


# Slide 4 -- Trust / credibility
slide4 = wrap(f"""
{progress_html(3)}
<div class="stack rise d1" style="max-width:860px;gap:26px;">
  <div class="eyebrow rise d1">WHY YOU CAN TRUST THIS</div>
  <div class="headline rise d2" style="font-size:50px;">We flew to Shanghai and<br><em>vetted the clinics ourselves.</em></div>
  <div style="display:grid;grid-template-columns:1fr 1fr;gap:14px;width:860px;" class="rise d3">
    <div>
      <div style="border-radius:14px;overflow:hidden;border:1.5px solid var(--accent-lt);">
        <img src="{_proc_hairline}" style="width:100%;display:block;object-fit:cover;height:430px;object-position:center -20px;">
      </div>
      <div style="font-family:var(--font-sans);font-size:15px;color:var(--muted);margin-top:10px;text-align:center;">@daytonleem &nbsp;&middot;&nbsp; co-founder</div>
    </div>
    <div>
      <div style="border-radius:14px;overflow:hidden;border:1.5px solid var(--accent-lt);">
        <img src="{_cofounder_female}" style="width:100%;display:block;object-fit:cover;height:430px;object-position:center -70px;">
      </div>
      <div style="font-family:var(--font-sans);font-size:15px;color:var(--muted);margin-top:10px;text-align:center;">@007cnd &nbsp;&middot;&nbsp; co-founder</div>
    </div>
  </div>
  <div style="display:flex;flex-direction:column;gap:12px;width:860px;" class="rise d4">
    <div style="border-radius:14px;background:var(--bg-mist);border:1.5px solid var(--accent-lt);padding:26px 32px;display:flex;gap:20px;align-items:flex-start;">
      <div style="font-size:28px;flex-shrink:0;">&#127973;</div>
      <div style="font-family:var(--font-sans);font-size:17px;color:var(--text);line-height:1.7;">Only specialist cosmetic surgery hospitals. Not beauty centres or general clinics.</div>
    </div>
    <div style="border-radius:14px;background:var(--bg-mist);border:1.5px solid var(--accent-lt);padding:26px 32px;display:flex;gap:20px;align-items:flex-start;">
      <div style="font-size:28px;flex-shrink:0;">&#128104;&#8205;&#9877;&#65039;</div>
      <div style="font-family:var(--font-sans);font-size:17px;color:var(--text);line-height:1.7;">Surgeon-led only. The lead surgeon performs your procedure, not a technician.</div>
    </div>
    <div style="border-radius:14px;background:var(--bg-mist);border:1.5px solid var(--accent-lt);padding:26px 32px;display:flex;gap:20px;align-items:flex-start;">
      <div style="font-size:28px;flex-shrink:0;">&#9992;&#65039;</div>
      <div style="font-family:var(--font-sans);font-size:17px;color:var(--text);line-height:1.7;">We coordinate everything end to end. You just show up.</div>
    </div>
  </div>
</div>
{FOOTER}
""")


# Slide 5 -- CTA (Meta lead form)
slide5 = wrap(f"""
<style>
@keyframes bounce-x {{
  0%,100% {{ transform: translateX(0); }}
  50% {{ transform: translateX(8px); }}
}}
@keyframes bounce-x-rev {{
  0%,100% {{ transform: translateX(0); }}
  50% {{ transform: translateX(-8px); }}
}}
</style>
{progress_html(4)}
<div class="stack rise d1" style="gap:32px;max-width:860px;">
  <div class="eyebrow rise d1">TAKES LESS THAN 1 MINUTE</div>
  <div class="headline rise d2" style="font-size:64px;line-height:1.1;">Find out if FUE<br><em>is right for you.</em></div>
  <div class="body-text rise d3" style="font-family:var(--font-sans);font-size:22px;color:var(--muted);line-height:1.7;text-align:center;">Takes less than 1 minute.<br>No commitment. No hard sell.</div>
  <div class="rise d4" style="width:860px;background:var(--accent);border-radius:50px;padding:24px 36px;display:flex;align-items:center;justify-content:center;gap:20px;">
    <img src="{_arrow_green}" style="width:40px;flex-shrink:0;filter:brightness(0) invert(1);animation:bounce-x 1s ease-in-out 1.2s infinite;">
    <span style="font-family:var(--font-sans);font-size:22px;font-weight:700;color:#fff;letter-spacing:.02em;">Press Learn More below to get started</span>
    <img src="{_arrow_green}" style="width:40px;flex-shrink:0;filter:brightness(0) invert(1);animation:bounce-x-rev 1s ease-in-out 1.2s infinite;">
  </div>
</div>
{FOOTER}
""")


slides = [slide1, slide2, slide3, slide4, slide5]
shutil.copy(
    "/tmp/vday_carousel/slides_why/base.css",
    os.path.join(SLIDES_DIR, "base.css")
)
for i, s in enumerate(slides, start=1):
    with open(os.path.join(SLIDES_DIR, f"slide{i}.html"), "w") as f:
        f.write(s)
print(f"wrote {len(slides)} slides")
```

---

## 9. How to Regenerate the Ad Carousel

1. Ensure all images are at `/tmp/vday_carousel/uploaded_images/` (upload if missing -- especially `cofounder_female2.png`)
2. Ensure `base.css` and `jost_embed.css` exist at `/tmp/vday_carousel/slides_why/`
3. Create output dirs: `mkdir -p /tmp/vday_carousel/slides_ad /tmp/vday_carousel/mp4_ad`
4. Run: `python3 /tmp/vday_carousel/gen_slides_ad.py`
5. Run: `node /tmp/vday_carousel/render_ad.js`
6. MP4s appear at `/tmp/vday_carousel/mp4_ad/slide{1-5}.mp4`
7. Copy to repo: `cp /tmp/vday_carousel/mp4_ad/slide*.mp4 /home/user/vday-aesthetics/ad_carousel/`
8. Commit and push to branch `claude/hopeful-cerf-01buv7`

---

## 10. Copy Rules

### Tone
- Direct, confident, specific. Lead with the price gap.
- Written from the client's side ("you just show up"), not the business's side.
- Never say "cheap" -- say "less than half the price" or "all-in".
- Active voice throughout.

### Words to Use
- "specialist cosmetic surgery hospital" (not "clinic" or "centre")
- "surgeon-led" (the lead surgeon performs the procedure, not a technician)
- "all-in" for the Shanghai package
- "we coordinate everything end to end"
- "you just show up"
- "FUE" (Follicular Unit Extraction)
- "hair grafts" (not "surgery" when referring to what SG's price covers)

### Words to Avoid
- "cheap", "affordable", "budget"
- "robotic", "automated", "robot-assisted"
- "hair transplant clinic" or "hair transplant centre"
- "follow-up" or "aftercare" (unless client asks)
- Dashes used as punctuation in copy text (use "to" or restructure)
- "guaranteed results" or any outcome guarantee

### Prices
- Singapore: "$12,000 to $16,000" (prose) or "$12k-$16k" (headline shorthand)
- Shanghai shaved: "$4,888"
- Shanghai non-shaved: "$6,688"
- Always include commas in four-figure numbers
- In prose: write "to" not a hyphen

---

## 11. Meta Ad Copy (Final Approved)

**Primary text:**
Hair transplant in Singapore costs $12,000 to $16,000. In Shanghai, the same procedure at a specialist cosmetic surgery hospital is all in at less than half the price. Hotel, transfers, medication all included. We flew there ourselves, vetted the clinics, and coordinate everything end to end. You just show up. Find out if FUE in Shanghai is right for you. Press Learn More

**Headline:** Hair Transplant in Shanghai Less Than Half the Price of SG

**Description:** All-in package. Surgeon-led. We handle everything.

**Alt headlines to test:**
- Save $6,000+ on Your Hair Transplant Here's How
- Same Surgeon Quality. Half the Price. Here's Where.
- Why Singaporeans Are Getting FUE Done in Shanghai

---

## 12. Why Carousel (8 slides -- Earlier Carousel)

Committed at: `carousel_exports/why/`
Generator: `carousel_exports/why/gen_slides_why.py`

Slide map:
1. Hook: "Why Singaporeans fly to Shanghai for hair transplants"
2. Why Shanghai: "Not just price. Quality you can trust."
3. Surgeon quality: "The same surgeon standard. A fraction of the cost."
4. The hospital: "A specialist cosmetic surgery hospital, not a clinic"
5. The procedure: "Surgeon-led FUE from start to finish"
6. The trip: "We coordinate everything. You just show up." (plane flies in)
7. Credibility: "We went there. We vetted it."
8. CTA: "Ready to find out if Shanghai is right for you?"

Plane animation (slide 6):
```css
@keyframes plane-fly {
  0%   { transform: translate(-920px, 1350px); opacity: 0; }
  6%   { opacity: 1; }
  100% { transform: translate(0, 0); opacity: 1; }
}
```
Applied to wrapper div: `animation: plane-fly 3.8s ease-in-out 0.95s both`
Inner img handles rotation -- never on the same element as the animation.
