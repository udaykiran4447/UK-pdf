import streamlit as st
import pdfplumber
import pandas as pd
import re
from io import BytesIO
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

st.set_page_config(
    page_title="UK-PDF Extractors",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cinzel+Decorative:wght@400;700;900&family=Cinzel:wght@400;600;700&family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans:wght@300;400;600&display=swap');

    html, body, [class*="css"] {
        font-family: 'IBM Plex Sans', sans-serif;
    }

    .stApp {
        background: #0a0a0f;
        min-height: 100vh;
    }

    /* ── HERO SECTION ── */
    .hero {
        position: relative;
        text-align: center;
        padding: 3.5rem 1rem 2.5rem;
        overflow: hidden;
    }

    .hero::before {
        content: '';
        position: absolute;
        inset: 0;
        background:
            radial-gradient(ellipse 80% 60% at 50% 0%, rgba(180,120,20,0.18) 0%, transparent 70%),
            radial-gradient(ellipse 60% 40% at 20% 80%, rgba(160,40,20,0.12) 0%, transparent 60%),
            radial-gradient(ellipse 50% 50% at 80% 90%, rgba(100,60,180,0.10) 0%, transparent 60%);
        pointer-events: none;
    }

    /* decorative horizontal rule with ornament */
    .divider {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 1rem;
        margin: 0.6rem auto 0.8rem;
    }
    .divider-line {
        flex: 1;
        max-width: 220px;
        height: 1.5px;
        background: linear-gradient(90deg, transparent, #c8952a, transparent);
    }
    .divider-gem {
        width: 10px; height: 10px;
        background: #c8952a;
        transform: rotate(45deg);
        box-shadow: 0 0 8px #c8952a88;
    }

    .hero-eyebrow {
        font-family: 'Cinzel', serif;
        font-size: 0.78rem;
        letter-spacing: 0.35em;
        text-transform: uppercase;
        color: #c8952a;
        margin-bottom: 0.5rem;
    }

    .hero-title {
        font-family: 'Cinzel Decorative', serif !important;
        font-size: clamp(2.2rem, 6vw, 4.4rem) !important;
        font-weight: 900 !important;
        line-height: 1.1 !important;
        letter-spacing: 0.04em !important;
        background: linear-gradient(135deg,
            #f5e6c0 0%,
            #c8952a 25%,
            #fff5d6 50%,
            #c8952a 75%,
            #f5e6c0 100%);
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        background-clip: text !important;
        text-shadow: none !important;
        filter: drop-shadow(0 2px 24px rgba(200,149,42,0.35));
        margin: 0 !important;
        padding: 0 !important;
    }

    .hero-tagline {
        font-family: 'Cinzel', serif;
        font-size: 0.9rem;
        color: #8a7a60;
        letter-spacing: 0.12em;
        margin-top: 0.5rem;
    }

    .hero-tagline span {
        color: #c8952a;
    }

    /* ── APP SELECTOR TABS ── */
    .app-tabs {
        display: flex;
        justify-content: center;
        gap: 0;
        margin: 1.5rem auto 0;
        max-width: 560px;
        border: 1.5px solid #2a2418;
        border-radius: 6px;
        overflow: hidden;
    }

    /* ── SECTION HEADER ── */
    .section-label {
        font-family: 'Cinzel', serif;
        font-size: 0.68rem;
        letter-spacing: 0.3em;
        text-transform: uppercase;
        color: #4a3f2a;
        text-align: center;
        margin: 1.6rem 0 0.4rem;
    }

    /* ── STREAMLIT TAB OVERRIDES ── */
    .stTabs [data-baseweb="tab-list"] {
        background: #0e0d0a !important;
        border-bottom: 2px solid #2a2010 !important;
        gap: 0 !important;
        padding: 0 !important;
        justify-content: center;
    }
    .stTabs [data-baseweb="tab"] {
        font-family: 'Cinzel', serif !important;
        font-size: 0.82rem !important;
        letter-spacing: 0.15em !important;
        color: #6a5a3a !important;
        background: transparent !important;
        border: none !important;
        padding: 0.85rem 2.2rem !important;
        border-bottom: 3px solid transparent !important;
        transition: all 0.25s ease !important;
    }
    .stTabs [aria-selected="true"] {
        color: #c8952a !important;
        border-bottom: 3px solid #c8952a !important;
        background: rgba(200,149,42,0.06) !important;
    }
    .stTabs [data-baseweb="tab"]:hover {
        color: #e0b060 !important;
        background: rgba(200,149,42,0.04) !important;
    }
    .stTabs [data-baseweb="tab-panel"] {
        background: transparent !important;
        padding-top: 1.5rem !important;
    }

    /* ── APP PANELS ── */
    .app-panel {
        background: #0e0d0a;
        border: 1px solid #1e1a10;
        border-radius: 10px;
        padding: 1.8rem 2rem;
        max-width: 860px;
        margin: 0 auto;
    }

    /* ── ESIC STYLES ── */
    .esic-title {
        font-family: 'IBM Plex Mono', monospace !important;
        font-size: 1.4rem !important;
        color: #f5e6c0 !important;
        border-bottom: 3px solid #c0392b !important;
        padding-bottom: 0.4rem !important;
        margin-bottom: 0.6rem !important;
    }

    /* ── TDS STYLES ── */
    .tds-title {
        font-family: 'Cinzel', serif;
        font-size: 1.35rem;
        color: #f5e6c0;
        border-bottom: 2px solid #c8952a;
        padding-bottom: 0.35rem;
        margin-bottom: 0.6rem;
    }

    /* ── SHARED WIDGET STYLES ── */
    .stButton > button {
        background: linear-gradient(135deg, #8b2010, #c0392b) !important;
        color: white !important;
        border: none !important;
        border-radius: 5px !important;
        font-family: 'IBM Plex Mono', monospace !important;
        font-weight: 600 !important;
        padding: 0.5rem 1.5rem !important;
        width: 100% !important;
        transition: all 0.2s !important;
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #c0392b, #e74c3c) !important;
        box-shadow: 0 0 14px rgba(192,57,43,0.5) !important;
    }

    div[data-testid="stFileUploader"] {
        background: #13110c !important;
        border: 2px dashed #2e2410 !important;
        border-radius: 8px !important;
        padding: 0.5rem !important;
        transition: border-color 0.2s !important;
    }
    div[data-testid="stFileUploader"]:hover {
        border-color: #c8952a !important;
    }

    .stDataFrame {
        border-radius: 8px !important;
        border: 1px solid #1e1a10 !important;
    }

    /* Metric cards */
    .metric-card {
        background: #13110c;
        border: 1px solid #2a2010;
        border-radius: 8px;
        padding: 16px;
        text-align: center;
    }
    .metric-value {
        font-family: 'Cinzel', serif;
        font-size: 2rem;
        font-weight: 700;
        color: #c8952a;
    }
    .metric-label {
        font-size: 11px;
        color: #6a5a3a;
        margin-top: 4px;
        letter-spacing: 0.1em;
        text-transform: uppercase;
    }

    /* Info / success boxes */
    .stAlert {
        background: #13110c !important;
        border-color: #2a2010 !important;
        border-radius: 6px !important;
    }

    /* Footer */
    .footer {
        text-align: center;
        padding: 2.5rem 1rem 1.5rem;
        font-family: 'Cinzel', serif;
        font-size: 0.65rem;
        letter-spacing: 0.2em;
        color: #2e2818;
        text-transform: uppercase;
    }
    .footer span { color: #4a3a20; }
    </style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════
#  HERO
# ═══════════════════════════════════════════════
st.markdown("""
<div class="hero">
    <p class="hero-eyebrow">⚔ &nbsp; The House of Documents &nbsp; ⚔</p>
    <h1 class="hero-title">UK-PDF Extractors</h1>
    <div class="divider">
        <div class="divider-line"></div>
        <div class="divider-gem"></div>
        <div class="divider-line"></div>
    </div>
    <p class="hero-tagline">Extract &nbsp;·&nbsp; Transform &nbsp;·&nbsp; <span>Conquer</span></p>
</div>
""", unsafe_allow_html=True)

st.markdown('<p class="section-label">⚜ &nbsp; My Apps &nbsp; ⚜</p>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════
#  TABS
# ═══════════════════════════════════════════════
tab1, tab2 = st.tabs(["📄  ESIC Challan Extractor", "📋  TDS Challan Extractor"])


# ═══════════════════════════════════════════════
#  APP 1 — ESIC CHALLAN EXTRACTOR  (unchanged logic)
# ═══════════════════════════════════════════════
with tab1:
    st.markdown('<h2 class="esic-title">ESIC Challan Extractor</h2>', unsafe_allow_html=True)
    st.markdown("Upload one or more ESIC Challan PDFs to extract and export data to Excel.")

    ESIC_FIELDS = {
        "Employer's Code No": "Employer Code No",
        "Employer's Name": "Employer Name",
        "Challan Period": "Challan Period",
        "Challan Number": "Challan Number",
        "Challan Created Date": "Challan Created Date",
        "Challan Submitted Date": "Challan Submitted Date",
        "Amount Paid": "Amount Paid",
        "Transaction Number": "Transaction Number",
        "Transaction status": "Transaction Status",
    }

    def esic_extract_from_pdf(file_bytes):
        data = {}
        with pdfplumber.open(BytesIO(file_bytes)) as pdf:
            text = "\n".join(page.extract_text() or "" for page in pdf.pages)
        for field, col in ESIC_FIELDS.items():
            pattern = re.escape(field) + r"[\s:]*([^\n]+)"
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                data[col] = match.group(1).strip().rstrip("*").strip()
            else:
                data[col] = ""
        return data

    def esic_create_excel(records):
        wb = Workbook()
        ws = wb.active
        ws.title = "ESIC Challans"
        headers = ["Source File"] + list(ESIC_FIELDS.values())
        header_font = Font(name="Arial", bold=True, color="FFFFFF", size=11)
        header_fill = PatternFill("solid", start_color="1A1A2E")
        header_align = Alignment(horizontal="center", vertical="center", wrap_text=True)
        data_font = Font(name="Arial", size=10)
        alt_fill = PatternFill("solid", start_color="F2F2EF")
        center_align = Alignment(horizontal="center", vertical="center")
        thin = Side(style="thin", color="CCCCCC")
        border = Border(left=thin, right=thin, top=thin, bottom=thin)
        for col_idx, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col_idx, value=header)
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = header_align
            cell.border = border
        ws.row_dimensions[1].height = 30
        for row_idx, record in enumerate(records, 2):
            fill = PatternFill("solid", start_color="FFFFFF") if row_idx % 2 == 0 else alt_fill
            for col_idx, header in enumerate(headers, 1):
                val = record.get(header, "")
                cell = ws.cell(row=row_idx, column=col_idx, value=val)
                cell.font = data_font
                cell.fill = fill
                cell.alignment = center_align
                cell.border = border
            ws.row_dimensions[row_idx].height = 20
        col_widths = [30, 22, 28, 14, 22, 22, 22, 14, 22, 26]
        for i, width in enumerate(col_widths, 1):
            ws.column_dimensions[get_column_letter(i)].width = width
        total_row = len(records) + 2
        ws.cell(row=total_row, column=1, value="TOTAL")
        ws.cell(row=total_row, column=1).fill = PatternFill("solid", start_color="C0392B")
        ws.cell(row=total_row, column=1).font = Font(name="Arial", bold=True, color="FFFFFF")
        ws.cell(row=total_row, column=1).alignment = center_align
        amt_col = headers.index("Amount Paid") + 1
        total_formula = f"=SUM({get_column_letter(amt_col)}2:{get_column_letter(amt_col)}{total_row-1})"
        total_cell = ws.cell(row=total_row, column=amt_col, value=total_formula)
        total_cell.font = Font(name="Arial", bold=True, color="FFFFFF")
        total_cell.fill = PatternFill("solid", start_color="C0392B")
        total_cell.alignment = center_align
        total_cell.border = border
        ws.freeze_panes = "A2"
        output = BytesIO()
        wb.save(output)
        output.seek(0)
        return output

    esic_files = st.file_uploader(
        "Upload ESIC Challan PDFs",
        type=["pdf"],
        accept_multiple_files=True,
        help="You can upload multiple PDFs at once",
        key="esic_uploader"
    )

    if esic_files:
        st.markdown(f"**{len(esic_files)} file(s) uploaded**")
        records = []
        errors = []
        for f in esic_files:
            try:
                record = esic_extract_from_pdf(f.read())
                record["_filename"] = f.name
                records.append(record)
            except Exception as e:
                errors.append(f"{f.name}: {e}")
        if errors:
            for err in errors:
                st.error(f"⚠️ {err}")
        if records:
            display_records = [{"Source File": r["_filename"], **{k: v for k, v in r.items() if k != "_filename"}} for r in records]
            df = pd.DataFrame(display_records)
            st.markdown("### Preview")
            st.dataframe(df, use_container_width=True)
            try:
                total_amt = sum(float(r.get('Amount Paid', 0) or 0) for r in display_records)
            except Exception:
                total_amt = 0.0
            st.markdown(f"**{len(records)} record(s) extracted** | Total Amount: ₹{total_amt:,.2f}")
            if st.button("⬇ Download Excel", key="esic_btn"):
                excel_file = esic_create_excel(display_records)
                st.download_button(
                    label="📥 Click to Save Excel File",
                    data=excel_file,
                    file_name="ESIC_Challans.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key="esic_download"
                )
    else:
        st.info("Upload PDFs above to get started.")


# ═══════════════════════════════════════════════
#  APP 2 — TDS CHALLAN EXTRACTOR  (unchanged logic)
# ═══════════════════════════════════════════════
with tab2:
    st.markdown('<h2 class="tds-title">TDS Challan PDF Extractor</h2>', unsafe_allow_html=True)
    st.markdown("Upload ITNS 281 challan receipts — all data extracted into a single Excel sheet.")

    def tds_extract_value(text, label):
        patterns = [
            rf"{re.escape(label)}\s*[:\-]\s*(.+)",
            rf"{re.escape(label)}\s+(.+)",
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        return ""

    def tds_clean_amount(val):
        val = val.replace("₹", "").replace(",", "").strip()
        match = re.search(r"[\d]+(?:\.\d+)?", val)
        return float(match.group()) if match else 0.0

    def tds_extract_challan_data(pdf_file):
        with pdfplumber.open(pdf_file) as pdf:
            full_text = ""
            for page in pdf.pages:
                full_text += page.extract_text() + "\n"
        data = {}
        fields = {
            "TAN": "TAN", "Name": "Name", "Assessment Year": "Assessment Year",
            "Financial Year": "Financial Year", "Major Head": "Major Head",
            "Minor Head": "Minor Head", "Nature of Payment": "Nature of Payment",
            "CIN": "CIN", "Mode of Payment": "Mode of Payment", "Bank Name": "Bank Name",
            "Bank Reference Number": "Bank Reference Number",
            "Date of Deposit": "Date of Deposit", "BSR code": "BSR Code",
            "Challan No": "Challan No", "Tender Date": "Tender Date",
        }
        for label, key in fields.items():
            data[key] = tds_extract_value(full_text, label)
        amount_match = re.search(r"Amount \(in Rs\.\)\s*[:\-]?\s*₹?\s*([\d,]+)", full_text)
        data["Amount (Rs.)"] = tds_clean_amount(amount_match.group(1)) if amount_match else 0.0
        amount_words_match = re.search(r"Amount \(in words\)\s*[:\-]?\s*(.+)", full_text)
        data["Amount (in words)"] = amount_words_match.group(1).strip() if amount_words_match else ""
        breakup_fields = {
            "Tax": r"A\s+Tax\s+₹?\s*([\d,]+)",
            "Surcharge": r"B\s+Surcharge\s+₹?\s*([\d,]+)",
            "Cess": r"C\s+Cess\s+₹?\s*([\d,]+)",
            "Interest": r"D\s+Interest\s+₹?\s*([\d,]+)",
            "Penalty": r"E\s+Penalty\s+₹?\s*([\d,]+)",
            "Fee u/s 234E": r"F\s+Fee under section 234E\s+₹?\s*([\d,]+)",
            "Total": r"Total \(A\+B\+C\+D\+E\+F\)\s+₹?\s*([\d,]+)",
        }
        for key, pattern in breakup_fields.items():
            match = re.search(pattern, full_text)
            data[key] = tds_clean_amount(match.group(1)) if match else 0.0
        itns_match = re.search(r"ITNS No\.\s*[:\-]?\s*(\d+)", full_text)
        data["ITNS No."] = itns_match.group(1).strip() if itns_match else ""
        return data

    def tds_create_excel(records):
        wb = Workbook()
        ws = wb.active
        ws.title = "TDS Challans"
        header_fill = PatternFill("solid", start_color="1a1a2e", end_color="1a1a2e")
        header_font = Font(bold=True, color="FFFFFF", name="Arial", size=10)
        sub_fill = PatternFill("solid", start_color="E8F4FD", end_color="E8F4FD")
        sub_font = Font(bold=True, name="Arial", size=9, color="1a1a2e")
        data_font = Font(name="Arial", size=9)
        alt_fill = PatternFill("solid", start_color="F8F9FA", end_color="F8F9FA")
        center = Alignment(horizontal="center", vertical="center")
        left = Alignment(horizontal="left", vertical="center")
        thin = Side(style="thin", color="DEE2E6")
        border = Border(left=thin, right=thin, top=thin, bottom=thin)
        ws.merge_cells("A1:T1")
        ws["A1"] = "TDS CHALLAN DETAILS — KAPSTON SERVICES LIMITED"
        ws["A1"].font = Font(bold=True, name="Arial", size=12, color="FFFFFF")
        ws["A1"].fill = PatternFill("solid", start_color="1a1a2e", end_color="1a1a2e")
        ws["A1"].alignment = center
        ws.row_dimensions[1].height = 28
        main_headers = [
            "S.No", "ITNS No.", "TAN", "Name", "Assessment Year", "Financial Year",
            "Nature of Payment", "CIN", "Mode of Payment", "Bank Name",
            "Bank Ref. No.", "Date of Deposit", "BSR Code", "Challan No", "Tender Date",
            "Tax (Rs.)", "Surcharge (Rs.)", "Cess (Rs.)", "Interest (Rs.)",
            "Penalty (Rs.)", "Fee u/s 234E (Rs.)", "Total Amount (Rs.)"
        ]
        ws.merge_cells("A2:A3")
        ws.merge_cells("B2:B3")
        for col_idx, header in enumerate(main_headers, 1):
            cell = ws.cell(row=2, column=col_idx, value=header)
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = center
            cell.border = border
            ws.cell(row=3, column=col_idx).font = sub_font
            ws.cell(row=3, column=col_idx).fill = sub_fill
            ws.cell(row=3, column=col_idx).alignment = center
            ws.cell(row=3, column=col_idx).border = border
        ws.row_dimensions[2].height = 20
        ws.row_dimensions[3].height = 16
        for i, rec in enumerate(records):
            row = i + 4
            fill = alt_fill if i % 2 == 0 else PatternFill("solid", start_color="FFFFFF", end_color="FFFFFF")
            values = [
                i + 1, rec.get("ITNS No.", ""), rec.get("TAN", ""), rec.get("Name", ""),
                rec.get("Assessment Year", ""), rec.get("Financial Year", ""),
                rec.get("Nature of Payment", ""), rec.get("CIN", ""),
                rec.get("Mode of Payment", ""), rec.get("Bank Name", ""),
                rec.get("Bank Reference Number", ""), rec.get("Date of Deposit", ""),
                rec.get("BSR Code", ""), rec.get("Challan No", ""), rec.get("Tender Date", ""),
                rec.get("Tax", 0), rec.get("Surcharge", 0), rec.get("Cess", 0),
                rec.get("Interest", 0), rec.get("Penalty", 0),
                rec.get("Fee u/s 234E", 0), rec.get("Total", 0),
            ]
            for col_idx, val in enumerate(values, 1):
                cell = ws.cell(row=row, column=col_idx, value=val)
                cell.font = data_font
                cell.fill = fill
                cell.border = border
                cell.alignment = center if col_idx == 1 else left
                if col_idx >= 16:
                    cell.number_format = '₹#,##0.00'
            ws.row_dimensions[row].height = 18
        total_row = len(records) + 4
        ws.cell(row=total_row, column=1, value="TOTAL")
        ws.cell(row=total_row, column=1).fill = PatternFill("solid", start_color="1a1a2e", end_color="1a1a2e")
        ws.cell(row=total_row, column=1).font = Font(bold=True, color="FFFFFF", name="Arial", size=9)
        ws.cell(row=total_row, column=1).alignment = center
        ws.merge_cells(f"A{total_row}:O{total_row}")
        for col_idx in range(16, 23):
            col_letter = get_column_letter(col_idx)
            formula = f"=SUM({col_letter}4:{col_letter}{total_row - 1})"
            cell = ws.cell(row=total_row, column=col_idx, value=formula)
            cell.font = Font(bold=True, name="Arial", size=9, color="FFFFFF")
            cell.fill = PatternFill("solid", start_color="1a1a2e", end_color="1a1a2e")
            cell.number_format = '₹#,##0.00'
            cell.alignment = center
            cell.border = border
        ws.row_dimensions[total_row].height = 20
        col_widths = [5, 8, 14, 28, 14, 12, 18, 26, 14, 14, 18, 14, 10, 10, 12, 14, 14, 10, 10, 10, 14, 16]
        for i, width in enumerate(col_widths, 1):
            ws.column_dimensions[get_column_letter(i)].width = width
        ws.freeze_panes = "A4"
        output = BytesIO()
        wb.save(output)
        output.seek(0)
        return output

    tds_files = st.file_uploader(
        "Upload challan PDF files",
        type=["pdf"],
        accept_multiple_files=True,
        help="Upload one or more ITNS 281 TDS challan PDF files",
        key="tds_uploader"
    )

    if tds_files:
        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f'<div class="metric-card"><div class="metric-value">{len(tds_files)}</div><div class="metric-label">Files Uploaded</div></div>', unsafe_allow_html=True)
        records = []
        errors = []
        with st.spinner("Extracting data from PDFs..."):
            for f in tds_files:
                try:
                    data = tds_extract_challan_data(f)
                    data["_filename"] = f.name
                    records.append(data)
                except Exception as e:
                    errors.append((f.name, str(e)))
        if errors:
            for fname, err in errors:
                st.error(f"❌ {fname}: {err}")
        if records:
            total_amount = sum(r.get("Total", 0) for r in records)
            with col2:
                st.markdown(f'<div class="metric-card"><div class="metric-value">{len(records)}</div><div class="metric-label">Extracted Successfully</div></div>', unsafe_allow_html=True)
            with col3:
                st.markdown(f'<div class="metric-card"><div class="metric-value">₹{total_amount:,.0f}</div><div class="metric-label">Total TDS Amount</div></div>', unsafe_allow_html=True)
            st.markdown("### 📊 Extracted Data Preview")
            preview_cols = [
                "Nature of Payment", "CIN", "Challan No", "Date of Deposit",
                "BSR Code", "Tax", "Surcharge", "Cess", "Interest", "Penalty", "Fee u/s 234E", "Total"
            ]
            df = pd.DataFrame(records)
            df.insert(0, "S.No", range(1, len(df) + 1))
            df["File"] = df["_filename"]
            display_cols = ["S.No", "File"] + [c for c in preview_cols if c in df.columns]
            st.dataframe(df[display_cols], use_container_width=True, hide_index=True)
            st.markdown("### 💾 Export to Excel")
            excel_data = tds_create_excel(records)
            st.download_button(
                label="⬇️ Download Excel File",
                data=excel_data,
                file_name="TDS_Challans.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key="tds_download"
            )
    else:
        st.info("👆 Upload one or more TDS challan PDF files to get started.")
        st.markdown("**Supported format:** ITNS 281 Challan Receipts from Income Tax Department")


# ═══════════════════════════════════════════════
#  FOOTER
# ═══════════════════════════════════════════════
st.markdown("""
<div class="footer">
    ⚔ &nbsp; UK-PDF Extractors &nbsp; ⚔ &nbsp;&nbsp; <span>Bahubali never stops</span>
</div>
""", unsafe_allow_html=True)
