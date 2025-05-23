import os
import requests
from msal import PublicClientApplication
from dotenv import load_dotenv
load_dotenv()

TENANT_ID = os.getenv("TENANT_ID")
CLIENT_ID = os.getenv("CLIENT_ID")
SCOPES = ["Files.ReadWrite.All", "Sites.Read.All", "User.Read"]
USER_PRINCIPAL_NAME = "husnain.ali@digifloat.com"

app = PublicClientApplication(
    CLIENT_ID,
    authority=f"https://login.microsoftonline.com/{TENANT_ID}"
)

def upload_week_files(week_no):
    # Prepare local and remote paths
    LOCAL_UPLOAD_BASE = "/home/husnain-ali/Desktop/taqa_pos/src/Data_Folder/OUTPUT"
    LOCAL_UPLOAD_DIR = os.path.join(LOCAL_UPLOAD_BASE, f"week_{week_no}")
    os.makedirs(LOCAL_UPLOAD_DIR, exist_ok=True)

    REMOTE_PARENT = f"TAQA_Electric_grid/project_1/week_{week_no}"
    REMOTE_NEW_FOLDER = "report"

    # Auth
    result = app.acquire_token_interactive(scopes=SCOPES, port=5000)
    if "access_token" not in result:
        raise RuntimeError("Failed to get access_token! Check error:", result)
    access_token = result["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}

    # Ensure remote folder
    def ensure_remote_folder(headers, user_principal, parent_path, new_folder_name):
        url = f"https://graph.microsoft.com/v1.0/users/{user_principal}/drive/root:/{parent_path}:/children"
        data = {
            "name": new_folder_name,
            "folder": {},
            "@microsoft.graph.conflictBehavior": "rename"
        }
        resp = requests.post(url, headers={**headers, "Content-Type": "application/json"}, json=data)
        if resp.status_code in (201, 409):
            print(f"Remote folder '{new_folder_name}' ready.")
        else:
            print(f"Failed to create/find folder: {resp.status_code} {resp.text}")
            raise RuntimeError(resp.text)

    # Upload all files
    def upload_files(headers, user_principal, parent_path, folder_name, local_dir):
        remote_folder = f"{parent_path}/{folder_name}"
        for filename in os.listdir(local_dir):
            local_path = os.path.join(local_dir, filename)
            if os.path.isfile(local_path):
                url = f"https://graph.microsoft.com/v1.0/users/{user_principal}/drive/root:/{remote_folder}/{filename}:/content"
                with open(local_path, 'rb') as f:
                    resp = requests.put(url, headers=headers, data=f)
                if resp.status_code in (200, 201):
                    print(f"Uploaded: {filename}")
                else:
                    print(f"Failed to upload {filename}: {resp.status_code} {resp.text}")

    ensure_remote_folder(headers, USER_PRINCIPAL_NAME, REMOTE_PARENT, REMOTE_NEW_FOLDER)
    upload_files(headers, USER_PRINCIPAL_NAME, REMOTE_PARENT, REMOTE_NEW_FOLDER, LOCAL_UPLOAD_DIR)

# # Usage example:
# if __name__ == "__main__":
#     upload_week_files(1)  # This will use OUTPUT/week_1 and upload all files to the report folder
