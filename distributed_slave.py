
import os
import psutil
import socket
import sys
import threading
import time

from distributed_master import *
from valid_server import *

REPORT_TIME_WAIT=5

'''
    Command List :
        Update Module :
            (sender Master) -> -update
            (form    Slave) <- None   
            ---  WARNING! Can not using UDP to tranceport big data ,it will be flash 
            ---  sock recv() buffer and than packet() can not correct resolve data stream
            (sender  Slave) -> connect to TCP port
            (sender  Slave) -> -update
            (form   Master) <- [['%file_index1%':'%file_index1_data%'],['%file_index2%':'%file_index2_data%'],...]
            
        Collect Data :
            (sender  Slave) -> -report {'IP':'%slave_ip%','CPU':%cpu_rate%,'Memory':%memory_using%,'PoCFile':%poc_file_count%}
            (form   Master) <- None
        
        Upload PoC :
            (sender Master) -> -upload
            (form    Slave) <- None
            ---
            (sender  Slave) -> connect to TCP port
            (sender  Slave) -> -upload [['%file_index1%':'%file_index1_data%'],['%file_index2%':'%file_index2_data%'],...]
            (form   Master) <- OK
            
        Discover Master :
            (sender  Slave) -> -discover
            (form   Master) <- -discover %master_ip%
'''

def get_cpu_rate() :
    cpu_data_list=psutil.cpu_percent(interval=REPORT_TIME_WAIT,percpu=True)
    cpu_rate=0.0
    for cpu_data_index in cpu_data_list :
        cpu_rate+=cpu_data_index
    cpu_rate/=psutil.cpu_count()
    return cpu_rate
    
def get_memory_rate() :
    memory_data=psutil.virtual_memory()
    return memory_data.percent

def poc_file_count() :
    file_count=0
    for file_name in os.listdir(CONFIG_POC_PATH):
        if file_name.find(EXTANSION_NAME_POC)>0 :
            file_count+=1
    return file_count

class thread_critical_section() :
    def __init__(self) :
        pass

class tcp_client() :
    def __init__(self,dest_address) :
        self.sock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.sock.connect((dest_address,TCP_PORT))
        
    def send(self,data) :
        self.sock.sendall(data)
        
    def recv(self) :
        return self.sock.recv(DATA_LENGTH)
    
    def close(self) :
        self.sock.close()

class distributed_slave() :
    def __init__(self) :
        self.broadcast=broadcast()
        
    def __get_current_path(self) :
        path = sys.path[0]
        if os.path.isdir(path):
            return path
        return os.path.dirname(path)
        
    def get_master_ip(self) :
        packet_data=packet()
        packet_data.set_slave()
        packet_data.set_slave_command(COMMAND_DISCOVER)
        self.broadcast.send(packet_data.tostring())

        self.broadcast.recv()  #  first recv is discover command
        packet_data.resolve(self.broadcast.recv())
        
        if packet_data.get_master() :
            command=packet_data.get_slave_command()
            if valid_command(COMMAND_DISCOVER,command) :
                return split_command_data(command)
        return ''
        
    def __background_server_upload(self) :
        file_count=0
        file_list=[]
        for file_name in os.listdir(CONFIG_POC_PATH) :
            if file_name.find(EXTANSION_NAME_POC)>0 :
                file_count+=1
                file_path=CONFIG_POC_PATH+'\\'+file_name
                file_data=open(file_path)
                if file_data :
                    file_index=[]
                    file_index.append(file_name)
                    file_index.append(file_data.read())
                    file_data.close()
                    file_list.append(file_index)
#                os.remove(file_path)
        trance_data=COMMAND_UPLOAD+' '+str(file_list)
        master_ip=self.get_master_ip()
        tcp_client_=tcp_client(master_ip)
        tcp_client_.send(trance_data)
        tcp_client_.close()

    def close_target_python_script(self,script_name) :
        for pid_index in psutil.pids() :
            try :
                process=psutil.Process(pid_index)
                command_line=process.cmdline()
                if len(command_line)>=2 :
                    if not command_line[1].find(script_name)==-1 :
                        os.kill(pid_index,9)
                        return True
            except :
                pass
        return False
        
    def __background_server_update(self) :
        master_ip=self.get_master_ip()
        tcp_client_=tcp_client(master_ip)
        tcp_client_.send(COMMAND_UPDATE)
        recv_data=''
        while True :
            recv_data_block=tcp_client_.recv()
            if not len(recv_data_block)==0 :
                recv_data+=recv_data_block
            else :
                break
        try :
            update_file_list=eval(recv_data)
            for update_file_index in update_file_list :
                update_path=BASE_DIR+'\\'+update_file_index[0]
                update_file=open(update_path,'w')
                if update_file :
                    update_file.write(update_file_index[1])
                    update_file.close()
                    if self.close_target_python_script(update_file_index[0]) :
                        os.system(update_path)
        except :
            print 'update ERROR!..'
        tcp_client_.close()
        
    def __background_server_thread(self) :
        while True :
            data_packet=packet()
            data_packet.resolve(self.broadcast.recv())
            if data_packet.get_master() :
                command=data_packet.get_slave_command()
                if valid_command(COMMAND_UPDATE,command) :
                    self.__background_server_update()
                elif valid_command(COMMAND_UPLOAD,command) :
                    self.__background_server_upload()
        
    def __background_server_report_thread(self) :
        while True :
            data_packet=packet()
            data_packet.set_slave()
            data_packet_command='{\'IP\':\''+get_local_ip()+'\',\'CPU\':'+str(get_cpu_rate())+',\'Memory\':'+str(get_memory_rate())+',\'PoCFile\':'+str(poc_file_count())+'}'  #  time wait in get_cpu_rate()
            data_packet.set_slave_command(COMMAND_REPORT+' '+data_packet_command)
            self.broadcast.send(data_packet.tostring())
        
    def run(self) :
        self.server_thread=threading.Thread(target=self.__background_server_thread)
        self.server_thread.start()
        
        self.report_thread=threading.Thread(target=self.__background_server_report_thread)
        self.report_thread.start()
    
    def exit(self) :
        self.server_thread.stop()
        self.report_thread.stop()
        
if __name__=='__main__' :
    distributed_slave_=distributed_slave()
    distributed_slave_.run()
    print 'Distributed Slave Will Exit!'
    