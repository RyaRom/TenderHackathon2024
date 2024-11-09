import os
import json
from parsing.FilesDecoder import FileHolder

def find_first_pdf_and_doc(directory):
    pdf_path = None
    doc_path = None
    print(directory)
    for root, _, files in os.walk(directory):
        print(files)
        for file in files:
            file_path = os.path.join(root, file)
            print(file.lower() + " file lower")
            if file.lower().endswith(".pdf") and pdf_path is None:
                pdf_path = file_path

            elif (file.lower().endswith(".doc") or file.lower().endswith(".docx")) and doc_path is None:
                doc_path = file_path

            if pdf_path and doc_path:
                return pdf_path, doc_path

    return pdf_path, doc_path


async def scan_files(auction_id):
    web_page_json = f"downloaded_files/{auction_id}/response_{auction_id}.json"
    doc_file, pdf_contract = find_first_pdf_and_doc("downloaded_files")
    print(f"{web_page_json}, {doc_file}, {pdf_contract}")

    with open(web_page_json, 'r', encoding="UTF-8") as file:
        data = json.load(file)

    title = data.get('customer-name')
    print(f"{title}")
    doc = FileHolder(doc_file)
    pdf = FileHolder(doc_file)
    print(f"{doc.data[0]}")
