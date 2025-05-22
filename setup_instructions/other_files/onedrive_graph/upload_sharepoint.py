import os
from dotenv import load_dotenv
from azure.identity import ClientSecretCredential
from msgraph.core import GraphClient

# ─── Load your secrets from .env ───────────────────────────────────────────────
load_dotenv()
TENANT_ID           = os.getenv("TENANT_ID")
CLIENT_ID           = os.getenv("CLIENT_ID")
CLIENT_SECRET       = os.getenv("CLIENT_SECRET")
USER_PRINCIPAL_NAME = os.getenv("USER_PRINCIPAL_NAME")  # e.g. husnain_ali@digifloat.onmicrosoft.com

# ─── Build a Graph client with client‐credentials ──────────────────────────────
credential = ClientSecretCredential(
    tenant_id=TENANT_ID,
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET
)
client = GraphClient(credential=credential)

# ─── (Optional) ensure the folder tree exists ──────────────────────────────────
def ensure_folder(path: str):

    parts = path.split("/")
    current = ""
    for p in parts:
        current = f"{current}/{p}".lstrip("/")
        resp = client.get(f"/users/{USER_PRINCIPAL_NAME}/drive/root:/{current}")
        if resp.status_code == 404:
            parent = "/".join(current.split("/")[:-1])
            if parent:
                post_to = f"/users/{USER_PRINCIPAL_NAME}/drive/root:/{parent}:/children"
            else:
                post_to = f"/users/{USER_PRINCIPAL_NAME}/drive/root/children"
            body = {"name": p, "folder": {}}
            client.post(post_to, json=body).raise_for_status()

# ─── Upload your file ──────────────────────────────────────────────────────────
def upload_file(local_path: str, target_folder: str):
    filename = os.path.basename(local_path)

    # 1) make sure the folder exists
    ensure_folder(target_folder)

    # 2) PUT the file contents
    with open(local_path, "rb") as f:
        data = f.read()

    resp = client.put(
        f"/users/{USER_PRINCIPAL_NAME}/drive/root:/{target_folder}/{filename}:/content",
        data=data,
        headers={"Content-Type": "application/octet-stream"}
    )
    resp.raise_for_status()
    print("✅ Uploaded:", resp.json().get("webUrl"))

# ─── Download your file ────────────────────────────────────────────────────────
def download_file(remote_path: str, local_dest: str):
    resp = client.get(
        f"/users/{USER_PRINCIPAL_NAME}/drive/root:/{remote_path}:/content",
        stream=True
    )
    resp.raise_for_status()
    with open(local_dest, "wb") as out:
        for chunk in resp.iter_bytes(4096):
            out.write(chunk)
    print("✅ Downloaded to", local_dest)


# ─── Example usage ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    FILE_PATH   = "/home/husnain-ali/Desktop/taqa_pos/src/Files/Taqa_Transmission_grid.pdf"
    TARGET_FOLD = "TAQA_Electric_grid/project_1/week_1"

    upload_file(FILE_PATH, TARGET_FOLD)
    # download_file(f"{TARGET_FOLD}/Taqa_Transmission_grid.pdf", "Taqa_dl.pdf")
