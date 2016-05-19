#!/usr/bin/env python
#-*- coding:utf-8 -*-

import hashlib
import HTMLParser
import requests
import sys

def get_md5(data) :
    md5=hashlib.md5()
    md5.update(data)
    return md5.hexdigest()

def save_poc(poc_data,exception_data) :
    if not exception_data=='' :
        file_=open('poc/'+exception_data+'-'+get_md5(poc_data)+'.poc.html','w')
    else :
        file_=open('poc/'+get_md5(poc_data)+'.poc.html','w')
    if file_ :
        poc_data=poc_data.replace('/*patch me in poc*/','//')
        file_.write(poc_data)
        file_.close()

def get_poc() :
    result_linux=requests.get('http://127.0.0.1/poc')
    return result_linux.content

if __name__=='__main__' :
    poc_data=get_poc()
    if len(sys.argv)==2 :
        save_poc(poc_data,sys.argv[1])
    else :
        save_poc(poc_data,'')
    