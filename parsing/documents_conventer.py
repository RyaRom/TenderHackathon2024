import pdfplumber
from docx import Document
import os
import win32com.client

def pdf_to_txt(pdf_path, txt_path):
    """Функция для конвертации PDF в текстовый файл."""
    with pdfplumber.open(pdf_path) as pdf:
        with open(txt_path, 'w', encoding='utf-8') as txt_file:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    txt_file.write(text)

def docx_to_txt(docx_path, txt_path):
    """Функция для конвертации DOCX в текстовый файл."""
    doc = Document(docx_path)
    with open(txt_path, 'w', encoding='utf-8') as txt_file:
        for para in doc.paragraphs:
            txt_file.write(para.text + '\n')

def doc_to_txt(doc_path, txt_path):
    """Функция для конвертации DOC в текстовый файл (для Windows)."""
    word = win32com.client.Dispatch("Word.Application")
    doc = word.Documents.Open(doc_path)
    doc.SaveAs(txt_path, 2)  # Формат 2 соответствует .txt
    doc.Close()
    word.Quit()

def convert_to_txt(input_path, output_path):
    """Функция для конвертации PDF, DOC, DOCX в TXT в зависимости от типа файла."""
    file_extension = os.path.splitext(input_path)[1].lower()

    if file_extension == '.pdf':
        pdf_to_txt(input_path, output_path)
    elif file_extension == '.docx':
        docx_to_txt(input_path, output_path)
    elif file_extension == '.doc':
        doc_to_txt(input_path, output_path)
    else:
        raise ValueError(f"Не поддерживаемый формат: {file_extension}")

if __name__ == '__main__':
    # Пример использования:
    # Преобразование PDF в TXT
    pdf_path = "test/Проектдоговора.pdf"
    txt_path = "test/Проектдоговора.txt"
    convert_to_txt(pdf_path, txt_path)
    
    # Преобразование DOCX в TXT
    docx_path = "test/ТЗканц.docx"
    txt_path = "test/ТЗканц.txt"
    convert_to_txt(docx_path, txt_path)

    # Преобразование DOC в TXT (на Windows)
    # doc_path = "input.doc"
    # txt_path = "output.txt"
    # convert_to_txt(doc_path, txt_path)
