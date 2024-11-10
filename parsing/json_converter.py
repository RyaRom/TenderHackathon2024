import json
import os
import aiohttp
import asyncio


async def send_request(session, user_prompt, system_prompt="", max_tokens=100):
    try:
        async with session.post('http://localhost:8080/generate', json={"system_prompt": system_prompt, "user_prompt": user_prompt, "max_tokens": max_tokens}) as response:
            response.raise_for_status()  # Вызывает ошибку для статусов, не относящихся к 2xx
            return await response.json()
    except aiohttp.ClientError as e:
        print(f"Запрос не удался: {e}")
        return None  # Или обработка ошибки по-другому


def split_text_by_sentences(text, max_length=2048):
    sentences = text.split('. ')
    chunks = []
    current_chunk = ''

    for sentence in sentences:
        # Добавляем предложение в текущую часть, если позволяет длина
        if len(current_chunk) + len(sentence) + 1 <= max_length:
            current_chunk += (sentence + '. ')
        else:
            chunks.append(current_chunk.strip())
            current_chunk = sentence + '. '

    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks



def extract_txt_files_to_list(directory_path):
    txt_files_content = []
    # Перебор всех файлов в указанной папке
    for filename in os.listdir(directory_path):
        if filename.endswith('.txt'):
            file_path = os.path.join(directory_path, filename)
            with open(file_path, 'r', encoding='utf-8') as file:
                file_content = file.read()
                txt_files_content.append(file_content)
    return txt_files_content


async def process_text_and_send_requests(text, system_prompt,max_tokens):
    chunks = split_text_by_sentences(text)
    async with aiohttp.ClientSession() as session:
        tasks = []
        for user_prompt in chunks:
            tasks.append(send_request(session, system_prompt=system_prompt,user_prompt=user_prompt,max_tokens=max_tokens))
        responses = await asyncio.gather(*tasks)
        return responses

def pt1_check(id):
    # 1.	Наименование закупки в интерфейсе полностью совпадает с наименованием в техническом задании и/или в проекте контракта.
    with open(f'test/response_{id}.json', encoding='utf-8') as js:
        dict = json.load(js)
        files = extract_txt_files_to_list('test')
        prompt = f"""
        Вам дан документ в виде строки текста, а также название государственной закупки. Ваша задача — найти упоминание данного названия в каждом из документов, если оно там присутствует, и выполнить сравнение. На выходе верните результаты в стандартизированном формате для программной обработки.

        Входные данные:
        1. Название госзакупки: {dict['name']}"""+"""

        Шаги для выполнения задачи:
        1. Найдите в каждом документе название госзакупки, полностью совпадающее с данными во входных данных.
        2. Если найдено полное совпадение названия госзакупки в каждом документе, укажите его в выходных данных как «Совпадение».
        3. Если совпадение частичное или название присутствует в разных вариациях, укажите его как «Частичное совпадение» и приведите найденное название из каждого документа.
        4. Если совпадение не обнаружено, укажите его как «Не найдено».

        Выходной формат (JSON):
        Верните данные в следующем формате:

        {
        "search_term": "[Название госзакупки]",
          "results": {
        "document_1": {
        "status": "[Совпадение | Частичное совпадение | Не найдено]",
              "found_text": "[Текст из документа 1, если частичное совпадение или совпадение]"
            },
            "document_2": {
        "status": "[Совпадение | Частичное совпадение | Не найдено]",
              "found_text": "[Текст из документа 2, если частичное совпадение или совпадение]"
            }
          }
        }
        """
        return process_text_and_send_requests(text=files[0],system_prompt=prompt,max_tokens=200)


def pt2_check(id):
    # 2.	Если в интерфейсе КС в поле «Обеспечение исполнения контракта» установлено значение «Требуется», то данное требование должно быть указано в техническом задании и/или в проекте контракта.
    with open(f'test/response_{id}.json', encoding='utf-8') as js:
        dict = json.load(js)
        prompt = f'{dict["isContractGuaranteeRequired"]}'
        print(prompt)


def pt3_check(id):
    # 3.	Если в интерфейсе КС нет поля «Наличие сертификатов/лицензий», то данное требование не предусмотрено закупкой и его в прикрепленных файлах быть не может
    # ИЛИ
    # Если в интерфейсе КС есть поле «Наличие сертификатов/лицензий» с перечислением значений в нем, то данное требование (наименование документов) должно быть в проекте контракта или в техническом задании.
    with open(f'test/response_{id}.json', encoding='utf-8') as js:
        dict = json.load(js)
        prompt = f'{dict["isLicenseProduction"]}'


def pt4_check(id):
    # 4.	В карточке КС в разделе «График поставки» значение должно соответствовать значению в проекте контракта и/или в техническом задании
    # И
    # В карточке КС в разделе «Этап поставки» значение должно соответствовать значению в проекте контракта и/или в техническом задании
    with open(f'test/response_{id}.json', encoding='utf-8') as js:
        dict = json.load(js)
        prompt = f'{dict["deliveriers"]}'
        # todo: учесть в промпте то, что скармливается вложенный dict


# def pt5_check(id):


print(asyncio.run(pt1_check(9864533)))
# send_request("hello", "Translate to russian", 50)