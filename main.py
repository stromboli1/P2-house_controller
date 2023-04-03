import _thread
import utime
import decompile_packet as dp
import sockettransmission_receiver as strev

def socket_thread():
    while True:
        packet = strev.receive_packet()
        clk, paramlist, devices = dp.decompile(packet)
        print(clk, paramlist, devices)

thread = _thread.start_new_thread(socket_thread(), ())

while True:
    utime.sleep(5)
    print('Still running')
