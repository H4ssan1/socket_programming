import tkinter

# Declare global variables for text areas and GUI window
devices_text_area = tkinter.Text()
program_text_area = tkinter.Text
server_text_area = tkinter.Text

def __init__():
    global devices_text_area, program_text_area, server_text_area
    
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

    client_GUI.mainloop() 

def devices_incoming_text(text):
    devices_text_area.insert(tkinter.END, text + "\n")
    devices_text_area.see(tkinter.END)

def programs_incoming_messages(text):
    program_text_area.insert(tkinter.END, text + "\n")
    program_text_area.see(tkinter.END)

def server_incoming_messages(text):
    server_text_area.insert(tkinter.END, text + "\n")
    server_text_area.see(tkinter.END)
