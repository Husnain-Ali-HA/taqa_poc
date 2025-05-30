import json
import base64, io, os, textwrap
from typing import List

import azure.functions as func
from dotenv import load_dotenv
from docx import Document
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from azure.ai.formrecognizer import DocumentAnalysisClient, AnalysisFeature
from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence.models import ContentFormat

load_dotenv(override=False)
ENDPOINT = os.getenv("AZURE_DOC_INTEL_ENDPOINT")
KEY = os.getenv("AZURE_DOC_INTEL_KEY")


app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

docintel_client = DocumentAnalysisClient(ENDPOINT, AzureKeyCredential(KEY))




def _read_with_docintel(pdf_bytes: bytes) -> str:
    poller = docintel_client.begin_analyze_document(
        model_id="prebuilt-layout",
        # model_id="prebuilt-read",
        document=pdf_bytes,
        # features=[AnalysisFeature.OCR_HIGH_RESOLUTION],
        output_content_format=ContentFormat.MARKDOWN
  
    )
    result = poller.result()
    return result.to_dict()
    # return "\n".join(line.content for pg in result.pages for line in pg.lines)

    parts = []

    # normal lines
    parts.extend(line.content for pg in result.pages for line in pg.lines)

    # table cells
    for table in result.tables:
        for cell in table.cells:
            if cell.content:
                parts.append(cell.content)

    return "\n".join(parts)
    # return result


@app.function_name(name="convert_docx_to_text")
@app.route(route="convert_docx_to_text")
def convert_docx_to_text(req: func.HttpRequest) -> func.HttpResponse:
    try:
        body = req.get_json()
        b64_pdf = body.get("content")

        pdf_bytes = base64.b64decode(b64_pdf)

        
        target_dir = os.getcwd()                     
        pdf_path = os.path.join(target_dir, "input.pdf")
        with open(pdf_path, "wb") as fh:
            fh.write(pdf_bytes)

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

