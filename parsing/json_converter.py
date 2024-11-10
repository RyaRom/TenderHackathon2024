import json

import os


def concatenate_txt_files(directory):
    return ''.join(open(os.path.join(directory, f), 'r', encoding='utf-8').read()
                   for f in os.listdir(directory)
                   if f.endswith('.txt') and os.path.isfile(os.path.join(directory, f)))


def pt1_check(id):
    # 1.	Наименование закупки в интерфейсе полностью совпадает с наименованием в техническом задании и/или в проекте контракта.
    with open(f'test/response_{id}.json',encoding='utf-8') as js:
        dict = json.load(js)
        #print(dict['name'])
        combined_text=concatenate_txt_files('test/')
        #print(combined_text)
        prompt = f'Проверь, находится ли наименование "{dict["name"]}" в файле. Сначала выведи то, чем этот файл является: техническим заданием(выведи "ТЗ" И НИЧЕГО БОЛЬШЕ).\nВот они в едином txt-файле: {combined_text}.\nЕсли наименование содержится точно также, как я тебе описал - выведи ТОЛЬКО то, что нашло И НИЧЕГО БОЛЬШЕ, если содержится что-то очень не похожее - выведи "No matches" И НИЧЕГО БОЛЕЕ'
        return prompt
def pt2_check(id):
    #2.	Если в интерфейсе КС в поле «Обеспечение исполнения контракта» установлено значение «Требуется», то данное требование должно быть указано в техническом задании и/или в проекте контракта.
    with open(f'test/response_{id}.json',encoding='utf-8') as js:
        dict = json.load(js)
        prompt = f'{dict["isContractGuaranteeRequired"]}'

def pt3_check(id):
    #3.	Если в интерфейсе КС нет поля «Наличие сертификатов/лицензий», то данное требование не предусмотрено закупкой и его в прикрепленных файлах быть не может
    # ИЛИ
    # Если в интерфейсе КС есть поле «Наличие сертификатов/лицензий» с перечислением значений в нем, то данное требование (наименование документов) должно быть в проекте контракта или в техническом задании.
    with open(f'test/response_{id}.json',encoding='utf-8') as js:
        dict = json.load(js)
        prompt = f'{dict["isLicenseProduction"]}'
def pt4_check(id):
    #4.	В карточке КС в разделе «График поставки» значение должно соответствовать значению в проекте контракта и/или в техническом задании
    # И
    # В карточке КС в разделе «Этап поставки» значение должно соответствовать значению в проекте контракта и/или в техническом задании
    with open(f'test/response_{id}.json',encoding='utf-8') as js:
        dict = json.load(js)
        prompt = f'{dict["deliveriers"]}'
        #todo: учесть в промпте то, что скармливается вложенный dict
def pt5_check(id):




print(pt1_check(9869958))