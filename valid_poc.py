
import os
import pydbg
import requests
import socket
import sys
import win32event
import win32process

BASE_DIR=os.path.dirname(__file__)
BROWSER_PATH='C:\\Program Files\\Internet Explorer\\iexplore.exe'
BROWSER_PID=0
DUMP_DATA_LENGTH=128
EXPLOIT_OUTPUT_PATH=BASE_DIR+'\\exploit'
POC_COUNT_URL='http://127.0.0.1/poc?all'
POC_URL='http://127.0.0.1/poc?'

debugger=None
exploit_index=0

def create_process(process_path) :
    return win32process.CreateProcess(None,process_path,None,None,0,win32process.CREATE_NO_WINDOW,None,None,win32process.STARTUPINFO())

def kill_process(pid) :
    os.kill(pid,9)
    
def restart_process(self) :
    self.detach()
    kill_process(BROWSER_PID)
    if not debugger_state :
        os.system('start valid_poc.py '+str(exploit_index+1))

def format_output(memory_data) :
    output_string=''
    for memory_data_index in memory_data :
        output_string+=str(hex(ord(memory_data_index)))+' '
    return output_string
        
def get_instruction(self,address) :
    for ins in self.disasm_around(address,10) :
        if ins[0]==address :
            print '->Add:'+str(hex(ins[0]))[:-1]+'-'+ins[1]
        else :
            print '  Add:'+str(hex(ins[0]))[:-1]+'-'+ins[1]
    
def dump_crash(self,EIP,EAX,EBX,ECX,EDX,ESP,EBP,ESI,EDI,instruction) :
    print 'WARNING! Exploit:',str(hex(EIP))[:-1],instruction,'\n'
    get_instruction(self,EIP)
    print ''
    print 'EAX:'+str(hex(EAX))[:-1],'EBX:'+str(hex(EBX))[:-1],'ECX:'+str(hex(ECX))[:-1],'EDX:'+str(hex(EDX))[:-1],'ESP:'+str(hex(ESP))[:-1],'EBP:'+str(hex(EBP))[:-1],'ESI:'+str(hex(ESI))[:-1],'EDI:'+str(hex(EDI))[:-1]
    if not debugger_state :
        exploit_data=requests.get(POC_URL+str(exploit_index)).text
        exploit_file=open(EXPLOIT_OUTPUT_PATH+'\\'+str(exploit_index)+'.exploit.html','w')
        if exploit_file :
            exploit_file.write(exploit_data)
            exploit_file.close()
    else :
        print 'Easy Debug Viewer:'
        print 'command:-r %regesit% (look regesit) ;-a %address% (look memory address) ;-u %address% (get instruction) ;-quit (will exit)'
        while True :
            command=raw_input('->')
            if command[:2]=='-r' :
                print str(hex(self.get_register(str.upper(command[3:]))))[:-1]
            elif command[:2]=='-a' and str.isdigit(command[3:]) :
                dump_data=self.read(eval(command[3:]),DUMP_DATA_LENGTH)
                print format_output(dump_data)
                print dump_data
            elif command[:2]=='-u' and str.isdigit(command[3:]) :
                get_instruction(self,eval(command[3:]))
            elif command[:5]=='-quit' :
                break
    
def debug_send(debug_string) :
    sock=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    sock.sendto(debug_string,('127.0.0.1',10086))
    sock.close()
    
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
    
    output=''
#    for ins in self.disasm_around(EIP,10) :
#        output+='Add:'+str(ins[0])+'-'+ins[1]+'\r'
    output+='index:'+str(exploit_index)+' addr:'+str(hex(EIP))[:-1]+'-'+instruction
    debug_send(output)
        
    if 'call'==instruction[0:4] :
        dump_crash(self,EIP,EAX,EBX,ECX,EDX,ESP,EBP,ESI,EDI,instruction)
    elif 'mov'==instruction[0:3] :
        dump_crash(self,EIP,EAX,EBX,ECX,EDX,ESP,EBP,ESI,EDI,instruction)
    elif 'pop'==instruction[0:3] :
        dump_crash(self,EIP,EAX,EBX,ECX,EDX,ESP,EBP,ESI,EDI,instruction)
#    else :
#        print 'None'
    restart_process(self)

def crash_recall_guard_page(self) :
    crash_recall_access_violation(self)
    
if __name__=='__main__' :
    poc_count=int(requests.get(POC_COUNT_URL).text)
    debugger=pydbg.pydbg()
    debugger.set_callback(pydbg.defines.EXCEPTION_ACCESS_VIOLATION,crash_recall_access_violation)
    debugger.set_callback(pydbg.defines.EXCEPTION_GUARD_PAGE,crash_recall_guard_page)
    debugger.set_callback(pydbg.defines.EXIT_PROCESS_DEBUG_EVENT,restart_process)
    
    browser_process=None
    if len(sys.argv)==2 and str.isdigit(sys.argv[1]) :
        if poc_count>int(sys.argv[1]) :
            browser_process=create_process(BROWSER_PATH+' '+POC_URL+str(sys.argv[1]))
            exploit_index=int(sys.argv[1])
    elif len(sys.argv)==2 and sys.argv[1]=='count' :
        print 'PoC File Count:'+str(poc_count)
        exit()
    else :
        browser_process=create_process(BROWSER_PATH+' '+POC_URL+str(0))
        exploit_index=0
    BROWSER_PID=browser_process[2]
    debugger.attach(BROWSER_PID)
    debugger.run()
    