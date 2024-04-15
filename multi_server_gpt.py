import socket
import threading
import select
import sys
import time

port_no = 12000
HEADER = 64
host_IP = "192.168.0.72"
ADDR = (host_IP, port_no)
print("Intelligent Job Scheduler")
print(f"Client IP: {host_IP}")

DISCONNECT_MESSAGE = "!BREAK"
format = 'UTF-8'
display_thread = None

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)

server_connections = {} ##dictionary to store server connections

def server_handler(conn, addr):
    print(f"NEW CONNECTION {addr} CONNECTED")
    connected = True

    while connected:
        try:
            # Attempt to receive a small amount of data
            data = conn.recv(16)
            if not data:
                # No data received, indicating that the server has closed the connection
                print(f"Connection closed by server {addr}")
                break
            else:
                # Process the received data
                msg = data.decode(format)
                if msg == DISCONNECT_MESSAGE:
                    connected = False
                print(f"[{addr}] {msg}")
        except ConnectionResetError:
            # Connection reset by the server
            print(f"Connection reset by server {addr}")
            break
    
    conn.close()
    # Remove the connection from the dictionary when it's closed
    del server_connections[addr]

def display_connections():
    while True:
        # Check if there are active connections
        if server_connections:
            # Join server addresses to a string
            server_addresses_str = ', '.join([str(addr) for addr in server_connections.keys()])
            # Clear the current line and print the updated server addresses
            sys.stdout.write(f"\rServer addresses: {server_addresses_str}")
            sys.stdout.flush()
        else:
            # If there are no active connections, print a message and break out of the loop
            sys.stdout.flush()
            break
        time.sleep(3)  # Update every 3 seconds


def send_to_server(server_addr, message):
    if server_addr in server_connections:
        server_conn = server_connections[server_addr]
        server_conn.send(message.encode(format))
    else:
        print("server not found.")

def if_send_to_server():
        server_input = input("Would you like to send a message to a server? (y/n)")
        if server_input == "y":
            server_IP = input("enter IP of server\n")
            server_port = int(input("enter port of server\n"))
            server_address = (server_IP, server_port)
            message_to_send = input("Enter calculation to send\n")
            send_to_server(server_address, message_to_send)

def start_display_thread():
    global display_thread
    if not display_thread or not display_thread.is_alive():
        display_thread = threading.Thread(target=display_connections)
        display_thread.daemon = True  # Set the thread as a daemon so it exits when the main thread exits
        display_thread.start()

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
            start_display_thread()
            print(f"[ACTIVE CONNECTIONS] {len(server_connections)}")
        elif (len(server_connections) == 0):
            print("No connections. Closing server...")
            break

        #if_send_to_server()
                
    server.close()

print("[STARTING] server is starting...")

start()

