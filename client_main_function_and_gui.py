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



server_connections = {}  # dictionary to store server connections
devices_usage_info = {}  # dictionary to store devices' usage info

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
                 # Check if the received data starts with the usage info prefix
                if data.startswith(b"USAGE_INFO:"):
                    usage_info = json.loads(data[len("USAGE_INFO:"):].decode(format))
                    devices_usage_info[addr] = usage_info
                else:
                    # Process the received data as a regular message
                    msg = data.decode(format)
                    server_incoming_messages(f"\n[{addr}] {msg}")
        except ConnectionResetError:
            # Connection reset by the server
            programs_incoming_messages(f"Connection reset by server {addr}")
            break

    conn.close()
    # Remove the connection from the dictionary when it's closed
    del server_connections[addr]
    del devices_usage_info[addr]

def request_usage_info():   
    while True:
        for address in server_connections:
            send_to_server(address, "usage info")
        display_devices()
        time.sleep(3)
        
def display_devices():
    devices_text_area.delete('1.0', tkinter.END)  # Clear existing content
    for i, (address, pc_usage_info) in enumerate(devices_usage_info.items()):
        devices_text_area.insert(tkinter.END, f"Device {i + 1}\n")
        devices_text_area.insert(tkinter.END, f"IP: {address[0]}\nPort:{address[1]}\n")
        formatted_usage_data = "\n".join([f"{key}: {value}" for key, value in pc_usage_info.items()])
        devices_text_area.insert(tkinter.END, f"{formatted_usage_data}\n\n")

def send_to_server(server_addr, message):
    if server_addr in server_connections:
        server_conn = server_connections[server_addr]
        server_conn.send(message.encode(format))
    else:
        programs_incoming_messages("server not found.")

def start_usage_info_thread():
    global usage_info_thread
    if not usage_info_thread or not usage_info_thread.is_alive():
        usage_info_thread = threading.Thread(target=request_usage_info)
        usage_info_thread.daemon = True  # set the thread as a daemon so it exits when the main thread exits
        usage_info_thread.start()

def start():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.bind(ADDR)
    client.listen()
    programs_incoming_messages(f"[LISTENING] Client is listening on {host_IP}")

    while True:
        conn, addr = client.accept()
        server_connections[addr] = conn
        thread = threading.Thread(target=server_handler, args=(conn, addr))
        thread.start()
        start_usage_info_thread()
        programs_incoming_messages(f"[ACTIVE CONNECTIONS] {len(server_connections)}")

def start_server_thread():
    server_thread = threading.Thread(target=start)
    server_thread.start()
    start_button.pack_forget()

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

    main_width = client_GUI.winfo_width()
    main_height = client_GUI.winfo_height()

    # Calculate the x and y coordinates for the center of the main window
    x = client_GUI.winfo_rootx() + main_width // 2 - 70
    y = client_GUI.winfo_rooty() + main_height // 2 - 70

    # Set the position of the new window to be centered relative to the main window
    new_window.geometry(f"260x190+{x}+{y}")

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

button_frame = tkinter.Frame(client_GUI)
button_frame.pack(anchor='nw', padx=10, pady=10)

frame1 = tkinter.Frame(client_GUI)
frame1.pack(side=tkinter.LEFT, padx=10, pady=10)

frame2 = tkinter.Frame(client_GUI)
frame2.pack(side=tkinter.LEFT, padx=10, pady=10)

devices_label = tkinter.Label(frame1, text="Devices")
devices_label.pack(anchor=tkinter.W)

devices_text_area = tkinter.Text(frame1, height=42, width=140)

devices_text_area.pack(pady=5)

program_messages_label = tkinter.Label(frame2, text="Program messages")
program_messages_label.pack(anchor=tkinter.W)

program_text_area = tkinter.Text(frame2, height=20, width=80)
program_text_area.pack(pady=5)

server_messages_label = tkinter.Label(frame2, text="Server messages")
server_messages_label.pack(anchor=tkinter.W)

server_text_area = tkinter.Text(frame2, height=20, width=80)
server_text_area.pack(pady=5)

start_button = tkinter.Button(button_frame, text="Start Program", command=start_server_thread)
start_button.pack(side=tkinter.LEFT, padx=5)

send_message_to_server_button = tkinter.Button(button_frame, text="Message a server", command=message_server)
send_message_to_server_button.pack(side=tkinter.LEFT, padx=5)


programs_incoming_messages("Intelligent Job Scheduler")
programs_incoming_messages(f"Client IP: {host_IP}")
programs_incoming_messages("[STARTING] server is starting...")

client_GUI.mainloop()