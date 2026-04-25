import streamlit as st
import pdfplumber
import pandas as pd
import re
from io import BytesIO
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

st.set_page_config(
    page_title="uk",
    page_icon="⬡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ═══════════════════════════════════════════════
#  THEME DEFINITIONS
# ═══════════════════════════════════════════════
THEMES = {
    "Obsidian": {
        "bg":          "#0f0f0f",
        "surface":     "#1a1a1a",
        "surface2":    "#242424",
        "border":      "#2e2e2e",
        "accent":      "#e8e8e8",
        "accent2":     "#a0a0a0",
        "highlight":   "#ffffff",
        "btn_bg":      "#ffffff",
        "btn_text":    "#0f0f0f",
        "btn_hover":   "#d0d0d0",
        "metric_val":  "#ffffff",
        "metric_lbl":  "#888888",
        "tab_active":  "#ffffff",
        "sub":         "#888888",
        "info_bg":     "#1e1e1e",
        "info_border": "#2e2e2e",
    },
    "Arctic": {
        "bg":          "#f0f4f8",
        "surface":     "#ffffff",
        "surface2":    "#e8eef4",
        "border":      "#c8d8e8",
        "accent":      "#1a3a5c",
        "accent2":     "#3a6a9c",
        "highlight":   "#0a2040",
        "btn_bg":      "#1a3a5c",
        "btn_text":    "#ffffff",
        "btn_hover":   "#0a2040",
        "metric_val":  "#1a3a5c",
        "metric_lbl":  "#6a8aac",
        "tab_active":  "#1a3a5c",
        "sub":         "#6a8aac",
        "info_bg":     "#e8f0f8",
        "info_border": "#c8d8e8",
    },
    "Forest": {
        "bg":          "#f2f5f0",
        "surface":     "#ffffff",
        "surface2":    "#e8ede4",
        "border":      "#c4d4b8",
        "accent":      "#2d5a27",
        "accent2":     "#5a8a52",
        "highlight":   "#1a3a14",
        "btn_bg":      "#2d5a27",
        "btn_text":    "#ffffff",
        "btn_hover":   "#1a3a14",
        "metric_val":  "#2d5a27",
        "metric_lbl":  "#7aaa72",
        "tab_active":  "#2d5a27",
        "sub":         "#7aaa72",
        "info_bg":     "#eaf2e6",
        "info_border": "#c4d4b8",
    },
    "Ember": {
        "bg":          "#1a0a00",
        "surface":     "#261200",
        "surface2":    "#321800",
        "border":      "#4a2800",
        "accent":      "#ff8c3a",
        "accent2":     "#cc6010",
        "highlight":   "#ffb870",
        "btn_bg":      "#ff8c3a",
        "btn_text":    "#1a0a00",
        "btn_hover":   "#ffb060",
        "metric_val":  "#ff8c3a",
        "metric_lbl":  "#cc6010",
        "tab_active":  "#ff8c3a",
        "sub":         "#cc7030",
        "info_bg":     "#261200",
        "info_border": "#4a2800",
    },
    "Violet": {
        "bg":          "#0e0818",
        "surface":     "#180d28",
        "surface2":    "#221238",
        "border":      "#3a1e5a",
        "accent":      "#b87aff",
        "accent2":     "#8840dd",
        "highlight":   "#d0aaff",
        "btn_bg":      "#b87aff",
        "btn_text":    "#0e0818",
        "btn_hover":   "#d0aaff",
        "metric_val":  "#b87aff",
        "metric_lbl":  "#8840dd",
        "tab_active":  "#b87aff",
        "sub":         "#8840dd",
        "info_bg":     "#180d28",
        "info_border": "#3a1e5a",
    },
    "Clay": {
        "bg":          "#f7f3ee",
        "surface":     "#ffffff",
        "surface2":    "#ede8e0",
        "border":      "#d8cec0",
        "accent":      "#8b5a3c",
        "accent2":     "#c48060",
        "highlight":   "#5c3020",
        "btn_bg":      "#8b5a3c",
        "btn_text":    "#ffffff",
        "btn_hover":   "#5c3020",
        "metric_val":  "#8b5a3c",
        "metric_lbl":  "#c48060",
        "tab_active":  "#8b5a3c",
        "sub":         "#c48060",
        "info_bg":     "#f0e8de",
        "info_border": "#d8cec0",
    },
}

THEME_ICONS = {
    "Obsidian": "⬛",
    "Arctic":   "🔷",
    "Forest":   "🟢",
    "Ember":    "🔶",
    "Violet":   "🟣",
    "Clay":     "🟤",
}

if "theme_name" not in st.session_state:
    st.session_state.theme_name = "Obsidian"

T = THEMES[st.session_state.theme_name]

# ═══════════════════════════════════════════════
#  INJECT CSS
# ═══════════════════════════════════════════════
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@300;400;500&family=Sora:wght@300;400;600;700&display=swap');

*, *::before, *::after {{ box-sizing: border-box; }}

html, body, [class*="css"] {{
    font-family: 'Sora', sans-serif !important;
    background: {T["bg"]} !important;
    color: {T["accent"]} !important;
}}
.stApp {{ background: {T["bg"]} !important; min-height: 100vh; }}
.main .block-container {{ padding: 0 !important; max-width: 100% !important; }}

/* ── TOPBAR ── */
.topbar {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0.85rem 2.5rem;
    background: {T["surface"]};
    border-bottom: 1.5px solid {T["border"]};
}}
.logo {{
    font-family: 'Lucida Sans Unicode', 'Lucida Grande', 'Lucida Sans', sans-serif;
    font-size: 1.7rem;
    font-weight: 700;
    color: {T["highlight"]} !important;
    letter-spacing: -0.04em;
    line-height: 1;
}}
.topbar-meta {{
    font-family: 'DM Mono', monospace;
    font-size: 0.68rem;
    color: {T["sub"]};
    letter-spacing: 0.1em;
}}

/* ── HERO ── */
.hero {{
    padding: 3rem 2.5rem 1.5rem;
    background: {T["bg"]};
}}
.hero-name {{
    font-family: 'Lucida Sans Unicode', 'Lucida Grande', 'Lucida Sans', sans-serif;
    font-size: clamp(3rem, 8vw, 6rem);
    font-weight: 700;
    color: {T["highlight"]} !important;
    letter-spacing: -0.05em;
    line-height: 0.95;
    margin: 0 0 0.5rem;
}}
.hero-sub {{
    font-family: 'DM Mono', monospace;
    font-size: 0.73rem;
    color: {T["sub"]};
    letter-spacing: 0.18em;
    text-transform: uppercase;
}}

/* ── THEME PICKER ── */
.theme-wrap {{
    padding: 1.4rem 2.5rem 0;
    background: {T["bg"]};
}}
.theme-label {{
    font-family: 'DM Mono', monospace;
    font-size: 0.62rem;
    letter-spacing: 0.28em;
    text-transform: uppercase;
    color: {T["sub"]};
    margin-bottom: 0.55rem;
}}
.divider-line {{
    height: 1px;
    background: {T["border"]};
    margin: 1.4rem 2.5rem 0;
}}
.section-label {{
    font-family: 'DM Mono', monospace;
    font-size: 0.6rem;
    letter-spacing: 0.3em;
    text-transform: uppercase;
    color: {T["sub"]};
    padding: 1rem 2.5rem 0.6rem;
}}

/* ── TABS ── */
.stTabs [data-baseweb="tab-list"] {{
    background: {T["surface"]} !important;
    border-bottom: 1.5px solid {T["border"]} !important;
    gap: 0 !important;
    padding: 0 2rem !important;
}}
.stTabs [data-baseweb="tab"] {{
    font-family: 'DM Mono', monospace !important;
    font-size: 0.72rem !important;
    letter-spacing: 0.14em !important;
    text-transform: uppercase !important;
    color: {T["sub"]} !important;
    background: transparent !important;
    border: none !important;
    padding: 0.9rem 1.6rem !important;
    border-bottom: 2px solid transparent !important;
    margin-bottom: -1.5px !important;
    transition: color 0.18s !important;
}}
.stTabs [aria-selected="true"] {{
    color: {T["tab_active"]} !important;
    border-bottom: 2px solid {T["tab_active"]} !important;
}}
.stTabs [data-baseweb="tab-panel"] {{
    background: {T["bg"]} !important;
    padding: 2rem 2.5rem !important;
}}

/* ── APP HEADER ── */
.app-h {{
    font-family: 'Lucida Sans Unicode', 'Lucida Grande', 'Lucida Sans', sans-serif;
    font-size: 1.2rem;
    font-weight: 700;
    color: {T["highlight"]} !important;
    letter-spacing: -0.02em;
    margin-bottom: 0.18rem;
}}
.app-desc {{
    font-family: 'DM Mono', monospace;
    font-size: 0.74rem;
    color: {T["sub"]};
    margin-bottom: 1.4rem;
}}

/* ── FILE UPLOADER ── */
div[data-testid="stFileUploader"] {{
    background: {T["surface"]} !important;
    border: 1.5px dashed {T["border"]} !important;
    border-radius: 8px !important;
    padding: 0.4rem !important;
}}
div[data-testid="stFileUploader"]:hover {{ border-color: {T["accent"]} !important; }}
div[data-testid="stFileUploader"] label,
div[data-testid="stFileUploader"] p,
div[data-testid="stFileUploader"] span {{ color: {T["accent"]} !important; }}

/* ── BUTTONS ── */
.stButton > button {{
    background: {T["btn_bg"]} !important;
    color: {T["btn_text"]} !important;
    border: none !important;
    border-radius: 5px !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 0.75rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.08em !important;
    padding: 0.55rem 1.4rem !important;
    width: 100% !important;
    transition: background 0.18s !important;
}}
.stButton > button:hover {{ background: {T["btn_hover"]} !important; }}

.stDownloadButton > button {{
    background: {T["surface2"]} !important;
    color: {T["accent"]} !important;
    border: 1.5px solid {T["border"]} !important;
    border-radius: 5px !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 0.75rem !important;
    transition: border-color 0.18s !important;
}}
.stDownloadButton > button:hover {{
    border-color: {T["accent"]} !important;
    color: {T["highlight"]} !important;
}}

/* ── METRIC CARD ── */
.metric-card {{
    background: {T["surface"]};
    border: 1.5px solid {T["border"]};
    border-radius: 10px;
    padding: 1.1rem 1rem;
    text-align: center;
}}
.metric-value {{
    font-family: 'Lucida Sans Unicode', 'Lucida Grande', 'Lucida Sans', sans-serif;
    font-size: 1.85rem;
    font-weight: 700;
    color: {T["metric_val"]} !important;
    letter-spacing: -0.03em;
}}
.metric-label {{
    font-family: 'DM Mono', monospace;
    font-size: 0.62rem;
    color: {T["metric_lbl"]};
    letter-spacing: 0.16em;
    text-transform: uppercase;
    margin-top: 0.25rem;
}}

/* ── DATAFRAME ── */
.stDataFrame {{ border: 1.5px solid {T["border"]} !important; border-radius: 8px !important; }}

/* ── ALERTS ── */
.stAlert {{
    background: {T["info_bg"]} !important;
    border: 1px solid {T["info_border"]} !important;
    border-radius: 6px !important;
}}
.stAlert p {{ color: {T["accent"]} !important; }}

/* ── GENERIC TEXT ── */
p, li, span, label {{ color: {T["accent"]}; }}
h1, h2, h3, h4, h5 {{ color: {T["highlight"]} !important; }}
hr {{ border-color: {T["border"]}; }}
.stSpinner > div {{ border-top-color: {T["accent"]} !important; }}

/* ── FOOTER ── */
.footer {{
    text-align: center;
    padding: 2rem 1rem 1.2rem;
    font-family: 'DM Mono', monospace;
    font-size: 0.6rem;
    letter-spacing: 0.24em;
    text-transform: uppercase;
    color: {T["sub"]};
    border-top: 1px solid {T["border"]};
    margin-top: 3rem;
}}
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════
#  TOPBAR
# ═══════════════════════════════════════════════
st.markdown(f"""
<div class="topbar">
    <div class="logo">uk</div>
    <div class="topbar-meta">PDF Extraction Suite &nbsp;/&nbsp; {st.session_state.theme_name}</div>
</div>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════
#  HERO
# ═══════════════════════════════════════════════
st.markdown(f"""
<div class="hero">
    <div class="hero-name">uk</div>
    <div class="hero-sub">PDF Extraction Suite &nbsp;·&nbsp; ESIC &nbsp;·&nbsp; TDS</div>
</div>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════
#  THEME PICKER
# ═══════════════════════════════════════════════
st.markdown('<div class="theme-wrap"><div class="theme-label">🎨 &nbsp; Personalize — choose a theme</div></div>', unsafe_allow_html=True)

cols = st.columns(len(THEMES))
for i, (tname, ticon) in enumerate(THEME_ICONS.items()):
    with cols[i]:
        active = st.session_state.theme_name == tname
        label = f"✓ {ticon} {tname}" if active else f"{ticon} {tname}"
        if st.button(label, key=f"theme_{tname}"):
            st.session_state.theme_name = tname
            st.rerun()

st.markdown('<div class="divider-line"></div>', unsafe_allow_html=True)
st.markdown('<div class="section-label">⬡ &nbsp; My Apps</div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════
#  TABS
# ═══════════════════════════════════════════════
tab1, tab2 = st.tabs(["  ESIC Challan Extractor  ", "  TDS Challan Extractor  "])


# ══════════════════════════════════════
#  APP 1 — ESIC  (logic unchanged)
# ══════════════════════════════════════
with tab1:
    st.markdown('<div class="app-h">ESIC Challan Extractor</div>', unsafe_allow_html=True)
    st.markdown('<div class="app-desc">Upload one or more ESIC Challan PDFs to extract and export data to Excel.</div>', unsafe_allow_html=True)

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
            data[col] = match.group(1).strip().rstrip("*").strip() if match else ""
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
                total_amt = sum(float(r.get("Amount Paid", 0) or 0) for r in display_records)
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


# ══════════════════════════════════════
#  APP 2 — TDS  (logic unchanged)
# ══════════════════════════════════════
with tab2:
    st.markdown('<div class="app-h">TDS Challan PDF Extractor</div>', unsafe_allow_html=True)
    st.markdown('<div class="app-desc">Upload ITNS 281 challan receipts — all data extracted into a single Excel sheet.</div>', unsafe_allow_html=True)

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
st.markdown(f"""
<div class="footer">
    uk &nbsp;·&nbsp; PDF Extraction Suite &nbsp;·&nbsp; {st.session_state.theme_name}
</div>
""", unsafe_allow_html=True)
