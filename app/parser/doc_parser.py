"""
    Модуль парсинга разных видов файлов
"""

import os
import re
import logging
from spire.doc import *
from spire.doc.common import *
from langchain.document_loaders import PyPDFLoader
import codecs
import chardet

logger = logging.getLogger(__name__)


def parse_document_to_file(filename: str, user_id: str)->bool:    
    """Преобразование файла в txt"""

    _, extension = os.path.splitext(filename)
    extension = extension.lower()
    logger.info(extension)
    new_filename = f'./storage/current_text_{user_id}.txt'     
    logger.info(f'{filename} -->>> {new_filename}')
    match extension:
        case ".txt":
            return save_txt(filename, new_filename)
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


def save_txt(filename: str, new_filename: str) -> bool:     
    """Сохранение txt-файла в кодировке utf-8"""

    try:
        #read input file
        logger.info(f'filename: {filename}')
        
        with open(filename, 'rb') as opened_file:
            bytes_file = opened_file.read()
            chardet_data = chardet.detect(bytes_file)
            fileencoding = (chardet_data['encoding'])
            logger.info(f'fileencoding {fileencoding}')
        if fileencoding == 'windows-1251':
            with codecs.open(filename, 'r', encoding = 'cp1251') as file:
                lines = file.read()
            with codecs.open(new_filename, 'w', encoding = 'utf-8') as file:
                file.write(lines)
        else:
            os.rename(filename, new_filename)       
    except:
        print('Ошибка сохранения файла')
        return False
    return True 


def convert_doc_to_txt(filename: str, new_filename: str) -> bool:   
    """Преобразование Word-документа в txt"""

    document = Document()
    document.LoadFromFile(filename)
    document.SaveToFile(new_filename, FileFormat.Txt)
    document.Close()
    return True

def convert_pdf_to_txt(filename: str, new_filename: str) -> bool:  
    """Преобразование PDF-документа в txt"""  

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
    """Очистка текстового файл от лишних пробелов"""
    
    with open(filename, 'r') as file:
        lines = file.readlines()
        text = ' '.join(lines)
 
    text_without_multyspaces = re.sub(' +', ' ', text)
    text_without_multyspaces_and_new_lines = text_without_multyspaces.replace("\n", "")

    with open(filename, 'w') as file:
        file.write(text_without_multyspaces_and_new_lines)
    