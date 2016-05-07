
import os
import sys
import socket

if __name__=='__main__' :
    sock=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    sock.bind(('127.0.0.1',10086))
    if len(sys.argv)==2 and sys.argv[1]=='debug' :
        os.system('start valid_server.py debug')
    else :
        os.system('start valid_server.py')
    os.system('start valid_poc.py 0')
    
    while True :
        data,addr=sock.recvfrom(1024)
        print data
