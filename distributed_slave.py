
import socket
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
            (form   Master) <- {'%file_index1%':'%file_index1_data%','%file_index2%':'%file_index2_data%',...}
            
        Collect Data :
            (sender  Slave) -> -report {'IP',%slave_ip%,'CPU':%cpu_rate%,'Memory':%memory_using%,'PoCFile':%poc_file_count%}
            (form   Master) <- None
        
        Upload PoC :
            (sender Master) -> -upload
            (form    Slave) <- None
            ---
            (sender  Slave) -> connect to TCP port
            (sender  Slave) -> -upload {'%file_index1%':'%file_index1_data%','%file_index2%':'%file_index2_data%',...}
            (form   Master) <- OK
            
        Discover Master :
            (sender  Slave) -> -discover
            (form   Master) <- -discover %master_ip%
'''

class distributed_slave() :
    def __init__(self) :
        self.broadcast=broadcast()
        
    def __background_server_thread(self) :
        while True :
            data_packet=packet()
            data_packet.resolve(self.broadcast.recv())
            if data_packet.get_master() :
                command=data_packet.get_slave_command()
                if COMMAND_UPDATE==command[:len(COMMAND_UPDATE)] :
                    pass  #  go back to home ,2333  
        
    def run(self) :
        self.thread=threading.Thread(target=self.__background_server_thread)
        self.thread.start()
        self.thread.join()
    
    def exit(self) :
        self.thread.stop()
        
if __name__=='__main__' :
    distributed_slave_=distributed_slave()
    distributed_slave_.run()
    print 'Distributed Slave Will Exit!'
    