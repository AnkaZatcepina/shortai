import logging
import re
import requests
from bs4 import BeautifulSoup


logger = logging.getLogger(__name__)

def parse_url_to_file(url: str, user_id: str)->bool:
    
    text = get_web_page(url)
    if text == None:
        return False
    
    output = ''
    blacklist = [
        '[document]',
        'noscript',
        'header',
        'html',
        'meta',
        'head', 
        'input',
        'script',
        # there may be more elements you don't want, such as "style", etc.
    ]

    for t in text:
        if t.parent.name not in blacklist:
            output += '{} '.format(t)

   
    output_without_multyspaces = re.sub(' +', ' ', output)
    output_without_multyspaces_and_new_lines = output_without_multyspaces.replace("\n", "")

    
    return save_text_to_storage(output_without_multyspaces_and_new_lines, user_id)

def get_web_page(url) -> str | None:
    
    logger.info(url)
    
    print(id(logger))
    try:
        response = requests.get(url, timeout = (10, 10))
        print(response.status_code)
    except requests.exceptions.Timeout:
        return None
    except requests.exceptions.RequestException as e:
        return None
    soup = BeautifulSoup(response.content, 'html.parser')
    text = soup.find_all(string=True)
    return text

def save_text_to_storage(text: str, user_id: str)->bool:
    #print(text)
    if len(text) <= 0:
        return False
    filename = f'./storage/current_text_{user_id:}.txt'
    logger.info(filename)
    try:
        with open(filename, mode='w', encoding='utf-8') as file:
            file.write(text)
    except:
        print('Ошибка сохранения файла')
        return False        
    return True

