import random
from datetime import datetime
import pytz

def heat_pump_time(kwh: float, clock: int, lastclock: int, variance: float) -> float:
    """Simulate the powerdraw of a heatpump.

    Args:
        kwh (float): KiloWattHours
        clock (int): Current Clock in unix time
        lastclock (int): Last registered clock in unix time
        variance (float): Powerdraw variance in percent.

    Returns:
        float: Powerdraw from heatpump in KWh
    """
    if 0 > variance or variance > 1: raise ValueError(f"{int(variance * 100)}% is an invalid variance")
    kws = kwh/24/60/60
    dtime = clock-lastclock
    clockdate = datetime.fromtimestamp(clock, tz = pytz.timezone('Europe/Copenhagen'))
    chances = {
        range(0,6): 0.4,
        range(6,9): 0.8,
        range(9,18): 0.3,
        range(17,24): 0.8
    }
    chance = 0.0
    for key in chances:
        if clockdate.hour in key:
            chance = chances[key]
            break

    if random.uniform(0,1) <= chance:
        kws_swing = kws * random.uniform(-variance, variance)
        return (kws+kws_swing)*dtime
    return 0
