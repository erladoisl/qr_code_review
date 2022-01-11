# Модуль, где импортируется модель для получения ответов на вопросы по тексту
# Для получения характеристик нужно вызвать answer()

from transformers.pipelines import pipeline
from transformers import Pipeline
from typing import Dict
import traceback, logging

logging.basicConfig(filename="logging.log", level=logging.INFO)

nlp = None

model_name = "phiyodr/bart-large-finetuned-squad2"

def get_model() -> Pipeline:
    '''
        Возвращает модель для распознавания текста
        Вернуть значение pipeline(), первым аргументом передать 'question-answering', в качестве model и tokenizer передать model_name
    '''
    global nlp 

    if nlp is None:
        nlp = pipeline('question-answering', model = model_name, tokenizer = model_name)
    
    return nlp


def answer(question: str, context: str) -> Dict[str, str]:
    '''
        Возвращает ответ на вопрос из текста
        Формирует словарь с ключами question и context, в качестве значений берет значения одноименных переменных
        Получить модель get_model() 
        Вызвать ее, передавав аргументом сформированный словарь, и вернуть полученное зачение
        >>> answer('What are the bad things of  product_name?', " Acer B296CL Editors' Choice See It $209.. 00 Solid color and grayscale performance... Mediocre vertical viewing angle")['answer']
        'Mediocre vertical viewing angle'
    '''

    result: Dict[str, str] = {'score': '-1.0', 'answer': ''}

    if question == '' or context == '':
        logging.error(f'Error(Empty question or context) while getting answer by the text: "{context}" and question: "{question}"')
    else:
        dic = {"question": question, "context": context}

        while float(result['score']) == -1.0:
            try:
                result = get_model()(dic)
                result['text'] = context
            except:
                logging.error(f'Error while getting answer by the text: {context} and question: {question} \n{traceback.format_exc()}')

    return result