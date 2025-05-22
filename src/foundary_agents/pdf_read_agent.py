import logging
from azure.ai.projects import AIProjectClient  # type: ignore
from azure.identity import DefaultAzureCredential  # type: ignore
from azure.ai.agents.models import ListSortOrder, FileSearchTool  # type: ignore
import os
from dotenv import load_dotenv

load_dotenv()


LOG_PATH = "agent_pipeline.log"
logging.basicConfig(
    level=logging.INFO,  # global minimum level
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    handlers=[
        logging.StreamHandler(),  # console
        # logging.FileHandler( mode="a", encoding="utf-8"),  # file
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
    file_ids=[file.id], name=os.getenv("VECTOR_STORE_NAME")
)

file_search = FileSearchTool(vector_store_ids=[vector_store.id])


def crete_Agent():
    return project.agents.create_agent(
        model="o3-mini",
        name="pdf-processing-agent",
        instructions="""You are a helpful assistant and can search errorrmation from uploaded
    files and return an json formt only dont include anything in it expect of json format.""",
        tools=file_search.definitions,
        tool_resources=file_search.resources,
    )
# def crete_Agent():
#     return project.agents.get_agent("asst_Btu00BJeg2bqzXdlHV7fsm0v")


def run_pdf_to_json_agent():
    agent = crete_Agent()
    logger.warning("=== Agent Creted Successfully  ===")
    thread = project.agents.threads.create()
    project.agents.messages.create(
        thread_id=thread.id,
        role="user",
        content="""
        Hello You have to provide An json fomat for these data according to files :
        i require these detials in json format you have to provide only json file in  in put . 
        The data i required :Invoice no ,Date ,Supplier,Payment  Terms, 	Subtotal,Vat on Amount,	Grand Total.
        Here is how you can write larger amounts 100,000 add comma in between after thre digits from left to rgiht 
        Now here is json key value should be look like : 
                {
                invoice_no':'',
                'date':'',
                'supplier':'',
                'payment_terms':'',
                'subtotal':'',
                'vat_on_amount':'',
                'grand_total_amount':'',
                }'
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
    raw_text = None
    if latest and latest.text_messages:
        raw_text = latest.text_messages[-1].text.value
        print("Assistant (raw):", raw_text)

    return {"raw_data": raw_text, "run_id": run.id}


# run_pdf_to_json_agent()
