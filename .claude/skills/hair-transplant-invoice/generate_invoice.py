#!/usr/bin/env python3
"""Generate a Vday hair transplant invoice as an A4 portrait PDF.

Usage:
    python3 generate_invoice.py invoice.json -o "Invoice 191026 - Client Name.pdf"

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
DEFAULT_GRAFTS = {"shaved": 4000, "non-shaved": None}
DEFAULT_HOTEL_NIGHTS = 2
DEFAULT_DEPOSIT = 1000.0
GRAFT_BLOCK = 1000  # grafts per top-up block
GRAFT_BLOCK_PRICE = 1000.0
HOTEL_NIGHT_PRICE = 64.0

BUSINESS = {
    "name": "Vday",
    "tagline": "Aesthetic Concierge · Shanghai",
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
    sign = "-" if value < 0 else ""
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
    if data.get("surgery_date"):
        title += f" – {fmt_date(parse_date(data['surgery_date']))}"

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


def draw_invoice(data, out_path):
    body, bold = "Helvetica", "Helvetica-Bold"
    W, H = A4
    margin = 18 * mm
    right = W - margin

    from reportlab.pdfgen import canvas

    c = canvas.Canvas(out_path, pagesize=A4)
    client = data["client"]
    inv_date = parse_date(data.get("date"))
    inv_no = str(data.get("invoice_no") or default_invoice_no(inv_date))
    inv_type = data.get("invoice_type", "balance")
    c.setTitle(f"Invoice {inv_no} - {client['name']}")
    c.setAuthor(BUSINESS["name"])

    # Header band
    c.setFillColor(MIST)
    c.rect(0, H - 52 * mm, W, 52 * mm, stroke=0, fill=1)
    c.setFillColor(ACCENT)
    c.rect(0, H - 52 * mm, W, 1.2 * mm, stroke=0, fill=1)

    logo = dark_logo()
    top = H - 14 * mm
    if logo:
        reader, (lw, lh) = logo
        logo_w = 42 * mm
        logo_h = logo_w * lh / lw
        c.drawImage(reader, margin - 2 * mm, top - logo_h + 2 * mm, logo_w, logo_h, mask="auto")
        y = top - logo_h - 2 * mm
    else:
        c.setFont(bold, 28)
        c.setFillColor(INK)
        c.drawString(margin, top - 20, BUSINESS["name"])
        y = top - 30
    c.setFillColor(MUTED)
    c.setFont(body, 9)
    for line in (BUSINESS["tagline"], f"{BUSINESS['website']}  ·  WhatsApp {BUSINESS['whatsapp']}"):
        c.drawString(margin, y, line)
        y -= 12

    c.setFillColor(INK)
    c.setFont(bold, 26)
    heading = {"deposit": "DEPOSIT INVOICE", "receipt": "RECEIPT"}.get(inv_type, "INVOICE")
    c.drawRightString(right, top - 18, heading)
    meta = [("Invoice No.", inv_no), ("Date", fmt_date(inv_date)),
            ("Payment Method", data.get("payment_method", "PayNow"))]
    if data.get("surgery_date"):
        meta.append(("Procedure Date", fmt_date(parse_date(data["surgery_date"]))))
    my = top - 38
    for label, value in meta:
        c.setFont(body, 9)
        c.setFillColor(MUTED)
        c.drawRightString(right - 34 * mm, my, label)
        c.setFont(bold, 9.5)
        c.setFillColor(INK)
        c.drawRightString(right, my, value)
        my -= 13

    # Bill to
    y = H - 64 * mm
    c.setFont(bold, 8)
    c.setFillColor(ACCENT)
    c.drawString(margin, y, "BILLED TO")
    y -= 15
    c.setFont(bold, 12)
    c.setFillColor(INK)
    c.drawString(margin, y, client["name"])
    y -= 14
    c.setFont(body, 9.5)
    c.setFillColor(MUTED)
    for label, key in (("Passport No.", "passport"), ("Nationality", "nationality"),
                       ("Mobile", "mobile"), ("Email", "email")):
        if client.get(key):
            c.drawString(margin, y, f"{label}:  {client[key]}")
            y -= 12.5

    # Line items
    y -= 10
    c.setFillColor(INK)
    c.rect(margin, y - 7, right - margin, 20, stroke=0, fill=1)
    c.setFillColor(HexColor("#ffffff"))
    c.setFont(bold, 9)
    c.drawString(margin + 8, y, "DESCRIPTION")
    c.drawRightString(right - 8, y, "AMOUNT (SGD)")
    y -= 26

    desc_style = ParagraphStyle("d", fontName=bold, fontSize=10.5, leading=13, textColor=INK)
    detail_style = ParagraphStyle("dd", fontName=body, fontSize=9, leading=12, textColor=MUTED)
    desc_w = right - margin - 45 * mm

    package_row, extras, discounts = build_lines(data)

    def row(item, amount_color=INK):
        nonlocal y
        p = Paragraph(item["description"], desc_style)
        _, ph = p.wrap(desc_w, 100)
        p.drawOn(c, margin + 8, y - ph + 10)
        c.setFont(bold, 10.5)
        c.setFillColor(amount_color)
        c.drawRightString(right - 8, y, money(item["amount"]))
        y -= ph + 2
        for d in item["detail"]:
            dp = Paragraph(f"–&nbsp;&nbsp;{d}", detail_style)
            _, dh = dp.wrap(desc_w - 10, 100)
            dp.drawOn(c, margin + 16, y - dh + 10)
            y -= dh
        y -= 8
        c.setStrokeColor(LINE)
        c.setLineWidth(0.6)
        c.line(margin, y + 4, right, y + 4)
        y -= 12

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

    totals = [("Subtotal", money(subtotal))]
    if discounts:
        totals.append(("Total Discount", money(discount_total)))
    totals.append(("Total", money(total)))
    if inv_type == "deposit":
        totals.append(("Balance payable before procedure", money(total - deposit)))
        due_label, due = "Deposit Due Now", deposit
    elif inv_type == "receipt":
        if deposit:
            label = "Deposit Paid"
            if data.get("deposit_invoice_no"):
                label += f" (Inv. {data['deposit_invoice_no']})"
            totals.append((label, money(-deposit)))
        totals.append(("Balance Paid", money(-(total - deposit))))
        due_label, due = "Remaining", 0.0
    else:
        if deposit:
            label = "Less Deposit Paid"
            if data.get("deposit_invoice_no"):
                label += f" (Inv. {data['deposit_invoice_no']})"
            totals.append((label, money(-deposit)))
        due_label, due = "Balance Due", total - deposit

    tx = right - 85 * mm
    y -= 2
    for label, value in totals:
        is_total = label == "Total"
        c.setFont(bold if is_total else body, 10 if is_total else 9.5)
        c.setFillColor(INK if is_total else MUTED)
        c.drawString(tx, y, label)
        c.setFillColor(INK)
        c.drawRightString(right - 8, y, value)
        y -= 16
    y -= 4
    c.setFillColor(ACCENT)
    c.roundRect(tx - 8, y - 9, right - tx + 8, 26, 3, stroke=0, fill=1)
    c.setFillColor(HexColor("#ffffff"))
    c.setFont(bold, 11.5)
    c.drawString(tx, y, due_label.upper())
    c.drawRightString(right - 8, y, money(due))
    bar_y = y
    y -= 30

    if inv_type == "receipt":
        c.saveState()
        c.setStrokeColor(ACCENT)
        c.setFillColor(ACCENT)
        c.setLineWidth(2)
        c.translate(margin + 35 * mm, bar_y + 45)
        c.rotate(10)
        c.roundRect(-25 * mm, -8 * mm, 50 * mm, 16 * mm, 4, stroke=1, fill=0)
        c.setFont(bold, 22)
        c.drawCentredString(0, -2.8 * mm, "PAID")
        c.restoreState()

    # Remarks
    notes = list(data.get("notes", []))
    if inv_type == "deposit" and not data.get("hide_deposit_note"):
        notes.append("The deposit secures your procedure date. The balance is invoiced the day before your procedure.")
    if notes:
        y -= 6
        c.setFont(bold, 8)
        c.setFillColor(ACCENT)
        c.drawString(margin, y, "REMARKS")
        y -= 13
        for n in notes:
            p = Paragraph(f"–&nbsp;&nbsp;{n}", detail_style)
            _, ph = p.wrap(right - margin, 200)
            p.drawOn(c, margin, y - ph + 10)
            y -= ph + 2

    # Terms, pinned to the bottom of the page
    term_style = ParagraphStyle("t", fontName=body, fontSize=7.8, leading=10.2, textColor=MUTED)
    paras = [Paragraph(f"–&nbsp;&nbsp;{t}", term_style) for t in TERMS]
    heights = [p.wrap(right - margin, 200)[1] for p in paras]
    ty = 20 * mm + sum(heights) + 14
    if ty > y - 10:
        sys.exit("Invoice content is too long for one page; shorten the notes or line items.")
    c.setStrokeColor(LINE)
    c.line(margin, ty + 10, right, ty + 10)
    c.setFont(bold, 8)
    c.setFillColor(INK)
    c.drawString(margin, ty - 2, "TERMS AND CONDITIONS")
    ty -= 14
    for p, h in zip(paras, heights):
        p.drawOn(c, margin, ty - h + 8)
        ty -= h + 1

    c.setFont(body, 8)
    c.setFillColor(ACCENT)
    c.drawCentredString(W / 2, 11 * mm, f"Thank you for choosing {BUSINESS['name']}  ·  {BUSINESS['website']}")

    c.showPage()
    c.save()
    return {"invoice_no": inv_no, "date": inv_date.isoformat(), "subtotal": subtotal,
            "discount": -discount_total, "total": total, "deposit": deposit, "due_label": due_label, "due": due}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("spec", help="JSON file with the invoice details")
    ap.add_argument("-o", "--output", help="PDF path (default: 'Invoice <no> - <name>.pdf' next to the JSON)")
    args = ap.parse_args()

    with open(args.spec) as f:
        data = json.load(f)
    inv_date = parse_date(data.get("date"))
    inv_no = str(data.get("invoice_no") or default_invoice_no(inv_date))
    out = args.output or os.path.join(os.path.dirname(os.path.abspath(args.spec)),
                                      f"Invoice {inv_no} - {data['client']['name']}.pdf")
    summary = draw_invoice(data, out)
    summary["pdf"] = out
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
