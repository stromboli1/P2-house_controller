
def decompile(packet: bytes) -> tuple[bytes, list[bytes], bytes]:
    """Decompiles the packet and extracts parameters

    Args:
        packet (bytes): A packet to be decompiled

    Returns:
        tuple[bytes, list[bytes], bytes]: Decompiled parameters
    """

    # Set variables
    cursor = 1
    flags = packet[0]
    clk = None
    devices = None
    paramlist = None

    # Decompile clock sync
    if flags & 1 > 0:
        clk = packet[cursor:cursor+4]
        cursor += 4

    # Decompile devices
    if flags & 8 > 0:
        devices = packet[cursor].to_bytes(1, 'big')
        cursor += 1

    return (clk, paramlist, devices)
