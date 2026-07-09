import os

SLIDES_DIR = "/tmp/vday_carousel/slides_v2_zh"
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

LOGO = '<div class="brand-logo"></div>'

def wrap(body, slide_cls=""):
    cls = f" {slide_cls}" if slide_cls else ""
    return f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><link rel="stylesheet" href="base.css"></head>
<body><div class="slide{cls}">{LOGO}{body}</div></body></html>"""

FOOTER     = '<div class="footer">Vday Aesthetic Concierge&nbsp;&nbsp;&middot;&nbsp;&nbsp;Singapore &ndash; Shanghai</div>'
FOOTER_ALT = '<div class="footer alt">Vday Aesthetic Concierge&nbsp;&nbsp;&middot;&nbsp;&nbsp;Singapore &ndash; Shanghai</div>'

# Slide 1 — Hook
slide1 = wrap(f"""
{progress_html(0)}
<div class="stack rise d1" style="max-width:860px;margin-top:-390px;">
  <div class="eyebrow rise d1">真实数字</div>
  <div class="headline rise d2">新加坡植发费用高达<br><em>$16,000。</em></div>
  <div class="headline rise d3">上海做同样的手术，<br><em>不到一半价格。</em></div>
  <div class="tag rise d5" style="font-size:30px;padding:12px 28px;margin-top:6px;">你花的钱，究竟买了什么</div>
</div>
<div class="img-block rise d5" style="position:absolute;bottom:380px;left:0;right:0;margin:0 auto;width:300px;height:300px;background-image:var(--img-follicle);"></div>
{FOOTER}
""")

# Slide 2 — Real cost breakdown (SG)
slide2 = wrap(f"""
{progress_html(1)}
<div class="stack rise d1">
  <div class="img-block rise d1" style="width:320px;height:224px;background-image:var(--img-sgmap);"></div>
  <div class="eyebrow warn rise d1">新加坡的价格</div>
  <div class="receipt rise d2">
    <div class="receipt-row"><span>乌节路 / CBD 诊所租金</span><span class="amt">$$$</span></div>
    <div class="receipt-row"><span>顾问介绍费</span><span class="amt">$$</span></div>
    <div class="receipt-row"><span>获客营销费用</span><span class="amt">$$</span></div>
    <div class="receipt-row"><span>医生薪资（量少、成本高）</span><span class="amt">$$$</span></div>
    <div class="receipt-row total"><span>约 $4/株 &times; 4,000 株</span><span class="amt">$16,000</span></div>
  </div>
  <div class="body-text rise d4">这还<strong>不算</strong>其他费用。</div>
</div>
{FOOTER}
""")

# Slide 3 — Side by side
slide3 = wrap(f"""
{progress_html(2)}
<div class="stack rise d1">
  <div class="eyebrow rise d1">同样的手术</div>
  <div class="compare rise d2">
    <div class="col sg">
      <div class="col-label">新加坡</div>
      <div class="col-amount">$16,000</div>
      <div class="col-sub">仅手术费</div>
    </div>
    <div class="col sh">
      <div class="col-label">上海</div>
      <div class="col-amount">全包价</div>
      <div class="col-sub">手术 + 接送机<br>+ 酒店 + 药物</div>
    </div>
  </div>
  <div class="body-text rise d4" style="margin-top:8px;">同样的毛囊数量，同样的 FUE 技术。<br>价格天壤之别。</div>
  <div class="headline rise d5" style="font-size:34px;margin-top:6px;">全包价格<em>不到新加坡的一半。</em></div>
</div>
{FOOTER}
""")

# Slide 4 — Why Shanghai can do this
slide4 = wrap(f"""
{progress_html(3)}
<div class="stack rise d1">
  <div class="eyebrow rise d1">价格背后的逻辑</div>
  <div class="compare rise d2">
    <div class="col sg">
      <div class="img-block" style="width:90px;height:90px;background-image:var(--img-sgperson);"></div>
      <div class="col-label">新加坡</div>
      <div class="col-sub" style="font-size:21px;margin-top:8px;">患者量少<br>&rarr; 每位患者分摊成本高</div>
    </div>
    <div class="col sh">
      <div class="img-block" style="width:140px;height:90px;background-image:var(--img-shpersons);"></div>
      <div class="col-label">上海</div>
      <div class="col-sub" style="font-size:21px;margin-top:8px;">高量专科诊所<br>&rarr; 成本由数百位<br>患者共同分摊</div>
    </div>
  </div>
  <div class="body-text rise d4" style="margin-top:8px;">医生水平没有差异。<br><strong>只是经营模式不同。</strong></div>
</div>
{FOOTER}
""")

# Slide 5 — What's included
slide5 = wrap(f"""
{progress_html(4)}
<div class="stack rise d1" style="gap:16px;">
  <div class="eyebrow rise d1">费用包含什么</div>
</div>
<div class="compare rise d2" style="align-items:stretch;margin-top:18px;">
  <div class="col sh" style="align-items:flex-start;">
    <div class="col-label" style="align-self:center;">上海</div>
    <ul class="checklist rise d2">
      <li class="yes"><span class="mark">&#10003;</span>4,000 株 FUE 植发</li>
      <li class="yes"><span class="mark">&#10003;</span>接送机服务</li>
      <li class="yes"><span class="mark">&#10003;</span>酒店住宿</li>
      <li class="yes"><span class="mark">&#10003;</span>术后药物</li>
      <li class="yes"><span class="mark">&#10003;</span>术后跟进服务</li>
    </ul>
  </div>
  <div class="col sg" style="align-items:flex-start;">
    <div class="col-label" style="align-self:center;">新加坡</div>
    <ul class="checklist rise d3">
      <li class="yes"><span class="mark">&#10003;</span>4,000 株 FUE 植发</li>
      <li class="no"><span class="mark">&#10007;</span>咨询费另计</li>
      <li class="no" style="align-items:flex-start;"><span class="mark">&#10007;</span><span>术后药物另计</span></li>
    </ul>
  </div>
</div>
{FOOTER}
""")

# Slide 6 — Uncomfortable truth (dark)
slide6 = wrap(f"""
{progress_html(5, alt=True)}
<div class="stack rise d1" style="max-width:800px;">
  <div class="eyebrow alt rise d1">一个不舒服的真相</div>
  <div class="headline alt rise d2" style="font-size:48px;">新加坡诊所收费高，<br>不是因为<em>贪心。</em></div>
  <div class="body-text alt rise d3" style="margin-top:14px;">他们也没有选择。<br>租金固定，薪资固定，客源有限。</div>
  <div class="headline alt rise d4" style="font-size:42px;margin-top:10px;">差价由<em>你来补。</em></div>
</div>
{FOOTER_ALT}
""", slide_cls="dark")

# Slide 7 — Trust bridge
slide7 = wrap(f"""
{progress_html(6)}
<div class="stack rise d1">
  <div class="eyebrow rise d1">为什么可以相信我们</div>
  <div class="photo-frame img-block rise d2" style="background-image:var(--img-procedure);background-size:cover;border-style:solid;border-color:var(--line);"></div>
  <div class="headline rise d3" style="font-size:36px;max-width:780px;font-weight:500;">「我亲自飞去上海考察，才把这门生意建立起来。」</div>
  <div class="tag rise d4">Dayton，创始人</div>
</div>
{FOOTER}
""")

# Slide 8 — CTA
slide8 = wrap(f"""
{progress_html(7)}
<div class="stack rise d1">
  <div class="eyebrow rise d1">名额有限</div>
  <div class="headline rise d2">正在考虑在 2026 年<br><em>恢复发际线？</em></div>
  <div class="body-text rise d3" style="max-width:680px;">我们每月只接受<br>少量客人。</div>
  <div class="pill rise d4" style="margin-top:6px;">立即联系我们</div>
</div>
{FOOTER}
""")

for i, s in enumerate([slide1,slide2,slide3,slide4,slide5,slide6,slide7,slide8], start=1):
    with open(os.path.join(SLIDES_DIR, f"slide{i}.html"), "w") as f:
        f.write(s)
print("wrote 8 pricing slides (zh)")
