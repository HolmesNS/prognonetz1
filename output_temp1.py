#Created on March 10th 2020
#Author : Nishu Singh (MA)
# The following script reads the database file and outputs minimum and maximum temperature for a given point in time.
# Time can be taken from user input or from system time and corresponds to number of a line in the database, that is read out.

import pandas
import matplotlib.pyplot as plt
import os
import numpy as np
import datetime
import datetime
import csv

time_h = datetime.datetime.now().hour % 12 # get number of hours from the system time and convert to 12-hour 
                                            # format to be in the range of the database file (1000 lines)
time_m = datetime.datetime.now().minute # get number of minutes from the system time
time = time_h * 60 + time_m     # system time in minutes

print("""The following script reads the database file and outputs minimum and maximum temperature for a given point in time.
Time can be taken from user input or from system time and corresponds to number of a line in the database, that is read out. 
""")

#if int(input("Would you like to input time manually?(yes = 1, no = 0): ")): # read user decision about time source
 #   time = int(input("Please input time in minutes(0-1000): ")) # read user time input and convert it to integer number
file_name = os.path.normpath("diff_csv/0318_conductor_temperature.csv") # create a variable with path to database file
skip_col = ["time_stamp"] # array with names of columns that we don't need
amps_database = pandas.read_csv(file_name, sep=";", engine="c").transpose().drop(skip_col)[time] # reading of the database file 
                                                                                                # and extracting the line we are interested in
pandas.set_option('display.max_rows', amps_database.shape[0] + 1) # increasing maximum number of lines that can be printed out. Is necessary to print 
                                                                # the whole line of temperatures
print("max value is {} C".format(round(amps_database.max(), 2))) # extract and output maximum temperature from the chosen line in the database
print("min value is {} C".format(round(amps_database.min(), 2))) # extract and output minimum temperature from the chosen line in the database
print(amps_database) # print the whole line from which we choose max and value 