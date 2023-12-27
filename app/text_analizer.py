import os
import logging
from dotenv import load_dotenv
from langchain.prompts import ChatPromptTemplate
from langchain.prompts import HumanMessagePromptTemplate
from langchain.prompts import PromptTemplate
from langchain.chat_models import GigaChat
from langchain.chains import LLMChain
from langchain.document_loaders import WebBaseLoader
from langchain.schema.messages import HumanMessage, SystemMessage
import nest_asyncio

logger = logging.getLogger(__name__)

nest_asyncio.apply()

load_dotenv()
CREDENTIALS = os.getenv('GIGACHAT_CREDENTIALS')
giga = GigaChat(credentials=CREDENTIALS, verify_ssl_certs=False)

def get_file(user_id: str)-> str | None:
    filename = f'./storage/current_text_{user_id:}.txt'
    try:
        with open(filename, mode='r', encoding='utf-8') as file:
            return file.readline()
    except:
        return None  

def get_summary(user_id: str)->str:
    text = get_file(user_id)
    if text == None:
        return "Извините, не получается проанализировать текст"  
    
    prompt_template = """
        Сделай краткое изложение по тексту ниже. Ничего не придумывай, только текст ниже между ``````
        Если текст не на русском языке, то переведи на русский язык.
        Краткое изложение текста должно быть не длинее 1 страницы A4 и на русском языке.
        Структура изложения обязательна:
            - Ключевые инсайты
            - Вывод
        ```{text}```
        """
    
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
        Ты писатель. Твоя задача написать основные тезисы по тексту ниже. Ничего не придумывай, только текст ниже между ``````
        Если текст не на русском языке, то переведи на русский язык.
        Каждый тезиз должен начинаться с новой строки с символа *.
        ```{text}```
        """
    chat_template = ChatPromptTemplate.from_messages(
        [
        SystemMessage(
            content=(
                "Ты эксперт журналист. Твоя задача написать основные тезисы статьи. Нельзя ничего придумывать, кроме информации из статьи."
            )
        ),
        HumanMessagePromptTemplate.from_template(prompt_template),
    ])
    prompt = chat_template.format_messages(text=text)
    response = giga.invoke(prompt).content
    return response