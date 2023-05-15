# Import Modules
from typing import Optional
import socket
import json
from threading import Thread
from time import sleep

# Own modules
from communication_utils import decompile_packet, datatrans_packetinator, receive_signal
from models import House, Heatpump, Oven, Dryer


# GLOBAL VARS
CONTROLPROTOCOLPORT: int = 42069
STOPTHREADS = False

with open('coefficients.json', 'r') as fd:
    coefficients = json.load(fd)

with open('house_settings.json', 'r') as fd:
    house_setting = json.load(fd)

with open('appliance_data.json', 'r') as fd:
    appliance_data = json.load(fd)

# Global sockets (CANNOT be recovered if they crash)
datasock: socket.socket = socket.socket(
        socket.AF_INET,
        socket.SOCK_DGRAM
        )

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


def receive_controlpacket() -> Optional[tuple[int, int, dict, int]]:
    try:
        csock, _ = controlprotocolsock.accept()
        packet = csock.recv(1024)
        csock.close()
        return decompile_packet(packet)
    except Exception as e:
        print(e)
        return None

# Configure the settings depending of the house number
house_nr = input("House Nr: ")
house_data = house_setting[house_nr]

# Configure the oven, according to the house number
oven_model = house_data["oven"]
oven_mode = house_data["mode"]
oven_dict = appliance_data["oven"]
oven_model_dict = oven_dict[oven_model]
oven_data = oven_model_dict[oven_mode]

# Configure the dryer, according to the house number
dryer_dict = appliance_data["dryer"]
dryer_data = dryer_dict[house_data["dryer"]]

# Configure the heat pumps target temperature, according to house number
hp_target = house_data["target temperature"]

# Creating a list with all the settings for the house object.
hd = [house_data["energy rating"], house_data["size"], house_data["height"], \
      house_data["start temperature"], house_data["start time"], \
      house_data["active days"]]

# Setting the different coefficients for the appliances.
"""
oven_coeff = coefficients["oven"]
dryer_coeff = coefficients["dryer"]
bg_coeff = coefficients["background"]
"""

oven_coeff = 1
dryer_coeff = 1
bg_coeff = 0.51

# Make Appliances and House (TODO: Make the contants defined somewhere else, controlprotocol maybe?)

# Creating oven appliance for house
oven = Oven(power_usage=oven_data, power_fluctuation=0.02, controllable=False, state_coeffs=oven_coeff, allowed_cycles=1, cycle_time_range=(30, 120))

# Creating dryer appliance for house
dryer = Dryer(power_usage=dryer_data, power_fluctuation=0.02, controllable=False, state_coeffs=dryer_coeff, allowed_cycles=1, cycle_time_range=(60,120))

# Creating heat pump appliance for house
heatpump = Heatpump(1.5, 0, True, heating_multiplier=3, heating_fluctuation=0.05, target_temperature=hp_target)

# Creating the house object.
house = House(hd[0], hd[1], hd[2], hd[3], hd[4], hd[5], [heatpump, dryer, oven], bg_coeff, 0.01, 0.01)

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
            if STOPTHREADS:
                break

class CommandListener(Thread):
    def run(self) -> None:
        global STOPTHREADS
        while True:
            packet = receive_controlpacket()
            print(packet)
            if packet == None:
                continue
            if packet[0] & 8 > 0:
                lock_flag = not packet[0] & 4 > 0
                print(lock_flag)
                heatpump.power_locker(lock_flag)
                print(heatpump._power_lock)

            # Check if clk flag in packet is set
            if packet[0] & 1 > 0:
                if packet[1] > house.time:
                    # Set house clk to recieved clk in the packet
                    house.set_time(packet[1])

            if STOPTHREADS:
                break

start_received = False

print("Ready for Area Controller")

while not start_received:
    if receive_signal():
        start_received = True

houserunner = HouseRunner()
houserunner.start()

commandlistener = CommandListener()
commandlistener.start()

while True:
    if not receive_signal():
        STOPTHREADS = True
        break

# TODO: Implement the code so it works
