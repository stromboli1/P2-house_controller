import models as mod
import matplotlib.pyplot as plt

house = mod.House('d', 150, 2.8, 21, 0, 212)

oven = mod.Oven(power_usage=1.1)
dryer = mod.Dryer(power_usage=1.47)
background = mod.background_power_consumption()

comp_list = []
average = []

for i in range(1440):
    average.append(i)

for days in range(1000):
    oven.reset()
    dryer.reset()
    day_list = []
    for minuts in range(1440):
        time_of_day = minuts*60
        consumption = 0
        consumption += oven.tick(1, time_of_day)
        consumption += dryer.tick(1, time_of_day)
        consumption += background.tick(1, time_of_day)
        day_list.append(consumption)
    comp_list.append(day_list)



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