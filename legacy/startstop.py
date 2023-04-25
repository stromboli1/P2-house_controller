# Import Modules
import socket

sock: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('', 6969))

def recv_broadcast() -> int:
    """Receive broadcast signal.

    Args:

    Returns:
        int: signal
    """
    sig, _ = sock.recvfrom(256)[0]
    return sig
