import struct
import socket

ADDR: tuple[str, int] = ("10.10.0.1", 42070)

soc: socket.socket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)

def send_data_packet(devices: int, powerusage: float, temperature: float, time: int) -> None:
    """Sends data as a UDP packet to the Area Controller.

    Args:
        devices (int): devices
        powerusage (float): powerusage
        temperature (float): temperature
        time (int): time

    Returns:
        None:
    """
    packet: bytes = b''

    packet += devices.to_bytes(1, 'big')
    packet += struct.pack('f', powerusage)
    packet += struct.pack('f', temperature)
    packet += time.to_bytes(4, 'big')

    soc.sendto(packet, ADDR)
