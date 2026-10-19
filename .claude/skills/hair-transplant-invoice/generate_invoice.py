#!/usr/bin/env python3
"""Generate a Vday hair transplant invoice as an A4 portrait PDF.

Usage:
    python3 generate_invoice.py invoice.json -o "Invoice 191026 - Client Name.pdf" --qr paynow_qr.png

See SKILL.md in this folder for the JSON fields.
"""
import argparse
import datetime as dt
import io
import json
import os
import sys

from PIL import Image
from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
LOGO = os.path.join(REPO, "Logo White.png")

# Brand colours, taken from the website's CSS variables.
INK = HexColor("#2c2c2c")
MUTED = HexColor("#6b6b6b")
ACCENT = HexColor("#6a9ab0")
LINE = HexColor("#e8e8e8")
MIST = HexColor("#f0f7fb")

PRICES = {"shaved": 4888.0, "non-shaved": 6688.0}
PACKAGE_NAMES = {
    "shaved": "Shaved FUE Hair Transplant Package",
    "non-shaved": "Non-Shaved FUE Hair Transplant Package",
}
DEFAULT_GRAFTS = {"shaved": 4000, "non-shaved": 4000}
DEFAULT_HOTEL_NIGHTS = 2
DEFAULT_DEPOSIT = 1000.0
GRAFT_BLOCK = 1000  # grafts per top-up block
GRAFT_BLOCK_PRICE = 1000.0
HOTEL_NIGHT_PRICE = 64.0

BUSINESS = {
    "name": "Vday",
    "tagline": "Aesthetic Concierge",
    "website": "vday.asia",
    "whatsapp": "+65 9899 1446",
}

TERMS = [
    "All medical procedures are performed by licensed physicians.",
    "Results are dependent on individual circumstances and adherence to post-operative care instructions.",
    "All services, coordination, marketing, and administrative support provided by the concierge are non-medical in nature.",
    "By paying for and continuing to receive services, the client acknowledges that they have read, understood, "
    "and accepted the risks and non-refundable terms of the procedure.",
]


def dark_logo():
    """The site logo is white on transparent; recolour it to ink for a white page."""
    if not os.path.exists(LOGO):
        return None
    im = Image.open(LOGO).convert("RGBA")
    solid = Image.new("RGBA", im.size, (0x2C, 0x2C, 0x2C, 255))
    solid.putalpha(im.getchannel("A"))
    buf = io.BytesIO()
    solid.save(buf, "PNG")
    buf.seek(0)
    return ImageReader(buf), im.size


def money(value):
    sign = "\u2212" if value < 0 else ""
    return f"{sign}${abs(value):,.2f}"


def parse_date(value):
    if not value:
        return dt.date.today()
    return dt.date.fromisoformat(value)


def fmt_date(d):
    return d.strftime("%d %b %Y")


def default_invoice_no(d):
    # Matches the existing numbering: day, month, two-digit year, no padding (14 Sep 2026 -> 14926).
    return f"{d.day}{d.month}{d.strftime('%y')}"


def build_lines(data):
    """Return (package_row, extra_rows, discount_rows) as dicts with description, detail and amount."""
    package = data.get("package", "shaved").lower().replace("_", "-").replace(" ", "-")
    if package not in PRICES:
        sys.exit(f"Unknown package '{package}'. Use 'shaved' or 'non-shaved'.")

    price = float(data.get("package_price", PRICES[package]))
    grafts = data.get("grafts_included", DEFAULT_GRAFTS[package])
    nights = int(data.get("hotel_nights", DEFAULT_HOTEL_NIGHTS))

    inclusions = data.get("inclusions")
    if inclusions is None:
        transplant = "Hair Transplant" + (f" ({int(grafts):,} Grafts)" if grafts else "")
        inclusions = [
            "Airport Pick Up",
            f"{nights} Night{'s' if nights != 1 else ''} Hotel Stay",
            "Body Check & Consultation",
            transplant,
            "Post Procedure Medication",
            "Remote Follow Up",
        ]

    title = data.get("package_name", PACKAGE_NAMES[package])

    package_row = {"description": title, "detail": inclusions, "amount": price}

    extras = []
    blocks = int(data.get("extra_graft_blocks", 0))
    if blocks:
        price_per_block = float(data.get("graft_block_price", GRAFT_BLOCK_PRICE))
        desc = f"Top Up {blocks * GRAFT_BLOCK:,} Grafts"
        if blocks > 1:
            desc += f" ({blocks} \u00d7 {money(price_per_block)} per {GRAFT_BLOCK:,})"
        extras.append({"description": desc, "detail": [], "amount": blocks * price_per_block})
    extra_nights = int(data.get("extra_hotel_nights", 0))
    if extra_nights:
        night_price = float(data.get("hotel_night_price", HOTEL_NIGHT_PRICE))
        desc = f"Additional Hotel Night{'s' if extra_nights != 1 else ''} ({extra_nights} \u00d7 {money(night_price)})"
        extras.append({"description": desc, "detail": [], "amount": extra_nights * night_price})
    for item in data.get("line_items", []):
        qty = item.get("qty", 1)
        if "amount" in item:
            amount = float(item["amount"])
        else:
            amount = float(item["unit_price"]) * qty
        desc = item["description"]
        if qty != 1 and "unit_price" in item:
            desc += f" ({qty} × {money(float(item['unit_price']))})"
        extras.append({"description": desc, "detail": item.get("detail", []), "amount": amount})

    discounts = [
        {"description": d.get("description", "Discount"), "detail": [], "amount": -abs(float(d["amount"]))}
        for d in data.get("discounts", [])
    ]
    return package_row, extras, discounts


FONT_DIR = os.path.join(HERE, "fonts")


def register_fonts():
    """Jost is the website's typeface; fall back to Helvetica if the font files are missing."""
    files = {"Light": "Jost-300.ttf", "Regular": "Jost-400.ttf", "Medium": "Jost-500.ttf"}
    paths = {k: os.path.join(FONT_DIR, v) for k, v in files.items()}
    if all(os.path.exists(p) for p in paths.values()):
        for k, p in paths.items():
            pdfmetrics.registerFont(TTFont(f"Jost-{k}", p))
        return "Jost-Light", "Jost-Regular", "Jost-Medium"
    return "Helvetica", "Helvetica", "Helvetica-Bold"


def spaced(c, x, y, text, font, size, color, space=0.0, align="left"):
    """Draw text with letter spacing; align is left, right or centre."""
    width = pdfmetrics.stringWidth(text, font, size) + space * max(len(text) - 1, 0)
    if align == "right":
        x -= width
    elif align == "centre":
        x -= width / 2
    t = c.beginText(x, y)
    t.setFont(font, size)
    t.setCharSpace(space)
    t.setFillColor(color)
    t.textOut(text)
    t.setCharSpace(0)  # char spacing is page state; reset it so Paragraphs aren't affected
    c.drawText(t)
    return width


def label(c, x, y, text, font, align="left", color=None):
    spaced(c, x, y, text.upper(), font, 7, color or ACCENT, 1.4, align)


def draw_invoice(data, out_path, qr_path=None, compact=False):
    """compact tightens vertical spacing for invoices with many lines."""
    gap = 0.55 if compact else 1.0
    light, regular, medium = register_fonts()
    W, H = A4
    margin = 22 * mm
    right = W - margin
    width = right - margin

    from reportlab.pdfgen import canvas

    c = canvas.Canvas(out_path, pagesize=A4)
    client = data["client"]
    inv_date = parse_date(data.get("date"))
    inv_no = str(data.get("invoice_no") or default_invoice_no(inv_date))
    inv_type = data.get("invoice_type", "balance")
    c.setTitle(f"Invoice {inv_no} - {client['name']}")
    c.setAuthor(BUSINESS["name"])

    # Thin accent line across the very top
    c.setFillColor(ACCENT)
    c.rect(0, H - 2.2 * mm, W, 2.2 * mm, stroke=0, fill=1)

    # Header: logo left, document title right
    top = H - 20 * mm
    logo = dark_logo()
    if logo:
        reader, (lw, lh) = logo
        logo_w = 38 * mm
        logo_h = logo_w * lh / lw
        c.drawImage(reader, margin - 2.5 * mm, top - logo_h + 6 * mm, logo_w, logo_h, mask="auto")
    else:
        spaced(c, margin, top - 14, BUSINESS["name"], medium, 26, INK)
    sub_y = top - 16 * mm
    spaced(c, margin, sub_y, BUSINESS["tagline"].upper(), regular, 7, MUTED, 1.4)
    spaced(c, margin, sub_y - 12, BUSINESS["whatsapp"], light, 8.5, MUTED)

    title = {"deposit": "Deposit Invoice", "receipt": "Receipt"}.get(inv_type, "Invoice")
    spaced(c, right, top - 4, title.upper(), light, 22, INK, 4.5, "right")
    spaced(c, right, top - 20, f"No. {inv_no}", regular, 9.5, MUTED, 0.6, "right")
    if inv_type == "receipt":
        pill = "PAID IN FULL"
        pw = pdfmetrics.stringWidth(pill, medium, 7) + 1.6 * (len(pill) - 1) + 16
        c.setStrokeColor(ACCENT)
        c.setLineWidth(0.8)
        c.roundRect(right - pw, top - 42, pw, 15, 7.5, stroke=1, fill=0)
        spaced(c, right - pw / 2, top - 37, pill, medium, 7, ACCENT, 1.6, "centre")

    # Details panel: billed to, dates, payment, on a tinted background
    y = top - 33 * mm
    pad = 14
    col_w = (width - 2 * pad) / 3
    cols = [margin + pad, margin + pad + col_w, margin + pad + 2 * col_w]

    details = [("Date", fmt_date(inv_date))]
    if data.get("surgery_date"):
        details.append(("Procedure", fmt_date(parse_date(data["surgery_date"]))))
    if data.get("deposit_invoice_no"):
        details.append(("Deposit inv.", str(data["deposit_invoice_no"])))
    pay_rows = [("Method", data.get("payment_method", "PayNow")), ("Currency", "SGD")]
    client_lines = sum(1 for k in ("nationality", "passport", "mobile", "email") if client.get(k))
    lowest = max(15 + 14 + 12.5 * (client_lines - 1) if client_lines else 15,
                 15 + 14 * (max(len(details), len(pay_rows)) - 1))
    c.setFillColor(MIST)
    c.roundRect(margin, y - lowest - 14, width, lowest + 14 + 22, 5, stroke=0, fill=1)

    label(c, cols[0], y, "Billed to", medium)
    yy = y - 15
    spaced(c, cols[0], yy, client["name"], medium, 11, INK)
    yy -= 14
    for key in ("nationality", "passport", "mobile", "email"):
        if client.get(key):
            value = client[key] if key != "passport" else f"Passport {client[key]}"
            spaced(c, cols[0], yy, value, light, 9, MUTED)
            yy -= 12.5
    bottom = yy

    def detail_column(x, heading, rows):
        label(c, x, y, heading, medium)
        ry = y - 15
        for k, v in rows:
            spaced(c, x, ry, k, light, 8.5, MUTED)
            spaced(c, x + 21 * mm, ry, v, regular, 9, INK)
            ry -= 14
        return ry

    detail_column(cols[1], "Details", details)
    detail_column(cols[2], "Payment", pay_rows)

    # Line items
    y = y - lowest - 14 - 9 * mm * gap
    label(c, margin, y, "Description", medium, color=MUTED)
    label(c, right, y, "Amount", medium, "right", color=MUTED)
    y -= 8
    c.setStrokeColor(INK)
    c.setLineWidth(0.8)
    c.line(margin, y, right, y)
    y -= 18

    desc_style = ParagraphStyle("d", fontName=medium, fontSize=10.5, leading=14, textColor=INK)
    detail_style = ParagraphStyle("dd", fontName=light, fontSize=8.8, leading=10.5 if compact else 11.5, textColor=MUTED)
    desc_w = width - 40 * mm

    package_row, extras, discounts = build_lines(data)

    def row(item, amount_color=INK):
        nonlocal y
        p = Paragraph(item["description"], desc_style)
        _, ph = p.wrap(desc_w, 100)
        p.drawOn(c, margin, y - ph + 11)
        spaced(c, right, y, money(item["amount"]), regular, 10.5, amount_color, 0.2, "right")
        y -= ph + 3
        for d in item["detail"]:
            dp = Paragraph(d, detail_style)
            _, dh = dp.wrap(desc_w - 10, 100)
            c.setFillColor(ACCENT)
            c.circle(margin + 2.2, y + 3.4, 1.1, stroke=0, fill=1)
            dp.drawOn(c, margin + 9, y - dh + 10)
            y -= dh
        y -= 7 * gap
        c.setStrokeColor(LINE)
        c.setLineWidth(0.6)
        c.line(margin, y + 2, right, y + 2)
        y -= 15 * gap

    row(package_row)
    for item in extras:
        row(item)
    for item in discounts:
        row(item, ACCENT)

    # Totals
    subtotal = package_row["amount"] + sum(i["amount"] for i in extras)
    discount_total = sum(i["amount"] for i in discounts)
    total = subtotal + discount_total
    deposit = float(data.get("deposit", DEFAULT_DEPOSIT))

    totals = []
    if discounts or extras:
        totals.append(("Subtotal", money(subtotal)))
    if discounts:
        totals.append(("Discount", money(discount_total)))
    if inv_type == "deposit":
        due_label, due = "Deposit due now", deposit
        after = [("Balance before procedure", money(total - deposit))]
    elif inv_type == "receipt":
        paid = []
        if deposit:
            label_text = "Deposit paid"
            if data.get("deposit_invoice_no"):
                label_text += f" (Inv. {data['deposit_invoice_no']})"
            paid.append((label_text, money(-deposit)))
            paid.append(("Balance paid", money(-(total - deposit))))
        else:
            paid.append((f"Paid {fmt_date(inv_date)}", money(-total)))
        due_label, due = "Balance remaining", 0.0
        after = paid
    else:
        after = []
        if deposit:
            label_text = "Less deposit paid"
            if data.get("deposit_invoice_no"):
                label_text += f" (Inv. {data['deposit_invoice_no']})"
            after.append((label_text, money(-deposit)))
        due_label, due = "Balance due", total - deposit

    tx = right - 74 * mm
    rx = right - 14
    y -= 14 * gap
    block_top = y
    rows_h = 17 * (len(totals) + 1 + len(after)) + 40
    c.setFillColor(MIST)
    c.roundRect(tx - 14, y - rows_h + 4, right - tx + 14, rows_h + 14, 5, stroke=0, fill=1)

    def total_row(text, value, font=light, colour=MUTED, size=9.5):
        nonlocal y
        spaced(c, tx, y, text, font, size, colour)
        spaced(c, rx, y, value, regular if font == light else medium, size, INK, 0.2, "right")
        y -= 17

    for t, v in totals:
        total_row(t, v)
    y -= 2
    c.setStrokeColor(LINE)
    c.setStrokeColor(HexColor("#d4e4ec"))
    c.line(tx, y + 11, rx, y + 11)
    total_row("Total", money(total), medium, INK, 10.5)
    for t, v in after:
        total_row(t, v)
    y -= 4
    c.setStrokeColor(INK)
    c.setLineWidth(0.8)
    c.line(tx, y + 12, rx, y + 12)
    y -= 10
    label(c, tx, y + 3, due_label, medium, color=ACCENT)
    spaced(c, rx, y - 2, money(due), medium, 17, INK, 0.3, "right")
    y -= 32

    if qr_path and inv_type != "receipt":
        qr_size = 30 * mm
        qx, qy = margin, block_top + 4
        label(c, qx, qy, "Pay via PayNow", medium)
        c.drawImage(ImageReader(qr_path), qx, qy - 8 - qr_size, qr_size, qr_size)
        tx2 = qx + qr_size + 5 * mm
        ly = qy - 22
        lines = []
        if data.get("paynow_name"):
            lines.append(data["paynow_name"])
        lines += [f"Amount  {money(due)}", f"Reference  {inv_no}"]
        for line in lines:
            spaced(c, tx2, ly, line, light, 8.8, MUTED)
            ly -= 13
        y = min(y, qy - 8 - qr_size - 10)

    # Remarks
    notes = list(data.get("notes", []))
    if inv_type == "deposit" and not data.get("hide_deposit_note"):
        notes.append("The deposit secures your procedure date. The balance is invoiced the day before your procedure.")
    if notes:
        y -= 8
        label(c, margin, y, "Remarks", medium)
        y -= 14
        for n in notes:
            p = Paragraph(n, detail_style)
            _, ph = p.wrap(width, 200)
            p.drawOn(c, margin, y - ph + 10)
            y -= ph + 3

    # Terms, pinned above the footer
    term_style = ParagraphStyle("t", fontName=light, fontSize=7.6, leading=10.5, textColor=MUTED)
    paras = [Paragraph(t, term_style) for t in TERMS]
    heights = [p.wrap(width - 8, 200)[1] for p in paras]
    ty = 21 * mm + sum(heights) + 3 * len(paras) + 14
    if ty > y + 4:
        raise OverflowError("Invoice content is too long for one page; shorten the notes or line items.")
    label(c, margin, ty, "Terms and conditions", medium, color=MUTED)
    ty -= 14
    for p, h in zip(paras, heights):
        c.setFillColor(LINE)
        c.circle(margin + 1.5, ty + 3, 1, stroke=0, fill=1)
        p.drawOn(c, margin + 8, ty - h + 9)
        ty -= h + 3

    c.setStrokeColor(LINE)
    c.setLineWidth(0.6)
    c.line(margin, 17 * mm, right, 17 * mm)
    spaced(c, W / 2, 11 * mm, f"THANK YOU FOR CHOOSING {BUSINESS['name'].upper()}",
           regular, 7, ACCENT, 1.4, "centre")

    c.showPage()
    c.save()
    return {"invoice_no": inv_no, "date": inv_date.isoformat(), "subtotal": subtotal,
            "discount": -discount_total, "total": total, "deposit": deposit, "due_label": due_label, "due": due}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("spec", help="JSON file with the invoice details")
    ap.add_argument("-o", "--output", help="PDF path (default: 'Invoice <no> - <name>.pdf' next to the JSON)")
    ap.add_argument("--qr", help="PayNow QR image, pulled from the sheet with extract_qr.py")
    args = ap.parse_args()

    with open(args.spec) as f:
        data = json.load(f)
    inv_date = parse_date(data.get("date"))
    inv_no = str(data.get("invoice_no") or default_invoice_no(inv_date))
    out = args.output or os.path.join(os.path.dirname(os.path.abspath(args.spec)),
                                      f"Invoice {inv_no} - {data['client']['name']}.pdf")
    try:
        summary = draw_invoice(data, out, args.qr)
    except OverflowError:
        try:
            summary = draw_invoice(data, out, args.qr, compact=True)
        except OverflowError as e:
            sys.exit(str(e))
    summary["pdf"] = out
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
