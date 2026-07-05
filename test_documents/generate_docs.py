"""
Synthetic Industrial Document Generator for IKIP Testing
=========================================================
Generates 5 realistic PDF documents with shared equipment tags
so the Knowledge Graph can demonstrate cross-document connections.

Shared Equipment Tags:
  P-101  Centrifugal Feed Pump (Unit 100)
  P-102  Booster Pump (Unit 100)
  E-301  Shell & Tube Heat Exchanger (Unit 300)
  V-201  Flash Separator Vessel (Unit 200)
  C-401  Reciprocating Compressor (Unit 400)
  TK-501 Storage Tank (Unit 500)

Documents Generated:
  1. Annual Equipment Inspection Report 2025
  2. SOP-MNT-001: Centrifugal Pump Maintenance Procedure
  3. Maintenance Work Order Log Q1-Q2 2025
  4. Incident Investigation Report IR-2025-017 (P-101 seal failure)
  5. Heat Exchanger E-301 Technical Specification & Datasheet
"""

from fpdf import FPDF
import os

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))


class IndustrialPDF(FPDF):
    """Base PDF class with consistent industrial document styling."""

    def __init__(self, title, doc_number=""):
        super().__init__()
        self.doc_title = title
        self.doc_number = doc_number
        self.set_auto_page_break(auto=True, margin=20)

    def header(self):
        self.set_font("Helvetica", "B", 9)
        self.set_text_color(100, 100, 100)
        self.cell(0, 5, "PETROMAX REFINING CORP. -- CONFIDENTIAL", align="L")
        if self.doc_number:
            self.cell(0, 5, self.doc_number, align="R", new_x="LMARGIN", new_y="NEXT")
        else:
            self.ln(5)
        self.set_draw_color(0, 80, 160)
        self.set_line_width(0.5)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(4)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}}", align="C")

    def section_title(self, title):
        self.set_font("Helvetica", "B", 14)
        self.set_text_color(0, 60, 120)
        self.cell(0, 10, title, new_x="LMARGIN", new_y="NEXT")
        self.set_draw_color(0, 80, 160)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(4)

    def sub_section(self, title):
        self.set_font("Helvetica", "B", 11)
        self.set_text_color(40, 40, 40)
        self.cell(0, 8, title, new_x="LMARGIN", new_y="NEXT")
        self.ln(2)

    def body_text(self, text):
        self.set_font("Helvetica", "", 10)
        self.set_text_color(30, 30, 30)
        self.multi_cell(0, 5.5, text)
        self.ln(3)

    def key_value(self, key, value):
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(60, 60, 60)
        self.cell(55, 6, key + ":")
        self.set_font("Helvetica", "", 10)
        self.set_text_color(30, 30, 30)
        self.cell(0, 6, value, new_x="LMARGIN", new_y="NEXT")

    def table_header(self, cols, widths):
        self.set_font("Helvetica", "B", 9)
        self.set_fill_color(0, 60, 120)
        self.set_text_color(255, 255, 255)
        for i, col in enumerate(cols):
            self.cell(widths[i], 7, col, border=1, fill=True, align="C")
        self.ln()

    def table_row(self, cols, widths, fill=False):
        self.set_font("Helvetica", "", 9)
        self.set_text_color(30, 30, 30)
        if fill:
            self.set_fill_color(235, 242, 250)
        for i, col in enumerate(cols):
            self.cell(widths[i], 6, col, border=1, fill=fill, align="C")
        self.ln()


# ============================================================================
# DOCUMENT 1: Annual Equipment Inspection Report
# ============================================================================
def generate_inspection_report():
    pdf = IndustrialPDF(
        "Annual Equipment Inspection Report -- Fiscal Year 2025",
        "RPT-INSP-2025-001"
    )
    pdf.alias_nb_pages()
    pdf.add_page()

    # Title page content
    pdf.set_font("Helvetica", "B", 22)
    pdf.set_text_color(0, 60, 120)
    pdf.ln(30)
    pdf.cell(0, 12, "ANNUAL EQUIPMENT", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 12, "INSPECTION REPORT", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)
    pdf.set_font("Helvetica", "", 14)
    pdf.set_text_color(80, 80, 80)
    pdf.cell(0, 8, "Fiscal Year 2025 -- Petromax Baytown Complex", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(15)
    pdf.set_font("Helvetica", "", 11)
    pdf.cell(0, 7, "Document Number: RPT-INSP-2025-001", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 7, "Revision: Rev. 2 (Final)", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 7, "Date: March 15, 2025", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 7, "Prepared by: R. Vasquez, Sr. Inspection Engineer", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 7, "Reviewed by: K. Tanaka, Plant Reliability Manager", align="C", new_x="LMARGIN", new_y="NEXT")

    # Page 2 -- Executive Summary
    pdf.add_page()
    pdf.section_title("1. Executive Summary")
    pdf.body_text(
        "This report presents the findings from the Annual Equipment Inspection program conducted "
        "across Units 100 through 500 at the Petromax Baytown Refining Complex during the period "
        "January 6, 2025 through March 10, 2025. A total of 47 equipment items were inspected as "
        "part of the API 510/570/653 inspection program. The inspection scope included pressure "
        "vessels, heat exchangers, rotating equipment, storage tanks, and associated piping systems."
    )
    pdf.body_text(
        "Overall, 38 equipment items (81%) were found in satisfactory condition with no immediate "
        "action required. Six items (13%) require corrective actions within 90 days, and three items "
        "(6%) have been flagged for priority attention. Most notably, Centrifugal Feed Pump P-101 "
        "exhibited significant mechanical seal degradation and bearing wear that warrants immediate "
        "seal replacement before the Q2 turnaround. Heat Exchanger E-301 showed tube bundle fouling "
        "exceeding 40% of design capacity, requiring chemical cleaning during the next planned outage."
    )

    # Page 3 -- Inspection Summary Table
    pdf.add_page()
    pdf.section_title("2. Inspection Summary by Unit")

    widths = [25, 40, 50, 35, 40]
    pdf.table_header(["Tag", "Description", "Type", "Condition", "Next Due"], widths)

    rows = [
        ["P-101", "Centrifugal Feed Pump", "API 610 Pump", "PRIORITY", "Q2 2025"],
        ["P-102", "Booster Pump", "API 610 Pump", "SATISFACTORY", "Q1 2026"],
        ["V-201", "Flash Separator", "Pressure Vessel", "MONITOR", "Q3 2025"],
        ["E-301", "Shell & Tube HX", "Heat Exchanger", "PRIORITY", "Q2 2025"],
        ["C-401", "Recip. Compressor", "API 618 Compressor", "SATISFACTORY", "Q1 2026"],
        ["TK-501", "Crude Storage Tank", "API 653 Tank", "MONITOR", "Q4 2025"],
    ]
    for i, row in enumerate(rows):
        pdf.table_row(row, widths, fill=(i % 2 == 0))

    # P-101 detailed findings
    pdf.ln(6)
    pdf.section_title("3. Detailed Findings -- Unit 100 (Feed System)")

    pdf.sub_section("3.1 P-101 -- Centrifugal Feed Pump")
    pdf.body_text(
        "Equipment Tag: P-101\n"
        "Manufacturer: Flowserve (Model: HPX 6x8x13)\n"
        "Installed: August 2018\n"
        "Service: Crude oil feed to atmospheric distillation column\n"
        "Operating Conditions: 285 degF, 165 psig discharge, 3,200 GPM rated"
    )
    pdf.body_text(
        "Inspection Findings:\n"
        "The mechanical seal (John Crane Type 4620) was found with visible leakage at the outboard "
        "seal face. Seal leakage rate measured at 12 drops/minute, exceeding the 3 drops/minute "
        "threshold per API 682. Vibration analysis conducted on January 22, 2025 revealed elevated "
        "readings at the drive-end bearing: 0.42 in/s peak velocity at 1x running speed (3,560 RPM), "
        "compared to the baseline of 0.18 in/s. Spectrum analysis indicates possible shaft misalignment. "
        "The coupling (Rexnord Omega E40) showed wear marks on the elastomeric element consistent with "
        "angular misalignment of approximately 0.008 inches."
    )
    pdf.body_text(
        "Recommendations:\n"
        "1. Replace mechanical seal assembly (John Crane Type 4620) -- Priority: HIGH\n"
        "2. Perform laser alignment of pump-motor coupling during seal replacement\n"
        "3. Replace coupling elastomeric element (Rexnord P/N E40-FLEX)\n"
        "4. Re-establish vibration baseline after corrective maintenance\n"
        "5. Schedule follow-up vibration survey within 30 days of repair\n"
        "Target completion: Before April 15, 2025 (Q2 turnaround window)"
    )

    pdf.sub_section("3.2 P-102 -- Booster Pump")
    pdf.body_text(
        "Equipment Tag: P-102\n"
        "Manufacturer: Sulzer (Model: MSD-D 150/6)\n"
        "Installed: August 2018\n"
        "Service: Intermediate pressure boost, downstream of P-101\n"
        "Operating Conditions: 310 degF, 320 psig discharge, 2,800 GPM rated"
    )
    pdf.body_text(
        "Inspection Findings:\n"
        "P-102 was found in satisfactory operating condition. Vibration levels at all measurement "
        "points are within acceptable limits per ISO 10816-3 (Zone A/B boundary). Bearing temperatures "
        "recorded at 168 degF drive-end and 155 degF non-drive-end, both within normal operating range. "
        "Mechanical seal (Flowserve QBW) showing no visible leakage. Suction strainer differential "
        "pressure reading 2.1 psi, below the 5 psi alarm threshold. Lubrication system oil analysis "
        "(Shell Morlina S4 B 220) returned satisfactory results -- water content < 100 ppm, particle "
        "count ISO 16/13/10."
    )
    pdf.body_text(
        "Recommendations:\n"
        "1. Continue routine condition monitoring per existing PM schedule\n"
        "2. Next comprehensive inspection due Q1 2026"
    )

    # V-201
    pdf.add_page()
    pdf.section_title("4. Detailed Findings -- Unit 200 (Separation)")

    pdf.sub_section("4.1 V-201 -- Flash Separator Vessel")
    pdf.body_text(
        "Equipment Tag: V-201\n"
        "Manufacturer: Boardman LLC\n"
        "Design Code: ASME Section VIII, Div. 1\n"
        "Installed: June 2016\n"
        "Service: Two-phase flash separation of crude feed\n"
        "Operating Conditions: 380 degF, 95 psig, two-phase crude/gas"
    )
    pdf.body_text(
        "Inspection Findings:\n"
        "Ultrasonic thickness (UT) measurements taken at 24 CML locations per API 510 inspection plan. "
        "Minimum measured wall thickness: 0.487 inches at CML-12 (lower shell course, 6 o'clock position), "
        "compared to nominal 0.625 inches. Calculated corrosion rate: 6.9 mils/year (long-term average). "
        "Remaining life at current rate: approximately 14 years, which exceeds the next inspection interval. "
        "Internal inspection via robotic crawler revealed minor pitting corrosion (maximum pit depth 0.045 inches) "
        "on the bottom head near the boot drain nozzle. Level instrumentation (Rosemount 5300 guided wave radar) "
        "verified and calibrated -- deviation within 0.5% of span."
    )
    pdf.body_text(
        "Recommendations:\n"
        "1. Continue monitoring CML-12 annually via UT spot check\n"
        "2. Evaluate internal coating application at next turnaround (2027)\n"
        "3. Next full API 510 internal inspection due Q3 2025 (aligned with planned outage)"
    )

    # E-301
    pdf.add_page()
    pdf.section_title("5. Detailed Findings -- Unit 300 (Heat Exchange)")

    pdf.sub_section("5.1 E-301 -- Shell and Tube Heat Exchanger")
    pdf.body_text(
        "Equipment Tag: E-301\n"
        "Manufacturer: Alfa Laval (TEMA Type: BEM)\n"
        "Installed: March 2017\n"
        "Service: Crude preheat via hot product return stream\n"
        "Design: 450 tubes, 3/4\" OD x 16 BWG, 20 ft effective length\n"
        "Shell Side: Hot product, 420 degF inlet / 290 degF outlet\n"
        "Tube Side: Crude feed, 250 degF inlet / 370 degF outlet\n"
        "Design Pressure: 300 psig (shell) / 250 psig (tube)"
    )
    pdf.body_text(
        "Inspection Findings:\n"
        "Performance monitoring data indicates heat transfer coefficient has declined by 38% over the past "
        "12 months. Shell-side pressure drop has increased from 4.2 psi to 11.7 psi, indicating significant "
        "fouling. Eddy current testing (ECT) of the tube bundle performed on February 14, 2025 identified "
        "12 tubes with wall loss exceeding 40% -- these tubes have been plugged. An additional 23 tubes "
        "showed wall loss between 20-40%. Total plugged tube count is now 31 out of 450 (6.9%), which is "
        "within the 10% maximum allowable per engineering evaluation. Tube sheet ligament measurements "
        "at the tube-to-tubesheet joints showed no significant erosion."
    )
    pdf.body_text(
        "Recommendations:\n"
        "1. Schedule chemical cleaning of shell side during Q2 2025 turnaround -- Priority: HIGH\n"
        "2. Consider tube bundle replacement if plugged tube count exceeds 45 (10%) at next inspection\n"
        "3. Install shell-side fouling monitor (DP transmitter) for real-time trending\n"
        "4. Evaluate antifouling coating (Curran International Plastocor) for tube bundle OD\n"
        "5. Increase tube-side velocity by 15% to reduce fouling tendency (requires P-101 capacity review)"
    )

    # C-401
    pdf.add_page()
    pdf.section_title("6. Detailed Findings -- Unit 400 (Gas Compression)")

    pdf.sub_section("6.1 C-401 -- Reciprocating Compressor")
    pdf.body_text(
        "Equipment Tag: C-401\n"
        "Manufacturer: Ariel Corporation (Model: JGK/4)\n"
        "Installed: November 2019\n"
        "Service: Off-gas compression from flash separator V-201 to fuel gas header\n"
        "Operating Conditions: 1st stage 15 psig suction / 65 psig discharge; "
        "2nd stage 60 psig suction / 185 psig discharge\n"
        "Driver: 500 HP electric motor, 1,200 RPM"
    )
    pdf.body_text(
        "Inspection Findings:\n"
        "All four cylinder bores measured within acceptable wear limits. Piston rod runout: "
        "0.0015 inches TIR (tolerance 0.003 inches). Valve inspection revealed minor wear on "
        "2nd stage discharge valve plates -- valve lift reduced to 0.085 inches from nominal 0.100 inches. "
        "Packing leakage rates within API 618 limits at 2.8 SCFM. Crosshead pin bearings inspected and "
        "found satisfactory. Rod load calculations verified within 95% of rated capacity. "
        "Pulsation dampener (Peerless orifice plate type) condition satisfactory."
    )
    pdf.body_text(
        "Recommendations:\n"
        "1. Plan 2nd stage discharge valve replacement at next opportunity (non-urgent, within 6 months)\n"
        "2. Continue packing leakage monitoring -- replacement recommended if exceeding 5 SCFM\n"
        "3. Next comprehensive API 618 inspection due Q1 2026"
    )

    # TK-501
    pdf.add_page()
    pdf.section_title("7. Detailed Findings -- Unit 500 (Storage)")

    pdf.sub_section("7.1 TK-501 -- Crude Oil Storage Tank")
    pdf.body_text(
        "Equipment Tag: TK-501\n"
        "Manufacturer: CB&I (now McDermott)\n"
        "Design Code: API 650\n"
        "Installed: 2012\n"
        "Service: Crude oil intermediate storage\n"
        "Capacity: 250,000 barrels\n"
        "Dimensions: 200 ft diameter x 48 ft shell height\n"
        "Roof Type: External floating roof with double-deck pontoon"
    )
    pdf.body_text(
        "Inspection Findings (API 653 External):\n"
        "Shell plate thickness measurements taken at 36 CML locations. Minimum shell thickness: "
        "0.372 inches at Course 1, CML-7 (nominal 0.500 inches). Long-term corrosion rate on Course 1: "
        "5.2 mils/year (soil-side). Floating roof condition: primary seal (mechanical shoe) in good "
        "condition, secondary seal (wiper type) showing wear on approximately 30% of circumference. "
        "Roof drain system functional -- no blockages observed. Settlement survey indicates uniform "
        "settlement of 1.2 inches over 13 years of service, within API 653 limits. Foundation ring wall "
        "shows no cracking or displacement. Cathodic protection system verified -- tank-to-soil potential "
        "-0.92V CSE (criterion: more negative than -0.85V CSE)."
    )
    pdf.body_text(
        "Recommendations:\n"
        "1. Replace secondary seal during next opportunity (within 12 months) -- Priority: MODERATE\n"
        "2. Continue annual external inspection per API 653\n"
        "3. Internal inspection (out-of-service) recommended by Q2 2027\n"
        "4. Verify cathodic protection rectifier output quarterly"
    )

    # Appendix
    pdf.add_page()
    pdf.section_title("8. Appendix -- Inspection Personnel & Certifications")
    pdf.body_text(
        "The following certified inspection personnel participated in this annual program:\n\n"
        "R. Vasquez -- API 510, API 570, API 653, ASNT Level II (UT, MT, PT, ECT)\n"
        "J. Morrison -- API 510, API 570, ASNT Level II (UT, RT)\n"
        "L. Chen -- API 653, CWI (Certified Welding Inspector)\n"
        "M. Okonkwo -- Vibration Analyst Category III (ISO 18436-2)\n"
        "S. Patel -- API 618 (Reciprocating Compressors), Machinery Diagnostic Specialist"
    )
    pdf.body_text(
        "This report has been prepared in accordance with API Recommended Practice 580 "
        "(Risk-Based Inspection) and the Petromax Refining Corp. Mechanical Integrity Program "
        "Manual (PM-MI-001, Rev. 8). All findings and recommendations are subject to review by "
        "the Plant Reliability Manager and the Process Safety Management Coordinator."
    )

    path = os.path.join(OUTPUT_DIR, "01_Annual_Equipment_Inspection_Report_2025.pdf")
    pdf.output(path)
    print(f"  [1/5] Generated: {os.path.basename(path)} ({pdf.page_no()} pages)")
    return path


# ============================================================================
# DOCUMENT 2: Standard Operating Procedure -- Pump Maintenance
# ============================================================================
def generate_sop_pump_maintenance():
    pdf = IndustrialPDF(
        "SOP-MNT-001: Centrifugal Pump Maintenance Procedure",
        "SOP-MNT-001 Rev. 4"
    )
    pdf.alias_nb_pages()
    pdf.add_page()

    pdf.set_font("Helvetica", "B", 20)
    pdf.set_text_color(0, 60, 120)
    pdf.ln(25)
    pdf.cell(0, 10, "STANDARD OPERATING PROCEDURE", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, "SOP-MNT-001", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 14)
    pdf.set_text_color(80, 80, 80)
    pdf.cell(0, 8, "Centrifugal Pump Mechanical Seal Replacement", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 8, "and Precision Alignment Procedure", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(15)

    pdf.set_font("Helvetica", "", 10)
    pdf.key_value("Applicable Equipment", "P-101, P-102, P-103, P-104 (API 610 centrifugal pumps)")
    pdf.key_value("Revision", "Rev. 4 (Effective January 10, 2025)")
    pdf.key_value("Author", "D. Kim, Rotating Equipment Engineer")
    pdf.key_value("Approved By", "K. Tanaka, Plant Reliability Manager")
    pdf.key_value("Review Cycle", "Annual")

    # Section 1
    pdf.add_page()
    pdf.section_title("1. Purpose and Scope")
    pdf.body_text(
        "This procedure defines the step-by-step process for mechanical seal replacement and precision "
        "shaft alignment on API 610 centrifugal pumps within the Petromax Baytown Complex. It applies "
        "specifically to the following equipment: P-101 (Centrifugal Feed Pump), P-102 (Booster Pump), "
        "P-103 (Transfer Pump), and P-104 (Recirculation Pump). All personnel performing this work must "
        "hold a minimum of Maintenance Technician Level II certification and have completed the "
        "Petromax Rotating Equipment Safety Training (Course RE-401)."
    )

    pdf.section_title("2. Safety Precautions")
    pdf.body_text(
        "DANGER: These pumps handle crude oil and hydrocarbon products at elevated temperatures (up to "
        "350 degF) and pressures (up to 400 psig). Failure to follow proper isolation and depressurization "
        "procedures can result in serious injury or death.\n\n"
        "Required PPE:\n"
        "- Flame-resistant coveralls (FRC) per NFPA 2112\n"
        "- Safety glasses with side shields (ANSI Z87.1)\n"
        "- Chemical-resistant gloves (neoprene or nitrile)\n"
        "- Steel-toe boots (ASTM F2413)\n"
        "- Hard hat (ANSI Z89.1 Type I)\n"
        "- H2S personal monitor (set to 10 ppm alarm / 20 ppm STEL)\n\n"
        "Required Permits:\n"
        "- Hot Work Permit (if any grinding, welding, or cutting is required)\n"
        "- Confined Space Entry Permit (if entering pump enclosure below grade)\n"
        "- Lock-Out/Tag-Out (LOTO) per OSHA 29 CFR 1910.147\n"
        "- Line Break Permit (for opening process connections)"
    )

    pdf.section_title("3. Pre-Job Planning")
    pdf.body_text(
        "3.1 Review the most recent vibration analysis report for the pump. For P-101, reference "
        "the baseline vibration data from the August 2018 commissioning report (VIB-P101-BASELINE). "
        "Current vibration trending data is available in the plant condition monitoring system "
        "(Emerson AMS Machinery Manager).\n\n"
        "3.2 Verify mechanical seal part number against the equipment bill of materials:\n"
        "  - P-101: John Crane Type 4620, API Plan 53B (pressurized dual seal)\n"
        "  - P-102: Flowserve QBW, API Plan 11 (single seal with flush)\n"
        "  - P-103: John Crane Type 4620, API Plan 53B\n"
        "  - P-104: Burgmann M7N, API Plan 21 (single seal with cooler)\n\n"
        "3.3 Ensure the following special tools are available:\n"
        "  - Laser alignment system (Pruftechnik ROTALIGN Ultra iS)\n"
        "  - Dial indicator set with magnetic base\n"
        "  - Bearing heater (SKF TIH 030m)\n"
        "  - Torque wrench set (calibrated within last 6 months)\n"
        "  - Seal installation sleeve (pump-model specific)"
    )

    pdf.add_page()
    pdf.section_title("4. Isolation and Preparation")
    pdf.body_text(
        "4.1 Notify the Control Room Operator (CRO) of the impending pump isolation. Coordinate with "
        "Operations to transfer service to the designated spare pump (if available).\n\n"
        "4.2 Implement LOTO per the pump-specific LOTO procedure:\n"
        "  - P-101 LOTO: LOTO-P101-001 (3 energy isolation points: motor breaker, suction valve, "
        "discharge valve)\n"
        "  - P-102 LOTO: LOTO-P102-001 (4 energy isolation points: motor breaker, suction valve, "
        "discharge valve, minimum flow recirculation valve)\n\n"
        "4.3 Drain the pump casing and flush with nitrogen to remove residual hydrocarbons. Verify "
        "atmosphere with a 4-gas detector (LEL < 10%, O2 19.5-23.5%, H2S < 10 ppm, CO < 25 ppm).\n\n"
        "4.4 Disconnect coupling guard. Remove coupling spacer (record spacer shim pack thickness "
        "for reinstallation reference)."
    )

    pdf.section_title("5. Mechanical Seal Removal")
    pdf.body_text(
        "5.1 Remove the gland plate bolts (typically 8 x 5/8\" UNC, Grade 8). Note: for P-101, the "
        "gland uses Superbolt multi-jackbolt tensioners -- refer to the Superbolt tightening procedure "
        "(torque each jackbolt to 45 ft-lbs in a star pattern, 3 passes).\n\n"
        "5.2 Slide the gland plate along the shaft toward the coupling end. For dual seals (P-101, P-103), "
        "first drain the barrier fluid reservoir and depressurize the seal chamber.\n\n"
        "5.3 Using the seal installation/removal sleeve, carefully slide the seal assembly off the shaft. "
        "Inspect the shaft sleeve for scoring, wear, or corrosion. Shaft sleeve OD should measure "
        "within 0.001\" of nominal (reference pump data sheet for exact dimension).\n\n"
        "5.4 Inspect the seal chamber bore for scoring or deposits. Clean with Scotch-Brite and solvent. "
        "Measure seal chamber bore ID -- must be within 0.002\" of nominal.\n\n"
        "5.5 Document all inspection measurements on Form MNT-SEAL-001 (Seal Replacement Inspection "
        "Checklist) and photograph the removed seal faces for failure analysis records."
    )

    pdf.add_page()
    pdf.section_title("6. Mechanical Seal Installation")
    pdf.body_text(
        "6.1 Verify the new seal part number matches the equipment BOM. Check the seal setting height "
        "against the seal manufacturer's installation drawing.\n\n"
        "6.2 Lubricate the shaft sleeve and seal O-rings with a compatible lubricant (for hydrocarbon "
        "service, use Krytox GPL-105). DO NOT use petroleum-based lubricants on elastomers.\n\n"
        "6.3 Install the seal using the installation sleeve. For John Crane Type 4620 (P-101, P-103), "
        "the seal setting clips must be in place during installation -- remove only after the gland "
        "plate is torqued to specification.\n\n"
        "6.4 Torque the gland plate bolts to the values specified in the seal installation drawing:\n"
        "  - P-101/P-103 (Superbolt): 45 ft-lbs per jackbolt\n"
        "  - P-102 (standard gland): 35 ft-lbs\n"
        "  - P-104 (standard gland): 30 ft-lbs\n\n"
        "6.5 For dual seal systems (P-101, P-103), fill the barrier fluid reservoir with the specified "
        "fluid (Petromax spec: synthetic barrier fluid, Shell Thermia B or equivalent). Pressurize "
        "the barrier system to 25 psi above seal chamber pressure."
    )

    pdf.section_title("7. Precision Shaft Alignment")
    pdf.body_text(
        "7.1 Install the laser alignment equipment (Pruftechnik ROTALIGN Ultra iS) per manufacturer's "
        "instructions. Mount sensor heads on the pump shaft and motor shaft coupling hubs.\n\n"
        "7.2 Acceptable alignment tolerances (at operating temperature):\n"
        "  Offset (Parallel): 0.002\" maximum\n"
        "  Angular: 0.0005\"/inch maximum\n\n"
        "7.3 Perform initial alignment measurement. Record values:\n"
        "  - Horizontal offset\n"
        "  - Vertical offset\n"
        "  - Horizontal angularity\n"
        "  - Vertical angularity\n\n"
        "7.4 Make corrections by shimming the motor feet (for vertical corrections) and sliding the "
        "motor (for horizontal corrections). Use stainless steel pre-cut shim stock only -- minimum "
        "shim thickness 0.002\", maximum shim pack 4 shims per foot.\n\n"
        "7.5 Re-measure and iterate until alignment is within tolerance at all positions. Document "
        "final alignment values on Form MNT-ALIGN-001 (Precision Alignment Record).\n\n"
        "7.6 Apply thermal growth compensation as specified in the pump data sheet. For P-101, the "
        "calculated thermal offset is 0.005\" (motor high) to compensate for operating temperature "
        "differential between pump (285 degF) and motor (180 degF ambient)."
    )

    pdf.add_page()
    pdf.section_title("8. Reassembly and Startup")
    pdf.body_text(
        "8.1 Reinstall coupling spacer and guard. Verify coupling guard clearances per plant standard.\n\n"
        "8.2 Remove all LOTO locks and tags per the de-isolation procedure. Verify with the CRO that "
        "all isolation points have been restored.\n\n"
        "8.3 Slowly open the suction valve and verify pump casing is fully vented (open vent valve "
        "on top of casing until steady liquid stream is observed).\n\n"
        "8.4 Coordinate with CRO for initial pump start. Monitor for:\n"
        "  - Seal leakage (visual check at gland plate)\n"
        "  - Vibration (handheld readings at all bearing housings)\n"
        "  - Bearing temperature (infrared gun readings)\n"
        "  - Discharge pressure and flow rate\n\n"
        "8.5 After 30 minutes of stable operation, take a full set of vibration readings (triaxial at "
        "each bearing housing) and compare to the pre-job baseline.\n\n"
        "8.6 After 24 hours of operation, perform a follow-up check of seal leakage, vibration levels, "
        "and bearing temperatures. Enter results in the Computerized Maintenance Management System "
        "(IBM Maximo, Work Order reference).\n\n"
        "8.7 Schedule a 30-day post-maintenance vibration survey to verify sustained acceptable operation."
    )

    pdf.section_title("9. Documentation and Records")
    pdf.body_text(
        "All work performed under this SOP must be documented in the following:\n\n"
        "1. IBM Maximo Work Order -- include labor hours, parts consumed, and condition codes\n"
        "2. Form MNT-SEAL-001 -- Seal Replacement Inspection Checklist\n"
        "3. Form MNT-ALIGN-001 -- Precision Alignment Record\n"
        "4. Vibration baseline file uploaded to Emerson AMS Machinery Manager\n"
        "5. Photographic record of removed seal faces (stored in Equipment History folder)\n\n"
        "Completed forms must be submitted to the Maintenance Planner within 48 hours of job completion. "
        "Any deviations from this procedure must be documented on a Management of Change (MOC) form "
        "and approved by the Reliability Engineer prior to implementation."
    )

    path = os.path.join(OUTPUT_DIR, "02_SOP_MNT_001_Pump_Seal_Replacement.pdf")
    pdf.output(path)
    print(f"  [2/5] Generated: {os.path.basename(path)} ({pdf.page_no()} pages)")
    return path


# ============================================================================
# DOCUMENT 3: Maintenance Work Order Log
# ============================================================================
def generate_work_order_log():
    pdf = IndustrialPDF(
        "Maintenance Work Order Log -- Q1/Q2 2025",
        "LOG-WO-2025-H1"
    )
    pdf.alias_nb_pages()
    pdf.add_page()

    pdf.set_font("Helvetica", "B", 20)
    pdf.set_text_color(0, 60, 120)
    pdf.ln(25)
    pdf.cell(0, 10, "MAINTENANCE WORK ORDER LOG", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)
    pdf.set_font("Helvetica", "", 14)
    pdf.set_text_color(80, 80, 80)
    pdf.cell(0, 8, "Petromax Baytown Refining Complex", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 8, "January 1, 2025 -- June 30, 2025", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(10)
    pdf.set_font("Helvetica", "", 10)
    pdf.key_value("Document Number", "LOG-WO-2025-H1")
    pdf.key_value("Prepared by", "Maintenance Planning Department")
    pdf.key_value("System of Record", "IBM Maximo Asset Management v7.6.1.3")

    pdf.add_page()
    pdf.section_title("1. Work Order Summary -- Q1 2025 (January - March)")

    widths = [22, 18, 28, 55, 22, 22, 23]
    pdf.table_header(["WO #", "Tag", "Date", "Description", "Priority", "Status", "Hours"], widths)

    q1_orders = [
        ["5001", "P-101", "01/22", "Vibration analysis - elevated DE brg", "HIGH", "CLOSED", "4.0"],
        ["5002", "E-301", "01/28", "ECT tube inspection - 12 tubes plugged", "HIGH", "CLOSED", "16.0"],
        ["5003", "V-201", "02/03", "UT thickness survey - 24 CML locations", "MED", "CLOSED", "8.0"],
        ["5004", "C-401", "02/10", "Valve inspection - 2nd stg disc valve", "LOW", "CLOSED", "6.0"],
        ["5005", "TK-501", "02/18", "API 653 external inspection", "MED", "CLOSED", "12.0"],
        ["5006", "P-101", "02/25", "Mech seal leak investigation", "HIGH", "CLOSED", "3.0"],
        ["5007", "P-102", "03/05", "Routine PM - oil sample & vib check", "LOW", "CLOSED", "2.5"],
        ["5008", "E-301", "03/12", "Performance test - U-value calc", "MED", "CLOSED", "4.0"],
    ]

    for i, row in enumerate(q1_orders):
        pdf.table_row(row, widths, fill=(i % 2 == 0))

    pdf.ln(6)

    # Detailed WO narratives
    pdf.sub_section("WO-5001: P-101 Vibration Analysis")
    pdf.body_text(
        "Date: January 22, 2025\n"
        "Equipment: P-101 -- Centrifugal Feed Pump\n"
        "Requestor: M. Okonkwo, Vibration Analyst\n\n"
        "Findings: Route-based vibration survey identified elevated readings at P-101 drive-end bearing "
        "position. Overall velocity measured 0.42 in/s peak, exceeding the Alert level of 0.35 in/s per "
        "the plant vibration severity chart (based on ISO 10816-3). Frequency spectrum shows dominant "
        "peak at 1x running speed (59.3 Hz = 3,560 RPM), indicating possible unbalance or misalignment. "
        "Sideband activity observed at bearing defect frequencies suggesting early-stage inner race "
        "degradation.\n\n"
        "Action: Recommended mechanical seal and coupling inspection at earliest opportunity. Work Order "
        "WO-5006 raised for follow-up investigation. Monitoring frequency increased from monthly to weekly."
    )

    pdf.sub_section("WO-5002: E-301 Eddy Current Testing")
    pdf.body_text(
        "Date: January 28, 2025\n"
        "Equipment: E-301 -- Shell & Tube Heat Exchanger\n"
        "Requestor: R. Vasquez, Sr. Inspection Engineer\n\n"
        "Findings: Eddy Current Testing (ECT) performed on 450 tubes using Eddyfi Ectane 2 instrument. "
        "Results: 12 tubes identified with >40% wall loss -- all plugged with tapered brass plugs per "
        "ASME PCC-2. An additional 23 tubes showed 20-40% wall loss, flagged for re-inspection at next "
        "outage. Total plugged tube count now 31/450 (6.9%). Fouling evident on shell side based on "
        "pressure drop increase (4.2 to 11.7 psi). Calculated fouling factor: 0.0035 hr-ft2-F/BTU "
        "versus design value of 0.001.\n\n"
        "Action: Chemical cleaning recommended during Q2 turnaround. Work Order WO-5012 to be raised "
        "for cleaning scope. Engineering evaluation req'd if plugged count approaches 45 tubes (10%)."
    )

    pdf.add_page()
    pdf.sub_section("WO-5006: P-101 Mechanical Seal Leak Investigation")
    pdf.body_text(
        "Date: February 25, 2025\n"
        "Equipment: P-101 -- Centrifugal Feed Pump\n"
        "Requestor: Operations (CRO shift report -- visible drip from seal gland)\n\n"
        "Findings: Visual inspection confirmed active leakage from the outboard seal face of the John "
        "Crane Type 4620 dual mechanical seal. Leak rate quantified at approximately 12 drops/minute "
        "by timed drip test. API 682 acceptance criterion is 3 drops/minute for hydrocarbon service. "
        "Barrier fluid (Shell Thermia B) reservoir level dropping approximately 0.5 liters/day. "
        "Seal faces inspected via borescope -- visible scoring and heat checking on the outboard face. "
        "Probable root cause: operating at reduced suction pressure during the January cold snap caused "
        "brief cavitation events that damaged the seal faces.\n\n"
        "Action: Seal replacement scheduled for April 2025 turnaround window. Follow SOP-MNT-001 Rev. 4 "
        "for the seal replacement procedure. In the interim, increase barrier fluid monitoring frequency "
        "to daily and maintain reservoir topped up. Pump operation approved to continue with restrictions "
        "(maximum 90% rated flow to minimize seal face loading)."
    )

    pdf.section_title("2. Work Order Summary -- Q2 2025 (April - June)")

    pdf.table_header(["WO #", "Tag", "Date", "Description", "Priority", "Status", "Hours"], widths)

    q2_orders = [
        ["5010", "P-101", "04/07", "Mech seal replacement per SOP-MNT-001", "CRIT", "CLOSED", "24.0"],
        ["5011", "P-101", "04/08", "Laser alignment post-seal replacement", "CRIT", "CLOSED", "6.0"],
        ["5012", "E-301", "04/14", "Shell-side chemical cleaning", "HIGH", "CLOSED", "18.0"],
        ["5013", "V-201", "04/20", "Level instrument recalibration", "LOW", "CLOSED", "2.0"],
        ["5014", "TK-501", "05/05", "Secondary seal partial replacement", "MED", "OPEN", "Est. 40"],
        ["5015", "P-101", "05/12", "30-day post-repair vib survey", "MED", "CLOSED", "3.0"],
        ["5016", "C-401", "06/01", "2nd stg discharge valve replacement", "MED", "PLANNED", "Est. 8"],
        ["5017", "E-301", "06/15", "Post-cleaning performance test", "MED", "CLOSED", "4.0"],
    ]

    for i, row in enumerate(q2_orders):
        pdf.table_row(row, widths, fill=(i % 2 == 0))

    pdf.ln(6)
    pdf.sub_section("WO-5010: P-101 Mechanical Seal Replacement")
    pdf.body_text(
        "Date: April 7, 2025\n"
        "Equipment: P-101 -- Centrifugal Feed Pump\n"
        "Procedure Reference: SOP-MNT-001 Rev. 4\n"
        "Lead Technician: A. Ramirez, Maintenance Tech Level III\n\n"
        "Work Performed:\n"
        "- Pump isolated per LOTO-P101-001 (3 energy isolation points)\n"
        "- Casing drained and nitrogen purged; atmosphere verified safe\n"
        "- Removed John Crane Type 4620 dual mechanical seal (S/N: JC-46200-29847)\n"
        "- Seal face inspection: outboard face exhibited severe heat checking and a radial crack "
        "approximately 0.3\" long; inboard face showed moderate wear grooves (depth ~0.001\")\n"
        "- Shaft sleeve inspected: OD measured 3.4985\" (nominal 3.500\") -- within tolerance\n"
        "- Seal chamber bore measured 4.8760\" (nominal 4.875\") -- within tolerance\n"
        "- Installed new John Crane Type 4620 seal (S/N: JC-46200-31052)\n"
        "- Gland plate torqued per specification (Superbolt jackbolts, 45 ft-lbs, star pattern, 3 passes)\n"
        "- Barrier fluid system charged with Shell Thermia B, pressurized to 190 psig "
        "(25 psi above seal chamber)\n"
        "- Coupling element (Rexnord Omega E40) replaced with new\n\n"
        "Total labor: 24 hours (3 technicians x 8 hours)\n"
        "Parts consumed: 1x JC Type 4620 seal kit, 1x Rexnord E40 coupling element, 5 gal Shell Thermia B"
    )

    pdf.add_page()
    pdf.sub_section("WO-5011: P-101 Laser Alignment")
    pdf.body_text(
        "Date: April 8, 2025\n"
        "Equipment: P-101 -- Centrifugal Feed Pump\n"
        "Alignment Equipment: Pruftechnik ROTALIGN Ultra iS (S/N: RT-20-1847)\n"
        "Technician: B. Thompson, Alignment Specialist\n\n"
        "Pre-alignment (as-found):\n"
        "  Vertical offset: +0.012\" (motor high)\n"
        "  Horizontal offset: -0.006\" (motor left)\n"
        "  Vertical angularity: +0.0018\"/inch\n"
        "  Horizontal angularity: -0.0009\"/inch\n\n"
        "Post-alignment (final):\n"
        "  Vertical offset: +0.006\" (motor high, includes 0.005\" thermal growth compensation)\n"
        "  Horizontal offset: +0.001\" (within tolerance)\n"
        "  Vertical angularity: +0.0003\"/inch (within tolerance)\n"
        "  Horizontal angularity: -0.0002\"/inch (within tolerance)\n\n"
        "Shim corrections: Added 0.008\" to outboard motor feet, removed 0.004\" from inboard motor feet. "
        "Motor slid 0.007\" to the right. Total shim pack at each foot: 3 shims (within 4-shim maximum).\n\n"
        "Result: PASS -- all values within tolerance per SOP-MNT-001 Section 7."
    )

    pdf.sub_section("WO-5015: P-101 Post-Repair Vibration Survey (30-Day)")
    pdf.body_text(
        "Date: May 12, 2025\n"
        "Equipment: P-101 -- Centrifugal Feed Pump\n"
        "Analyst: M. Okonkwo, Vibration Analyst CAT III\n\n"
        "Results:\n"
        "  Drive-end bearing: 0.15 in/s peak velocity (1x) -- EXCELLENT\n"
        "  Non-drive-end bearing: 0.12 in/s peak velocity (1x) -- EXCELLENT\n"
        "  No bearing defect frequencies detected\n"
        "  Seal area vibration: within normal limits\n\n"
        "Comparison to pre-repair: Drive-end bearing velocity reduced from 0.42 in/s to 0.15 in/s, "
        "a 64% improvement. New vibration baseline established and uploaded to AMS Machinery Manager.\n\n"
        "Assessment: Mechanical seal replacement and precision alignment have fully resolved the "
        "elevated vibration condition. P-101 returned to normal monitoring frequency (monthly)."
    )

    path = os.path.join(OUTPUT_DIR, "03_Maintenance_Work_Order_Log_2025.pdf")
    pdf.output(path)
    print(f"  [3/5] Generated: {os.path.basename(path)} ({pdf.page_no()} pages)")
    return path


# ============================================================================
# DOCUMENT 4: Incident Investigation Report
# ============================================================================
def generate_incident_report():
    pdf = IndustrialPDF(
        "Incident Investigation Report -- IR-2025-017",
        "IR-2025-017"
    )
    pdf.alias_nb_pages()
    pdf.add_page()

    pdf.set_font("Helvetica", "B", 20)
    pdf.set_text_color(180, 30, 30)
    pdf.ln(25)
    pdf.cell(0, 10, "INCIDENT INVESTIGATION REPORT", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(3)
    pdf.set_font("Helvetica", "B", 14)
    pdf.set_text_color(0, 60, 120)
    pdf.cell(0, 10, "IR-2025-017", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 13)
    pdf.set_text_color(80, 80, 80)
    pdf.cell(0, 8, "P-101 Mechanical Seal Failure and Hydrocarbon Release", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(10)

    pdf.set_font("Helvetica", "", 10)
    pdf.key_value("Incident Date", "January 15, 2025, 03:42 AM CST")
    pdf.key_value("Location", "Unit 100, P-101 Pump Skid, Petromax Baytown Complex")
    pdf.key_value("Severity Classification", "OSHA Recordable -- Near Miss (no injuries)")
    pdf.key_value("Investigation Lead", "T. Nakamura, Process Safety Engineer")
    pdf.key_value("Investigation Team", "R. Vasquez, D. Kim, M. Okonkwo, J. Rodriguez (Ops Supervisor)")
    pdf.key_value("Report Date", "February 28, 2025")

    pdf.add_page()
    pdf.section_title("1. Incident Description")
    pdf.body_text(
        "On January 15, 2025 at approximately 03:42 AM CST, the Control Room Operator (CRO) received "
        "a high-level alarm on the P-101 mechanical seal barrier fluid reservoir (LIA-10105). The alarm "
        "indicated that the barrier fluid level had dropped below the low-low setpoint of 25%, "
        "suggesting a significant seal leak. Simultaneously, a combustible gas detector (GD-10103) "
        "located near the P-101 pump skid alarmed at 15% LEL."
    )
    pdf.body_text(
        "The CRO immediately initiated the Emergency Operating Procedure EOP-100-01 (Unit 100 Pump "
        "Trip and Isolation). P-101 was tripped remotely from the control room at 03:44 AM. The suction "
        "and discharge block valves (HV-10101 and HV-10102) were remotely closed. The area fire water "
        "deluge system was placed in manual standby."
    )
    pdf.body_text(
        "The on-shift Operations Supervisor (J. Rodriguez) dispatched two operators to the P-101 area "
        "at 03:50 AM. They confirmed visible crude oil spray from the outboard mechanical seal gland "
        "area. Estimated release volume: 5-8 gallons of crude oil, contained within the pump skid drip "
        "pan and secondary containment. No personnel were in the immediate vicinity at the time of the "
        "release. No fire or ignition occurred. The area was barricaded and the release was cleaned up "
        "by the environmental response team by 06:30 AM."
    )

    pdf.section_title("2. Timeline of Events")
    pdf.body_text(
        "December 18, 2024, 14:00: Routine vibration survey by M. Okonkwo identifies slightly elevated "
        "readings at P-101 drive-end bearing (0.28 in/s vs. 0.18 in/s baseline). Noted as \"watch\" "
        "status in condition monitoring database.\n\n"
        "January 8-10, 2025: Extreme cold weather event (temperatures below 10 degF for 72 hours). Plant "
        "operates in cold weather contingency mode. Suction piping to P-101 experiences partial "
        "trace heat failure; suction temperature drops from 250 degF to approximately 180 degF.\n\n"
        "January 12, 2025, 08:00: Operators report unusual noise from P-101 during shift rounds. "
        "Noise described as intermittent \"crackling\" sound near the seal area. Noted in shift log "
        "but no work order raised.\n\n"
        "January 13, 2025, 22:00: Barrier fluid consumption rate noted as increasing (0.3 liters/day, "
        "up from normal 0.05 liters/day). CRO noted in shift log.\n\n"
        "January 15, 2025, 03:42: Barrier fluid low-low alarm. Gas detector alarm at 15% LEL. "
        "Pump tripped and isolated. Crude oil spray observed from seal area.\n\n"
        "January 15, 2025, 06:30: Area cleaned, release contained. No environmental impact "
        "outside secondary containment."
    )

    pdf.add_page()
    pdf.section_title("3. Root Cause Analysis")
    pdf.body_text(
        "The investigation team performed a root cause analysis using the TapRooT methodology "
        "and fault tree analysis. The physical root cause and contributing factors are summarized below."
    )

    pdf.sub_section("3.1 Physical Root Cause")
    pdf.body_text(
        "Examination of the removed mechanical seal (John Crane Type 4620, S/N: JC-46200-29847) "
        "by the manufacturer's failure analysis laboratory revealed the following:\n\n"
        "- The outboard seal face (silicon carbide rotating element) exhibited severe thermal shock "
        "cracking. A radial crack approximately 7mm long propagated from the ID to the OD of the "
        "seal face.\n"
        "- The inboard seal face showed heat checking patterns consistent with dry running.\n"
        "- The elastomeric secondary seals (O-rings, Viton Grade GF) showed no degradation.\n\n"
        "The thermal shock cracking was caused by rapid temperature transients during the January "
        "cold weather event. When suction temperature dropped from 250 degF to 180 degF over a short period, "
        "the differential thermal expansion between the silicon carbide seal face and the stainless "
        "steel seal hardware exceeded the design limits, initiating the crack."
    )

    pdf.sub_section("3.2 Contributing Factors")
    pdf.body_text(
        "1. HEAT TRACE FAILURE: The electric heat tracing on the P-101 suction piping (Circuit HT-101-S) "
        "failed due to a defective thermostat (Chromalox model 1900-11). This allowed the suction "
        "temperature to drop well below the minimum recommended pump inlet temperature of 220 degF.\n\n"
        "2. INADEQUATE COLD WEATHER PROCEDURE: The existing cold weather contingency procedure "
        "(WI-CW-001) did not include specific guidance for monitoring P-101 suction temperature or "
        "triggering a pump trip on low suction temperature.\n\n"
        "3. DELAYED RESPONSE TO ABNORMAL NOISE: The unusual noise reported on January 12 was an early "
        "indicator of seal distress. The observation was recorded in the shift log but was not escalated "
        "to the Reliability Engineer or Vibration Analyst for assessment. No work order was raised.\n\n"
        "4. VIBRATION MONITORING GAP: The elevated vibration reading from December 2024 (0.28 in/s) "
        "was noted as \"watch\" status but the monitoring interval was not increased from monthly to "
        "weekly until after the January 22 follow-up survey -- which occurred AFTER the incident."
    )

    pdf.add_page()
    pdf.section_title("4. Corrective Actions")

    widths2 = [10, 80, 30, 30, 40]
    pdf.table_header(["#", "Action Item", "Owner", "Due Date", "Status"], widths2)
    actions = [
        ["1", "Replace P-101 mech seal per SOP-MNT-001", "D. Kim", "04/15/25", "COMPLETE"],
        ["2", "Repair heat trace circuit HT-101-S", "Electrical", "02/15/25", "COMPLETE"],
        ["3", "Install low suction temp alarm on P-101", "I&E", "03/01/25", "COMPLETE"],
        ["4", "Update cold weather procedure WI-CW-001", "T. Nakamura", "03/15/25", "COMPLETE"],
        ["5", "Abnormal situation mgmt refresher training", "Operations", "04/30/25", "COMPLETE"],
        ["6", "Review all pump seal barrier fluid alarms", "I&E", "05/30/25", "IN PROGRESS"],
        ["7", "Evaluate upgrade to SiC/SiC seal faces", "D. Kim", "06/30/25", "IN PROGRESS"],
    ]
    for i, row in enumerate(actions):
        pdf.table_row(row, widths2, fill=(i % 2 == 0))

    pdf.ln(6)
    pdf.section_title("5. Lessons Learned")
    pdf.body_text(
        "1. ABNORMAL SITUATION RECOGNITION: Unusual equipment sounds are critical early warning "
        "indicators and must always be reported AND escalated to the appropriate technical resource "
        "(Reliability Engineer or Vibration Analyst). An \"observe and report\" culture alone is "
        "insufficient -- operators must have clear guidance on when to initiate a work order.\n\n"
        "2. COLD WEATHER PREPAREDNESS: Heat tracing is a safety-critical system for process equipment "
        "operating above ambient temperature. Heat trace circuits for pump suction lines and seal "
        "systems should be verified functional before each winter season.\n\n"
        "3. CONDITION MONITORING FOLLOW-UP: When vibration readings reach \"watch\" status, the "
        "monitoring frequency should be automatically escalated. This has been codified into the "
        "updated Vibration Monitoring Procedure (VIB-PROC-002, Rev. 5).\n\n"
        "4. BARRIER FLUID MONITORING: The barrier fluid consumption rate is a leading indicator of "
        "seal health. An automatic trending alarm on consumption rate (not just level) should be "
        "implemented for all dual mechanical seal systems. This action is being tracked under "
        "Corrective Action #6."
    )

    pdf.section_title("6. PSM Classification")
    pdf.body_text(
        "This incident is classified as a Near Miss under the Petromax Process Safety Management "
        "program. It is reportable to OSHA as a process safety incident under 29 CFR 1910.119 "
        "because it involved the release of a highly hazardous chemical (crude oil) above the "
        "threshold quantity. The incident has been entered into the Petromax SAFER incident tracking "
        "system (Case #PM-2025-00417) and will be presented at the Q2 2025 Plant Safety Review Meeting."
    )

    path = os.path.join(OUTPUT_DIR, "04_Incident_Report_IR_2025_017_P101_Seal_Failure.pdf")
    pdf.output(path)
    print(f"  [4/5] Generated: {os.path.basename(path)} ({pdf.page_no()} pages)")
    return path


# ============================================================================
# DOCUMENT 5: Heat Exchanger E-301 Technical Specification
# ============================================================================
def generate_e301_datasheet():
    pdf = IndustrialPDF(
        "E-301 Shell & Tube Heat Exchanger -- Technical Specification",
        "DS-E301-001 Rev. 3"
    )
    pdf.alias_nb_pages()
    pdf.add_page()

    pdf.set_font("Helvetica", "B", 20)
    pdf.set_text_color(0, 60, 120)
    pdf.ln(25)
    pdf.cell(0, 10, "EQUIPMENT DATA SHEET", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(3)
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, "E-301 -- Shell and Tube Heat Exchanger", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 14)
    pdf.set_text_color(80, 80, 80)
    pdf.cell(0, 8, "Crude Preheat Service -- Unit 300", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(15)

    pdf.set_font("Helvetica", "", 10)
    pdf.key_value("Document Number", "DS-E301-001 Rev. 3")
    pdf.key_value("Manufacturer", "Alfa Laval (formerly Aalborg Industries)")
    pdf.key_value("PO Number", "PM-PO-2016-03045")
    pdf.key_value("Year Manufactured", "2016")
    pdf.key_value("Year Installed", "March 2017")
    pdf.key_value("TEMA Type Designation", "BEM (Bonnet, Single Pass, Fixed Tubesheet)")

    # Design data
    pdf.add_page()
    pdf.section_title("1. Design Data -- Shell Side")

    kv_data_shell = [
        ("Fluid", "Hot product return (heavy naphtha)"),
        ("Flow Rate", "850,000 lb/hr"),
        ("Inlet Temperature", "420 degF (215.6 degC)"),
        ("Outlet Temperature", "290 degF (143.3 degC)"),
        ("Operating Pressure", "185 psig"),
        ("Design Pressure", "300 psig"),
        ("Design Temperature", "500 degF (260 degC)"),
        ("Material (Shell)", "SA-516 Gr. 70, normalized"),
        ("Shell ID", "42 inches"),
        ("Corrosion Allowance", "0.125 inches"),
        ("Shell Thickness (nominal)", "0.750 inches"),
        ("Baffle Type", "Single segmental, 25% cut"),
        ("Baffle Spacing", "12 inches (central), 9 inches (inlet/outlet)"),
        ("MDMT", "-20 degF (impact tested)"),
    ]
    for k, v in kv_data_shell:
        pdf.key_value(k, v)

    pdf.ln(4)
    pdf.section_title("2. Design Data -- Tube Side")

    kv_data_tube = [
        ("Fluid", "Crude oil feed (desalted)"),
        ("Flow Rate", "1,200,000 lb/hr"),
        ("Inlet Temperature", "250 degF (121.1 degC)"),
        ("Outlet Temperature", "370 degF (187.8 degC)"),
        ("Operating Pressure", "195 psig"),
        ("Design Pressure", "250 psig"),
        ("Design Temperature", "450 degF (232.2 degC)"),
        ("Number of Tubes", "450"),
        ("Tube OD", "0.750 inches (3/4\")"),
        ("Tube BWG", "16 (wall thickness 0.065 inches)"),
        ("Tube Length (effective)", "20 feet"),
        ("Tube Pitch", "1.0 inch, triangular (30 deg)"),
        ("Tube Material", "SA-179 (seamless carbon steel)"),
        ("Tube-to-Tubesheet Joint", "Expanded and seal welded"),
        ("Number of Passes", "1 (single pass)"),
    ]
    for k, v in kv_data_tube:
        pdf.key_value(k, v)

    pdf.add_page()
    pdf.section_title("3. Thermal Performance Data")
    pdf.body_text(
        "The following thermal performance parameters are based on the original design calculations "
        "and the as-built guarantee test performed during commissioning in April 2017."
    )

    perf_widths = [60, 45, 45, 40]
    pdf.table_header(["Parameter", "Design", "Guarantee", "Unit"], perf_widths)
    perf_rows = [
        ["Heat Duty", "52.4", "51.8", "MMBTU/hr"],
        ["Overall U (clean)", "128", "125", "BTU/hr-ft2-F"],
        ["Overall U (fouled)", "95", "--", "BTU/hr-ft2-F"],
        ["LMTD (corrected)", "48.2", "47.5", " degF"],
        ["Effective Area", "7,069", "7,069", "ft2"],
        ["Fouling Factor (shell)", "0.001", "--", "hr-ft2-F/BTU"],
        ["Fouling Factor (tube)", "0.002", "--", "hr-ft2-F/BTU"],
        ["Shell-side DP (clean)", "3.5", "3.8", "psi"],
        ["Tube-side DP (clean)", "5.2", "5.5", "psi"],
    ]
    for i, row in enumerate(perf_rows):
        pdf.table_row(row, perf_widths, fill=(i % 2 == 0))

    pdf.ln(6)
    pdf.section_title("4. Current Operating Performance (as of March 2025)")
    pdf.body_text(
        "Based on the most recent performance test conducted on March 12, 2025 (ref: WO-5008), the "
        "following operating performance was recorded. Note that 31 tubes have been plugged as of "
        "January 2025 (ref: WO-5002), reducing the effective tube count to 419."
    )

    curr_widths = [60, 50, 50, 30]
    pdf.table_header(["Parameter", "Current", "Design (clean)", "Status"], curr_widths)
    curr_rows = [
        ["Overall U (operating)", "79", "128", "DEGRADED"],
        ["Heat Duty (actual)", "45.2", "52.4", "87% of design"],
        ["Crude Outlet Temp", "348 degF", "370 degF", "22 degF below"],
        ["Shell-side DP", "11.7 psi", "3.5 psi", "FOULED"],
        ["Tube-side DP", "6.8 psi", "5.2 psi", "MARGINAL"],
        ["Plugged Tubes", "31 / 450", "0", "6.9%"],
    ]
    for i, row in enumerate(curr_rows):
        pdf.table_row(row, curr_widths, fill=(i % 2 == 0))

    pdf.ln(4)
    pdf.body_text(
        "Analysis: The 38% decline in overall heat transfer coefficient from clean design value "
        "(128 to 79 BTU/hr-ft2-F) is primarily attributable to shell-side fouling, as evidenced by "
        "the 234% increase in shell-side pressure drop (3.5 to 11.7 psi). The crude outlet temperature "
        "of 348 degF (versus design 370 degF) means the downstream fired heater (H-301) must compensate with "
        "an additional 7.2 MMBTU/hr of fuel firing, at an estimated cost of $12,800/day in additional "
        "fuel gas consumption."
    )
    pdf.body_text(
        "Recommendation: Chemical cleaning of the shell side during the Q2 2025 turnaround is expected "
        "to restore the overall U to approximately 110-115 BTU/hr-ft2-F (85-90% of clean value). "
        "Long-term, the engineering team should evaluate the installation of an automatic backwash "
        "system or continuous antifouling treatment (e.g., Nalco EC1270A) to extend the cleaning interval."
    )

    # Nozzle schedule
    pdf.add_page()
    pdf.section_title("5. Nozzle Schedule")

    noz_widths = [20, 50, 25, 30, 25, 40]
    pdf.table_header(["Nozzle", "Service", "Size", "Rating", "Facing", "Material"], noz_widths)
    noz_rows = [
        ["N1", "Shell Inlet", "16\"", "300#", "RF", "SA-105"],
        ["N2", "Shell Outlet", "16\"", "300#", "RF", "SA-105"],
        ["N3", "Tube Inlet", "18\"", "150#", "RF", "SA-105"],
        ["N4", "Tube Outlet", "18\"", "150#", "RF", "SA-105"],
        ["N5", "Shell Vent", "2\"", "300#", "RF", "SA-105"],
        ["N6", "Shell Drain", "2\"", "300#", "RF", "SA-105"],
        ["N7", "Tube Vent", "2\"", "150#", "RF", "SA-105"],
        ["N8", "Tube Drain", "2\"", "150#", "RF", "SA-105"],
        ["N9", "Shell DP Conn.", "1\"", "300#", "NPT", "SA-105"],
        ["N10", "Tube DP Conn.", "1\"", "150#", "NPT", "SA-105"],
    ]
    for i, row in enumerate(noz_rows):
        pdf.table_row(row, noz_widths, fill=(i % 2 == 0))

    pdf.ln(6)
    pdf.section_title("6. Maintenance History Summary")
    pdf.body_text(
        "The following is a summary of significant maintenance events for E-301 since installation:\n\n"
        "March 2017: Commissioning and guarantee test. Performance verified within 2% of design.\n\n"
        "September 2018: First shell-side chemical cleaning (Zyme-Flow product). U-value restored "
        "to 122 BTU/hr-ft2-F.\n\n"
        "March 2020: ECT inspection during turnaround. 8 tubes plugged (>40% wall loss). Performance "
        "acceptable.\n\n"
        "October 2021: Shell-side chemical cleaning. U-value restored to 118 BTU/hr-ft2-F.\n\n"
        "April 2023: ECT inspection. 11 additional tubes plugged (total 19). Fouling factor trending "
        "higher -- cleaning interval reduced from 24 months to 18 months.\n\n"
        "January 2025: ECT inspection (ref: WO-5002). 12 additional tubes plugged (total 31). "
        "Performance significantly degraded. Chemical cleaning scheduled for Q2 2025 turnaround.\n\n"
        "April 2025: Shell-side chemical cleaning performed (ref: WO-5012). Post-cleaning performance "
        "test (ref: WO-5017) confirmed U-value restored to 112 BTU/hr-ft2-F."
    )

    pdf.section_title("7. Interconnected Equipment")
    pdf.body_text(
        "E-301 is part of the crude preheat train and is directly interconnected with the following "
        "equipment:\n\n"
        "Upstream (Tube Side Feed): P-101 (Centrifugal Feed Pump) supplies crude oil to E-301 tube side "
        "via 18\" line 100-CR-018-A5. Any capacity changes to P-101 directly affect E-301 tube-side "
        "velocity and fouling tendency.\n\n"
        "Downstream (Tube Side): V-201 (Flash Separator Vessel) receives the heated crude from E-301. "
        "The crude outlet temperature from E-301 directly affects V-201 flash efficiency.\n\n"
        "Upstream (Shell Side): The hot product return stream from the atmospheric column overhead "
        "condenser feeds the E-301 shell side.\n\n"
        "Downstream (Shell Side): The cooled product exits E-301 and flows to TK-501 (Storage Tank) "
        "via the product rundown cooler.\n\n"
        "Note: P-102 (Booster Pump) operates in series with P-101 and indirectly affects E-301 "
        "through its impact on total system flow rate and pressure."
    )

    path = os.path.join(OUTPUT_DIR, "05_E301_Heat_Exchanger_Technical_Specification.pdf")
    pdf.output(path)
    print(f"  [5/5] Generated: {os.path.basename(path)} ({pdf.page_no()} pages)")
    return path


# ============================================================================
# Main
# ============================================================================
if __name__ == "__main__":
    print("=" * 60)
    print("IKIP Synthetic Document Generator")
    print("=" * 60)
    print(f"Output directory: {OUTPUT_DIR}\n")
    print("Generating documents...\n")

    files = []
    files.append(generate_inspection_report())
    files.append(generate_sop_pump_maintenance())
    files.append(generate_work_order_log())
    files.append(generate_incident_report())
    files.append(generate_e301_datasheet())

    print(f"\nDone! Generated {len(files)} PDF documents.")
    print("\nEquipment tag cross-reference matrix:")
    print("  P-101 -> Docs 1, 2, 3, 4, 5  (appears in ALL documents)")
    print("  P-102 -> Docs 1, 2, 3, 5")
    print("  E-301 -> Docs 1, 3, 5")
    print("  V-201 -> Docs 1, 3, 5")
    print("  C-401 -> Docs 1, 3")
    print("  TK-501 -> Docs 1, 3, 5")
    print("\nUpload these via the IKIP Document Manager to populate")
    print("the Knowledge Graph with cross-document entity connections.")
