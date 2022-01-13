import tornado.web
import os
from modules.parse_document import parse_document


def get_uniq_file_name(folder: str, file_name: str) -> str:
    i = 1
    uniq_file_name = f'{folder}/{file_name}'

    while os.path.exists(f'{uniq_file_name}'):
        uniq_file_name =f'{folder}/({i}){file_name}'
        i += 1

    return uniq_file_name


class QRCodeVerifyHandler(tornado.web.RequestHandler):
    def get(self):
        directory = 'uploads'

        if not os.path.exists(directory): 
            os.makedirs(directory) 
        
        for field_name, files in self.request.files.items():
            for info in files:
                filename = get_uniq_file_name(directory, info['filename'])
                body = info['body']
                print(filename)

                with open(f'{filename}', 'wb') as f:
                    f.write(body)

                self.write(parse_document(filename))

                os.remove(filename)

        if len(self.request.files) == 0:
            self.write({'error': 'Необходимо прикрепить документ с qr-кодом'})