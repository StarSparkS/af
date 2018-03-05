# CLASSIFICATION: UNCLASSIFIED
# Now that we have:
#     Randy's 3 bins (IV&V, SwA, Acq),
#     Gordon's 4 bins (Control, Must, Nice, Like)
#     Jerita's 26 bins (report card)
#     My bins (Red, White, Blue)
#     Code CSCI bins,
# Please craft a python script and/or excel sheet, like the autoti one, that will
#     1. Given report card ratios
#     2. Given SLOC, complexity, and % reuse tables by program & CSCI
#     3. Given major facility upgrades costs by FY
#     4. Given an average FTE for each Red, White, Blue
#     5. Given a fixed budget from the POM cycle
# Then, when Randy gives a funding cap by FY:
#     1. Provide Labor, Travel, Material by FY
#     2. Cost increase beyond controls by FY
# Also, If funding is not an issue, the what is the 3,5,7,9,11,13,15 year plan?
# Good luck,
# Jim
# CLASSIFICATION: UNCLASSIFIED

# while(1):
#     data = input()
#     if(data):
#         print ("hello")
# IVV 


import math,os,csv,functools,operator,io,re,sys,csv,requests,argparse, calendar
from copy import deepcopy
from collections import defaultdict
from pprint import pprint as pp
from datetime import date, timedelta, datetime
from decimal import *
# from lxml import html
from itertools import groupby


a = open("inputs.md.html","r")
tabstart = 0
tables = []
for n in a:
    if ("**_**"in n):
        if tabstart ==1:
            table = []

        tabstart+=1
        if tabstart ==3:
            tables.append(table)
            tabstart= tabstart%2
    elif tabstart ==2:
        if ("-" not in n and len(n)>0):
            table.append(n.replace("\t", " ").strip().replace(" ", "").split("|"))
  

        
        
print ("DONE")    
for tab in tables:
    print("table")
    for lin in tab:
        print (lin)
    print