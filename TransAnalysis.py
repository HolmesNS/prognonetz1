import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import scipy.integrate as S
from scipy.optimize import fsolve
import math
import pandas
from steadyTemp import steadyTemp

conductorData = {'Rdc': 67.4E-6, 'alpha': 0.004, 'alphaS': 0.5, 'y': 300, 'D': 0.0248, 'DSt': 0.0084, 'd': 3.18E-3,
                 'epsilon': 0.5, 'gammaAl': 2703, 'gammaSt': 7780, 'cAl': 897, 'cSt': 481, 'AAl': 428.9E-6,
                 'ASt': 55.6E-6}

weatherData = {'S': 980, 'Ta': 40, 'V': 2, 'delta': 45 }
file_list = ["csv/0318_0105.csv", "csv/0318_0003.csv", "csv/0318_0833.csv"] ## list with name of files

ind_list = []

# get temperature in steady state for given Current and weather condition
def solve_steady(Tin, Iac):
    Tss = fsolve(steadyTemp, Tin, maxfev=1000, args=(Iac, weatherData))
    return Tss[0]

# read weather condition from a csv file and update data in dictionary
def get_weatherData(n_file):
    result = pandas.read_csv(file_list[n_file], sep=";") ## reads the data
    weatherData['S'] = result[" global radiation [W/m^2]"][30]
    weatherData['Ta'] = result[" temperature [deg]"][30]
    weatherData['V'] = result[" wind speed [m/s]"][30]
    weatherData['delta'] = result[" wind direction [deg]"][30]

# get list of Temperatures for given T_steady_state, T_initial, current and time-series. Time starts from zero.
def calc_unstedy(Tss,Tin, Iac, t):
     # Mass calculation
    mAl = conductorData['gammaAl'] * conductorData['AAl']
    mSt = conductorData['gammaSt'] * conductorData['ASt']
    mc = mAl * conductorData['cAl'] + mSt * conductorData['cSt']
    # Idc = Iac * math.sqrt(1.0123 + 2.36E-5 * Iac) # DC current [A]
    Rac = (1.0123 + 2.36E-5 * Iac) * conductorData["Rdc"]

    tau = mc * (Tss - weatherData["Ta"]) / (np.power(Iac,2) * Rac + conductorData['alphaS'] * weatherData['S'] * conductorData['D'])
    T = Tss - (Tss  - Tin) * np.exp(-t/tau)
    return T

# add a segment of plot
def plot_segment(Tin, Tss, t_start, t_finish, Iac, t_shift, axs1, axs2):
    t = np.arange(t_start, t_finish) # time series
    lbl = "I = " + str(Iac) + "A"
    T = calc_unstedy(Tss, Tin, Iac, t)
    if(max(T) > 100):
        ind_list[-1] += next(x[0] for x in enumerate(T) if x[1] > 100)
    else:
        ind_list[-1] += T.size
    t_plot = (t + t_shift) / 60 # change time units to minutes
    axs1.plot(t_plot, T, label=lbl)
    axs1.text(t_plot[0]+2, Tss + 30, lbl) # plot label
    axs2.plot([t_plot[0], t_plot[-1]], [Iac, Iac])
    return T[-1]

Iac_list = [] # list of currents for every weather condition
t_list = [] # # list of time intervals for every weather condition
t_shift = 0 # shift next curve in plot, in seconds
n_file = 0 # number of a file
fig_list = []

T_in_input = int(input("Initial temperature(Celsius):"))
Tin = T_in_input
n_plots = int(input("How many inputs?(number):"))
for i in range(n_plots):
    Iac_list.append(int(input("Current " + str(i+1) + ":")))
    t_list.append(60*int(input("Time " + str(i+1) + "(in minutes):")))

for j in range(3):         ##iteration
    get_weatherData(n_file)
    fig, axs = plt.subplots(2)
    fig_list.append(fig)
    ind_list.append(0)
    for i, Iac in enumerate(Iac_list): ##find Tss and put segment of plot
        Tss = solve_steady(Tin, Iac)
        Tin = plot_segment(Tin, Tss, 0, t_list[i], Iac, t_shift, axs[0], axs[1])
        t_shift += t_list[i]
    Tin = T_in_input
    n_file += 1
    t_shift = 0
    axis = plt.gca()
    xmin, xmax = axis.get_xlim()
    axs[0].plot([xmin, xmax], [100, 100], "--") # max temperature level
    axs[0].set(xlabel='', ylabel='T, Celsius')
    axs[1].set(xlabel='t, minutes', ylabel='I, A')
    plt.savefig("fig_weather" + str(n_file) + ".png")
    plt.clf()
# print(ind_list)
plt.close("all")
plt.imshow(mpimg.imread("fig_weather" + str(ind_list.index(min(ind_list))+1) + ".png"))
# plt.show()

plt.savefig('fig_choose.png') # to save plot as a file