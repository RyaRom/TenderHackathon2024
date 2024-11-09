import os
from pdfminer.high_level import extract_pages, extract_text
from pdfminer.layout import LTTextContainer, LTChar, LTRect, LTFigure
import PyPDF2
import pdfplumber


class MYFILE:
    USABLE_SIGNATURES = ["pdf", "txt", "doc", "docx", "xls", "xlsx"]

    def text_extraction(self, element):
        # Извлекаем текст из вложенного текстового элемента
        line_text = element.get_text()

        # Находим форматы текста
        line_formats = []
        for text_line in element:
            if isinstance(text_line, LTTextContainer):
                # Итеративно обходим каждый символ в строке текста
                for character in text_line:
                    if isinstance(character, LTChar):
                        # Добавляем к символу название шрифта
                        line_formats.append(character.fontname)
                        # Добавляем к символу размер шрифта
                        line_formats.append(character.size)
        # Находим уникальные размеры и названия шрифтов в строке
        format_per_line = list(set(line_formats))

        # Возвращаем кортеж с текстом в каждой строке вместе с его форматом
        return (line_text, format_per_line)

    def read_pdf(self):
        # создаём объект файла PDF
        f = open(self.filename, 'rb')
        # создаём объект считывателя PDF
        pdf = PyPDF2.PdfReader(f)
        # Создаём словарь для извлечения текста из каждого изображения
        text_result = {}
        # Извлекаем страницы из PDF
        for number, page in enumerate(extract_pages(self.filename)):

            # текст со страницы
            page_text = []
            line_format = []
            text_from_tables = []
            page_content = []
            # Инициализируем количество исследованных таблиц
            # table_num = 0
            # first_element = True
            table_extraction_flag = False
            # Открываем файл pdf
            # pdf = pdfplumber.open(self.filename)
            # Находим исследуемую страницу
            # page_tables = pdf.pages[pagenum]
            # Находим количество таблиц на странице
            # tables = page_tables.find_tables()

            # Находим все элементы
            page_elements = [(element.y1, element) for element in page._objs]
            # Сортируем все элементы по порядку нахождения на странице
            page_elements.sort(key=lambda a: a[0], reverse=True)

            # Находим элементы, составляющие страницу
            for i, elem in enumerate(page_elements):
                # Извлекаем элемент структуры страницы
                element = elem[1]

                # Проверяем, является ли элемент текстовым
                if isinstance(element, LTTextContainer):
                    # Проверяем, находится ли текст в таблице
                    if table_extraction_flag == False:
                        # Используем функцию извлечения текста и формата для каждого текстового элемента
                        (line_text, format_per_line) = self.text_extraction(element)
                        # Добавляем текст каждой строки к тексту страницы
                        page_text.append(line_text)
                        # Добавляем формат каждой строки, содержащей текст
                        line_format.append(format_per_line)
                        page_content.append(line_text)
                    else:
                        # Пропускаем текст, находящийся в таблице
                        pass

            # Создаём ключ для словаря
            dctkey = 'Page_' + str(number)
            # Добавляем список списков как значение ключа страницы
            text_result[dctkey] = [page_text, line_format, text_from_tables, page_content]

        # Удаляем содержимое страницы
        result = ''.join(text_result['Page_0'][4])
        f.close()
        return result

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
