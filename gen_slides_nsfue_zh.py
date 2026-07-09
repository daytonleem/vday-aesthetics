import os, base64

SLIDES_DIR = "/tmp/vday_carousel/slides_nsfue_zh"
IMG_DIR    = "/tmp/vday_carousel/uploaded_images"
TOTAL = 8

def progress_html(active_idx, total=TOTAL, alt=False):
    segs = []
    for i in range(total):
        cls = "seg"
        if i < active_idx:   cls += " done"
        elif i == active_idx: cls += " active"
        segs.append(f'<div class="{cls}"><div class="fill"></div></div>')
    alt_cls = " alt" if alt else ""
    return f'<div class="progress{alt_cls}">{"".join(segs)}</div>'

LOGO   = '<div class="brand-logo"></div>'
FOOTER = '<div class="footer">Vday Aesthetic Concierge&nbsp;&nbsp;&middot;&nbsp;&nbsp;新加坡 &ndash; 上海</div>'

def wrap(body, slide_cls=""):
    cls = f" {slide_cls}" if slide_cls else ""
    return f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><link rel="stylesheet" href="base.css"></head>
<body><div class="slide{cls}">{LOGO}{body}</div></body></html>"""

def _b64(fname):
    ext = fname.split(".")[-1]
    mime = "image/jpeg" if ext in ("jpg","jpeg") else "image/webp" if ext=="webp" else "image/png"
    data = base64.b64encode(open(os.path.join(IMG_DIR, fname), "rb").read()).decode()
    return f"data:{mime};base64,{data}"

# ── Slide 1 — Hook ─────────────────────────────────────────────────────────
_s1_top = _b64("nsfue_img1_top.jpeg")
_s1_bot = _b64("nsfue_img1_bot.jpeg")

slide1 = wrap(f"""
{progress_html(0)}
<div class="stack rise d1" style="max-width:880px;gap:20px;">
  <div class="eyebrow rise d1">另一种选择</div>
  <div class="headline rise d2" style="font-size:62px;">你不需要<br>剃光头。</div>
  <div class="rise d3" style="display:flex;gap:14px;width:880px;height:400px;">
    <div style="flex:1;border-radius:14px;overflow:hidden;height:400px;box-shadow:0 10px 40px -10px rgba(42,60,80,.12);">
      <img src="{_s1_top}" style="width:100%;height:400px;object-fit:cover;object-position:center top;display:block;">
    </div>
    <div style="flex:1;border-radius:14px;overflow:hidden;height:400px;box-shadow:0 10px 40px -10px rgba(42,60,80,.12);">
      <img src="{_s1_bot}" style="width:100%;height:400px;object-fit:cover;object-position:center top;display:block;">
    </div>
  </div>
  <div class="body-text rise d4" style="font-size:28px;margin-top:4px;">很多人以为必须剃头。其实不是。<br>往下看，了解免剃发FUE的原理。</div>
</div>
{FOOTER}
""")

# ── Slide 2 — What is Non-Shave FUE? ──────────────────────────────────────
_s2 = _b64("nsfue_img2.jpeg")

slide2 = wrap(f"""
{progress_html(1)}
<div class="stack rise d1" style="gap:16px;max-width:880px;margin-top:-40px;">
  <div class="eyebrow rise d1">什么是免剃发FUE？</div>
  <div class="headline rise d2" style="font-size:54px;">免剃发FUE植发</div>
  <div class="rise d3" style="width:880px;border-radius:14px;overflow:hidden;height:430px;box-shadow:0 10px 40px -10px rgba(42,60,80,.12);">
    <img src="{_s2}" style="width:100%;height:430px;object-fit:cover;object-position:center bottom;display:block;">
  </div>
  <div class="card rise d4" style="width:880px;padding:28px 48px;">
    <div class="body-text" style="font-size:28px;text-align:left;color:var(--text);">
      毛囊从现有头发之间<strong style="color:var(--accent);">逐一提取</strong>，无需剃发，无剃痕，术后看不出任何痕迹。
    </div>
  </div>
</div>
{FOOTER}
""")

# ── Slide 3 — Who is it for? ───────────────────────────────────────────────
slide3 = wrap(f"""
{progress_html(2)}
<div class="stack rise d1" style="gap:28px;max-width:860px;">
  <div class="eyebrow rise d1">适合哪些人？</div>
  <div class="headline rise d2" style="font-size:54px;">专为注重<em>隐私</em>的人而设计。</div>
  <div class="card rise d3" style="width:860px;padding:40px 56px;">
    <ul class="checklist">
      <li class="yes"><span class="mark">&#10003;</span>职场人士，外形不能有明显变化</li>
      <li class="yes"><span class="mark">&#10003;</span>留长发、希望全程不露痕迹</li>
      <li class="yes"><span class="mark">&#10003;</span>术前术后都要保持低调</li>
      <li class="yes"><span class="mark">&#10003;</span>因为"要剃头"而一直不敢做的人</li>
    </ul>
  </div>
</div>
{FOOTER}
""")

# ── Slide 4 — Shave vs Non-Shave ──────────────────────────────────────────
_s4l = _b64("nsfue_new3.jpeg")
_s4r = _b64("nsfue_new1.jpeg")

slide4 = wrap(f"""
{progress_html(3)}
<div class="stack rise d1" style="gap:22px;">
  <div class="eyebrow rise d1">两者的区别</div>
  <div class="headline rise d2" style="font-size:52px;">直观对比。</div>
  <div class="compare rise d3" style="width:940px;">
    <div class="col sg" style="gap:16px;padding:28px 22px;">
      <div class="col-label">传统剃发FUE</div>
      <div style="width:100%;border-radius:10px;overflow:hidden;max-height:300px;display:flex;align-items:center;justify-content:center;">
        <img src="{_s4l}" style="width:100%;max-height:300px;object-fit:cover;display:block;">
      </div>
      <ul class="checklist" style="width:100%;">
        <li class="no"><span class="mark">&#10007;</span>供区需完全剃光</li>
        <li class="no"><span class="mark">&#10007;</span>剃痕明显持续2至4周</li>
        <li class="no"><span class="mark">&#10007;</span>难以遮盖</li>
      </ul>
    </div>
    <div class="col sh" style="gap:16px;padding:28px 22px;">
      <div class="col-label">免剃发FUE</div>
      <div style="width:100%;border-radius:10px;overflow:hidden;max-height:300px;display:flex;align-items:center;justify-content:center;">
        <img src="{_s4r}" style="width:100%;max-height:300px;object-fit:cover;object-position:center bottom;display:block;">
      </div>
      <ul class="checklist" style="width:100%;">
        <li class="yes"><span class="mark">&#10003;</span>头发保持原有长度</li>
        <li class="yes"><span class="mark">&#10003;</span>外观无变化</li>
        <li class="yes"><span class="mark">&#10003;</span>当天即可恢复正常生活</li>
      </ul>
    </div>
  </div>
</div>
{FOOTER}
""")

# ── Slide 5 — The Procedure ────────────────────────────────────────────────
slide5 = wrap(f"""
{progress_html(4)}
<div class="stack rise d1" style="gap:26px;max-width:880px;">
  <div class="eyebrow rise d1">手术当天</div>
  <div class="headline rise d2" style="font-size:54px;">手术全流程。</div>
  <div class="card rise d3" style="width:880px;padding:40px 52px;">
    <div class="steps">
      <div class="step"><div class="step-num">01</div><div class="step-text">保持头发自然状态到院</div></div>
      <div class="step"><div class="step-num">02</div><div class="step-text">局部麻醉，几乎无痛感</div></div>
      <div class="step"><div class="step-num">03</div><div class="step-text">在现有头发间逐一提取毛囊</div></div>
      <div class="step"><div class="step-num">04</div><div class="step-text">将毛囊移植至稀疏或后退区域</div></div>
      <div class="step"><div class="step-num">05</div><div class="step-text">数小时内完成，无人知晓你动过手术。</div></div>
    </div>
  </div>
</div>
{FOOTER}
""")

# ── Slide 6 — Recovery ─────────────────────────────────────────────────────
_s6 = _b64("nsfue_new2.jpeg")

slide6 = wrap(f"""
{progress_html(5)}
<div class="stack rise d1" style="gap:24px;max-width:880px;">
  <div class="eyebrow rise d1">恢复期</div>
  <div class="headline rise d2" style="font-size:54px;"><em>7至10天</em>恢复如常。</div>
  <div class="rise d3" style="width:880px;border-radius:14px;overflow:hidden;max-height:340px;display:flex;align-items:center;justify-content:center;box-shadow:0 10px 40px -10px rgba(42,60,80,.12);">
    <img src="{_s6}" style="width:100%;max-height:340px;object-fit:cover;display:block;">
  </div>
  <div class="card rise d4" style="width:880px;padding:28px 48px;">
    <div class="body-text" style="font-size:27px;text-align:left;color:var(--text);">
      现有头发自然遮盖受区，回公司没人会注意到，不需要解释，不需要编理由。
    </div>
  </div>
</div>
{FOOTER}
""")

# ── Slide 7 — Pattern Interrupt ────────────────────────────────────────────
slide7 = wrap(f"""
{progress_html(6)}
<div class="stack rise d1" style="gap:20px;max-width:800px;">
  <div class="headline rise d2" style="font-size:58px;">还在担心<br>别人会发现？</div>
  <div class="body-text rise d3" style="font-size:32px;margin-top:8px;">不会的。<br>这就是免剃发FUE的意义所在。</div>
</div>
{FOOTER}
""")

# ── Slide 8 — CTA ──────────────────────────────────────────────────────────
_cursor_data = base64.b64encode(open(os.path.join(IMG_DIR, "cursor_hand.png"), "rb").read()).decode()
_cursor_src  = f"data:image/png;base64,{_cursor_data}"

slide8 = wrap(f"""
{progress_html(7)}
<div class="stack rise d1" style="gap:26px;">
  <div class="eyebrow rise d1">下一步</div>
  <div class="headline rise d2" style="max-width:820px;">私信我们<em>「HAIR」</em>，<br>了解免剃发FUE是否适合你。</div>
  <div style="position:relative;display:inline-block;margin-top:6px;">
    <div class="pill rise d3" id="cta-pill">立即私信「HAIR」</div>
    <img id="cursor" src="{_cursor_src}" style="position:absolute;width:110px;right:-70px;bottom:-60px;opacity:0;transform:scale(1);transition:opacity 0.12s,transform 0.12s;pointer-events:none;">
  </div>
</div>
<script>
(function() {{
  var delay = 2200;
  setTimeout(function() {{
    var pill = document.getElementById('cta-pill');
    var cursor = document.getElementById('cursor');
    function doClick() {{
      cursor.style.opacity = '1';
      setTimeout(function() {{
        cursor.style.transform = 'scale(0.85)';
        pill.classList.add('pill-press');
        setTimeout(function() {{
          cursor.style.transform = 'scale(1)';
          pill.classList.remove('pill-press');
          setTimeout(function() {{
            cursor.style.opacity = '0';
            setTimeout(doClick, 2800);
          }}, 300);
        }}, 350);
      }}, 400);
    }}
    doClick();
  }}, delay);
}})();
</script>
{FOOTER}
""")

# ── Write files ────────────────────────────────────────────────────────────
for i, s in enumerate([slide1, slide2, slide3, slide4, slide5, slide6, slide7, slide8], start=1):
    with open(os.path.join(SLIDES_DIR, f"slide{i}.html"), "w") as f:
        f.write(s)

print("wrote 8 non-shave FUE slides (zh)")
