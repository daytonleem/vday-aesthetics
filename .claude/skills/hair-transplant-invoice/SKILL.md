---
name: hair-transplant-invoice
description: Generate a Vday hair transplant client invoice (deposit invoice, balance invoice, or paid receipt) as an A4 portrait PDF and log it in the Client Tracker tab of the "Invoice" Google Sheet. Use whenever the user gives details of a new or existing client and asks for an invoice, receipt, or to update client tracking.
---

# Hair transplant invoices

This repo is public (it hosts vday.asia). Never commit client details, generated PDFs,
invoice JSON or the spreadsheet link. Keep them in the scratchpad.

## How the business bills

- **Deposit**: $1,000 SGD taken before booking (`invoice_type: "deposit"`).
- **Balance**: invoiced the day before the procedure: total less the deposit (`invoice_type: "balance"`).
- **Receipt**: everything paid, shows a PAID stamp and $0 remaining (`invoice_type: "receipt"`).
- All amounts are in SGD.

Standard prices (use unless the user says otherwise):

| Package | Price (SGD) | Default inclusions |
|---|---|---|
| Shaved FUE | $4,888 | 4,000 grafts, 2 hotel nights |
| Non-shaved FUE | $6,688 | 2 hotel nights (graft count not stated) |

Each package lists: Airport Pick Up, 2 Nights Hotel Stay, Body Check & Consultation,
Hair Transplant, Post Procedure Medication, Remote Follow Up.

Past add-on pricing: graft top-ups have been $1 per graft (1,000 grafts = $1,000).
There is no fixed price for an extra hotel night: always ask.

## Every time, before generating

Ask the user to confirm or fill in all of these in one message. Don't generate until they answer:

1. Client details: full name (as on passport), nationality, mobile, email, passport no. (optional).
2. Package: shaved or non-shaved, and whether the standard price applies.
3. Invoice type: deposit, balance, or receipt. Deposit paid so far (default $1,000).
4. Procedure date (optional, shown on the invoice).
5. **Additional grafts?** How many and at what price.
6. **Additional hotel nights?** How many and the price per night.
7. **Any discount?** Amount and label (e.g. "Referral Discount", "Hotel Offset").
8. Payment method (default PayNow), invoice date (default today), and any remarks.

Then show a short price breakdown (package + add-ons - discounts = total, less deposit = due)
and get a yes before making the PDF.

Invoice number: default is day + month + 2-digit year with no padding (14 Sep 2026 -> `14926`).
Check the tracker for a clash; if one exists add `-2`, `-3`.
A balance invoice for a client who already has a deposit invoice keeps their deposit invoice number
unless the user says otherwise.

## Generate the PDF

Write the spec to the scratchpad and run the script from the repo root:

```json
{
  "invoice_type": "balance",
  "date": "2026-10-19",
  "invoice_no": "191026",
  "package": "shaved",
  "package_price": 4888,
  "surgery_date": "2026-10-20",
  "grafts_included": 4000,
  "hotel_nights": 2,
  "payment_method": "PayNow",
  "client": {"name": "...", "nationality": "Singaporean", "mobile": "+65 ...", "email": "...", "passport": "..."},
  "line_items": [
    {"description": "Top Up 1,000 Grafts", "amount": 1000},
    {"description": "Additional Hotel Night", "qty": 1, "unit_price": 150}
  ],
  "discounts": [{"description": "Discount", "amount": 800}],
  "deposit": 1000,
  "notes": ["Optional remark shown under the totals."]
}
```

Only `client.name` is required. Defaults: today's date, auto invoice number, shaved package at the
standard price, standard inclusions, $1,000 deposit, PayNow. `inclusions` (a list) replaces the
default inclusion bullets, and `package_name` replaces the package title.

```
python3 .claude/skills/hair-transplant-invoice/generate_invoice.py <scratchpad>/<spec>.json -o "<scratchpad>/Invoice <no> - <Name>.pdf"
```

The script prints the totals as JSON. Check them against the breakdown the user approved, render
page 1 to PNG (pypdfium2) and look at it, then send the PDF with SendUserFile.

## Log it in the tracker

The tracker is the **Client Tracker** tab of the Google Sheet titled `Invoice ` (with a trailing
space). Find it with Google Drive search (`title contains 'Invoice' and mimeType =
'application/vnd.google-apps.spreadsheet'`) or use the link the user gives. Read the
google-workspace skill first.

Columns A to R: Invoice No | Invoice Date | Client Name | Nationality | Mobile | Email | Package |
Surgery Date | Package Price (SGD) | Add-ons (SGD) | Add-on Details | Discount (SGD) | Total (SGD) |
Deposit Paid (SGD) | Balance Due (SGD) | Status | Notes | Invoice Tab

- New client: add a row under the last one. Prefix invoice no. and mobile with `'` so they stay text.
  Write M as `=IF(In="","",In+Jn-Ln)` and O as `=IF(Mn="","",Mn-Nn)` for that row n. Discount is a
  positive number. Leave R empty for PDF-only invoices.
- Existing client (e.g. balance after a deposit): update their row instead of adding one.
- Status is a dropdown: Deposit paid, Balance invoiced, Paid in full, Surgery done, Cancelled.
- Read the row back and check the totals match the PDF.

Older invoices live in tabs named `YYYY-MM-DD First name`; the original sheet template is
the `Old Template` tab.
