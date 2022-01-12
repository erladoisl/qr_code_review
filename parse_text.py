
# 1. Из текста определяет ФИО и срок действия справки
# 2. По ссылке на госуслуги возвращает дату рождения, инициалы и срок действия вакцины или иммунитета

from typing import Dict
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import re
import logging
import traceback
import qr_code

logging.basicConfig(filename="logging.log", level=logging.INFO, encoding='utf-8')

def get_vactination_info(text: str) -> Dict[str, str]:
    '''
        Возвращает Инициалы, до какого числа действует и дату рождения

        >>> get_vactination_info('RUS Сертификат вакцинации от COVID-19 Действителен № 9160 0000 1895 1163 Действует до: 08.07.2022 Л******* Р***** Н******** Дата рождения: 18.06.1994 Паспорт: 92** ***711 Закрыть')
        {'Тип сертификата': ' Сертификат вакцинации от COVID-19', 'ФИО': 'ЛРН', 'Дата действия': '08.07.2022', 'День рождения': '18.06.1994'}
        >>> get_vactination_info('RUS Сведения о перенесенном заболевании COVID-19 Переболел № 8161 0321 2161 6110 Дата выздоровления: 14.04.2021 Действует до: 14.04.2022 м*********** и***** Н******** Паспорт: 92** ***764 Дата рождения: 09.08.1957 Закрыть')
        {'Тип сертификата': ' Сведения о перенесенном заболевании COVID-19', 'ФИО': 'МИН', 'Дата действия': '14.04.2022', 'День рождения': '09.08.1957'}
        >>> get_vactination_info('RUS Сертификат COVID-19 Действителен № 1000 0844 1623 0689 Действует до 02.11.2022 Ц******* Е**** И******* Дата рождения: 05.08.1968 Паспорт: 92** ***293 Закрыть')
        {'Тип сертификата': ' Сертификат COVID-19', 'ФИО': 'ЦЕИ', 'Дата действия': '02.11.2022', 'День рождения': '05.08.1968'}
    '''
    res = {}

    for key, reg_exp in zip(['Тип сертификата', 'ФИО', 'Дата действия', 'День рождения'],
                   ['[А-я ]+ COVID-19',
                    '[а-я]\*{2,}',
                    'действует [до:]+ [0-9]{2}.[0-9]{2}.[0-9]{4}',
                    'дата рождения: [0-9]{2}.[0-9]{2}.[0-9]{4}']):
        
        try:
            if key == 'ФИО':
                res[key] = ''.join([i[0] for i in re.findall(reg_exp, text.lower())]).upper()
            elif key in ['Дата действия', 'День рождения']:
                res[key] = re.findall('[0-9]{2}.[0-9]{2}.[0-9]{4}', re.findall(reg_exp, text.lower())[0])[0]
            else:
                res[key] = re.findall(reg_exp, text)[0]
        except:
            logging.error(f'Error while getting {key} from the text: {text}\n{traceback}')

    return res


def get_html_text(url: str) -> str:
    '''
        Возвращает текст по ссылке url

        >>> get_html_text('https://www.gosuslugi.ru/covid-cert/verify/9160000018951163?lang=ru&ck=198310ac93c58daab87590afc2aa3f95')
        'RUS Сертификат вакцинации от COVID-19 Действителен № 9160 0000 1895 1163 Действует до: 08.07.2022 Л******* Р***** Н******** Дата рождения: 18.06.1994 Паспорт: 92** ***711 Закрыть'
        >>> get_html_text('https://www.gosuslugi.ru/covid-cert/verify/8161032121616110?lang=ru&ck=96ea7ed4b8c1333bbb4445ca014709cb')
        'RUS Сведения о перенесенном заболевании COVID-19 Переболел № 8161 0321 2161 6110 Дата выздоровления: 14.04.2021 Действует до: 14.04.2022 м*********** и***** Н******** Паспорт: 92** ***764 Дата рождения: 09.08.1957 Закрыть'
    '''
    driver = webdriver.Chrome(ChromeDriverManager().install())

    driver.get(url) # аналог страницы браузера Chrome
    driver.set_page_load_timeout(55)
    driver.maximize_window()
    driver.implicitly_wait(5)
    innerText = ' '.join([node.text for node in driver.find_elements_by_class_name("vaccine-result")])

    while '\n' in innerText:
        innerText = innerText.replace('\n', ' ')
        
    return innerText


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
        logging.info(f'URL from qr-code: {url_from_qr_code}')
        inner_text = get_html_text(url_from_qr_code)
        result = get_vactination_info(inner_text)
    else:
        logging.info('Unable to get url from QR-code')

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