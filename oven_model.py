import random
import function_script as fs

oven_flag = 0
flag_time = 0
saved_consumption = 0
duration_time = random.randint(3400, 7200)

time_dict = {0: 0.03,
             1: 0.02,
             2: 0.02,
             3: 0.02,
             4: 0.03,
             5: 0.04,
             6: 0.05,
             7: 0.07,
             8: 0.06,
             9: 0.02,
             10: 0.02,
             11: 0.02,
             12: 0.02,
             13: 0.04,
             14: 0.06,
             15: 0.15,
             16: 0.30,
             17: 0.35,
             18: 0.30,
             19: 0.30,
             20: 0.10,
             21: 0.08,
             22: 0.06,
             23: 0.04}
          


def oven(kWh, time):
    """ The oven function is used to simulate the use of a oven in 
    a household. 
    
    The inputs in the function is the average power consumption
    from a single cycle, and the time of the day written in seconds 
    from midnight.

    The fuction will return either a value, based on the power consumption
    value given as an input, or a zero if the dryer was not used. Furthermore the power consumption which is returned fluctuates a small amount to give
    a more realistic output.

    """

    global oven_flag
    global time_dict
    global flag_time
    global saved_consumption
    global duration_time

    weight = time_dict[fs.second_to_hour(time)]
    
    chance_per_hour = random.randint(0,3600)
    on_chance = random.random()

    if chance_per_hour == 0 and on_chance <= weight and oven_flag == 0:
        kWh = float(kWh)
        uncertainty = float(random.randint(-2, 5)/100)
        consumption = kWh
        consumption += uncertainty
        oven_flag = 1
        flag_time = time
        saved_consumption = consumption
        return(consumption)
            
    elif oven_flag == 1:
        flag_time_diff = time - flag_time
        if flag_time_diff < duration_time:
            return(saved_consumption)
        else:
            return(0)
    else:
        return(0)


