
def decompile(packet: bytes) -> tuple[int, int, list[bytes], int]:
    """Decompiles the packet and extracts parameters

    Args:
        packet (bytes): A packet to be decompiled

    Returns:
        tuple[int, bytes, list[bytes], int]: Decompiled parameters
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
    if self.flags & 2 > 0:
        paramnum = self.packet[cursor]
        cursor += 1

        paramlist = []
        for _ in range(paramnum):
            paramid = self.packet[cursor]
            paramsize = self.packet[cursor+1]
            cursor += 2
            paramdata = self.packet[cursor:cursor+paramsize]
            cursor += paramsize
            parambytes = paramid.to_bytes(1, 'big') + paramsize.to_bytes(1, 'big') + paramdata
            paramlist.append(parambytes)

        cursor += 1

    # Decompile devices
    if flags & 8 > 0:
        devices = packet[cursor]
        cursor += 1

    return (flags, clk, paramlist, devices)
