
# 1. Из текста определяет ФИО и срок действия справки
# 2. По ссылке на госуслуги возвращает дату рождения, инициалы и срок действия вакцины или иммунитета

from datetime import datetime
from typing import Dict
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import re

document_type = {'vactination': 1,
                 'antitela': 2,  # болезнь перенесена или есть антитела
                 'modotvod': 3}  # приложена справка


def get_vactination_info(text: str) -> Dict[str, str]:
    '''
        Возвращает Инициалы, до какого числа действует и дату рождения

        >>> get_vactination_info('RUS Сертификат вакцинации от COVID-19 Действителен № 9160 0000 1895 1163 Действует до: 08.07.2022 Л******* Р***** Н******** Дата рождения: 18.06.1994 Паспорт: 92** ***711 Закрыть')
        {'ФИО': 'ЛРН', 'до': '08.07.2022', 'день рождения': '18.06.1994'}
        >>> get_vactination_info('RUS Сведения о перенесенном заболевании COVID-19 Переболел № 8161 0321 2161 6110 Дата выздоровления: 14.04.2021 Действует до: 14.04.2022 м*********** и***** Н******** Паспорт: 92** ***764 Дата рождения: 09.08.1957 Закрыть')
        {'ФИО': 'МИН', 'до': '14.04.2022', 'день рождения': '09.08.1957'}
    '''
    return {'ФИО': ''.join([i[0] for i in re.findall('[а-я]\*{2,}', text.lower())]).upper(), 
            'до': re.search('Действует до: [0-9]{2}.[0-9]{2}.[0-9]{4}', text)[0][14:],
            'день рождения': re.search('(Дата рождения: )[0-9]{2}.[0-9]{2}.[0-9]{4}', text)[0][15:]}


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
    driver.set_page_load_timeout(10)
    driver.maximize_window()
    driver.implicitly_wait(2)

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


def get_document_type() -> str:
    '''
        Возвращает тип документа из document_type
    '''
    pass


def get_date(text: str) -> datetime:
    '''
        Возвращает 
            1. Дату вакцианции, если вакцинирован
            2. Дату выздоровления, если перенесено заболевание covid
            3. Дату результата анализа, если тест на антитела
    '''                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      
    pass