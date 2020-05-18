#Created on 9th Feb 2020
#Author : Nishu Singh (MA)
#Base Flask file, Transient Analysis and


from flask import Flask,render_template,request,jsonify
import json

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
import datetime
import matplotlib

matplotlib.use('agg')
matplotlib.pyplot.switch_backend('Agg')

app = Flask(__name__)

conductorData = {'Rdc': 67.4E-6, 'alpha': 0.004, 'alphaS': 0.5, 'y': 300, 'D': 0.0248, 'DSt': 0.0084, 'd': 3.18E-3,
                 'epsilon': 0.5, 'gammaAl': 2703, 'gammaSt': 7780, 'cAl': 897, 'cSt': 481, 'AAl': 428.9E-6,
                 'ASt': 55.6E-6}
temperatureData = {}
weatherData = {'S': 980, 'Ta': 40, 'V': 2, 'delta': 45, 'time': 0}
file_list = []  # it is the list, that stores names of files to read
num_of_row = 30
ind_list = []  # the list will store time points when Temperature reaches 100C
csv_data = {}
response = {}

# TRANSIENT ANALYSIS UTILITY FUNCTIONS

def get_time(tim):
    tim = str(tim)
    return "UTC time: " + tim[0:4] + "." + tim[4:6] + "." + tim[6:8] + "    " + tim[8:10] + ":" + tim[10:12]

def get_file_list(file_list):
    prev_file_list = []
    for csvfile in os.listdir('csv'):
        file_name = 'csv/' + csvfile
        if file_name.endswith("csv") and file_name not in file_list:
            file_list.append(file_name)
            get_weatherData(file_name)
        elif file_name == "csv_files_list.txt":
            with open(file_name) as f:
                prev_file_list = f.read().splitlines()
    file_list.sort()
    prev_file_list.sort()
    if prev_file_list and len(prev_file_list) < len(file_list):
        dif = set(file_list).difference(set(prev_file_list))
        for dif_el in list(dif):
            file_list.remove(dif_el)
            file_list.append(dif_el)
        print(dif)
    with open("csv_files_list.txt", "w+") as f:
        f.writelines("%s\n" % file_name for file_name in file_list)

# get temperature in steady state for given Current and weather condition
def solve_steady(Tin, Iac):
    global weatherData
    Tss = fsolve(steadyTemp, Tin, maxfev=1000, args=(Iac, weatherData))  # it solves steady state equation numerically
    return Tss[0]

# read weather condition from a csv file and update data in dictionary
def get_weatherData(file_name):
    global weatherData, csv_data, file_list
    result = pandas.read_csv(file_name, sep=";", engine="c", nrows=2, skiprows=lambda x: x in range(1,
                                                                                                    num_of_row - 1))  # read and decode the file which name is at number n_file in file_list
    if " global radiation [W/m^2]" in result:
        weatherData['S'] = result[" global radiation [W/m^2]"][
            0]  # update information in weatherdata dictionary based on file
        weatherData['Ta'] = result[" temperature [deg]"][0]
        weatherData['V'] = result[" wind speed [m/s]"][0]
        weatherData['delta'] = result[" wind direction [deg]"][0]
        weatherData['time'] = result["time UTC [yyyymmddHHMM]"][0]
        csv_data[file_name] = copy.deepcopy(weatherData)
    else:
        file_list.remove(file_name)

# get list of Temperatures for given T_steady_state, T_initial, current and time-series. Time starts from zero.
def calc_unstedy(Tss, Tin, Iac, t):
    global weatherData
    # Mass calculation
    mAl = conductorData['gammaAl'] * conductorData['AAl']
    mSt = conductorData['gammaSt'] * conductorData['ASt']
    mc = mAl * conductorData['cAl'] + mSt * conductorData['cSt']
    Rac = (1.0123 + 2.36E-5 * Iac) * conductorData["Rdc"]  # alternating current resistance

    tau = mc * (Tss - weatherData["Ta"]) / (
                np.power(Iac, 2) * Rac + conductorData['alphaS'] * weatherData['S'] * conductorData['D'])  # tau calc
    T = Tss - (Tss - Tin) * np.exp(
        -t / tau)  # calculate the list of temperatures for curve in unsteady state. t here is a list
    return T

def plot_temperature(T_seq, t_seq, Iac_seq, axs1, axs2, file_name):
    global response
    t = np.arange(0, sum(t_seq)) / 60  # time series
    t_shift = 0
    for i, t_intrv in enumerate(t_seq):
        lbl = "I = " + str(Iac_seq[i]) + "A"  # this will be a label on plot
        axs1.plot(t[t_shift:t_shift + t_intrv], T_seq[t_shift:t_shift + t_intrv])
        axs2.plot(t[t_shift:t_shift + t_intrv], [Iac_seq[i]] * (t_intrv))

        if max(T_seq[t_shift:t_shift + t_intrv]) > 100:  # check if T reaches 100C
            t_surp = t_shift + next(x[0] for x in enumerate(T_seq[t_shift:t_shift + t_intrv]) if x[1] > 100)
            if T_seq[t_surp] < T_seq[t_surp + 1]:
                # axs2.text(t_shift / 60, Iac - 100,
                #           "Warning: at time {} min \n you are surpassing the \n maximum temperature.".format(
                #               round(t_surp / 60)))
                response['warning1'] = "Warning: at time {} min \n you are surpassing the \n maximum temperature.".format(
                              round(t_surp / 60))
        t_shift += t_intrv

def calc_segment(Tin, Tss, t_start, t_finish, Iac, t_shift, file_name):
    t = np.arange(t_start, t_finish)
    T = calc_unstedy(Tss, Tin, Iac, t)  # get the list of temperatures
    if file_name in temperatureData.keys():
        temperatureData[file_name] = np.append(temperatureData[file_name], T)
    else:
        temperatureData[file_name] = T
    if (max(T) > 100):  # check if T reaches 100C
        ind_list[-1] += next(x[0] for x in enumerate(T) if x[1] > 100)  # find where exactly it reaches 100C
        if ind_list[-1] < t_shift and T[1] > T[0]:
            t_surp = t_shift + next(x[0] for x in enumerate(T) if x[1] > 100)
    else:
        ind_list[-1] += T.size
    return T[-1]

# MAIN WEB SERVICES #

# SERVE INDEX PAGE ON OPENING WEB APP
@app.route('/')
def index():
    return render_template('index.html')

# UPON SUBMITTING TRANSIENT ANALYSIS DATA FROM WEB APP, 
# CREATE NEW IMAGE FROM DATA AND SEND SUCCESS RESPONSE
@app.route('/saveImage', methods = ['POST'])
def saveImage():
    global weatherData
    data = request.get_json() # GET DATA FROM WEB APP REQUEST
    
    Iac_list = [] # list of currents for every weather condition
    t_list = [] # # list of time intervals for every weather condition
    t_shift = 0 # shift next curve in plot, in seconds
    n_file = 0 # number of a file
    fig_list = []

    get_file_list(file_list)

    T_in_input = data['temperature'] # GET FROM REQUEST DATA
    Tin = T_in_input

    # GET TEMP VALUES AND TIME FROM REQUEST DATA AND APPEND TO LIST
    for d in data['values']:
        Iac_list.append(d['current'])
        t_list.append(60*d['time'])
        # print(str() + ' - ' + str(d['time']))

    counter = 0
    for file_name in file_list:
        weatherData.clear()
        weatherData = csv_data[file_name].copy()
        if(len(ind_list)) == 0:
            ind_list.append(0)
        for i, Iac in enumerate(Iac_list):
            Tss = solve_steady(Tin, Iac)  # calculate temperature of steady state
            Tin = calc_segment(Tin, Tss, 0, t_list[i], Iac, t_shift, file_name)  # plot one segment of a curve
            t_shift += t_list[
                i]  # update time shift for plot. Each segment should be shifted to the right on the length of previous one
        Tin = T_in_input  # reseting Tin to initial state
        n_file += 1  # next file
        t_shift = 0  # reseting time shift

    fig, axs = plt.subplots(2)  # create empty plot with 2 subplots
    plot_temperature(temperatureData[file_list[ind_list.index(min(ind_list))]], t_list, Iac_list, axs[0], axs[1],
                    file_list[ind_list.index(min(ind_list))])

    axs[0].text(0, 110, get_time(csv_data[file_name]["time"]))
    axis = plt.gca()
    xmin, xmax = axis.get_xlim()
    axs[0].plot([xmin, xmax], [100, 100], "--")  # max temperature level
    axs[0].set(xlabel='', ylabel='T, Celsius')
    axs[1].set(xlabel='t, minutes', ylabel='I, A')
    if sum(t_list) > 3600:
        # axs[0].text(30, Tss,
        #             "Warning: analysis isn't accurate \n if you are looking at data for \n more than 60 minutes into the future.")
        response['warning2'] = "Warning: analysis isn't accurate \n if you are looking at data for \n more than 60 minutes into the future."

    plt.tight_layout()
    plt.savefig("static/fig_choose.png")

    # SEND JSON RESPONSE
    json_response = json.dumps(response, sort_keys=True)

    return json_response

# ELECTRICAL GRID DESIGN SECTION
#This section pairs the json coordinates to the

# FETCH LOCATION DATA FROM GIVEN TIME FROM WEB APP REQUEST
@app.route('/location_data', methods = ['POST'])
def locationData():
    time_h = datetime.datetime.now().hour % 12 # get number of hours from the system time and convert to 12-hour 
                                            # format to be in the range of the database file (1000 lines)
    # get number of minutes from the system time
    time_m = datetime.datetime.now().minute
    time = time_h * 60 + time_m  # system time in minutes
    
    # create a variable with path to database file
    file_name = os.path.normpath("diff_csv/0318_conductor_temperature.csv")
    skip_col = ["time_stamp"]  # array with names of columns that we don't need
    amps_database = pandas.read_csv(file_name, sep=";", engine="c").transpose().drop(skip_col)[time] # reading of the database file 
                                                                                                # and extracting the line we are interested in
    # increasing maximum number of lines that can be printed out. Is necessary to print
    pandas.set_option('display.max_rows', amps_database.shape[0] + 1)
    # the whole line of temperatures
    
    # SEND JSON RESPONSE
    myjson = amps_database.to_json()
    return myjson
