
import os
import pydbg
import time
import win32event
import win32process

from valid_poc import *

BROWSER_PATH='"C:\\Program Files\\Internet Explorer\\iexplore.exe"'
BROWSER_ARG_LIST=''
FUZZING_URL='http://127.0.0.1/vector'
EXCEPTION_STACK_OVEWFLOW=0xC00000FD

BROWSER_PID=0
debugger=None

def create_process(process_path) :
    return win32process.CreateProcess(None,process_path,None,None,0,win32process.CREATE_NO_WINDOW,None,None,win32process.STARTUPINFO())

def get_browser_name() :
    return BROWSER_PATH[BROWSER_PATH.rfind('\\')+1:-1]  #  -1 will filter the "

def get_sub_process(create_process_pid) :
    browser_name=get_browser_name()
    command_data=os.popen('tasklist | find "'+browser_name+'"')
    line_data=command_data.readline()
    sub_process_list=[]
    while len(line_data) :
        num=line_data[line_data.find(browser_name)+len(browser_name):line_data.find('Console')]
        num=int(num.replace(' ',''))
        if create_process_pid!=num :
            sub_process_list.append(num)
        line_data=command_data.readline()
    return sub_process_list

def kill_process(pid) :
    os.kill(pid,9)
    
def dump_process_and_restart(exception) :
    EIP=debugger.get_register('EIP')
    except_instruction=debugger.disasm_around(EIP,1)
    if exception==pydbg.defines.EXCEPTION_GUARD_PAGE or exception==pydbg.defines.EXCEPTION_ACCESS_VIOLATION or exception==EXCEPTION_STACK_OVERFLOW :
        os.system('get_poc.py "'+get_exception(exception)+'-'+str(hex(EIP))[:-1]+'-'+except_instruction[1][1]+'"')
    debugger.detach()
    kill_process(BROWSER_PID)
    
def crash_recall_guard_page(self) :
    dump_process_and_restart(pydbg.defines.EXCEPTION_GUARD_PAGE)
    
def crash_recall_access_violation(self) :
    dump_process_and_restart(pydbg.defines.EXCEPTION_ACCESS_VIOLATION)
    
def crash_recall_stack_overflow(self) :
    dump_process_and_restart(EXCEPTION_STACK_OVERFLOW)
    
def main() :
    browser_process=create_process(BROWSER_PATH+' '+BROWSER_ARG_LIST+' '+FUZZING_URL)
    global BROWSER_PID
    global debugger
    BROWSER_PID=browser_process[2]  #  browser_process[2] === PID
    time.sleep(0.2)
    debugger=pydbg.pydbg()
#    try :
    debugger.attach(BROWSER_PID)    #  get_sub_process(BROWSER_PID)[0])
    debugger.set_callback(pydbg.defines.EXCEPTION_ACCESS_VIOLATION,crash_recall_access_violation)
    debugger.set_callback(pydbg.defines.EXCEPTION_GUARD_PAGE,crash_recall_guard_page)
    debugger.set_callback(EXCEPTION_STACK_OVEWFLOW,crash_recall_stack_overflow)
    debugger.run()
    win32event.WaitForSingleObject(browser_process[0],-1)  #  browser_process[0] === Process Handle
#    except :
#        print 'WARNING! pydbg can not attach to this process ,maybe you attach to a 64-bit process ,pydbg jut support attach to 32-bit process!'
#        exit()
    
if __name__=='__main__' :
    main()
    os.system('start process_monitor.py')
