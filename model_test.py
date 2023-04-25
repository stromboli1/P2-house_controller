import models as mod
import matplotlib.pyplot as plt

oven_coeff = [3.23654726e-02, -8.87464977e-02, 1.10875118e-01, -5.55039379e-02, 1.41481147e-02, -2.00354900e-03, 1.63395561e-04, -7.60766518e-06,
 1.87551879e-07, -1.89766897e-09]

dryer_coeff = [ 1.79708907e-02,  3.55758062e-02, -5.97575512e-02,  3.11564699e-02,
-7.99325968e-03,  1.19446290e-03, -1.10903593e-04,  6.46081210e-06,
-2.28247678e-07,  4.44239437e-09, -3.63712544e-11]

heatpump_coeff = [ 3.78897407e-01,  6.42680175e-01, -8.59110854e-01,  4.11481727e-01, -9.78468135e-02,  1.34481405e-02, -1.14484299e-03,  6.15032763e-05, -2.03241753e-06,  3.77414792e-08, -3.01481897e-10]

bg_coeff = [ 2.99668164e-01, -2.71379376e-02,  5.62845605e-02, -3.89511608e-02,1.25851865e-02, -2.19645119e-03,  2.24538898e-04, -1.38772202e-05,5.11234640e-07, -1.03491589e-08,  8.87078335e-11]

oven = mod.Oven(power_usage=1.1, power_fluctuation=0.02, controllable=False, state_coeffs=oven_coeff, allowed_cycles=1, cycle_time_range=(30, 120))


dryer = mod.Dryer(power_usage=1.47, power_fluctuation=0.02, controllable=False, state_coeffs=dryer_coeff, allowed_cycles=1, cycle_time_range=(60,120))


heatpump = mod.Heatpump(1.5, 0.2, True, heating_multiplier=3, heating_fluctuation=0.2, min_temperature=20.5, max_temperature=21.4)

house = mod.House('d', 150, 2.8, 21, 0, 212, [oven, dryer, heatpump], bg_coeff, 0.05)

comp_list = []
on_list = []
average = []

for i in range(1440):
    average.append(i)


for n in range(100):
    day_list = []
    for i in range(1440):
        house.update_time(60)
        state, draw, temp = house.tick()
        day_list.append(state)
    on_list.append(day_list)

for n in range(100):
    print(on_list[n][1379])

"""
for n in range(100):
    day_list = []
    for i in range(1440):
        house.update_time(60)
        state, draw, temp = house.tick()
        day_list.append(draw)
    comp_list.append(day_list)



for i in range(1440):
    sum = 0
    for n in range(100):
        sum += comp_list[n][i]
    average[i] = sum/100

x_list = []

for i in range(1440):
    x_list.append(i)

plt.plot(x_list, average)
plt.show()
"""