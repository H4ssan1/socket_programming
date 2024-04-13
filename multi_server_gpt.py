import socket
import threading

port = 12000
HEADER = 64
HOST = "192.168.0.72"
ADDR = (HOST, port)
DISCONNECT = "!break"
FORMAT = 'UTF-8'

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)
client_connections = {}  # Dictionary to store client connections
active_connections = 0  # Counter for active connections


def client_handler(conn, addr):
    global active_connections
    
    print(f"New connection {addr} connected.")
    active_connections += 1
    
    connected = True
    while connected:
        print(f"client connections {client_connections}\n")
        msg_length = conn.recv(HEADER).decode(FORMAT)
        if msg_length:
            msg_length = int(msg_length)
            msg = conn.recv(msg_length).decode(FORMAT)
            if msg == DISCONNECT:
                connected = False
            print(f"[{addr}] {msg}")
        conn.send("Message received".encode(FORMAT))

    conn.close()
    active_connections -= 1
    print(f"Connection with {addr} closed. Active connections: {active_connections}")


def start():
    global active_connections
    
    running = True
    server.listen()
    print(f"[LISTENING] Server is listening on {HOST}")
    
    while running:
        conn, addr = server.accept()
        client_connections[addr] = conn
        thread = threading.Thread(target=client_handler, args=(conn, addr))
        thread.start()
        active_connections += 1
        print(f"[ACTIVE CONNECTIONS] {active_connections}")
        
        if active_connections == 1:  # Only initial connection, close server
            print("No active connections other than the initial one. Closing server.")
            server.close()
            break

print("[STARTING] server is starting...")
start()
