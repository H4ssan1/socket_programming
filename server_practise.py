import socket
import os
import sys
serv=socket.socket(socket.AF_INET, socket.SOCK_STREAM)

host="127.0.0.1"
port= 12000 
serv.bind((host,port))
serv.listen(2)
print("socket listening")
client_socket,client_address = serv.accept()
print ("Client connected", client_address)
print ('Got Connection from', client_address)
while True:
    content=client_socket.recv(100).decode()
    if not content:
        print("connection is over")
        break
    print("response is:"+content)
    ret = input("enter response\n")
    client_socket.send(ret.encode())
    print("waiting for response...\n")

client_socket.close()
serv.close()
    