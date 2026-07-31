import os, base64

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

_doctor_src         = _b64('img_doctor.png')
_before_after_male  = _b64('before_after_male.webp')
_before_after_female= _b64('before_after_female.jpeg')
_doc_thinking       = _b64('doc_thinking.png')
_doc_magnify        = _b64('doc_magnify.png')
_proc_hairline      = _b64('proc_hairline.webp')
_proc_surgery       = _b64('proc_surgery.jpeg')
_arrow_green        = _b64('arrow_green.webp')

def wrap(body, slide_cls=""):
    cls = f" {slide_cls}" if slide_cls else ""
    return f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><link rel="stylesheet" href="base.css"></head>
<body><div class="slide{cls}">{LOGO}{body}</div></body></html>"""


# ── Slide 1 — Hook ────────────────────────────────────────────────────────────
slide1 = wrap(f"""
{progress_html(0)}
<div class="stack rise d1" style="max-width:860px;gap:18px;">
  <div class="eyebrow rise d1">THE REAL NUMBERS</div>
  <div class="headline rise d2" style="font-size:58px;line-height:1.1;">Hair transplant in SG<br><em><span style="color:#e03030;">costs $12k–$16k.</span></em></div>
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


# ── Slide 2 — Why SG is expensive ────────────────────────────────────────────
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
        <span>$3–$4/graft &times; 4,000 grafts</span><span style="color:var(--accent);">$12,000–$16,000</span>
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


# ── Slide 3 — Side by side ────────────────────────────────────────────────────
slide3 = wrap(f"""
{progress_html(2)}
<div class="stack rise d1" style="max-width:860px;gap:22px;">
  <div class="eyebrow rise d1">SAME PROCEDURE. DIFFERENT PRICE.</div>
  <div class="headline rise d2" style="font-size:48px;">Here&rsquo;s what you<br>get for your money.</div>

  <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;width:860px;" class="rise d3">
    <div style="border-radius:16px;border:1.5px solid var(--accent-lt);overflow:hidden;">
      <div style="background:var(--bg-mist);padding:20px 24px;text-align:center;font-family:var(--font-sans);font-size:15px;font-weight:700;letter-spacing:.06em;text-transform:uppercase;color:var(--muted);">🇸🇬 Singapore</div>
      <div style="padding:20px 24px;display:flex;flex-direction:column;gap:10px;">
        <div style="font-family:var(--font-sans);font-size:32px;font-weight:800;color:var(--text);text-align:center;">$12,000–$16,000</div>
        <div style="height:1px;background:var(--accent-lt);"></div>
        <div style="font-family:var(--font-sans);font-size:16px;color:var(--text);line-height:1.7;">Surgery only<br><span style="color:var(--muted);">Hotel — not included</span><br><span style="color:var(--muted);">Transfers — not included</span><br><span style="color:var(--muted);">Medication — not included</span></div>
      </div>
    </div>
    <div style="border-radius:16px;background:var(--accent);overflow:hidden;">
      <div style="padding:20px 24px;text-align:center;font-family:var(--font-sans);font-size:15px;font-weight:700;letter-spacing:.06em;text-transform:uppercase;color:rgba(255,255,255,.7);">🇨🇳 Shanghai</div>
      <div style="padding:20px 24px;display:flex;flex-direction:column;gap:10px;">
        <div style="font-family:var(--font-sans);font-size:36px;font-weight:800;color:#fff;text-align:center;">All-in</div>
        <div style="height:1px;background:rgba(255,255,255,.25);"></div>
        <div style="font-family:var(--font-sans);font-size:16px;color:#fff;line-height:1.7;">Surgery included<br>Hotel included<br>Airport transfers included<br>Medication included</div>
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


# ── Slide 4 — Trust / credibility ────────────────────────────────────────────
slide4 = wrap(f"""
{progress_html(3)}
<div class="stack rise d1" style="max-width:860px;gap:26px;">
  <div class="eyebrow rise d1">WHY YOU CAN TRUST THIS</div>
  <div class="headline rise d2" style="font-size:50px;">We flew to Shanghai and<br><em>vetted the clinics ourselves.</em></div>

  <div style="display:grid;grid-template-columns:1fr 1fr;gap:14px;width:860px;" class="rise d3">
    <div style="border-radius:14px;overflow:hidden;border:1.5px solid var(--accent-lt);">
      <img src="{_proc_hairline}" style="width:100%;display:block;object-fit:cover;height:430px;object-position:center top;">
    </div>
    <div style="border-radius:14px;overflow:hidden;border:1.5px solid var(--accent-lt);">
      <img src="{_proc_surgery}" style="width:100%;display:block;object-fit:cover;height:430px;object-position:calc(50% - 50px) center;">
    </div>
  </div>

  <div style="display:flex;flex-direction:column;gap:12px;width:860px;" class="rise d4">
    <div style="border-radius:14px;background:var(--bg-mist);border:1.5px solid var(--accent-lt);padding:26px 32px;display:flex;gap:20px;align-items:flex-start;">
      <div style="font-size:28px;flex-shrink:0;">🏥</div>
      <div style="font-family:var(--font-sans);font-size:17px;color:var(--text);line-height:1.7;">Only specialist cosmetic surgery hospitals. Not beauty centres or general clinics.</div>
    </div>
    <div style="border-radius:14px;background:var(--bg-mist);border:1.5px solid var(--accent-lt);padding:26px 32px;display:flex;gap:20px;align-items:flex-start;">
      <div style="font-size:28px;flex-shrink:0;">👨‍⚕️</div>
      <div style="font-family:var(--font-sans);font-size:17px;color:var(--text);line-height:1.7;">Surgeon-led only. The lead surgeon performs your procedure, not a technician.</div>
    </div>
    <div style="border-radius:14px;background:var(--bg-mist);border:1.5px solid var(--accent-lt);padding:26px 32px;display:flex;gap:20px;align-items:flex-start;">
      <div style="font-size:28px;flex-shrink:0;">✈️</div>
      <div style="font-family:var(--font-sans);font-size:17px;color:var(--text);line-height:1.7;">We coordinate everything end to end. You just show up.</div>
    </div>
  </div>
  <div class="body-text rise d5" style="font-size:20px;color:var(--muted);">Dayton, Founder &nbsp;·&nbsp; Singapore</div>
</div>
{FOOTER}
""")


# ── Slide 5 — CTA (Meta lead form) ───────────────────────────────────────────
slide5 = wrap(f"""
{progress_html(4)}
<div class="stack rise d1" style="gap:32px;max-width:860px;">
  <div class="eyebrow rise d1">TAKES LESS THAN 1 MINUTE</div>

  <div class="headline rise d2" style="font-size:64px;line-height:1.1;">Find out if FUE<br><em>is right for you.</em></div>

  <div class="body-text rise d3" style="font-family:var(--font-sans);font-size:22px;color:var(--muted);line-height:1.7;text-align:center;">Takes less than 1 minute.<br>No commitment. No hard sell.</div>

  <div class="rise d4" style="width:860px;background:var(--accent);border-radius:50px;padding:24px 36px;display:flex;align-items:center;justify-content:center;gap:20px;">
    <img src="{_arrow_green}" style="width:40px;flex-shrink:0;filter:brightness(0) invert(1);">
    <span style="font-family:var(--font-sans);font-size:22px;font-weight:700;color:#fff;letter-spacing:.02em;">Press Learn More below to get started</span>
    <img src="{_arrow_green}" style="width:40px;flex-shrink:0;filter:brightness(0) invert(1);">
  </div>
</div>
{FOOTER}
""")



slides = [slide1, slide2, slide3, slide4, slide5]
import shutil
shutil.copy(
    "/tmp/vday_carousel/slides_why/base.css",
    os.path.join(SLIDES_DIR, "base.css")
)
for i, s in enumerate(slides, start=1):
    path = os.path.join(SLIDES_DIR, f"slide{i}.html")
    with open(path, "w") as f:
        f.write(s)
print(f"wrote {len(slides)} slides")
