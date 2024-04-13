import socket
import threading
import select
import sys
import tkinter as tk

port = 12000
HEADER = 64

host = "192.168.0.72"
ADDR = (host, port)

disconnect = "!break"
format = 'UTF-8'

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)
client_connections = {}  # Dictionary to store client connections

# Function to handle client messages
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
            # Update GUI with incoming message
            update_messages(f"[{addr}] {msg}")
        con.send("Message received".encode(format))
    con.close()

# Function to send message to a client
def send_to_client(client_addr, message):
    if client_addr in client_connections:
        client_conn = client_connections[client_addr]
        client_conn.send(message.encode(format))
    else:
        print("Client not found.")

# Function to prompt user for sending message to a client
def if_send_to_client():
    server_input = input("Would you like to send a message to a client? (y/n)")
    if server_input == "y":
        client_IP = input("Enter IP of client: ")
        client_port = int(input("Enter port of client: "))
        client_address = (client_IP, client_port)
        message_to_send = input("Enter message to send: ")
        send_to_client(client_address, message_to_send)

# Function to start the server
def start_server():
    server.listen()
    print(f"[LISTENING] Server is listening on {host}")
    while True:
        ready, _, _ = select.select([server], [], [], 10)
        if ready:
            conn, addr = server.accept()
            client_connections[addr] = conn
            thread = threading.Thread(target=client_handler, args=(conn, addr))
            thread.start()
            print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")
        elif threading.active_count() - 1 == 0:
            print("No connections. Closing server...")
            break
        print(f"Client addresses: {client_connections}")
        if_send_to_client()

# GUI function to update messages
def update_messages(message):
    text_area.config(state=tk.NORMAL)
    text_area.insert(tk.END, message + "\n")
    text_area.config(state=tk.DISABLED)

# GUI setup
root = tk.Tk()
root.title("Server")

# Left frame for server log
left_frame = tk.Frame(root)
left_frame.pack(side=tk.LEFT, padx=5, pady=5)
tk.Label(left_frame, text="Server Log").pack()
text_area = tk.Text(left_frame, height=20, width=50)
text_area.pack()
text_area.config(state=tk.DISABLED)

# Right frame for sending messages to clients
right_frame = tk.Frame(root)
right_frame.pack(side=tk.LEFT, padx=5, pady=5)
tk.Label(right_frame, text="Send Message to Client").pack()
send_message_button = tk.Button(right_frame, text="Send Message", command=if_send_to_client)
send_message_button.pack()

# Start server in a separate thread
server_thread = threading.Thread(target=start_server)
server_thread.start()

# Run GUI
root.mainloop()
