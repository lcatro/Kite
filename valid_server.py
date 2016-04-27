#! /user/bin/python
# coding:UTF-8

import logging
import os
import random
import sys
import tornado.web
import tornado.ioloop

BASE_DIR=os.path.dirname(__file__)
CONFIG_POC_PATH=BASE_DIR+'\\poc'
CONFIG_EXPLOIT_PATH=BASE_DIR+'\\exploit'

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
            elif data=='files' :
                global file_list
                self.write(str(file_list).encode('utf-8'))
            elif str.isdigit(data) :
                global file_count
                global file_list
                if file_count>0 :
                    print str(int(data)),CONFIG_POC_PATH+'\\'+file_list[int(data)]
                    file_poc=open(CONFIG_EXPLOIT_PATH+'\\'+file_list[int(data)]);
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
    
def flash_file_list(file_path,file_extansion_name) :
    global file_count,file_list
    file_count=0
    for file_name in os.listdir(file_path):
        if file_name.find(file_extansion_name)>0 :
            file_count+=1
            file_list.append(file_name)
    print 'Add '+str(file_count)+' Files - Path:'+file_path
    
if __name__=='__main__' :
    print 'Server Running'
    if len(sys.argv)==2 and sys.argv[1]=='debug' :
        flash_file_list(CONFIG_EXPLOIT_PATH,'.exploit.html')
    else :
        flash_file_list(CONFIG_POC_PATH,'.poc.html')
    listen(80)
    