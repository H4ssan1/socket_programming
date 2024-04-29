import socket

sock = socket.socket()
print("socket success")

port = 7000

sock.bind(('', port))
print("socket binded to %s" %(port))

sock.listen(5)
print("socket listening")

while True:
    c, address = sock.accept()
    print('got connection from', address)

    c.send('thanks for connecting'.encode())

    c.close()

    break