# Import Modules
from typing import Optional
import socket
import json

# Own modules
from communication_utils import decompile_packet, datatrans_packetinator
from models import House, Heatpump, Oven, Dryer

# GLOBAL VARS
STARTSTOPPORT: int = 6969
CONTROLPROTOCOLPORT: int = 42069

# Global sockets (CANNOT be recovered if they crash)
datasock: socket.socket = socket.socket(
        socket.AF_INET,
        socket.SOCK_DGRAM
        )

startstopsock: socket.socket = socket.socket(
        socket.AF_INET,
        socket.SOCK_DGRAM
        )
startstopsock.bind(('', STARTSTOPPORT))

controlprotocolsock: socket.socket = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM
        )
controlprotocolsock.bind(('', CONTROLPROTOCOLPORT))

def transmit_data(
        target_ip: str,
        port: int,
        devices: int,
        powerusage: float,
        temperature: float,
        time: int
        ) -> None:

    # Make the packet
    packet: bytes = datatrans_packetinator(
            devices,
            powerusage,
            temperature,
            time
            )

    datasock.sendto(packet, (target_ip, port))

def listen_for_startstop() -> Optional[bool]:

    try:
        sig, _ = startstopsock.recvfrom(128)
        return sig[0] > 0
    except:
        return None

def receive_controlpacket() -> Optional[tuple[int, int, dict, int]]:
    try:
        csock, _ = controlprotocolsock.accept()
        packet = csock.recv(1024)
        return decompile_packet(packet)
    except:
        return None





