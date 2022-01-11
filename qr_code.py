# Модуль для получения содержимого qr-кода со страницы пдф файла или картинки
# Вызвать метод parse_file_with_qr_code(), аргумент - название файла

import logging
import os
import cv2
import numpy  as np
from PIL import Image
from pyzbar.pyzbar import decode
from pdf2image import convert_from_path


# cкорее всего не нужно будет
def get_qr_code(file_name, res_file_name: str = 'data\qr.jpg') -> np.ndarray:
    '''
        Возвращает участок рисунка с qr-кодом
    
        >>> qr_code_file_name = get_qr_code('data\doctest\certificate_covid.jpg')
        >>> get_text_from_qr_code(Image.open(qr_code_file_name))
        'https://www.gosuslugi.ru/covid-cert/verify/9160000018951163?lang=ru&ck=198310ac93c58daab87590afc2aa3f95'
        >>> qr_code_file_name = get_qr_code('data\doctest\perebolel_imunizaciya.jpg')
        >>> get_text_from_qr_code(Image.open(qr_code_file_name))
        'https://www.gosuslugi.ru/covid-cert/status/68a72008-53b4-461d-a26b-ad0c5fc4353c?lang=ru'
    '''
    # Load imgae, grayscale, Gaussian blur, Otsu's threshold
    image = cv2.imread(file_name)
    original = image.copy()
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (9,9), 0)
    thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

    # Morph close
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5,5))
    close = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel, iterations=2)

    # Find contours and filter for QR code
    cnts = cv2.findContours(close, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]

    for c in cnts: 
        approx = cv2.approxPolyDP(c, 0.04 * cv2.arcLength(c, True), True)
        x,y,w,h = cv2.boundingRect(approx)
        ar = w / float(h)

        if len(approx) == 4 and cv2.contourArea(c) > 10000 and (ar > .85 and ar < 1.3):
            cv2.rectangle(image, (x, y), (x + w, y + h), (36,255,12), 3)
            ROI = original[y - 10:y + h + 10, x  - 10:x + w + 10]
            # cv2.imshow('ROI', ROI)
            cv2.imwrite(res_file_name, ROI)
            # cv2.waitKey()  

    return res_file_name


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


def get_image(file_name: str):
    '''
        Возвращает картинку первой страницы в пдф файле

        >>> img = get_image('data\doctest\certificate_covid.pdf')
        >>> get_text_from_qr_code(img)
        'https://www.gosuslugi.ru/covid-cert/verify/9160000018951163?lang=ru&ck=198310ac93c58daab87590afc2aa3f95'
    '''
    return convert_from_path(file_name)[0]


def parse_file_with_qr_code(file_name: str):
    '''
        Из файла-картинки или пдф файла возвращает текст из qr-кода

        >>> parse_file_with_qr_code('data\certifacates\\\\antitela\\\\470a5799085306cd3020ad5ed44ce2aa.pdf')
        'https://www.gosuslugi.ru/covid-cert/verify/8161092133559674?lang=ru&ck=036f49d5bc68826ed8a5c3f5f1a1a424'
        >>> parse_file_with_qr_code('data\certifacates\\\\revactination\\\\2ef617b77492c637464f4305cdd1b502.pdf')
        'https://www.gosuslugi.ru/covid-cert/status/e284c129-beb0-4eee-9031-78cdaef16e7a?lang=ru'
        >>> parse_file_with_qr_code('data\certifacates\\\\antitela\\\\6c1ba0866e006478db187881ea670bfc.jpg')
        'https://www.gosuslugi.ru/covid-cert/verify/8161032121616110?lang=ru&ck=96ea7ed4b8c1333bbb4445ca014709cb'
        >>> parse_file_with_qr_code('data\certifacates\\\\antitela\\\\217b1355df7962f073ec7ee59b7e704d.jfif')
        'https://www.gosuslugi.ru/covid-cert/verify/8161082131159530?lang=ru&ck=eb757f1207bfce6b8b98e38eac16741d'
    '''
    if file_name.endswith('.pdf'):
        pil_image = convert_from_path(file_name)[0]
    elif file_name.split('.')[-1] in ['jpg', 'jfif', 'png']:
        pil_image = Image.open(file_name)
    else:
        logging.error('Неизвестный формат файла')

        return ''
    
    return get_text_from_qr_code(pil_image)


if __name__ == '__main__':
    print(parse_file_with_qr_code('data\certifacates\\antitela\\6c1ba0866e006478db187881ea670bfc.jpg'))