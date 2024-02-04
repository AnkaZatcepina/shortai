
"""
    Модуль анализа текста пользователя, разные промпты
"""
import os
import logging
from dotenv import load_dotenv
from langchain.prompts import ChatPromptTemplate
from langchain.prompts import HumanMessagePromptTemplate
from langchain.prompts import PromptTemplate
from langchain.chat_models import GigaChat
from langchain.chains import LLMChain
from langchain.chains.summarize import load_summarize_chain
from langchain.document_loaders import WebBaseLoader
from langchain.schema.messages import HumanMessage, SystemMessage
from langchain.text_splitter import RecursiveCharacterTextSplitter
import nest_asyncio

import re
import requests
import json

logger = logging.getLogger(__name__)

nest_asyncio.apply()

load_dotenv()
CREDENTIALS = os.getenv('GIGACHAT_CREDENTIALS')
API_URL = os.getenv('API_URL')
giga = GigaChat(credentials=CREDENTIALS, verify_ssl_certs=False)

def get_file(user_id: str)-> str | None:
    filename = f'./storage/current_text_{user_id}.txt'
    try:
        with open(filename, mode='r', encoding='utf-8') as file:
            text = ' '.join(file.readlines())
        return text    
    except:
        return None  
    
def make_request(prompt_template: str, combine_prompt: str, text: str):
    json_request = { 'map_prompt' :  prompt_template, 'combine_prompt':  combine_prompt, 'text': text}
    response = requests.post(f'{API_URL}/prompt_text', json=json_request)
    logger.info(f'STATUS {response.status_code}')
    content_type = response.headers['Content-Type']
    logger.info(f'CONTENT TYPE {content_type}')  
    if content_type == 'text/html; charset=utf-8':
        return json.loads(response.text) 
    raise ValueError("Ошибка в API")    

def get_summary(user_id: str)->str:
    text = get_file(user_id)

    if not text:
        return "Извините, не получается проанализировать текст"  
    
    prompt_template = """
        Сделай краткое изложение по тексту ниже. Ничего не придумывай, только текст ниже между ``````
        Краткое изложение текста должно быть не длинее 1 страницы A4 и на русском языке.
        ```{text}```
        """
    
    combine_prompt = prompt_template
    response_dict = make_request(prompt_template, combine_prompt, text) 
    return response_dict['prompted_text']


def get_one_sentence(user_id: str)->str:
    text = get_file(user_id)
    if not text:
        return "Извините, не получается проанализировать текст"  

    prompt_template = """
        Сделай краткое изложение по тексту ниже. Ничего не придумывай, только текст ниже между ``````
        Краткое изложение текста должно быть не длинее 1 страницы A4 и на русском языке.
        ```{text}```
    """

    combine_prompt = """
        Ты писатель. Напиши аннотацию текста ниже одним предложением. Ничего не придумывай, только текст ниже между ``````
        В результате должно быть только одно предложение.
        ```{text}```
    """ 

    response_dict = make_request(prompt_template, combine_prompt, text)  
    return response_dict['prompted_text'] 

def get_theses(user_id: str)->str:
    text = get_file(user_id)
    if not text:
        return "Извините, не получается проанализировать текст"  

    prompt_template = """
        Сделай краткое изложение по тексту ниже. Ничего не придумывай, только текст ниже между ``````
        Краткое изложение текста должно быть не длинее 1 страницы A4.
        ```{text}```
    """

    combine_prompt = """
        Напиши основные тезисы текста в виде нумерованного списка. Нельзя ничего придумывать кроме информации из текста.
        Тезисы должны быть не длинее 1 страницы A4.
        ```{text}```
    """ 

    response_dict = make_request(prompt_template, combine_prompt, text)  
    return response_dict['prompted_text'] 

