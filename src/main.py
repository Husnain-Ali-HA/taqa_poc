import logging
from foundary_agents.pdf_read_agent import run_pdf_to_json_agent
from foundary_agents.write_into_excel import write_agents_data_into_excel
from foundary_agents.item_details_agent import item_data_processing_Agent
from utils.string_into_json_parsing import parse_first_json, parse_first_list
from foundary_agents.write_into_pptx import modify_existing_odp
import os
import json
from dotenv import load_dotenv
import time
# from datetime import datetime


load_dotenv()


LOG_PATH = "agent_pipeline.log"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    handlers=[
        logging.StreamHandler(),  # console
        logging.FileHandler(LOG_PATH, mode="a", encoding="utf-8"),  # file
    ],
)
logger = logging.getLogger("agent-workflow")


def run_pdf_pipeline():
    try:
        data = run_pdf_to_json_agent()
        logger.warning("=== Agent Pipeline Ended  ===")

        raw_text = data["raw_data"]
        run_id = data["run_id"]
        current_output = parse_first_json(raw_text)
    except ValueError:
        current_output = {"unparsed": raw_text}
    OUTPUT_FILE_PATH = os.getenv("OUTPUT_FILE_PATH")
    write_path = f"{OUTPUT_FILE_PATH}/pdf_read_agent/{run_id}.json"
    with open(write_path, "a", encoding="utf-8") as f:
        json.dump(current_output, f, ensure_ascii=False)
        f.write("\n")
    logger.warning("=== Agent Pipeline data proceed into json successfully  ===")
    return current_output


def run_item_data_processing_pipeline_for_pptx():
    try:
        data = item_data_processing_Agent()
        logger.warning("=== Agent Pipeline Ended  ===")

        raw_text = data["raw_data"]
        run_id = data["run_id"]
        current_output = parse_first_list(raw_text)
    except ValueError:
        current_output = {"unparsed": raw_text}
    OUTPUT_FILE_PATH = os.getenv("OUTPUT_FILE_PATH")
    write_path = f"{OUTPUT_FILE_PATH}/item_detail_agents/{run_id}.json"
    with open(write_path, "a", encoding="utf-8") as f:
        json.dump(current_output, f, ensure_ascii=False)
        f.write("\n")
    logger.warning("=== Agent Pipeline data proceed into json successfully  ===")
    return current_output


def run_complete_pipeline():
    start = time.perf_counter()
    logger.warning("=== Agentic Pdf Porcessing started  ===")

    pdf_extraction_agents = run_pdf_pipeline()
    elapsed_1 = time.perf_counter() - start

    path_of_excel_sheet = write_agents_data_into_excel(pdf_extraction_agents)
    elapsed_2 = time.perf_counter() - elapsed_1

    logger.warning(f"=== Agentic Pdf Porcessing Pipeline Completed  in {elapsed_1}===")
    print(f"Pdf Extraction Agents : {pdf_extraction_agents}")
    logger.warning(f"=== Agentic Pdf Porcessing Pipeline Completed  in {elapsed_2}===")
    print(f"Excel Sheet Path : {path_of_excel_sheet}")

    elapsed_3 = time.perf_counter()

    logger.warning(f"=== Agentic PPTX Porcessing Pipeline Started   in {elapsed_3}===")
    pptx_table = run_item_data_processing_pipeline_for_pptx()
    elapsed_4 = time.perf_counter() - elapsed_3
    logger.warning(
        f"=== Agentic PPTX  Porcessing Pipeline Completed  in {elapsed_4}==="
    )

    logger.warning(f"===Summary : {pptx_table}===")

    summary = {
        "SubTotal Amount ":pdf_extraction_agents["subtotal"],
        "Vat On  Amount ":pdf_extraction_agents["vat_on_amount"],
        "Grand Total Amount ":pdf_extraction_agents["grand_total_amount"]
    }
    modify_existing_odp(
        input_path=os.getenv("INPUT_ODP_PATH"),
        output_path=os.getenv("OUTPUT_ODP_FILE_PATH"),
        table_data=pptx_table,
        summary_json=summary,
    )
    logger.warning("=== ALL Pipeine completed in  ===")


if __name__ == "__main__":
    run_complete_pipeline()
