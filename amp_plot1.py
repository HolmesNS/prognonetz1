#Created on March 10th 2020
#Author : Nishu Singh (MA)
# The following script reads the database file and generates a plot of ampacity to time.
# First half of the plot corresponds to real measured data in the past and the other half to the predicted values for the future.
# Time can be taken from user input or from system time and corresponds to number of a line in the database, that is read out. 

import pandas
import matplotlib.pyplot as plt
import os
import numpy as np
import datetime
import time

plt.rcParams.update({'font.size': 7}) # update matplotlib default font size 

file_name = os.path.normpath("diff_csv/preds_linear_comb_qrf_fnnnwp.csv") # create a variable with path to database file
time_0 = datetime.datetime.now().hour # get number of hours from the system time

# print("""The following script reads the database file and generates a plot of ampacity to time. 
# First half of the plot corresponds to real measured data in the past and the other half to the predicted values for the future.
# Time can be taken from user input or from system time and corresponds to number of a line in the database, that is read out. 
# """)

if int(input("would you like to input time?(yes = 1, no = 0): ")): # read user decision about time source
    time_0 = int(input("Please input time in hours(0-48): "))  # read user time input and convert it to integer number
amps_database = pandas.read_csv(file_name, sep=",", engine="c") # read the database file

# Create an array with the names of the prediction columns
pred_col_names = ['Ampacity_Prediction_' + str(i + 1).zfill(2) for i in range(48)]
t_past = np.arange(-48, 0) # time series for graph, past
t_futr = np.arange(-0, 48) # time series for graph, future

# The following loop will be taking the row corresponding to t0, plot the past and prediction, and then wait for one minute before executing the next loop
# t0 has to begin at 48, otherwise you dont have the past data
for t0 in range(48 + time_0, amps_database.size):
    if "amp_realtime.png" in os.listdir(): # check if there is a plot file 
        os.remove("amp_realtime.png") # if there is one -- remove it (it means it isn't the first time the program enters this loop)
    # take all values from t0 to the past 48 hours
    past_from_t0 = np.round(np.array(amps_database["Ampacity_Truth_01"].values.tolist()[t0 - 48:t0]), 2)
    # take the predictions for the row t0
    future_from_t0 = np.round(np.array(amps_database[pred_col_names].values.tolist()[t0]), 2)
    # Plot the concatenation of the past and the prediction from -48 hours to 48 hours

    plt.figure(figsize=(5,2)) # create figure for plot, set aspect ratio
    plt.plot(t_past, past_from_t0, label="Ampacity") # plot past ampacity values 
    plt.plot(t_futr, future_from_t0, label="Ampacity prediction") # plot future ampacity values
    plt.title("Ampacity plot") # create title for graph
    plt.xlabel("Time (hours)") # assign a label for x axis
    plt.ylabel("Ampacity, A") # and y
    plt.legend(loc="upper right") # add a legend to the graph, set location for it
    plt.tight_layout() # ensure everything will be inside the saved picture
    plt.savefig("static/amp_realtime.png", dpi=200) # save generated graph as a png file.
    time.sleep(60) # wait 60 seconds
