""" This fuction script is meant to be used with dryer_model module, 
oven_model module and background_usage module.

The script contains several functions related to simulating the 
power consumption in a household.

"""

import dryer_model as dm
import oven_model as om
import background_usage as bgu

# A global dictionary for storing power consumption in.
power_dict = {}

def sim_day(dryer_value, oven_value):
    """ The sim_day function is used to simulate a whole day of power 
    consumption in a single household.

    It takes the average power consumption of the chosen oven and dryer as 
    inputs.

    The output of the function is a list of power consumption, based on the values returned by the dryer model, oven model and background usage model. The list is 86400 data points long, which makes up each second of 24 hours.

    """

    consumption_list = []
    for i in range(86400):
        dryer = dm.dryer(dryer_value, i)
        oven = om.oven(oven_value, i)
        power_consumption = float(dryer) + float(oven)
        power_consumption += bgu.background_usage(i)
        power_consumption = "%.2f" % power_consumption
        power_consumption = float(power_consumption)/3600
        consumption_list.append(float(power_consumption))
    return(consumption_list)

def sim_second(dryer_value, oven_value, time_in_second):
    """ The sim_second function is used to simulate a single second of power 
    consumption in a single household.

    It takes the average power consumption of the chosen oven and dryer as 
    inputs.

    The output of the function is the power consumption, based on the values returned by the dryer model, oven model and background usage model.

    """

    dryer = dm.dryer(dryer_value, time_in_second)
    oven = om.oven(oven_value, time_in_second)
    power_consumption = float(dryer) + float(oven)
    power_consumption += bgu.background_usage(time_in_second)
    power_consumption = float(power_consumption)/3600
    power_consumption = "%.2f" % power_consumption
    return(float(power_consumption))


def new_day():
    """ The new_day function is used to reset several key variables and
    the power_dict. This is used before simulating a new day.

    """
    global power_dict
    power_dict = {}
    dm.dryer_flag = 0
    om.oven_flag = 0

def power_data_dict(dryer_value, oven_value):
    """ The power_data_dict function is used to simulate 24 hours of 
    power consumption in a single household. The consumption is then
    stored in the global dictionary 'power_dict.'

    It takes the average power consumption of the chosen oven and dryer as 
    inputs.

    The function does not return anything, but simply writes the results of 
    the simulation in the power_dict.

    """
    global power_dict
    power_list = sim_day(dryer_value, oven_value)
    for i in range(len(power_list)):
        power_dict[i] = power_list[i]


def second_to_hour(second_time):
    """ The second_to_hour function floor divides the time given as input 
    by 3600, as to change it into the correct hour of the day.

    Midnight (00:00) is second_time=0. 
    """
    hour_time = second_time//3600
    return(hour_time)


def power_usage(time):
    """ The power_usage function is used to return the power consumption from 
    a specific time, given in seconds from midnight.

    """
    global power_dict
    return(power_dict[time])

def sim_10_seconds(dryer_value, oven_value, start_time_in_second):
    """ The sim_10_seconds function simulates the power consumption of a 
    household for a 10 second period.

    It takes the average power consumption of a oven and dryer, as well as 
    the start time, which is given in seconds from midnight.

    It returns the sum of the power consumption from the 10 seconds.

    """
    power_consumption = 0
    time = start_time_in_second
    for sim_nr in range(10):
        power_consumption += sim_second(dryer_value, oven_value, 
                                        time)
        time += 1
    return(power_consumption)



