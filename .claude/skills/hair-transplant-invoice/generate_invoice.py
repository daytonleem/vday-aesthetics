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
    "All medical procedures are performed by licensed physicians at our partner hospital.",
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
            "Pick-up & Drop-off Transfers",
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
        extras.append({"description": desc, "detail": [], "amount": blocks * price_per_block})
    extra_nights = int(data.get("extra_hotel_nights", 0))
    if extra_nights:
        night_price = float(data.get("hotel_night_price", HOTEL_NIGHT_PRICE))
        desc = f"Additional Hotel Night{'s' if extra_nights != 1 else ''} ({extra_nights} \u00d7 {money(night_price)})"
        extras.append({"description": desc, "detail": [], "amount": extra_nights * night_price})
    for item in data.get("line_items", []):
        if "graft" in item["description"].lower():
            sys.exit("Grafts are only sold in blocks of 1,000. Use extra_graft_blocks, not line_items.")
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
    gap = 0.6 if compact else 1.0
    light, regular, medium = register_fonts()
    W, H = A4
    margin = 20 * mm
    right = W - margin
    width = right - margin
    col_r = right - 66 * mm  # start of the right-hand column (details, totals)
    pad = 12  # inner padding of the totals panel

    from reportlab.pdfgen import canvas

    c = canvas.Canvas(out_path, pagesize=A4)
    client = data["client"]
    inv_date = parse_date(data.get("date"))
    inv_no = str(data.get("invoice_no") or default_invoice_no(inv_date))
    inv_type = data.get("invoice_type", "balance")
    c.setTitle(f"Invoice {inv_no} - {client['name']}")
    c.setAuthor(BUSINESS["name"])

    def key_value(y, key, value, x0=col_r, x1=right, size=9, key_font=None, value_font=None, colour=INK):
        spaced(c, x0, y, key, key_font or light, size, MUTED)
        spaced(c, x1, y, value, value_font or regular, size, colour, 0, "right")

    # Header
    top = H - 17 * mm
    logo = dark_logo()
    logo_h = 0
    if logo:
        reader, (lw, lh) = logo
        logo_w = 34 * mm
        logo_h = logo_w * lh / lw
        c.drawImage(reader, margin - 2 * mm, top - logo_h, logo_w, logo_h, mask="auto")
    else:
        spaced(c, margin, top - 20, BUSINESS["name"], medium, 26, INK)
        logo_h = 24
    sub_y = top - logo_h - 4 * mm
    label(c, margin, sub_y, BUSINESS["tagline"], regular, color=MUTED)
    spaced(c, margin, sub_y - 12, BUSINESS["whatsapp"], light, 8.5, MUTED)

    title = {"deposit": "Deposit Invoice", "receipt": "Receipt"}.get(inv_type, "Invoice")
    title_y = top - logo_h + 9 * mm
    spaced(c, right, title_y, title.upper(), light, 19, INK, 3.2, "right")
    spaced(c, right, title_y - 16, f"No. {inv_no}", light, 9, MUTED, 0.4, "right")
    if inv_type == "receipt":
        tag = "PAID IN FULL"
        tw = pdfmetrics.stringWidth(tag, regular, 6.5) + 1.4 * (len(tag) - 1) + 14
        c.setStrokeColor(ACCENT)
        c.setLineWidth(0.6)
        c.roundRect(right - tw, title_y - 38, tw, 13, 6.5, stroke=1, fill=0)
        spaced(c, right - tw / 2, title_y - 33.5, tag, regular, 6.5, ACCENT, 1.4, "centre")

    # Details band, full page width so its text sits on the page margins
    band_top = sub_y - 12 - 8 * mm
    y0 = band_top - 8 * mm
    client_rows = [client[k] if k != "passport" else f"Passport {client[k]}"
                   for k in ("nationality", "passport", "mobile", "email") if client.get(k)]
    details = [("Date", fmt_date(inv_date))]
    if data.get("surgery_date"):
        details.append(("Procedure", fmt_date(parse_date(data["surgery_date"]))))
    if data.get("deposit_invoice_no"):
        details.append(("Deposit invoice", str(data["deposit_invoice_no"])))
    details.append(("Payment", data.get("payment_method", "PayNow")))
    left_h = 16 + 13 * len(client_rows)
    right_h = 16 + 14 * (len(details) - 1)
    band_bottom = y0 - max(left_h, right_h) - 7 * mm
    c.setFillColor(MIST)
    c.rect(0, band_bottom, W, band_top - band_bottom, stroke=0, fill=1)

    label(c, margin, y0, "Billed to", regular, color=MUTED)
    spaced(c, margin, y0 - 16, client["name"], regular, 11.5, INK)
    yy = y0 - 16
    for row_text in client_rows:
        yy -= 13
        spaced(c, margin, yy, row_text, light, 9, MUTED)
    label(c, col_r, y0, "Details", regular, color=MUTED)
    ry = y0 - 16
    for k, v in details:
        key_value(ry, k, v)
        ry -= 14

    # Line items
    y = band_bottom - 10 * mm * gap
    label(c, margin, y, "Description", regular, color=MUTED)
    label(c, right, y, "Amount", regular, "right", color=MUTED)
    y -= 7
    c.setStrokeColor(INK)
    c.setLineWidth(0.5)
    c.line(margin, y, right, y)
    row_pad = (11 if not compact else 7)

    name_style = ParagraphStyle("n", fontName=regular, fontSize=10, leading=13, textColor=INK)
    incl_style = ParagraphStyle("i", fontName=light, fontSize=8.5, leading=12, textColor=MUTED)
    desc_w = width - 32 * mm

    package_row, extras, discounts = build_lines(data)

    def row(item):
        nonlocal y
        y -= row_pad + 10
        p = Paragraph(item["description"], name_style)
        _, ph = p.wrap(desc_w, 100)
        p.drawOn(c, margin, y - ph + 10)
        spaced(c, right, y, money(item["amount"]), regular, 10, INK, 0, "right")
        y -= ph - 10
        if item["detail"]:
            ip = Paragraph("  ·  ".join(item["detail"]), incl_style)
            _, ih = ip.wrap(desc_w, 200)
            y -= 4
            ip.drawOn(c, margin, y - ih)
            y -= ih
        y -= row_pad
        c.setStrokeColor(LINE)
        c.setLineWidth(0.6)
        c.line(margin, y, right, y)

    row(package_row)
    for item in extras + discounts:
        row(item)

    # Totals
    subtotal = package_row["amount"] + sum(i["amount"] for i in extras)
    discount_total = sum(i["amount"] for i in discounts)
    total = subtotal + discount_total
    deposit = float(data.get("deposit", DEFAULT_DEPOSIT))

    rows = []
    if discounts or extras:
        rows.append(("Subtotal", money(subtotal)))
    if discounts:
        rows.append(("Discount", money(discount_total)))
    after = []
    if inv_type == "deposit":
        due_label, due = "Deposit due now", deposit
        after.append(("Balance before procedure", money(total - deposit)))
    elif inv_type == "receipt":
        if deposit:
            dl = "Deposit paid" + (f" (Inv. {data['deposit_invoice_no']})" if data.get("deposit_invoice_no") else "")
            after += [(dl, money(-deposit)), ("Balance paid", money(-(total - deposit)))]
        else:
            after.append(("Paid " + fmt_date(inv_date), money(-total)))
        due_label, due = "Balance remaining", 0.0
    else:
        if deposit:
            dl = "Less deposit" + (f" (Inv. {data['deposit_invoice_no']})" if data.get("deposit_invoice_no") else "")
            after.append((dl, money(-deposit)))
        due_label, due = "Balance due", total - deposit

    step = 15
    panel_top = y - 10 * mm * gap
    n = len(rows) + 1 + len(after)
    panel_h = pad + 9 + step * (n - 1) + (3 if rows else 0) + 14 + 26 + pad
    panel_bottom = panel_top - panel_h
    c.setFillColor(MIST)
    c.roundRect(col_r - pad, panel_bottom, right - col_r + 2 * pad, panel_h, 4, stroke=0, fill=1)

    ty = panel_top - pad - 9
    for k, v in rows:
        key_value(ty, k, v)
        ty -= step
    if rows:
        c.setStrokeColor(HexColor("#d4e4ec"))
        c.setLineWidth(0.6)
        c.line(col_r, ty + 10, right, ty + 10)
        ty -= 3
    key_value(ty, "Total", money(total), key_font=regular, value_font=regular, colour=INK)
    ty -= step
    for k, v in after:
        key_value(ty, k, v)
        ty -= step
    ty += step - 9
    c.setStrokeColor(INK)
    c.setLineWidth(0.5)
    c.line(col_r, ty, right, ty)
    due_y = ty - 24
    label(c, col_r, due_y + 2, due_label, regular, color=ACCENT)
    spaced(c, right, due_y, money(due), regular, 17, INK, 0.2, "right")

    # Left of the totals: how to pay
    left_bottom = panel_bottom
    ly = panel_top - pad - 7
    if qr_path and inv_type != "receipt":
        label(c, margin, ly, "Pay via PayNow", regular, color=MUTED)
        qr_size = 27 * mm
        c.drawImage(ImageReader(qr_path), margin - 2, ly - 8 - qr_size, qr_size, qr_size)
        info_x = margin + qr_size + 5 * mm
        iy = ly - 22
        for k, v in (("Amount", money(due)), ("Reference", inv_no)):
            spaced(c, info_x, iy, k, light, 8.5, MUTED)
            spaced(c, info_x, iy - 12, v, regular, 9.5, INK)
            iy -= 30
        left_bottom = min(left_bottom, ly - 8 - qr_size)
    elif inv_type == "receipt":
        label(c, margin, ly, "Payment", regular, color=MUTED)
        p = Paragraph(f"Received in full on {fmt_date(inv_date)} by {data.get('payment_method', 'PayNow')}. "
                      "Thank you.", incl_style)
        _, ph = p.wrap(col_r - margin - 10 * mm, 100)
        p.drawOn(c, margin, ly - 10 - ph)

    # Remarks
    y = left_bottom - 9 * mm * gap
    notes = list(data.get("notes", []))
    if inv_type == "deposit" and not data.get("hide_deposit_note"):
        notes.append("The deposit secures your procedure date. The balance is invoiced the day before your procedure.")
    if notes:
        label(c, margin, y, "Remarks", regular, color=MUTED)
        y -= 6
        for note in notes:
            p = Paragraph(note, incl_style)
            _, ph = p.wrap(width, 200)
            p.drawOn(c, margin, y - ph)
            y -= ph + 2

    # Terms, above the footer
    term_style = ParagraphStyle("t", fontName=light, fontSize=7.3, leading=10, textColor=MUTED)
    paras = [Paragraph(f"{i}.&nbsp;&nbsp;{t}", term_style) for i, t in enumerate(TERMS, 1)]
    heights = [p.wrap(width, 200)[1] for p in paras]
    terms_top = 22 * mm + sum(heights) + 2 * len(paras) + 12
    if terms_top > y - 6:
        raise OverflowError("Invoice content is too long for one page; shorten the notes or line items.")
    label(c, margin, terms_top, "Terms and conditions", regular, color=MUTED)
    ty = terms_top - 6
    for p, h in zip(paras, heights):
        p.drawOn(c, margin, ty - h)
        ty -= h + 2

    c.setStrokeColor(LINE)
    c.setLineWidth(0.6)
    c.line(margin, 15 * mm, right, 15 * mm)
    spaced(c, W / 2, 10 * mm, f"THANK YOU FOR CHOOSING {BUSINESS['name'].upper()}", regular, 6.5, MUTED, 1.6, "centre")

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
