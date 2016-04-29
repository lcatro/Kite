
import socket
import sys
import threading

from distributed_master import *

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
            (sender  Slave) -> -report {'IP',%slave_ip%,'CPU':%cpu_rate%,'Memory':%memory_using%,'PoCFile':%poc_file_count%}
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

class tcp_client() :
    def __init__(self,dest_address) :
        self.sock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.sock.connect((dest_address,TCP_PORT))
        
    def send(self,data) :
        self.sock.send(data)
        
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
        
        packet_data=packet()
        packet_data.resolve(self.broadcast.recv())
        
        if packet_data.get_master() :
            command=packet_data.get_slave_command()
            if valid_command(COMMAND_DISCOVER,command) :
                return command[command.find(' ')+1:]
        return ''
        
    def __background_server_upload_thread(self) :
        mutex=threading.Lock()
        if mutex.acquire() :
            dir_path=self.__get_current_path()
            file_count=0
            file_list=[]
            for file_name in os.listdir(dir_path):
                if file_name.find('.poc.html')>0 :
                    file_count+=1
                    file_path=dir_path+'\\'+file_name
                    file_data=open(file_path)
                    if file_data :
                        file_index=[]
                        file_index.append(file_path)
                        file_index.append(file_data.read())
                        file_data.close()
                        file_list.append(file_index)
            trance_data='-upload '+str(file_list)
            master_ip=self.get_master_ip()
            tcp_client_=tcp_client(master_ip)
            tcp_client_.send(trance_data)
            tcp_client_.close()
            mutex.release()
        
    def __background_server_thread(self) :
        while True :
            data_packet=packet()
            data_packet.resolve(self.broadcast.recv())
            if data_packet.get_master() :
                command=data_packet.get_slave_command()
                if valid_command(COMMAND_UPDATE,command) :
                    upload_thread=threading.Thread(target=self.__background_server_upload_thread)
                    upload_thread.start()
                #elif COMMAND_UPDATE==command[:len(COMMAND_UPDATE)] :
        
    def run(self) :
        self.thread=threading.Thread(target=self.__background_server_thread)
        self.thread.start()
    
    def exit(self) :
        self.thread.stop()
        
if __name__=='__main__' :
    distributed_slave_=distributed_slave()
    distributed_slave_.run()
    print distributed_slave_.get_master_ip()
    print 'Distributed Slave Will Exit!'
    