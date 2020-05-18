#Created on 9th Feb 2020
#Author : Nishu Singh (MA)
#This is the main program that calculates and displays the transient analysis
# The following program calculates temperature of a wire for given weather conditions during the unsteady process of heating it up
# by a flowing electrical current. Calculated temperature will be ploted and saved as .png image.


import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import scipy.integrate as S
from scipy.optimize import fsolve
import math
import os
import copy
import pandas
from steadyTemp import steadyTemp

conductorData = {'Rdc': 67.4E-6, 'alpha': 0.004, 'alphaS': 0.5, 'y': 300, 'D': 0.0248, 'DSt': 0.0084, 'd': 3.18E-3,
                 'epsilon': 0.5, 'gammaAl': 2703, 'gammaSt': 7780, 'cAl': 897, 'cSt': 481, 'AAl': 428.9E-6,
                 'ASt': 55.6E-6} # all necessary constants for calculations
temperatureData = {}
weatherData = {'S': 980, 'Ta': 40, 'V': 2, 'delta': 45, 'time': 0} # dictionary with weather data from the database
file_list = []  # it is the list, that stores names of files to read
num_of_row = 30
ind_list = []  # the list will store time points when Temperature reaches 100C
csv_data = {}


def get_time(tim):
    """
        Converts timestamp from the database into readable string.
        """

    tim = str(tim)
    return "UTC time: " + tim[0:4] + "." + tim[4:6] + "." + tim[6:8] + "    " + tim[8:10] + ":" + tim[10:12]


def get_file_list(file_list):
    """
        Get a list of database files in script's folder

        Following function reads .txt file that contains list of previously detected database files and compares it to the actual
        .csv files in the folder. If any new files appeared since last script running, they added to the end of list "file_list",
        that ensures using it in the calculations. .txt file updated to contain names of all database files.
        """

    prev_file_list = [] # empty list to store name of files
    for csvfile in os.listdir('csv'): # for every file in the folder
        file_name = 'csv/' + csvfile
        if file_name.endswith("csv") and file_name not in file_list: # check if it is a .csv file and if it has been already added to the list
            file_list.append(file_name) # store the name of .csv to the list
            get_weatherData(file_name) # update weather data dictionary from a database file
        elif file_name == "csv_files_list.txt": # if it is the file from previous run of this script
            with open(file_name) as f: # read it
                prev_file_list = f.read().splitlines() # and store to the list
    file_list.sort() # sort names in lists
    prev_file_list.sort()
    if prev_file_list and len(prev_file_list) < len(file_list): # if old list and the new one have different length
        dif = set(file_list).difference(set(prev_file_list)) # check what the difference between them
        for dif_el in list(dif): # for each found difference
            file_list.remove(dif_el) # ensure that it will be placed at the end of a list "file_list"
            file_list.append(dif_el) # by removing it and appending to the end
        print(dif)
    with open("csv_files_list.txt", "w+") as f: # open .txt file with names of databases
        f.writelines("%s\n" % file_name for file_name in file_list) # and update it with new data



def solve_steady(Tin, Iac):
    """
       Get temperature in steady state for given current and weather condition.
    """
    global weatherData # use global variable
    Tss = fsolve(steadyTemp, Tin, maxfev=1000, args=(Iac, weatherData))  # it solves steady state equation numerically
    return Tss[0]



def get_weatherData(file_name):
    """
        Read weather condition from a csv file and update data in the dictionary "weatherData"
    """
    global weatherData, csv_data, file_list #using bunch of global variables
    result = pandas.read_csv(file_name, sep=";", engine="c", nrows=2, skiprows=lambda x: x in range(1,
                                                                                                    num_of_row - 1))  # read and decode the file which name is at number n_file in file_list
    if " global radiation [W/m^2]" in result: # check if the database file is the correct one
        weatherData['S'] = result[" global radiation [W/m^2]"][
            0]  # update information in weatherdata dictionary based on file
        weatherData['Ta'] = result[" temperature [deg]"][0]
        weatherData['V'] = result[" wind speed [m/s]"][0]
        weatherData['delta'] = result[" wind direction [deg]"][0]
        weatherData['time'] = result["time UTC [yyyymmddHHMM]"][0]
        csv_data[file_name] = copy.deepcopy(weatherData) # store weather data from the database to the dictionary
    else:
        file_list.remove(file_name) # remove the name of file from list if it isn't a valid database



def calc_unstedy(Tss, Tin, Iac, t):
    """
       Get list of temperatures for given T_steady_state, T_initial, current and time-series. Time starts from zero.

    """
    global weatherData # use global variable weather dictionary
    # Mass calculation
    mAl = conductorData['gammaAl'] * conductorData['AAl'] # straightforward calculations
    mSt = conductorData['gammaSt'] * conductorData['ASt']
    mc = mAl * conductorData['cAl'] + mSt * conductorData['cSt']
    Rac = (1.0123 + 2.36E-5 * Iac) * conductorData["Rdc"]  # alternating current resistance

    tau = mc * (Tss - weatherData["Ta"]) / (
                np.power(Iac, 2) * Rac + conductorData['alphaS'] * weatherData['S'] * conductorData['D'])  # tau calc
    T = Tss - (Tss - Tin) * np.exp(
        -t / tau)  # calculate the list of temperatures for curve in unsteady state. t here is a list
    return T # return list of temperatures


def plot_temperature(T_seq, t_seq, Iac_seq, axs1, axs2, file_name):
    """
        Add graph to the existing plot.

        Plots a line for given Temperatures and time series, place all important information on the plot.
    """
    t = np.arange(0, sum(t_seq)) / 60  # time series
    t_shift = 0
    for i, t_intrv in enumerate(t_seq): # for every time interval given by user
        lbl = "I = " + str(Iac_seq[i]) + "A"  # this will be a label on plot
        axs1.plot(t[t_shift:t_shift + t_intrv], T_seq[t_shift:t_shift + t_intrv]) # plot a temperature curve
        axs2.plot(t[t_shift:t_shift + t_intrv], [Iac_seq[i]] * (t_intrv)) # plot a Current line

        if max(T_seq[t_shift:t_shift + t_intrv]) > 100:  # check if T reaches 100C
            t_surp = t_shift + next(x[0] for x in enumerate(T_seq[t_shift:t_shift + t_intrv]) if x[1] > 100) # save time when it happened
            if T_seq[t_surp] < T_seq[t_surp + 1]: # if temperature rises at tis point
                axs2.text(t_shift / 60, Iac - 100,
                          "Warning: at time {} min \n you are surpassing the \n maximum temperature.".format(
                              round(t_surp / 60))) # show a warning
        t_shift += t_intrv # update t_shift so the next section will be shifted forward


def calc_segment(Tin, Tss, t_start, t_finish, Iac, t_shift, file_name):
    """
        Make calculation of temperature curve for unsteady process for given initial temperature, time interval, current and weather data.

        The function calculates a temperature curve and stores it in global dictionary "temperatureData" for future analysis

    """
    t = np.arange(t_start, t_finish) # creating time series for given interval
    T = calc_unstedy(Tss, Tin, Iac, t)  # get the list of temperatures
    if file_name in temperatureData.keys(): # check if there is data for this weather in dictionary
        temperatureData[file_name] = np.append(temperatureData[file_name], T) # add new data to the dictionary
    else:
        temperatureData[file_name] = T # if there is no such key in dictionary, create one
    if (max(T) > 100):  # check if T reaches 100C
        ind_list[-1] += next(x[0] for x in enumerate(T) if x[1] > 100)  # find where exactly it reaches 100C
        if ind_list[-1] < t_shift and T[1] > T[0]: # check if temperature rises at this moment
            t_surp = t_shift + next(x[0] for x in enumerate(T) if x[1] > 100) # store where is it happened
    else:
        ind_list[-1] += T.size # if temperature doesn't exceeds 100C, store this fact too
    return T[-1] # return temperature that will be initial for the next section


Iac_list = [] # list of currents for every weather condition
t_list = [] # list of time intervals for every weather condition
t_shift = 0 # variable to store shift for each new section of graph
n_file = 0 # file counter

get_file_list(file_list) # update file list
T_in_input = int(input("Initial temperature(Celsius):")) # user input of temperature
Tin = T_in_input # store it t the second variable
n_plots = int(input("How many inputs?(number):")) # user input
for i in range(n_plots): # for every user input
    Iac_list.append(int(input("Current " + str(i + 1) + ":"))) # ask and store current
    t_list.append(60 * int(input("Time " + str(i + 1) + "(in minutes):"))) # and time

counter = 0
for file_name in file_list: # for every weather database
    weatherData.clear() # clear existing dictionary
    weatherData = csv_data[file_name].copy() # and update it with new data
    ind_list.append(0) # it will store where temperature exceeds 100C. Initial value 0
    for i, Iac in enumerate(Iac_list): # for every user defined Current
        Tss = solve_steady(Tin, Iac)  # calculate temperature of steady state
        Tin = calc_segment(Tin, Tss, 0, t_list[i], Iac, t_shift, file_name)  # calculate one segment of a curve
        t_shift += t_list[
            i]  # update time shift for plot. Each segment should be shifted to the right on the length of previous one
    Tin = T_in_input  # reseting Tin to initial state
    n_file += 1  # next file
    t_shift = 0  # reseting time shift

fig, axs = plt.subplots(2)  # create empty plot with 2 subplots
plot_temperature(temperatureData[file_list[ind_list.index(min(ind_list))]], t_list, Iac_list, axs[0], axs[1],
                 file_list[ind_list.index(min(ind_list))]) # plot everything

axs[0].text(0, 110, get_time(csv_data[file_name]["time"])) # show time stamp
axis = plt.gca() # get axis of a plot
xmin, xmax = axis.get_xlim() # get a size of x axis
axs[0].plot([xmin, xmax], [100, 100], "--")  # max temperature level
axs[0].set(xlabel='', ylabel='T, Celsius')
axs[1].set(xlabel='t, minutes', ylabel='I, A')
if sum(t_list) > 3600:
    axs[0].text(30, Tss,
                "Warning: analysis isn't accurate \n if you are looking at data for \n more than 60 minutes into the future.")

plt.tight_layout() # it improves plot appearence
plt.savefig("static/fig_choose.png")
#plt.show()  # it is neccesary to actually show something
