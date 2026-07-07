# Employee Document Verification Portal

An end-to-end portal that ingests employee identity documents (Aadhaar,
PAN, Passport, Degree Certificate), extracts structured information via
OCR (PaddleOCR for printed text, TrOCR for handwritten text), verifies
the extracted data, persists everything in SQLite, and exposes both a
FastAPI and a Gradio interface.

---

## Architecture

```
            +-----------+      +----------------+
   User --> |  Gradio   | ---> |                |
            +-----------+      |    FastAPI     |
                                |     (REST)     |
            +-----------+      |                |
   User --> |  Swagger  | ---> |   app/api/*    |
            +-----------+      +-------+--------+
                                       |
                          +------------v-------------+
                          |     services/            |
                          |  preprocessing/          |
                          |  paddleocr/              |
                          |  trocr/                  |
                          |  extraction/             |
                          |  verification/           |
                          +------------+-------------+
                                       |
                          +------------v-------------+
                          |     database/ (SQLAlchemy)|
                          |     SQLite (portal.db)    |
                          +--------------------------+
```

### Pipeline

```
Upload Image
  -> Image Preprocessing (OpenCV)        <- Phase 5
       load -> resize -> grayscale -> denoise -> contrast -> deskew
       (optional) -> binarize
  -> PaddleOCR Detection (printed text + boxes + confidence)  <- Phase 6
  -> Handwritten Region Detection
  -> TrOCR Recognition (handwritten)    <- Phase 7
  -> Field Extraction (document-type parsers)                  <- Phase 8
  -> JSON
  -> Verification Engine                <- Phase 9
  -> SQLite persistence                 <- Phase 10
  -> FastAPI / Gradio response
```

---

## Tech Stack

- **Python 3.11+**
- **FastAPI** + **uvicorn** — REST API
- **Gradio** — demo UI
- **SQLite** + **SQLAlchemy** — persistence
- **Pydantic / pydantic-settings** — models and config
- **OpenCV** + **Pillow** + **NumPy** — image handling
- **PaddleOCR** — printed text OCR
- **Transformers + TrOCR + Torch** — handwritten OCR
- **python-dotenv** — env management

---

## Project Structure

```
ocr_mini/
├── app/
│   ├── api/              # FastAPI routers
│   ├── core/             # config, logging
│   ├── database/         # SQLAlchemy base + session
│   ├── models/           # ORM models
│   ├── schemas/          # Pydantic schemas
│   ├── services/         # preprocessing/, paddleocr/, trocr/, extraction/, verification/
│   ├── utils/            # helpers
│   └── main.py           # FastAPI entry
├── gradio_app/           # Gradio UI
├── tests/                # pytest suite
├── sample_documents/     # sample inputs
├── data/                 # runtime: uploads, sqlite db
├── logs/                 # rotating app.log
├── requirements.txt
├── .env.example
└── README.md
```

---

## Installation

```bash
# 1. Clone and enter
cd ocr_mini

# 2. Create virtual environment
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux / macOS
# source .venv/bin/activate

# 3. Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# 4. Configure
copy .env.example .env       # Windows
# cp .env.example .env       # Linux/macOS
```

> PaddlePaddle wheels are platform-specific. If `pip install` fails on
> PaddlePaddle, follow the official install matrix for your
> OS/CUDA/Python version.

---

## How to Run

### FastAPI (Swagger UI)

```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

- OpenAPI docs: <http://127.0.0.1:8000/docs>
- Health check: <http://127.0.0.1:8000/health>

### Gradio (added in Phase 4)

```bash
# 1. Make sure the FastAPI backend is running on http://127.0.0.1:8000
uvicorn app.main:app --reload

# 2. In a second terminal, launch the Gradio UI
python -m gradio_app.app
```

Then open <http://127.0.0.1:7860>. The UI shows a live backend health
check, a file picker, a document-type dropdown, an optional employee-id
field, a preview, and a JSON panel that mirrors the FastAPI response.

The Gradio backend URL is configurable via `GRADIO_API_URL` in `.env`
(defaults to `http://127.0.0.1:8000`).

---

## API Endpoints (current)

| Method | Path                                  | Description                                              |
|--------|---------------------------------------|----------------------------------------------------------|
| GET    | `/health`                             | Liveness / readiness                                     |
| POST   | `/api/v1/employees`                   | Create an employee                                       |
| GET    | `/api/v1/employees`                   | List employees (paginated)                               |
| GET    | `/api/v1/employees/{id}`              | Get an employee by id                                    |
| PATCH  | `/api/v1/employees/{id}`              | Update an employee                                       |
| DELETE | `/api/v1/employees/{id}`              | Delete an employee (cascades to their documents)         |
| POST   | `/api/v1/documents/upload`            | Upload a document image (multipart)                      |
| GET    | `/api/v1/documents`                   | List documents (paginated, filterable)                   |
| GET    | `/api/v1/documents/{id}`              | Get a single document                                    |
| DELETE | `/api/v1/documents/{id}`              | Delete a document row                                    |

### Upload request

```bash
# 1. (Optional) Create an employee
curl -X POST http://127.0.0.1:8000/api/v1/employees \
  -H "Content-Type: application/json" \
  -d '{"full_name":"Jane Doe","email":"jane@example.com","department":"Eng"}'

# 2. Upload bound to that employee
curl -X POST http://127.0.0.1:8000/api/v1/documents/upload \
  -F "file=@aadhaar.png" \
  -F "document_type=aadhaar" \
  -F "employee_id=<UUID-from-step-1>"
```

Allowed `document_type` values: `aadhaar`, `pan`, `passport`, `degree`,
`unknown`. Allowed file extensions: `.jpg`, `.jpeg`, `.png`, `.webp`,
`.bmp`, `.tiff`. The file is also magic-byte checked.

If `employee_id` is omitted, the upload is bound to a singleton
`Unassigned` bucket so foreign keys stay valid.

### Error response shape

```json
{ "error": { "code": "invalid_image", "message": "..." } }
```

### Database

Phase 3 creates two tables on startup (`employees`, `documents`).

- **employees**: `id` (UUID, PK), `full_name`, `email` (unique, nullable),
  `employee_code` (unique, nullable), `department`, `created_at`, `updated_at`.
- **documents**: `id` (UUID, PK), `employee_id` (FK, nullable),
  `document_type` (enum), `status` (enum: `received|processing|verified|failed`),
  `original_filename`, `content_type`, `size_bytes`, `sha256` (indexed),
  `stored_path`, `ocr_json` (nullable, used in Phase 10),
  `verification_json` (nullable, used in Phase 10),
  `error_message` (nullable), `created_at`, `updated_at`.

Cascades: deleting an employee sets their documents' `employee_id` to
NULL (the documents themselves are preserved, on purpose, for audit).
Deleting a document removes the row only; the on-disk file is left in
place for now (atomic unlink lands in a later phase).

---

## Completed

- [x] **Phase 1** — Project initialization, config, logging, DB session, minimal FastAPI app
- [x] **Phase 2** — FastAPI foundation: `/health`, upload, list endpoints, Pydantic schemas, file validation, error envelope, tests
- [x] **Phase 3** — SQLite models (`Employee`, `Document`), repository layer, employees CRUD, DB-backed documents API, full test suite (44 tests)
- [x] **Phase 4** — Gradio UI: upload form, image preview, calls FastAPI, shows JSON response (57 tests)
- [x] **Phase 5** — OpenCV preprocessing pipeline (load → resize → grayscale → denoise → contrast → deskew, optional binarize), 76 tests
- [x] **Phase 6** — PaddleOCR integration
- [x] **Phase 9** — Verification engine
- [x] **Phase 10** — Full DB persistence of OCR + verification
- [x] **Phase 11** — Advanced API: search, history, pagination

- [x] **Phase 11** — Advanced API: search, history, pagination
- [x] **Phase 12** — Polish, bugfixes, UI finishing touches, final docs

## Pending (Roadmap)
- None. Project is complete!

---

## Screenshots

> Placeholder. UI screenshots will be added in Phase 4 (Gradio) and
> Phase 12 (polish).

---

## Known Limitations

- **No migrations yet** — schema is created via `Base.metadata.create_all` on
  startup. Alembic is on the roadmap.
- Deleting a document removes the DB row only; the on-disk file is not
  unlinked.
- PaddlePaddle installation may need a manual wheel on some platforms.
- TrOCR requires PyTorch; CPU inference will be slow for large images.
- SQLite is suitable for single-instance dev; swap to PostgreSQL via
  `DATABASE_URL` for production.
- Headless Jupyter notebooks are executed natively in the same Python process for performance (ZMQ and `nbclient` were removed).

---

## Configuration

All settings live in `.env` (see `.env.example` for the full list):

| Key                          | Default                            | Purpose                              |
|------------------------------|------------------------------------|--------------------------------------|
| `APP_ENV`                    | `development`                      | runtime environment                  |
| `DATABASE_URL`               | `sqlite:///./data/portal.db`       | SQLAlchemy URL                       |
| `LOG_LEVEL`                  | `INFO`                             | root log level                       |
| `LOG_FILE`                   | `./logs/app.log`                   | rotating log file                    |
| `UPLOAD_DIR`                 | `./data/uploads`                   | where uploaded files are stored      |
| `MAX_UPLOAD_MB`              | `10`                               | max upload size in MiB               |
| `OCR_CONFIDENCE_THRESHOLD`   | `0.6`                              | min OCR score to trust a token       |
| `VERIFICATION_MIN_CONFIDENCE`| `0.6`                              | min field confidence to pass         |
| `TROCR_MODEL`                | `microsoft/trocr-base-handwritten` | TrOCR model id                       |
| `GRADIO_API_URL`             | `http://127.0.0.1:8000`            | FastAPI URL the Gradio UI calls      |
| `GRADIO_HOST` / `GRADIO_PORT`| `127.0.0.1` / `7860`               | Gradio server bind                   |
| `GRADIO_SHARE`               | `false`                            | `true` creates a public Gradio link  |
| `PREPROCESS_MAX_DIM`         | `1600`                             | Resize cap on the longest side (px)  |
| `PREPROCESS_DESKEW`          | `true`                             | Run the deskew step                   |
| `PREPROCESS_BINARIZE`        | `false`                            | Run adaptive threshold binarization   |
