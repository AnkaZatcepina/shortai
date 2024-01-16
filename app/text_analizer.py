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

logger = logging.getLogger(__name__)

nest_asyncio.apply()

load_dotenv()
CREDENTIALS = os.getenv('GIGACHAT_CREDENTIALS')
giga = GigaChat(credentials=CREDENTIALS, verify_ssl_certs=False)

def get_file(user_id: str)-> str | None:
    filename = f'./storage/current_text_{user_id}.txt'
    try:
        with open(filename, mode='r', encoding='utf-8') as file:
            text = ' '.join(file.readlines())
        return text    
    except:
        return None  

def get_summary(user_id: str)->str:
    text = get_file(user_id)
    """#logger.info(text)
    num_tokens = giga.get_num_tokens(text)
    logger.info(f'Num tokens: {num_tokens}')
    text = re.sub(' +', ' ', text)
    text = text.replace("\n", "")
    #text = text.replace("�", "")
    text_splitter = RecursiveCharacterTextSplitter(separators=["\n\n", "\n", "."], chunk_size=10000, chunk_overlap=500)
    splitted_text = text_splitter.create_documents([text])
    logger.info(f'Num texts: {len(splitted_text)}')
    #logger.info(len(splitted_text[0]))
    #logger.info(splitted_text[2])
    #text = splitted_text[2]


    summary_chain = load_summarize_chain(llm=giga, chain_type='map_reduce',
#                                      verbose=True # Set verbose=True if you want to see the prompts being used
                                    )
    #output = summary_chain.run(splitted_text)
"""
    if text == None:
        return "Извините, не получается проанализировать текст"  
    

    
    prompt_template = """
        Сделай краткое изложение по тексту ниже. Ничего не придумывай, только текст ниже между ``````
        Краткое изложение текста должно быть не длинее 1 страницы A4 и на русском языке.
        ```{text}```
        """
    """map_prompt_template = PromptTemplate(template=prompt_template, input_variables=["text"])
    combine_prompt_template = PromptTemplate(template=prompt_template, input_variables=["text"])
    summary_chain = load_summarize_chain(llm=giga,
                                     chain_type='map_reduce',
                                     map_prompt=map_prompt_template,
                                     combine_prompt=combine_prompt_template,
#                                      verbose=True
                                    )
    response = summary_chain.run(splitted_text)"""
    
    json = { 'map_prompt' :  prompt_template, 'combine_prompt':  prompt_template, 'text': text}
    #response = web.post('/promt_text', json=json)
    #response = requests.post('http://localhost/promt_text', json=json)
    response = requests.post('http://192.168.50.8:8077/promt_text', json=json)
    #response.text.decode('utf-8')
    logger.info(f'STATUS {response.status_code}')
    content_type = {response.headers['Content-Type']}
    logger.info(f'CONTENT TYPE {content_type}')    
    logger.info(f'CONTENT1 {response.content}')    
    logger.info(f'CONTENT2 {response.content.decode("utf-8")}')    
    logger.info(f'TEXT {response.text}')  
    #logger.info(f'JSON {response.json}')
    #if content_type == {'application/json'}:
    if content_type == {'text/html; charset=utf-8'}:
        #logger.info(f'HEADERS {rv.headers['Content-Type']}')
        #result = response.json
        return response.content.decode("utf-8")
    return "Ошибка в API" 

    chat_template = ChatPromptTemplate.from_messages(
        [
        SystemMessage(
            content=(
                "Ты эксперт журналист. Твоя задача делать короткие эссе на статью. Нельзя ничего придумывать, кроме информации из статьи."
            )
        ),
        HumanMessagePromptTemplate.from_template(prompt_template),
    ])
    prompt = chat_template.format_messages(text=text)
    response = giga.invoke(prompt).content
    #prompt = PromptTemplate.from_template(prompt_template)
    #chain = LLMChain(llm=giga, prompt=prompt, verbose=True)
    #response = chain.run(text=text)
    return response

def get_one_sentence(user_id: str)->str:
    text = get_file(user_id)
    if text == None:
        return "Извините, не получается проанализировать текст"  
    
    prompt_template = """
        Ты писатель. Сделай написать смысл текста ниже одним предложением. Ничего не придумывай, только текст ниже между ``````
        Если текст не на русском языке, то переведи на русский язык.
        В результате должно быть только одно предложение.
        ```{text}```
        """
    
    chat_template = ChatPromptTemplate.from_messages(
        [
        SystemMessage(
            content=(
                "Ты эксперт журналист. Твоя задача написать смысл статьи в одном предложении. Нельзя ничего придумывать, кроме информации из статьи."
            )
        ),
        HumanMessagePromptTemplate.from_template(prompt_template),
    ])
    prompt = chat_template.format_messages(text=text)
    response = giga.invoke(prompt).content
    return response

def get_theses(user_id: str)->str:
    text = get_file(user_id)
    if text == None:
        return "Извините, не получается проанализировать текст"  
    
    prompt_template = """
        Ты писатель. Твоя задача перевести текст на русский язык и написать основные тезисы по тексту ниже. Ничего не придумывай, только текст ниже между ``````
        Тезисы должны быть написаны в виде нумерованного списка на русском языке.
        ```{text}```
        """
    chat_template = ChatPromptTemplate.from_messages(
        [
        SystemMessage(
            content=(
                "Ты эксперт журналист. Твоя задача написать основные тезисы статьи в виде нумерованного списка. Нельзя ничего придумывать, кроме информации из статьи."
            )
        ),
        HumanMessagePromptTemplate.from_template(prompt_template),
    ])
    prompt = chat_template.format_messages(text=text)
    response = giga.invoke(prompt).content
    return response