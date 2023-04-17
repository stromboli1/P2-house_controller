# Import Modules
import socket

sock: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('', 6969))

def recv_broadcast() -> bytes:
    """Receive broadcast signal.

    Args:

    Returns:
        bytes: signal
    """
    b, _ = sock.recvfrom(256)
    return b
