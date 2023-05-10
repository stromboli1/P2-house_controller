import socket

start_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
start_sock.bind(('', 6969))

def receive_start() -> bool:
    if start_sock.recv(1024):
        start_sock.close()
        return True
    return False

def receive_stop() -> bool:
    if not start_sock.recv(1024):
        start_sock.close()
        return True
    return False
