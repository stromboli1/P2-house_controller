import socket

PORT = 42069

soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
soc.bind(('0.0.0.0',PORT))
soc.listen(1)

def receive_packet():
    c, a = soc.accept()
    return c.recv(2048)
