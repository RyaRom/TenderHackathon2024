import os
import json
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
    print(pdf_path, doc_path)
    return pdf_path, doc_path


# List[str = filename]
def extract_txt_files_to_list(directory_path):
    txt_files_content = []
    # Перебор всех файлов в указанной папке
    for filename in os.listdir(directory_path):
        if filename.endswith('.txt'):
            # txt_files_content.append(filename)
            file_path = os.path.join(directory_path, filename)
            with open(file_path, 'r', encoding='utf-8') as file:
                file_content = file.read()
                txt_files_content.append(file_content)
    return txt_files_content


# List[bool]
def checker(idloc, prams):
    JSON = open(f'test/response_{idloc}.json', encoding='utf-8')
    main_dict = json.load(JSON)
    # files = List[str = content]
    files = extract_txt_files_to_list("test")
    # files = ["" for j in files_names]
    # for file in range(len(files_names)):
    #     files[file] = "".join(open(files_names[file], encoding='utf-8').readlines()).lower()
    # j[0] - ключ JSON
    # j[1] - текст для поиска
    # j[2] - информация для поиска в документе (">-NULL-<")
    # j[3] - информация для поиска подстроки (">-NULL-<")
    # j[4] - обрезание строки (">-NULL-<")

    # 1 условие
    prompt = str(main_dict["name"])
    for file in files:
        if prompt in file:
            prams[0] = True
            break

    # 2 условие
    prompt = bool(main_dict["isContractGuaranteeRequired"])
    if prompt:
        for file in files:
            if "Обеспечение исполнения контракта" in file:
                prams[1] = True
                break
    else:
        prams[1] = True

    # 3 условие
    prompt = (bool(main_dict["isElectronicContractExecutionRequired"]) or
              bool(main_dict["isContractGuaranteeRequired"]))
    if prompt:
        for file in files:
            if file.count("сертификат") >= 3:
                prams[2] = True
                break
    else:
        prams[2] = True

    # TODO модель в 4 и 6

    # deliveries = main_dict["deliveries"]
    # for delivery in deliveries:

    # 5 условие
    prompt = str(main_dict["startCost"])
    for file in files:
        if prompt in file:
            prams[4] = True
            break

    return prams


async def scan_files(auction_id, options):
    web_page_json = f"C:\\Programming\\ParserTenderhack\\parsing\\test/response_{auction_id}.json"
    doc_file, pdf_contract = find_first_pdf_and_doc("C:\\Programming\\ParserTenderhack\\parsing\\test")
    print(f"{web_page_json}, {doc_file}, {pdf_contract}")

    with open(web_page_json, 'r', encoding="UTF-8") as file:
        data = json.load(file)

    title = data.get('customer-name')
    # docname = FileHolder(pdf_contract)

    pdf = FileHolder(pdf_contract).data
    doc = FileHolder(doc_file).data
    returnList = [False, False, False, False, False, False]
    return checker(auction_id, returnList)

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
