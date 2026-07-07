"""
PDF Toolkit — Streamlit App
============================
Features:
1. Unlock PDF (remove password protection)
2. Convert PDF -> Word (.docx)
3. Convert Word (.docx) -> PDF

Run with:
    streamlit run app.py
"""

import io
import os
import shutil
import subprocess
import tempfile

import streamlit as st
from pypdf import PdfReader, PdfWriter

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(page_title="PDF Toolkit", page_icon="📄", layout="centered")

st.title("📄 PDF Toolkit")
st.caption("Unlock PDFs, and convert between PDF and Word — all in one place.")

tab_unlock, tab_pdf2word, tab_word2pdf = st.tabs(
    ["🔓 Unlock PDF", "📄 ➜ 📝 PDF to Word", "📝 ➜ 📄 Word to PDF"]
)

# ---------------------------------------------------------------------------
# Helper: check if LibreOffice (soffice) is available for Word -> PDF
# ---------------------------------------------------------------------------
def get_soffice_path():
    for name in ("soffice", "libreoffice"):
        path = shutil.which(name)
        if path:
            return path
    return None


# ---------------------------------------------------------------------------
# TAB 1 — Unlock PDF
# ---------------------------------------------------------------------------
with tab_unlock:
    st.subheader("Remove password protection from one or more PDFs")
    st.write(
        "Upload one or more password-protected PDFs. A password field will "
        "appear for **each file, labeled with that file's name**, so you can "
        "enter the correct password for the right PDF."
    )

    unlock_files = st.file_uploader(
        "Upload PDF(s)",
        type=["pdf"],
        key="unlock_uploader",
        accept_multiple_files=True,
    )

    # One password field per uploaded file, clearly labeled with the file name
    passwords = {}
    if unlock_files:
        st.markdown("**Enter the password for each file:**")
        for idx, f in enumerate(unlock_files):
            passwords[idx] = st.text_input(
                f"🔑 Password for \"{f.name}\"",
                type="password",
                key=f"unlock_password_{idx}_{f.name}",
            )

    if st.button("Unlock PDF(s)", key="unlock_btn"):
        if not unlock_files:
            st.error("Please upload at least one PDF file first.")
        else:
            results = []  # (filename, bytes) for successfully unlocked files
            any_errors = False

            for idx, f in enumerate(unlock_files):
                pwd = passwords.get(idx, "")
                try:
                    reader = PdfReader(f)

                    if reader.is_encrypted:
                        result = reader.decrypt(pwd)
                        if result == 0:
                            st.error(
                                f"❌ \"{f.name}\": incorrect password, or the PDF "
                                "could not be decrypted."
                            )
                            any_errors = True
                            continue
                    else:
                        st.info(
                            f"ℹ️ \"{f.name}\" doesn't appear to be password-protected — "
                            "creating a clean copy anyway."
                        )

                    writer = PdfWriter()
                    for page in reader.pages:
                        writer.add_page(page)

                    out_buffer = io.BytesIO()
                    writer.write(out_buffer)
                    out_buffer.seek(0)

                    results.append((f.name, out_buffer.getvalue()))
                    st.success(f"✅ \"{f.name}\" unlocked successfully!")

                except Exception as e:
                    st.error(f"❌ \"{f.name}\": could not unlock PDF — {e}")
                    any_errors = True

            # Individual download buttons for each unlocked file
            for name, data in results:
                st.download_button(
                    label=f"⬇️ Download unlocked \"{name}\"",
                    data=data,
                    file_name=f"unlocked_{name}",
                    mime="application/pdf",
                    key=f"download_{name}",
                )

            # If more than one file succeeded, also offer a single ZIP download
            if len(results) > 1:
                import zipfile

                zip_buffer = io.BytesIO()
                with zipfile.ZipFile(zip_buffer, "w") as zf:
                    for name, data in results:
                        zf.writestr(f"unlocked_{name}", data)
                zip_buffer.seek(0)

                st.download_button(
                    label="⬇️ Download all unlocked PDFs as ZIP",
                    data=zip_buffer,
                    file_name="unlocked_pdfs.zip",
                    mime="application/zip",
                    key="download_zip",
                )

# ---------------------------------------------------------------------------
# TAB 2 — PDF to Word
# ---------------------------------------------------------------------------
with tab_pdf2word:
    st.subheader("Convert PDF to an editable Word document")
    st.write(
        "Upload a PDF and get back a .docx file with the extracted text, "
        "tables, and layout preserved as closely as possible."
    )

    pdf2word_file = st.file_uploader(
        "Upload PDF", type=["pdf"], key="pdf2word_uploader"
    )

    if st.button("Convert to Word", key="pdf2word_btn"):
        if not pdf2word_file:
            st.error("Please upload a PDF file first.")
        else:
            try:
                from pdf2docx import Converter

                with tempfile.TemporaryDirectory() as tmpdir:
                    input_path = os.path.join(tmpdir, "input.pdf")
                    output_path = os.path.join(tmpdir, "output.docx")

                    with open(input_path, "wb") as f:
                        f.write(pdf2word_file.getbuffer())

                    with st.spinner("Converting PDF to Word... this may take a moment"):
                        cv = Converter(input_path)
                        cv.convert(output_path)
                        cv.close()

                    with open(output_path, "rb") as f:
                        docx_bytes = f.read()

                st.success("Conversion complete!")
                base_name = os.path.splitext(pdf2word_file.name)[0]
                st.download_button(
                    label="⬇️ Download Word document",
                    data=docx_bytes,
                    file_name=f"{base_name}.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                )
            except Exception as e:
                st.error(f"Could not convert PDF to Word: {e}")

# ---------------------------------------------------------------------------
# TAB 3 — Word to PDF
# ---------------------------------------------------------------------------
with tab_word2pdf:
    st.subheader("Convert a Word document to PDF")
    st.write("Upload a .docx file and get back a PDF version of it.")

    word2pdf_file = st.file_uploader(
        "Upload Word document", type=["docx"], key="word2pdf_uploader"
    )

    if st.button("Convert to PDF", key="word2pdf_btn"):
        if not word2pdf_file:
            st.error("Please upload a .docx file first.")
        else:
            soffice_path = get_soffice_path()
            if not soffice_path:
                st.error(
                    "LibreOffice (soffice) was not found on this system. "
                    "Word-to-PDF conversion requires LibreOffice to be installed.\n\n"
                    "Install it with:\n"
                    "- **Ubuntu/Debian**: `sudo apt-get install libreoffice`\n"
                    "- **Mac**: `brew install --cask libreoffice`\n"
                    "- **Windows**: download from https://www.libreoffice.org/"
                )
            else:
                try:
                    with tempfile.TemporaryDirectory() as tmpdir:
                        input_path = os.path.join(tmpdir, "input.docx")
                        with open(input_path, "wb") as f:
                            f.write(word2pdf_file.getbuffer())

                        with st.spinner("Converting Word document to PDF..."):
                            subprocess.run(
                                [
                                    soffice_path,
                                    "--headless",
                                    "--convert-to",
                                    "pdf",
                                    "--outdir",
                                    tmpdir,
                                    input_path,
                                ],
                                check=True,
                                capture_output=True,
                                timeout=120,
                            )

                        output_path = os.path.join(tmpdir, "input.pdf")
                        with open(output_path, "rb") as f:
                            pdf_bytes = f.read()

                    st.success("Conversion complete!")
                    base_name = os.path.splitext(word2pdf_file.name)[0]
                    st.download_button(
                        label="⬇️ Download PDF",
                        data=pdf_bytes,
                        file_name=f"{base_name}.pdf",
                        mime="application/pdf",
                    )
                except subprocess.CalledProcessError as e:
                    st.error(f"LibreOffice conversion failed: {e.stderr.decode(errors='ignore')}")
                except Exception as e:
                    st.error(f"Could not convert Word to PDF: {e}")

st.divider()
st.caption(
    "🔒 Files are processed in memory/temporary storage only and are not saved "
    "anywhere by this app."
)
