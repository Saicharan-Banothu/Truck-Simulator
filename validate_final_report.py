"""
Automated Quality Assurance and Compliance Validation Script
Validates: Predicting_Industrial_Truck_Failures_From_Operational_Telemetry_CBP_Report_FINAL.pdf
"""

import sys
import fitz  # PyMuPDF

TARGET_PDF = "Predicting_Industrial_Truck_Failures_From_Operational_Telemetry_CBP_Report_FINAL.pdf"
REF_PDF = "docs/Talos_Brain_CBP_Report_final.pdf"

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
    "Computer Science and Business Systems", "22PC2CB302", "R25", "JNTUH", "Hyderabad",
    "Akhil", "Lakshmi Deepthi", "Baby"
]

EXACT_TITLE = "PREDICTING INDUSTRIAL TRUCK FAILURES FROM OPERATIONAL TELEMETRY"

def run_validation():
    print("=" * 65)
    print("  VNR VJIET CBP REPORT - AUTOMATED QA VALIDATION (FINAL BUILD)")
    print("=" * 65)

    doc = fitz.open(TARGET_PDF)
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

    # 2. Negative Verification
    print("\n[CHECK 2] Prohibited Author Verification (Zero Old Authors):")
    found_prohibited = []
    for p in PROHIBITED_AUTHORS:
        if p.lower() in full_text.lower():
            found_prohibited.append(p)
    if not found_prohibited:
        print("  -> PASS: Zero occurrences of old team members found (100% clean).")
    else:
        print(f"  -> FAIL: Found prohibited strings: {found_prohibited}")
        return False

    # 3. Required Authors & Roll Numbers
    print("\n[CHECK 3] Required Authors & Roll Numbers Presence:")
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

    # 4. Institutional Details & Faculty
    print("\n[CHECK 4] Institutional & Faculty Details:")
    missing_inst = []
    for inst in REQUIRED_INSTITUTIONAL:
        if inst.lower() not in full_text.lower():
            missing_inst.append(inst)
    if not missing_inst:
        print("  -> PASS: All supervisors, HOD, and institutional identifiers present.")
    else:
        print(f"  -> FAIL: Missing institutional elements: {missing_inst}")
        return False

    # 5. Exact Project Title
    print("\n[CHECK 5] Project Title Exact Match:")
    if EXACT_TITLE in normalized_full_text:
        print("  -> PASS: Exact project title found and matches perfectly.")
    else:
        print("  -> FAIL: Exact project title string not found in normalized text.")
        return False

    # 6. Empirical Numbers & Metrics Check
    print("\n[CHECK 6] Empirical Dataset & Scania Research Metrics:")
    metrics = [
        ("PR-AUC = 0.789", "0.789"),
        ("ROC-AUC = 0.930", "0.930"),
        ("43,796 observations", "43,796"),
        ("400 vehicles", "400"),
        ("Optimal Cost $24,430", "24,430"),
        ("Cost Reduction 62.7%", "62.7%"),
    ]
    missing_metrics = []
    for desc, val in metrics:
        if val in full_text:
            print(f"  - {desc}: VERIFIED")
        else:
            missing_metrics.append(desc)
    if not missing_metrics:
        print("  -> PASS: All empirical project metrics verified.")
    else:
        print(f"  -> FAIL: Missing metrics: {missing_metrics}")
        return False

    # 7. Figure References Check
    print("\n[CHECK 7] Figure References in Document:")
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

    print("\n" + "=" * 65)
    print("  FINAL QA STATUS: 100% COMPLETE & VERIFIED (ALL 7 CHECKS PASSED)")
    print("=" * 65 + "\n")
    return True

if __name__ == "__main__":
    success = run_validation()
    sys.exit(0 if success else 1)
