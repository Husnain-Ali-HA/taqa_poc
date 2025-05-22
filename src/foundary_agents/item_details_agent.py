import logging
from azure.ai.projects import AIProjectClient  # type: ignore
from azure.identity import DefaultAzureCredential  # type: ignore
from azure.ai.agents.models import ListSortOrder, FileSearchTool  # type: ignore
import os
from dotenv import load_dotenv

load_dotenv()

LOG_PATH = "agent_pipeline_1.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    handlers=[
        logging.StreamHandler(),
        # logging.FileHandler(mode="a", encoding="utf-8"),
        logging.FileHandler(LOG_PATH, mode="a", encoding="utf-8"),  # file
    ],
)
logger = logging.getLogger("agent-workflow")


project = AIProjectClient(
    endpoint=os.getenv("AZURE_PROJECT_ENDPOINT"),
    credential=DefaultAzureCredential(),
)


file = project.agents.files.upload(
    file_path=os.getenv("INPUT_FILE_PATH"),
    purpose="assistants",
)
vector_store = project.agents.vector_stores.create_and_poll(
    file_ids=[file.id], name=os.getenv("VECTOR_STORE_NAME_2")
)

file_search = FileSearchTool(vector_store_ids=[vector_store.id])


def crete_Agent():
    return project.agents.create_agent(
        model="o3-mini",
        name="item-detail-processing-agent",
        instructions="""You are a helpful assistant You have to find item descriptions form data and return that table data into list of list format.""",
        tools=file_search.definitions,
        tool_resources=file_search.resources,
    )


# def crete_Agent():
# return project.agents.get_agent("asst_ISt0WYwSTrcNdEQnJMEF91Jp")


def item_data_processing_Agent():
    agent = crete_Agent()
    logger.warning("=== Agent Creted Successfully  ===")
    thread = project.agents.threads.create()
    project.agents.messages.create(
        thread_id=thread.id,
        role="user",
        content="""
        Hello You have to provide An json fomat for these data according to files :
        i require these detials in json format you have to provide only list of list  file in  in output . 
        The data i required from Line-Item Details :Item Description ,Specification / Notes,Qty,Unit Price (USD) , Line Total (USD) . you have to provide list of list 
        Here is an a example list you have to provide like this : [
                        ["Item", "Description", "Specification / Notes", "Qty", "Unit Price (USD)", "Line Total (USD)"],
                        [1, "ABC ", "6", "8", "9", "7"]
                    ]
        The data i required :Item Description ,Specification / Notes,Qty,Unit Price (USD) , Line Total (USD) . you have to provide list of list
        The file name i have provided is Taqa_transmission_grid.pdf
    """,
    )
    logger.warning("=== Agent Data Processing Started  ===")

    run = project.agents.runs.create_and_process(thread_id=thread.id, agent_id=agent.id)

    logger.warning("=== Agent Data Processing Ended  ===")

    if run.status == "failed":
        print(f"Run failed: {run.last_error}")
    logger.warning("=== Agent Clen up Processing Started  ===")

    project.agents.files.delete(file_id=file.id)
    project.agents.delete_agent(agent.id)

    logger.warning("=== Agent Clen up Processing Ended  ===")

    latest_msg_iter = project.agents.messages.list(
        thread_id=thread.id, run_id=run.id, order=ListSortOrder.DESCENDING, limit=1
    )
    latest = next(latest_msg_iter, None)

    if latest and latest.text_messages:
        raw_text = latest.text_messages[-1].text.value
        print("Assistant (raw):", raw_text)

    return {"raw_data": raw_text, "run_id": run.id}


# item_data_processing_Agent()
