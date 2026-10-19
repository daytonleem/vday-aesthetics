---
name: hair-transplant-invoice
description: Generate a Vday hair transplant client invoice (deposit invoice, balance invoice, or paid receipt) as an A4 portrait PDF, send it to the user in chat, and record it in the Client Tracker and Invoice Log tabs of the "Invoice" Google Sheet. Use whenever the user gives details of a new or existing client and asks for an invoice, receipt, or to update client tracking.
---

# Hair transplant invoices

This repo is public (it hosts vday.asia). Never commit client details, generated PDFs,
invoice JSON or the spreadsheet link. Keep them in the scratchpad.

## How the business bills

Each client gets two separate invoices, and both are kept:

1. **Deposit invoice** (`invoice_type: "deposit"`): $1,000 SGD taken before booking. It shows the
   full price breakdown and the balance payable later.
2. **Balance invoice** (`invoice_type: "balance"`): sent the day before the procedure. New invoice
   number, total less the deposit, and it names the deposit invoice (`deposit_invoice_no`).
3. **Receipt** (`invoice_type: "receipt"`), only if asked: PAID stamp, $0 remaining.

Never edit or overwrite an earlier invoice. Each document gets its own number and its own
Invoice Log row. All amounts are in SGD.

Standard prices (use unless the user says otherwise):

| Item | Price (SGD) |
|---|---|
| Shaved FUE package (4,000 grafts, 2 hotel nights) | $4,888 |
| Non-shaved FUE package (2 hotel nights) | $6,688 |
| Graft top-up | $1,000 per 1,000-graft block (`extra_graft_blocks`) |
| Additional hotel night | $64 per night for now (`extra_hotel_nights`); still ask each time |

Each package lists: Airport Pick Up, 2 Nights Hotel Stay, Body Check & Consultation,
Hair Transplant, Post Procedure Medication, Remote Follow Up.

## Every time, before generating

Ask the user to confirm or fill in all of these in one message. Don't generate until they answer:

1. Client details: full name (as on passport), nationality, mobile, email, passport no. (optional).
   For a balance invoice of an existing client, read their row in the Client Tracker and confirm
   the details instead of asking again.
2. Package: shaved or non-shaved, and whether the standard price applies.
3. Invoice type: deposit, balance, or receipt. Deposit paid (default $1,000).
4. Procedure date.
5. **Additional grafts?** How many 1,000-graft blocks ($1,000 each unless told otherwise).
6. **Additional hotel nights?** How many, and confirm the price ($64 per night unless told otherwise).
7. **Any discount?** Amount and label (e.g. "Referral Discount", "Hotel Offset").
8. Payment method (default PayNow), invoice date (default today), and any remarks.

For a balance invoice, start from the deposit invoice's spec in the Invoice Log (column Q) and ask
only what changed: extra grafts, hotel nights or discounts agreed since the deposit.

Then show a short price breakdown (package + add-ons - discounts = total, less deposit = due)
and get a yes before making the PDF.

Invoice number: day + month + 2-digit year with no padding (14 Sep 2026 -> `14926`). Check the
Invoice Log for a clash; if one exists add `-2`, `-3`. The balance invoice always gets its own number.

## Generate the PDF

Write the spec to the scratchpad and run the script from the repo root:

```json
{
  "invoice_type": "balance",
  "date": "2026-11-19",
  "invoice_no": "191126",
  "deposit_invoice_no": "191026",
  "package": "shaved",
  "package_price": 4888,
  "surgery_date": "2026-11-20",
  "grafts_included": 4000,
  "hotel_nights": 2,
  "extra_graft_blocks": 1,
  "extra_hotel_nights": 1,
  "hotel_night_price": 64,
  "payment_method": "PayNow",
  "client": {"name": "...", "nationality": "Singaporean", "mobile": "+65 ...", "email": "...", "passport": "..."},
  "line_items": [{"description": "Any other charge", "amount": 100}],
  "discounts": [{"description": "Discount", "amount": 800}],
  "deposit": 1000,
  "notes": ["Optional remark shown under the totals."]
}
```

Only `client.name` is required. Defaults: today's date, auto invoice number, shaved package at the
standard price, standard inclusions, $1,000 deposit, PayNow, $1,000 per graft block, $64 per hotel
night. `line_items` takes any other charge (`amount`, or `qty` + `unit_price`). `inclusions` (a list)
replaces the default inclusion bullets, and `package_name` replaces the package title.

```
python3 .claude/skills/hair-transplant-invoice/generate_invoice.py <scratchpad>/<spec>.json -o "<scratchpad>/Invoice <no> - <Name>.pdf"
```

The script prints the totals as JSON. Check them against the breakdown the user approved, render
page 1 to PNG (pypdfium2) and look at it, then **send the PDF to the user with SendUserFile**
(`display: "attach"`, so they can download it and send it to the client).

## Record it in the sheet

The sheet is the Google Sheet titled `Invoice ` (with a trailing space). Find it with Google Drive
search (`title contains 'Invoice' and mimeType = 'application/vnd.google-apps.spreadsheet'`) or
use the link the user gives. Read the google-workspace skill first. Prefix invoice numbers and
mobile numbers with `'` so they stay text. Discounts are positive numbers.

**Invoice Log** tab: one row per invoice document, added under the last row. Columns A to Q:
Invoice No | Invoice Type (Deposit/Balance/Receipt) | Invoice Date | Client Name | Package |
Package Price (SGD) | Add-ons (SGD) | Add-on Details | Discount (SGD) | Discount Details |
Total (SGD) | Deposit (SGD) | Amount Due (SGD) | Payment Method | Paid? (Yes/No) | Notes |
Invoice Spec (JSON)
- K: `=IF(Fn="","",Fn+Gn-In)`. M: `=IF(Kn="","",IF(Bn="Deposit",Ln,IF(Bn="Receipt",0,Kn-Ln)))`.
- Q holds the exact JSON spec used (one line), so the PDF can be regenerated identically.

**Client Tracker** tab: one row per client. Columns A to U:
Client Name | Nationality | Mobile | Email | Passport No | Package | Surgery Date |
Package Price (SGD) | Add-ons (SGD) | Add-on Details | Discount (SGD) | Total (SGD) |
Deposit Invoice No | Deposit Invoice Date | Deposit Paid (SGD) | Balance Invoice No |
Balance Invoice Date | Balance Due (SGD) | Status | Notes | Old Invoice Tab
- L: `=IF(Hn="","",Hn+In-Kn)`. R: `=IF(Ln="","",Ln-On)`.
- Deposit invoice: add the client's row with M, N, O filled and Status "Deposit invoiced".
- Balance invoice: update the same row (P, Q, any changed add-ons or discount) and set Status
  "Balance invoiced". Never add a second row for the same client.
- Status dropdown: Deposit invoiced, Deposit paid, Balance invoiced, Paid in full, Surgery done, Cancelled.

Read both rows back and check the totals match the PDF.

Older invoices (before separate deposit and balance invoices) live in tabs named
`YYYY-MM-DD First name`; the original sheet template is the `Old Template` tab. The user can save
PDFs into the private "Invoice PDFs" Drive folder next to the sheet.
