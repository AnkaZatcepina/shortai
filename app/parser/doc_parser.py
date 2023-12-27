import os
import re
import logging
from spire.doc import *
from spire.doc.common import *
from langchain.document_loaders import PyPDFLoader


logger = logging.getLogger(__name__)

def parse_document_to_file(filename: str, user_id: str)->bool:
    _, extension = os.path.splitext(filename)
    extension = extension.lower()
    logger.info(extension)
    new_filename = f'./storage/current_text_{user_id}.txt'     
    logger.info(f'{filename} -->>> {new_filename}')
    match extension:
        case ".txt":
            return rename_file(filename, new_filename)
        case ".pdf":
            return convert_pdf_to_txt(filename, new_filename)
        case ".doc" | ".docx":
            return convert_doc_to_txt(filename, new_filename)
        case _:
            return False
      
    return False

def rename_file(filename: str, new_filename: str) -> bool: 
    os.rename(filename, new_filename)     
    return True

def convert_doc_to_txt(filename: str, new_filename: str) -> bool:   
    document = Document()
    document.LoadFromFile(filename)
    document.SaveToFile(new_filename, FileFormat.Txt)
    document.Close()
    return True

def convert_pdf_to_txt(filename: str, new_filename: str) -> bool:   
    loader = PyPDFLoader(filename)
    logger.info(loader)
    pages = loader.load_and_split()
    logger.info(pages)

    text = " ".join(page.page_content for page in pages)
    logger.info(text)
    try:
        with open(new_filename, mode='w', encoding='utf-8') as file:
            file.write(text)
    except:
        print('Ошибка сохранения файла')
        return False
    return True

def clean_file(filename: str):
    with open(filename, 'r') as file:
        lines = file.readlines()
        text = ' '.join(lines)
 
    text_without_multyspaces = re.sub(' +', ' ', text)
    text_without_multyspaces_and_new_lines = text_without_multyspaces.replace("\n", "")

    with open(filename, 'w') as file:
        file.write(text_without_multyspaces_and_new_lines)
    