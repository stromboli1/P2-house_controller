import socket

def receive_start() -> bool:
    start_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    start_sock.bind(('', 6969))
    if start_sock.recv(1024):
        start_sock.close()
        return True
    return False

