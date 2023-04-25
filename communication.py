# Import Modules
from typing import Optional
import socket
import json
from concurrent.futures import ThreadPoolExecutor

# Own modules
from communication_utils import decompile_packet, datatrans_packetinator

# GLOBAL VARS
STARTSTOPPORT: int = 6969

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








# TODO: Threading and other stupid shit
