import models as mod
import matplotlib.pyplot as plt

oven_coeff = [ 2.91224354e-02,  3.43245148e-02, -7.41751676e-02, 4.77055793e-02, -1.49646564e-02, 2.71775105e-03, -3.03456792e-04,  2.09968211e-05, -8.72185305e-07,  1.98402817e-08, -1.89451849e-10]

dryer_coeff = [ 1.79708907e-02,  3.55758062e-02, -5.97575512e-02,  3.11564699e-02,
-7.99325968e-03,  1.19446290e-03, -1.10903593e-04,  6.46081210e-06,
-2.28247678e-07,  4.44239437e-09, -3.63712544e-11]

heatpump_coeff = [ 3.78897407e-01,  6.42680175e-01, -8.59110854e-01,  4.11481727e-01, -9.78468135e-02,  1.34481405e-02, -1.14484299e-03,  6.15032763e-05, -2.03241753e-06,  3.77414792e-08, -3.01481897e-10]

bg_coeff = [ 2.99668164e-01, -2.71379376e-02,  5.62845605e-02, -3.89511608e-02,1.25851865e-02, -2.19645119e-03,  2.24538898e-04, -1.38772202e-05,5.11234640e-07, -1.03491589e-08,  8.87078335e-11]

oven = mod.Oven(power_usage=1.1, power_fluctuation=0.02, controllable=False, state_coeffs=oven_coeff, allowed_cycles=1, cycle_time_range=(1800, 7200))


dryer = mod.Dryer(power_usage=1.47, power_fluctuation=0.02, controllable=False, state_coeffs=dryer_coeff, allowed_cycles=1, cycle_time_range=(3600, 7200))


heatpump = mod.Heatpump(1.5, 0.2, True, state_coeffs=heatpump_coeff, allowed_cycles=144, cycle_time_range=(60,61), heating_multiplier=3, heating_fluctuation=0.2)

house = mod.House('d', 150, 2.8, 21, 0, 212, [oven, dryer, heatpump], bg_coeff, 0.05)

comp_list = []
average = []

for i in range(1440):
    average.append(i)

print(house.tick())



for i in range(1440):
    sum = 0
    for n in range(1000):
        sum += comp_list[n][i]
    average[i] = sum/1000

x_list = []

for i in range(1440):
    x_list.append(i)

plt.plot(x_list, average)
plt.show()
