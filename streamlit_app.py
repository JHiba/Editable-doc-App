import io
import re
import streamlit as st
from PIL import Image
from docx import Document
from docx.shared import Inches

import os

try:
    import pytesseract
    PYTESSERACT_AVAILABLE = True
except ImportError:
    PYTESSERACT_AVAILABLE = False

from PIL import ImageEnhance

st.set_page_config(page_title="Notes to Editable DOCX", page_icon="📄", layout="centered")

def is_cloud_environment():
    """Detect if running on Streamlit Cloud or if Tesseract is unavailable"""
    # Check for Streamlit Cloud environment variables
    is_cloud = (
        os.getenv("STREAMLIT_SHARING_MODE") is not None or
        os.getenv("STREAMLIT_RUNTIME_ENV") == "cloud"
    )
    return is_cloud or not PYTESSERACT_AVAILABLE

# Note: Tesseract OCR is only available for local use
# Download from: https://github.com/UB-Mannheim/tesseract/wiki
# Or use: winget install UB-Mannheim.TesseractOCR

def tesseract_extract(pil_img: Image.Image) -> str:
    """Extract text from image using Tesseract OCR"""
    # Skip OCR if in cloud environment
    if is_cloud_environment():
        return ""
    
    if pil_img.mode != "RGB":
        pil_img = pil_img.convert("RGB")
    
    # Enhance image for better OCR results
    # Increase contrast
    enhancer = ImageEnhance.Contrast(pil_img)
    pil_img = enhancer.enhance(1.5)
    
    # Increase sharpness
    enhancer = ImageEnhance.Sharpness(pil_img)
    pil_img = enhancer.enhance(1.5)
    
    try:
        # Run OCR with custom config for better handwriting recognition
        custom_config = r'--oem 3 --psm 6'
        text = pytesseract.image_to_string(pil_img, config=custom_config)
        return text.strip()
    except Exception as e:
        return ""

def clean_text(text: str) -> str:
    # light cleanup, keeps it honest but less ugly
    text = text.replace("\x0c", " ").strip()
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text

def add_image_to_doc(doc: Document, pil_img: Image.Image, width_in=6.2):
    # docx needs a file-like object
    img_bytes = io.BytesIO()
    pil_img.save(img_bytes, format="PNG")
    img_bytes.seek(0)
    doc.add_picture(img_bytes, width=Inches(width_in))

def build_docx(images, include_image=True, include_text=True):
    doc = Document()
    doc.add_heading("Handwritten Notes (Converted)", level=1)

    for idx, pil_img in enumerate(images, start=1):
        doc.add_heading(f"Page {idx}", level=2)

        # Preserve diagrams/layout by embedding the original image
        if include_image:
            add_image_to_doc(doc, pil_img)
            doc.add_paragraph("")  # spacing

        # Editable OCR text
        if include_text:
            raw = tesseract_extract(pil_img)
            text = clean_text(raw)

            doc.add_heading("Editable Text (OCR)", level=3)
            if text:
                for line in text.split("\n"):
                    doc.add_paragraph(line)
            else:
                doc.add_paragraph("[No text detected]")

        if idx != len(images):
            doc.add_page_break()

    out = io.BytesIO()
    doc.save(out)
    out.seek(0)
    return out

# ---------- UI ----------
st.title("📄 Handwritten Notes → Editable DOCX")

# Check if running in cloud environment
on_cloud = is_cloud_environment()

if on_cloud:
    st.info("ℹ️ **Running in cloud mode** - OCR is disabled (Tesseract not available). You can still download images embedded in DOCX format.")
else:
    st.write("Upload your note images, keeps diagrams by embedding the original page image, and adds editable OCR text underneath.")

uploaded = st.file_uploader(
    "Upload one or more images",
    type=["png", "jpg", "jpeg", "webp"],
    accept_multiple_files=True
)

col1, col2 = st.columns(2)
with col1:
    include_image = st.checkbox("Include original page image (preserves diagrams)", value=True)
with col2:
    include_text = st.checkbox(
        "Include editable OCR text" + (" (local only)" if on_cloud else ""),
        value=not on_cloud,
        disabled=on_cloud,
        help="OCR requires Tesseract which is only available locally" if on_cloud else "Extract text from images using OCR"
    )

if uploaded:
    images = []
    st.subheader("Preview")
    for f in uploaded:
        img = Image.open(f)
        images.append(img)
        st.image(img, caption=f.name, width=700)

    st.divider()

    if st.button("Generate DOCX", type="primary"):
        if not include_image and not include_text:
            st.error("Select at least one option: image and/or editable text.")
        else:
            with st.spinner("Converting..."):
                docx_bytes = build_docx(images, include_image=include_image, include_text=include_text)

            st.success("Done.")
            st.download_button(
                label="⬇ Download DOCX",
                data=docx_bytes,
                file_name="handwritten_notes_converted.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
else:
    st.info("Upload images to start.")
