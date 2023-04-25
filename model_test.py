import models as mod
import matplotlib.pyplot as plt

consumption_list = []
on_list = []
average = []
x_list = []
minutes = 1440
days = 1

oven_coeff = [5.11972665e-04, -7.03402445e-04,  7.68026707e-04, -3.66363583e-04, 8.96781866e-05, -1.14300653e-05, 7.10339539e-07, -1.23448103e-08, -8.17581893e-10, 4.38334209e-11, -6.15768582e-13]

dryer_coeff = [2.99514846e-04, 5.92930103e-04, -9.95959187e-04, 5.19274499e-04, -1.33220995e-04, 1.99077151e-05, -1.84839322e-06, 1.07680202e-07, -3.80412797e-09, 7.40399062e-11, -6.06187573e-13]


bg_coeff = [ 2.99994599e-01, -5.51791329e-04, -4.13148994e-02,  2.10030766e-02, -4.10493904e-03,  4.10768972e-04, -2.29920196e-05,  7.26545140e-07, -1.20913754e-08,  8.21833884e-11]

# Creating oven appliance for house
oven = mod.Oven(power_usage=1.1, power_fluctuation=0.02, controllable=False, state_coeffs=oven_coeff, allowed_cycles=1, cycle_time_range=(30, 120))

# Creating dryer appliance for house
dryer = mod.Dryer(power_usage=1.47, power_fluctuation=0.02, controllable=False, state_coeffs=dryer_coeff, allowed_cycles=1, cycle_time_range=(60,120))

# Creating heatpump appliance for house
heatpump = mod.Heatpump(1.5, 0, True, heating_multiplier=3, heating_fluctuation=0.05, min_temperature=20.5, max_temperature=21.4)

# Creating house with appliances
house = mod.House('d', 150, 2.8, 22, 0, 212,[], bg_coeff, 0.01)

for minut in range(minutes):
    average.append(minut)
    x_list.append(minut)

for n in range(days):
    day_list = []
    for i in range(minutes):
        house.update_time(60)
        state, draw, temp, time = house.tick()
        day_list.append(draw)
    consumption_list.append(day_list)


for i in range(minutes):
    sum = 0
    for n in range(1):
        sum += consumption_list[n][i]
    average[i] = sum/days

plt.plot(x_list, average)
plt.show()
