#####Imported various libraries for use within my project
import socket
import threading
import sys
import time
import json
import tkinter

port_no = 12000 # port number for servers to connect to
HEADER = 64 # header space
host_IP = "" # REPLACE THIS WITH host ip for socket to be binded to
ADDR = (host_IP, port_no) 

format = 'UTF-8' # encoding format for messages to be sent out
usage_info_thread = None #thread for printing usage information
main_thread_ending = threading.Event() # flag to halt all threads if main closes

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # creation of TCP socket
client.bind(ADDR) # binding address to socket so that servers has reference to connect to it

server_connections = {}  # dictionary to store server connections
devices_usage_info = {}  # dictionary to store devices' usage info

def server_handler(conn, addr): # deals with different server connections, including receiving messages
    programs_incoming_messages(f"NEW CONNECTION {addr} CONNECTED")
    connected = True #while connected to a server

    while connected:
        try:
            #attempt to receive a small amount of data
            data = conn.recv(256)
            if not data:
                #no data received, indicating that the server has closed the connection
                programs_incoming_messages(f"Connection closed by server {addr}")
                break
            else:
                 #check if the received data starts with the usage info prefix
                if data.startswith(b"USAGE_INFO:"):
                    usage_info = json.loads(data[len("USAGE_INFO:"):].decode(format))
                    devices_usage_info[addr] = usage_info #adds usage info of server to dictionary
                else:
                    #process the received data as a regular message
                    msg = data.decode(format)
                    server_incoming_messages(f"Message from server{addr}: {msg}\n") #print response
        except ConnectionResetError:
            #connection reset by the server
            programs_incoming_messages(f"Connection reset by server {addr}")
            break
        if main_thread_ending.is_set(): #if main thread flag set close all threads
            programs_incoming_messages("Main thread is ending. Closing connection.")
            break

    conn.close()
    #remove the connection from the dictionary when it's closed
    del server_connections[addr]
    del devices_usage_info[addr]

def request_usage_info(): #request usage info from server
    while True:
        for address in server_connections: #sends message to each connected server
            send_to_server(address, "usage info")
        display_devices()
        time.sleep(1) #sleep timer as instantaneous update not required

def display_devices():
    devices_text_area.delete('1.0', tkinter.END)  # Clear existing content to ensure messages arent repeated
    for i, (address, pc_usage_info) in enumerate(devices_usage_info.items()):
        devices_text_area.insert(tkinter.END, f"Device {i + 1}\n") #insert device number
        devices_text_area.insert(tkinter.END, f"IP: {address[0]}\nPort:{address[1]}\n") #device address
        formatted_usage_data = "\n".join([f"{key}: {value}" for key, value in pc_usage_info.items()]) #process usage information to display it line by line
        devices_text_area.insert(tkinter.END, f"{formatted_usage_data}\n\n")

def send_to_server(server_addr, message):
    if server_addr in server_connections: #checks if server is connected
        server_conn = server_connections[server_addr]
        server_conn.send(message.encode(format)) #sends message to server in encoded format
    else:
        programs_incoming_messages("server not found.") #lets user know if server is not found

def start_usage_info_thread():
    global usage_info_thread
    if not usage_info_thread or not usage_info_thread.is_alive(): #to ensure the method does not try start a thread more than once
        usage_info_thread = threading.Thread(target=request_usage_info)
        usage_info_thread.daemon = True  # set the thread as a daemon so it exits when the main thread exits
        usage_info_thread.start()

def start():
    client.listen() #listens for connections
    programs_incoming_messages(f"[LISTENING] Client is listening on {host_IP}")

    while True:
        conn, addr = client.accept() #accepts the connection and assigns variable to be used
        server_connections[addr] = conn #saves server address
        thread = threading.Thread(target=server_handler, args=(conn, addr)) #starts separate thread to handle that server on its own
        thread.start()
        start_usage_info_thread() #start request info thread
        programs_incoming_messages(f"[ACTIVE CONNECTIONS] {len(server_connections)}") #lets user know current active connections

def start_server_thread():
    server_thread = threading.Thread(target=start) #starts a thread for start method so gui and method can run concurrently
    server_thread.start()
    start_button.pack_forget() #button is removed after initial press as it then becomes useless 

################################################################
# GUI Functions

def devices_incoming_text(text):
    devices_text_area.insert(tkinter.END, text + "\n") #inserts info in devices box
    devices_text_area.see(tkinter.END) #scrolls to last line to ensure users all information

def programs_incoming_messages(text):
    program_text_area.insert(tkinter.END, text + "\n") #inserts info in program messages box
    program_text_area.see(tkinter.END)

def server_incoming_messages(text):
    server_text_area.insert(tkinter.END, text + "\n") #inserts info in server messages box
    server_text_area.see(tkinter.END)

def on_closing():
    #set the main_thread_ending event before closing the GUI
    main_thread_ending.set()
    
    client.close() #closes socket
    client_GUI.destroy() #ends gui
    sys.exit() #exits program

def message_server():
    new_window = tkinter.Toplevel(client_GUI) #sets top level because this new window is a sub level window
    new_window.title("Message a server") #sets name

    main_width = client_GUI.winfo_width()
    main_height = client_GUI.winfo_height()

    # Calculate the x and y coordinates for the center of the main window
    x = client_GUI.winfo_rootx() + main_width // 2 - 70 #sets width size of window
    y = client_GUI.winfo_rooty() + main_height // 2 - 70 #sets height size of window

    # Set the position of the new window to be centered relative to the main window
    new_window.geometry(f"260x200+{x}+{y}") #adjusts window spawn area to my liking

    frame = tkinter.Frame(new_window) #creates new frame for new window
    frame.pack(padx=10, pady=10)

    #get available IPs and ports from devices_usage_info
    ips = [addr[0] for addr in devices_usage_info.keys()]
    ports = [str(addr[1]) for addr in devices_usage_info.keys()]

    tkinter.Label(frame, text='IP').grid(sticky="W")
    if not devices_usage_info:  #check if devices_usage_info is empty
        #if empty, create entry boxes for IP and port without dropdown menus
        ip_entry = tkinter.Entry(frame)
        ip_entry.grid(sticky="W")

        tkinter.Label(frame, text='Port').grid(sticky="W")
        port_entry = tkinter.Entry(frame)
        port_entry.grid(sticky="W")
    else:
        #get available IPs and ports from devices_usage_info
        ips = [addr[0] for addr in devices_usage_info.keys()]
        ports = [str(addr[1]) for addr in devices_usage_info.keys()]

        selected_ip = tkinter.StringVar(new_window)
        selected_ip.set(ips[0] if ips else '')  #set the default value if available, else set to empty string
        ip_dropdown = tkinter.OptionMenu(frame, selected_ip, *ips) #creates a dropdown for IPs and ports
        ip_dropdown.grid(sticky="W")

        tkinter.Label(frame, text='Port').grid(sticky="W")
        selected_port = tkinter.StringVar(new_window)
        selected_port.set(ports[0] if ports else '')  #set the default value if available, else set to empty string
        port_dropdown = tkinter.OptionMenu(frame, selected_port, *ports) #creates a dropdown for ports
        port_dropdown.grid(sticky="W")

    tkinter.Label(frame, text='Message').grid(sticky="W")
    message_entry = tkinter.Entry(frame) #creates entry for calculation
    message_entry.grid(sticky="W")
    
    def submit_button():
        sending_ip = selected_ip.get() #gets ip address selected
        sending_port = int(selected_port.get()) #gets port address selected
        sending_message = message_entry.get() #gets calculation inputed selected
        server_address = (sending_ip, sending_port) #makes variable for server address
        send_to_server(server_address, sending_message) #sends off message to that server address
        new_window.destroy()  #close the new window after sending the message
    
    submit_button = tkinter.Button(frame, text="Send", command=submit_button) #creates a submission button
    submit_button.grid(pady=10)

################################################################
# GUI tkinter settings

client_GUI = tkinter.Tk() #creates gui window
client_GUI.title("Intelligent Job Scheduler") #name of window

client_GUI.protocol("WM_DELETE_WINDOW", on_closing) #protocol linked to a method when window is closed

button_frame = tkinter.Frame(client_GUI) #created a frame for the buttons
button_frame.pack(anchor='nw', padx=10, pady=10)

frame1 = tkinter.Frame(client_GUI) #frame for devices list
frame1.pack(side=tkinter.LEFT, padx=10, pady=10)

frame2 = tkinter.Frame(client_GUI) #frame for program and server messages
frame2.pack(side=tkinter.LEFT, padx=10, pady=10)

devices_label = tkinter.Label(frame1, text="Devices") #label for devices area
devices_label.pack(anchor=tkinter.W)

devices_text_area = tkinter.Text(frame1, height=42, width=140) #created text box for devices list

devices_text_area.pack(pady=5)

program_messages_label = tkinter.Label(frame2, text="Program messages") #label for program messages box
program_messages_label.pack(anchor=tkinter.W)

program_text_area = tkinter.Text(frame2, height=20, width=80) #created text box for program messages
program_text_area.pack(pady=5)

server_messages_label = tkinter.Label(frame2, text="Server messages") #label for server messages box
server_messages_label.pack(anchor=tkinter.W)

server_text_area = tkinter.Text(frame2, height=20, width=80) #created text box for server messages
server_text_area.pack(pady=5)

start_button = tkinter.Button(button_frame, text="Start Program", command=start_server_thread) #created start button linked to start thread method
start_button.pack(side=tkinter.LEFT, padx=5)

send_message_to_server_button = tkinter.Button(button_frame, text="Message a server", command=message_server) #created message button linked to message server method
send_message_to_server_button.pack(side=tkinter.LEFT, padx=5)


programs_incoming_messages("Intelligent Job Scheduler") #title
programs_incoming_messages(f"Client IP: {host_IP}")
programs_incoming_messages("[STARTING] server is starting...")

client_GUI.mainloop() #launches GUI window