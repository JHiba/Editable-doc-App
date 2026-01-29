#  Editable-doc-App: =Image to Formatted DOCX

A professional document conversion application. This tool extracts text from images (handwritten or printed) while preserving basic formatting such as bold, italics, and paragraph alignment. 

The app utilizes a hybrid approach: **Large Language Model (LLM) Vision** for high-accuracy OCR and **Mammoth** for real-time document previewing.

##  Features
- **Intelligent OCR**: Uses Groq's Llama-4-Vision to extract text from dense handwritten notes (e.g., Chemistry notes on Surface Chemistry and Colloids).
- **Formatting Preservation**: Automatically detects and applies **Bold**, *Italic*, and Text Alignment (Center/Left/Right) to the final output.
- **Live Preview**: Integrated Mammoth engine to provide a formatted HTML preview of the document before downloading.
- **Red Ink Detection**: Specifically tuned to bold text written in red ink, often used for headings and important formulas in educational notes.
- **Multi-Page Support**: Processes multiple images and generates a single cohesive `.docx` file with page breaks.
- **Diagram Support**: Optional inclusion of original images to preserve complex hand-drawn diagrams (e.g., Adsorption Isotherms or Electric Disintegration apparatus).

## 🛠️ Tech Stack
- **Frontend**: [Streamlit](https://streamlit.io/)
- **OCR/Vision Engine**: [Groq Cloud API](https://groq.com/) (Llama-3-Vision)
- **Document Generation**: [python-docx](https://python-docx.readthedocs.io/)
- **Preview Engine**: [Mammoth](https://github.com/mwillow/mammoth.js)

## 📋 Installation & Setup

1. **Clone the repository**:
   ```bash
   git clone [https://github.com/JHiba/Editable-doc-App.git](https://github.com/JHiba/Editable-doc-App.git)
   cd Editable-doc-App
