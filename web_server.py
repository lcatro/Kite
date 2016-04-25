#! /user/bin/python
# coding:UTF-8
import os
import random
import logging
import tornado.web
import tornado.ioloop

MOR_POC = None

class MainHandler(tornado.web.RequestHandler):
    def initialize(self, copy_data):
        self.template = copy_data
        self.vectors = None

    def gen(self):
        self.vectors = None
        # 1.generate random arrays
        intArray = []
        int_max=700
        for x in range(int_max):
            intArray.append(random.randint(0, int_max))
        # 2.replace vecotr template
        self.vectors = self.template.replace("%MOR_ARRAY%", str(intArray), 1)
        self.vectors = self.vectors.replace("%MOR_INDEX%", str(random.randint(0, 10)), 1)

    def get(self):
        global MOR_POC
        self.gen()
        MOR_POC = self.vectors
        self.write(self.vectors.encode('utf-8'))

class PocHandler(tornado.web.RequestHandler):
    def get(self):
       global MOR_POC
       self.write(MOR_POC.encode('utf-8'))

class FileHandler():
    def set_extra_headers(self, path):
        self.set_header("Cache-control", "no-cache")


def listen(port_args, fuzzer_args, postfix=".html"):
    # cancel log output in commandline
    logging.getLogger('tornado.access').disabled = True
    logging.getLogger('tornado.general').disabled = True

    # set static file path and read template
    if os.path.isfile(os.path.join('fuzzer', fuzzer_args)):
        f = open(os.path.join('fuzzer', fuzzer_args), 'r')
        static_path = os.path.join(os.path.dirname(__file__), "fuzzer")
    else:
        f = open(os.path.join('fuzzer', fuzzer_args, fuzzer_args+postfix), 'r')
        static_path = os.path.join(os.path.dirname(__file__), os.path.join('fuzzer', fuzzer_args))
    try:
        copy_data = f.read()
    except Exception as e:
        raise e
    finally:
        f.close()

    handler = [
        (r"/vector", MainHandler, dict(copy_data=copy_data)),
        (r"/poc", PocHandler),
        (r"/(.*)", tornado.web.StaticFileHandler, dict(path=static_path)),
    ]
    http_Server = tornado.web.Application(handlers=handler)
    http_Server.listen(port_args)
    tornado.ioloop.IOLoop.current().start()
    
    
if __name__=='__main__' :
    print 'Server running'
    listen(80,'','nduja.html')
    