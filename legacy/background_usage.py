""" The background_usage module is used to simulate additional power 
consumption in a household, from lights, small appliances ect.

"""

import random
import function_script as fs

# The following dictionary is used for a standard background power 
# consumption, based on an estimate of the daily fluctuation in such 
# consumption.
time_dict = {0: 0.30,
             1: 0.30,
             2: 0.30,
             3: 0.30,
             4: 0.30,
             5: 0.30,
             6: 0.32,
             7: 0.36,
             8: 0.38,
             9: 0.35,
             10: 0.32,
             11: 0.32,
             12: 0.35,
             13: 0.38,
             14: 0.38,
             15: 0.40,
             16: 0.45,
             17: 0.48,
             18: 0.51,
             19: 0.51,
             20: 0.51,
             21: 0.45,
             22: 0.40,
             23: 0.30}

def background_usage(time):
    """ The background_usage function is used to simulate the power 
    consumption, which is not from the use of a dryer or oven.

    As input, it takes a time of day, given in seconds from midnight.

    The function returns the power usage from that given time of day.

    """

    global time_dict
    usage = random.uniform(-0.05, 0.05) + time_dict[fs.second_to_hour(time)]
    usage = "%.2f" % usage
    return(float(usage))

