#Created on 9th Feb 2020
#Author : Nishu Singh (MA)

# The following script reads the database file and outputs minimum and maximum temperature for a given point in time.
# Time can be taken from user input or from system time and corresponds to number of a line in the database, that is read out.


import pandas
import matplotlib.pyplot as plt
import os
import numpy as np
import datetime
import datetime
import json

def CustomParser(data):
    import json
    j1 = json.loads(data)
    return j1

time_h = datetime.datetime.now().hour
time_m = datetime.datetime.now().minute
time = time_h * 60 + time_m
if int(input("would you like to input time?(yes = 1, no = 0): ")):
    time = int(input("Please input time in minutes(0-26300): "))
file_name = os.path.normpath("diff_csv/0318_ampacity_merged_min_no83abcd.csv")
skip_col = ["time_stamp", "min_amp", "min_line_section"]
amps_database = pandas.read_csv(file_name, sep=";", engine="c").transpose().drop(skip_col)[time]
pandas.set_option('display.max_rows', amps_database.shape[0] + 1)
# print("max value is {} A".format(round(amps_database.max(), 2)))
# print("min value is {} A".format(round(amps_database.min(), 2)))
# print(amps_database)
myjson = amps_database.to_json()
print(myjson)