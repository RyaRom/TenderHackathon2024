import os
from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer


class File:
    USABLE_SIGNATURES = ["pdf", "txt", "doc", "docx", "xls", "xlsx"]

    def read_pdf(self):
        # Создаём словарь для извлечения текста из каждого изображения
        text_result = {}
        # Извлекаем страницы из PDF
        for number, page in enumerate(extract_pages(self.filename)):
            # Находим все элементы
            page_elements = [(element.y1, element) for element in page._objs]
            # Сортируем все элементы по порядку нахождения на странице
            page_elements.sort(key=lambda a: a[0], reverse=True)
            page_text = []
            # Находим элементы, составляющие страницу
            for i, elem in enumerate(page_elements):
                # Проверяем, является ли элемент текстовым
                if isinstance(elem[1], LTTextContainer):
                    # Добавляем текст каждой строки к тексту страницы
                    page_text.append(elem[1].get_text())
            # Добавляем список списков как значение ключа страницы
            text_result[number] = [page_text]
        return [''.join(text_result[i][0]) for i in text_result.keys()]

    def read_data(self):
        if self.signature == "pdf":
            return self.read_pdf()
        elif self.signature == "doc" or self.signature == "docx":
            pass
        elif self.signature == "xls" or self.signature == "xlsx":
            pass
        else:
            f = open(self.filename, "rb")
            return f.readlines()

    def make_signature(self):
        temp = self.filename.split(".")
        for i in temp:
            if i in self.USABLE_SIGNATURES:
                return i
        return "txt"

    def __init__(self, filename, signature="NULL_FILE_SIGNATURE"):
        is_exist = os.path.exists(filename)
        if is_exist:
            self.filename = str(filename).lower()
            self.signature = str(signature).lower()
            if signature == "NULL_FILE_SIGNATURE":
                self.signature = self.make_signature()
            else:
                if self.signature not in self.USABLE_SIGNATURES:
                    self.signature = self.make_signature()
            self.data = self.read_data()
        else:
            print("[ERROR] ФАЙЛ НЕ ДОСТУПЕН. СОЗДАНИЕ КОНСТРУКТОРА ОСТАНОВЛЕНО.")