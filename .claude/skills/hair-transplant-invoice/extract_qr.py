#!/usr/bin/env python3
"""Pull the PayNow QR image out of the "Invoice Template" tab of an .xlsx export.

The QR lives only in the user's private Google Sheet, never in this repo. Export the sheet with
Google Drive download_file_content (exportMimeType .xlsx); the tool saves the JSON result to a
file. Then:

    python3 extract_qr.py <saved-result.json or .xlsx> <out.png> [--tab "Invoice Template"]

The tab has two images: the Vday logo (square, light blue) and the QR. The QR is the one that is
not the logo: the script picks the image with the most dark, saturated pixels.
"""
import argparse
import base64
import io
import json
import posixpath
import re
import sys
import zipfile

from PIL import Image


def open_xlsx(path):
    with open(path, "rb") as f:
        raw = f.read()
    if raw[:2] == b"PK":
        return zipfile.ZipFile(io.BytesIO(raw))
    data = json.loads(raw)
    return zipfile.ZipFile(io.BytesIO(base64.b64decode(data["content"])))


def rel_targets(z, rels_path):
    if rels_path not in z.namelist():
        return {}
    xml = z.read(rels_path).decode()
    out = {}
    for rel in re.findall(r"<Relationship [^>]*>", xml):
        rid = re.search(r'Id="([^"]+)"', rel).group(1)
        out[rid] = re.search(r'Target="([^"]+)"', rel).group(1)
    return out


def tab_images(z, tab):
    wb = z.read("xl/workbook.xml").decode()
    m = re.search(r'<sheet [^>]*name="%s"[^>]*r:id="([^"]+)"' % re.escape(tab), wb)
    if not m:
        sys.exit(f"Tab '{tab}' not found in the export.")
    sheet = posixpath.normpath(posixpath.join("xl", rel_targets(z, "xl/_rels/workbook.xml.rels")[m.group(1)]))
    sheet_rels = posixpath.join(posixpath.dirname(sheet), "_rels", posixpath.basename(sheet) + ".rels")
    images = []
    for target in rel_targets(z, sheet_rels).values():
        if "drawings/" not in target:
            continue
        drawing = posixpath.normpath(posixpath.join(posixpath.dirname(sheet), target))
        drawing_rels = posixpath.join(posixpath.dirname(drawing), "_rels", posixpath.basename(drawing) + ".rels")
        for img in rel_targets(z, drawing_rels).values():
            images.append(posixpath.normpath(posixpath.join(posixpath.dirname(drawing), img)))
    return images


def qr_score(im):
    small = im.convert("RGB").resize((64, 64))
    px = small.tobytes()
    dark = sum(1 for i in range(0, len(px), 3) if (px[i] + px[i + 1] + px[i + 2]) / 3 < 140)
    return dark / (64 * 64)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("export")
    ap.add_argument("out")
    ap.add_argument("--tab", default="Invoice Template")
    args = ap.parse_args()

    z = open_xlsx(args.export)
    paths = tab_images(z, args.tab)
    if not paths:
        sys.exit(f"No images on tab '{args.tab}'.")
    scored = sorted(((qr_score(Image.open(io.BytesIO(z.read(p)))), p) for p in paths), reverse=True)
    best = scored[0][1]
    Image.open(io.BytesIO(z.read(best))).convert("RGB").save(args.out)
    print(json.dumps({"tab": args.tab, "images": paths, "qr": best, "saved": args.out}))


if __name__ == "__main__":
    main()
