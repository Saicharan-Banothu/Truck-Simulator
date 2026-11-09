"""
Render all 31 pages of the final PDF to PNG images for visual QA inspection.
"""

import pymupdf
from pathlib import Path

PDF_PATH = "Predicting_Industrial_Truck_Failures_From_Operational_Telemetry_CBP_Report_OCTOBER_2026_FINAL.pdf"
OUTPUT_DIR = Path("generated_page_renders")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

doc = pymupdf.open(PDF_PATH)
print(f"Rendering {len(doc)} pages of {PDF_PATH} at 150 DPI...")

for i, page in enumerate(doc):
    zoom = 150.0 / 72.0
    mat = pymupdf.Matrix(zoom, zoom)
    pix = page.get_pixmap(matrix=mat)
    out_file = OUTPUT_DIR / f"page_{i+1:02d}.png"
    pix.save(str(out_file))
    print(f"Saved {out_file.name} ({pix.width}x{pix.height})")

print("Rendering complete!")
