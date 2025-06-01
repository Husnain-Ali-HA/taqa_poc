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
from azure.ai.projects import AIProjectClient
# from azure.ai.agents.models import ChatRole

load_dotenv(override=False)

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)


def call_agent(prompt: str) -> dict:
    endpoint = os.getenv("AZURE_FOUNDRY_AGENTS_ENDPOINT")
    agent_id = os.getenv("WORD_FILE_DATA_EXTRRACTOR_AGENT")
    if not endpoint or not agent_id:
        raise RuntimeError(
            "Environment variables AZURE_AI_PROJECT_ENDPOINT and AGENT_ID must be set."
        )

    # 2. Authenticate and create the client
    credential = DefaultAzureCredential()
    client = AIProjectClient(
        endpoint=endpoint,
        credential=credential, 
        # api_version="latest"
    )

    thread = client.agents.threads.create()
    client.agents.messages.create(thread_id=thread.id, role="user", content=prompt)

    # 4. Kick off the agent run and wait for completion
    run = client.agents.runs.create_and_process(thread_id=thread.id, agent_id=agent_id)
    while run.status in ("queued", "in_progress"):
        time.sleep(1)
        run = client.agents.runs.get(thread_id=thread.id, run_id=run.id)

    # 5. Fetch all messages in the thread; pick the last assistant message
    all_msgs = client.agents.messages.list(thread_id=thread.id)
    assistant_reply = None
    for message in client.agents.messages.list(thread_id=thread.id):
        if message.role == "assistant":
            content_obj = message.content
            if hasattr(content_obj, "text"):
                assistant_reply = content_obj.text
            else:
                assistant_reply = str(content_obj)
                

    return {"response": assistant_reply, }


@app.function_name(name="prcoess_excel_file")
@app.route(route="prcoess_excel_file")
def prcoess_excel_file(req: func.HttpRequest) -> func.HttpResponse:
    req_body = req.get_json()
    content_b64 = req_body.get("content")
    # file_bytes = base64.b64decode(content_b64)
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
    return func.HttpResponse(json.dumps(result), status_code=200)
