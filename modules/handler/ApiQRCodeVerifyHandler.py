import tornado.web
import os
from modules.parse_document import parse_document
import modules.util as util


class ApiQRCodeVerifyHandler(tornado.web.RequestHandler):
    def get(self):
        directory = 'uploads'

        if not os.path.exists(directory): 
            os.makedirs(directory) 
        
        for field_name, files in self.request.files.items():
            for info in files:
                filename = util.get_uniq_file_name(directory, info['filename'])
                body = info['body']
                print(filename)

                with open(f'{filename}', 'wb') as f:
                    f.write(body)

                self.write(parse_document(filename))

                os.remove(filename)
        if len(self.request.files) == 0:
            self.write({'error': 'You need to attach a document with a qr code'})