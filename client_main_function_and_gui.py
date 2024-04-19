import socket
import threading
import select
import sys
import time
import json
import tkinter

port_no = 12000
HEADER = 64
host_IP = "192.168.0.72"
ADDR = (host_IP, port_no)

DISCONNECT_MESSAGE = "!BREAK"
format = 'UTF-8'
usage_info_thread = None

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)

server_connections = {}  # dictionary to store server connections

def server_handler(conn, addr):
    programs_incoming_messages(f"NEW CONNECTION {addr} CONNECTED")
    connected = True

    while connected:
        try:
            # Attempt to receive a small amount of data
            data = conn.recv(256)
            if not data:
                # No data received, indicating that the server has closed the connection
                programs_incoming_messages(f"Connection closed by server {addr}")
                break
            else:
                # Try decoding the received data as JSON
                try:
                    usage_info = json.loads(data.decode(format))
                    # If decoding succeeds, it's JSON data
                    devices_incoming_text(f"\n[{addr}]:{usage_info}")
                except json.JSONDecodeError:
                    # Process the received data
                    msg = data.decode(format)
                    if msg == DISCONNECT_MESSAGE:
                        connected = False
                    server_incoming_messages(f"\n[{addr}] {msg}")
        except ConnectionResetError:
            # Connection reset by the server
            programs_incoming_messages(f"Connection reset by server {addr}")
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
    server_addresses = ', '.join([str(addr) for addr in server_connections.keys()])
    devices_text_area.delete('1.0', tkinter.END)  # Clear existing content
    devices_text_area.insert(tkinter.END, server_addresses)


def send_to_server(server_addr, message):
    if server_addr in server_connections:
        server_conn = server_connections[server_addr]
        server_conn.send(message.encode(format))
    else:
        programs_incoming_messages("server not found.")

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
        usage_info_thread.daemon = True  # set the thread as a daemon so it exits when the main thread exits
        usage_info_thread.start()

def start():

    server.listen()
    programs_incoming_messages(f"[LISTENING] Client is listening on {host_IP}")

    while True:
        conn, addr = server.accept()
        server_connections[addr] = conn
        thread = threading.Thread(target=server_handler, args=(conn, addr))
        thread.start()
        start_usage_info_thread()
        display_connections()
        programs_incoming_messages(f"[ACTIVE CONNECTIONS] {len(server_connections)}")

def start_server_thread():
    server_thread = threading.Thread(target=start)
    server_thread.start()

################################################################
# GUI Functions

def devices_incoming_text(text):
    devices_text_area.insert(tkinter.END, text + "\n")
    devices_text_area.see(tkinter.END)

def programs_incoming_messages(text):
    program_text_area.insert(tkinter.END, text + "\n")
    program_text_area.see(tkinter.END)

def server_incoming_messages(text):
    server_text_area.insert(tkinter.END, text + "\n")
    server_text_area.see(tkinter.END)

def message_server():
    new_window = tkinter.Toplevel(client_GUI)
    new_window.title("Message a server")

    frame = tkinter.Frame(new_window)
    frame.pack(padx=10, pady=10)

    tkinter.Label(frame, text='IP').grid(sticky="W")
    ip_entry = tkinter.Entry(frame)
    ip_entry.grid(sticky="W")
    tkinter.Label(frame, text='Port').grid(sticky="W")
    port_entry = tkinter.Entry(frame)
    port_entry.grid(sticky="W")
    tkinter.Label(frame, text='Message').grid(sticky="W")
    message_entry = tkinter.Entry(frame)
    message_entry.grid(sticky="W")
    
    def submit_button():
        sending_ip = ip_entry.get()
        sending_port = int(port_entry.get())
        sending_message = message_entry.get()
        server_address = (sending_ip, sending_port)
        send_to_server(server_address, sending_message)
        new_window.destroy()  # Close the new window after sending the message
    
    submit_button = tkinter.Button(frame, text="Send", command=submit_button)
    submit_button.grid(pady=10)

################################################################
# GUI tkinter settings

client_GUI = tkinter.Tk()
client_GUI.title("Intelligent Job Scheduler")

frame1 = tkinter.Frame(client_GUI)
frame1.pack(side=tkinter.LEFT, padx=10, pady=10)

frame2 = tkinter.Frame(client_GUI)
frame2.pack(side=tkinter.LEFT, padx=10, pady=10)

devices_label = tkinter.Label(frame1, text="Devices")
devices_label.pack(anchor=tkinter.W)

devices_text_area = tkinter.Text(frame1, height=22, width=80)
devices_text_area.pack(pady=5)

program_messages_label = tkinter.Label(frame2, text="Program messages")
program_messages_label.pack(anchor=tkinter.W)

program_text_area = tkinter.Text(frame2, height=10, width=40)
program_text_area.pack(pady=5)

server_messages_label = tkinter.Label(frame2, text="Server messages")
server_messages_label.pack(anchor=tkinter.W)

server_text_area = tkinter.Text(frame2, height=10, width=40)
server_text_area.pack(pady=5)


send_message_to_server_button = tkinter.Button(client_GUI, text="Message a server", command=message_server)
send_message_to_server_button.pack(pady=10)

start_button = tkinter.Button(client_GUI, text="Start", command=start_server_thread)
start_button.pack(pady=10)


programs_incoming_messages("Intelligent Job Scheduler")
programs_incoming_messages(f"Client IP: {host_IP}")
programs_incoming_messages("[STARTING] server is starting...")

client_GUI.mainloop()

