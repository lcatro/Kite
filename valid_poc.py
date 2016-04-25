
import os
import pydbg
import requests
import sys
import win32event
import win32process


BROWSER_PATH='C:\\Program Files\\Internet Explorer\\iexplore.exe'
BROWSER_PID=0
POC_COUNT_URL='http://127.0.0.1/poc?all'
POC_URL='http://127.0.0.1/poc?'
EXPLOIT_OUTPUT_PATH='C:\\Users\\Administrator\\Desktop\\browser_fuzzing\\exploit'
debugger=None
exploit_index=0

def create_process(process_path) :
    return win32process.CreateProcess(None, process_path, None , None , 0 ,win32process.CREATE_NO_WINDOW , None , None ,win32process.STARTUPINFO())

def kill_process(pid) :
    os.kill(pid,9)
    
def restart_process(self) :
    self.detach()
    kill_process(BROWSER_PID)
    os.system('valid_poc.py '+str(exploit_index))
    
def crash_recall_access_violation(self) :
    EIP=self.get_register('EIP')
    EAX=self.get_register('EAX')
    EBX=self.get_register('EBX')
    ECX=self.get_register('ECX')
    EDX=self.get_register('EDX')
    ESP=self.get_register('ESP')
    EBP=self.get_register('EBP')
    ESI=self.get_register('ESI')
    EDI=self.get_register('EDI')
    
    instruction=self.disasm(EIP)
    if 'call'==instruction[0:4] :
        print 'WARNING! Exploit:\n',str(EIP)[:-1],instruction,str(EAX),str(EBX),str(ECX),str(EDX),str(ESP),str(EBP),str(ESI),str(EDI)
        exploit_data=requests.get(POC_COUNT_URL).text
        exploit_file=open(EXPLOIT_OUTPUT_PATH+'\\'+str(poc_index)+'.exploit.html','w')
        if exploit_file :
            exploit_file.write(exploit_data)
            exploit_file.close()
#    else :
#        print 'None'
    restart_process(self)

def crash_recall_guard_page(self) :
    pass
    
if __name__=='__main__' :
    poc_count=int(requests.get(POC_COUNT_URL).text)
    debugger=pydbg.pydbg()
    debugger.set_callback(pydbg.defines.EXCEPTION_ACCESS_VIOLATION,crash_recall_access_violation)
    debugger.set_callback(pydbg.defines.EXCEPTION_GUARD_PAGE,crash_recall_guard_page)
    debugger.set_callback(pydbg.defines.EXIT_PROCESS_DEBUG_EVENT,restart_process)
    if len(sys.argv)==2 and str.isdigit(sys.argv[1]) :
        if poc_count>int(sys.argv[1]) :
            browser_process=create_process(BROWSER_PATH+' '+POC_URL+str(sys.argv[1]))
            exploit_index=int(sys.argv[1])+1
    else :
        browser_process=create_process(BROWSER_PATH+' '+POC_URL+str(0))
        exploit_index=0
    BROWSER_PID=browser_process[2]
    debugger.attach(browser_process[2])
    debugger.run()
    