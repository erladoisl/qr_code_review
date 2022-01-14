# 1. Из текста определяет ФИО и срок действия справки
# 2. По ссылке на госуслуги возвращает дату рождения, инициалы и срок действия вакцины или иммунитета

from typing import Dict
import requests
import logging
import traceback
import modules.qr_code as qr_code
from modules.config import api_url_verify, api_url_status

logging.basicConfig(filename="logging.log", level=logging.INFO, encoding='utf-8')


def get_api_url(url: str) -> str:
    '''
        В зависимости от ссылки формирует и возвращает ссылку для запроса api

        >>> get_api_url('https://www.gosuslugi.ru/covid-cert/verify/XXX')
        'https://www.gosuslugi.ru/api/covid-cert/v3/cert/check/XXX'
        >>> get_api_url('https://www.gosuslugi.ru/covid-cert/status/XXX')
        'https://www.gosuslugi.ru/api/covid-cert-checker/v3/cert/status/XXX'
        >>> get_api_url('https://www.gosuslugi.ru/covid-cert/XXX')
        'https://www.gosuslugi.ru/covid-cert/XXX'
    '''
    try:
        if url.split('/')[-2] == 'verify':
            url = f'{api_url_verify}{url.split("/")[-1]}'
        elif url.split('/')[-2] == 'status':
            url = f'{api_url_status}{url.split("/")[-1]}'
        else:
            raise Exception
    except:
        logging.error(f'Unknown url format: {url}')
    finally:
        return url


def get_vactination_info(url: str) -> Dict[str, str]:
    '''
        Возвращает Инициалы, до какого числа действует и дату рождения

        >>> get_vactination_info('https://www.gosuslugi.ru/covid-cert/verify/9160000018951163?lang=ru&ck=198310ac93c58daab87590afc2aa3f95')
        {'title': 'Сертификат вакцинации от COVID-19', 'expiredAt': '08.07.2022', 'ФИО': 'Л******* Р***** Н********', 'Дата рождения': '18.06.1994', 'Паспорт': '92** ***711'}
        >>> get_vactination_info('https://www.gosuslugi.ru/covid-cert/status/68a72008-53b4-461d-a26b-ad0c5fc4353c?lang=ru')
        {'title': 'Сертификат COVID-19', 'expiredAt': '12.08.2022', 'ФИО': 'А*********** Г****** С********', 'Дата рождения': '02.06.1966', 'Паспорт': '92** ***640'}
        >>> get_vactination_info('wrong_url')
        {}
    '''
    res = {}
    status_code = -1
    api_url = get_api_url(url)
    try:
        response = requests.get(api_url)
        status_code = response.status_code
    except:
        logging.error(f'Cannot get response from url: {api_url}')

    if status_code == 200:
        try:
            response_json = response.json()
            data = response_json.get('items', {})[0] if 'items' in response_json.keys() else response_json

            res['title'] = data.get('title', '')
            res['expiredAt'] = data.get('expiredAt', '')

            for attr in data.get('attrs', {}):
                res[attr.get('title', 'undefind')] = attr.get('value')
        except:
            logging.ERROR(f'Unable to get data from json {response_json}\n{traceback}')

    return res


def is_valid_qr_code(url: str) ->  bool:
    '''
        Если url начинается с "https://www.gosuslugi.ru/", текст из qr-кода считается валидным

        >>> is_valid_qr_code('https://www.gosuslugi.ru/covid-cert/verify/9160000018951163?lang=ru&ck=198310ac93c58daab87590afc2aa3f95')
        True
        >>> is_valid_qr_code('')
        False
    '''
    return url.startswith('https://www.gosuslugi.ru/')


def parse_document(file_name: str) -> Dict[str, str]:
    '''
        Возвращает:
            фио владельца
            дата рождения владельца
            дата окончания действия
    '''
    url_from_qr_code = qr_code.parse_file_with_qr_code(file_name)
    result = {}

    if is_valid_qr_code(url_from_qr_code):
        try:
            result = get_vactination_info(url_from_qr_code)
        except:
            logging.ERROR(f'Error while getting response by url:{url_from_qr_code} from the file {file_name}')
    else:
        logging.info('Unable to get url from QR-code')

    logging.info(f'Result: {result}')

    return result


if __name__ == '__main__':
    import os
    directory = 'data\certifacates'

    for subdir, dirs, files in os.walk(directory):
        for file in files:
            #print os.path.join(subdir, file)
            filepath = subdir + os.sep + file

            if filepath.split('.')[-1] in ['jpg', 'pdf', 'png', 'jfif', 'docx']:
                logging.info(f'Cur document: {os.path.join(directory, filepath)}')
                
                res = parse_document(filepath)
                print(os.path.join(directory, filepath))
                
                print(res)
                logging.info(f'RESULT: {res}')
            else:
                print(f'Unknown file format: {filepath}')