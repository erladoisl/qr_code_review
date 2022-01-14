import tornado.web
import modules.util as util
import os


class QRCodeVerifyHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("upload.html")


    def post(self):
        directory = 'uploads'

        if not os.path.exists(directory): 
            os.makedirs(directory) 

        file_name = util.get_uniq_file_name(directory, self.request.files['file1'][0]['filename'])
        file_body = self.request.files['file1'][0]['body']
        
        with open(f'{file_name}', 'wb') as f:
            f.write(file_body)
    
        self.redirect("/qrservice/result?file_name=" + file_name)