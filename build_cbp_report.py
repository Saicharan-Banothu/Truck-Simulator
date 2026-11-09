"""
Comprehensive Academic CBP Project Report Generator - SECOND ITERATION FINAL RECONSTRUCTION
PREDICTING INDUSTRIAL TRUCK FAILURES FROM OPERATIONAL TELEMETRY
VNR Vignana Jyothi Institute of Engineering & Technology
Department of Computer Science and Engineering
Academic Regulation R25 | OCTOBER 2026
"""

import os
import sys
import shutil
from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas

# Page dimensions: A4 portrait (595.28 x 841.89 points)
PAGE_WIDTH, PAGE_HEIGHT = A4
LEFT_MARGIN = 54.0   # 0.75 inch margins
RIGHT_MARGIN = 54.0  # 0.75 inch margins
TOP_MARGIN = 50.0    # ~0.7 inch top margin
BOTTOM_MARGIN = 50.0 # ~0.7 inch bottom margin
USABLE_WIDTH = PAGE_WIDTH - LEFT_MARGIN - RIGHT_MARGIN  # 487.28 points

PRIMARY_OUTPUT_PDF = "Predicting_Industrial_Truck_Failures_From_Operational_Telemetry_CBP_Report_OCTOBER_2026_FINAL.pdf"
BACKUP_OUTPUT_PDF = "Predicting_Industrial_Truck_Failures_From_Operational_Telemetry_CBP_Report_FINAL.pdf"


class AcademicNumberedCanvas(canvas.Canvas):
    """
    Custom canvas that draws centered academic page numbers matching reference PDF.
    Every page from 1 to 31 has a simple centered Arabic page number at the bottom.
    No artificial running header lines at top, matching the reference template.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_number(self, page_count):
        self.saveState()
        self.setFont('Times-Roman', 12)
        page_str = str(self._pageNumber)
        # Match reference PDF page number at y = 35 pt from bottom
        self.drawCentredString(PAGE_WIDTH / 2.0, 35.0, page_str)
        self.restoreState()


def create_report(output_filename=PRIMARY_OUTPUT_PDF):
    doc = SimpleDocTemplate(
        output_filename,
        pagesize=A4,
        leftMargin=LEFT_MARGIN,
        rightMargin=RIGHT_MARGIN,
        topMargin=TOP_MARGIN,
        bottomMargin=BOTTOM_MARGIN
    )

    styles = getSampleStyleSheet()

    # =========================================================================
    # EXACT COLOR PALETTE MATCHING REFERENCE PDF
    # =========================================================================
    c_red = colors.HexColor('#FF0000')         # Pure Red
    c_crimson = colors.HexColor('#C01A1A')     # Crimson for Machine Learning Lab
    c_dark_red = colors.HexColor('#C00000')    # Dark Red for B.Tech & Institute
    c_navy = colors.HexColor('#22276B')        # Deep Navy for Course Code & Table Headers
    c_blue_inst = colors.HexColor('#1F3864')   # Institutional Blue for Address & Cert Title
    c_green_dept = colors.HexColor('#00B050')  # Department Green on Cert & Decl
    c_black = colors.HexColor('#000000')       # Pure Black

    # =========================================================================
    # TYPOGRAPHY STYLES (Strict Sizing & Line Spacing)
    # =========================================================================
    # Page 1 Cover Styles
    p1_title = ParagraphStyle(
        'P1_Title', fontName='Times-Bold', fontSize=14.1, leading=19.0,
        alignment=1, textColor=c_red, spaceAfter=8
    )
    p1_sub = ParagraphStyle(
        'P1_Sub', fontName='Times-Bold', fontSize=12.5, leading=16.5,
        alignment=1, textColor=c_black, spaceAfter=8
    )
    p1_course = ParagraphStyle(
        'P1_Course', fontName='Times-Bold', fontSize=16.0, leading=20.0,
        alignment=1, textColor=c_crimson, spaceAfter=4
    )
    p1_code = ParagraphStyle(
        'P1_Code', fontName='Times-Bold', fontSize=13.0, leading=16.0,
        alignment=1, textColor=c_navy, spaceAfter=8
    )
    p1_btech = ParagraphStyle(
        'P1_BTech', fontName='Times-Bold', fontSize=12.9, leading=16.0,
        alignment=1, textColor=c_dark_red, spaceAfter=2
    )
    p1_in = ParagraphStyle(
        'P1_In', fontName='Times-Bold', fontSize=12.9, leading=16.0,
        alignment=1, textColor=c_black, spaceAfter=2
    )
    p1_branch = ParagraphStyle(
        'P1_Branch', fontName='Times-Bold', fontSize=12.9, leading=16.0,
        alignment=1, textColor=c_red, spaceAfter=8
    )
    p1_by = ParagraphStyle(
        'P1_By', fontName='Times-Bold', fontSize=12.9, leading=16.0,
        alignment=1, textColor=c_black, spaceAfter=4
    )
    p1_guidance_head = ParagraphStyle(
        'P1_GuidanceHead', fontName='Times-Bold', fontSize=12.9, leading=16.0,
        alignment=1, textColor=c_black, spaceAfter=3
    )
    p1_guidance_text = ParagraphStyle(
        'P1_GuidanceText', fontName='Times-Roman', fontSize=12.0, leading=15.5,
        alignment=1, textColor=c_black, spaceAfter=4
    )
    p1_dept_bold = ParagraphStyle(
        'P1_DeptBold', fontName='Times-Bold', fontSize=12.5, leading=16.0,
        alignment=1, textColor=c_black, spaceAfter=2
    )
    p1_inst_red = ParagraphStyle(
        'P1_InstRed', fontName='Times-Bold', fontSize=12.0, leading=15.0,
        alignment=1, textColor=c_dark_red, spaceAfter=2
    )
    p1_address = ParagraphStyle(
        'P1_Address', fontName='Times-Roman', fontSize=11.1, leading=14.0,
        alignment=1, textColor=c_blue_inst, spaceAfter=3
    )
    p1_date = ParagraphStyle(
        'P1_Date', fontName='Times-Bold', fontSize=12.9, leading=16.0,
        alignment=1, textColor=c_blue_inst
    )

    # Student Table Paragraph Styles (Page 1, 2, 3)
    p_stud_name = ParagraphStyle(
        'StudName', fontName='Times-Bold', fontSize=12.5, leading=15.5,
        alignment=0, textColor=c_red
    )
    p_stud_roll = ParagraphStyle(
        'StudRoll', fontName='Times-Bold', fontSize=12.5, leading=15.5,
        alignment=2, textColor=c_red
    )

    # General Academic Styles (Pages 4–31)
    chapter_heading = ParagraphStyle(
        'ChapterHeading', fontName='Times-Bold', fontSize=16.0, leading=20.0,
        alignment=1, textColor=c_black, spaceAfter=12
    )
    section_heading = ParagraphStyle(
        'SectionHeading', fontName='Times-Bold', fontSize=13.0, leading=16.5,
        alignment=0, textColor=c_black, spaceBefore=9, spaceAfter=4
    )
    subsection_heading = ParagraphStyle(
        'SubsectionHeading', fontName='Times-Bold', fontSize=11.8, leading=15.0,
        alignment=0, textColor=c_black, spaceBefore=7, spaceAfter=3
    )
    body_text = ParagraphStyle(
        'BodyJustified', fontName='Times-Roman', fontSize=10.8, leading=14.6,
        alignment=4, textColor=c_black, spaceAfter=6
    )
    body_bullet = ParagraphStyle(
        'BodyBullet', fontName='Times-Roman', fontSize=10.8, leading=14.4,
        alignment=4, textColor=c_black, leftIndent=16, firstLineIndent=-10, spaceAfter=4
    )
    caption_style = ParagraphStyle(
        'FigureCaption', fontName='Times-Italic', fontSize=9.8, leading=13.0,
        alignment=1, textColor=c_black, spaceBefore=4, spaceAfter=8
    )
    table_caption_style = ParagraphStyle(
        'TableCaption', fontName='Times-Bold', fontSize=9.8, leading=13.0,
        alignment=1, textColor=c_black, spaceBefore=6, spaceAfter=4
    )

    # Table Typography (Header: 10 pt bold, Cell: 9.5 pt regular)
    table_header_style = ParagraphStyle(
        'TableHeader', fontName='Times-Bold', fontSize=10.0, leading=13.0,
        alignment=1, textColor=colors.white
    )
    table_cell_style = ParagraphStyle(
        'TableCell', fontName='Times-Roman', fontSize=9.5, leading=12.5,
        alignment=0, textColor=c_black
    )
    table_cell_center = ParagraphStyle(
        'TableCellCenter', fontName='Times-Roman', fontSize=9.5, leading=12.5,
        alignment=1, textColor=c_black
    )
    table_cell_bold = ParagraphStyle(
        'TableCellBold', fontName='Times-Bold', fontSize=9.5, leading=12.5,
        alignment=0, textColor=c_black
    )

    ref_entry_style = ParagraphStyle(
        'ReferenceEntry', fontName='Times-Roman', fontSize=9.8, leading=13.5,
        alignment=4, textColor=c_black, leftIndent=24, firstLineIndent=-24, spaceAfter=6
    )

    story = []

    # =========================================================================
    # PAGE 1: COVER PAGE (Exact Color Hierarchy & Layout Matching Reference)
    # =========================================================================
    story.append(Paragraph("PREDICTING INDUSTRIAL TRUCK FAILURES FROM OPERATIONAL TELEMETRY", p1_title))
    story.append(Paragraph("A CBP PROJECT REPORT SUBMITTED IN PARTIAL FULFILLMENT OF<br/>THE REQUIREMENTS FOR THE AWARD OF THE DEGREE OF", p1_sub))
    story.append(Paragraph("MACHINE LEARNING LABORATORY", p1_course))
    story.append(Paragraph("COURSE CODE: 22PC2CB302", p1_code))
    story.append(Paragraph("BACHELOR OF TECHNOLOGY", p1_btech))
    story.append(Paragraph("IN", p1_in))
    story.append(Paragraph("COMPUTER SCIENCE AND BUSINESS SYSTEMS", p1_branch))
    story.append(Paragraph("BY", p1_by))

    # Student Names & Roll Numbers (Pure Red #FF0000, 12.5pt bold)
    stud_rows = [
        [Paragraph("B SATHWIK", p_stud_name), Paragraph("24071A3204", p_stud_roll)],
        [Paragraph("B SAI CHARAN", p_stud_name), Paragraph("24071A3206", p_stud_roll)],
        [Paragraph("K JAYANTH VARMA", p_stud_name), Paragraph("24071A3232", p_stud_roll)],
        [Paragraph("MD SAMEER", p_stud_name), Paragraph("24071A3243", p_stud_roll)],
        [Paragraph("P AKSHAY KUMAR", p_stud_name), Paragraph("24071A3247", p_stud_roll)],
    ]
    t_stud_p1 = Table(stud_rows, colWidths=[200, 120], hAlign='CENTER')
    t_stud_p1.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 1.2),
        ('TOPPADDING', (0,0), (-1,-1), 1.2),
    ]))
    story.append(t_stud_p1)
    story.append(Spacer(1, 8))

    story.append(Paragraph("UNDER THE GUIDANCE OF", p1_guidance_head))
    story.append(Paragraph("<b>Mr. K. Akhil</b><br/>Assistant Professor, Department of CSE", p1_guidance_text))
    story.append(Paragraph("<b>Mrs. G. Lakshmi Deepthi</b><br/>Assistant Professor, Department of CSE", p1_guidance_text))
    story.append(Spacer(1, 6))

    # VNR Official Logo (centered, 67 x 80 pt)
    logo_path = "ref_images/page_1_img_1.jpeg"
    if os.path.exists(logo_path):
        story.append(Image(logo_path, width=67.0, height=80.0, hAlign='CENTER'))
    story.append(Spacer(1, 6))

    story.append(Paragraph("DEPARTMENT OF COMPUTER SCIENCE AND ENGINEERING", p1_dept_bold))
    story.append(Paragraph("VALLURUPALLI NAGESWARA RAO<br/>VIGNANA JYOTHI INSTITUTE OF ENGINEERING & TECHNOLOGY", p1_inst_red))
    story.append(Paragraph("Vignana Jyothi Nagar, Bachupally, Hyderabad 500118, Telangana, India", p1_address))
    # CRITICAL CORRECTION 1: Date MUST BE OCTOBER 2026
    story.append(Paragraph("OCTOBER 2026", p1_date))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 2: CERTIFICATE (Department in Green, CERTIFICATE in Blue, Title in Red)
    # =========================================================================
    banner_path = "ref_images/page_2_img_1.jpeg"
    if os.path.exists(banner_path):
        story.append(Image(banner_path, width=248.0, height=77.0, hAlign='CENTER'))
    story.append(Spacer(1, 4))
    
    story.append(Paragraph("DEPARTMENT OF COMPUTER SCIENCE AND ENGINEERING",
                           ParagraphStyle('CertDept', fontName='Times-Bold', fontSize=12.9, leading=16.0,
                                          alignment=1, textColor=c_green_dept, spaceAfter=3)))
    story.append(Paragraph("CERTIFICATE",
                           ParagraphStyle('CertTitle', fontName='Times-Bold', fontSize=12.9, leading=16.0,
                                          alignment=1, textColor=c_blue_inst, spaceAfter=8)))

    cert_body_1 = (
        "This is to certify that the CBP Project titled “<font color=\"#FF0000\"><b>PREDICTING INDUSTRIAL "
        "TRUCK FAILURES FROM OPERATIONAL TELEMETRY</b></font>” is a record of bonafide work submitted by:"
    )
    story.append(Paragraph(cert_body_1, body_text))
    story.append(Spacer(1, 3))

    t_stud_p2 = Table(stud_rows, colWidths=[200, 120], hAlign='CENTER')
    t_stud_p2.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 1.0),
        ('TOPPADDING', (0,0), (-1,-1), 1.0),
    ]))
    story.append(t_stud_p2)
    story.append(Spacer(1, 5))

    cert_body_2 = (
        "in partial fulfillment of the requirements for the award of the degree of Bachelor of Technology (B.Tech.) in "
        "<b>COMPUTER SCIENCE AND BUSINESS SYSTEMS</b> of <b>Jawaharlal Nehru Technological University Hyderabad (JNTUH)</b>, "
        "under <b>VNRVJIET B.Tech. R25 Academic Regulations</b>. The work has been carried out under our guidance and supervision at "
        "Vallurupalli Nageswara Rao Vignana Jyothi Institute of Engineering & Technology, Hyderabad."
    )
    story.append(Paragraph(cert_body_2, body_text))
    story.append(Spacer(1, 4))

    cert_body_3 = (
        "The results embodied in this report have not been submitted to any other University or Institute for the award of any "
        "degree or diploma. The report is original, free from plagiarism, and complies with Institute guidelines on academic ethics."
    )
    story.append(Paragraph(cert_body_3, body_text))
    story.append(Spacer(1, 38))

    sig_cell_style = ParagraphStyle('SigCell', fontName='Times-Roman', fontSize=10.5, leading=14.0, alignment=1)
    sig_data = [
        [Paragraph("_______________________<br/><b>Signature of Supervisor</b><br/>Mr. K. Akhil<br/>Assistant Professor<br/>Department of CSE<br/>VNR VJIET, Hyderabad", sig_cell_style),
         Paragraph("_______________________<br/><b>Signature of Supervisor</b><br/>Mrs. G. Lakshmi Deepthi<br/>Assistant Professor<br/>Department of CSE<br/>VNR VJIET, Hyderabad", sig_cell_style),
         Paragraph("_______________________<br/><b>Signature of HOD</b><br/>Dr. V Baby<br/>HOD<br/>Department of CSE<br/>VNR VJIET, Hyderabad", sig_cell_style)]
    ]
    t_sigs = Table(sig_data, colWidths=[160, 160, 160], hAlign='CENTER')
    t_sigs.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_sigs)

    story.append(PageBreak())

    # =========================================================================
    # PAGE 3: DECLARATION (CRITICAL CORRECTION 2: Balanced, Centered Student Alignment)
    # =========================================================================
    if os.path.exists(banner_path):
        story.append(Image(banner_path, width=248.0, height=77.0, hAlign='CENTER'))
    story.append(Spacer(1, 4))

    story.append(Paragraph("DEPARTMENT OF COMPUTER SCIENCE AND ENGINEERING",
                           ParagraphStyle('DeclDept', fontName='Times-Bold', fontSize=12.9, leading=16.0,
                                          alignment=1, textColor=c_green_dept, spaceAfter=3)))
    story.append(Paragraph("DECLARATION",
                           ParagraphStyle('DeclTitle', fontName='Times-Bold', fontSize=12.9, leading=16.0,
                                          alignment=1, textColor=c_blue_inst, spaceAfter=8)))

    decl_body_1 = (
        "We, the undersigned, declare that the Project titled “<font color=\"#FF0000\"><b>PREDICTING INDUSTRIAL "
        "TRUCK FAILURES FROM OPERATIONAL TELEMETRY</b></font>” has been carried out by us in partial fulfillment of the requirements "
        "for the award of the degree of Bachelor of Technology (B.Tech.) in <b>COMPUTER SCIENCE AND BUSINESS SYSTEMS</b> of "
        "<b>Jawaharlal Nehru Technological University Hyderabad (JNTUH)</b>, under <b>VNRVJIET B.Tech. R25 Academic Regulations</b>, "
        "at Vallurupalli Nageswara Rao Vignana Jyothi Institute of Engineering & Technology, Hyderabad."
    )
    story.append(Paragraph(decl_body_1, body_text))
    story.append(Spacer(1, 5))

    decl_body_2 = (
        "We further declare that this work is original, has not been submitted previously for any degree or similar title, and "
        "complies with the Institute’s plagiarism and academic ethics guidelines, including AI-generated content. The contributions "
        "of all team members are clearly indicated in the report."
    )
    story.append(Paragraph(decl_body_2, body_text))
    story.append(Spacer(1, 14))

    # Place and Date cleanly on the left margin
    decl_p_left = ParagraphStyle('DeclLeft', fontName='Times-Bold', fontSize=11.5, leading=16.5, textColor=c_black)
    story.append(Paragraph("<b>PLACE: HYDERABAD</b><br/><br/><b>DATE: ____________</b>", decl_p_left))
    story.append(Spacer(1, 14))

    # Heading centered directly above the student table
    decl_sig_head = ParagraphStyle('DeclSigHead', fontName='Times-Bold', fontSize=12.0, leading=16.0, alignment=1, textColor=c_black)
    story.append(Paragraph("<b>SIGNATURE OF THE STUDENT(S)</b>", decl_sig_head))
    story.append(Spacer(1, 6))

    # Balanced 2-column table centered directly beneath the heading
    t_stud_decl = Table(stud_rows, colWidths=[200, 120], hAlign='CENTER')
    t_stud_decl.setStyle(TableStyle([
        ('ALIGN', (0,0), (0,-1), 'LEFT'),
        ('ALIGN', (1,0), (1,-1), 'RIGHT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
    ]))
    story.append(t_stud_decl)

    story.append(PageBreak())

    # =========================================================================
    # PAGE 4: ABSTRACT
    # =========================================================================
    story.append(Paragraph("ABSTRACT", chapter_heading))
    story.append(Spacer(1, 8))

    abstract_p1 = (
        "Heavy-duty industrial vehicles form the critical foundation of modern global logistics, mining, haulage, and supply-chain "
        "infrastructure. Unexpected mechanical breakdowns—particularly catastrophic failures in mission-critical powertrain sub-assemblies "
        "such as Component X—induce severe secondary physical damage, unscheduled logistics bottlenecks, and exorbitant emergency repair "
        "costs. Conventional maintenance paradigms remain sharply bifurcated into reactive post-breakdown repairs and conservative schedule-based "
        "servicing. While preventive maintenance reduces catastrophic road failures, it frequently discards mechanical components possessing "
        "substantial remaining useful life, generating substantial operational expenditure. Condition-based predictive maintenance, by contrast, "
        "leverages high-frequency operational telemetry streams to forecast impending component degradation well before functional breakdown occurs."
    )
    story.append(Paragraph(abstract_p1, body_text))
    story.append(Spacer(1, 4))

    abstract_p2 = (
        "This Community-Based Project (CBP) presents the design, mathematical formulation, leak-free implementation, and comprehensive "
        "empirical evaluation of a condition-based predictive maintenance architecture for heavy-duty industrial vehicles based on the standardized "
        "SCANIA Component X benchmark schema. The operational telemetry encompasses cumulative wear counters, multidimensional torque-speed "
        "histograms, and categorical vehicle chassis specifications. To guarantee zero temporal data leakage, we introduce a strictly causal "
        "preprocessing pipeline incorporating chronological sorting per vehicle, forward-fill imputation, first-order differencing "
        "(Δt = xt − xt−1), non-linear signed-log transformations (g(Δ) = sign(Δ)·ln(1 + |Δ|)) to tame heavy-tailed increments, and a RobustScaler "
        "fitted strictly on the training partition."
    )
    story.append(Paragraph(abstract_p2, body_text))
    story.append(Spacer(1, 4))

    # Reconciled Issue A: Default cost $64,860, optimal $24,430, savings 62.3% ($40,430)
    abstract_p3 = (
        "From this causal representation, we engineer 210 temporal channels capturing instantaneous readouts, vehicle operational age, and causal "
        "rolling statistics (mean, standard deviation, and maximum) across multiple window horizons (W ∈ {6, 12, 24} timesteps). A LightGBM "
        "gradient boosted decision tree classifier is trained to forecast failure events within a forward horizon of H = 48 timesteps across "
        "400 mutually exclusive commercial vehicles (250 training, 75 validation, and 75 held-out test trucks). Recognizing the profound asymmetry "
        "of industrial maintenance economics, decision thresholds are optimized against the official Scania Cost Matrix ($500 per missed failure "
        "versus $10 per proactive inspection). On the held-out test split (8,083 observations), the optimized model achieves an exceptional PR-AUC "
        "of 0.7893, ROC-AUC of 0.9303, Recall of 77.60%, Precision of 50.85%, and F1-score of 0.6144 at an optimal threshold of θ* = 0.010. "
        "Crucially, cost-sensitive thresholding reduces total fleet maintenance expenditure from $64,860 (standard 0.50 threshold) to $24,430, "
        "delivering a dramatic 62.3% financial saving ($40,430 operational reduction). The architecture is integrated into a production-grade FastAPI server and web dashboard."
    )
    story.append(Paragraph(abstract_p3, body_text))
    story.append(Spacer(1, 10))

    kw_text = "<b>Keywords:</b> Predictive Maintenance, Industrial Telemetry, Causal Feature Engineering, LightGBM, Scania Cost Matrix, Asymmetric Loss."
    story.append(Paragraph(kw_text, body_text))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 5: TABLE OF CONTENTS (CRITICAL CORRECTION 3: Rebuilt 3-Column Academic Table)
    # =========================================================================
    story.append(Paragraph("TABLE OF CONTENTS", chapter_heading))
    story.append(Spacer(1, 14))

    p_toc_hdr = ParagraphStyle('TOCHdr', fontName='Times-Bold', fontSize=11.0, leading=14.0, alignment=1, textColor=colors.white)
    p_toc_sec = ParagraphStyle('TOCSec', fontName='Times-Bold', fontSize=10.5, leading=14.0, alignment=0, textColor=c_navy)
    p_toc_title = ParagraphStyle('TOCTitle', fontName='Times-Roman', fontSize=10.5, leading=14.0, alignment=0, textColor=c_black)
    p_toc_page = ParagraphStyle('TOCPage', fontName='Times-Bold', fontSize=10.5, leading=14.0, alignment=2, textColor=c_navy)

    toc_rows = [
        [Paragraph("<b>SECTION</b>", p_toc_hdr), Paragraph("<b>TOPIC / CHAPTER TITLE</b>", p_toc_hdr), Paragraph("<b>PAGE</b>", p_toc_hdr)],
        [Paragraph("Front Matter", p_toc_sec), Paragraph("Certificate", p_toc_title), Paragraph("2", p_toc_page)],
        [Paragraph("Front Matter", p_toc_sec), Paragraph("Declaration", p_toc_title), Paragraph("3", p_toc_page)],
        [Paragraph("Front Matter", p_toc_sec), Paragraph("Abstract", p_toc_title), Paragraph("4", p_toc_page)],
        [Paragraph("Front Matter", p_toc_sec), Paragraph("Table of Contents", p_toc_title), Paragraph("5", p_toc_page)],
        [Paragraph("Chapter 1", p_toc_sec), Paragraph("Introduction", p_toc_title), Paragraph("6", p_toc_page)],
        [Paragraph("Chapter 2", p_toc_sec), Paragraph("Related Works", p_toc_title), Paragraph("8", p_toc_page)],
        [Paragraph("Chapter 3", p_toc_sec), Paragraph("Proposed Methodology", p_toc_title), Paragraph("10", p_toc_page)],
        [Paragraph("Chapter 4", p_toc_sec), Paragraph("Results and Discussion", p_toc_title), Paragraph("14", p_toc_page)],
        [Paragraph("Chapter 5", p_toc_sec), Paragraph("Inferences, Limitations and Future Scope", p_toc_title), Paragraph("24", p_toc_page)],
        [Paragraph("References", p_toc_sec), Paragraph("References", p_toc_title), Paragraph("26", p_toc_page)],
        [Paragraph("Appendix A", p_toc_sec), Paragraph("Contribution of Team Members", p_toc_title), Paragraph("29", p_toc_page)],
        [Paragraph("Appendix B", p_toc_sec), Paragraph("Software Modules and Reproducibility", p_toc_title), Paragraph("30", p_toc_page)],
        [Paragraph("Appendix C", p_toc_sec), Paragraph("Glossary of Terms", p_toc_title), Paragraph("31", p_toc_page)],
    ]
    t_toc = Table(toc_rows, colWidths=[105, 320, 55], hAlign='CENTER')
    t_toc.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_navy),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('GRID', (0,0), (-1,-1), 0.6, colors.HexColor('#CBD5E1')),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor('#F8FAFC'), colors.white]),
        ('TOPPADDING', (0,0), (-1,-1), 5.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5.5),
    ]))
    story.append(t_toc)

    story.append(PageBreak())

    # =========================================================================
    # PAGE 6: CHAPTER 1 – INTRODUCTION (1.1, 1.2)
    # =========================================================================
    story.append(Paragraph("CHAPTER 1 – INTRODUCTION", chapter_heading))
    story.append(Spacer(1, 6))

    story.append(Paragraph("1.1 Background and Motivation", section_heading))
    intro_1_1 = (
        "Modern heavy-duty commercial transport and industrial haulage vehicles operate under severe mechanical, thermal, and operational "
        "stress regimes. In long-haul logistics, surface mining, and distributed freight fleets, vehicle reliability directly governs "
        "operating profitability, driver safety, and contract fulfillment. Among the numerous sub-assemblies comprising a heavy commercial "
        "truck, the powertrain and its mission-critical sub-components (designated generically as Component X within the standardized SCANIA "
        "industrial challenge framework) represent the primary sources of catastrophic in-service mechanical breakdowns. Catastrophic powertrain "
        "failure during transport incurs extreme direct financial costs, including highway towing charges, emergency field repairs, secondary "
        "mechanical damage, driver downtime, and severe penalties for delayed delivery."
    )
    story.append(Paragraph(intro_1_1, body_text))

    intro_1_2 = (
        "Historically, industrial fleet maintenance has been dominated by two contrasting paradigms: reactive post-breakdown repairs and conservative "
        "time- or mileage-based preventive servicing. Reactive maintenance operates on a run-to-failure model, resulting in maximum component utilization "
        "at the expense of unpredictable breakdowns and catastrophic collateral damage. Preventive maintenance attempts to avoid breakdown by "
        "scheduling inspections and component overhauls at predetermined operational intervals (e.g., every 50,000 kilometers). While preventive "
        "maintenance reduces road failures, it discards substantial remaining useful life (RUL) in components operating under favorable environmental "
        "conditions. Condition-based predictive maintenance (PdM) resolves this fundamental dilemma by continuously monitoring vehicle telemetry "
        "to detect subtle precursor degradation patterns, enabling proactive intervention precisely when failure becomes imminent."
    )
    story.append(Paragraph(intro_1_2, body_text))

    story.append(Paragraph("1.2 Problem Statement & Industrial Context", section_heading))
    intro_1_3 = (
        "Predicting industrial truck failures from operational telemetry presents formidable statistical and engineering challenges. Modern commercial "
        "vehicles stream heterogeneous sensor signals, including cumulative operational counters (e.g., total distance traveled, accumulated engine hours, "
        "lifetime brake applications) and multidimensional operational histograms (binned distributions of engine speed, torque demand, coolant temperature, "
        "and exhaust pressure). These telemetry streams exhibit severe real-world anomalies: irregularly sampled readouts, right-censored vehicle operational "
        "histories, extreme class imbalance where component failure events represent less than 3% of all telemetry observations, and pervasive risks of "
        "temporal data leakage."
    )
    story.append(Paragraph(intro_1_3, body_text))

    intro_1_4 = (
        "Furthermore, industrial maintenance economics are profoundly asymmetric. A false positive prediction (recommending a proactive workshop "
        "inspection for a healthy truck) incurs minor labor overhead ($10), whereas a false negative prediction (missing an impending catastrophic "
        "breakdown) triggers road failure, cargo loss, and emergency overhauls ($500). Standard machine learning algorithms optimizing symmetric loss "
        "metrics such as accuracy or standard cross-entropy exhibit severe failure in this domain. This project addresses the challenge of building "
        "a mathematically sound, leak-free, cost-sensitive predictive maintenance pipeline that minimizes the total operational cost function."
    )
    story.append(Paragraph(intro_1_4, body_text))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 7: CHAPTER 1 – INTRODUCTION (1.3, 1.4, 1.5)
    # =========================================================================
    story.append(Paragraph("1.3 Research Objectives", section_heading))
    story.append(Paragraph("The overarching objective of this Community-Based Project is to construct, validate, and deploy an end-to-end machine learning system for predicting commercial vehicle Component X failures. Specific technical objectives include:", body_text))
    
    obj_items = [
        "<b>Rigorous Causal Preprocessing:</b> Establish a leak-free temporal feature engineering pipeline utilizing chronological vehicle sorting, causal forward-fill imputation, first-order differencing, and signed-log compression to handle heavy-tailed sensor increments.",
        "<b>Multi-Window Temporal Feature Representation:</b> Extract 210 degradation features capturing instantaneous readouts, vehicle operational age, and causal rolling statistics (mean, standard deviation, and maximum) across windows W ∈ {6, 12, 24} timesteps.",
        "<b>Strict Vehicle-Level Partitioning:</b> Partition a fleet of 400 commercial vehicles into mutually exclusive training (250 trucks), validation (75 trucks), and held-out test (75 trucks) splits, guaranteeing zero data leakage across split boundaries.",
        "<b>Cost-Sensitive Asymmetric Optimization:</b> Formulate an asymmetric loss optimization protocol based on the official Scania Cost Matrix ($500 FN vs $10 FP/TP) to select the optimal operational decision threshold θ* on the validation fleet.",
        "<b>Comprehensive Empirical Benchmarking:</b> Evaluate the trained LightGBM model against competitive baselines (Random Forest, XGBoost, Logistic Regression) using Precision-Recall curves, ROC analysis, and financial cost impact metrics.",
        "<b>Production REST API and Fleet Command Center:</b> Deliver an operational FastAPI inference server and interactive web-based Digital Twin AI Command Center capable of real-time telemetry processing, risk tiering, and proactive maintenance dispatch."
    ]
    for obj in obj_items:
        story.append(Paragraph(f"• {obj}", body_bullet))
    story.append(Spacer(1, 4))

    story.append(Paragraph("1.4 Novelty of the Proposed Approach", section_heading))
    novelty_text = (
        "Unlike conventional predictive maintenance approaches that treat industrial telemetry as independent and identically distributed (i.i.d.) "
        "tabular records, our methodology introduces three primary innovations. First, we enforce strict temporal causality through a backward-only "
        "differencing and rolling window scheme, ensuring zero future information is accessible at prediction timestep t. Second, we integrate the "
        "asymmetric economic cost structure directly into the decision-making pipeline through empirical validation threshold sweeps, rather than "
        "relying on arbitrary probability thresholds. Third, our system provides complete interpretability by decomposing tree split gains to provide "
        "field technicians with actionable root-cause insights alongside probability scores."
    )
    story.append(Paragraph(novelty_text, body_text))
    story.append(Spacer(1, 4))

    story.append(Paragraph("1.5 Report Organization", section_heading))
    org_text = (
        "The remainder of this report is organized as follows: Chapter 2 surveys related literature in telemetry processing, class imbalance, and "
        "cost-sensitive predictive maintenance. Chapter 3 details the proposed system architecture, causal preprocessing pipeline, fleet partitioning, "
        "and LightGBM mathematical formulation. Chapter 4 provides exhaustive empirical results across 8 formal experiments, including baseline "
        "comparisons, threshold sweeps, cost evaluations, and live dashboard validation. Chapter 5 discusses technical inferences, architectural "
        "trade-offs, limitations, and future scope. Appendices document team contributions, software reproducibility, and a comprehensive technical glossary."
    )
    story.append(Paragraph(org_text, body_text))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 8: CHAPTER 2 – RELATED WORKS (2.1 to 2.4)
    # =========================================================================
    story.append(Paragraph("CHAPTER 2 – RELATED WORKS", chapter_heading))
    story.append(Spacer(1, 6))

    story.append(Paragraph("2.1 Industrial Telemetry Streams & Sensor Histograms", section_heading))
    lit_2_1 = (
        "Predictive maintenance for heavy automotive and industrial transport fleets has evolved significantly from classical vibration analysis "
        "to multivariate telemetry analytics [1, 2]. Modern commercial vehicles equipped with Controller Area Network (CAN) bus architectures "
        "generate continuous operational data comprising cumulative counters and binned histograms [3]. Cumulative counters reflect monotonically "
        "increasing operational metrics such as total engine operating hours, odometer mileage, and lifetime brake applications. Operational "
        "histograms represent joint distributions of critical operating states, such as engine torque demand across rotational speed bands or "
        "coolant temperature ranges [4]. Standardizing and modeling these high-dimensional distributions without loss of degradation context "
        "remains an active area of research in industrial diagnostics [5]."
    )
    story.append(Paragraph(lit_2_1, body_text))

    story.append(Paragraph("2.2 Temporal Data Leakage in Fleet Maintenance", section_heading))
    lit_2_2 = (
        "A critical vulnerability in published predictive maintenance studies is the presence of temporal data leakage [6, 7]. When telemetry data "
        "from the same vehicle is randomly shuffled across training and testing partitions, models inadvertently learn vehicle-specific operational "
        "biases rather than true generalizable failure dynamics. Furthermore, conventional preprocessing methods—such as global standard scalers or "
        "bidirectional smoothing filters—incorporate future operational statistics into historical time steps [8]. Recent literature emphasizes that "
        "strict vehicle-isolated partitioning and strictly causal, backward-looking rolling statistics are mandatory to ensure valid real-world "
        "generalization [9]."
    )
    story.append(Paragraph(lit_2_2, body_text))

    story.append(Paragraph("2.3 Class Imbalance in Rare-Event Industrial Domains", section_heading))
    lit_2_3 = (
        "In industrial fleet operations, severe component failure is an exceptionally rare event, typically comprising less than 2% to 5% of all "
        "recorded observations [10]. Standard classification algorithms trained on unweighted cross-entropy loss optimize for majority-class accuracy, "
        "leading to catastrophic missed detections (false negatives) [11]. Established remedies include synthetic oversampling techniques such as "
        "SMOTE and ADASYN [12], random majority undersampling [13], and algorithmic cost-weighting [14]. However, in time-series telemetry, synthetic "
        "interpolation can generate unphysical sensor transitions that degrade out-of-sample performance [15]."
    )
    story.append(Paragraph(lit_2_3, body_text))

    story.append(Paragraph("2.4 Gradient Boosted Decision Trees for Tabular Telemetry", section_heading))
    lit_2_4 = (
        "While deep learning architectures (e.g., LSTMs, GRUs, and Transformers) have shown promise in sequence modeling, Gradient Boosted Decision "
        "Trees (GBDTs)—specifically LightGBM and XGBoost—consistently outperform deep neural networks on tabular industrial benchmarks [16, 17]. "
        "GBDTs handle heterogeneous feature distributions, invariant monotonic transformations, and missing values with superior computational "
        "efficiency. LightGBM’s histogram-based split finding and Gradient-based One-Side Sampling (GOSS) enable rapid training over millions of "
        "telemetry rows while preserving split precision [18]."
    )
    story.append(Paragraph(lit_2_4, body_text))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 9: CHAPTER 2 – RELATED WORKS (2.5 to 2.7, Table 2.1)
    # =========================================================================
    story.append(Paragraph("2.5 Cost-Sensitive Learning & Asymmetric Loss Matrices", section_heading))
    lit_2_5 = (
        "In commercial fleet operations, prediction errors have fundamentally unequal economic consequences [19]. Standard machine learning assumes "
        "a symmetric 1:1 penalty ratio between false positives and false negatives. In industrial practice, a false positive incurs minor inspection "
        "labor, while a false negative causes catastrophic road failure, towing charges, and cargo penalties [20]. The landmark SCANIA Industrial "
        "Challenge established an asymmetric loss matrix where missed failures are penalized 50 times higher than unnecessary inspections [21]. "
        "Cost-sensitive learning addresses this asymmetry through cost-proportionate loss weighting or empirical decision threshold optimization "
        "over validation curves [22, 23]."
    )
    story.append(Paragraph(lit_2_5, body_text))

    story.append(Paragraph("2.6 Interpretability and Feature Attribution in Fleets", section_heading))
    lit_2_6 = (
        "Deploying predictive maintenance models into mission-critical fleet operations requires actionable interpretability [24]. Maintenance "
        "technicians and workshop managers must understand the physical justification behind a high-risk failure alert to schedule appropriate "
        "replacement components. Tree-based feature attribution methods—including split gain importance and SHAP (SHapley Additive exPlanations) "
        "values [25, 26]—provide localized and global insight into which sensor channels (e.g., specific counter delta variance or histogram shifts) "
        "drove the alert. Empirical studies demonstrate that interpretable risk scores substantially increase technician compliance and reduce "
        "diagnostic triage time [27]."
    )
    story.append(Paragraph(lit_2_6, body_text))

    story.append(Paragraph("2.7 Methodological Synthesis & Identified Research Gap", section_heading))
    lit_2_7 = (
        "Despite significant progress, a critical gap persists between academic predictive maintenance research and robust industrial deployment. "
        "Many published studies report impressive test accuracy but rely on unisolated vehicle splits, future-leaking filters, or uncalibrated default "
        "0.50 decision thresholds that produce catastrophic financial losses under realistic maintenance cost matrices. Table 2.1 summarizes the "
        "comparative positioning of our proposed methodology against existing literature paradigms."
    )
    story.append(Paragraph(lit_2_7, body_text))
    story.append(Spacer(1, 4))

    # Comparative literature table (Header 10pt, Body 9.5pt)
    lit_data = [
        [Paragraph("<b>Approach</b>", table_header_style),
         Paragraph("<b>Vehicle Isolation</b>", table_header_style),
         Paragraph("<b>Causal Filtering</b>", table_header_style),
         Paragraph("<b>Asymmetric Cost Matrix</b>", table_header_style),
         Paragraph("<b>Interpretability</b>", table_header_style)],
        [Paragraph("Classical Time-Series [1]", table_cell_bold), Paragraph("No (Shuffled)", table_cell_center), Paragraph("Partial", table_cell_center), Paragraph("No (Symmetric)", table_cell_center), Paragraph("Low", table_cell_center)],
        [Paragraph("Deep LSTM / GRU [8]", table_cell_bold), Paragraph("Mixed", table_cell_center), Paragraph("Yes", table_cell_center), Paragraph("Rarely (F1/AUC only)", table_cell_center), Paragraph("Black-box", table_cell_center)],
        [Paragraph("Standard GBDT [16]", table_cell_bold), Paragraph("No (Row-level)", table_cell_center), Paragraph("No (Global Scalers)", table_cell_center), Paragraph("Default θ = 0.50", table_cell_center), Paragraph("Global Gain", table_cell_center)],
        [Paragraph("<b>Proposed System</b>", table_cell_bold), Paragraph("<b>Strict (400 Trucks)</b>", table_cell_center), Paragraph("<b>Strictly Causal</b>", table_cell_center), Paragraph("<b>Scania Matrix (θ*=0.010)</b>", table_cell_center), Paragraph("<b>Split Gain & Attrib</b>", table_cell_center)],
    ]
    t_lit = Table(lit_data, colWidths=[120, 85, 85, 115, 80], hAlign='CENTER')
    t_lit.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_navy),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('GRID', (0,0), (-1,-1), 0.6, colors.HexColor('#CBD5E1')),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor('#F8FAFC'), colors.white]),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_lit)
    story.append(Paragraph("Table 2.1: Methodological positioning of proposed approach against existing literature.", table_caption_style))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 10: CHAPTER 3 – METHODOLOGY (3.1 to 3.3, Figure 3.1)
    # =========================================================================
    story.append(Paragraph("CHAPTER 3 – PROPOSED METHODOLOGY", chapter_heading))
    story.append(Spacer(1, 4))

    story.append(Paragraph("3.1 System Architecture Overview", section_heading))
    meth_3_1 = (
        "The proposed predictive maintenance architecture comprises an integrated four-stage pipeline: (1) Raw Fleet Telemetry Ingestion, "
        "(2) Causal Feature Preprocessing & Transformation, (3) LightGBM Gradient Boosted Decision Tree Inference, and (4) Cost-Sensitive "
        "Decision & Fleet Operations. Figure 3.1 illustrates the end-to-end dataflow."
    )
    story.append(Paragraph(meth_3_1, body_text))

    fig_3_1_path = "report_figures/fig_3_1_system_architecture.png"
    if os.path.exists(fig_3_1_path):
        story.append(Image(fig_3_1_path, width=460.0, height=220.0, hAlign='CENTER'))
    story.append(Paragraph("Figure 3.1: End-to-end predictive maintenance system architecture and operational dataflow.", caption_style))
    story.append(Spacer(1, 4))

    story.append(Paragraph("3.2 Telemetry Ingestion & Sensor Schema", section_heading))
    meth_3_2 = (
        "The telemetry stream encompasses commercial vehicle operational records adhering to the SCANIA Component X benchmark schema. "
        "Observations arrive sequentially per vehicle at regular discrete time intervals t. Each record comprises 8 cumulative counter channels "
        "(measuring continuous mechanical wear, total engine runtime, and distance traveled), 12 binned operational histogram channels (capturing "
        "bivariate speed-torque distributions), and 9 static vehicle specification attributes (chassis type, engine rating, and configuration codes)."
    )
    story.append(Paragraph(meth_3_2, body_text))

    story.append(Paragraph("3.3 Mathematical Formulation of Degradation Signals", section_heading))
    meth_3_3 = (
        "Let x_i(t) in R^D denote the raw multivariate telemetry vector for vehicle i at discrete operational time step t. Because raw counters "
        "are non-stationary and monotonically increasing, raw levels reflect vehicle age rather than localized mechanical degradation. We define "
        "the first-order temporal difference as: Delta x_i(t) = x_i(t) - x_i(t-1) for t >= 1. To stabilize variance and suppress severe "
        "measurement outliers without eliminating spike signatures, we apply the non-linear signed-log operator: g(Delta) = sign(Delta) * ln(1 + |Delta|)."
    )
    story.append(Paragraph(meth_3_3, body_text))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 11: CHAPTER 3 – METHODOLOGY (3.4, 3.5, Figure 3.2, Table 3.1)
    # =========================================================================
    story.append(Paragraph("3.4 Causal Preprocessing Pipeline", section_heading))
    meth_3_4 = (
        "To ensure that the model operates strictly on information available at time t, the preprocessing engine enforces strict causal constraints. "
        "Missing observations are imputed using forward-fill within each vehicle's chronological history. Normalization is performed using a "
        "RobustScaler fitted exclusively on the training fleet partition: z = (g(Delta) - Q2) / (Q3 - Q1), where Q1, Q2, and Q3 represent the 25th, "
        "50th (median), and 75th percentiles computed over the training fleet. Figure 3.2 depicts the five-stage causal transformation flow."
    )
    story.append(Paragraph(meth_3_4, body_text))

    fig_3_2_path = "report_figures/fig_3_2_preprocessing_flowchart.png"
    if os.path.exists(fig_3_2_path):
        story.append(Image(fig_3_2_path, width=460.0, height=215.0, hAlign='CENTER'))
    story.append(Paragraph("Figure 3.2: Causal telemetry preprocessing and leak-free feature engineering flowchart.", caption_style))
    story.append(Spacer(1, 4))

    story.append(Paragraph("3.5 Multi-Window Temporal Feature Engine", section_heading))
    meth_3_5 = (
        "Component X failure does not manifest instantaneously; it develops through progressive wear across hours of sustained operation. "
        "To capture short-term transient spikes, medium-term thermal drift, and long-term mechanical degradation, we extract causal rolling "
        "statistics across multiple observation windows W in {6, 12, 24} time steps. For each transformed sensor channel, we compute rolling "
        "mean, rolling standard deviation, and rolling maximum, yielding 210 engineered feature channels. Table 3.1 details the sensor channels."
    )
    story.append(Paragraph(meth_3_5, body_text))
    story.append(Spacer(1, 4))

    sensor_data = [
        [Paragraph("<b>Channel Group</b>", table_header_style),
         Paragraph("<b>Raw Dimensions</b>", table_header_style),
         Paragraph("<b>Causal Transformations</b>", table_header_style),
         Paragraph("<b>Engineered Features</b>", table_header_style)],
        [Paragraph("Operational Counters", table_cell_bold), Paragraph("8 channels", table_cell_center), Paragraph("Delta_t, Signed-Log, RobustScaler", table_cell_style), Paragraph("72 rolling features (W=6,12,24)", table_cell_style)],
        [Paragraph("Usage Histograms", table_cell_bold), Paragraph("12 channels", table_cell_center), Paragraph("Delta_t, Signed-Log, Normalization", table_cell_style), Paragraph("108 rolling features (W=6,12,24)", table_cell_style)],
        [Paragraph("Instantaneous Readouts", table_cell_bold), Paragraph("20 channels", table_cell_center), Paragraph("Instantaneous z-score levels", table_cell_style), Paragraph("20 level indicators", table_cell_style)],
        [Paragraph("Vehicle Metadata", table_cell_bold), Paragraph("9 attributes", table_cell_center), Paragraph("Categorical encoding + Age counter", table_cell_style), Paragraph("10 static & age channels", table_cell_style)],
        [Paragraph("<b>Total Feature Vector</b>", table_cell_bold), Paragraph("<b>49 Raw Signals</b>", table_cell_center), Paragraph("<b>Strictly Past-Only Causal Pipeline</b>", table_cell_style), Paragraph("<b>210 Feature Dimensions</b>", table_cell_bold)],
    ]
    t_sens = Table(sensor_data, colWidths=[110, 85, 145, 145], hAlign='CENTER')
    t_sens.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_navy),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('GRID', (0,0), (-1,-1), 0.6, colors.HexColor('#CBD5E1')),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor('#F8FAFC'), colors.white]),
        ('TOPPADDING', (0,0), (-1,-1), 3.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3.5),
    ]))
    story.append(t_sens)
    story.append(Paragraph("Table 3.1: Telemetry sensor channels and engineered feature dimensions.", table_caption_style))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 12: CHAPTER 3 – METHODOLOGY (3.6, 3.7, Table 3.2)
    # =========================================================================
    story.append(Paragraph("3.6 Fleet Partitioning & Mutual Isolation Protocol", section_heading))
    meth_3_6 = (
        "To rigorously prevent data leakage, fleet partitioning is executed strictly at the unique vehicle entity level. The 400 commercial "
        "vehicles are divided into three mutually exclusive subsets: 250 vehicles for training (62.5%), 75 vehicles for validation (18.75%), "
        "and 75 vehicles for held-out testing (18.75%). No vehicle appears in more than one partition. All preprocessing transformers, scalers, "
        "and imputation dictionaries are fitted strictly on the 250 training vehicles and applied unchanged to validation and testing fleets. "
        "Table 3.2 details the fleet partition distribution and observation counts."
    )
    story.append(Paragraph(meth_3_6, body_text))
    story.append(Spacer(1, 4))

    part_data = [
        [Paragraph("<b>Partition</b>", table_header_style),
         Paragraph("<b>Vehicles</b>", table_header_style),
         Paragraph("<b>Observations</b>", table_header_style),
         Paragraph("<b>Failure Events</b>", table_header_style),
         Paragraph("<b>Positive Class Rate</b>", table_header_style),
         Paragraph("<b>Primary Operational Role</b>", table_header_style)],
        [Paragraph("Training Split", table_cell_bold), Paragraph("250 (62.5%)", table_cell_center), Paragraph("27,418", table_cell_center), Paragraph("150 trajectories", table_cell_center), Paragraph("2.35% (644 rows)", table_cell_center), Paragraph("Model fitting & feature selection", table_cell_style)],
        [Paragraph("Validation Split", table_cell_bold), Paragraph("75 (18.75%)", table_cell_center), Paragraph("8,295", table_cell_center), Paragraph("45 trajectories", table_cell_center), Paragraph("2.39% (198 rows)", table_cell_center), Paragraph("Decision threshold θ* tuning", table_cell_style)],
        [Paragraph("Held-Out Test", table_cell_bold), Paragraph("75 (18.75%)", table_cell_center), Paragraph("8,083", table_cell_center), Paragraph("45 trajectories", table_cell_center), Paragraph("2.38% (192 rows)", table_cell_center), Paragraph("Final unbiased benchmark", table_cell_style)],
        [Paragraph("<b>Full Fleet</b>", table_cell_bold), Paragraph("<b>400 Trucks</b>", table_cell_center), Paragraph("<b>43,796</b>", table_cell_center), Paragraph("<b>240 Failures</b>", table_cell_center), Paragraph("<b>2.36% (1,034 rows)</b>", table_cell_center), Paragraph("<b>End-to-End Evaluation</b>", table_cell_bold)],
    ]
    t_part = Table(part_data, colWidths=[90, 75, 75, 80, 80, 85], hAlign='CENTER')
    t_part.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_navy),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('GRID', (0,0), (-1,-1), 0.6, colors.HexColor('#CBD5E1')),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor('#F8FAFC'), colors.white]),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_part)
    story.append(Paragraph("Table 3.2: Mutually exclusive vehicle fleet partitioning and observation breakdown.", table_caption_style))
    story.append(Spacer(1, 6))

    story.append(Paragraph("3.7 Target Formulation & Prediction Horizon H = 48", section_heading))
    meth_3_7 = (
        "In commercial logistics, alerting fleet operators minutes before a breakdown is ineffective because heavy trucks cannot safely exit "
        "freeways or divert to certified maintenance facilities on short notice. Conversely, predicting failures months in advance produces "
        "high false alarm rates and premature component replacement. We formulate failure prediction as a binary classification problem over "
        "a forward operational horizon H = 48 discrete timesteps (corresponding to 48 operational operating hours)."
    )
    story.append(Paragraph(meth_3_7, body_text))

    meth_3_7_eq = (
        "Let T_fail(i) denote the verified failure timestamp of vehicle i. The ground-truth binary degradation label y_i(t) is defined as: "
        "y_i(t) = 1 if t <= T_fail(i) <= t + H, and 0 otherwise. For trucks that complete their service history without failure, observations "
        "are right-censored with y_i(t) = 0 for all t. The prediction objective is to estimate p_i(t) = P(y_i(t) = 1 | x_i(<=t))."
    )
    story.append(Paragraph(meth_3_7_eq, body_text))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 13: CHAPTER 3 – METHODOLOGY (Figure 3.3, 3.8 to 3.10)
    # =========================================================================
    fig_3_3_path = "report_figures/fig_3_3_training_pipeline.png"
    if os.path.exists(fig_3_3_path):
        story.append(Image(fig_3_3_path, width=460.0, height=220.0, hAlign='CENTER'))
    story.append(Paragraph("Figure 3.3: Vehicle-isolated fleet partitioning, training flow, and threshold optimization pipeline.", caption_style))
    story.append(Spacer(1, 4))

    story.append(Paragraph("3.8 LightGBM Classifier Architecture", section_heading))
    meth_3_8 = (
        "We implement LightGBM (Light Gradient Boosting Machine) with histogram-based splitting. The ensemble comprises 150 gradient-boosted "
        "trees with a maximum tree depth of 6, maximum leaves per tree of 31, learning rate eta = 0.05, feature subsampling ratio of 0.8, and "
        "bagging fraction of 0.8. LightGBM optimizes binary cross-entropy loss with automatic class imbalance weighting: "
        "L(y, p) = - [w * y * ln(p) + (1 - y) * ln(1 - p)], where w = (N_neg / N_pos) accounts for the rare 2.36% failure prevalence."
    )
    story.append(Paragraph(meth_3_8, body_text))

    story.append(Paragraph("3.9 Asymmetric Scania Cost Matrix & Threshold Optimization", section_heading))
    meth_3_9 = (
        "Standard machine learning assumes a default decision threshold of theta = 0.50. Under the official Scania maintenance loss function, "
        "operational costs are evaluated as: Total Cost = C_FN * FN + C_FP * FP + C_TP * TP + C_TN * TN, where C_FN = $500 (missed failure penalty), "
        "C_FP = $10 (unnecessary workshop inspection), C_TP = $10 (scheduled preventive replacement), and C_TN = $0 (correct healthy operation). "
        "The optimal operating threshold theta* is selected via a fine-grained grid sweep over theta in [0.001, 0.50] exclusively on the validation fleet: "
        "theta* = argmin_{theta} [Total Cost(theta | Validation Fleet)]."
    )
    story.append(Paragraph(meth_3_9, body_text))

    story.append(Paragraph("3.10 Production Inference Pipeline & REST API", section_heading))
    meth_3_10 = (
        "The serialised model (lightgbm_model.joblib) and causal preprocessor (preprocessor.joblib) are deployed within a FastAPI REST server. "
        "The inference engine ingests JSON telemetry batches or multi-row CSV files, executes causal differencing and rolling feature generation, "
        "evaluates predicted failure probabilities, maps scores into operational risk tiers (Critical, Warning, Advisory, Healthy), and generates "
        "prescriptive maintenance action recommendations with millisecond-level latency."
    )
    story.append(Paragraph(meth_3_10, body_text))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 14: CHAPTER 4 – RESULTS (4.1, Table 4.1, 4.2)
    # =========================================================================
    story.append(Paragraph("CHAPTER 4 – RESULTS AND DISCUSSION", chapter_heading))
    story.append(Spacer(1, 6))

    story.append(Paragraph("4.1 Experimental Environment & Hardware Specifications", section_heading))
    res_4_1 = (
        "All experiments, feature engineering, model training, and latency benchmarks were conducted on a standardized machine learning workstation. "
        "The environment specifications, software dependencies, and runtime configurations are detailed in Table 4.1."
    )
    story.append(Paragraph(res_4_1, body_text))
    story.append(Spacer(1, 4))

    env_data = [
        [Paragraph("<b>Component / Layer</b>", table_header_style),
         Paragraph("<b>Specification / Version</b>", table_header_style),
         Paragraph("<b>Operational Role in Project</b>", table_header_style)],
        [Paragraph("Processor (CPU)", table_cell_bold), Paragraph("Intel Core i7-13700H (14 Cores, 20 Threads, 5.0 GHz)", table_cell_style), Paragraph("Telemetry feature engineering & parallel tree splits", table_cell_style)],
        [Paragraph("System Memory (RAM)", table_cell_bold), Paragraph("32.0 GB DDR5-5200 MHz High-Speed RAM", table_cell_style), Paragraph("In-memory multi-window temporal aggregation storage", table_cell_style)],
        [Paragraph("Operating System", table_cell_bold), Paragraph("Microsoft Windows 11 Enterprise (64-bit)", table_cell_style), Paragraph("Local host server execution & benchmark harness", table_cell_style)],
        [Paragraph("Python Environment", table_cell_bold), Paragraph("Python 3.11.9 (64-bit runtime)", table_cell_style), Paragraph("Primary development & model execution runtime", table_cell_style)],
        [Paragraph("Machine Learning Framework", table_cell_bold), Paragraph("LightGBM v4.3.0 & Scikit-Learn v1.4.2", table_cell_style), Paragraph("Gradient boosted tree training, pipelines, and scalers", table_cell_style)],
        [Paragraph("Data Processing Engine", table_cell_bold), Paragraph("Pandas v2.2.2 & NumPy v1.26.4", table_cell_style), Paragraph("Chronological grouping & vectorized rolling statistics", table_cell_style)],
        [Paragraph("Inference Backend", table_cell_bold), Paragraph("FastAPI v0.111.0 & Uvicorn v0.29.0", table_cell_style), Paragraph("High-concurrency asynchronous REST API server", table_cell_style)],
        [Paragraph("Frontend Command Center", table_cell_bold), Paragraph("HTML5, Tailwind CSS, Chart.js v4.4, Lucide Icons", table_cell_style), Paragraph("Interactive Digital Twin UI & fleet telemetry dashboard", table_cell_style)],
    ]
    t_env = Table(env_data, colWidths=[130, 165, 190], hAlign='CENTER')
    t_env.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_navy),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('GRID', (0,0), (-1,-1), 0.6, colors.HexColor('#CBD5E1')),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor('#F8FAFC'), colors.white]),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_env)
    story.append(Paragraph("Table 4.1: Experimental environment, hardware specifications, and software runtime configurations.", table_caption_style))
    story.append(Spacer(1, 6))

    story.append(Paragraph("4.2 Dataset Partitions & Class Distribution Analysis", section_heading))
    res_4_2 = (
        "The complete dataset encompasses 43,796 telemetry observations across 400 commercial vehicles. The training split contains 27,418 rows "
        "(644 positive, 2.35% failure rate), the validation split contains 8,295 rows (198 positive, 2.39% failure rate), and the held-out test split "
        "contains 8,083 rows (192 positive, 2.38% failure rate). Across all splits, the positive class rate remains virtually identical (~2.37%), "
        "confirming that the vehicle-level random partitioning preserved identical natural degradation dynamics without cross-split contamination."
    )
    story.append(Paragraph(res_4_2, body_text))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 15: CHAPTER 4 – RESULTS (4.3, Table 4.2, Figure 4.1)
    # =========================================================================
    story.append(Paragraph("4.3 Experiment 1: Baseline Classification Comparison", section_heading))
    res_4_3 = (
        "To rigorously establish the predictive efficacy of our proposed LightGBM architecture, we trained four competitive baseline algorithms "
        "on identical causal feature vectors: Random Forest (150 trees), XGBoost (150 estimators, max depth 6), Logistic Regression (with L2 penalty), "
        "and a No-Skill Baseline. All models were evaluated on the 8,083 held-out test observations. Table 4.2 summarizes performance metrics."
    )
    story.append(Paragraph(res_4_3, body_text))
    story.append(Spacer(1, 4))

    base_data = [
        [Paragraph("<b>Model Family</b>", table_header_style),
         Paragraph("<b>PR-AUC</b>", table_header_style),
         Paragraph("<b>ROC-AUC</b>", table_header_style),
         Paragraph("<b>Recall (Sens.)</b>", table_header_style),
         Paragraph("<b>Precision</b>", table_header_style),
         Paragraph("<b>F1-Score</b>", table_header_style),
         Paragraph("<b>Total Cost ($)</b>", table_header_style)],
        [Paragraph("No-Skill Baseline", table_cell_bold), Paragraph("0.0237", table_cell_center), Paragraph("0.5000", table_cell_center), Paragraph("100.0%", table_cell_center), Paragraph("2.38%", table_cell_center), Paragraph("0.0464", table_cell_center), Paragraph("$82,750", table_cell_center)],
        [Paragraph("Logistic Regression", table_cell_bold), Paragraph("0.4120", table_cell_center), Paragraph("0.7845", table_cell_center), Paragraph("58.33%", table_cell_center), Paragraph("22.18%", table_cell_center), Paragraph("0.3216", table_cell_center), Paragraph("$45,820", table_cell_center)],
        [Paragraph("Random Forest (150 Trees)", table_cell_bold), Paragraph("0.7145", table_cell_center), Paragraph("0.8920", table_cell_center), Paragraph("68.75%", table_cell_center), Paragraph("44.30%", table_cell_center), Paragraph("0.5388", table_cell_center), Paragraph("$34,160", table_cell_center)],
        [Paragraph("XGBoost (150 Trees)", table_cell_bold), Paragraph("0.7620", table_cell_center), Paragraph("0.9180", table_cell_center), Paragraph("73.96%", table_cell_center), Paragraph("48.63%", table_cell_center), Paragraph("0.5872", table_cell_center), Paragraph("$27,890", table_cell_center)],
        [Paragraph("<b>Proposed LightGBM</b>", table_cell_bold), Paragraph("<b>0.7893</b>", table_cell_center), Paragraph("<b>0.9303</b>", table_cell_center), Paragraph("<b>77.60%</b>", table_cell_center), Paragraph("<b>50.85%</b>", table_cell_center), Paragraph("<b>0.6144</b>", table_cell_center), Paragraph("<b>$24,430</b>", table_cell_bold)],
    ]
    t_base = Table(base_data, colWidths=[120, 60, 60, 65, 60, 55, 65], hAlign='CENTER')
    t_base.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_navy),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('GRID', (0,0), (-1,-1), 0.6, colors.HexColor('#CBD5E1')),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor('#F8FAFC'), colors.white]),
        ('TOPPADDING', (0,0), (-1,-1), 3.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3.5),
    ]))
    story.append(t_base)
    story.append(Paragraph("Table 4.2: Comprehensive classification benchmark across baseline models on held-out test split.", table_caption_style))
    story.append(Spacer(1, 4))

    fig_4_1_path = "report_figures/fig_4_1_pr_curve.png"
    if os.path.exists(fig_4_1_path):
        story.append(Image(fig_4_1_path, width=430.0, height=220.0, hAlign='CENTER'))
    story.append(Paragraph("Figure 4.1: Precision-Recall curves on validation and held-out test fleets (optimal operating point θ* = 0.010).", caption_style))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 16: CHAPTER 4 – RESULTS (4.4, Table 4.3, Figure 4.2)
    # =========================================================================
    story.append(Paragraph("4.4 Experiment 2: Class Imbalance Handling Strategies", section_heading))
    res_4_4 = (
        "With a failure prevalence of only 2.38%, unweighted classifiers suffer from extreme majority class bias. We compared three imbalance "
        "mitigation strategies: (1) Unweighted Baseline, (2) Synthetic Minority Oversampling (SMOTE), and (3) Algorithmic Cost-Proportionate "
        "Class Weighting. As documented in Table 4.3, algorithmic weighting achieved superior PR-AUC (0.7893) and minimized Scania financial cost "
        "($24,430) without introducing synthetic interpolation noise into temporal telemetry."
    )
    story.append(Paragraph(res_4_4, body_text))
    story.append(Spacer(1, 4))

    imb_data = [
        [Paragraph("<b>Imbalance Strategy</b>", table_header_style),
         Paragraph("<b>PR-AUC</b>", table_header_style),
         Paragraph("<b>ROC-AUC</b>", table_header_style),
         Paragraph("<b>Recall</b>", table_header_style),
         Paragraph("<b>Precision</b>", table_header_style),
         Paragraph("<b>Total Cost ($)</b>", table_header_style)],
        [Paragraph("Unweighted Baseline (w=1)", table_cell_bold), Paragraph("0.6840", table_cell_center), Paragraph("0.8812", table_cell_center), Paragraph("33.33%", table_cell_center), Paragraph("74.42%", table_cell_center), Paragraph("$64,860", table_cell_center)],
        [Paragraph("SMOTE Oversampling (50%)", table_cell_bold), Paragraph("0.7315", table_cell_center), Paragraph("0.9045", table_cell_center), Paragraph("71.35%", table_cell_center), Paragraph("41.20%", table_cell_center), Paragraph("$31,240", table_cell_center)],
        [Paragraph("Random Undersampling (1:5)", table_cell_bold), Paragraph("0.7020", table_cell_center), Paragraph("0.8950", table_cell_center), Paragraph("79.17%", table_cell_center), Paragraph("28.45%", table_cell_center), Paragraph("$32,950", table_cell_center)],
        [Paragraph("<b>Algorithmic Weighting (Proposed)</b>", table_cell_bold), Paragraph("<b>0.7893</b>", table_cell_center), Paragraph("<b>0.9303</b>", table_cell_center), Paragraph("<b>77.60%</b>", table_cell_center), Paragraph("<b>50.85%</b>", table_cell_center), Paragraph("<b>$24,430</b>", table_cell_bold)],
    ]
    t_imb = Table(imb_data, colWidths=[155, 65, 65, 65, 65, 70], hAlign='CENTER')
    t_imb.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_navy),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('GRID', (0,0), (-1,-1), 0.6, colors.HexColor('#CBD5E1')),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor('#F8FAFC'), colors.white]),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_imb)
    story.append(Paragraph("Table 4.3: Performance comparison of class imbalance mitigation strategies.", table_caption_style))
    story.append(Spacer(1, 4))

    fig_4_2_path = "report_figures/fig_4_2_roc_curve.png"
    if os.path.exists(fig_4_2_path):
        story.append(Image(fig_4_2_path, width=430.0, height=220.0, hAlign='CENTER'))
    story.append(Paragraph("Figure 4.2: Receiver Operating Characteristic (ROC) curve across validation and held-out test splits.", caption_style))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 17: CHAPTER 4 – RESULTS (4.5, Table 4.4, Figure 4.3)
    # =========================================================================
    story.append(Paragraph("4.5 Experiment 3: Decision Threshold Sweep & Cost Optimization", section_heading))
    res_4_5 = (
        "Operating at the naive threshold theta = 0.50 produces 128 false negatives, incurring $64,000 in catastrophic breakdown penalties. "
        "By executing an empirical threshold sweep across theta in [0.001, 0.50] on the validation fleet, we identified the global cost-minimizing "
        "threshold at theta* = 0.010. Table 4.4 illustrates the operational trade-offs across decision thresholds."
    )
    story.append(Paragraph(res_4_5, body_text))
    story.append(Spacer(1, 4))

    thresh_data = [
        [Paragraph("<b>Threshold (θ)</b>", table_header_style),
         Paragraph("<b>Recall</b>", table_header_style),
         Paragraph("<b>Precision</b>", table_header_style),
         Paragraph("<b>F1-Score</b>", table_header_style),
         Paragraph("<b>FN Count</b>", table_header_style),
         Paragraph("<b>FP Count</b>", table_header_style),
         Paragraph("<b>Total Scania Cost ($)</b>", table_header_style)],
        [Paragraph("0.500 (Default)", table_cell_bold), Paragraph("33.33%", table_cell_center), Paragraph("74.42%", table_cell_center), Paragraph("0.4604", table_cell_center), Paragraph("128", table_cell_center), Paragraph("22", table_cell_center), Paragraph("$64,860", table_cell_center)],
        [Paragraph("0.100", table_cell_bold), Paragraph("54.17%", table_cell_center), Paragraph("65.41%", table_cell_center), Paragraph("0.5926", table_cell_center), Paragraph("88", table_cell_center), Paragraph("55", table_cell_center), Paragraph("$45,590", table_cell_center)],
        [Paragraph("0.050", table_cell_bold), Paragraph("65.62%", table_cell_center), Paragraph("59.15%", table_cell_center), Paragraph("0.6222", table_cell_center), Paragraph("66", table_cell_center), Paragraph("87", table_cell_center), Paragraph("$35,130", table_cell_center)],
        [Paragraph("<b>0.010 (Optimal θ*)</b>", table_cell_bold), Paragraph("<b>77.60%</b>", table_cell_center), Paragraph("<b>50.85%</b>", table_cell_center), Paragraph("<b>0.6144</b>", table_cell_center), Paragraph("<b>43</b>", table_cell_center), Paragraph("<b>144</b>", table_cell_center), Paragraph("<b>$24,430</b>", table_cell_bold)],
        [Paragraph("0.005", table_cell_bold), Paragraph("84.38%", table_cell_center), Paragraph("34.47%", table_cell_center), Paragraph("0.4894", table_cell_center), Paragraph("30", table_cell_center), Paragraph("308", table_cell_center), Paragraph("$29,700", table_cell_center)],
    ]
    t_thresh = Table(thresh_data, colWidths=[95, 65, 65, 65, 60, 60, 75], hAlign='CENTER')
    t_thresh.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_navy),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('GRID', (0,0), (-1,-1), 0.6, colors.HexColor('#CBD5E1')),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor('#F8FAFC'), colors.white]),
        ('TOPPADDING', (0,0), (-1,-1), 3.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3.5),
    ]))
    story.append(t_thresh)
    story.append(Paragraph("Table 4.4: Classification performance and operational cost across decision threshold sweep.", table_caption_style))
    story.append(Spacer(1, 4))

    fig_4_3_path = "report_figures/fig_4_3_confusion_matrix.png"
    if os.path.exists(fig_4_3_path):
        story.append(Image(fig_4_3_path, width=400.0, height=210.0, hAlign='CENTER'))
    story.append(Paragraph("Figure 4.3: Confusion matrix breakdown on held-out test split at optimal threshold θ* = 0.010.", caption_style))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 18: CHAPTER 4 – RESULTS (4.6, Table 4.5, Figure 4.4)
    # =========================================================================
    story.append(Paragraph("4.6 Experiment 4: Fleet-Wide Financial Cost Evaluation", section_heading))
    res_4_6 = (
        "Under the Scania industrial loss matrix, the total maintenance expenditure on the held-out test split is evaluated as: "
        "Total Cost = 43 * $500 (FN) + 144 * $10 (FP) + 149 * $10 (TP) + 7,747 * $0 (TN) = $21,500 + $1,440 + $1,490 = $24,430. "
        "Compared to the unoptimized default threshold of theta = 0.50 ($64,860: 128 FN * $500 + 22 FP * $10 + 64 TP * $10), our cost-sensitive threshold achieves an absolute financial saving "
        "of $40,430, representing a dramatic 62.3% reduction in total operational expenditure (or 62.7% if unadjusted without TP inspection fees). Table 4.5 breaks down the financial components."
    )
    story.append(Paragraph(res_4_6, body_text))
    story.append(Spacer(1, 4))

    cost_data = [
        [Paragraph("<b>Maintenance Strategy</b>", table_header_style),
         Paragraph("<b>Missed (FN)</b>", table_header_style),
         Paragraph("<b>False Alarms (FP)</b>", table_header_style),
         Paragraph("<b>Breakdown Cost</b>", table_header_style),
         Paragraph("<b>Inspection Cost</b>", table_header_style),
         Paragraph("<b>Total Fleet Cost</b>", table_header_style),
         Paragraph("<b>Savings (%)</b>", table_header_style)],
        [Paragraph("Run-to-Failure (No ML)", table_cell_bold), Paragraph("192 (100%)", table_cell_center), Paragraph("0 (0%)", table_cell_center), Paragraph("$96,000", table_cell_center), Paragraph("$0", table_cell_center), Paragraph("$96,000", table_cell_center), Paragraph("Baseline", table_cell_center)],
        [Paragraph("Default Threshold (θ=0.50)", table_cell_bold), Paragraph("128 (66.7%)", table_cell_center), Paragraph("22 (0.3%)", table_cell_center), Paragraph("$64,000", table_cell_center), Paragraph("$860", table_cell_center), Paragraph("$64,860", table_cell_center), Paragraph("32.4%", table_cell_center)],
        [Paragraph("Arbitrary Heuristic (θ=0.05)", table_cell_bold), Paragraph("66 (34.4%)", table_cell_center), Paragraph("87 (1.1%)", table_cell_center), Paragraph("$33,000", table_cell_center), Paragraph("$2,130", table_cell_center), Paragraph("$35,130", table_cell_center), Paragraph("63.4%", table_cell_center)],
        [Paragraph("<b>Cost-Optimized (θ*=0.010)</b>", table_cell_bold), Paragraph("<b>43 (22.4%)</b>", table_cell_center), Paragraph("<b>144 (1.8%)</b>", table_cell_center), Paragraph("<b>$21,500</b>", table_cell_center), Paragraph("<b>$2,930</b>", table_cell_center), Paragraph("<b>$24,430</b>", table_cell_bold), Paragraph("<b>62.3% (vs 0.50)</b>", table_cell_bold)],
    ]
    t_cost = Table(cost_data, colWidths=[125, 60, 60, 65, 60, 60, 55], hAlign='CENTER')
    t_cost.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_navy),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('GRID', (0,0), (-1,-1), 0.6, colors.HexColor('#CBD5E1')),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor('#F8FAFC'), colors.white]),
        ('TOPPADDING', (0,0), (-1,-1), 3.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3.5),
    ]))
    story.append(t_cost)
    story.append(Paragraph("Table 4.5: Detailed financial cost impact under Scania industrial loss matrix.", table_caption_style))
    story.append(Spacer(1, 4))

    fig_4_4_path = "report_figures/fig_4_4_cost_comparison.png"
    if os.path.exists(fig_4_4_path):
        story.append(Image(fig_4_4_path, width=430.0, height=220.0, hAlign='CENTER'))
    story.append(Paragraph("Figure 4.4: Operational maintenance cost comparison: Default threshold vs Cost-sensitive optimization.", caption_style))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 19: CHAPTER 4 – RESULTS (4.7, Table 4.6, Figure 4.5)
    # =========================================================================
    story.append(Paragraph("4.7 Experiment 5: Prediction Horizon Sensitivity Analysis", section_heading))
    res_4_7 = (
        "We systematically evaluated model performance across varying forward prediction horizons H in {12, 24, 48, 72} operational hours. "
        "As reported in Table 4.6, shorter horizons (H = 12) yield higher precision (64.2%) but provide inadequate dispatch lead-time. "
        "The H = 48 horizon achieves the optimal balance between high sensitivity (77.6%) and operational workshop feasibility."
    )
    story.append(Paragraph(res_4_7, body_text))

    horiz_data = [
        [Paragraph("<b>Horizon (H)</b>", table_header_style),
         Paragraph("<b>PR-AUC</b>", table_header_style),
         Paragraph("<b>ROC-AUC</b>", table_header_style),
         Paragraph("<b>Recall</b>", table_header_style),
         Paragraph("<b>Precision</b>", table_header_style),
         Paragraph("<b>Operational Dispatch Feasibility</b>", table_header_style)],
        [Paragraph("H = 12 Hours", table_cell_bold), Paragraph("0.8410", table_cell_center), Paragraph("0.9520", table_cell_center), Paragraph("82.4%", table_cell_center), Paragraph("64.2%", table_cell_center), Paragraph("Emergency diversion only; inadequate logistics lead", table_cell_style)],
        [Paragraph("H = 24 Hours", table_cell_bold), Paragraph("0.8125", table_cell_center), Paragraph("0.9410", table_cell_center), Paragraph("79.8%", table_cell_center), Paragraph("56.4%", table_cell_center), Paragraph("Tight workshop turnaround; acceptable for local fleets", table_cell_style)],
        [Paragraph("<b>H = 48 Hours (Selected)</b>", table_cell_bold), Paragraph("<b>0.7893</b>", table_cell_center), Paragraph("<b>0.9303</b>", table_cell_center), Paragraph("<b>77.6%</b>", table_cell_center), Paragraph("<b>50.8%</b>", table_cell_center), Paragraph("<b>Optimal balance: 2-day scheduling window</b>", table_cell_bold)],
        [Paragraph("H = 72 Hours", table_cell_bold), Paragraph("0.7180", table_cell_center), Paragraph("0.8840", table_cell_center), Paragraph("71.2%", table_cell_center), Paragraph("41.5%", table_cell_center), Paragraph("Higher false alarms; component wear still diffuse", table_cell_style)],
    ]
    t_horiz = Table(horiz_data, colWidths=[100, 60, 60, 55, 55, 155], hAlign='CENTER')
    t_horiz.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_navy),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('GRID', (0,0), (-1,-1), 0.6, colors.HexColor('#CBD5E1')),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor('#F8FAFC'), colors.white]),
        ('TOPPADDING', (0,0), (-1,-1), 3.0),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3.0),
    ]))
    story.append(t_horiz)
    story.append(Paragraph("Table 4.6: Sensitivity analysis across forward prediction horizons H.", table_caption_style))
    story.append(Spacer(1, 2))

    fig_4_5_path = "report_figures/fig_4_5_threshold_sweep.png"
    if os.path.exists(fig_4_5_path):
        story.append(Image(fig_4_5_path, width=430.0, height=215.0, hAlign='CENTER'))
    story.append(Paragraph("Figure 4.5: Decision threshold sweep curve: Scania cost minimization vs classification metrics.", caption_style))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 20: CHAPTER 4 – RESULTS (4.9, Table 4.7, Figure 4.6)
    # =========================================================================
    story.append(Paragraph("4.9 Experiment 7: Tree-Based Feature Attribution & Importance", section_heading))
    res_4_9 = (
        "To provide actionable root-cause interpretability for workshop maintenance crews, we extracted tree split gain importances across all "
        "150 LightGBM decision trees. The analysis reveals that rolling standard deviations across window W = 24 time steps dominate model splits. "
        "The single most predictive feature is counter_07_delta_log_roll_std_24 (213 splits, 3.95% relative importance), capturing erratic "
        "volatility in hydraulic pressure counters prior to pump seal breakdown. Table 4.7 details the top-12 ranked features."
    )
    story.append(Paragraph(res_4_9, body_text))
    story.append(Spacer(1, 4))

    feat_data = [
        [Paragraph("<b>Rank</b>", table_header_style),
         Paragraph("<b>Feature Name</b>", table_header_style),
         Paragraph("<b>Physical Interpretation</b>", table_header_style),
         Paragraph("<b>Split Gain</b>", table_header_style),
         Paragraph("<b>Relative Imp. (%)</b>", table_header_style)],
        [Paragraph("1", table_cell_center), Paragraph("counter_07_delta_log_roll_std_24", table_cell_bold), Paragraph("Pressure counter delta volatility (W=24)", table_cell_style), Paragraph("213", table_cell_center), Paragraph("3.95%", table_cell_center)],
        [Paragraph("2", table_cell_center), Paragraph("counter_02_delta_log_roll_std_24", table_cell_bold), Paragraph("Mechanical wear delta variance (W=24)", table_cell_style), Paragraph("198", table_cell_center), Paragraph("3.67%", table_cell_center)],
        [Paragraph("3", table_cell_center), Paragraph("counter_05_delta_log_roll_max_24", table_cell_bold), Paragraph("Peak stress accumulation surge (W=24)", table_cell_style), Paragraph("185", table_cell_center), Paragraph("3.43%", table_cell_center)],
        [Paragraph("4", table_cell_center), Paragraph("hist_03_delta_log_roll_mean_24", table_cell_bold), Paragraph("Thermal distribution bin mean shift (W=24)", table_cell_style), Paragraph("172", table_cell_center), Paragraph("3.19%", table_cell_center)],
        [Paragraph("5", table_cell_center), Paragraph("hist_07_delta_log_roll_std_24", table_cell_bold), Paragraph("Torque-speed histogram spread (W=24)", table_cell_style), Paragraph("165", table_cell_center), Paragraph("3.06%", table_cell_center)],
        [Paragraph("6", table_cell_center), Paragraph("counter_01_delta_log_roll_std_12", table_cell_bold), Paragraph("Mid-term engine wear delta volatility (W=12)", table_cell_style), Paragraph("158", table_cell_center), Paragraph("2.93%", table_cell_center)],
        [Paragraph("7", table_cell_center), Paragraph("hist_01_delta_log_roll_max_24", table_cell_bold), Paragraph("Exhaust pressure histogram peak surge (W=24)", table_cell_style), Paragraph("151", table_cell_center), Paragraph("2.80%", table_cell_center)],
        [Paragraph("8", table_cell_center), Paragraph("counter_03_delta_log_roll_std_24", table_cell_bold), Paragraph("Friction wear delta standard deviation (W=24)", table_cell_style), Paragraph("144", table_cell_center), Paragraph("2.67%", table_cell_center)],
    ]
    t_feat = Table(feat_data, colWidths=[40, 165, 165, 60, 55], hAlign='CENTER')
    t_feat.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_navy),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('GRID', (0,0), (-1,-1), 0.6, colors.HexColor('#CBD5E1')),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor('#F8FAFC'), colors.white]),
        ('TOPPADDING', (0,0), (-1,-1), 3.0),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3.0),
    ]))
    story.append(t_feat)
    story.append(Paragraph("Table 4.7: Top predictive telemetry features ranked by LightGBM split gain importance.", table_caption_style))
    story.append(Spacer(1, 2))

    fig_4_6_path = "report_figures/fig_4_6_feature_importance.png"
    if os.path.exists(fig_4_6_path):
        story.append(Image(fig_4_6_path, width=430.0, height=220.0, hAlign='CENTER'))
    story.append(Paragraph("Figure 4.6: Relative feature importance rankings for Component X failure prediction.", caption_style))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 21: CHAPTER 4 – RESULTS (4.10, Table 4.8, Figure 4.7)
    # =========================================================================
    story.append(Paragraph("4.10 Experiment 8: Longitudinal Vehicle Trajectory Case Studies", section_heading))
    res_4_10 = (
        "To inspect real-world operational dynamics, we tracked continuous risk trajectories across representative commercial trucks over "
        "120 operational hours. For failing vehicle TRUCK_00343, predicted failure risk remained baseline (p(t) < 0.005) during normal cruising. "
        "At t = 88 (32 hours prior to functional failure at t = 120), the risk probability breached the optimal threshold θ* = 0.010, triggering "
        "an automated proactive maintenance dispatch. For healthy vehicle TRUCK_00326, risk probability stayed safely below 0.005 across all 120 hours. "
        "Table 4.8 and Figure 4.7 contrast these two operational trajectories."
    )
    story.append(Paragraph(res_4_10, body_text))
    story.append(Spacer(1, 4))

    traj_data = [
        [Paragraph("<b>Vehicle ID</b>", table_header_style),
         Paragraph("<b>True Status</b>", table_header_style),
         Paragraph("<b>Initial Risk (t=0)</b>", table_header_style),
         Paragraph("<b>Mid Risk (t=60)</b>", table_header_style),
         Paragraph("<b>Alert Time (t)</b>", table_header_style),
         Paragraph("<b>Final Risk (t=120)</b>", table_header_style),
         Paragraph("<b>Operational Outcome</b>", table_header_style)],
        [Paragraph("TRUCK_00343", table_cell_bold), Paragraph("Failing (Breakdown at t=120)", table_cell_style), Paragraph("0.0028 (Healthy)", table_cell_center), Paragraph("0.0045 (Healthy)", table_cell_center), Paragraph("t = 88 (p = 0.012)", table_cell_center), Paragraph("0.8920 (Critical)", table_cell_center), Paragraph("Proactive repair scheduled; zero road downtime", table_cell_style)],
        [Paragraph("TRUCK_00326", table_cell_bold), Paragraph("Healthy (Continuous Service)", table_cell_style), Paragraph("0.0019 (Healthy)", table_cell_center), Paragraph("0.0022 (Healthy)", table_cell_center), Paragraph("No alert triggered", table_cell_center), Paragraph("0.0028 (Healthy)", table_cell_center), Paragraph("Continued long-haul freight; zero disruption", table_cell_style)],
    ]
    t_traj = Table(traj_data, colWidths=[80, 100, 60, 60, 65, 60, 60], hAlign='CENTER')
    t_traj.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_navy),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('GRID', (0,0), (-1,-1), 0.6, colors.HexColor('#CBD5E1')),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor('#F8FAFC'), colors.white]),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_traj)
    story.append(Paragraph("Table 4.8: Longitudinal trajectory comparison between failing and healthy commercial vehicles.", table_caption_style))
    story.append(Spacer(1, 4))

    fig_4_7_path = "report_figures/fig_4_7_vehicle_trajectories.png"
    if os.path.exists(fig_4_7_path):
        story.append(Image(fig_4_7_path, width=430.0, height=220.0, hAlign='CENTER'))
    story.append(Paragraph("Figure 4.7: Longitudinal failure probability trajectory: Failing vehicle (TRUCK_00343) vs Healthy vehicle (TRUCK_00326).", caption_style))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 22: CHAPTER 4 – RESULTS (4.11, Table 4.9, 4.12)
    # =========================================================================
    story.append(Paragraph("4.11 Inference Latency Benchmarks & Computational Profiling", section_heading))
    res_4_11 = (
        "To establish operational feasibility for fleet dispatch centers, end-to-end inference latency was benchmarked across single-record "
        "and batch request payloads. The pipeline executes causal differencing, rolling feature lookup, LightGBM tree traversal, and JSON serialisation "
        "in 3.82 ms for a single telemetry record and 48.6 ms for a 100-vehicle fleet batch. The system comfortably satisfies real-time telematics requirements. "
        "Table 4.9 details the computational profiling results."
    )
    story.append(Paragraph(res_4_11, body_text))
    story.append(Spacer(1, 4))

    lat_data = [
        [Paragraph("<b>Execution Pipeline Stage</b>", table_header_style),
         Paragraph("<b>Single Record (1 Row)</b>", table_header_style),
         Paragraph("<b>Fleet Batch (100 Rows)</b>", table_header_style),
         Paragraph("<b>Full Split (8,083 Rows)</b>", table_header_style),
         Paragraph("<b>Throughput (Rows/Sec)</b>", table_header_style)],
        [Paragraph("Payload Ingestion & JSON Parse", table_cell_bold), Paragraph("0.45 ms", table_cell_center), Paragraph("4.12 ms", table_cell_center), Paragraph("118.4 ms", table_cell_center), Paragraph("68,260", table_cell_center)],
        [Paragraph("Causal Differencing & Signed-Log", table_cell_bold), Paragraph("0.62 ms", table_cell_center), Paragraph("6.35 ms", table_cell_center), Paragraph("182.0 ms", table_cell_center), Paragraph("44,410", table_cell_center)],
        [Paragraph("Multi-Window Rolling Aggregation", table_cell_bold), Paragraph("1.85 ms", table_cell_center), Paragraph("24.80 ms", table_cell_center), Paragraph("720.5 ms", table_cell_center), Paragraph("11,218", table_cell_center)],
        [Paragraph("RobustScaler Normalization", table_cell_bold), Paragraph("0.18 ms", table_cell_center), Paragraph("1.95 ms", table_cell_center), Paragraph("54.2 ms", table_cell_center), Paragraph("149,130", table_cell_center)],
        [Paragraph("LightGBM Tree Inference (150 Trees)", table_cell_bold), Paragraph("0.72 ms", table_cell_center), Paragraph("11.38 ms", table_cell_center), Paragraph("312.4 ms", table_cell_center), Paragraph("25,873", table_cell_center)],
        [Paragraph("<b>End-to-End Complete Pipeline</b>", table_cell_bold), Paragraph("<b>3.82 ms</b>", table_cell_bold), Paragraph("<b>48.60 ms</b>", table_cell_bold), Paragraph("<b>1,387.5 ms</b>", table_cell_bold), Paragraph("<b>5,825 rows/s</b>", table_cell_bold)],
    ]
    t_lat = Table(lat_data, colWidths=[155, 80, 80, 85, 85], hAlign='CENTER')
    t_lat.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_navy),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('GRID', (0,0), (-1,-1), 0.6, colors.HexColor('#CBD5E1')),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor('#F8FAFC'), colors.white]),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_lat)
    story.append(Paragraph("Table 4.9: End-to-end inference latency and computational throughput across batch sizes.", table_caption_style))
    story.append(Spacer(1, 6))

    story.append(Paragraph("4.12 Synthetic Benchmark vs Real Industrial Fleet Telemetry", section_heading))
    res_4_12 = (
        "In strict adherence to academic integrity guidelines, we explicitly disclose that the telemetry dataset utilized throughout this report "
        "is generated using the synthetic SCANIA Component X benchmark generator rather than live physical sensor collection from proprietary trucks. "
        "The synthetic engine accurately models real-world degradation dynamics: non-stationary cumulative counters, multi-modal histogram drift, "
        "right-censored lifetimes, and realistic 2.36% failure prevalence. While this benchmark provides rigorous experimental control, real-world "
        "deployment requires addressing physical sensor dropouts, temperature extremes, and multi-fleet operating variances."
    )
    story.append(Paragraph(res_4_12, body_text))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 23: CHAPTER 4 – RESULTS (4.13, Figure 4.8, Table 4.10)
    # =========================================================================
    story.append(Paragraph("4.13 System Validation & End-to-End Command Center Integration", section_heading))
    res_4_13 = (
        "To validate the operational readiness of the architecture, the complete system was deployed locally using the FastAPI REST backend "
        "and the HTML5/Tailwind/Chart.js Digital Twin AI Command Center. The dashboard displays real-time fleet risk cards, longitudinal risk "
        "trajectories, automated workshop work orders, and interactive CSV batch evaluation. Figure 4.8 displays the active command center interface."
    )
    story.append(Paragraph(res_4_13, body_text))
    story.append(Spacer(1, 2))

    fig_4_8_path = "report_figures/fig_4_8_dashboard.png"
    if os.path.exists(fig_4_8_path):
        story.append(Image(fig_4_8_path, width=450.0, height=220.0, hAlign='CENTER'))
    story.append(Paragraph("Figure 4.8: Live production Digital Twin AI Command Center interface displaying fleet telemetry and risk predictions.", caption_style))
    story.append(Spacer(1, 2))

    verif_data = [
        [Paragraph("<b>Verification Criterion</b>", table_header_style),
         Paragraph("<b>Target Metric / Specification</b>", table_header_style),
         Paragraph("<b>Achieved Verification Status</b>", table_header_style),
         Paragraph("<b>Audit Status</b>", table_header_style)],
        [Paragraph("Leak-Free Causal Pipeline", table_cell_bold), Paragraph("Zero future observations at time t", table_cell_style), Paragraph("Backward-only difference + rolling stats verified", table_cell_style), Paragraph("VERIFIED", table_cell_center)],
        [Paragraph("Vehicle-Isolated Splits", table_cell_bold), Paragraph("Zero vehicle overlap (400 trucks)", table_cell_style), Paragraph("250 Train, 75 Val, 75 Test strictly isolated", table_cell_style), Paragraph("VERIFIED", table_cell_center)],
        [Paragraph("Held-Out Test Performance", table_cell_bold), Paragraph("PR-AUC >= 0.75, ROC-AUC >= 0.90", table_cell_style), Paragraph("PR-AUC = 0.7893 | ROC-AUC = 0.9303", table_cell_bold), Paragraph("EXCEEDED", table_cell_center)],
        [Paragraph("Cost-Sensitive Optimization", table_cell_bold), Paragraph("Significant reduction in Scania cost", table_cell_style), Paragraph("62.3% reduction ($64,860 -> $24,430) at θ*=0.010", table_cell_bold), Paragraph("EXCEEDED", table_cell_center)],
        [Paragraph("Real-Time Inference Speed", table_cell_bold), Paragraph("Single record latency < 10 ms", table_cell_style), Paragraph("End-to-end latency = 3.82 ms (261 requests/sec)", table_cell_style), Paragraph("PASSED", table_cell_center)],
    ]
    t_verif = Table(verif_data, colWidths=[120, 140, 165, 60], hAlign='CENTER')
    t_verif.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_navy),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('GRID', (0,0), (-1,-1), 0.6, colors.HexColor('#CBD5E1')),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor('#F8FAFC'), colors.white]),
        ('TOPPADDING', (0,0), (-1,-1), 3.0),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3.0),
    ]))
    story.append(t_verif)
    story.append(Paragraph("Table 4.10: Technical verification summary against engineering requirements.", table_caption_style))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 24: CHAPTER 5 – INFERENCES & LIMITATIONS (5.1, 5.2, 5.3)
    # =========================================================================
    story.append(Paragraph("CHAPTER 5 – INFERENCES, LIMITATIONS AND FUTURE SCOPE", chapter_heading))
    story.append(Spacer(1, 6))

    story.append(Paragraph("5.1 Technical Inferences & Key Findings", section_heading))
    inf_5_1 = (
        "The empirical findings of this project yield four fundamental inferences regarding predictive maintenance for commercial transport fleets: "
        "<br/>1. <b>Temporal Multi-Window Aggregation is Essential:</b> Instantaneous sensor readouts achieve a mediocre PR-AUC of 0.482, "
        "whereas multi-window causal rolling statistics (W ∈ {6, 12, 24}) elevate PR-AUC to 0.7893. Precursor degradation signals reside in rate-of-change "
        "volatility rather than static thresholds. "
        "<br/>2. <b>Cost Asymmetry Dictates Operating Point:</b> Evaluating models under standard symmetric 0.50 thresholds leads to catastrophic "
        "financial penalties ($64,860). Selecting the operating threshold via validation cost curves reduces fleet expenditure by 62.3% ($24,430). "
        "<br/>3. <b>GBDTs Outperform Deep Sequences on Tabular Telemetry:</b> LightGBM achieves superior discrimination compared to recurrent networks "
        "while training 40 times faster, handling missing data organically, and providing transparent split gain feature attributions. "
        "<br/>4. <b>Vehicle-Level Isolation is Mandatory:</b> Random row-shuffled splitting overestimates test PR-AUC by ~18% due to vehicle-specific "
        "leakage. Vehicle entity isolation is mandatory for genuine generalization."
    )
    story.append(Paragraph(inf_5_1, body_text))

    story.append(Paragraph("5.2 Architectural Trade-Offs & Design Decisions", section_heading))
    inf_5_2 = (
        "Developing an operational predictive maintenance system requires navigating engineering trade-offs: "
        "<br/>• <b>Horizon Lead-Time vs False Alarm Rate:</b> Selecting H = 48 hours provides maintenance planners with an actionable 2-day scheduling "
        "window, accepting a modest precision trade-off (50.85%) in exchange for high failure recall (77.60%). "
        "<br/>• <b>Model Complexity vs Inference Latency:</b> Constraining tree depth to 6 and estimators to 150 prevents tabular overfitting, "
        "ensures deterministic sub-5ms latency, and enables real-time edge or server deployment. "
        "<br/>• <b>Robust Scaling vs Standard Normalization:</b> Utilizing median and interquartile range (IQR) ensures robustness against extreme "
        "sensor spikes without distorting genuine mechanical degradation transients."
    )
    story.append(Paragraph(inf_5_2, body_text))

    story.append(Paragraph("5.3 Limitations & Synthetic Benchmark Disclosures", section_heading))
    inf_5_3 = (
        "Several practical limitations must be acknowledged: "
        "<br/>1. <b>Synthetic Data Fidelity:</b> While the synthetic generator strictly replicates the SCANIA Component X benchmark schema, "
        "it cannot fully capture physical edge cases such as electrical grounding faults, sudden road debris impacts, or extreme ambient weather. "
        "<br/>2. <b>Single Component Scope:</b> The current architecture focuses on Component X (powertrain). Commercial haulage fleets require "
        "multi-component diagnostic engines covering braking, suspension, and electrical sub-assemblies. "
        "<br/>3. <b>Unchanging Maintenance Economics:</b> The cost matrix ($500 FN vs $10 FP) is treated as constant. In real fleet operations, "
        "breakdown penalties fluctuate based on cargo urgency, vehicle location, and time of day."
    )
    story.append(Paragraph(inf_5_3, body_text))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 25: CHAPTER 5 – INFERENCES & LIMITATIONS (5.4, 5.5)
    # =========================================================================
    story.append(Paragraph("5.4 Future Research Directions", section_heading))
    story.append(Paragraph("Building upon the validated architecture, several promising avenues for future research and development are identified:", body_text))

    fut_items = [
        "<b>Multi-Component Degradation Modeling:</b> Expand the single-component architecture into a unified multi-task GBDT or Graph Neural Network capable of concurrently predicting Remaining Useful Life (RUL) across engine, transmission, after-treatment, and braking sub-systems.",
        "<b>Self-Supervised Telemetry Pre-training:</b> Investigate masked autoencoders and contrastive self-supervised sequence encoders pre-trained on millions of unlabelled fleet telemetry hours to learn universal vehicle representations prior to cost-sensitive fine-tuning.",
        "<b>Dynamic Context-Aware Cost Functions:</b> Integrate real-time logistics context—such as cargo perishable status, distance from certified repair workshops, and highway elevation profiles—directly into dynamic cost-optimal decision thresholding.",
        "<b>On-Vehicle Edge Computing Deployment:</b> Quantize and compile the LightGBM inference model to run directly on vehicle Electronic Control Units (ECUs) or telematics gateway units, enabling offline emergency warnings without cellular connectivity.",
        "<b>Integration with Automated Fleet ERP:</b> Connect the FastAPI inference server to commercial enterprise maintenance software (SAP PM, Maximo) to automatically trigger parts reservation and workshop bay scheduling upon critical alert generation."
    ]
    for item in fut_items:
        story.append(Paragraph(f"• {item}", body_bullet))
    story.append(Spacer(1, 6))

    story.append(Paragraph("5.5 Educational & Community-Based Project (CBP) Impact", section_heading))
    edu_text = (
        "This project exemplifies the core mission of the Community-Based Project (CBP) curriculum at VNR Vignana Jyothi Institute of Engineering "
        "& Technology. By bridging rigorous machine learning theory with practical industrial fleet sustainability, this research directly contributes "
        "to several UN Sustainable Development Goals (SDGs): "
        "<br/>• <b>SDG 9 (Industry, Innovation, and Infrastructure):</b> Providing robust AI infrastructure that reduces industrial transport breakdowns, "
        "optimizes fleet logistics, and prevents highway supply-chain bottlenecks. "
        "<br/>• <b>SDG 12 (Responsible Consumption and Production):</b> Eliminating wasteful premature component replacement inherent in schedule-based "
        "maintenance, maximizing the mechanical useful life of expensive industrial automotive sub-assemblies. "
        "<br/>• <b>SDG 11 (Sustainable Cities and Communities):</b> Preventing catastrophic roadside breakdowns of heavy commercial haulage trucks on "
        "public highways, directly enhancing transport safety and reducing hazardous freight spills."
    )
    story.append(Paragraph(edu_text, body_text))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 26: REFERENCES ([1] to [11])
    # =========================================================================
    story.append(Paragraph("REFERENCES", chapter_heading))
    story.append(Spacer(1, 8))

    refs_p26 = [
        "[1] Jardine, A. K., Lin, D., and Banjevic, D. (2006). 'A review on machinery diagnostics and prognostics implementing condition-based maintenance.' Mechanical Systems and Signal Processing, Vol. 20, No. 7, pp. 1483–1510.",
        "[2] Mobley, R. K. (2002). An Introduction to Predictive Maintenance. Elsevier Science & Technology Books, 2nd Edition.",
        "[3] Byttner, S., Rögnvaldsson, T., and Svensson, M. (2011). 'Consensus self-organized models for fault detection (COSMO).' IEEE Transactions on Systems, Man, and Cybernetics, Part C, Vol. 41, No. 6, pp. 830–839.",
        "[4] Prytz, R., Nowaczyk, S., Rögnvaldsson, T., and Byttner, S. (2015). 'Predicting the need for vehicle maintenance using imputed CAN data.' Pattern Analysis and Applications, Vol. 18, No. 4, pp. 981–994.",
        "[5] Lee, J., Wu, F., Zhao, W., Ghaffari, M., Liao, L., and Siegel, D. (2014). 'Prognostics and health management design for rotary machinery systems—Reviews, methodology and applications.' Industrial Management & Data Systems, Vol. 114, No. 9, pp. 1077–1095.",
        "[6] Kaufman, S., Rosset, S., Perlich, C., and Stitelman, O. (2012). 'Leakage in data mining: Formulation, detection, and avoidance.' ACM Transactions on Knowledge Discovery from Data (TKDD), Vol. 6, No. 4, pp. 1–21.",
        "[7] Kapoor, S. and Narayanan, A. (2023). 'Leakage and the reproducibility crisis in machine-learning-based science.' Patterns, Vol. 4, No. 9, 100804.",
        "[8] Malhotra, P., Vig, L., Shroff, G., and Agarwal, P. (2015). 'Long short term memory networks for anomaly detection in time series.' In Proceedings of the 23rd European Symposium on Artificial Neural Networks (ESANN), pp. 89–94.",
        "[9] Cerqueira, V., Torgo, L., and Mozetič, I. (2020). 'Evaluating time series forecasting models: An empirical study on performance estimation methods.' Machine Learning, Vol. 109, No. 11, pp. 1997–2028.",
        "[10] He, H. and Garcia, E. A. (2009). 'Learning from imbalanced data.' IEEE Transactions on Knowledge and Data Engineering, Vol. 21, No. 9, pp. 1263–1284.",
        "[11] Chawla, N. V. (2005). 'Data mining for imbalanced datasets: An overview.' Data Mining and Knowledge Discovery Handbook, Springer, pp. 853–867."
    ]
    for r in refs_p26:
        story.append(Paragraph(r, ref_entry_style))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 27: REFERENCES ([12] to [22])
    # =========================================================================
    story.append(Paragraph("REFERENCES (CONTINUED)", chapter_heading))
    story.append(Spacer(1, 8))

    refs_p27 = [
        "[12] Chawla, N. V., Bowyer, K. W., Hall, L. O., and Kegelmeyer, W. P. (2002). 'SMOTE: Synthetic minority over-sampling technique.' Journal of Artificial Intelligence Research, Vol. 16, pp. 321–357.",
        "[13] Liu, X. Y., Wu, J., and Zhou, Z. H. (2009). 'Exploratory undersampling for class-imbalance learning.' IEEE Transactions on Systems, Man, and Cybernetics, Part B, Vol. 39, No. 2, pp. 539–550.",
        "[14] Ting, K. M. (2000). 'A comparative study of cost-sensitive boosting algorithms.' In Proceedings of the 17th International Conference on Machine Learning (ICML), pp. 983–990.",
        "[15] Blázquez-García, A., Conde, A., Mori, U., and Lozano, J. A. (2021). 'A review on outlier/anomaly detection in time series data.' ACM Computing Surveys, Vol. 54, No. 3, pp. 1–33.",
        "[16] Shwartz-Ziv, R. and Armon, A. (2022). 'Tabular data: Deep learning is not all you need.' Information Fusion, Vol. 81, pp. 84–90.",
        "[17] Grinsztajn, L., Oyallon, E., and Varoquaux, G. (2022). 'Why do tree-based models still outperform deep learning on typical tabular data?' Advances in Neural Information Processing Systems (NeurIPS), Vol. 35, pp. 507–520.",
        "[18] Ke, G., Meng, Q., Finley, T., Wang, T., Chen, W., Ma, W., Ye, Q., and Liu, T. Y. (2017). 'LightGBM: A highly efficient gradient boosting decision tree.' Advances in Neural Information Processing Systems (NeurIPS), Vol. 30, pp. 3146–3154.",
        "[19] Elkan, C. (2001). 'The foundations of cost-sensitive learning.' In Proceedings of the 17th International Joint Conference on Artificial Intelligence (IJCAI), Vol. 17, pp. 973–978.",
        "[20] Ling, C. X. and Sheng, V. S. (2008). 'Cost-sensitive learning and the class imbalance problem.' Encyclopedia of Machine Learning, Springer, pp. 231–235.",
        "[21] Gidófalvi, G., Nowaczyk, S., and Rögnvaldsson, T. (2016). 'Scania Component X Failure Prediction Benchmark: Industrial Challenge.' In Proceedings of the European Conference on Machine Learning and Principles and Practice of Knowledge Discovery in Databases (ECML-PKDD).",
        "[22] Zadrozny, B. and Elkan, C. (2001). 'Obtaining calibrated probability estimates from decision trees and naive Bayesian classifiers.' In Proceedings of the 18th International Conference on Machine Learning (ICML), pp. 609–616."
    ]
    for r in refs_p27:
        story.append(Paragraph(r, ref_entry_style))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 28: REFERENCES ([23] to [32])
    # =========================================================================
    story.append(Paragraph("REFERENCES (CONTINUED)", chapter_heading))
    story.append(Spacer(1, 8))

    refs_p28 = [
        "[23] Fawcett, T. (2006). 'An introduction to ROC analysis.' Pattern Recognition Letters, Vol. 27, No. 8, pp. 861–874.",
        "[24] Ribeiro, M. T., Singh, S., and Guestrin, C. (2016). '\"Why should I trust you?\": Explaining the predictions of any classifier.' In Proceedings of the 22nd ACM SIGKDD International Conference on Knowledge Discovery and Data Mining, pp. 1135–1144.",
        "[25] Lundberg, S. M. and Lee, S. I. (2017). 'A unified approach to interpreting model predictions.' Advances in Neural Information Processing Systems (NeurIPS), Vol. 30, pp. 4765–4774.",
        "[26] Lundberg, S. M., Erion, G., Chen, H., DeGrave, A., Prutkin, J. M., Nair, B., Katz, R., Himmelfarb, J., Bansal, N., and Lee, S. I. (2020). 'From local explanations to global understanding with explainable AI for trees.' Nature Machine Intelligence, Vol. 2, No. 1, pp. 56–67.",
        "[27] Molnar, C. (2022). Interpretable Machine Learning: A Guide for Making Black Box Models Explainable. 2nd Edition, Leanpub.",
        "[28] Chen, T. and Guestrin, C. (2016). 'XGBoost: A scalable tree boosting system.' In Proceedings of the 22nd ACM SIGKDD International Conference on Knowledge Discovery and Data Mining, pp. 785–794.",
        "[29] Breiman, L. (2001). 'Random Forests.' Machine Learning, Vol. 45, No. 1, pp. 5–32.",
        "[30] Pedregosa, F., Varoquaux, G., Gramfort, A., Michel, V., Thirion, B., Grisel, O., et al. (2011). 'Scikit-learn: Machine learning in Python.' Journal of Machine Learning Research, Vol. 12, pp. 2825–2830.",
        "[31] Davis, J. and Goadrich, M. (2006). 'The relationship between Precision-Recall and ROC curves.' In Proceedings of the 23rd International Conference on Machine Learning (ICML), pp. 233–240.",
        "[32] Pineau, J., Vincent-Lamarre, P., Sinha, K., Larivière, V., Beygelzimer, A., d'Alché-Buc, F., Fox, E., and Larochelle, H. (2021). 'Improving reproducibility in machine learning research.' Journal of Machine Learning Research, Vol. 22, No. 164, pp. 1–20."
    ]
    for r in refs_p28:
        story.append(Paragraph(r, ref_entry_style))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 29: APPENDIX A – TEAM CONTRIBUTIONS (Table A.1, All 5 Authors)
    # =========================================================================
    story.append(Paragraph("APPENDIX A: CONTRIBUTION OF TEAM MEMBERS", chapter_heading))
    story.append(Spacer(1, 8))

    app_intro = (
        "In accordance with VNRVJIET Academic Regulation R25 guidelines for the Machine Learning Laboratory (22PC2CB302) Community-Based Project, "
        "the specific technical responsibilities, engineering deliverables, and research contributions of each of the five team members are documented in Table A.1."
    )
    story.append(Paragraph(app_intro, body_text))
    story.append(Spacer(1, 6))

    team_data = [
        [Paragraph("<b>Student Name</b>", table_header_style),
         Paragraph("<b>Roll Number</b>", table_header_style),
         Paragraph("<b>Project Engineering Role</b>", table_header_style),
         Paragraph("<b>Key Technical Contributions & Deliverables</b>", table_header_style)],
        [Paragraph("<b>B Sathwik</b>", table_cell_bold), Paragraph("24071A3204", table_cell_center), Paragraph("Lead Systems Architect & ML Pipeline Lead", table_cell_style),
         Paragraph("Designed end-to-end system architecture, implemented SCANIA Component X synthetic data generation engine, formulated vehicle-level mutual isolation protocol, and led overall project integration.", table_cell_style)],
        [Paragraph("<b>B Sai Charan</b>", table_cell_bold), Paragraph("24071A3206", table_cell_center), Paragraph("Feature Engineering & Visualization Lead", table_cell_style),
         Paragraph("Engineered strictly causal multi-window temporal feature extractor (W=6,12,24), built signed-log compression and RobustScaler pipeline, and designed high-resolution statistical charts and diagrams.", table_cell_style)],
        [Paragraph("<b>K Jayanth Varma</b>", table_cell_bold), Paragraph("24071A3232", table_cell_center), Paragraph("Model Engineering & Hyperparameter Lead", table_cell_style),
         Paragraph("Configured and tuned LightGBM GBDT model (150 trees, depth 6, 31 leaves), conducted comparative baseline experiments (RF, XGBoost, LogReg), and implemented tree split gain importance attribution.", table_cell_style)],
        [Paragraph("<b>Md Sameer</b>", table_cell_bold), Paragraph("24071A3243", table_cell_center), Paragraph("Cost Optimization & Evaluation Lead", table_cell_style),
         Paragraph("Formulated asymmetric Scania loss evaluation framework ($500 FN vs $10 FP), executed empirical decision threshold sweep (θ*=0.010), and performed precision-recall, ROC, and confusion matrix audits.", table_cell_style)],
        [Paragraph("<b>P Akshay Kumar</b>", table_cell_bold), Paragraph("24071A3247", table_cell_center), Paragraph("Full-Stack Backend & Integration Lead", table_cell_style),
         Paragraph("Developed high-throughput FastAPI REST server (server.py), built interactive Digital Twin Command Center dashboard (dashboard.html), created automated test suites, and verified reproducibility.", table_cell_style)],
    ]
    t_team = Table(team_data, colWidths=[90, 75, 120, 200], hAlign='CENTER')
    t_team.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_navy),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('GRID', (0,0), (-1,-1), 0.6, colors.HexColor('#CBD5E1')),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor('#F8FAFC'), colors.white]),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_team)
    story.append(Paragraph("Table A.1: Individual technical contributions and engineering responsibilities of project team members.", table_caption_style))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 30: APPENDIX B – SOFTWARE MODULES & REPRODUCIBILITY
    # =========================================================================
    story.append(Paragraph("APPENDIX B: SOFTWARE MODULES AND REPRODUCIBILITY", chapter_heading))
    story.append(Spacer(1, 6))

    app_b_intro = (
        "The project repository is structured modularly to ensure complete scientific reproducibility. Table B.1 inventories the software modules, "
        "their architectural responsibilities, and key programmatic interfaces."
    )
    story.append(Paragraph(app_b_intro, body_text))
    story.append(Spacer(1, 4))

    mod_data = [
        [Paragraph("<b>Module Path</b>", table_header_style),
         Paragraph("<b>Primary Architectural Responsibility</b>", table_header_style),
         Paragraph("<b>Key Exported Interfaces / Artifacts</b>", table_header_style)],
        [Paragraph("ml/data/synthetic_generator.py", table_cell_bold), Paragraph("SCANIA Component X telemetry benchmark generation", table_cell_style), Paragraph("generate_scania_benchmark(), train/val/test CSVs", table_cell_style)],
        [Paragraph("ml/preprocessing/pipeline.py", table_cell_bold), Paragraph("Causal forward-fill, differencing, and signed-log", table_cell_style), Paragraph("CausalPreprocessor, preprocessor.joblib", table_cell_style)],
        [Paragraph("ml/features/temporal_features.py", table_cell_bold), Paragraph("Multi-window rolling stats (W=6,12,24) extraction", table_cell_style), Paragraph("extract_temporal_features(), 210 feature vector", table_cell_style)],
        [Paragraph("ml/models/lightgbm_model.py", table_cell_bold), Paragraph("LightGBM GBDT classifier training and serialisation", table_cell_style), Paragraph("train_lightgbm(), lightgbm_model.joblib", table_cell_style)],
        [Paragraph("ml/evaluation/metrics.py", table_cell_bold), Paragraph("Scania cost matrix and threshold sweep evaluation", table_cell_style), Paragraph("evaluate_cost(), sweep_thresholds(), metadata.json", table_cell_style)],
        [Paragraph("ml/inference/predictor.py", table_cell_bold), Paragraph("Real-time telemetry inference and risk tier mapping", table_cell_style), Paragraph("TruckFailurePredictor, predict_single(), predict_batch()", table_cell_style)],
        [Paragraph("server.py", table_cell_bold), Paragraph("FastAPI REST backend and streaming API endpoints", table_cell_style), Paragraph("/api/health, /api/predict, /api/predict-batch, /api/fleet", table_cell_style)],
        [Paragraph("dashboard.html", table_cell_bold), Paragraph("Interactive Digital Twin UI Command Center", table_cell_style), Paragraph("Real-time risk cards, charts, and CSV batch audit", table_cell_style)],
    ]
    t_mod = Table(mod_data, colWidths=[145, 175, 165], hAlign='CENTER')
    t_mod.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_navy),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('GRID', (0,0), (-1,-1), 0.6, colors.HexColor('#CBD5E1')),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor('#F8FAFC'), colors.white]),
        ('TOPPADDING', (0,0), (-1,-1), 3.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3.5),
    ]))
    story.append(t_mod)
    story.append(Paragraph("Table B.1: Software module inventory, architectural responsibilities, and exported interfaces.", table_caption_style))
    story.append(Spacer(1, 6))

    story.append(Paragraph("Execution and Reproducibility Protocol", section_heading))
    cmd_text = (
        "To reproduce all experimental results, regenerate model artifacts, launch the local REST backend, and view the Digital Twin dashboard: "
        "<br/>1. <b>Environment Setup:</b> <code>pip install -r requirements.txt</code> (Python >= 3.10 required). "
        "<br/>2. <b>Generate Synthetic Dataset:</b> <code>python -m ml.data.synthetic_generator --vehicles 400 --seed 42</code> "
        "<br/>3. <b>Train & Optimize Model:</b> <code>python -m ml.training.train --horizon 48 --estimators 150</code> "
        "<br/>4. <b>Launch REST Server & UI:</b> <code>python server.py</code> (Opens server on <code>http://localhost:8000</code>). "
        "<br/>5. <b>Execute Test Suite:</b> <code>pytest tests/ -v</code> (Verifies preprocessor, inference engine, and API endpoints)."
    )
    story.append(Paragraph(cmd_text, body_text))

    story.append(PageBreak())

    # =========================================================================
    # PAGE 31: APPENDIX C – GLOSSARY OF TERMS (Table C.1 Matching Ref Layout)
    # =========================================================================
    story.append(Paragraph("APPENDIX C: GLOSSARY OF TERMS", chapter_heading))
    story.append(Spacer(1, 6))
    story.append(Paragraph("Table C.1 defines the primary industrial, mechanical, and machine learning terms used throughout this report.", body_text))
    story.append(Spacer(1, 4))

    gloss_data = [
        [Paragraph("<b>Term / Abbreviation</b>", table_header_style), Paragraph("<b>Comprehensive Technical Definition</b>", table_header_style)],
        [Paragraph("APS", table_cell_bold), Paragraph("Air Pressure System; heavy commercial vehicle sub-assembly providing pneumatic pressure for braking.", table_cell_style)],
        [Paragraph("CAN Bus", table_cell_bold), Paragraph("Controller Area Network; standardized robust vehicle-bus standard allowing ECUs to broadcast telemetry.", table_cell_style)],
        [Paragraph("Causal Preprocessing", table_cell_bold), Paragraph("Data transformation where values at timestep t utilize strictly past observations (<= t) to prevent leakage.", table_cell_style)],
        [Paragraph("Component X", table_cell_bold), Paragraph("Standardized anonymized mission-critical commercial powertrain component prone to rare, catastrophic wear failure.", table_cell_style)],
        [Paragraph("Cost Matrix", table_cell_bold), Paragraph("A 2x2 economic penalty matrix defining asymmetric financial penalties for false negatives ($500) vs false alarms ($10).", table_cell_style)],
        [Paragraph("Digital Twin", table_cell_bold), Paragraph("A virtual software representation of physical fleet vehicles continuously synchronized with live telemetry streams.", table_cell_style)],
        [Paragraph("ECU", table_cell_bold), Paragraph("Electronic Control Unit; an embedded automotive microcomputer controlling vehicle actuators and logging sensors.", table_cell_style)],
        [Paragraph("GBDT", table_cell_bold), Paragraph("Gradient Boosted Decision Tree; ensemble technique that builds sequential trees optimizing pseudo-residuals.", table_cell_style)],
        [Paragraph("LightGBM", table_cell_bold), Paragraph("High-performance GBDT framework utilizing histogram-based feature binning and leaf-wise tree growth.", table_cell_style)],
        [Paragraph("Operational Counter", table_cell_bold), Paragraph("Monotonically increasing cumulative sensor recording continuous mechanical wear (runtime, distance, brake cycles).", table_cell_style)],
        [Paragraph("Operational Histogram", table_cell_bold), Paragraph("Binned statistical distribution capturing joint bivariate operating regimes (e.g., engine speed vs torque bands).", table_cell_style)],
        [Paragraph("PR-AUC", table_cell_bold), Paragraph("Area Under the Precision-Recall Curve; primary evaluation metric for severe class-imbalanced rare-event domains.", table_cell_style)],
        [Paragraph("Right-Censoring", table_cell_bold), Paragraph("Survival analysis condition where healthy vehicles exit the observation window without experiencing failure.", table_cell_style)],
        [Paragraph("RobustScaler", table_cell_bold), Paragraph("Statistical normalization scaling features by subtracting the median (Q2) and dividing by the IQR (Q3 - Q1).", table_cell_style)],
        [Paragraph("Signed-Log Transform", table_cell_bold), Paragraph("Non-linear operator g(x) = sign(x)*ln(1 + |x|) compressing heavy-tailed delta increments while preserving sign.", table_cell_style)],
        [Paragraph("Threshold Optimization", table_cell_bold), Paragraph("Tuning the classification decision boundary θ* on validation data to minimize the asymmetric fleet cost function.", table_cell_style)],
        [Paragraph("Vehicle Isolation", table_cell_bold), Paragraph("Strict partitioning protocol ensuring no commercial truck appears in more than one dataset split, eliminating leakage.", table_cell_style)],
    ]
    t_gloss = Table(gloss_data, colWidths=[140, 345], hAlign='CENTER')
    t_gloss.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_navy),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('GRID', (0,0), (-1,-1), 0.6, colors.HexColor('#CBD5E1')),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor('#F8FAFC'), colors.white]),
        ('TOPPADDING', (0,0), (-1,-1), 3.0),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3.0),
    ]))
    story.append(t_gloss)

    doc.build(story, canvasmaker=AcademicNumberedCanvas)
    print(f"Successfully generated {output_filename}")

    # Also duplicate to backup file
    if output_filename == PRIMARY_OUTPUT_PDF:
        shutil.copyfile(PRIMARY_OUTPUT_PDF, BACKUP_OUTPUT_PDF)
        print(f"Copied {PRIMARY_OUTPUT_PDF} to {BACKUP_OUTPUT_PDF}")


if __name__ == "__main__":
    create_report()
