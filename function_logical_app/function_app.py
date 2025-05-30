import json
import base64, io, os, textwrap
from typing import List

import azure.functions as func
from dotenv import load_dotenv
from docx import Document
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from azure.ai.formrecognizer import DocumentAnalysisClient ,  AnalysisFeature
from azure.core.credentials import AzureKeyCredential


load_dotenv(override=False)
ENDPOINT = os.getenv("AZURE_DOC_INTEL_ENDPOINT")
KEY = os.getenv("AZURE_DOC_INTEL_KEY")


app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

docintel_client = DocumentAnalysisClient(ENDPOINT, AzureKeyCredential(KEY))


def _docx_bytes_to_text(doc_bytes: bytes) -> str:
    doc = Document(io.BytesIO(doc_bytes))
    paras: List[str] = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
    return "\n".join(paras)


def _make_pdf_bytes(text: str) -> bytes:
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=letter)
    width, height = letter
    x_margin, y_margin = 72, 72
    y = height - y_margin
    c.setFont("Times-Roman", 11)

    for para in text.splitlines():
        for line in textwrap.wrap(para, 90) or [""]:
            if y < y_margin:
                c.showPage()
                c.setFont("Times-Roman", 11)
                y = height - y_margin
            c.drawString(x_margin, y, line)
            y -= 14
        y -= 14
    c.save()
    pdf_bytes = buf.getvalue()
    buf.close()
    return pdf_bytes


def _read_with_docintel(pdf_bytes: bytes) -> str:
    poller = docintel_client.begin_analyze_document(
        model_id="prebuilt-layout", document=pdf_bytes, features=[  AnalysisFeature.OCR_HIGH_RESOLUTION],
    )
    result = poller.result()
    return "\n".join(line.content for pg in result.pages for line in pg.lines)
    # return result


@app.function_name(name="convert_docx_to_text")
@app.route(route="convert_docx_to_text")
def convert_docx_to_text(req: func.HttpRequest) -> func.HttpResponse:
    try:
        body = req.get_json()
        b64_docx = body.get("content")
        if not b64_docx:
            return func.HttpResponse(
                "'content' (Base-64 DOCX) is required.", status_code=400
            )

        if "," in b64_docx:
            b64_docx = b64_docx.split(",", 1)[1]

        doc_bytes = base64.b64decode(b64_docx)

        plain_text = _docx_bytes_to_text(doc_bytes)

        pdf_bytes = _make_pdf_bytes(plain_text)

        extracted = _read_with_docintel(pdf_bytes)
        response = {
            "extracted_text": extracted,
        }
        return func.HttpResponse(
            json.dumps(response),
            mimetype="text/plain",
            status_code=200,
        )

    except Exception as exc:
        return func.HttpResponse(f"Server error: {exc}", status_code=500)
