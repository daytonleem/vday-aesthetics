import os, base64

SLIDES_DIR = "/tmp/vday_carousel/slides_myths_zh"
IMG_DIR = "/tmp/vday_carousel/uploaded_images"
TOTAL = 8

def progress_html(active_idx, total=TOTAL, alt=False):
    segs = []
    for i in range(total):
        cls = "seg"
        if i < active_idx:
            cls += " done"
        elif i == active_idx:
            cls += " active"
        segs.append(f'<div class="{cls}"><div class="fill"></div></div>')
    alt_cls = " alt" if alt else ""
    return f'<div class="progress{alt_cls}">{"".join(segs)}</div>'

LOGO = '<div class="brand-logo"></div>'

def wrap(body, slide_cls=""):
    cls = f" {slide_cls}" if slide_cls else ""
    return f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><link rel="stylesheet" href="base.css"></head>
<body><div class="slide{cls}">{LOGO}{body}</div></body></html>"""

FOOTER = '<div class="footer">Vday Aesthetic Concierge&nbsp;&nbsp;&middot;&nbsp;&nbsp;新加坡 &ndash; 上海</div>'

def img_tag(fname, w=860, mh=460):
    ext = fname.split(".")[-1]
    mime = "image/jpeg" if ext in ("jpg","jpeg") else "image/webp"
    data = base64.b64encode(open(os.path.join(IMG_DIR, fname), "rb").read()).decode()
    style = f"width:{w}px;max-height:{mh}px;"
    img_style = f"max-height:{mh}px;"
    return f'<div class="slide-photo" style="{style}"><img src="data:{mime};base64,{data}" style="{img_style}"></div>'

# Slide 1 — Hook
slide1 = wrap(f"""
{progress_html(0)}
<div class="stack rise d1" style="max-width:840px;gap:20px;">
  <div class="eyebrow rise d1">做决定之前</div>
  <div class="headline rise d2">这5个植发误区，<br>正在让你<em>继续脱发。</em></div>
  {img_tag("myth_new1.webp")}
  <div class="body-text rise d4" style="margin-top:6px;font-size:30px;">往下看，你中了几个？</div>
</div>
{FOOTER}
""")

def myth_slide(idx, n, myth, truth, photo_html):
    return wrap(f"""
{progress_html(idx)}
<div class="stack rise d1" style="gap:8px;margin-top:-90px;">
  <div class="myth-label rise d1">误区 {n}</div>
  <div class="myth-text rise d2" style="font-size:57px;">&ldquo;{myth}&rdquo;</div>
  <div class="rise d3">{photo_html}</div>
  <div class="truth-wrap rise d4" style="gap:6px;">
    <div class="truth-icon" style="width:42px;height:42px;font-size:19px;">&#10003;</div>
    <div class="truth-label">真相</div>
    <div class="truth-text" style="font-size:42px;">{truth}</div>
  </div>
</div>
{FOOTER}
""")

slide2 = myth_slide(1, 1,
  "效果看起来很假。",
  "现代FUE愈合后<strong>几乎看不出来</strong>，发际线自然真实。",
  img_tag("myth_img1.webp", w=920, mh=690))

slide3 = myth_slide(2, 2,
  "必须完全秃头才能做。",
  "发际线后退或局部稀疏就可以，<strong>不需要</strong>严重脱发。",
  img_tag("myth_img2.webp", w=920, mh=690))

slide4 = myth_slide(3, 3,
  "恢复期要好几个月。",
  "大多数客人<strong>7至10天</strong>即可恢复正常生活。",
  img_tag("myth_new2.jpeg", w=920, mh=690))

slide5 = myth_slide(4, 4,
  "效果维持不了多久。",
  "移植的毛囊<strong>永久存活</strong>，术后2至6周的脱落属正常现象。",
  img_tag("myth_img4.webp", w=920, mh=690))

slide6 = myth_slide(5, 5,
  "做了就要剃光头。",
  "免剃发FUE技术<strong>无需剃头</strong>，术后没有任何痕迹。",
  img_tag("myth_img3.jpeg", w=920, mh=690))

# Slide 7 — Pattern interrupt
slide7 = wrap(f"""
{progress_html(6)}
<div class="stack rise d1">
  <div class="headline rise d2" style="font-size:52px;max-width:780px;">还有疑问？<br>你不是第一个。</div>
</div>
{FOOTER}
""")

# Embed cursor image
_cursor_data = base64.b64encode(open(os.path.join(IMG_DIR, "cursor_hand.png"), "rb").read()).decode()
_cursor_src = f"data:image/png;base64,{_cursor_data}"

# Slide 8 — CTA
slide8 = wrap(f"""
{progress_html(7)}
<div class="stack rise d1" style="gap:26px;">
  <div class="eyebrow rise d1">下一步</div>
  <div class="headline rise d2" style="max-width:820px;">私信我们<em>「HAIR」</em>，<br>了解你是否适合植发。</div>
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

for i, s in enumerate([slide1, slide2, slide3, slide4, slide5, slide6, slide7, slide8], start=1):
    with open(os.path.join(SLIDES_DIR, f"slide{i}.html"), "w") as f:
        f.write(s)

print("wrote 8 myths slides (zh)")
