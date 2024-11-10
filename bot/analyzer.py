import os
import json
import mammoth
from parsing.FilesDecoder import FileHolder


def find_first_pdf_and_doc(directory):
    pdf_path = None
    doc_path = None
    print(directory)
    for root, _, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            if file.lower().endswith(".pdf") and pdf_path is None:
                pdf_path = file_path

            elif (file.lower().endswith(".doc") or file.lower().endswith(".docx")) and doc_path is None:
                doc_path = file_path

            if pdf_path and doc_path:
                return pdf_path, doc_path

    return pdf_path, doc_path


async def scan_files(auction_id, options):
    web_page_json = f"downloaded_files/{auction_id}/response_{auction_id}.json"
    doc_file, pdf_contract = find_first_pdf_and_doc("downloaded_files")
    print(f"{web_page_json}, {doc_file}, {pdf_contract}")

    with open(web_page_json, 'r', encoding="UTF-8") as file:
        data = json.load(file)

    title = data.get('customer-name')
    # docname = FileHolder(pdf_contract)

    pdf = FileHolder(pdf_contract).data
    doc = FileHolder(doc_file).data
    print(pdf)
    print(doc)
    returnList = [False, False, False, False, False, False]
    if "1" in options:
        returnList[0] = validate_title(title, doc, pdf)
    if "2" in options:
        returnList[1] = validate_contract(data.get("isContractGuaranteeRequired"), doc, pdf)
    if "5" in options:
        returnList[4] = validate_price(data.get("startCost"), doc, pdf)


def validate_title(title, doc_data: str, pdf_data: str) -> bool:
    return title in doc_data or title in pdf_data


def validate_price(price, doc_data: str, pdf_data: str):
    return price in doc_data or price in pdf_data


def validate_contract(price, doc_data: str, pdf_data: str):
    if price:
        return "Обеспечение исполнения контракта" in pdf_data or "Обеспечение исполнения контракта" in pdf_data
    else:
        return True
