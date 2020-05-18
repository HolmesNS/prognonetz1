#Created on 9th Nov 2019
#Author : Nishu Singh (MA)
# Use this function to calculate the steady state temperature of the
# conductor under certain weather conditions (global structure WeatherData)
# and the current value of the line (global variable Iac). The returning
# value P (total heat) must be zero to have the corresponding T.
# Reference: Cigre 207, matlab program by Gabriela Molinar

import numpy as np
import matplotlib.pyplot as plt
import scipy.integrate as S
from scipy.optimize import fsolve
import math


conductorData = {'Rdc': 67.4E-6, 'alpha': 0.004, 'alphaS': 0.5, 'y': 300, 'D': 0.0286, 'DSt': 0.00954, 'd': 3.18E-3,
                 'epsilon': 0.5, 'gammaAl': 2703, 'gammaSt': 7780, 'cAl': 897, 'cSt': 481, 'AAl': 428.9E-6,
                 'ASt': 55.6E-6} # all necessary constants for calculations

weatherData ={'S': 980, 'Ta': 40, 'V': 2, 'delta': 45} # default weather data



Iac = 600 # default Current value
T0 = 58.5 # default initial temperature value


def steadyTemp(T, Iac, weatherData):

    # Constants definition
    sigmaB = 5.67E-8 # Stefan-Boltzmann [W/(m^2*K^4)]

    # Constants calculation
    Idc = Iac * math.sqrt(1.0123 + 2.36E-5 * Iac)# DC current [A]
    Tf = (T + weatherData['Ta']) / 2
    lambdaf = 2.42E-2 + 7.2E-5 * Tf# Thermal conductivity of air
    vf = 1.32E-5 + 9.5E-8 * Tf# Kinematic viscosity

    if weatherData['V'] != 0: # check if there is wind
        # Force convective cooling
        ro = np.exp(-1.16E-4 * conductorData['y'])    # Relative air density
        Re = ro * weatherData['V'] * conductorData['D'] / vf    # Reynolds number

        if (1E2 < Re) and (Re < 2.65E3): # in case Reynolds number in certain range
            B1 = 0.641 # set the constants
            n = 0.471
        else: # otherwise constants have another values
            Rf = conductorData['d'] / (2 * (conductorData['D'] - conductorData['d']))
            if Rf <= 0.05:
                B1 = 0.178
                n = 0.633
            else:
                B1 = 0.048
                n = 0.8

        Nu90 = B1 * np.abs(Re) ** n # calculate other constants
        A1 = 0.42

        if (0 < weatherData['delta']) and (weatherData['delta'] < 24): # check if delta is in certain range
            B2 = 0.68 # set constants to this values
            m1 = 1.08
        else: # otherwise
            B2 = 0.58 # other values
            m1 = 0.9

        Nuf = Nu90 * (A1 + B2 * (np.abs(np.sin(weatherData['delta'] * np.pi / 180)) ** m1))
        Nu = Nuf

    if weatherData['V'] < 0.5: # check if wind is low speed
        # Natural convective cooling
        Gr = conductorData['D'] ** 3 * (T - weatherData['Ta']) * 9.807 / ((Tf + 273) * vf ** 2)  # Grashof number
        Pr = 1005 * 1.983E-5 / lambdaf  # Prandtl number

        GrPr = Gr * Pr

        if (1E2 < GrPr) and (GrPr < 1E4): # if Grashof number * Prandtl number is in certain range
            A2 = 0.85 # set constants
            m2 = 0.188
        else: # otherwise
            A2 = 0.48 # another values
            m2 = 0.25


        Nun = A2 * (GrPr) ** m2
        Nu = Nun

    if (0 < weatherData['V']) and (
            weatherData['V'] < 0.5):
        # Cooling at low wind speed
        if Nun > Nuf:
            Nu = Nun
        else:
            Nu = Nuf

        Nucor = 0.55 * Nu90
        if Nucor > Nu:
            Nu = Nucor

    # Heat equation calculation
    # Joule heating
    PJ = Idc ** 2 * conductorData['Rdc'] - Idc ** 2 * conductorData['Rdc'] * conductorData['alpha'] * 20 + Idc ** 2 * conductorData['Rdc'] * conductorData['alpha'] * T

    # Solar heating
    PS = conductorData['alphaS'] * weatherData['S'] * conductorData['D']

    # Convective cooling
    PC = np.pi * lambdaf * (T - weatherData['Ta']) * Nu

    # Radiative cooling
    PR = np.pi * conductorData['D'] * conductorData['epsilon'] * sigmaB * ((T + 273) ** 4 - (weatherData['Ta'] + 273) ** 4)

    P = PJ + PS - PC - PR
    return P

def solve_steady(Tin, Iac, weatherData):
    '''
        Get temperature for steady state process.
        '''

    # calling function from scipy.optimise that numericaly solve steady state temperature equation.
    # It is looking for such T that returning value of steadyTemp (heating power) becomes 0
    Tss = fsolve(steadyTemp, Tin, args=(Iac, weatherData))
    return Tss[0] # return temperature in steady state

if __name__ == '__main__': # check if the script is opened directly by user and not imported by other script
    print(solve_steady(T0, Iac, weatherData)) # in this case solve equation for default values of temperature, Current an weather conditions

