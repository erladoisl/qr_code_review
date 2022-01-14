# Модуль для получения содержимого qr-кода со страницы пдф файла или картинки
# Вызвать метод parse_file_with_qr_code(), аргумент - название файла

import logging
import os
from PIL import Image
from pyzbar.pyzbar import decode
from pdf2image import convert_from_path

logging.basicConfig(filename="logging.log", level=logging.INFO)


def get_text_from_qr_code(pil_image):
    '''
        Возвращает текст из qr-кода

        >>> get_text_from_qr_code(Image.open('data\doctest\qr_code_cutted(2).jpg'))
        'https://www.gosuslugi.ru/covid-cert/verify/9160000018951163?lang=ru&ck=198310ac93c58daab87590afc2aa3f95'
        >>> get_text_from_qr_code(Image.open('data\doctest\qr_code_cutted.jpg'))
        'https://www.gosuslugi.ru/covid-cert/status/68a72008-53b4-461d-a26b-ad0c5fc4353c?lang=ru'
        >>> get_text_from_qr_code(Image.open('data\doctest\certificate_covid.jpg'))
        'https://www.gosuslugi.ru/covid-cert/verify/9160000018951163?lang=ru&ck=198310ac93c58daab87590afc2aa3f95'
    '''
    data = decode(pil_image)
    res = ''
    
    if len(data) > 0:
        res = data[0].data.decode()
        logging.info(f'Текст из qr-кода: {res}')
    else:
        logging.info('Не обнаружен qr-код')

    return res


def parse_file_with_qr_code(file_name: str):
    '''
        Из файла-картинки или пдф файла возвращает текст из qr-кода

        >>> parse_file_with_qr_code('data\certifacates\\\\antitela\\\\470a5799085306cd3020ad5ed44ce2aa.pdf')
        'https://www.gosuslugi.ru/covid-cert/verify/8161092133559674?lang=ru&ck=036f49d5bc68826ed8a5c3f5f1a1a424'
        >>> parse_file_with_qr_code('data\certifacates\\\\revactination\\\\2ef617b77492c637464f4305cdd1b502.pdf')
        'https://www.gosuslugi.ru/covid-cert/status/e284c129-beb0-4eee-9031-78cdaef16e7a?lang=ru'
        >>> parse_file_with_qr_code('data\certifacates\\\\antitela\\\\6c1ba0866e006478db187881ea670bfc.jpg')
        'https://www.gosuslugi.ru/covid-cert/verify/8161032121616110?lang=ru&ck=96ea7ed4b8c1333bbb4445ca014709cb'
        >>> parse_file_with_qr_code('data\doctest\doc with qr-code.docx')
        ''
    '''
    if file_name.endswith('.pdf'):
        pil_image = convert_from_path(file_name)[0]
    elif file_name.split('.')[-1].lower() in ['jpg', 'jfif', 'png']:
        pil_image = Image.open(file_name)
    else:
        logging.error('Неизвестный формат файла')

        return ''
    
    return get_text_from_qr_code(pil_image)


if __name__ == '__main__':
    directory = 'data\certifacates'

    for subdir, dirs, files in os.walk(directory):
        for file in files:
            filepath = subdir + os.sep + file

            if filepath.split('.')[-1] in ['jpg', 'pdf', 'png', 'jfif', 'docx']:
                print(os.path.join(directory, filepath))
                
                print(parse_file_with_qr_code(filepath))
            else:
                print(f'Unknown file format: {filepath}')