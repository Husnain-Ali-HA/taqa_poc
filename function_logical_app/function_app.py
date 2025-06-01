import json
import logging
import base64, io, os, textwrap
from typing import List
import azure.functions as func
from dotenv import load_dotenv

load_dotenv(override=False)

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)






@app.function_name(name="prcoess_excel_file")
@app.route(route="prcoess_excel_file")
def prcoess_excel_file(req: func.HttpRequest) -> func.HttpResponse:
    
    req_body = req.get_json()
    content_b64 = req_body.get("content")
    if not content_b64:
        return func.HttpResponse(
            "Missing 'content' field in JSON body.",
            status_code=400
        )

    # 2. Decode Base64 → raw bytes
    try:
        file_bytes = base64.b64decode(content_b64)
    except Exception as e:
        logging.error(f"Base64 decoding failed: {e}")
        return func.HttpResponse(
            "Invalid Base64 content.",
            status_code=400
        )

    # 3. Write bytes to a .xlsx file (keeps all original formatting)
    #    You can change 'output.xlsx' to whatever filename you need.
    #    In Azure Linux consumption, you can write to os.getcwd() or '/tmp'.
    output_path = os.path.join(os.getcwd(), "output.xlsx")
    try:
        with open(output_path, "wb") as f:
            f.write(file_bytes)
    except Exception as e:
        logging.error(f"Error writing file: {e}")
        return func.HttpResponse(
            f"Failed to write file: {e}",
            status_code=500
        )

    return func.HttpResponse(
        f"Excel file successfully saved to '{output_path}'.",
        status_code=200
    )