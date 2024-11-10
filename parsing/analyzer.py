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

    # 4 условие
    deliveries = main_dict["deliveries"]
    prams[3] = [True, []]
    conditions = [] # str
    for delivery in deliveries:
        delPlace = delivery["deliveryPlace"]
        for file in files:
            if delPlace not in file:
                conditions.append(f"Не совпадает адрес поставки {delPlace}")
                prams[0] = prams[0] and False
        items = delivery["items"]
        for item in items:
            name = item["name"]
            print(f"name = {name}")
            for file in files:
                if delPlace not in file:
                    conditions.append(f"Не совпадает названия этапов поставки {name}")
                    prams[0] = prams[0] and False
    prams[3][1] = conditions

    # 5 условие
    prompt = str(main_dict["startCost"])
    for file in files:
        if prompt in file:
            prams[4] = True
            break

    return prams