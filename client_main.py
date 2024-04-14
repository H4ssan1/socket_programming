import socket
import threading
import select

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

server_connections = {} ##dictionary to store client connections

def server_handler(conn, addr):
    print(f"NEW CONNECTION {addr} CONNECTED")
    connected = True

    while connected:
        
        msg_length = conn.recv(HEADER).decode(format)
        if msg_length:
            msg_length = int(msg_length)
            msg = conn.recv(msg_length).decode(format)
            if msg == DISCONNECT_MESSAGE:
                connected = False
            print(f"[{addr}] {msg}")
    
    conn.close()

def send_to_client(client_addr, message):
    if client_addr in server_connections:
        client_conn = server_connections[client_addr]
        client_conn.send(message.encode(format))
    else:
        print("Client not found.")

def if_send_to_client():
        server_input = input("Would you like to send a message to a client? (y/n)")
        if server_input == "y":
            client_IP = input("enter IP of client\n")
            client_port = int(input("enter port of client\n"))
            client_address = (client_IP, client_port)
            message_to_send = input("Enter calculation to send\n")
            send_to_client(client_address, message_to_send)

def start():
    server.listen()
    print(f"[LISTENING] Client is listening on {host_IP}")
    while True:
        # Wait for incoming connections with a timeout of 10 seconds
        ready, _, _ = select.select([server], [], [], 10) ##ready holds list of sockets ready for operation reading, 
        #while the underscores (_) are placeholders to disregard unused parameters
        if ready:
            conn, addr = server.accept()
            server_connections[addr] = conn
            thread = threading.Thread(target=server_handler, args=(conn, addr))
            thread.start()
            print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")
        elif (threading.active_count() - 1 == 0):
            print("No connections. Closing server...")
            break

        print(f"Client addresses: {server_connections}")
        if_send_to_client()
                


print("[STARTING] server is starting...")
start()
