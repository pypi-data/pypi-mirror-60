#!/usr/bin/env python

"""bmi.py: A tool that provides functions to check for the bmi of input data."""

from time import sleep


def get_bmi():
    mass = float(input("Wie viel wiegst du? (kg) "))
    cm_height = float(input("Wie groß bist du? (cm) "))
    height = cm_height / 100
    squareheight = height * height
    float_bmi = mass / squareheight
    bmi = round(float_bmi, 1)
    str_bmi = str(bmi)
    for i in range(2):
        print("")
    print("Dein BMI ist: "
          + str_bmi
          + "!")
    classify(bmi)
    again = input("Möchtest du einen neuen BMI berechnen? (y/n) ")
    for i in range(3):
        print("")
    if again == 'y':
        get_bmi()
    else:
        print("Das Programm wird nun beendet!")
        sleep(3)


def classify(bmi):
    if bmi < 16:
        print("Das ist starkes Untergewicht!")
    elif 16 < bmi < 16.9:
        print("Das ist mäßiges Untergewicht!")
    elif 17 < bmi < 18.4:
        print("Das ist leichtes Untergewicht!")
    elif 18.5 < bmi < 24.9:
        print("Das ist Normalgewicht!")
    elif 25 < bmi < 29.9:
        print("Das ist Präadipositas (Übergewicht)")
    elif 30 < bmi < 34.9:
        print("Das ist Adipositas Grad 1!")
    elif 35 < bmi < 39.9:
        print("Das ist Adipositas Grad 2!")
    elif bmi > 40:
        print("Das ist Adipositas Grad 3!")


if __name__ == '__main__':
    try:
        get_bmi()
    except KeyboardInterrupt:
        print("Stopping...")
        sleep(1)
    finally:
        exit()

__author__ = "Nico Hähn"
__copyright__ = "Copyright 2020, Thomas Lenz, Nico Hähn"
__credits__ = ["Nico Hähn", "Thomas Lenz"]
__license__ = "MIT"
__version__ = "0.1"
__maintainer__ = "Nico Hähn"
__email__ = "nicohaehn@t-online.de"
__status__ = "Prototype"
