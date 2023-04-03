import _thread
import time
import network
import decompile_packet as dp
import sockettransmission_receiver as strev

SSID = 'supercoolnetwork'
PASSWD = 'letmeinfuck'

wlan = network.WLAN(network.STA_IF)
wlan.active(True)

def ap_connect() -> None:
    """Connect to access point

    Args:

    Returns:
        None:
    """
    wlan.connect(SSID, PASSWD)
    max_wait = 10
    while max_wait > 0:
        if wlan.status() < 0 or wlan.status() >= 3:
            break
        max_wait -= 1

        time.sleep_ms(1000)

    if wlan.status() != 3:
        raise RuntimeError('Network Connection Failed')

ap_connect()


def socket_thread() -> None:
    """Socket thread for recieving packets

    Args:

    Returns:
        None:
    """
    while True:
        packet = strev.receive_packet()
        clk, paramlist, devices = dp.decompile(packet)
        print(clk, paramlist, devices)

thread = _thread.start_new_thread(socket_thread, ())

while True:
    time.sleep(5)
    print('Still running')
