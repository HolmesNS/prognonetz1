#Created on 9th Feb 2020
#Author : Nishu Singh (MA)

import pandas
import matplotlib.pyplot as plt
import os
import numpy as np
import datetime
import time


def get_time(tim):
    tim = str(tim)
    return "UTC time: " + tim[0:4] + "." + tim[4:6] + "." + tim[6:8] + "    " + tim[8:10] + ":" + tim[10:12]


file_name = os.path.normpath("diff_csv/preds_linear_comb_qrf_fnnnwp.csv")

time_0 = datetime.datetime.now().hour
if int(input("would you like to input time?(yes = 1, no = 0): ")):
    time_0 = int(input("Please input time in hours(0-48): "))
amps_database = pandas.read_csv(file_name, sep=",", engine="c")

# Create an array with the names of the prediction columns
pred_col_names = ['Ampacity_Prediction_' + str(i + 1).zfill(2) for i in range(48)]
t_past = np.arange(-48, 0)
t_futr = np.arange(-0, 48)

# The following loop will be taking the row corresponding to t0, plot the past and prediction, and then wait for one minute before executing the next loop
# t0 has to begin at 48, otherwise you dont have the past data
for t0 in range(48 + time_0, amps_database.size):
    plt.close("all")
    if "amp_realtime.png" in os.listdir('static'):
        os.remove("static/amp_realtime.png")
    # take all values from t0 to the past 48 hours
    past_from_t0 = np.round(np.array(amps_database["Ampacity_Truth_01"].values.tolist()[t0 - 48:t0]), 2)
    # take the predictions for the row t0
    future_from_t0 = np.round(np.array(amps_database[pred_col_names].values.tolist()[t0]), 2)
    # Plot the concatenation of the past and the prediction from -48 hours to 48 hours

    plt.plot(t_past, past_from_t0, label="Ampacity")
    plt.plot(t_futr, future_from_t0, label="Ampacity prediction")
    plt.title("Ampacity plot, {}".format(get_time(amps_database.iloc[t0, 0])))
    plt.xlabel("Time (hours)")
    plt.ylabel("Ampacity, A")
    plt.legend(loc="upper right")
    plt.savefig("static/amp_realtime.png")
    time.sleep(60)
