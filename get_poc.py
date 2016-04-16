#!/usr/bin/env python
#-*- coding:utf-8 -*-

import HTMLParser
import requests
import hashlib

def get_md5(data) :
    md5=hashlib.md5()
    md5.update(data)
    return md5.hexdigest()

def save_poc(data) :
    file_=open('poc/'+get_md5(data)+'.poc.html','w')
    if file_ :
        data=data.replace('/*patch me in poc*/','//')
        file_.write(data)
        file_.close()

def get_poc() :
    result_linux=requests.get('http://127.0.0.1/poc')
    return result_linux.content

if __name__=='__main__' :
    data=get_poc()
    save_poc(data)