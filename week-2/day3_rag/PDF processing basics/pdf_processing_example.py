import fitz          # PyMuPDF — fast text + metadata
import pdfplumber    # table extraction

PDF_PATH = " " # path of the PDF

# ── 1. Metadata ────────────────────────────────────────────────────────────────
def get_metadata(path: str) -> dict:
    doc = fitz.open(path)
    meta = doc.metadata
    return {
        "title":      meta.get("title", "N/A"),
        "author":     meta.get("author", "N/A"),
        "pages":      doc.page_count,
        "created":    meta.get("creationDate", "N/A"),
    }

# ── 2. Text extraction ─────────────────────────────────────────────────────────
def extract_text(path: str) -> list[str]:
    doc = fitz.open(path)
    return [page.get_text("text").strip() for page in doc]

# ── 3. Clean text ──────────────────────────────────────────────────────────────
def clean(text: str) -> str:
    import re
    text = re.sub(r'\n{3,}', '\n\n', text)   # collapse blank lines
    text = re.sub(r'[ \t]+', ' ', text)       # collapse spaces
    text = re.sub(r'\bPage \d+\b', '', text)  # strip page numbers
    return text.strip()

# ── 4. Chunking ────────────────────────────────────────────────────────────────
def chunk(text: str, size: int = 500, overlap: int = 50) -> list[str]:
    chunks, start = [], 0
    while start < len(text):
        chunks.append(text[start:start + size])
        start += size - overlap
    return chunks

# ── 5. Table extraction ────────────────────────────────────────────────────────
def extract_tables(path: str, page_num: int = 0) -> list:
    with pdfplumber.open(path) as pdf:
        page = pdf.pages[page_num]
        return page.extract_tables()   # list of 2-D lists

# ── 6. Images ──────────────────────────────────────────────────────────────────
def extract_images(path: str, out_dir: str = ".") -> list[str]:
    import os
    doc, saved = fitz.open(path), []
    for page in doc:
        for img in page.get_images():
            xref = img[0]
            pix  = fitz.Pixmap(doc, xref)
            name = os.path.join(out_dir, f"img_{xref}.png")
            pix.save(name)
            saved.append(name)
    return saved

# ── Demo ───────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("── Metadata ──")
    print(get_metadata(PDF_PATH))

    print("\n── Page 1 text (cleaned) ──")
    pages = extract_text(PDF_PATH)
    cleaned = clean(pages[0])
    print(cleaned[:300], "...")

    print("\n── Chunks (page 1) ──")
    for i, c in enumerate(chunk(cleaned, size=200), 1):
        print(f"[{i}] {c[:80]}...")

    print("\n── Tables (page 1) ──")
    for t in extract_tables(PDF_PATH):
        for row in t:
            print(row)

    print("\n── Saved images ──")
    print(extract_images(PDF_PATH, out_dir="./images"))