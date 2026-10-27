import pdfplumber
from pathlib import Path
import sys

sys.stdout.reconfigure(encoding='utf-8')

pdf_path = Path(r"02_raw/silver/silver__silver_institute__world_silver_survey__2024__original.pdf")
print(f"Opening {pdf_path.name}...")

with pdfplumber.open(pdf_path) as pdf:
    print(f"Total pages: {len(pdf.pages)}")
    found_pages = []
    for i, page in enumerate(pdf.pages[:25]): # usually in first 15-20 pages
        text = page.extract_text() or ""
        if "supply and demand" in text.lower() and "mine production" in text.lower():
            print(f"Found candidate page: {i+1}")
            found_pages.append(i+1)
            tables = page.extract_tables()
            print(f"  Extracted {len(tables)} tables on page {i+1}")
            for t_idx, t in enumerate(tables):
                print(f"  --- Table {t_idx+1} (shape {len(t)}x{len(t[0]) if t else 0}) ---")
                for r in t[:8]:
                    print("   ", [str(c).replace('\n', ' ')[:20] for c in r if c is not None])
