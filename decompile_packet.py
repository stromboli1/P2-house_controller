import json
import struct

with open('param_oracle.json', 'r') as fp:
    param_oracle = json.load(fp)

def decompile(packet: bytes) -> tuple[int, int, dict, int]:
    """Decompiles the packet and extracts parameters

    Args:
        packet (bytes): A packet to be decompiled

    Returns:
        tuple[int, int, dict, int]: Decompiled parameters
    """

    # Set variables
    cursor = 1
    flags = packet[0]
    clk = None
    devices = None
    paramlist = None

    # Decompile clock sync
    if flags & 1 > 0:
        clk = int.from_bytes(packet[cursor:cursor+4], 'big')
        cursor += 4

    # Decompile parameters
    if flags & 2 > 0:
        paramnum = packet[cursor]
        cursor += 1

        paramdict = {}
        for _ in range(paramnum):
            paramid = packet[cursor]
            paramsize = packet[cursor+1]
            cursor += 2
            paramdata = packet[cursor:cursor+paramsize]
            cursor += paramsize

            paramname = ''
            paramtype = ''
            for item in param_oracle.items():
                if item[1]['id'] == paramid:
                    paramname = item[0]
                    paramtype = item[1]['type']
                    break

            match paramtype:

                case 'int':
                    paramdict[paramname] = int.from_bytes(paramdata, 'big')

                case 'bool':
                    paramdict[paramname] = paramdata[0] > 0

                case 'float':
                    paramdict[paramname] = struct.unpack('>d', paramdata)[0]

                case _:
                    raise ValueError('Invalid type or id not found')

    # Decompile devices
    if flags & 8 > 0:
        devices = packet[cursor]
        cursor += 1

    return (flags, clk, paramdict, devices)
