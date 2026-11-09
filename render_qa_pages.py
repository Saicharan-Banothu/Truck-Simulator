"""
Render every page of the generated report to high-resolution PNGs for QA inspection.
"""

import os
import fitz

OUTPUT_DIR = "generated_page_renders"
os.makedirs(OUTPUT_DIR, exist_ok=True)

doc = fitz.open("Predicting_Industrial_Truck_Failures_From_Operational_Telemetry_CBP_Report.pdf")
print(f"Rendering {len(doc)} pages...")

for i, page in enumerate(doc):
    pix = page.get_pixmap(dpi=150)
    out_path = os.path.join(OUTPUT_DIR, f"page_{i+1:02d}.png")
    pix.save(out_path)
    print(f"Rendered {out_path} ({pix.width}x{pix.height})")

print("Rendering complete.")
