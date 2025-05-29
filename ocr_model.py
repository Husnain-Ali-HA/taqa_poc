import os
from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence import DocumentIntelligenceClient

def extract_plain_text_from_pdf_bytes(file_path: str, output_path: str):

    endpoint ="https://taqa-document-intellgience.cognitiveservices.azure.com/"
    api_key  = "BmGDVp82plbBSTdjRwqBf7RfAPPTAkTCnhsbSw9wMRcnyVruwkDaJQQJ99BEACYeBjFXJ3w3AAALACOGlHKk"
    client   = DocumentIntelligenceClient(endpoint, AzureKeyCredential(api_key))


    model="prebuilt-read"
    with open(file_path, "rb") as infile:
        poller = client.begin_analyze_document(
            model_id=model,
            body=infile,
            content_type="application/pdf"  
        )
    result = poller.result()
    print(f">>> Analyze status: {poller.status()}")
    print(f">>> Pages returned: {len(result.pages)}")

    # 4) Collect lines
    lines = []
    for i, page in enumerate(result.pages, start=1):
        print(f"  – Page {i}: {len(page.lines)} lines")
        for line in page.lines:
            lines.append(line.content)

    # 5) Write out
    if not lines:
        print(">>> No lines found—try a different model or check your input PDF.")
    plain_text = "\n".join(lines)
    with open(output_path, "w", encoding="utf-8") as outfile:
        outfile.write(plain_text)

    print(f">>> Extracted text written to {output_path} ({len(plain_text)} chars)")


if __name__ == "__main__":

    input_txt   = "/home/husnain-ali/Desktop/taqa_pos/file_pdf.txt"
    output_txt  = "/home/husnain-ali/Desktop/taqa_pos/_output.txt"
    extract_plain_text_from_pdf_bytes(input_txt, output_txt)
