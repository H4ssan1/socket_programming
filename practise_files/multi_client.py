import socket
import select
import sys

port = 12000
header = 64
format = 'UTF-8'
disconnect = "!break"

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

while True:
    # Check if there's data to be received
    ready_to_read, _, _ = select.select([client], [], [], 0)
    for sock in ready_to_read:
        if sock == client:
            message_received = client.recv(2048).decode(format)
            if message_received:
                print(message_received)
    
    # Check for user input
    message_to_send = input("Enter message to send (type '!break' to exit): ")

    # Send user input if available
    if message_to_send:
        if message_to_send == disconnect:
            send(disconnect)
            sys.exit()  # Exit the program
        else:
            send(message_to_send)