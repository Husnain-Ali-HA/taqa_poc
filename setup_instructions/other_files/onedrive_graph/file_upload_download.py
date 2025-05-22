import os
import requests
from msal import ConfidentialClientApplication
from dotenv import load_dotenv
load_dotenv() 


TENANT_ID = os.getenv("TENANT_ID")
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
USER_PRINCIPAL_NAME = os.getenv("USER_PRINCIPAL_NAME")
SCOPES = ["https://graph.microsoft.com/.default"]


app = ConfidentialClientApplication(
    CLIENT_ID,
    authority=f"https://login.microsoftonline.com/{TENANT_ID}",
    client_credential=CLIENT_SECRET,
)


token = app.acquire_token_for_client(scopes=SCOPES)
if "access_token" not in token:
    raise RuntimeError(token.get("error_description"))


HEADERS = {
    "Authorization": f"Bearer {token['access_token']}",
    "Accept": "application/json",
}



def upload_file(local_path: str, target_folder: str):
    filename = os.path.basename(local_path)
    url = (
        f"https://graph.microsoft.com/v1.0/users/{USER_PRINCIPAL_NAME}"
        f"/drive/root:/{target_folder}/{filename}:/content"
    )
    with open(local_path, "rb") as f:
        data = f.read()
    r = requests.put(
        url, headers={**HEADERS, "Content-Type": "application/octet-stream"}, data=data
    )
    r.raise_for_status()
    print("✅ Uploaded:", r.json().get("webUrl"))


def download_file(drive_item_path: str, local_dest: str):
    url = (
        f"https://graph.microsoft.com/v1.0/users/{USER_PRINCIPAL_NAME}"
        f"/drive/root:/{drive_item_path}:/content"
    )
    r = requests.get(url, headers=HEADERS, stream=True)
    r.raise_for_status()
    with open(local_dest, "wb") as out:
        for chunk in r.iter_constent(4096):
            out.write(chunk)
    print(" Downloaded to", local_dest)


if __name__ == "__main__":
    upload_file("/home/husnain-ali/Desktop/taqa_pos/src/Files/Taqa_Transmission_grid.pdf", "TAQA_Electric_grid/project_1/week_1")
    # download_file("TAQA_Eectric_grid/week_1/Taqa.pdf", "Taqa_downloaded.pdf")
