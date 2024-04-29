import socket
import os
client=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#host=socket.gethostname() #server hostname
server_IP='192.168.0.72'
port=12000 #same as server
client.connect((server_IP,port))

while True:

    inp = input("enter message\n")
    client.send(inp.encode())
    print("waiting for response...\n")
    if inp == "close":
        print("connection closed")
        break

    answer = client.recv(1024).decode()
    if answer == "close":
        print("connection closed")
        break
    print("response is: "+answer)

client.close()
    