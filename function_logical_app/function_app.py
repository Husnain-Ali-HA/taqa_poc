import json
import logging
import re
import base64, io, os, textwrap
from typing import List
import azure.functions as func
from dotenv import load_dotenv
import os
import time
from azure.identity import DefaultAzureCredential
# from azure.core.credentials import AzureKeyCredential
from azure.ai.projects import AIProjectClient

# Deployment : Jun 2 : 11:29 AM


from openpyxl import load_workbook, Workbook

load_dotenv()

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

@app.route(route="health_check")
def health_check(req: func.HttpRequest) -> func.HttpResponse:
    return func.HttpResponse(
        json.dumps({"content": "ok"}), status_code=200, mimetype="application/json"
    )



def call_agent(prompt: str) -> dict:
    # endpoint = os.environ.get("AZURE_FOUNDRY_AGENTS_ENDPOINT")
    # agent_id = os.environ.get("WORD_FILE_DATA_EXTRRACTOR_AGENT")    
    endpoint = "https://taqa-electric-grid.services.ai.azure.com/api/projects/taqa-electric-grid"
    agent_id = "asst_NbiJUw9yQGRWX1LLMC7dWBdI"
    AZURE_FOUNDRY_AGENTS_APIKEY="8YHvIOstZSLqX7Lb8plm4k2XqLRWQSDWGGJ4ypuQDpZqKyWM74H3JQQJ99BEACHYHv6XJ3w3AAAAACOGYX4y"
    if not endpoint or not agent_id:
        raise RuntimeError(
            "Environment variables AZURE_AI_PROJECT_ENDPOINT and AGENT_ID must be set."
        )

    # credential = AzureKeyCredential(AZURE_FOUNDRY_AGENTS_APIKEY)

    client = AIProjectClient(
        endpoint=endpoint,
        credential=DefaultAzureCredential(),
        # api_version="latest"
    )

    thread = client.agents.threads.create()
    client.agents.messages.create(thread_id=thread.id, role="user", content=prompt)
    run = client.agents.runs.create_and_process(thread_id=thread.id, agent_id=agent_id)
    while run.status in ("queued", "in_progress"):
        time.sleep(1)
        run = client.agents.runs.get(thread_id=thread.id, run_id=run.id)

    all_msgs = list(client.agents.messages.list(thread_id=thread.id))

    assistant_msgs = [m for m in all_msgs if m.role == "assistant"]

    if not assistant_msgs:
        raise RuntimeError("No assistant message found in thread.")
    last_assistant = assistant_msgs[-1]

    content_obj = last_assistant.content
    if hasattr(content_obj, "text"):
        assistant_reply = content_obj.text
    else:
        assistant_reply = str(content_obj)
    return {"response": assistant_reply}


def parse_progress_from_response(response_str):
    match = re.search(r'"progress"\s*:\s*([0-9]+(?:\.[0-9]+)?)', response_str)
    if not match:
        raise ValueError("Progress value not found in the response string.")
    progress_value = float(match.group(1))
    return {"progress": progress_value}


def load_workbook_from_base64(b64_string: str) -> Workbook:
    """
    Decode a Base64 string into bytes, then load it into an openpyxl Workbook.
    Returns the loaded Workbook object (preserving all formatting).
    """
    file_bytes = base64.b64decode(b64_string)
    stream = io.BytesIO(file_bytes)
    wb = load_workbook(filename=stream, data_only=False)
    return wb


def save_workbook_to_base64(wb: Workbook) -> str:
    stream = io.BytesIO()
    wb.save(stream)
    stream.seek(0)
    return base64.b64encode(stream.read()).decode("utf-8")

@app.route(route="prcoess_excel_file")
@app.function_name(name="prcoess_excel_file")
def prcoess_excel_file(req: func.HttpRequest) -> func.HttpResponse:
    req_body = req.get_json()
    content_b64 = req_body.get("content")
    file_bytes = base64.b64decode(content_b64)
    # output_path = os.path.join(os.getcwd(), "output.xlsx")

    # with open(output_path, "wb") as f:
    #         f.write(file_bytes)

    user_prompt = """
                    You are given access to a tool named `extractdatafromwordfile_Tool`. When instructed, you must:  
                    1. Call `extractdatafromwordfile_Tool` to retrieve its output (a JSON object containing a field called `"progress"` whose value is in percentage  
                    2. Read the `"From Over all progress planned you have to find out actual "` Find out this form the output of the tool.  
                    3. Return only a JSON object with a single key `"progress"` and its   
                    value set to the computed percentage (as a number). Do not include any other keys or any extra text.  

                    For example, if the tool returns:  
                    ```json  
                    {  
                    "progress": "the overall progress actual",  
                    }  

                  """
    result = call_agent(user_prompt)
    progress = parse_progress_from_response(result["response"])
    wb = load_workbook_from_base64(content_b64)

    # 4) Access the "Progress %" sheet
    sheet_name = "Progress %"
    if sheet_name not in wb.sheetnames:
        return func.HttpResponse(
            json.dumps({"error": f"Worksheet '{sheet_name}' not found."}),
            status_code=400,
            mimetype="application/json",
        )
    ws = wb[sheet_name]

    ws["B4"].value = 1
    ws["C4"].value = "Project 1"
    ws["D4"].value = progress["progress"]
    # wb.save("input.xlsx")

    new_b64 = save_workbook_to_base64(wb)


    # Decode the Base64 string into binary Excel content
    excel_data = base64.b64decode(new_b64)

    # Write the binary content to an Excel file
    with open("output.xlsx", "wb") as f:
        f.write(excel_data)
    return func.HttpResponse(
        json.dumps({"content": new_b64}), status_code=200, mimetype="application/json"
    )














































import base64
import json
import io
from pptx import Presentation
import uuid

@app.route(route="prcoess_power_point_file")
@app.function_name(name="prcoess_power_point_file")
def prcoess_power_point_file(req: func.HttpRequest) -> func.HttpResponse:
    try:
        req_body = req.get_json()
        content_b64 = req_body.get("content")
        new_value = "AED 350,000"
        
        # Decode the PowerPoint file
        ppt_bytes = base64.b64decode(content_b64)
        
        # Load the presentation
        prs = Presentation(io.BytesIO(ppt_bytes))
        
        # Process slide 2 (index 1)
        if len(prs.slides) >= 2:
            slide = prs.slides[1]
            
            # Search through all shapes
            for shape in slide.shapes:
                # Check if shape is a table
                if shape.has_table:
                    table = shape.table
                    for row in table.rows:
                        for i, cell in enumerate(row.cells):
                            if "Awarded value:" in cell.text:
                                # Found the label cell, next cell should contain the value
                                if i + 1 < len(row.cells):
                                    # Clear existing text and add new value
                                    next_cell = row.cells[i+1]
                                    next_cell.text = new_value
                                    # Preserve formatting by keeping at least one run
                                    if not next_cell.text_frame.paragraphs[0].runs:
                                        next_cell.text_frame.paragraphs[0].add_run()
                                    break
                
                # Check text frames if not found in tables
                elif shape.has_text_frame:
                    for paragraph in shape.text_frame.paragraphs:
                        if "Awarded value:" in paragraph.text:
                            # Replace just the value portion if possible
                            if "AED" in paragraph.text:
                                paragraph.text = paragraph.text.replace("AED 220,500,000.00", new_value)
                            else:
                                paragraph.text = f"Awarded value: {new_value}"
                            break
        
        # Save modified presentation
        modified_ppt = io.BytesIO()
        prs.save(modified_ppt)
        modified_ppt.seek(0)
        
        # Save locally for debugging
        debug_filename = f"modified_{uuid.uuid4().hex[:6]}.pptx"
        with open(debug_filename, "wb") as f:
            f.write(modified_ppt.getvalue())
        
        # Return modified file
        return func.HttpResponse(
            json.dumps({
                "content": base64.b64encode(modified_ppt.getvalue()).decode('utf-8'),
                "debug_file": debug_filename,
                "message": "PowerPoint updated successfully"
            }), 
            status_code=200, 
            mimetype="application/json"
        )
    
    except Exception as e:
        return func.HttpResponse(
            json.dumps({
                "error": str(e),
                "details": "Failed to update PowerPoint value",
                "solution": "Please ensure the slide contains either a table with 'Awarded value:' or text frame with this label"
            }),
            status_code=500,
            mimetype="application/json"
        )