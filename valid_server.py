#! /user/bin/python
# coding:UTF-8
import os
import random
import logging
import tornado.web
import tornado.ioloop

config_poc_path='C:\\Users\\Administrator\\Desktop\\browser_fuzzing\\poc'
# WARNING! There will need a full path
file_count=0
file_list=[]

class PocHandler(tornado.web.RequestHandler):
    def get(self):
        # /poc?all -> Get file count
        # /poc?1 -> Get file Number 1
        url=self.request.uri
        if url.find('?')>0 :
            data=url[url.find('?')+1:]
            if data=='all' :
                global file_count
                self.write(str(file_count).encode('utf-8'))
            elif str.isdigit(data) :
                global file_count
                global file_list
                if file_count>0 :
                    print str(int(data)),config_poc_path+'\\'+file_list[int(data)]
                    file_poc=open(config_poc_path+'\\'+file_list[int(data)]);
                    if file_poc :
                        self.write(file_poc.read().encode('utf-8'))
                        file_poc.close()
                    else :
                        self.write('Open File ERROR!'.encode('utf-8'))
            else :
                self.write('Argv ERROR!'.encode('utf-8'))
        else :
            self.write('Argv -> /poc?all or /poc?%file_number%'.encode('utf-8'))

def listen(port_args):
    handler = [
        (r"/poc", PocHandler),
    ]
    http_Server = tornado.web.Application(handlers=handler)
    http_Server.listen(port_args)
    tornado.ioloop.IOLoop.current().start()
    
if __name__=='__main__' :
    print 'Server Running'
    file_count=0
    for file_name in os.listdir(config_poc_path):
        if file_name.find('.poc.html')>0 :
            file_count+=1
            file_list.append(file_name)
    listen(80)
    