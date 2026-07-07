"""End-to-end processing pipeline orchestrator (Phase 10)."""

import json

from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.database import repository as repo
from app.models.enums import DocumentStatus
from app.services.extraction.dispatcher import get_parser
from app.services.paddleocr.service import PaddleOCRService
from app.services.preprocessing.pipeline import preprocess
from app.services.verification.engine import verify_document


logger = get_logger(__name__)

# Reusing a single OCR service instance across pipeline calls is much faster,
# especially since the notebook engine has startup overhead.
# In a real async production app, this would be managed by a dependency or lifespan.
_ocr_service = None

def _get_ocr_service() -> PaddleOCRService:
    global _ocr_service
    if _ocr_service is None:
        _ocr_service = PaddleOCRService()
    return _ocr_service


def process_document(db: Session, document_id: str) -> bool:
    """Run preprocessing, OCR, parsing, and verification on a document.
    
    The results are serialized to JSON and saved on the Document record.
    Status is updated to VERIFIED or FAILED.
    """
    doc = repo.get_document(db, document_id)
    if not doc:
        logger.error("process_document: Document %s not found", document_id)
        return False
        
    if doc.status == DocumentStatus.PROCESSING:
        logger.warning("process_document: Document %s is already processing", document_id)
        return False

    doc.status = DocumentStatus.PROCESSING
    db.commit()

    try:
        # 1. Load image and preprocess
        # doc.stored_path points to the uploaded image file.
        pre_result = preprocess(doc.stored_path)
        
        # 2. Run OCR (PaddleOCR)
        ocr_service = _get_ocr_service()
        ocr_result = ocr_service.recognize(pre_result)
        doc.ocr_json = json.dumps(ocr_result.to_dict())
        
        # 3. Parse fields
        parser = get_parser(doc.document_type)
        parsed_data = parser.parse(ocr_result)
        
        # 4. Verify against Employee record
        verification_data = None
        if not doc.employee:
            # Auto-create employee from parsed name if available
            name = None
            if hasattr(parsed_data, "full_name") and parsed_data.full_name:
                name = parsed_data.full_name
            elif hasattr(parsed_data, "given_name") and parsed_data.given_name:
                name = f"{parsed_data.given_name} {getattr(parsed_data, 'surname', '') or ''}".strip()
            elif hasattr(parsed_data, "student_name") and parsed_data.student_name:
                name = parsed_data.student_name
            
            if name:
                import uuid
                new_emp_id = str(uuid.uuid4())
                new_employee = repo.create_employee(
                    db,
                    employee_id=new_emp_id,
                    full_name=name,
                    email=None,
                    employee_code=None,
                    department=None,
                )
                db.commit()
                # Reload document to ensure relationship is tracked
                doc = repo.get_document(db, document_id)
                doc.employee_id = new_emp_id
                doc.employee = new_employee
                logger.info("Auto-created employee %s for unassigned document %s", new_emp_id, document_id)

        if doc.document_type.value == "unknown":
            doc.verification_json = json.dumps({"parsed_fields": parsed_data.model_dump()})
            doc.status = DocumentStatus.VERIFIED
            logger.info("Skipped strict verification for UNKNOWN document %s", document_id)
        elif doc.employee:
            verification_result = verify_document(doc.employee, parsed_data)
            verification_data = {
                "parsed_fields": parsed_data.model_dump(),
                "verification": verification_result.model_dump(),
            }
            doc.verification_json = json.dumps(verification_data)
            doc.status = DocumentStatus.VERIFIED if verification_result.is_verified else DocumentStatus.FAILED
        else:
            # If there's still no bound employee (e.g. unknown doc type or no name found)
            doc.verification_json = json.dumps({"parsed_fields": parsed_data.model_dump()})
            # Wait for employee assignment to fully verify, but extraction succeeded.
            doc.status = DocumentStatus.VERIFIED
            
        doc.error_message = None

    except Exception as exc:
        logger.exception("Pipeline failed for document %s: %s", document_id, exc)
        doc.status = DocumentStatus.FAILED
        doc.error_message = str(exc)
        
    finally:
        db.commit()

    return doc.status == DocumentStatus.VERIFIED
