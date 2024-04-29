#####Imported various libraries for use within my project
import socket
import select
import time
import sys
import json
import psutil
import threading

port_no = 12000 # port number for servers to connect to
HEADER = 64 # header space
host_IP = "192.168.0.72" # host ip for socket to binded to
format = 'UTF-8' # encoding format for messages to be sent out
ADDR = (host_IP, port_no)

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # creation of TCP socket
server.connect(ADDR) #connect to socket with selected address
status = 'F' # default status code for server
tasks = 0 #default task count for server

def server_running():
    global status
    global tasks
    while True:
        #check if there's data to be received
        ready_to_read, _, _ = select.select([server], [], [], 30) #if no messages be sent from client then break
        if not ready_to_read: 
            print("Nothing has been received for 30 seconds. Exiting...")
            server.close()
            sys.exit()  #exit the program
        for sock in ready_to_read: #if socket connected
            if sock == server:
                message_received = server.recv(2048).decode(format) #decode received message
                if message_received == "usage info": #if the client requires usage info then send it
                    system_info_thread = threading.Thread(target=send_system_info) #starts thread for the method that send usage info of server
                    system_info_thread.start()
                else: 
                    print(f"Algorithm sent from client ({ADDR}): {message_received}") #show the message sent from client
                    status = 'B' #status is now busy as it has to deal with request
                    tasks += 1 #task count increased
                    process_algorithms_thread = threading.Thread(target=process_algorithms, args=(message_received,)) #start thread for method that deals with calculations
                    process_algorithms_thread.start()

def send_system_info():
    system_info = get_system_info() #gets usage info
    server.sendall(("USAGE_INFO:" + json.dumps(system_info)).encode(format)) #sends usage info as JSON data

def get_system_info():
    memory = psutil.virtual_memory() #get memory usage information
    total_memory_gb = round(memory.total / (1024 ** 3), 1)  #convert bytes to gigabytes and round to 1 decimal place
    available_memory_gb = round(memory.available / (1024 ** 3), 1)  #convert bytes to gigabytes and round to 1 decimal place
    return { #presents usage info in desired format
        "CPU usage": f"{psutil.cpu_percent(interval=1)}%",
        "Memory usage": f"{memory.percent}%",
        "Memory total": f"{total_memory_gb}GB",
        "Memory available": f"{available_memory_gb}GB",
        "Status": status,
        "Tasks": tasks
    }

def process_algorithms(algorithm):
    global status
    global tasks
    operation_found = False #variable to check if operation is found
    ##variables for calculation
    first_num = ""
    operation = ""
    second_num = ""
    calculated_operation = 0
    for numerical in algorithm:
        if operation == "" and (numerical == "+" or numerical == "-" or numerical == "*" or numerical == "/"): #checks message that its truly a calculation
            # and separates it into a format that can be used for calculation
            operation = numerical
        elif operation == "":
            first_num += numerical
        else:
            second_num += numerical
    
    if operation == "+": #if addition then add and round to 3 decimal places
        calculated_operation = round(int(first_num) + int(second_num),3)
        operation_found = True

    elif operation == "-": #if subtraction then substract them and round to 3 decimal places
        calculated_operation = round(int(first_num) - int(second_num),3)
        operation_found = True

    elif operation == "*": #if multiplication then multiply and round to 3 decimal places
        calculated_operation = round(int(first_num) * int(second_num),3)
        operation_found = True

    elif operation == "/": #if division then divide and round to 3 decimal places
        calculated_operation = round(int(first_num) / int(second_num),3)
        operation_found = True

    else:
        print("No operation was found") #lets server know there was no operation found
        send_to_client("Resend calculation. No operation was found") #lets client know there was no operation found

    if operation_found == True:
        time.sleep(15) #sleep timer to simulate slow processes and see true functionality of program
        tasks -= 1 #if task complete then count is decremented
        send_to_client(F"{algorithm} = {str(calculated_operation)}") #sends result to client
        if tasks == 0: #sets status of server back to free if no more tasks left to do 
            status = 'F'

def send_to_client(result):
    message = result.encode(format) #encodes message 
    server.send(message) #sends it to client

server_running() #runs main method