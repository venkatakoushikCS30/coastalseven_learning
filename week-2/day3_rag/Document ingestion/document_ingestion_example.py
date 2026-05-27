import os
import json
import re
import pandas as pd
from bs4 import BeautifulSoup
from pypdf import PdfReader
from docx import Document
from PIL import Image
import pytesseract


class UniversalDocumentIngestor:

    def __init__(self, chunk_size=500):
        self.chunk_size = chunk_size

    # =========================
    # MAIN INGEST FUNCTION
    # =========================
    def ingest(self, file_path):

        extension = os.path.splitext(file_path)[1].lower()

        handlers = {
            ".txt": self.read_txt,
            ".pdf": self.read_pdf,
            ".docx": self.read_docx,
            ".csv": self.read_csv,
            ".xlsx": self.read_excel,
            ".json": self.read_json,
            ".html": self.read_html,
            ".htm": self.read_html,
            ".png": self.read_image,
            ".jpg": self.read_image,
            ".jpeg": self.read_image
        }

        if extension not in handlers:
            raise ValueError(f"Unsupported file type: {extension}")

        raw_text = handlers[extension](file_path)

        cleaned_text = self.clean_text(raw_text)

        chunks = self.chunk_text(cleaned_text)

        return {
            "file_name": os.path.basename(file_path),
            "file_type": extension,
            "content": cleaned_text,
            "chunks": chunks
        }

    # =========================
    # TXT
    # =========================
    def read_txt(self, file_path):
        with open(file_path, "r", encoding="utf-8") as file:
            return file.read()

    # =========================
    # PDF
    # =========================
    def read_pdf(self, file_path):
        reader = PdfReader(file_path)

        text = ""

        for page in reader.pages:
            extracted = page.extract_text()

            if extracted:
                text += extracted + "\n"

        return text

    # =========================
    # DOCX
    # =========================
    def read_docx(self, file_path):
        doc = Document(file_path)

        text = ""

        for para in doc.paragraphs:
            text += para.text + "\n"

        return text

    # =========================
    # CSV
    # =========================
    def read_csv(self, file_path):
        df = pd.read_csv(file_path)

        return df.to_string(index=False)

    # =========================
    # EXCEL
    # =========================
    def read_excel(self, file_path):
        df = pd.read_excel(file_path)

        return df.to_string(index=False)

    # =========================
    # JSON
    # =========================
    def read_json(self, file_path):
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)

        return json.dumps(data, indent=2)

    # =========================
    # HTML
    # =========================
    def read_html(self, file_path):
        with open(file_path, "r", encoding="utf-8") as file:
            html = file.read()

        soup = BeautifulSoup(html, "html.parser")

        return soup.get_text()

    # =========================
    # IMAGE OCR
    # =========================
    def read_image(self, file_path):
        image = Image.open(file_path)

        text = pytesseract.image_to_string(image)

        return text

    # =========================
    # CLEAN TEXT
    # =========================
    def clean_text(self, text):

        text = re.sub(r"\s+", " ", text)

        text = text.strip()

        return text

    # =========================
    # CHUNKING
    # =========================
    def chunk_text(self, text):

        chunks = []

        for i in range(0, len(text), self.chunk_size):
            chunks.append(text[i:i + self.chunk_size])

        return chunks


# ==========================================
# USAGE
# ==========================================

if __name__ == "__main__":

    ingestor = UniversalDocumentIngestor(chunk_size=300)

    file_path = " "   # Put your file path here

    result = ingestor.ingest(file_path)

    print("\n========== FILE INFO ==========")
    print("Name :", result["file_name"])
    print("Type :", result["file_type"])

    print("\n========== CLEANED CONTENT ==========")
    print(result["content"][:1000])

    print("\n========== CHUNKS ==========")
    print(f"Total Chunks: {len(result['chunks'])}")

    for index, chunk in enumerate(result["chunks"][:3]):
        print(f"\nChunk {index + 1}:")
        print(chunk)