# ── ./ExtractDocxText/__init__.py ──────────────────────────────────────────────
import base64
import io
from typing import List

import azure.functions as func
from docx import Document     

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)


def _docx_bytes_to_text(doc_bytes: bytes) -> str:
    doc = Document(io.BytesIO(doc_bytes))
    paragraphs: List[str] = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
    return "\n".join(paragraphs)


@app.function_name(name="convert_docx_to_text")
@app.route(    route="convert_docx_to_text")
def convert_docx_to_text(req: func.HttpRequest) ->func.HttpResponse:

        body = req.get_json()
        file_b64 = body.get("content")
        if not file_b64:
            return func.HttpResponse(
                "Missing 'file_b64' in request body.",
                status_code=400
            )

        if "," in file_b64:
            file_b64 = file_b64.split(",", 1)[1]

        doc_bytes = base64.b64decode(file_b64)
        text = _docx_bytes_to_text(doc_bytes)

        return func.HttpResponse(
            text or "(no text found)",
            mimetype="text/plain",
            status_code=200,
        )



