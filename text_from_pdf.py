import logging, traceback
from pdf2image import convert_from_path
from typing import List
import config as c
import pytesseract
import fitz
import re

logging.basicConfig(filename="logging.log", level=logging.INFO)


def get_text_from_scan(filename: str, archive_uuid: str = '') -> List[str]:
    '''
        Возвращает список текстов из каждой сканированной страницы пдф
        
        Используя convert_from_path() получить список картинок - страниц из файла пдф
        Использовать tesseract получить текст с каждой картинки
        и вернуть текст с каждой страницы 
      
        >>> get_text_from_scan('docx/scan.pdf')
        ["Simple PDF File 2 ...continued from page 1. Yet more text And more text. And more text. And more text. And more text And more text. And more text. And more text Oh, how boring typing this stuff. But not as boring as watching paint dry. And more text And mote text. And more text. And more text. Bon'ng. More, a littte more text The end. and just as well.", 'A Simple PDF File This is a small demonstration .pdf file « just for use in the Virtual Mechanies Models. More text. And more text And more text. And more text. And more text. And more text. And more text And more text. And more text, And more text And more text Boring, zzzzz. And more text. And more text And more text And more text. And more text. And more text. And more text. And more text. And more text And mote text. And more text And more text. And more text. And more text And more text And more text. Even more. Continued on page 2']
    '''
    logging.info('Using tesseract')
    imgs = convert_from_path(filename)
    res: List[str] = []

    try:
        for i, img in enumerate(imgs):
            logging.info(f'Page № {i}')
            text = correct_the_text(pytesseract.image_to_string(img))
            
            res.append(text)
        logging.info('Text successfully got')
    except:
        logging.error(f'Error while gettig text from pdf, \n {traceback.format_exc()}')
    finally:
        return res


def is_valid_text(text: str) -> bool:
    '''
        Определяет, нормальные ли текст на странице определил fitz или надо определять текст с помощью tesseract
        Есть текст не пустой и в нем нет ломаных символов �, вернуть True, иначе - False
        >>> is_valid_text('Again, thank you for selecting Avalon Princeton Junction. Our entire team is dedicated to creating a community that you are proud to call home.')
        True
        >>> is_valid_text('')
        False
        >>> is_valid_text('For all other questions - ������ ���� �� �� ��� ��������� �������� Karen Echenique� �� 609-275-9577 �� ���')
        False
    '''
    return text != '' and '�' not in text


def correct_the_text(text: str) -> str:
    '''
        Удаляет лишние пробелы тексте
        Удалить одиночные переносы строк. Заменить несколько подряд идущие переносы разделителем предложения.
        Удалить переносы строк и пробелы в начале и конце
        >>> correct_the_text('Closed \\nSunday: 10:00 am to 5:00 pm \\n \\n \\n \\n \\n \\n \\n \\n \\nResident Initial \\nResident Initial \
\\nResident Initial \\nResident Initial \\nResident Initial \\nGuarantor Initial \\n \\n \\n \\nDocuSign Envelope ID: 934026A9-EE61-4591-BBBA-43719F330704\\n')
        'Closed Sunday: 10:00 am to 5:00 pm. Resident Initial Resident Initial Resident Initial Resident Initial Resident Initial \
Guarantor Initial. DocuSign Envelope ID: 934026A9-EE61-4591-BBBA-43719F330704'
    '''
    while ' \n \n \n' in text:
        text = text.replace(' \n \n \n', ' \n \n')

    text = text.strip().replace(' \n \n', '. ').replace('\n', ' ')

    return re.sub(" +", " ", text)
        

def get_text_from_pdf(filename: str, show_progress: bool = False, archive_uuid: str = '') -> List[str]:
    '''
        Возвращает текст из пдф в виде списка текстов из каждой страницы пдф
        Получить текст из pdf файла с названием filename с помощью pdfplumber постранично и записывать в результирующий список. 
        В конце его вернуть
        Если при получении текста из страниц, возвращается None, значит, это скан
        Тогда вызвать метод get_text_from_scan() для этого файла и вернуть результат
        >>> get_text_from_pdf('docx/text.pdf')
        ['A Simple PDF File This is a small demonstration .pdf file - just for use in the Virtual Mechanics tutorials. More text. And more text. And more text. And more text. And more text. And more text. And more text. And more text. And more text. And more text. And more text. Boring, zzzzz. And more text. And more text. And more text. And more text. And more text. And more text. And more text. And more text. And more text. And more text. And more text. And more text. And more text. And more text. And more text. And more text. Even more. Continued on page 2 ...', 'Simple PDF File 2 ...continued from page 1. Yet more text. And more text. And more text. And more text. And more text. And more text. And more text. And more text. Oh, how boring typing this stuff. But not as boring as watching paint dry. And more text. And more text. And more text. And more text. Boring. More, a little more text. The end, and just as well.']
        >>> get_text_from_pdf('docx/scan.pdf')
        ["Simple PDF File 2 ...continued from page 1. Yet more text And more text. And more text. And more text. And more text And more text. And more text. And more text Oh, how boring typing this stuff. But not as boring as watching paint dry. And more text And mote text. And more text. And more text. Bon'ng. More, a littte more text The end. and just as well.", 'A Simple PDF File This is a small demonstration .pdf file « just for use in the Virtual Mechanies Models. More text. And more text And more text. And more text. And more text. And more text. And more text And more text. And more text, And more text And more text Boring, zzzzz. And more text. And more text And more text And more text. And more text. And more text. And more text. And more text. And more text And mote text. And more text And more text. And more text. And more text And more text And more text. Even more. Continued on page 2']
    '''
    logging.info(f'Getting text from {filename}')
    res: List[str] = []
    use_tesseract = False
    
    with fitz.open(filename) as pdf:
        logging.info('Using fitz')

        for i, page in enumerate(pdf):
            logging.info(f'Page № {i}')
            text = correct_the_text(page.getText())

            res.append(text)
            use_tesseract = use_tesseract or not is_valid_text(text)

            if use_tesseract: 
                logging.info(f'Unable to get text with fitz')
                break


    if use_tesseract: res = get_text_from_scan(filename, archive_uuid)

    return res

if __name__ == '__main__':
    print(get_text_from_pdf('test_lease.pdf'))