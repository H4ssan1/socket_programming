import socket
import threading

port_no = 12000
HEADER = 64
host_IP = "192.168.0.72"
ADDR = (host_IP, port_no)
print("Intelligent Job Scheduler")
print(f"Client IP: {host_IP}")

DISCONNECT_MESSAGE = "!BREAK"
format = 'UTF-8'

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)

def server_handler(conn, addr):
    print(f"NEW CONNECTION {addr} CONNECTED")
    connected = True
    while connected:
        calculation = input("Enter a calculation\n")
        conn.send(calculation.encode(format))
        msg_length = conn.recv(HEADER).decode(format)
        if msg_length:
            msg_length = int(msg_length)
            msg = conn.recv(msg_length).decode(format)
            if msg == DISCONNECT_MESSAGE:
                connected = False
            print(f"[{addr}] {msg}")
        conn.send("Message received".encode(format))
    
    conn.close()

"""
def message_server(msg):
    message = msg.encode(format)
    msg_length = len(message)
    send_length = str(msg_length).encode(format)
    send_length += b' ' * (HEADER - len(send_length))
    server.send(send_length)
    server.send(message)
    print(server.recv(2048).decode(format))

"""


def start():
    running = True
    server.listen()
    print(f"[LISTENING] Client is listening on {host_IP}")
    while (running):
        conn, addr = server.accept()
        thread = threading.Thread(target=server_handler, args=(conn, addr))
        thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")
        

print("[STARTING] server is starting...")
start()