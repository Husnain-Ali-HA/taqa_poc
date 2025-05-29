# function_app.py
from dotenv import load_dotenv
import os
import json
import tempfile
import subprocess
import requests

import azure.functions as func
from azure.functions import FunctionApp, HttpRequest, HttpResponse, AuthLevel

from msal import ConfidentialClientApplication
from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer import DocumentAnalysisClient

from urllib.parse import quote

# 1) Load environment variables
load_dotenv()
TENANT_ID       = os.getenv("SP_TENANT_ID")
CLIENT_ID       = os.getenv("SP_CLIENT_ID")
CLIENT_SECRET   = os.getenv("SP_CLIENT_SECRET")
SITE_ID         = os.getenv("SP_SITE_ID")
DRIVE_ID        = os.getenv("SP_DRIVE_ID")
FORM_ENDPOINT   = os.getenv("FORM_RECOGNIZER_ENDPOINT")
FORM_KEY        = os.getenv("FORM_RECOGNIZER_KEY")

app = FunctionApp()

@app.function_name(name="ProcessSharePointDoc")
@app.route(
    route="ProcessSharePointDoc",
    methods=["POST"],
   
)
def process_sharepoint_doc(req: HttpRequest) -> HttpResponse:



    body     = req.get_json()
    filePath = body.get("filePath", "").lstrip("/")

    authority = f"https://login.microsoftonline.com/{TENANT_ID}"
    msal_app  = ConfidentialClientApplication(
        client_id=CLIENT_ID,
        client_credential=CLIENT_SECRET,
        authority=authority
    )
    result = msal_app.acquire_token_for_client(scopes=["https://graph.microsoft.com/.default"])
    access_token = result.get("access_token")

    headers = {"Authorization": f"Bearer {access_token}"}


    encoded_path = quote(filePath, safe="/")
    graph_url = (
        f"https://graph.microsoft.com/v1.0/"
        f"sites/{SITE_ID}/drives/{DRIVE_ID}"
        f"/root:/{encoded_path}:/content"
    )
    resp = requests.get(graph_url, headers=headers)
    if resp.status_code != 200:
        return HttpResponse(
            json.dumps({
                "error": "Failed to download DOCX",
                "status": resp.status_code,
                "detail": resp.text
            }),
            status_code=502,
            mimetype="application/json"
        )
    docx_bytes = resp.content

   
    with tempfile.TemporaryDirectory() as tmp:
        in_docx = os.path.join(tmp, "in.docx")
        out_pdf = os.path.join(tmp, "in.pdf")
        with open(in_docx, "wb") as f:
            f.write(docx_bytes)

            subprocess.run([
                "libreoffice", "--headless",
                "--convert-to", "pdf",
                "--outdir", tmp,
                in_docx
            ], check=True)
        with open(out_pdf, "rb") as f:
            pdf_bytes = f.read()
            
    form_client = DocumentAnalysisClient(
        endpoint=FORM_ENDPOINT,
        credential=AzureKeyCredential(FORM_KEY)
    )

    poller = form_client.begin_analyze_document("prebuilt-document", pdf_bytes)
    result = poller.result()



    return HttpResponse(
        json.dumps(result.to_dict(), default=str),
        status_code=200,
        mimetype="application/json"
    )
