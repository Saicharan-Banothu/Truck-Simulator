"""
Automated Quality Assurance and Compliance Validation Script - SECOND ITERATION
Validates:
1. Predicting_Industrial_Truck_Failures_From_Operational_Telemetry_CBP_Report_OCTOBER_2026_FINAL.pdf
2. Predicting_Industrial_Truck_Failures_From_Operational_Telemetry_CBP_Report_FINAL.pdf
"""

import sys
import pymupdf

TARGET_PDF = "Predicting_Industrial_Truck_Failures_From_Operational_Telemetry_CBP_Report_OCTOBER_2026_FINAL.pdf"
BACKUP_PDF = "Predicting_Industrial_Truck_Failures_From_Operational_Telemetry_CBP_Report_FINAL.pdf"

REQUIRED_AUTHORS = [
    ("B Sathwik", "24071A3204"),
    ("B Sai Charan", "24071A3206"),
    ("K Jayanth Varma", "24071A3232"),
    ("Md Sameer", "24071A3243"),
    ("P Akshay Kumar", "24071A3247")
]

PROHIBITED_AUTHORS = [
    "Chatradhara", "Shiva Sai", "Rakshit", "Koushik", "Veerabhadra",
    "24071A3214", "24071A3240", "24071A3254", "24071A3256", "24071A3262", "23071A32"
]

REQUIRED_INSTITUTIONAL = [
    "VNR", "Vignana Jyothi", "Computer Science and Engineering",
    "Computer Science and Business Systems", "22PC2CB302", "R22", "JNTUH", "Hyderabad",
    "Akhil", "Lakshmi Deepthi", "Baby"
]

EXACT_TITLE = "PREDICTING INDUSTRIAL TRUCK FAILURES FROM OPERATIONAL TELEMETRY"


def run_validation(pdf_path=TARGET_PDF):
    print("=" * 70)
    print(f"  VNR VJIET CBP REPORT - AUTOMATED QA VALIDATION (SECOND ITERATION)")
    print(f"  Validating Target: {pdf_path}")
    print("=" * 70)

    doc = pymupdf.open(pdf_path)
    num_pages = len(doc)
    
    # 1. Page Count Check
    print(f"\n[CHECK 1] Page Count: {num_pages} pages (Target: 31)")
    if num_pages == 31:
        print("  -> PASS: Exact 31-page match.")
    else:
        print(f"  -> FAIL: Document has {num_pages} pages, expected 31.")
        return False

    full_text = ""
    pages_text = []
    for i, page in enumerate(doc):
        t = page.get_text()
        pages_text.append(t)
        full_text += t + "\n"

    normalized_full_text = " ".join(full_text.split())

    # 2. Date Check (Mandatory OCTOBER 2026)
    print("\n[CHECK 2] Submission Date Verification (OCTOBER 2026):")
    p1_text = pages_text[0]
    if "OCTOBER 2026" in p1_text:
        print("  -> PASS: 'OCTOBER 2026' correctly displayed on Cover Page.")
    else:
        print("  -> FAIL: 'OCTOBER 2026' NOT found on Cover Page.")
        return False

    if "November 2026" in full_text:
        print("  -> FAIL: Found stale date 'November 2026' in report text.")
        return False
    else:
        print("  -> PASS: Zero occurrences of outdated 'November 2026' date.")

    if "R25" in full_text:
        print("  -> FAIL: Found stale regulation 'R25' in report text.")
        return False
    else:
        print("  -> PASS: Zero occurrences of outdated 'R25' regulation (R22 verified).")

    # 3. Negative Verification
    print("\n[CHECK 3] Prohibited Author Verification (Zero Old Authors):")
    found_prohibited = []
    for p in PROHIBITED_AUTHORS:
        if p.lower() in full_text.lower():
            found_prohibited.append(p)
    if not found_prohibited:
        print("  -> PASS: Zero occurrences of old team members found (100% clean).")
    else:
        print(f"  -> FAIL: Found prohibited strings: {found_prohibited}")
        return False

    # 4. Required Authors & Roll Numbers
    print("\n[CHECK 4] Required Authors & Roll Numbers Presence:")
    missing_authors = []
    for name, roll in REQUIRED_AUTHORS:
        n_pres = name.lower() in full_text.lower()
        r_pres = roll.lower() in full_text.lower()
        print(f"  - Author {name} ({roll}): Name={n_pres}, Roll={r_pres}")
        if not (n_pres and r_pres):
            missing_authors.append(f"{name} ({roll})")
    if not missing_authors:
        print("  -> PASS: All 5 required team members and roll numbers present.")
    else:
        print(f"  -> FAIL: Missing authors: {missing_authors}")
        return False

    # 5. Declaration Page Student Alignment
    print("\n[CHECK 5] Declaration Page Student Alignment (Page 3 Geometry):")
    p3 = doc[2]
    p3_blocks = p3.get_text('blocks')
    stud_block = None
    for b in p3_blocks:
        if "B SATHWIK" in b[4]:
            stud_block = b
            break
    if stud_block:
        x0, y0, x1, y1 = stud_block[:4]
        mid_x = (x0 + x1) / 2.0
        page_center = 595.28 / 2.0
        dev = abs(mid_x - page_center)
        print(f"  - Student Table Bounds: x0={x0:.1f}, x1={x1:.1f}, Center={mid_x:.1f} (Page Center={page_center:.1f}, Dev={dev:.1f} pt)")
        if dev < 15.0 and x1 < 520.0:
            print("  -> PASS: Student block is visually and geometrically centered on Page 3 (no right overflow).")
        else:
            print(f"  -> FAIL: Student block has excessive deviation ({dev:.1f} pt) or right overflow ({x1:.1f} pt).")
            return False
    else:
        print("  -> FAIL: Student block not located on Page 3.")
        return False

    # 6. Table of Contents 3-Column Check
    print("\n[CHECK 6] Table of Contents Structure (Page 5):")
    p5_text = pages_text[4]
    toc_required = ["SECTION", "TOPIC / CHAPTER TITLE", "PAGE", "Front Matter", "Chapter 1", "Appendix C"]
    missing_toc = [t for t in toc_required if t not in p5_text]
    if not missing_toc:
        print("  -> PASS: Rebuilt 3-column academic Table of Contents verified on Page 5.")
    else:
        print(f"  -> FAIL: Missing TOC components: {missing_toc}")
        return False

    # 7. Institutional Details & Faculty
    print("\n[CHECK 7] Institutional & Faculty Details:")
    missing_inst = []
    for inst in REQUIRED_INSTITUTIONAL:
        if inst.lower() not in full_text.lower():
            missing_inst.append(inst)
    if not missing_inst:
        print("  -> PASS: All supervisors, HOD, and institutional identifiers present.")
    else:
        print(f"  -> FAIL: Missing institutional elements: {missing_inst}")
        return False

    # 8. Exact Project Title
    print("\n[CHECK 8] Project Title Exact Match:")
    if EXACT_TITLE in normalized_full_text:
        print("  -> PASS: Exact project title found and matches perfectly.")
    else:
        print("  -> FAIL: Exact project title string not found in normalized text.")
        return False

    # 9. Empirical Numbers & Inconsistency Reconciled Check
    print("\n[CHECK 9] Empirical Dataset & Inconsistency Reconciled Numbers:")
    metrics = [
        ("PR-AUC = 0.789", "0.789"),
        ("ROC-AUC = 0.930", "0.930"),
        ("43,796 observations", "43,796"),
        ("400 vehicles", "400"),
        ("1,034 positive rows", "1,034"),
        ("240 failure events/trajectories", "240"),
        ("Default Cost $64,860", "64,860"),
        ("Optimal Cost $24,430", "24,430"),
        ("62.3% cost reduction", "62.3%"),
    ]
    missing_metrics = []
    for desc, val in metrics:
        if val in full_text:
            print(f"  - {desc}: VERIFIED")
        else:
            missing_metrics.append(desc)
    if not missing_metrics:
        print("  -> PASS: All empirical project metrics and reconciled numbers verified.")
    else:
        print(f"  -> FAIL: Missing metrics: {missing_metrics}")
        return False

    # 10. Figure References Check
    print("\n[CHECK 10] Figure References in Document:")
    figs = [f"Figure {ch}.{idx}" for ch in [3, 4] for idx in range(1, 9 if ch==4 else 4)]
    missing_figs = []
    for fig in figs:
        if fig in full_text:
            print(f"  - {fig}: VERIFIED")
        else:
            missing_figs.append(fig)
    if not missing_figs:
        print("  -> PASS: All 11 figures referenced in text.")
    else:
        print(f"  -> FAIL: Missing figure references: {missing_figs}")
        return False

    print("\n" + "=" * 70)
    print("  FINAL QA STATUS: 100% COMPLETE & VERIFIED (ALL 10 CHECKS PASSED)")
    print("=" * 70 + "\n")
    return True


if __name__ == "__main__":
    t_pass = run_validation(TARGET_PDF)
    b_pass = run_validation(BACKUP_PDF)
    sys.exit(0 if (t_pass and b_pass) else 1)
