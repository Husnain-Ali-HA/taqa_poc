import os
import logging
from dotenv import load_dotenv

import msal
import requests

import azure.functions as func
from azure.functions import FunctionApp, HttpRequest, HttpResponse, AuthLevel


load_dotenv()

TENANT_ID     = os.getenv("TENANT_ID")
CLIENT_ID     = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")

SCOPES        = [
    "https://graph.microsoft.com/Sites.Read.All",
    "https://graph.microsoft.com/Files.Read.All"
]


app = FunctionApp()

def get_obo_token(user_assertion: str) -> str:
    """
    Exchange the front-end's user token for a new on-behalf-of token
    carrying your delegated Graph scopes.
    """
    cca = msal.ConfidentialClientApplication(
        CLIENT_ID,
        authority=f"https://login.microsoftonline.com/{TENANT_ID}",
        client_credential=CLIENT_SECRET
    )

    obo_result = cca.acquire_token_on_behalf_of(
        user_assertion=user_assertion,
        scopes=SCOPES
    )
    logging.info("MSAL OBO response: %s", obo_result)

    if "access_token" in obo_result:
        return obo_result["access_token"]

    error = obo_result.get("error_description") or obo_result.get("error")
    logging.error("OBO error: %s", error)
    raise RuntimeError(f"OBO failed: {error}")


@app.function_name(name="get_sharepoint_file")
@app.route(
    route="get_sharepoint_file",
    auth_level=AuthLevel.FUNCTION,
    methods=["GET", "POST"]
)
def get_sharepoint_file(req: HttpRequest) -> HttpResponse:
    # 1) Extract the incoming user token
    auth_header = req.headers.get("Authorization", "")
    if not auth_header.lower().startswith("bearer "):
        return HttpResponse("Missing or invalid Authorization header.", status_code=401)

    user_token = auth_header.split(" ", 1)[1]

    # 2) Acquire an OBO token
    try:
        graph_token = get_obo_token(user_token)
    except Exception as e:
        return HttpResponse(f"Token exchange error: {e}", status_code=500)

    headers = {"Authorization": f"Bearer {graph_token}"}

    # 3) (Optional) Ping the site to verify delegated access
    ping = requests.get(f"https://graph.microsoft.com/v1.0/sites/{os.getenv('SHAREPOINT_SITE_ID')}", headers=headers)
    logging.info("Site-metadata fetch: %d %s", ping.status_code, ping.text)
    if ping.status_code != 200:
        return HttpResponse(f"Site lookup failed: {ping.status_code} {ping.text}", status_code=ping.status_code)

    # 4) Download the file under delegated context
    body = req.get_json(silent=True) or {}
    path = body.get("path")
    if not path:
        return HttpResponse("Please supply JSON body { \"path\": \"Folder/Sub/f.docx\" }", status_code=400)

    download_url = (
        f"https://graph.microsoft.com/v1.0/"
        f"sites/{os.getenv('SHAREPOINT_SITE_ID')}/drive/root:/{path}:/content"
    )
    resp = requests.get(download_url, headers=headers, stream=True)

    if resp.status_code != 200:
        return HttpResponse(f"Graph returned {resp.status_code}: {resp.text}", status_code=resp.status_code)

    filename = os.path.basename(path)
    return HttpResponse(
        body=resp.content,
        status_code=200,
        headers={
            "Content-Disposition": f"attachment; filename={filename}",
            "Content-Type": resp.headers.get("Content-Type", "application/octet-stream"),
            "Access-Control-Allow-Origin": "*"    # if you’re calling this from browser-side JS
        }
    )
