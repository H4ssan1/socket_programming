import socket
import os
client=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_IP='192.168.0.182'
port=12000 #same as server
client.connect((server_IP,port))

while True:

    inp = input("enter message\n")
    client.send(inp.encode())
    print("waiting for response...\n")
    if not inp:
        break

    answer = client.recv(1024)
    print("response is: "+answer.decode())

client.close()
    