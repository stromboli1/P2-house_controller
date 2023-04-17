# Import Modules
import struct
import socket

# Address of the Area Controller
ADDR: tuple[str, int] = ("10.10.0.1", 42070)

# Make socket object
soc: socket.socket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)

def send_data_packet(devices: int, powerusage: float, temperature: float, time: int) -> None:
    """Sends data as a UDP packet to the Area Controller.

    Args:
        devices (int): Device state
        powerusage (float): The amount of powerusage
        temperature (float): The temperature in the house
        time (int): Unix timestamp

    Returns:
        None:
    """

    # Define packet byte object
    packet: bytes = b''

    # Add data to the packet
    packet += devices.to_bytes(1, 'big')
    packet += struct.pack('f', powerusage)
    packet += struct.pack('f', temperature)
    packet += time.to_bytes(4, 'big')

    # Send the packet
    soc.sendto(packet, ADDR)
