import os

import docx
from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer
from docx import Document
import mammoth


import os
import docx
import subprocess
import platform
from comtypes import client

class FileHolder:
    USABLE_SIGNATURES = ["pdf", "txt", "doc", "docx", "xls", "xlsx"]

    def __init__(self, filename, signature="NULL_FILE_SIGNATURE"):
        if os.path.exists(filename):
            self.filename = filename.lower()
            self.signature = signature.lower()

            if signature == "NULL_FILE_SIGNATURE" or self.signature not in self.USABLE_SIGNATURES:
                self.signature = self.make_signature()

            self.data = self.read_data()
        else:
            raise FileNotFoundError(f"[ERROR] File '{filename}' not found. Constructor halted.")

    def make_signature(self):
        ext = self.filename.split(".")[-1]
        return ext if ext in self.USABLE_SIGNATURES else "txt"

    def convert_doc_to_docx(self):
        """Convert .doc to .docx format if necessary"""
        if platform.system() == 'Windows':
            word = client.CreateObject('Word.Application')
            doc = word.Documents.Open(self.filename)
            docx_filename = self.filename.replace(".doc", ".docx")
            doc.SaveAs(docx_filename, FileFormat=16)  # 16 represents the .docx format
            doc.Close()
            word.Quit()
        else:
            # Assuming LibreOffice is installed for non-Windows platforms
            subprocess.run(['libreoffice', '--headless', '--convert-to', 'docx', self.filename], check=True)
            docx_filename = self.filename.replace(".doc", ".docx")

        self.filename = docx_filename
        self.signature = 'docx'

    def read_docx(self):
        doc = docx.Document(self.filename)
        full_text = []
        for para in doc.paragraphs:
            full_text.append(para.text)
        return ' '.join(full_text)

    def read_pdf(self):
        try:
            text_result = {}
            for number, page in enumerate(extract_pages(self.filename)):
                page_elements = [(element.y1, element) for element in page]
                page_elements.sort(key=lambda a: a[0], reverse=True)
                page_text = []

                for _, elem in page_elements:
                    if isinstance(elem, LTTextContainer):
                        page_text.append(elem.get_text())

                text_result[number] = ''.join(page_text)

            return " ".join([text_result[i] for i in text_result.keys()])
        except Exception as e:
            raise ValueError(f"Error reading PDF file: {e}")

    def read_data(self) -> str:
        if self.signature == "pdf":
            return self.read_pdf()
        elif self.signature == "doc":
            self.convert_doc_to_docx()  # Convert .doc to .docx
            return self.read_docx()
        elif self.signature == "docx":
            return self.read_docx()
        elif self.signature in ["xls", "xlsx"]:
            # Placeholder for Excel file handling
            raise NotImplementedError(f"Reading Excel files ('{self.signature}') is not implemented yet.")
        else:
            try:
                with open(self.filename, "r", encoding="utf-8") as f:
                    return f.read()
            except Exception as e:
                raise ValueError(f"Error reading text file: {e}")
