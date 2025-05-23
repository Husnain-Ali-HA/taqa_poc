# import os
# import requests
# from msal import PublicClientApplication
# from dotenv import load_dotenv
# load_dotenv()

# TENANT_ID = os.getenv("TENANT_ID")
# CLIENT_ID = os.getenv("CLIENT_ID")
# SCOPES = ["Files.Read.All", "Sites.Read.All", "User.Read"]

# app = PublicClientApplication(
#     CLIENT_ID,
#     authority=f"https://login.microsoftonline.com/{TENANT_ID}"
# )

# result = app.acquire_token_interactive(scopes=SCOPES, port=5000)

# if "access_token" not in result:
#     raise RuntimeError("Failed to get access_token! Check error:", result)

# access_token = result["access_token"]

# USER_PRINCIPAL_NAME = "husnain.ali@digifloat.com"

# # File paths in OneDrive
# FILES_TO_DOWNLOAD = [
#     ("TAQA_Electric_grid/project_1/week_1/Taqa_Transmission_grid.pdf", "Taqa_Transmission_grid.pdf"),
#     ("TAQA_Electric_grid/project_1/week_1/grid_system_ppt.pptx", "grid_system_ppt.pptx"),
#     ("TAQA_Electric_grid/project_1/week_1/invoices.xlsx", "invoices.xlsx"),
# ]

# # Local directory to save files
# DOWNLOAD_DIR = "/home/husnain-ali/Desktop/taqa_pos/src/Data_Folder/INPUT"
# os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# headers = {"Authorization": f"Bearer {access_token}"}

# for file_path, save_as in FILES_TO_DOWNLOAD:
#     url = f"https://graph.microsoft.com/v1.0/users/{USER_PRINCIPAL_NAME}/drive/root:/{file_path}:/content"
#     local_path = os.path.join(DOWNLOAD_DIR, save_as)
#     resp = requests.get(url, headers=headers, stream=True)
#     if resp.status_code == 200:
#         with open(local_path, "wb") as f:
#             for chunk in resp.iter_content(chunk_size=8192):
#                 f.write(chunk)
#         print(f"Downloaded: {local_path}")
#     else:
#         print(f"Failed to download {file_path}: {resp.status_code} {resp.text}")


import os
import requests
from msal import PublicClientApplication
from dotenv import load_dotenv
load_dotenv()

TENANT_ID = os.getenv("TENANT_ID")
CLIENT_ID = os.getenv("CLIENT_ID")
SCOPES = ["Files.Read.All", "Sites.Read.All", "User.Read"]
USER_PRINCIPAL_NAME = "husnain.ali@digifloat.com"
BASE_DOWNLOAD_DIR = "/home/husnain-ali/Desktop/taqa_pos/src/Data_Folder/INPUT"

app = PublicClientApplication(
    CLIENT_ID,
    authority=f"https://login.microsoftonline.com/{TENANT_ID}"
)

def get_access_token():
    result = app.acquire_token_interactive(scopes=SCOPES, port=5000)
    if "access_token" not in result:
        raise RuntimeError("Failed to get access_token! Check error:", result)
    return result["access_token"]

def download_week_files(week_no):
    access_token = get_access_token()
    headers = {"Authorization": f"Bearer {access_token}"}
    week_path = f"TAQA_Electric_grid/project_1/week_{week_no}"
    files = [
        (f"{week_path}/Taqa_Transmission_grid.pdf", "Taqa_Transmission_grid.pdf"),
        (f"{week_path}/grid_system_ppt.pptx", "grid_system_ppt.pptx"),
        (f"{week_path}/invoices.xlsx", "invoices.xlsx"),
    ]
    week_download_dir = os.path.join(BASE_DOWNLOAD_DIR, f"week_{week_no}")
    os.makedirs(week_download_dir, exist_ok=True)
    for file_path, save_as in files:
        url = f"https://graph.microsoft.com/v1.0/users/{USER_PRINCIPAL_NAME}/drive/root:/{file_path}:/content"
        local_path = os.path.join(week_download_dir, save_as)
        resp = requests.get(url, headers=headers, stream=True)
        if resp.status_code == 200:
            with open(local_path, "wb") as f:
                for chunk in resp.iter_content(chunk_size=8192):
                    f.write(chunk)
            print(f"Downloaded: {local_path}")
        else:
            print(f"Failed to download {file_path}: {resp.status_code} {resp.text}")

