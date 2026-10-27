import pdfplumber
from pathlib import Path
import sys

sys.stdout.reconfigure(encoding='utf-8')

pdf_path = Path(r"02_raw/copper/copper__icsg__world_refined_copper_production_and_usage_trends__original.pdf")
with pdfplumber.open(pdf_path) as pdf:
    print(f"Total pages: {len(pdf.pages)}")
    for i, page in enumerate(pdf.pages):
        tables = page.extract_tables()
        print(f"Page {i+1}: {len(tables)} tables")
        for t_idx, t in enumerate(tables):
            print(f"  --- Table {t_idx+1} ({len(t)}x{len(t[0]) if t else 0}) ---")
            for r in t[:10]:
                print("   ", [str(c).replace('\n', ' ')[:25] for c in r if c is not None])
