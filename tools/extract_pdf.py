"""Extract a PDF into page-marked text plus embedded images.

Usage (from the repo root):
    .venv/bin/python -I tools/extract_pdf.py "docs/<file>.pdf" <source-id>

Writes:
    kb/raw/<source-id>.txt          page-marked text; well-formed tables re-emitted as `a | b | c` rows
    kb/assets/<source-id>/pN_i.png  embedded images (diagrams), N = page number
Table fragments (header row with empty cells) are dropped; they are duplicates of the page text.
"""
import os
import sys

import pdfplumber
import pypdf


def main(src, source_id):
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    raw_path = os.path.join(root, "kb", "raw", f"{source_id}.txt")
    asset_dir = os.path.join(root, "kb", "assets", source_id)

    with pdfplumber.open(src) as pdf, open(raw_path, "w") as out:
        for n, page in enumerate(pdf.pages, 1):
            out.write(f"\n\n===== PAGE {n} =====\n")
            out.write(page.extract_text() or "")
            for table in page.extract_tables():
                if len(table) < 2 or len(table[0]) < 2 or not all((c or "").strip() for c in table[0]):
                    continue
                out.write("\n[TABLE]\n")
                for row in table:
                    out.write(" | ".join((c or "").replace("\n", " ") for c in row) + "\n")
        pages = len(pdf.pages)

    images = 0
    for n, page in enumerate(pypdf.PdfReader(src).pages, 1):
        for i, image in enumerate(page.images):
            os.makedirs(asset_dir, exist_ok=True)
            ext = os.path.splitext(image.name)[1] or ".png"
            with open(os.path.join(asset_dir, f"p{n}_{i}{ext}"), "wb") as f:
                f.write(image.data)
            images += 1

    print(f"{source_id}: {pages} pages -> {raw_path}; {images} image(s) -> {asset_dir}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2])
