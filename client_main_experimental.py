import socket
import threading
import select
import sys
import time
import json

port_no = 12000
HEADER = 64
host_IP = "192.168.0.72"
ADDR = (host_IP, port_no)
print("Intelligent Job Scheduler")
print(f"Client IP: {host_IP}")

DISCONNECT_MESSAGE = "!BREAK"
format = 'UTF-8'
usage_info_thread = None

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)

server_connections = {} ##dictionary to store server connections

def server_handler(conn, addr):
    print(f"NEW CONNECTION {addr} CONNECTED")
    connected = True

    while connected:
        try:
            # Attempt to receive a small amount of data
            data = conn.recv(256)
            if not data:
                # No data received, indicating that the server has closed the connection
                print(f"Connection closed by server {addr}")
                break
            else:
                # Try decoding the received data as JSON
                try:
                    usage_info = json.loads(data.decode(format))
                    # If decoding succeeds, it's JSON data
                    print(f"\n[{addr}]:")
                    print(usage_info)
                except json.JSONDecodeError:
                    # Process the received data
                    msg = data.decode(format)
                    if msg == DISCONNECT_MESSAGE:
                        connected = False
                    print(f"\n[{addr}] {msg}")
        except ConnectionResetError:
            # Connection reset by the server
            print(f"Connection reset by server {addr}")
            break
    
    conn.close()
    # Remove the connection from the dictionary when it's closed
    del server_connections[addr]

def request_usage_info():
    while True:
        for address in server_connections:
            send_to_server(address, "usage info")
        time.sleep(30)

def display_connections():
    #while True:
        server_addresses_str = ', '.join([str(addr) for addr in server_connections.keys()])
        # Print the server addresses without creating a new line
        sys.stdout.write(f"\rServer addresses: {server_addresses_str}\n")
        #sys.stdout.write(f"\rServer addresses: {server_connections}")
        sys.stdout.flush()
        #time.sleep(3)

def send_to_server(server_addr, message):
    if server_addr in server_connections:
        server_conn = server_connections[server_addr]
        server_conn.send(message.encode(format))
    else:
        print("server not found.")

def if_send_to_server():
        server_input = input("Would you like to send a message to a server? (y/n)\n")
        if server_input == "y":
            server_IP = input("enter IP of server\n")
            server_port = int(input("enter port of server\n"))
            server_address = (server_IP, server_port)
            message_to_send = input("Enter calculation to send\n")
            send_to_server(server_address, message_to_send)

def start_usage_info_thread():
    global usage_info_thread
    if not usage_info_thread or not usage_info_thread.is_alive():
        usage_info_thread = threading.Thread(target=request_usage_info)
        usage_info_thread.daemon = True  #set the thread as a daemon so it exits when the main thread exits
        usage_info_thread.start()

def start():
    server.listen()
    print(f"[LISTENING] Client is listening on {host_IP}")
    
    while True:
        
        #wait for incoming connections with a timeout of 10 seconds
        ready, _, _ = select.select([server], [], [], 10) ##ready holds list of sockets ready for operation reading, 
        #while the underscores (_) are placeholders to disregard unused parameters
        
        if ready:
            conn, addr = server.accept()
            server_connections[addr] = conn
            thread = threading.Thread(target=server_handler, args=(conn, addr))
            thread.start()
            start_usage_info_thread()
            display_connections()
            print(f"[ACTIVE CONNECTIONS] {len(server_connections)}")
        elif (len(server_connections) == 0):
            print("No connections. Closing server...")
            break

        #if_send_to_server()
                
    server.close()

print("[STARTING] server is starting...")

start()

