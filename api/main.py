import os
import logging
from dotenv import load_dotenv

from flask import Flask, jsonify, render_template, request

from langchain.prompts import ChatPromptTemplate
from langchain.prompts import HumanMessagePromptTemplate
from langchain.prompts import PromptTemplate
from langchain.chat_models import GigaChat
from langchain.chains import LLMChain
from langchain.chains.summarize import load_summarize_chain
from langchain.document_loaders import WebBaseLoader
from langchain.schema.messages import HumanMessage, SystemMessage
from langchain.text_splitter import RecursiveCharacterTextSplitter

import json
import re

app = Flask(__name__)
load_dotenv()
CREDENTIALS = os.getenv('GIGACHAT_CREDENTIALS')
giga = GigaChat(credentials=CREDENTIALS, verify_ssl_certs=False)
logger = logging.getLogger(__name__)

@app.route('/')
def hello_world():
    return 'Hello World!'

@app.route("/prompt_text", methods=['POST'])
def prompt_text():
    data = request.get_json()
    if data is None:
        return jsonify({ 'error': 'Missing input' }), 400
    
    map_prompt = data.get('map_prompt', 0)
    combine_prompt = data.get('combine_prompt', 0)
    text = data.get('text', 0)

    num_tokens = giga.get_num_tokens(text)
    logger.info(f'Num tokens: {num_tokens}')
    text = re.sub(' +', ' ', text)
    text = text.replace("\n", "")
    #text = text.replace("�", "")
    text_splitter = RecursiveCharacterTextSplitter(separators=["\n\n", "\n", "."], chunk_size=10000, chunk_overlap=500)
    splitted_text = text_splitter.create_documents([text])
    logger.info(f'Num texts: {len(splitted_text)}')


    map_prompt_template = PromptTemplate(template=map_prompt, input_variables=["text"])
    combine_prompt_template = PromptTemplate(template=combine_prompt, input_variables=["text"])
    summary_chain = load_summarize_chain(llm=giga,
                                     chain_type='map_reduce',
                                     map_prompt=map_prompt_template,
                                     combine_prompt=combine_prompt_template,
#                                      verbose=True
                                    )
    result = summary_chain.run(splitted_text)

    response = {
        'prompted_text': result,
    }
    
    logger.info(f'RESPONSE: {response}')
    return json.dumps(response, ensure_ascii=False)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
