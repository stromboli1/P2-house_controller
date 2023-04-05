import socket

PORT = 42069

soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
soc.bind(('0.0.0.0',PORT))
soc.listen(1)

def receive_packet():
    print('Ready for accepting')
    c, _ = soc.accept()
    data = c.recv(2048)
    c.close()
    return data
