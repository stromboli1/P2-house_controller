import threading
import socket
import time
import decompile_packet as dp
import sockettransmission_receiver as strev

def socket_thread() -> None:
    """Socket thread for recieving packets

    Args:

    Returns:
        None:
    """
    while True:
        packet = strev.receive_packet()
        print(packet)
        clk, paramlist, devices = dp.decompile(packet)
        print('\n', clk, paramlist, devices)


thread = threading.Thread(target = socket_thread, args = ())
thread.start()

while True:
    time.sleep(5)
    print('Still running')
