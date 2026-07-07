# OpenCode project memory — Employee Document Verification Portal

## Current Phase
- **Phase 12 — Polish, bugfixes, UI finishing touches** (DONE)
- Next: **None. Project Complete!**

## Architecture
- FastAPI (REST) + Gradio (UI) + SQLite/SQLAlchemy + PaddleOCR + TrOCR.
- Layered: `api` -> `services/*` -> `database/repository` -> SQLAlchemy.
- Preprocessing is a step-based pipeline (`Pipeline` orchestrator) with
  composable, stateless steps. Default order:
  `load -> resize -> grayscale -> denoise -> contrast -> deskew -> binarize(opt)`.
- Gradio UI is a separate process that calls FastAPI over HTTP via
  `gradio_app.client.APIClient` (stdlib `urllib`).
- DELETE routes use `response_model=None` + `response_class=Response`.

## Implemented APIs
- `GET    /health`
- `POST   /api/v1/employees`, `GET /api/v1/employees`, `GET /api/v1/employees/{id}`,
  `PATCH /api/v1/employees/{id}`, `DELETE /api/v1/employees/{id}`
- `POST   /api/v1/documents/upload`, `GET /api/v1/documents`,
  `GET /api/v1/documents/{id}`, `DELETE /api/v1/documents/{id}`

## Gradio UI
- Launch: `python -m gradio_app.app` (binds `GRADIO_HOST:GRADIO_PORT`).
- File picker, document-type dropdown, optional employee-id, image preview,
  JSON response panel, backend health banner.

## Database Tables
- `employees`, `documents`. `Base.metadata.create_all` on startup. Alembic planned.

## OCR Status
- PaddleOCR integration completed (Phase 6). `PaddleOCRService` added.
- TrOCR integration completed (Phase 7). `TrOCRService` added.

## Verification Status
- Phase 9 complete. `verify_document` uses `SequenceMatcher` to compare Employee full name with parsed document name.
- Phase 10 complete. Final pipeline successfully saves parsed fields and verification states to JSON blobs in DB.

## Folder Structure
```
app/
  api/ router.py, health.py, employees.py, documents.py
  core/ config.py, logging.py, errors.py
  database/ db.py, repository.py
  models/ enums.py, employee.py, document.py
  schemas/ common.py, document.py, employee.py
  services/
    documents.py
    preprocessing/
      __init__.py, context.py, steps.py, pipeline.py
    paddleocr/    (Phase 6)
    trocr/        (Phase 7)
    extraction/   (Phase 8)
    verification/ (Phase 9)
  utils/ files.py, validators.py
  main.py
gradio_app/
  client.py, app.py
tests/
  conftest.py
  test_health.py, test_validators.py, test_upload.py (P2)
  test_models.py, test_documents_api.py, test_employees_api.py (P3)
  test_gradio_client.py, test_gradio_app.py (P4)
  test_preprocessing.py (P5)
```

## Completed Features
- Phase 1: project skeleton, config, logging, DB session.
- Phase 2: typed upload + list endpoints, validators, error envelope.
- Phase 3: ORM models, repository, employees CRUD, DB-backed documents API.
- Phase 4: Gradio UI talking to FastAPI over HTTP.
- Phase 5: OpenCV preprocessing pipeline (load/resize/grayscale/denoise/contrast/deskew/binarize),
  76 passing tests.
- Phase 6: PaddleOCR integration (`PaddleOCRService` running headless Jupyter notebooks).
- Phase 7: TrOCR integration (`TrOCRService` running headless Jupyter notebooks).
- Phase 8: Document-type parsers (Aadhaar, PAN, Passport, Degree).
- Phase 9: Verification engine (Fuzzy string matching name logic).
- Phase 10: Persist OCR + verification JSON via full processing pipeline.

## Pending Features
- Phase 11: Advanced API.
- Phase 12: Polish.

## Important Decisions
- Preprocessing accepts path / bytes / ndarray; Pipeline is composable.
- `binarize` is opt-in (helps printed forms, hurts photos).
- `deskew` heuristic uses `cv2.minAreaRect` on the inverted/OTSU-thresholded image.
- `minAreaRect` angle ambiguity handled by `min(|a|, |a-90|)`.

## Configuration Variables
- APP_ENV, APP_NAME, APP_VERSION,
- DATABASE_URL, LOG_LEVEL, LOG_FILE,
- UPLOAD_DIR, MAX_UPLOAD_MB,
- OCR_CONFIDENCE_THRESHOLD, TROCR_MODEL,
- VERIFICATION_MIN_CONFIDENCE,
- GRADIO_API_URL, GRADIO_HOST, GRADIO_PORT, GRADIO_SHARE,
- PREPROCESS_MAX_DIM, PREPROCESS_DESKEW, PREPROCESS_BINARIZE.

## Recent Changes
- Phase 5: added `app/services/preprocessing/{context,steps,pipeline}.py`,
  re-exports in `__init__.py`; added `PREPROCESS_*` settings + `.env.example`;
  added `tests/test_preprocessing.py` (synthetic-image unit tests).
- Fixed `load_image` to wrap `OSError` in `ValueError` for a clean contract.
- Fixed skew-estimator test to handle the 90-degree ambiguity of `minAreaRect`.
- Fixed `NotebookRunner` to execute notebook cells natively via `exec()` instead of using `nbclient`, resolving an `AttributeError` and removing Jupyter ZeroMQ overhead.
- Installed `paddleocr` and `paddlepaddle` dependencies to correctly boot the PaddleOCR engine.

## Known Issues / TODOs
- PaddlePaddle / Torch install size — handled via platform wheels.
- Delete-document does not unlink the file from disk.
- No Alembic migrations; schema changes require dropping the DB.
- PaddleOCR model download is slow on first run (mitigated by PaddleOCR's cache).
- Deskew uses OTSU+minAreaRect — accurate for printed text, may struggle on
  purely handwritten or photographic inputs (acceptable for Phase 5).
