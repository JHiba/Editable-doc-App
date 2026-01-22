#  Written Notes to Editable DOCX Converter

A Streamlit web application that converts handwritten notes (images) into editable Word documents using Tesseract OCR.

##  Features

-  **Upload multiple images** - PNG, JPG, JPEG, WebP supported
-  **Preserve original layout** - Embeds original images to keep diagrams intact
-  **Extract editable text** - Uses Tesseract OCR for handwriting recognition
-  **Generate DOCX files** - Download ready-to-edit Word documents
-  **Image enhancement** - Automatic contrast and sharpness improvements for better OCR

##  Quick Start

### Prerequisites

1. **Python 3.8+** installed
2. **Tesseract OCR** installed:
   ```bash
   winget install UB-Mannheim.TesseractOCR
   ```
   Or download from: https://github.com/UB-Mannheim/tesseract/wiki

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/JHiba/Editable-doc-App.git
   cd Editable-doc-App
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the app:
   ```bash
   streamlit run streamlit_app.py
   ```

4. Open your browser at `http://localhost:8501`

## How to Use

1. **Upload Images** - Click "Browse files" or drag-and-drop your handwritten note images
2. **Configure Options**:
   - ✅ Include original page image (preserves diagrams)
   - ✅ Include editable OCR text
3. **Generate DOCX** - Click the button and wait for processing
4. **Download** - Save your converted document

## 🛠️ Technologies Used

- **Streamlit** - Web interface
- **Tesseract OCR** - Text extraction engine
- **python-docx** - DOCX file generation
- **Pillow** - Image processing and enhancement

## 📋 Requirements

```
streamlit>=1.32.2
python-docx>=1.1.0
pillow>=11.0.0
pytesseract
pdf2image
```

##  Troubleshooting

### "Tesseract OCR not installed" error
- Install Tesseract: `winget install UB-Mannheim.TesseractOCR`
- Restart the app

### Low OCR accuracy
- Use high-resolution images (300+ DPI)
- Ensure good lighting and contrast
- Write clearly and legibly

##  License

MIT License - feel free to use and modify!

## 👤 Author

**JHiba and Reha**

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!

---

⭐ Star this repo if you find it helpful!