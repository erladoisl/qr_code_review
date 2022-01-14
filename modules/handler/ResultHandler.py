import tornado.web
import os
from modules.parse_document import parse_document


class ResultHandler(tornado.web.RequestHandler):
    def get(self):
        data = {}
        file_name = self.get_argument('file_name', '')
        
        if file_name != '':
            data = parse_document(file_name)
            os.remove(file_name)
            
        self.render("result.html", data = data)