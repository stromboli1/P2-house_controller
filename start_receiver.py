# imports
import socket

# create socket
def start_start_socket():
    start_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    start_sock.bind(('', 6969))

def receive_start() -> bool:
    """function for starting data transfer.

    Args:

    Returns:
        bool:
    """

    # returns true if start signal is received
    if start_sock.recv(1024):
        start_sock.close()
        return True
    return False
