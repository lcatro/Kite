#! /user/bin/python
# coding:UTF-8
import os
import random
import logging
import threading
import time
import tornado.web
import tornado.ioloop

import process_monitor

BLOCK_TIME=300    #  If process_monitor.py be block by browser ,we could kill and restart browser for next test
MAKE_MAX_ELEMENT=6
MOR_POC = None

globle_tick=0
thread=threading.Lock()

def get_process_id() :
    try :
        browser_name=process_monitor.get_browser_name()
        command_data=os.popen('tasklist | find "'+browser_name+'"')
        line_data=command_data.readline()
        num=line_data[line_data.find(browser_name)+len(browser_name):line_data.find('Console')]
        num=int(num.replace(' ',''))
        return num
    except :
        return -1

def kill_process(pid) :
    os.kill(pid,9)

def restart_process_monitor() :
    pid=get_process_id()
    if pid is not -1 :
        kill_process(get_process_id())  #  process_monitor.py will auto restart when it kill browser process
    
def time_wait_restart_process_monitor_thread() :
    global BLOCK_TIME,globle_tick
    static_tick=globle_tick
    while True :
        is_restart=True
        for time_tick in range(BLOCK_TIME) :
            if static_tick!=globle_tick :
                static_tick=globle_tick
                is_restart=False
                break
            time.sleep(1)
        if is_restart :
            restart_process_monitor()
            
def rand(rand_range) :
    return int(random.random()*(rand_range))
    
def rand_bool() :
    if rand(2) :
        return True
    return False
    
def make_dom_element(max_element,close_element=True,is_nested_element=False) :
    all_html_element=['<!-->','<!DOCTYPE>','<a>','<abbr>','<acronym>','<address>','<applet>','<area>','<article>','<aside>','<audio>','<b>','<base>','<basefont>','<bdi>','<bdo>','<big>','<blockquote>','<body>','<br>','<button>','<canvas>','<caption>','<center>','<cite>','<code>','<col>','<colgroup>','<command>','<datalist>','<dd>','<del>','<details>','<dfn>','<dialog>','<dir>','<div>','<dl>','<dt>','<em>','<embed>','<fieldset>','<figcaption>','<figure>','<font>','<footer>','<form>','<frame>','<frameset>','<h1>','<h2>','<h3>','<h4>','<h5>','<h6>','<head>','<header>','<hr>','<html>','<i>','<iframe>','<img>','<input>','<ins>','<kbd>','<keygen>','<label>','<legend>','<li>','<link>','<main>','<map>','<mark>','<menu>','<menuitem>','<meta>','<meter>','<nav>','<noframes>','<noscript>','<object>','<ol>','<optgroup>','<option>','<output>','<p>','<param>','<pre>','<progress>','<q>','<rp>','<rt>','<ruby>','<s>','<samp>','<script>','<section>','<select>','<small>','<source>','<span>','<strike>','<strong>','<style>','<sub>','<summary>','<sup>','<table>','<tbody>','<td>','<textarea>','<tfoot>','<th>','<thead>','<time>','<title>','<tr>','<track>','<tt>','<u>','<ul>','<var>','<video>','<wbr>']
    make_element_string=''
    if max_element<=0 :
        return ''
    if is_nested_element :
        select_element=all_html_element[rand(len(all_html_element))]
        make_element_string=select_element
        make_element_string+=make_dom_element(max_element-1,close_element,is_nested_element)
        select_element='</'+select_element[1:]
        make_element_string+=select_element
    else :
        for element_index in range(max_element) :
            select_element=all_html_element[rand(len(all_html_element))]
            make_element_string+=select_element
            if rand_bool() and close_element :  #  get close element
                select_element='</'+select_element[1:]
                make_element_string+=select_element
    return make_element_string

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
        self.vectors = self.vectors.replace("%MOR_MOD%", str(random.randint(3, 21)), 1)
        self.vectors = self.vectors.replace("<!--HTML Element-->", make_dom_element(rand(MAKE_MAX_ELEMENT),rand_bool(),rand_bool()))

        self.vectors = self.vectors.replace("//turn_on_fuzzing", '', 1)
        self.vectors = self.vectors.replace("%DYNAMIC_MAKE_RANDOM_NUMBER_ARRAY%", str(intArray), 1)
        #self.vectors = self.vectors.replace("//turn_on_element", '', 1)
        #self.vectors = self.vectors.replace("%DYNAMIC_MAKE_SPCEIFY_ELEMENT_ARRAY%", make_dom_element , 1)
        
    def get(self):
        global MOR_POC,globle_tick
        self.gen()
        MOR_POC = self.vectors
        self.write(self.vectors.encode('utf-8'))
        # Setting Timeout Restart Fuzzing Monitor
        thread.acquire()
        globle_tick+=1
        thread.release()

class PocHandler(tornado.web.RequestHandler):
    def get(self):
       global MOR_POC
       self.write(MOR_POC.encode('utf-8'))

class FileHandler():
    def set_extra_headers(self, path):
        self.set_header("Cache-control", "no-cache")
        
class OtherHandler(tornado.web.RequestHandler) :
    def get(self,a) :
        self.write("<script>window.location.href='vector';</script>")

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
        (r"/(.*)", OtherHandler),
    ]
    http_Server = tornado.web.Application(handlers=handler)
    http_Server.listen(port_args)
    tornado.ioloop.IOLoop.current().start()
    
if __name__=='__main__' :
    print 'Server running'
    restart_thread=threading.Thread(target=time_wait_restart_process_monitor_thread)
    restart_thread.start()
#    listen(80,'','nduja.html')
    listen(80,'','kite.html')
    