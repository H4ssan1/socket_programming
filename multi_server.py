import socket
import threading
import select

port = 12000
HEADER = 64

host = "192.168.0.72"
print(host)
print(socket.gethostname())
ADDR = (host, port)

disconnect = "!break"
format = 'UTF-8'

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)
client_connections = {} ##dictionary to store client connections

def client_handler(con, addr):
    print(f"New connection {addr} connected.")
    connected = True
    while connected:
        msg_length = con.recv(HEADER).decode(format)
        if msg_length:
            msg_length = int(msg_length)
            msg = con.recv(msg_length).decode(format)
            if msg == disconnect:
                connected = False
            print(f"[{addr}] {msg}")
        con.send("Message received".encode(format))

    con.close()
    
    

def start():
    server.listen()
    print(f"[LISTENING] Server is listening on {host}")
    while True:
        # Wait for incoming connections with a timeout of 10 seconds
        ready, _, _ = select.select([server], [], [], 10) ##ready holds list of sockets ready for operation reading, 
        #while the underscores (_) are placeholders to disregard unused parameters
        if ready:
            conn, addr = server.accept()
            client_connections[addr] = conn
            thread = threading.Thread(target=client_handler, args=(conn, addr))
            thread.start()
            print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")
        elif (threading.active_count() - 1 == 0):
            print("No connections. Closing server...")
            break

print("[STARTING] server is starting...")
start()