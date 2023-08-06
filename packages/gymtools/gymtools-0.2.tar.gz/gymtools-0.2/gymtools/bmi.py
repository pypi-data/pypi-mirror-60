#!/usr/bin/env python

"""bmi.py: A tool that provides functions to check for the bmi of input data."""

from time import sleep


def calc(weight, height):
    return weight / (height/100)**2


def classify(bmi):
    if bmi < 16:
        print("Severe underweight!")
    elif 16 <= bmi < 17:
        print("Moderately underweight")
    elif 17 <= bmi < 18.5:
        print("Slightly underweight")
    elif 18.5 <= bmi < 25:
        print("Normal weight")
    elif 25 <= bmi < 30:
        print("Overweight")
    elif 30 <= bmi < 35:
        print("Slight obese")
    elif 35 <= bmi < 40:
        print("Moderate obese")
    elif bmi >= 40:
        print("Severe obese!")


if __name__ == '__main__':
    xweight = int(input("Weight (kg): "))
    xheight = int(input("Height (cm): "))
    bmi = calc(xweight, xheight)
    print("Your BMI is " + str(round(bmi, 1)) + ", which is:", end=" ")
    classify(bmi)

__author__ = "Nico Hähn"
__copyright__ = "Copyright 2020, Thomas Lenz, Nico Hähn"
__credits__ = ["Nico Hähn", "Thomas Lenz"]
__license__ = "MIT"
__version__ = "0.2"
__maintainer__ = "Nico Hähn"
__email__ = "nicohaehn@t-online.de"
__status__ = "Prototype"
