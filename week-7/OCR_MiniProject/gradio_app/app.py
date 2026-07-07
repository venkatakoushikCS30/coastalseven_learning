"""Gradio UI for the Employee Document Verification Portal.

The UI is a thin client to the FastAPI backend: it never imports the
backend's SQLAlchemy models. Configure the backend URL via the
``GRADIO_API_URL`` environment variable (see ``.env.example``).

Run with:

    python -m gradio_app.app

…or directly:

    python gradio_app/app.py
"""

from __future__ import annotations

import json
from collections.abc import Callable
from typing import Any

import gradio as gr

from app.core.config import settings
from app.core.logging import configure_logging, get_logger
from gradio_app.client import APIClient, APIError

logger = get_logger(__name__)

# Document-type choices shown in the dropdown.
DOC_TYPE_CHOICES: list[tuple[str, str]] = [
    ("Aadhaar", "aadhaar"),
    ("PAN", "pan"),
    ("Passport", "passport"),
    ("Degree Certificate", "degree"),
    ("Unknown", "unknown"),
]

# Max upload size the Gradio component allows (matches FastAPI default).
MAX_UPLOAD_BYTES = 10 * 1024 * 1024  # 10 MiB


def _client_factory() -> APIClient:
    """Build an :class:`APIClient` from the current settings."""
    return APIClient(base_url=settings.gradio_api_url)


def _check_backend(client: APIClient) -> str:
    """Return a short health status string for the UI header."""
    try:
        body = client.health()
        return f"Backend OK — v{body.get('version', '?')} ({body.get('env', '?')})"
    except APIError as exc:
        logger.warning("backend health check failed: %s", exc)
        return f"Backend unreachable: {exc}"


def _format_response(payload: dict[str, Any] | str) -> str:
    """Pretty-print a JSON payload for the response panel."""
    if isinstance(payload, str):
        return payload
    try:
        return json.dumps(payload, indent=2, sort_keys=True, default=str)
    except (TypeError, ValueError):
        return str(payload)


def _handle_upload(
    file_path: str | None,
    document_type: str,
    employee_id: str | None,
    client_factory: Callable[[], APIClient] = _client_factory,
) -> tuple[str, str, str]:
    """Submit an upload to the FastAPI backend.

    Returns ``(status, response_json, preview_label)`` for the Gradio
    components. ``preview_label`` is currently informational; the image
    itself is rendered by the Gradio ``Image`` component.
    """
    if not file_path:
        yield "No file selected.", "", ""
        return

    document_type = (document_type or "unknown").strip().lower() or "unknown"
    employee_id_clean = (employee_id or "").strip() or None

    try:
        with open(file_path, "rb") as fh:
            contents = fh.read()
    except OSError as exc:
        yield f"Failed to read uploaded file: {exc}", "", ""
        return

    if len(contents) > MAX_UPLOAD_BYTES:
        yield (
            f"File is too large ({len(contents) // (1024 * 1024)} MiB > "
            f"{MAX_UPLOAD_BYTES // (1024 * 1024)} MiB).",
            "",
            "",
        )
        return

    filename = file_path.rsplit("/", 1)[-1] or "upload.bin"

    client = client_factory()
    try:
        upload = client.upload_document(
            filename=filename,
            content=contents,
            content_type=_guess_content_type(filename),
            document_type=document_type,
            employee_id=employee_id_clean,
        )
    except APIError as exc:
        logger.info("upload failed: %s", exc)
        yield (
            f"Upload failed: {exc}",
            _format_response({"error": {"code": exc.code, "message": str(exc)}}),
            "",
        )
        return

    document_id = upload.get("document_id")
    if not document_id:
        yield (
            "Upload succeeded, but no ID returned.",
            _format_response(upload),
            "",
        )
        return
    
    yield (
        f"Uploaded {document_id}... Processing...",
        _format_response(upload),
        f"document_id={document_id}",
    )
    
    try:
        detail = client.process_document(document_id)
        if detail.get("ocr_result") and "boxes" in detail["ocr_result"]:
            del detail["ocr_result"]["boxes"]
    except APIError as exc:
        logger.info("processing failed: %s", exc)
        yield (
            f"Processing failed: {exc}",
            _format_response({"error": {"code": exc.code, "message": str(exc)}}),
            f"document_id={document_id}",
        )
        return

    yield (
        f"Processed {document_id}",
        _format_response(detail),
        f"document_id={document_id}",
    )


def _handle_search_employees(
    search: str,
    client_factory: Callable[[], APIClient] = _client_factory,
) -> str:
    client = client_factory()
    try:
        results = client.list_employees(search=search if search.strip() else None)
        return _format_response(results)
    except APIError as exc:
        return f"Error: {exc}"


def _handle_search_documents(
    search: str,
    client_factory: Callable[[], APIClient] = _client_factory,
) -> str:
    client = client_factory()
    try:
        results = client.list_documents(search=search if search.strip() else None)
        return _format_response(results)
    except APIError as exc:
        return f"Error: {exc}"


def _guess_content_type(filename: str) -> str:
    """Best-effort content-type guess from a filename (no mimetypes module)."""
    lower = filename.lower()
    if lower.endswith((".jpg", ".jpeg")):
        return "image/jpeg"
    if lower.endswith(".png"):
        return "image/png"
    if lower.endswith(".webp"):
        return "image/webp"
    if lower.endswith(".bmp"):
        return "image/bmp"
    if lower.endswith((".tif", ".tiff")):
        return "image/tiff"
    return "application/octet-stream"


def build_interface(client_factory: Callable[[], APIClient] = _client_factory) -> gr.Blocks:
    """Construct (but do not launch) the Gradio Blocks interface."""
    with gr.Blocks(title=settings.app_name) as demo:
        gr.Markdown(
            f"# {settings.app_name}\n"
            f"Upload an employee identity document. The UI calls the FastAPI "
            f"backend at `{settings.gradio_api_url}` — make sure it is running."
        )

        backend_status = gr.Markdown(
            value=_check_backend(client_factory()),
            elem_id="backend-status",
        )

        with gr.Tabs():
            with gr.Tab("Upload & Process"):
                with gr.Row():
                    with gr.Column(scale=1):
                        file_input = gr.File(
                            label="Document image",
                            file_types=["image"],
                            type="filepath",
                        )
                        doc_type = gr.Dropdown(
                            label="Document type",
                            choices=DOC_TYPE_CHOICES,
                            value="aadhaar",
                        )
                        employee_id = gr.Textbox(
                            label="Employee ID (optional UUID)",
                            placeholder="leave blank to bind to 'Unassigned'",
                        )
                        upload_btn = gr.Button("Upload & extract", variant="primary")

                    with gr.Column(scale=2):
                        preview = gr.Image(
                            label="Preview",
                            interactive=False,
                            height=320,
                        )
                        status_box = gr.Markdown(value="Awaiting upload…", elem_id="upload-status")
                        doc_id_box = gr.Markdown(value="")
                        response_json = gr.Code(
                            label="Backend response (JSON)",
                            language="json",
                            interactive=False,
                        )

                # When a file is dropped in, refresh the preview image.
                file_input.change(
                    fn=lambda p: p,
                    inputs=[file_input],
                    outputs=[preview],
                )

                # Wire the upload button. ``inputs`` order matches the handler signature.
                upload_btn.click(
                    fn=_handle_upload,
                    inputs=[file_input, doc_type, employee_id],
                    outputs=[status_box, response_json, doc_id_box],
                )

            with gr.Tab("Search Employees"):
                emp_search = gr.Textbox(label="Search Query (Name, Email, or Code)")
                emp_btn = gr.Button("Search")
                emp_results = gr.Code(label="Results", language="json", interactive=False)
                
                emp_btn.click(
                    fn=_handle_search_employees,
                    inputs=[emp_search],
                    outputs=[emp_results],
                )

            with gr.Tab("Search Documents"):
                doc_search = gr.Textbox(label="Search Query (Filename)")
                doc_btn = gr.Button("Search")
                doc_results = gr.Code(label="Results", language="json", interactive=False)
                
                doc_btn.click(
                    fn=_handle_search_documents,
                    inputs=[doc_search],
                    outputs=[doc_results],
                )

        # Re-check the backend on load.
        demo.load(
            fn=lambda: _check_backend(client_factory()),
            outputs=[backend_status],
        )

    return demo


def main() -> None:  # pragma: no cover - manual launch path
    """Entry point for ``python -m gradio_app.app``."""
    configure_logging()
    logger.info(
        "starting gradio api_url=%s host=%s port=%d",
        settings.gradio_api_url,
        settings.gradio_host,
        settings.gradio_port,
    )
    demo = build_interface()
    demo.launch(
        server_name=settings.gradio_host,
        server_port=settings.gradio_port,
        share=settings.gradio_share,
        show_error=True,
        theme=gr.themes.Soft(),
    )


if __name__ == "__main__":  # pragma: no cover
    main()
