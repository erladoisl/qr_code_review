from modules.handler.QRCodeVerifyHandler import QRCodeVerifyHandler
from modules.handler.ApiQRCodeVerifyHandler import ApiQRCodeVerifyHandler
from modules.handler.ResultHandler import ResultHandler
import json
import tornado
import tornado.ioloop
import tornado.web
import os
import traceback

application = tornado.web.Application([
    (r"/api/qrservice", ApiQRCodeVerifyHandler),
    (r"/qrservice/upload", QRCodeVerifyHandler),
    (r"/qrservice/result", ResultHandler)],
 template_path=os.path.join(os.path.dirname(__file__), "templates"),
 static_path=os.path.join(os.path.dirname(__file__), "static"),
 autoreload=True,
 autoescape=None,
 debug=True
)


if __name__ == "__main__":
 try:
  f = open("config.json", "r")
  config = json.load(f)
  server_ip = config["server-ip"]
  server_port = config["server-port"]
  protocol = 'http://'
  host_url = protocol + server_ip + ":" + server_port + "/"
  print("start with:     " + host_url)
 except:
  print("Can not load file config.json")
  traceback.print_exc()
 else:
  print("loading server")
  application.listen(int(server_port))
  print("starting")
  tornado.ioloop.IOLoop.instance().start()