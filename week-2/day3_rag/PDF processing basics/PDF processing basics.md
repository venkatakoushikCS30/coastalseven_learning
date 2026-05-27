# PDF Processing — Quick Reference

## What & Why
PDF processing covers **text/image extraction, OCR, table parsing, splitting/merging,** and converting PDFs into AI-readable data. Used in RAG pipelines, document search, OCR systems, resume parsers, and AI assistants.

---

## PDF Types

| Type | Description | Examples |
|---|---|---|
| Text-based | Selectable text, easy to process | Reports, invoices, ebooks |
| Scanned | Image of pages, needs OCR | Handwritten notes, photographed docs |

---

## Core Pipeline

```
PDF → Load → Extract Text/Images → Clean → Chunk → Embed → Vector DB / LLM
```

For scanned PDFs, insert **OCR** between Load and Extract.

---

## Key Libraries

| Library | Best For |
|---|---|
| PyMuPDF (fitz) | Fast text, images, metadata |
| pdfplumber | Tables + structured extraction |
| pdfminer.six | Detailed text extraction |
| pytesseract | OCR (scanned PDFs) |
| camelot / tabula-py | Table extraction |

---

## Common Tasks & Challenges

- **Text Extraction** — broken formatting, missing spaces, multi-column layouts, headers/footers
- **OCR** — slower, medium accuracy; tools: Tesseract, EasyOCR, PaddleOCR
- **Table Extraction** — PDFs store positions, not structure; use camelot or pdfplumber
- **Chunking** — fixed-size, paragraph, or semantic; critical for RAG and search
- **Metadata** — author, title, page count, creation date; useful for indexing/filtering

---

## OCR vs Text Extraction

| | Text Extraction | OCR |
|---|---|---|
| Speed | Fast | Slower |
| Accuracy | High | Medium |
| Works on scanned | ✗ | ✓ |

---

## PDF in AI / RAG Workflow

```
PDF → Extract → Chunk → Embed → Vector DB → Semantic Search → LLM answers
```

---

## Learning Roadmap

1. PDF structure + text extraction
2. OCR + image extraction
3. Table extraction + text cleaning
4. **Build:** PDF semantic search → PDF chatbot (upload → extract → chunk → embed → query via Ollama)