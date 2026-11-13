import os
import fitz  # PyMuPDF for PDFs
from docx import Document  # python-docx for Word files

def parse_document(file_path: str) -> list[dict]:
    """
    Parses various document types (PDF, DOCX, TXT, images) page-by-page or section-by-section,
    returning a list of dictionaries containing page numbers and extracted text chunks.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    ext = os.path.splitext(file_path)[1].lower()
    parsed_pages = []

    # 1. Parse PDF files page-by-page using PyMuPDF (fitz)
    if ext == ".pdf":
        doc = fitz.open(file_path)
        for page_num, page in enumerate(doc, start=1):
            text = page.get_text()
            if text.strip():
                parsed_pages.append({
                    "page": page_num,
                    "text": text.strip()
                })
        doc.close()

    # 2. Parse Microsoft Word files (.docx)
    elif ext == ".docx":
        doc = Document(file_path)
        full_text = "\n".join([para.text for para in doc.paragraphs if para.text.strip()])
        parsed_pages.append({
            "page": 1,
            "text": full_text
        })

    # 3. Parse Plain Text files (.txt)
    elif ext == ".txt":
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        parsed_pages.append({
            "page": 1,
            "text": content.strip()
        })

    # 4. Handle Image files (.png, .jpg, .jpeg) for OCR / Multimodal Notes
    elif ext in [".png", ".jpg", ".jpeg"]:
        # For images, we pass a descriptive placeholder or let Gemini handle the image directly
        parsed_pages.append({
            "page": 1,
            "text": f"[Uploaded Image File: {os.path.basename(file_path)}]"
        })

    else:
        raise ValueError(f"Unsupported file extension: {ext}")

    return parsed_pages