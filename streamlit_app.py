import io
import os
import json
import base64
import streamlit as st
from PIL import Image
import mammoth  # NEW: Added for live preview

from docx import Document
from docx.shared import Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH

from groq import Groq

# -------------------------
# Page Config & Constants
# -------------------------
st.set_page_config(page_title="Image to Formatted DOCX ", page_icon="📄", layout="centered")

# -------------------------
# Groq + Vision helpers
# -------------------------
def get_groq_client() -> Groq:
    api_key = os.getenv("GROQ_API_KEY") or st.secrets.get("GROQ_API_KEY", None)
    if not api_key:
        raise RuntimeError("Missing GROQ_API_KEY. Set it in environment variables or Streamlit secrets.")
    return Groq(api_key=api_key)

def pil_to_data_url(pil_img: Image.Image) -> str:
    if pil_img.mode != "RGB":
        pil_img = pil_img.convert("RGB")
    buf = io.BytesIO()
    pil_img.save(buf, format="JPEG", quality=90)
    b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
    return f"data:image/jpeg;base64,{b64}"

SYSTEM_PROMPT = """
You are a document conversion engine.
Your job: extract text AND basic formatting from a single-page English document image.

Return ONLY valid JSON (no markdown, no commentary).
Be accurate and conservative: if you are unsure about bold/italic, mark them false.

Formatting to detect:
- paragraphs (separate blocks of text)
- alignment for each paragraph: left, center, right, justify
- bold and italic within text runs

Rules:
- Preserve the reading order top-to-bottom, left-to-right.
- Keep paragraph breaks.
- Headings are words or sentences with a '#' symbol.
- Mark all headings as BOLD in the JSON.
- Keep line breaks inside a paragraph only when they are real (like bullet lists). Otherwise keep as normal sentences.
- If the page contains a title, make it the first paragraph, typically center aligned and bold if it looks like a heading.
"""

USER_PROMPT = """
Extract the document into this JSON shape:
{
  "paragraphs": [
    {
      "alignment": "left|center|right|justify",
      "runs": [
        {"text": "string", "bold": true|false, "italic": true|false}
      ]
    }
  ]
}
"""

def groq_extract_layout(pil_img: Image.Image, model_id: str) -> dict:
    client = get_groq_client()
    data_url = pil_to_data_url(pil_img)

    for attempt in range(2):
        temperature = 0.2 if attempt == 0 else 0.0
        completion = client.chat.completions.create(
            model=model_id,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT.strip()},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": USER_PROMPT.strip()},
                        {"type": "image_url", "image_url": {"url": data_url}},
                    ],
                },
            ],
            response_format={"type": "json_object"},
            temperature=temperature,
            max_completion_tokens=2048,
        )

        content = completion.choices[0].message.content
        try:
            obj = json.loads(content)
            if "paragraphs" not in obj or not isinstance(obj["paragraphs"], list):
                raise ValueError("Bad JSON shape")
            return obj
        except Exception:
            if attempt == 1:
                raise RuntimeError("Groq returned invalid JSON.")
    return {"paragraphs": []}

# -------------------------
# DOCX building
# -------------------------
def add_image_to_doc(doc: Document, pil_img: Image.Image, width_in=6.2):
    buf = io.BytesIO()
    pil_img.save(buf, format="PNG")
    buf.seek(0)
    doc.add_picture(buf, width=Inches(width_in))

def alignment_to_docx(alignment: str):
    a = (alignment or "").lower().strip()
    if a == "center": return WD_ALIGN_PARAGRAPH.CENTER
    if a == "right": return WD_ALIGN_PARAGRAPH.RIGHT
    if a == "justify": return WD_ALIGN_PARAGRAPH.JUSTIFY
    return WD_ALIGN_PARAGRAPH.LEFT

def build_docx_from_layout(layout: dict, include_page_image: bool, pil_img: Image.Image, page_idx: int, doc: Document):
    doc.add_heading(f"Page {page_idx}", level=2)
    if include_page_image:
        add_image_to_doc(doc, pil_img)
        doc.add_paragraph("")

    for p in layout.get("paragraphs", []):
        runs = p.get("runs", [])
        text_join = "".join([r.get("text", "") for r in runs]).strip()
        if not text_join: continue

        para = doc.add_paragraph()
        para.alignment = alignment_to_docx(p.get("alignment", "left"))
        for r in runs:
            t = r.get("text", "")
            if not t: continue
            run = para.add_run(t)
            run.bold = bool(r.get("bold", False))
            run.italic = bool(r.get("italic", False))

def build_docx(images, model_id: str, include_page_image: bool):
    doc = Document()
    doc.add_heading("Image to Formatted DOCX ", level=1)
    for idx, pil_img in enumerate(images, start=1):
        layout = groq_extract_layout(pil_img, model_id=model_id)
        build_docx_from_layout(layout, include_page_image, pil_img, idx, doc)
        if idx != len(images): doc.add_page_break()
    
    out = io.BytesIO()
    doc.save(out)
    out.seek(0)
    return out

# -------------------------
# UI Logic
# -------------------------
st.title("📄 Image → Formatted DOCX ")
st.write("Extracts text and formatting from images with a live screen preview.")

model_id = st.selectbox(
    "Groq Vision Model",
    ["meta-llama/llama-4-scout-17b-16e-instruct", "meta-llama/llama-4-maverick-17b-128e-instruct"]
)

include_page_image = st.checkbox("Include original page image", value=True)

uploaded = st.file_uploader("Upload images", type=["png", "jpg", "jpeg", "webp"], accept_multiple_files=True)

if uploaded:
    images = [Image.open(f) for f in uploaded]
    st.divider()

    if st.button("Generate DOCX", type="primary"):
        try:
            with st.spinner("Analyzing layout + generating DOCX..."):
                docx_io = build_docx(images, model_id, include_page_image)
            
            # --- PREVIEW LOGIC ---
            st.subheader("📝 Live Output Preview")
            docx_io.seek(0)
            result = mammoth.convert_to_html(docx_io)
            html_content = result.value
            
            # Displaying the Word content in a scrollable container
            st.markdown(
                f'<div style="background-color: white; color: black; padding: 20px; border-radius: 5px; border: 1px solid #ddd; max-height: 400px; overflow-y: auto;">{html_content}</div>', 
                unsafe_allow_html=True
            )
            
            st.success("Analysis complete.")
            st.download_button(
                "⬇ Download DOCX",
                data=docx_io.getvalue(),
                file_name="formatted_output.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )
        except Exception as e:
            st.error(str(e))
else:
    st.info("Upload images to start.")