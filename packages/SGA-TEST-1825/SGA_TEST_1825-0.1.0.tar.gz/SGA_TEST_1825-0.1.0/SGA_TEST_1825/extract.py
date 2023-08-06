# -*- coding: utf-8 -*-
"""
Created on Mon Feb  3 06:56:01 2020

@author: tanishs
"""
import pandas as pd


def type_str(string):
    
    if string.isdigit()==True:
        print("String is Numeric")
    elif string.isalpha()==True:
        print("String is Alphabetical")
    elif string.isalnum()==True:
        print("String is Alphanumeric")
    else:
        print("Incorrect Input")
                