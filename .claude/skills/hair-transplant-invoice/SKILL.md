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
| Non-shaved FUE package (4,000 grafts, 2 hotel nights) | $6,688 |
| Graft top-up | $1,000 per 1,000-graft block (`extra_graft_blocks`). Grafts are only sold in whole blocks of 1,000: never 500 or other part blocks |
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
5. **Additional grafts?** How many 1,000-graft blocks ($1,000 each unless told otherwise). Only whole
   blocks of 1,000; if the user gives a number that isn't a multiple of 1,000, ask them to confirm.
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

The PDF design is final and approved by the user: Jost typeface, a two-column grid, a full-width
tinted client band, one totals panel aligned with the item amounts, the PayNow QR beside it, and
numbered terms. Don't change the layout, fonts, colours or wording unless the user asks.

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

First get the PayNow QR. It is the only QR to use on invoices (VDAY PTE. LTD.), and it lives only on
the `Invoice Template` tab of the private sheet, never in this repo. Export the sheet with Drive
`download_file_content` (`exportMimeType: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`);
the result is too large to show and is saved to a file. Then:

```
python3 .claude/skills/hair-transplant-invoice/extract_qr.py <saved result file> <scratchpad>/paynow_qr.png
python3 .claude/skills/hair-transplant-invoice/generate_invoice.py <scratchpad>/<spec>.json -o "<scratchpad>/Invoice <no> - <Name>.pdf" --qr <scratchpad>/paynow_qr.png
```

Do the export once per conversation and reuse the PNG. If the QR can't be extracted, stop and tell
the user rather than sending an invoice without it. Deposit and balance invoices show the QR with
the amount to pay and the invoice number as reference; receipts don't.

The script prints the totals as JSON. Check them against the breakdown the user approved, render
page 1 to PNG (pypdfium2) and look at it, then **send the PDF to the user with SendUserFile**
(`display: "attach"`, so they can download it and send it to the client).

## Record it in the sheet

The sheet is the Google Sheet titled `Invoice ` (with a trailing space). Find it with Google Drive
search (`title contains 'Invoice' and mimeType = 'application/vnd.google-apps.spreadsheet'`) or
use the link the user gives. Read the google-workspace skill first. Prefix invoice numbers and
mobile numbers with `'` so they stay text. Discounts are positive numbers.

**Invoice tab**: for every invoice, duplicate the `Invoice Template` tab (`duplicateSheet`, insert
after the last client tab) and name it `YYYY-MM-DD First name Deposit` or `... Balance`. It keeps the
logo and QR. Fill only these cells:
- B7 name, B8 nationality, B9 mobile, B10 email; G7 invoice no. (with `'`), G8 date, G9 payment method.
- A13 package name, G13 package price. A14:A18 inclusions (edit the hotel nights line if changed).
- Add-ons in rows 19 to 21: description in A, amount in G (e.g. "Top Up 1000 Grafts", 1000).
- G22 discount as a negative number (clear E22 if there's no discount).
- G24 total and G27 balance are formulas; don't overwrite them. G26 deposit.
- Deposit invoice: F26 "Deposit Due", F27 "Balance Due". Balance invoice: F26
  "Deposit Paid (Inv. <no>)", F27 "Balance Due".
Read the tab back and check G24 and G27 match the PDF. Never edit the template tab itself.

**Invoice Log** tab: one row per invoice document, added under the last row. Columns A to Q:
Invoice No | Invoice Type (Deposit/Balance/Receipt) | Invoice Date | Client Name | Package |
Package Price (SGD) | Add-ons (SGD) | Add-on Details | Discount (SGD) | Discount Details |
Total (SGD) | Deposit (SGD) | Amount Due (SGD) | Payment Method | Paid? (Yes/No) | Notes |
Invoice Spec (JSON)
- K: `=IF(Fn="","",Fn+Gn-In)`. M: `=IF(Kn="","",IF(Bn="Deposit",Ln,IF(Bn="Receipt",0,Kn-Ln)))`.
- Q holds the exact JSON spec used (one line), so the PDF can be regenerated identically.

**Client Tracker** tab: one row per client. Columns A to W:
Client Name | Nationality | Mobile | Email | Passport No | Package | Surgery Date |
Package Price (SGD) | Add-ons (SGD) | Add-on Details | Discount (SGD) | Total (SGD) |
Deposit Invoice No | Deposit Invoice Date | Deposit Paid (SGD) | Balance Invoice No |
Balance Invoice Date | Balance Due (SGD) | Status | Fully Paid (Yes/No) | Surgery Done (Yes/No) |
Notes | Invoice Tab
- L: `=IF(Hn="","",Hn+In-Kn)`. R: `=IF(Ln="","",Ln-On)`.
- Deposit invoice: add the client's row with M, N, O filled and Status "Deposit invoiced".
- Balance invoice: update the same row (P, Q, any changed add-ons or discount) and set Status
  "Balance invoiced". Never add a second row for the same client.
- W: `=HYPERLINK("#gid=<sheetId of the client's latest invoice tab>","Open")`.
- Status dropdown: Deposit invoiced, Deposit paid, Balance invoiced, Paid in full, Surgery done,
  Unresponsive (client stopped replying with money owed), Cancelled.

Read both rows back and check the totals match the PDF.

## Payment and surgery check-ins

Columns T (Fully Paid) and U (Surgery Done) are only ever set from what the user tells you; never
assume a client paid or had surgery.

- At the start of any invoice or tracking request, read the Client Tracker and list clients with a
  balance invoice where T or U is not "Yes" (skip Cancelled; for Unresponsive, only remind about the amount owed). Ask in one short question, e.g.
  "Before we start: has <client> paid the $<balance> balance, and has their surgery been done?"
  Prioritise clients whose surgery date has passed. Don't ask again about a client the user said is
  still pending in this conversation.
- When the user answers (or says on their own that a client paid or finished surgery), set T and U,
  set Status ("Paid in full" when paid, "Surgery done" when both are done), and in the Invoice Log
  set Paid? to "Yes" on that client's balance invoice row.
- When the user asks who still owes money or who is pending, answer from the tracker: name,
  balance due, surgery date, and what is outstanding.

Older invoices (before separate deposit and balance invoices) live in tabs named
`YYYY-MM-DD First name`; the original sheet template is the `Old Template` tab. The user can save
PDFs into the private "Invoice PDFs" Drive folder next to the sheet.
