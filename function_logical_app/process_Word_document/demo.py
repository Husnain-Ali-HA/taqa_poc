# # function_app.py

# from dotenv import load_dotenv
# import os
# import json
# # import tempfile
# # import subprocess

# # from office365.sharepoint.client_context import ClientContext
# # from office365.runtime.auth.client_credential import ClientCredential

# # from azure.core.credentials import AzureKeyCredential
# # from azure.ai.formrecognizer import DocumentAnalysisClient

# import azure.functions as func
# from azure.functions import AuthLevel
# # from azure.functions import FunctionApp, HttpRequest, HttpResponse, AuthLevel

# # Load .env into environment
# load_dotenv()

# # # SharePoint and Form Recognizer settings
# # CLIENT_ID       = os.getenv("SP_CLIENT_ID")
# # CLIENT_SECRET   = os.getenv("SP_CLIENT_SECRET")
# # SITE_URL        = os.getenv("SP_SITE_URL")            # e.g. https://<tenant>.sharepoint.com/sites/<YourSite>
# # FORM_ENDPOINT   = os.getenv("FORM_RECOGNIZER_ENDPOINT")
# # FORM_KEY        = os.getenv("FORM_RECOGNIZER_KEY")

# app = func.FunctionApp(AuthLevel=AuthLevel.ANONYMOUS)



# @app.function_name(name="hello")

# @app.route(route="hello")             
# def hello(req: func.HttpRequest) -> func.HttpResponse:

#     return func.HttpResponse("My name is Ali and email is abc@gmial.com", status_code=200)





























# @app.function_name(name="ProcessSharePointDoc")
# @app.route(route="ProcessSharePointDoc")
# def process_sharepoint_doc(req: HttpRequest) -> HttpResponse:
#     # # 1) Validate configuration
#     # if not all([CLIENT_ID, CLIENT_SECRET, SITE_URL, FORM_ENDPOINT, FORM_KEY]):
#     #     return HttpResponse(
#     #         json.dumps({"error": "Missing required environment variables."}),
#     #         status_code=500,
#     #         mimetype="application/json"
#     #     )

#     # # 2) Parse filePath from request body
#     # try:
#     #     body      = req.get_json()
#     #     file_path = body.get("filePath", "").strip()
#     # except ValueError:
#     #     return HttpResponse(
#     #         json.dumps({"error": "Invalid JSON payload."}),
#     #         status_code=400,
#     #         mimetype="application/json"
#     #     )
#     # if not file_path:
#     #     return HttpResponse(
#     #         json.dumps({"error": "`filePath` is required in the request body."}),
#     #         status_code=400,
#     #         mimetype="application/json"
#     #     )

#     # # 3) Connect to SharePoint via service principal
#     # creds = ClientCredential(CLIENT_ID, CLIENT_SECRET)
#     # ctx   = ClientContext(SITE_URL).with_credentials(creds)
 
#     # # Ensure the server-relative URL starts with a slash
#     # server_relative_url = file_path if file_path.startswith("/") else f"/{file_path}"

#     # # 4) Download the DOCX to a temp file
#     # with tempfile.TemporaryDirectory() as tmp:
#     #     local_docx = os.path.join(tmp, "input.docx")
#     #     ctx.web.get_file_by_server_relative_url(server_relative_url) \
#     #         .download(local_docx) \
#     #         .execute_query()

#     #     # 5) Convert DOCX → PDF using LibreOffice CLI
#     #     local_pdf = os.path.join(tmp, "input.pdf")
#     #     try:
#     #         subprocess.run([
#     #             "libreoffice", "--headless",
#     #             "--convert-to", "pdf",
#     #             "--outdir", tmp,
#     #             local_docx
#     #         ], check=True)
#     #     except subprocess.CalledProcessError as e:
#     #         return HttpResponse(
#     #             json.dumps({"error": "PDF conversion failed", "detail": str(e)}),
#     #             status_code=500,
#     #             mimetype="application/json"
#     #         )

#     #     # Read the generated PDF bytes
#     #     with open(local_pdf, "rb") as f:
#     #         pdf_bytes = f.read()

#     # # 6) Analyze the PDF with Azure Document Intelligence
#     # form_client = DocumentAnalysisClient(
#     #     endpoint=FORM_ENDPOINT,
#     #     credential=AzureKeyCredential(FORM_KEY)
#     # )
#     # try:
#     #     poller = form_client.begin_analyze_document("prebuilt-document", pdf_bytes)
#     #     result = poller.result()
#     # except Exception as e:
#     #     return HttpResponse(
#     #         json.dumps({"error": "Document analysis failed", "detail": str(e)}),
#     #         status_code=500,
#     #         mimetype="application/json"
#     #     )

#     # 7) Return the analysis JSON
#     # return HttpResponse(
#     #     json.dumps(result.to_dict(), default=str),
#     #     status_code=200,
#     #     mimetype="application/json"
#     # )
#     dict={"test":"This is an empyee name is Demmo user 1 and meial is abc@gmail.com"}
#     return HttpResponse(
#         json.dumps(dict, default=str),
#         status_code=200,
#         mimetype="application/json"
#     )