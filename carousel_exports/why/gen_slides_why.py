import os, base64

SLIDES_DIR = "/tmp/vday_carousel/slides_why"
IMG_DIR    = "/tmp/vday_carousel/uploaded_images"

def _b64(fname):
    ext  = fname.split(".")[-1]
    mime = "image/jpeg" if ext in ("jpg","jpeg") else "image/webp" if ext=="webp" else "image/png"
    data = base64.b64encode(open(os.path.join(IMG_DIR, fname), "rb").read()).decode()
    return f"data:{mime};base64,{data}"

TOTAL = 8

def progress_html(active_idx, total=TOTAL):
    segs = []
    for i in range(total):
        cls = "seg"
        if i < active_idx:    cls += " done"
        elif i == active_idx: cls += " active"
        segs.append(f'<div class="{cls}"><div class="fill"></div></div>')
    return f'<div class="progress">{"".join(segs)}</div>'

LOGO   = '<div class="brand-logo"></div>'

_doctor_src = f"data:image/png;base64,{base64.b64encode(open(os.path.join(IMG_DIR,'img_doctor.png'),'rb').read()).decode()}"
_globe_src  = f"data:image/png;base64,{base64.b64encode(open(os.path.join(IMG_DIR,'img_globe.png'),'rb').read()).decode()}"
_plane_src  = f"data:image/png;base64,{base64.b64encode(open(os.path.join(IMG_DIR,'img_plane.png'),'rb').read()).decode()}"
_cursor_src   = f"data:image/png;base64,{base64.b64encode(open(os.path.join(IMG_DIR,'cursor_pixel.png'),'rb').read()).decode()}"
_building_src = _b64('img_building.webp')
_surgeon_src  = _b64('img_surgeon.webp')
_doctor2_src  = _b64('img_doctor2.webp')
FOOTER = '<div class="footer">Vday Aesthetic Concierge&nbsp;&nbsp;&middot;&nbsp;&nbsp;Singapore &ndash; Shanghai</div>'

def wrap(body, slide_cls=""):
    cls = f" {slide_cls}" if slide_cls else ""
    return f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><link rel="stylesheet" href="base.css"></head>
<body><div class="slide{cls}">{LOGO}{body}</div></body></html>"""


# ── Slide 1 — Hook with 3-country table ──────────────────────────────────────
slide1 = wrap(f"""
{progress_html(0)}
<div class="stack rise d1" style="max-width:860px;gap:28px;">
  <div class="eyebrow rise d1">DESTINATION COMPARISON</div>
  <div class="headline rise d2" style="font-size:58px;line-height:1.1;">When the result<br>is your priority,<br><em>you choose Shanghai.</em></div>
  <div class="body-text rise d3" style="font-size:23px;">Here&rsquo;s how the three most popular destinations compare for Asia-Pacific patients.</div>

  <div class="rise d4" style="width:860px;border-radius:16px;overflow:hidden;border:1.5px solid var(--accent-lt);">
    <div style="display:grid;grid-template-columns:1.4fr 1fr 1fr 1fr;background:var(--accent);color:#fff;font-family:var(--font-sans);font-size:14px;font-weight:600;letter-spacing:.07em;text-transform:uppercase;">
      <div style="padding:16px 20px;border-right:1px solid rgba(255,255,255,.2);">Factor</div>
      <div style="padding:16px 12px;border-right:1px solid rgba(255,255,255,.2);text-align:center;">🇨🇳 Shanghai</div>
      <div style="padding:16px 12px;border-right:1px solid rgba(255,255,255,.2);text-align:center;">🇹🇭 Thailand</div>
      <div style="padding:16px 12px;text-align:center;">🇹🇷 Turkey</div>
    </div>
    {"".join([
      f'''<div style="display:grid;grid-template-columns:1.4fr 1fr 1fr 1fr;font-family:var(--font-sans);font-size:15px;color:var(--text);border-top:1px solid var(--accent-lt);background:{bg};">
        <div style="padding:14px 20px;border-right:1px solid var(--accent-lt);font-weight:500;">{factor}</div>
        <div style="padding:14px 12px;border-right:1px solid var(--accent-lt);text-align:center;color:var(--accent);font-weight:700;">{sh}</div>
        <div style="padding:14px 12px;border-right:1px solid var(--accent-lt);text-align:center;color:var(--muted);">{th}</div>
        <div style="padding:14px 12px;text-align:center;color:var(--muted);">{tr}</div>
      </div>'''
      for bg, factor, sh, th, tr in [
        ("var(--bg-mist)", "Technology",     "Very advanced", "Advanced",  "Varies"),
        ("#fff",           "Specialist focus","Dedicated",     "Mixed",     "Mixed"),
        ("var(--bg-mist)", "Surgeon-led",    "Yes",           "Varies",    "Varies"),
        ("#fff",           "Flight from SG", "~5 hrs",        "~2.5 hrs",  "~11 hrs"),
        ("var(--bg-mist)", "Price range",    "$$",            "$$",        "$"),
      ]
    ])}
  </div>
  <div class="body-text rise d5" style="font-size:21px;color:var(--muted);">Swipe to understand why.</div>
</div>
<div class="rise d5" style="position:absolute;bottom:-230px;right:-260px;">
  <img src="{_doctor_src}" style="width:560px;opacity:.95;pointer-events:none;display:block;transform:rotate(-22deg);transform-origin:bottom center;">
</div>
{FOOTER}
""")


# ── Slide 2 — What determines your result ────────────────────────────────────
slide2 = wrap(f"""
{progress_html(1)}
<div class="stack rise d1" style="max-width:860px;gap:28px;">
  <div class="eyebrow rise d1">WHAT ACTUALLY MATTERS</div>
  <div class="headline rise d2" style="font-size:52px;">Three things determine<br>the quality of<br><em>your result.</em></div>

  <div style="display:flex;flex-direction:column;gap:12px;width:860px;" class="rise d3">
    <div style="display:flex;align-items:center;gap:24px;background:var(--accent);border-radius:14px;padding:28px 32px;">
      <div style="width:52px;height:52px;border-radius:50%;background:rgba(255,255,255,.2);display:flex;align-items:center;justify-content:center;font-family:var(--font-sans);font-weight:700;font-size:22px;color:#fff;flex-shrink:0;">1</div>
      <div>
        <div style="font-family:var(--font-sans);font-weight:700;font-size:20px;color:#fff;margin-bottom:4px;">The technology in the operating room</div>
        <div style="font-family:var(--font-sans);font-size:16px;color:rgba(255,255,255,.8);line-height:1.6;">Instruments, magnification, and implantation precision directly affect graft survival.</div>
      </div>
    </div>
    <div style="display:flex;align-items:center;gap:24px;background:var(--accent);border-radius:14px;padding:28px 32px;">
      <div style="width:52px;height:52px;border-radius:50%;background:rgba(255,255,255,.2);display:flex;align-items:center;justify-content:center;font-family:var(--font-sans);font-weight:700;font-size:22px;color:#fff;flex-shrink:0;">2</div>
      <div>
        <div style="font-family:var(--font-sans);font-weight:700;font-size:20px;color:#fff;margin-bottom:4px;">The environment your procedure is done in</div>
        <div style="font-family:var(--font-sans);font-size:16px;color:rgba(255,255,255,.8);line-height:1.6;">A proper surgical hospital operates at a higher standard than a general beauty or cosmetic clinic.</div>
      </div>
    </div>
    <div style="display:flex;align-items:center;gap:24px;background:var(--accent);border-radius:14px;padding:28px 32px;">
      <div style="width:52px;height:52px;border-radius:50%;background:rgba(255,255,255,.2);display:flex;align-items:center;justify-content:center;font-family:var(--font-sans);font-weight:700;font-size:22px;color:#fff;flex-shrink:0;">3</div>
      <div>
        <div style="font-family:var(--font-sans);font-weight:700;font-size:20px;color:#fff;margin-bottom:4px;">Who actually performs the procedure</div>
        <div style="font-family:var(--font-sans);font-size:16px;color:rgba(255,255,255,.8);line-height:1.6;">Your surgeon, not a technician, should be doing the critical steps.</div>
      </div>
    </div>
  </div>

  <div class="body-text rise d4" style="font-size:22px;">Shanghai checks all three.</div>
</div>
{FOOTER}
""")


# ── Slide 3 — Technology ──────────────────────────────────────────────────────
slide3 = wrap(f"""
{progress_html(2)}
<div class="stack rise d1" style="max-width:860px;gap:26px;">
  <div class="eyebrow rise d1">REASON 1 &nbsp;·&nbsp; TECHNOLOGY</div>
  <div class="headline rise d2" style="font-size:54px;">The most advanced<br>surgical technology<br><em>in the region.</em></div>

  <div style="display:flex;gap:12px;width:860px;" class="rise d3">
    <div style="flex:1;border-radius:16px;background:var(--bg-mist);border:1.5px solid var(--accent-lt);padding:26px 22px;display:flex;flex-direction:column;gap:10px;">
      <div style="font-family:var(--font-sans);font-size:13px;font-weight:600;letter-spacing:.08em;text-transform:uppercase;color:var(--muted);">🇹🇭 Thailand</div>
      <div style="font-family:var(--font-sans);font-size:16px;color:var(--text);line-height:1.6;">FUE available. Quality of equipment and technique varies across clinics.</div>
    </div>
    <div style="flex:1;border-radius:16px;background:var(--bg-mist);border:1.5px solid var(--accent-lt);padding:26px 22px;display:flex;flex-direction:column;gap:10px;">
      <div style="font-family:var(--font-sans);font-size:13px;font-weight:600;letter-spacing:.08em;text-transform:uppercase;color:var(--muted);">🇹🇷 Turkey</div>
      <div style="font-family:var(--font-sans);font-size:16px;color:var(--text);line-height:1.6;">FUE widely available. Technology quality varies significantly across hundreds of clinics.</div>
    </div>
    <div style="flex:1;border-radius:16px;background:var(--accent);padding:26px 22px;display:flex;flex-direction:column;gap:10px;">
      <div style="font-family:var(--font-sans);font-size:13px;font-weight:600;letter-spacing:.08em;text-transform:uppercase;color:rgba(255,255,255,.65);">🇨🇳 Shanghai</div>
      <div style="display:flex;flex-direction:column;gap:8px;">
        <div style="font-family:var(--font-sans);font-size:14px;color:#fff;display:flex;align-items:center;gap:8px;"><span style="color:#a8d8b0;">✓</span> Sapphire blades</div>
        <div style="font-family:var(--font-sans);font-size:14px;color:#fff;display:flex;align-items:center;gap:8px;"><span style="color:#a8d8b0;">✓</span> High-powered magnification</div>
        <div style="font-family:var(--font-sans);font-size:14px;color:#fff;display:flex;align-items:center;gap:8px;"><span style="color:#a8d8b0;">✓</span> Refined implantation techniques</div>
        <div style="font-family:var(--font-sans);font-size:14px;color:#fff;display:flex;align-items:center;gap:8px;"><span style="color:#a8d8b0;">✓</span> Precision extraction tools</div>
      </div>
    </div>
  </div>

  <div class="card rise d4" style="width:860px;padding:26px 36px;">
    <div style="font-family:var(--font-sans);font-size:19px;color:var(--text);line-height:1.7;text-align:center;">
      China invested heavily in medical technology over the past decade. The instruments in the room directly affect how many grafts survive and what your result looks like.
    </div>
  </div>
</div>
<img src="{_doctor2_src}" style="position:absolute;bottom:-8px;right:-30px;width:381px;opacity:.92;pointer-events:none;" class="rise d5">
{FOOTER}
""")


# ── Slide 4 — Specialist Focus ────────────────────────────────────────────────
slide4 = wrap(f"""
{progress_html(3)}
<div class="stack rise d1" style="max-width:860px;gap:26px;">
  <div class="eyebrow rise d1">REASON 2 &nbsp;·&nbsp; WHERE YOU GO</div>
  <div class="headline rise d2" style="font-size:52px;">A specialist cosmetic<br>surgery hospital.<br><em>Not a walk-in clinic.</em></div>

  <div style="display:flex;gap:16px;width:860px;align-items:stretch;" class="rise d3">
    <div style="flex:1;border-radius:16px;background:var(--bg-mist);border:1.5px solid var(--accent-lt);padding:32px 28px;display:flex;flex-direction:column;gap:12px;">
      <div style="font-family:var(--font-sans);font-size:13px;font-weight:600;letter-spacing:.1em;text-transform:uppercase;color:var(--muted);">Elsewhere</div>
      <div style="font-family:var(--font-sans);font-size:17px;color:var(--text);line-height:1.65;">Hair transplants carried out at general clinics or beauty-focused centres where surgical standards and oversight can vary widely.</div>
    </div>
    <div style="flex:1;border-radius:16px;background:var(--accent);padding:32px 28px;display:flex;flex-direction:column;gap:12px;">
      <div style="font-family:var(--font-sans);font-size:13px;font-weight:600;letter-spacing:.1em;text-transform:uppercase;color:rgba(255,255,255,.65);">Shanghai with Vday</div>
      <div style="font-family:var(--font-sans);font-size:17px;color:#fff;line-height:1.65;">A proper cosmetic surgery hospital with full surgical infrastructure, anaesthesia support, and trained medical staff. The same environment used for serious surgical procedures.</div>
    </div>
  </div>

  <div class="card rise d4" style="width:860px;padding:28px 40px;">
    <div style="font-family:var(--font-sans);font-size:20px;color:var(--text);line-height:1.7;text-align:center;">
      The hospital environment matters. It sets the standard for how your procedure is carried out.
    </div>
  </div>
</div>
<img src="{_building_src}" class="rise d5" style="position:absolute;bottom:60px;right:40px;width:320px;opacity:.93;pointer-events:none;">
{FOOTER}
""")


# ── Slide 5 — Surgeon-led ─────────────────────────────────────────────────────
slide5 = wrap(f"""
{progress_html(4)}
<div class="stack rise d1" style="max-width:860px;gap:26px;">
  <div class="eyebrow rise d1">REASON 3 &nbsp;·&nbsp; WHO DOES THE WORK</div>
  <div class="headline rise d2" style="font-size:52px;">Your surgeon does<br>the surgery.<br><em>Not a technician.</em></div>

  <div style="width:860px;" class="rise d3">
    <div style="display:flex;flex-direction:column;gap:10px;">
      <div style="border-radius:14px;background:#fff7f0;border:1.5px solid #f0c4a0;padding:28px 32px;">
        <div style="font-family:var(--font-sans);font-size:14px;font-weight:600;letter-spacing:.08em;text-transform:uppercase;color:#a05a20;margin-bottom:10px;">A common concern with some clinics</div>
        <div style="font-family:var(--font-sans);font-size:17px;color:#7a4a20;line-height:1.7;">A surgeon consults, then hands over to a team of technicians who perform extraction and implantation. You don't always know who made the critical decisions about your hairline.</div>
      </div>
      <div style="border-radius:14px;background:var(--accent);padding:28px 32px;">
        <div style="font-family:var(--font-sans);font-size:14px;font-weight:600;letter-spacing:.08em;text-transform:uppercase;color:rgba(255,255,255,.65);margin-bottom:10px;">How reputable Shanghai clinics operate</div>
        <div style="font-family:var(--font-sans);font-size:17px;color:#fff;line-height:1.7;">The lead surgeon designs your hairline, performs extraction, and oversees implantation personally. You know exactly who is responsible for your result.</div>
      </div>
    </div>
  </div>

  <div class="body-text rise d4" style="font-size:21px;color:var(--muted);">Always verify this with your specific clinic.<br>Vday only works with clinics that meet this standard.</div>
</div>
<img src="{_surgeon_src}" class="rise d5" style="position:absolute;bottom:75px;left:40px;width:264px;opacity:.93;pointer-events:none;">
{FOOTER}
""")


# ── Slide 6 — The flight ──────────────────────────────────────────────────────
slide6 = wrap(f"""
{progress_html(5)}
<div class="stack rise d1" style="max-width:860px;gap:26px;">
  <div class="eyebrow rise d1">REASON 4 &nbsp;·&nbsp; ACCESSIBILITY</div>
  <div class="headline rise d2" style="font-size:54px;">A short flight away<br>for most of<br><em>Asia-Pacific.</em></div>
  <div class="body-text rise d3" style="font-size:23px;">Singapore, Malaysia, Australia, Hong Kong, Taiwan, Indonesia. Shanghai is closer than you think.</div>

  <div style="display:flex;flex-direction:column;gap:10px;width:860px;" class="rise d4">
    <div style="display:flex;align-items:center;gap:22px;background:var(--bg-mist);border-radius:14px;padding:22px 30px;border:1.5px solid var(--accent-lt);">
      <div style="font-size:28px;">🇹🇭</div>
      <div style="flex:1;font-family:var(--font-sans);">
        <div style="font-weight:600;font-size:18px;color:var(--text);">Thailand</div>
        <div style="font-size:14px;color:var(--muted);margin-top:2px;">Shortest flight</div>
      </div>
      <div style="font-family:var(--font-sans);font-weight:700;font-size:30px;color:var(--muted);letter-spacing:-.02em;">~2.5 hrs</div>
    </div>
    <div style="display:flex;align-items:center;gap:22px;background:var(--accent);border-radius:14px;padding:22px 30px;">
      <div style="font-size:28px;">🇨🇳</div>
      <div style="flex:1;font-family:var(--font-sans);">
        <div style="font-weight:700;font-size:18px;color:#fff;">Shanghai</div>
        <div style="font-size:14px;color:rgba(255,255,255,.7);margin-top:2px;">Easy to get to from Singapore, Malaysia, Australia, HK</div>
      </div>
      <div style="font-family:var(--font-sans);font-weight:700;font-size:30px;color:#fff;letter-spacing:-.02em;">~5 hrs</div>
    </div>
    <div style="display:flex;align-items:center;gap:22px;background:var(--bg-mist);border-radius:14px;padding:22px 30px;border:1.5px solid var(--accent-lt);">
      <div style="font-size:28px;">🇹🇷</div>
      <div style="flex:1;font-family:var(--font-sans);">
        <div style="font-weight:600;font-size:18px;color:var(--text);">Turkey</div>
        <div style="font-size:14px;color:var(--muted);margin-top:2px;">A full day of travel each way</div>
      </div>
      <div style="font-family:var(--font-sans);font-weight:700;font-size:30px;color:var(--muted);letter-spacing:-.02em;">~11 hrs</div>
    </div>
  </div>
  <div class="body-text rise d5" style="font-size:21px;">No full-day travel. No major time difference. You fly in, get it done, and fly home.</div>
</div>
<style>
@keyframes plane-fly {{
  0%   {{ transform: translate(-920px, 1350px); opacity:0; }}
  6%   {{ opacity:1; }}
  100% {{ transform: translate(0px, 0px); opacity:1; }}
}}
.plane-wrapper {{
  position:absolute; top:60px; right:60px;
  animation: plane-fly 3.8s ease-in-out 0.95s both;
  pointer-events:none;
}}
</style>
<div class="plane-wrapper">
  <img src="{_plane_src}" style="width:220px;display:block;transform:rotate(45deg);">
</div>
{FOOTER}
""")


# ── Slide 7 — Vday vets the clinics ──────────────────────────────────────────
slide7 = wrap(f"""
{progress_html(6)}
<div class="stack rise d1" style="max-width:860px;gap:26px;">
  <div class="eyebrow rise d1">HOW VDAY WORKS</div>
  <div class="headline rise d2" style="font-size:52px;">We&rsquo;ve already vetted<br>the clinics.<br><em>So you don&rsquo;t have to.</em></div>
  <div class="body-text rise d3" style="font-size:23px;">Finding the right clinic in Shanghai takes months of research. We&rsquo;ve done it for you.</div>

  <div style="display:flex;flex-direction:column;gap:12px;width:860px;" class="rise d4">
    <div style="display:flex;align-items:center;gap:20px;background:var(--bg-mist);border-radius:14px;padding:26px 30px;border:1.5px solid var(--accent-lt);">
      <div style="font-size:32px;">🔍</div>
      <div style="font-family:var(--font-sans);">
        <div style="font-weight:600;font-size:18px;color:var(--text);">We only work with surgeon-led clinics</div>
        <div style="font-size:15px;color:var(--muted);margin-top:3px;">Every clinic in our network meets our standard for who performs the critical steps</div>
      </div>
    </div>
    <div style="display:flex;align-items:center;gap:20px;background:var(--bg-mist);border-radius:14px;padding:26px 30px;border:1.5px solid var(--accent-lt);">
      <div style="font-size:32px;">✈️</div>
      <div style="font-family:var(--font-sans);">
        <div style="font-weight:600;font-size:18px;color:var(--text);">We manage the full trip from Singapore</div>
        <div style="font-size:15px;color:var(--muted);margin-top:3px;">Consultation, travel, accommodation, surgery and aftercare. All handled.</div>
      </div>
    </div>
    <div style="display:flex;align-items:center;gap:20px;background:var(--bg-mist);border-radius:14px;padding:26px 30px;border:1.5px solid var(--accent-lt);">
      <div style="font-size:32px;">🤝</div>
      <div style="font-family:var(--font-sans);">
        <div style="font-weight:600;font-size:18px;color:var(--text);">We&rsquo;re with you before, during, and after</div>
        <div style="font-size:15px;color:var(--muted);margin-top:3px;">No navigating a foreign healthcare system alone</div>
      </div>
    </div>
  </div>
</div>
{FOOTER}
""")


# ── Slide 8 — CTA ─────────────────────────────────────────────────────────────

slide8 = wrap(f"""
{progress_html(7)}
<div class="stack rise d1" style="gap:28px;max-width:860px;">
  <div class="eyebrow rise d1">THE BOTTOM LINE</div>

  <div class="card rise d2" style="width:860px;padding:48px 52px;gap:0;">
    <div style="font-family:var(--font-serif);font-size:30px;font-style:italic;color:var(--text);line-height:1.6;text-align:center;">
      &ldquo;Shanghai is where you go<br>when the result is your priority.&rdquo;
    </div>
    <div style="margin-top:24px;font-family:var(--font-sans);font-size:15px;font-weight:600;letter-spacing:.08em;text-transform:uppercase;color:var(--accent);text-align:center;">Vday Aesthetic Concierge</div>
  </div>

  <div class="headline rise d3" style="font-size:46px;max-width:820px;">DM us <em>&ldquo;HAIR&rdquo;</em> to find out<br>if Shanghai is right for you.</div>
  <div class="body-text rise d4" style="font-size:22px;max-width:700px;">We&rsquo;ll assess your hair loss, estimate your graft count, and tell you honestly whether Shanghai is the right call.</div>

  <div style="position:relative;display:inline-block;margin-top:4px;">
    <div class="pill rise d5" id="cta-pill">DM &ldquo;HAIR&rdquo; Now</div>
    <img id="cursor" src="{_cursor_src}" style="position:absolute;width:77px;right:-60px;bottom:-50px;opacity:0;transform:rotate(-30deg) scale(1);transition:opacity 0.12s,transform 0.12s;pointer-events:none;">
  </div>
</div>
<script>
(function() {{
  setTimeout(function() {{
    var pill = document.getElementById('cta-pill');
    var cursor = document.getElementById('cursor');
    function doClick() {{
      cursor.style.opacity = '1';
      setTimeout(function() {{
        cursor.style.transform = 'rotate(-30deg) scale(0.85)';
        pill.classList.add('pill-press');
        setTimeout(function() {{
          cursor.style.transform = 'rotate(-30deg) scale(1)';
          pill.classList.remove('pill-press');
          setTimeout(function() {{
            cursor.style.opacity = '0';
            setTimeout(doClick, 2800);
          }}, 300);
        }}, 350);
      }}, 400);
    }}
    doClick();
  }}, 2200);
}})();
</script>
{FOOTER}
""")


os.makedirs(SLIDES_DIR, exist_ok=True)
for i, s in enumerate([slide1,slide2,slide3,slide4,slide5,slide6,slide7,slide8], start=1):
    with open(os.path.join(SLIDES_DIR, f"slide{i}.html"), "w") as f:
        f.write(s)
print("wrote 8 slides")
