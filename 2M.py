import math,os,csv,functools,operator,io,re,sys,csv,argparse, calendar
from copy import deepcopy
from collections import defaultdict
from pprint import pprint as pp
from datetime import date, timedelta, datetime
from decimal import *
from itertools import groupby
from openpyxl import * #reads workbooks
from HolidayScraper import webScraper #gets Federal Holidays

def main():
    args = cmdlread()
    holidays = webScraper()
    config(args, holidays)

def cmdlread():
    parser = argparse.ArgumentParser(description='Command-line, Automated Budgeting and Projection Program in Python.') 
    parser.add_argument('-w', metavar= 'wFile')
    parser.add_argument('-file', metavar='FILE',help='the input team file to read from')
    parser.add_argument('-rates', metavar='RATE',help='the input rates folder to read from')
    parser.add_argument('-eqs', metavar='EQS',help='the input equivalency file to read from')
    parser.add_argument('-log', metavar="LOG",help='Keeps track of when tests were run') 
    parser.add_argument('-tf', metavar='TFR',help="Filter One File and test only certain Team")
    parser.add_argument('-name', metavar='NAME',help="singleName (""first.last"") for projecting/funding")
    parser.add_argument('-lu', action='store_true',help="Generates ACTS LABOR UPLOAD CSV upload template")
    parser.add_argument('-date', metavar='DATE',help="Enter Date to Find Money Required to reach Date yyyy-mm-dd")
    parser.add_argument('-amt', metavar='AMOUNT',help="Enter Amount to Find Runouts and Distribution of Hours For All task orders")
    parser.add_argument('-ksr', metavar='RATIO',help="Testing Ratio")
    parser.add_argument('-rl', action='store_true', help="Removes Balancing Limits to Burn Down Money")
    parser.add_argument('-comp', metavar='CMP',help="Filter by company")
    parser.add_argument('-exl', metavar="EXL", help="Runs without a certain company")
    args = parser.parse_args()
    return args 
def filtercmd():
    return 
def config(args, holidays):
    wb = load_workbook(filename = 'wt1.xlsx')
    s = wb.sheetnames
    return
if __name__ == '__main__':
    main()

