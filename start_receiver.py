# start_receiver.py

# imports
import socket

# create socket
def start_start_socket():
    start_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    start_sock.bind(('', 6969))
    return start_sock

def receive_start(sock) -> bool:
    """function for starting data transfer.

    Args:

    Returns:
        bool:
    """

    # returns true if start signal is received
    if sock.recvfrom(1024):
        sock.close()
        return True
    return False
