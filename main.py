# Import Modules
from typing import Optional
import socket
import json
from threading import Thread
from time import sleep

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
controlprotocolsock.listen()

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
        csock.close()
        return decompile_packet(packet)
    except:
        return None

# Make Appliances and House (TODO: Make the contants defined somewhere else, controlprotocol maybe?)
oven_coeff = [5.11972665e-04, -7.03402445e-04,  7.68026707e-04, -3.66363583e-04, 8.96781866e-05, -1.14300653e-05, 7.10339539e-07, -1.23448103e-08, -8.17581893e-10, 4.38334209e-11, -6.15768582e-13]
dryer_coeff = [2.99514846e-04, 5.92930103e-04, -9.95959187e-04, 5.19274499e-04, -1.33220995e-04, 1.99077151e-05, -1.84839322e-06, 1.07680202e-07, -3.80412797e-09, 7.40399062e-11, -6.06187573e-13]
bg_coeff = [ 2.99994599e-01, -5.51791329e-04, -4.13148994e-02,  2.10030766e-02, -4.10493904e-03,  4.10768972e-04, -2.29920196e-05,  7.26545140e-07, -1.20913754e-08,  8.21833884e-11]

# Creating oven appliance for house
oven = Oven(power_usage=1.1, power_fluctuation=0.02, controllable=False, state_coeffs=oven_coeff, allowed_cycles=1, cycle_time_range=(30, 120))

# Creating dryer appliance for house
dryer = Dryer(power_usage=1.47, power_fluctuation=0.02, controllable=False, state_coeffs=dryer_coeff, allowed_cycles=1, cycle_time_range=(60,120))

# Creating heatpump appliance for house
heatpump = Heatpump(1.5, 0, True, heating_multiplier=1, heating_fluctuation=0.05, target_temperature=20.5)

house = House('e', 300, 3, 21, 0, 212,[heatpump,dryer, oven], bg_coeff, 0.01, 0.01)

class HouseRunner(Thread):
    def run(self) -> None:
        while True:
            sleep(1)
            house.update_time(60)
            devicelist, powerusage, temperature, time = house.tick()
            devices = 0
            for i, device in enumerate(devicelist):
                devices += 2**i if device else 0
            print(devicelist, devices, powerusage, temperature, time)
            transmit_data("10.10.0.1", 42070, devices, powerusage, temperature, time)

class CommandListener(Thread):
    def run(self) -> None:
        while True:
            packet = receive_controlpacket()
            if packet == None:
                continue
            lock_flag = not packet[0] & 4 > 0
            heatpump.power_locker(lock_flag)


houserunner = HouseRunner()
houserunner.start()

commandlistener = CommandListener()
commandlistener.start()

# TODO: Implement the code so it works
