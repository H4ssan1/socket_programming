import socket
import select
import time
import sys

port_no = 12000
HEADER = 64
host_IP = "192.168.0.72"
format = 'UTF-8'
DISCONNECT_MESSAGE = "!BREAK"
ADDR = (host_IP, port_no)

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.connect(ADDR)

def server_running():
    while True:
        # Check if there's data to be received
        ready_to_read, _, _ = select.select([server], [], [], 30)
        if not ready_to_read: 
            print("Nothing has been received for 30 seconds. Exiting...")
            sys.exit()  # Exit the program
        for sock in ready_to_read:
            if sock == server:
                message_received = server.recv(2048).decode(format)
                if message_received:
                    print(f"Algorithm sent from client ({ADDR}): {message_received}")
                    process_algorithms(message_received)

def process_algorithms(algorithm):
    first_num = ""
    operation = ""
    second_num = ""
    calculated_operation = 0
    for numerical in algorithm:
        if operation == "" and (numerical == "+" or numerical == "-" or numerical == "*" or numerical == "/"):
            operation = numerical
        elif operation == "":
            first_num += numerical
        else:
            second_num += numerical
    
    if operation == "+":
        calculated_operation = round(int(first_num) + int(second_num),3)
        time.sleep(10)
        send_to_client(str(calculated_operation))

    elif operation == "-":
        calculated_operation = round(int(first_num) - int(second_num),3)
        time.sleep(10)
        send_to_client(str(calculated_operation))

    elif operation == "*":
        calculated_operation = round(int(first_num) * int(second_num),3)
        time.sleep(10)
        send_to_client(str(calculated_operation))

    elif operation == "/":
        calculated_operation = round(int(first_num) / int(second_num),3)
        time.sleep(10)
        send_to_client(str(calculated_operation))

    else:
        print("No operation was found")
        send_to_client("Resend calculation. No operation was found")


def send_to_client(result):
    message = result.encode(format)
    server.send(message)

server_running()