""" This script contains the dryer model for the power consumption simulation.

"""

import random
import function_script as fs

dryer_flag = 0
flag_time = 0
saved_consumption = 0
duration_time = random.randint(3400, 7200)

# The following dictionary is used for storing the different decimal
# percentiles for the dryer to be turned on during a single day.
time_dict = {0: 0.02,
             1: 0.01,
             2: 0.01,
             3: 0.01,
             4: 0.01,
             5: 0.01,
             6: 0.03,
             7: 0.05,
             8: 0.04,
             9: 0.03,
             10: 0.02,
             11: 0.02,
             12: 0.02,
             13: 0.03,
             14: 0.06,
             15: 0.15,
             16: 0.16,
             17: 0.23,
             18: 0.32,
             19: 0.38,
             20: 0.40,
             21: 0.30,
             22: 0.15,
             23: 0.8}
          


def dryer(kWh, time):
    """ The dryer function is used to simulate the use of a dryer in 
    a household. 
    
    The inputs in the function is the average power consumption
    from a single drying cycle, and the time of the day written in seconds 
    from midnight.

    The fuction will return either a value, based on the power consumption
    value given as an input, or a zero if the dryer was not used. Furthermore the power consumption which is returned fluctuates a small amount to give
    a more realistic output.
    
    """

    global dryer_flag
    global time_dict
    global flag_time
    global saved_consumption
    global duration_time

    weight = time_dict[fs.second_to_hour(time)]

    chance_per_hour = random.randint(0,3600)
    on_chance = random.random()
    
    
    if chance_per_hour == 0 and on_chance <= weight and dryer_flag == 0:
        kWh = float(kWh)
        uncertainty = float(random.randint(-2, 5)/100)
        consumption = kWh
        consumption += uncertainty
        consumption = consumption
        dryer_flag = 1
        flag_time = time
        saved_consumption = consumption
        return(consumption)
    
    elif dryer_flag == 1:
        flag_time_diff = time - flag_time
        if flag_time_diff < duration_time:
            return(saved_consumption)
        else:
            return(0)
        
    else:
        return(0)
    
