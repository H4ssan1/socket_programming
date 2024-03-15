import socket


port = 12000
header = 64
format = 'UTF-8'
disconnect = "!break"
name = "john"
# Whatever IP address you found from running ifconfig in terminal.
# SERVER = ""
ip = "192.168.0.72"
message_to_send = ""

ADDR = (ip, port)
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Officially connecting to the server.
client.connect(ADDR)

def send(msg):
    message = msg.encode(format)
    msg_length = len(message)
    send_length = str(msg_length).encode(format)
    send_length += b' ' * (header - len(send_length))
    client.send(send_length)
    client.send(message)
    print(client.recv(2048).decode(format))

username = input("Enter username\n")

while 1:
    message_to_send = input("enter message to send\n")
    if message_to_send == disconnect:
        send(disconnect)
        break
    else: 
        send(message_to_send)

