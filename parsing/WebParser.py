import os
import docx
import asyncio
import httpx
import json
from PyPDF2 import PdfReader
import magic  # To determine file type by MIME
import win32com.client
# Маска для подстановки URL ссылки
BASE_URL = "https://zakupki.mos.ru/newapi/api/Auction/Get?auctionId="


# Функция для сохранения данных в текстовый файл
async def save_to_txt(folder, file_name, text, file_id):
    # Создаем .txt файл с именем на основе оригинального имени файла
    txt_file_path = folder + file_name.split('.')[0] + ".txt"

    # Сохранение текста, если он передан
    with open(txt_file_path, "w", encoding="utf-8") as txt_file:
        txt_file.write(text)

    print("downloading")
    file_url = f"https://zakupki.mos.ru/newapi/api/FileStorage/Download?id={file_id}"

    async with httpx.AsyncClient() as client:
        response = await client.get(file_url)

    if response.status_code == 200:
        file_content = response.content
        file_path = folder + file_name.replace(" ", "")

        # Define the file type using the magic library (determine file MIME type)
        mime_type = magic.from_buffer(file_content, mime=True)
        print(mime_type)

        # Save the file
        with open(file_path, 'wb') as file:
            file.write(file_content)

        print(f"[INFO]: File {file_name} saved in folder {folder}.")

        # Output the file content based on its type
        if mime_type == 'text/plain':
            text = file_content.decode('utf-8')
            return text

        elif mime_type == 'application/pdf':
            print("[INFO]: PDF file detected. Extracting text...")
            return read_pdf(file_content)

        elif mime_type in ['application/vnd.ms-word', 'application/msword']:
            print("[INFO]: DOC file detected")
            text = read_doc(file_path)
            return text

        elif mime_type in ['application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                           'application/msword']:
            print("[INFO]: DOCX file detected. Extracting text...")
            text = read_docx(file_path)
            return text

        else:
            print(f"[INFO]: Unsupported file type {mime_type}.")
    else:
        print(f"[ERROR]: Failed to download file {file_name}. Status code: {response.status_code}")


def read_doc(file_path):
    word = win32com.client.Dispatch("Word.Application")
    word.visible = False
    doc = word.Documents.Open(file_path)
    doc_content = doc.Content.Text
    doc.Close(False)
    word.Quit()
    return doc_content


def read_pdf(file_content):
    # Reading PDF from content in memory
    with open("temp.pdf", "wb") as temp_pdf:
        temp_pdf.write(file_content)

    with open("temp.pdf", "rb") as file:
        reader = PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
    os.remove("temp.pdf")
    return text


def read_docx(file_path):
    doc = docx.Document(file_path)
    full_text = []
    for para in doc.paragraphs:
        full_text.append(para.text)
    return('\n'.join(full_text))


def flatten_json(nested_json, prefix=''):
    flat_dict = {}
    for key, value in nested_json.items():
        new_key = f"{prefix}{key}" if prefix == '' else f"{prefix}-{key}"
        if value is None:
            continue

        if isinstance(value, dict):
            flat_dict.update(flatten_json(value, new_key))
        elif isinstance(value, list):
            for i, item in enumerate(value):
                flat_dict.update(flatten_json(item, f"{new_key}-{i}"))
        else:
            flat_dict[new_key] = value
    return flat_dict

def download_json(json_data, auction_folder, auction_id):
    path = os.path.join(auction_folder, f"response_{auction_id}.json")
    with open(path, mode='w', encoding='utf-8') as file:
        json.dump(json_data, file, indent=4, ensure_ascii=False)
    print(f"[INFO]: Data for auction {auction_id} saved as CSV in {auction_folder}.")


# Процедура получения данных для страницы аукциона
async def process_auction_page(auction_id):
    ''' Локальные переменные для функции '''
    print(f"[INFO]: Processing auction with ID: {auction_id}")
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}{auction_id}")
    if response.status_code == 200:
        try:
            data = response.json()
            files = data.get("files", [])
            auction_folder = "downloaded_files" + str(auction_id)
            if not os.path.exists(auction_folder):
                os.makedirs(auction_folder)
            for file in files:
                print()
                a = await save_to_txt(auction_folder, file["name"], auction_folder, auction_id)
            flattened_data = flatten_json(data)
            download_json(flattened_data, auction_folder, auction_id)
        except json.JSONDecodeError:
            print(f"[ERROR]: Invalid answer from auction {auction_id}. The response is not valid JSON.")
    else:
        print(f"[ERROR]: Failed to fetch data for auction {auction_id}. Status code: {response.status_code}")


async def main():
    # may be modified for async parsing
    await process_auction_page(9864533)
    print("[INFO]: Processing completed.")


if __name__ == "__main__":
    asyncio.run(main())
