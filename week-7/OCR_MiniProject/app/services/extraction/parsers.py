"""Document-specific parsers for extracting structured data (Phase 8)."""

import re

from pydantic import BaseModel

from app.schemas.extraction import AadhaarData, DegreeData, PanData, PassportData, UnknownData
from app.services.extraction.base import BaseParser
from app.services.paddleocr.result import OCRResult


class AadhaarParser(BaseParser):
    """Parser for Aadhaar cards."""

    def parse(self, result: OCRResult) -> AadhaarData:
        text = result.full_text
        data = AadhaarData()

        # Aadhaar number: 4 digits, space, 4 digits, space, 4 digits
        aadhaar_match = re.search(r"\b\d{4}\s\d{4}\s\d{4}\b", text)
        if aadhaar_match:
            data.aadhaar_number = aadhaar_match.group(0)

        # DOB: Look for "DOB" or "Year of Birth" / "YOB"
        dob_match = re.search(r"(?:DOB|Year of Birth|YOB).*?([\d/]+)", text, re.IGNORECASE)
        if dob_match:
            data.dob = dob_match.group(1).strip()
        else:
            # Fallback for simple year
            dob_match = re.search(r"\b(19\d{2}|20\d{2})\b", text)
            if dob_match:
                data.dob = dob_match.group(1)

        # Gender: Male, Female, or Transgender
        gender_match = re.search(r"\b(Male|Female|Transgender)\b", text, re.IGNORECASE)
        if gender_match:
            data.gender = gender_match.group(1).capitalize()
            
        # Name: Name often appears before DOB, but OCR text ordering is tricky.
        # We will attempt a heuristic: the line above DOB, or just skip if too hard to find robustly without boxes.
        # We'll do a simple heuristic for tests.
        lines = text.split("\n")
        for i, line in enumerate(lines):
            if "DOB" in line or "Year of Birth" in line:
                if i > 0:
                    data.full_name = lines[i - 1].strip()
                    break

        return data


class PanParser(BaseParser):
    """Parser for PAN cards."""

    def parse(self, result: OCRResult) -> PanData:
        text = result.full_text
        data = PanData()

        # PAN number: 5 letters, 4 numbers, 1 letter
        pan_match = re.search(r"\b[A-Z]{5}\d{4}[A-Z]\b", text, re.IGNORECASE)
        if pan_match:
            data.pan_number = pan_match.group(0).upper()

        # DOB: DD/MM/YYYY
        dob_match = re.search(r"\b\d{2}/\d{2}/\d{4}\b", text)
        if dob_match:
            data.dob = dob_match.group(0)

        # For tests, we use simple line heuristics
        lines = text.split("\n")
        for i, line in enumerate(lines):
            # Father's name is usually below Name.
            # Real parsing requires advanced layout analysis, but for Phase 8 this satisfies the schema.
            if "Name" in line and "Father" not in line and i + 1 < len(lines):
                data.full_name = lines[i + 1].strip()
            if "Father" in line and i + 1 < len(lines):
                data.father_name = lines[i + 1].strip()

        return data


class PassportParser(BaseParser):
    """Parser for Passports."""

    def parse(self, result: OCRResult) -> PassportData:
        text = result.full_text
        data = PassportData()

        # Passport number: 1 letter followed by 7 digits
        passport_match = re.search(r"\b[A-Z]\d{7}\b", text, re.IGNORECASE)
        if passport_match:
            data.passport_number = passport_match.group(0).upper()

        lines = text.split("\n")
        for i, line in enumerate(lines):
            if "Surname" in line and i + 1 < len(lines):
                data.surname = lines[i + 1].strip()
            if "Given Name" in line and i + 1 < len(lines):
                data.given_name = lines[i + 1].strip()
            if "Date of Birth" in line and i + 1 < len(lines):
                data.dob = lines[i + 1].strip()
            if "Date of Expiry" in line and i + 1 < len(lines):
                data.expiry_date = lines[i + 1].strip()

        return data


class DegreeParser(BaseParser):
    """Parser for Degree certificates."""

    def parse(self, result: OCRResult) -> DegreeData:
        text = result.full_text
        data = DegreeData()

        lines = text.split("\n")
        # Usually University is at the top (first few lines)
        if lines:
            data.university_name = lines[0].strip()

        # Degree often contains "Bachelor", "Master", "B.Tech", etc.
        for line in lines:
            if re.search(r"\b(Bachelor|Master|B\.?Tech|M\.?Tech|B\.?Sc|M\.?Sc|Ph\.?D)\b", line, re.IGNORECASE):
                data.degree_name = line.strip()
                break

        # Year of passing
        year_match = re.search(r"\b(19|20)\d{2}\b", text)
        if year_match:
            data.year_of_passing = year_match.group(0)
            
        for i, line in enumerate(lines):
            if "certified that" in line.lower() and i + 1 < len(lines):
                data.student_name = lines[i + 1].strip()

        return data


class UnknownParser(BaseParser):
    """Fallback parser."""

    def parse(self, result: OCRResult) -> UnknownData:
        return UnknownData(raw_text=result.full_text)
