import math,os,csv,functools,operator,io,re,sys,csv,requests,argparse, calendar
from copy import deepcopy
from collections import defaultdict
from pprint import pprint as pp
from datetime import date, timedelta, datetime
from decimal import *
from lxml import html
from itertools import groupby

import plotly
from plotly.graph_objs import Bar, Area, Layout
import plotly.plotly as py
import plotly.graph_objs as go
def enum(**enums):return type('Enum', (), enums)
pd = enum(name=0,color=1,customer=2,center=3,contract=4,company=5,lc=6,site=7,loe=8,runout=9,gna=10,hrs=11,val=12,tr=13, df=14, hf=15)
rd = enum(contract=0,company=1,lc=2,site=3,dl=4,dg=5,rate=6)
mpr = enum(FY = 0, ID = 1, MIV = 2, awarded =3, submitted = 4, drafted = 5, balance = 6, pb = 7, pe = 8, ce=9, tp = 10)
rr = enum(rr = Decimal(130))
ks = enum(ratio = Decimal(1)) # need to create a ratio that automically adjusts based on # of people in test and amount of money
cent = Decimal('0.01')
taskdic = {}
# monpro = {}

def main():
    mipr = []
    cent = Decimal('0.01')
    #
    # Command Line Parsing
    #
    os.system('cls') #Begin Command Line Parsing
    print "\nCommand-line, Automated Budgeting and Projection Program in Python\n" 
    print
    parser = argparse.ArgumentParser(description='Command-line, Automated Budgeting and Projection Program in Python.')
    parser.add_argument('file', metavar='FILE',help='the input team file to read from')
    parser.add_argument('rates', metavar='RATE',help='the input rates file to read from')
    parser.add_argument('eqs', metavar='EQS',help='the input equivalency file to read from')
    parser.add_argument('log', metavar="LOG",help='Keeps track of when tests were run')   
    parser.add_argument('-date', metavar='DATE',help="Enter Date to Find Money Required to reach Date yyyy-mm-dd")
    parser.add_argument('-amt', metavar='AMOUNT',help="Enter Amount to Find Runouts and Distribution of Hours For All task orders")
    parser.add_argument('-ksr', metavar='RATIO',help="Testing Ratio")
    parser.add_argument('-rl', action='store_true', help="Removes Balancing Limits to Burn Down Money")
    parser.add_argument('-name', metavar='NAME',help="singleName for projecting/funding")
    parser.add_argument('-comp', metavar='CMP',help="Filter by company")
    parser.add_argument('-exl', metavar="EXL", help="Runs without a certain company")
    parser.add_argument('-tf', metavar='TFR',help="Filter One File and test only certain Team")
    parser.add_argument('-r3', action='store_true', help="Prints Custom Financial Report")
    #below commands still under development 1/9/2018
    parser.add_argument('MIPR', metavar='MIPRCSV',help='the input rates file to read from')
    parser.add_argument('TRAVEL', metavar='TRAVELCSV',help='the input rates file to read from')
    parser.add_argument('TI', metavar='TINCSV',help='the input rates file to read from')
    parser.add_argument('-names', metavar='NAMES',help="group of names for projecting/funding")
    parser.add_argument('-mpr', metavar='MPR',help="Use Only the Following MIPR for funding")
    parser.add_argument('-dr1', metavar='dt1',help="Date Range Start")
    parser.add_argument('-dr2', metavar='dt2',help="Date Range End")
    parser.add_argument('-tr', action='store_true')
    parser.add_argument('-m', action='store_true')
    parser.add_argument('-t', action='store_true')
    # parser.add_argument('-', action='store_true', help="Prints Custom Financial Report")

    #parser contract?
    args = parser.parse_args()
    logruns = open('RUN_LOG.csv', 'a')
    linr = str("Python 2.7   ")+ str(datetime.now().strftime('%Y-%m-%d %H:%M:%S')) + "\t\t"
   

    rf = open(args.file).read().split("\n") ##
    #
    # Read in Inputs/create data structures
    #
    spt = args.rates
    people = teamInput(csv.reader(rf))
    holidays = webScraper()
    dateratelookup = dataMaker(people, spt)
    #find start date
    start_Date = (map(min, zip(*(filter(lambda x: x[pd.runout].year > 1950, people))))[pd.runout])+timedelta(days=1)
    #
    # Split Team to GNA vs NON GNA
    #
    # Parse based on inpute command (date vs amount)
    #
   

    if(args.ksr):
        ks.ratio = Decimal(args.ksr)
        linr = linr + "KSR Ratio: \t" + args.ksr + '\t\t'
    if(args.MIPR and args.m):
        print "MIPR DATA FILE available"
        print "Inputting and Updating Balances based on expenses/submissions \n"
        mf = open(args.MIPR).read().split("\n")
        mfr = csv.reader(mf)
        for row in mfr:
            if len(row)>0:
                # print row
                mipr.append(row)
        mipr = mipr[1:]
        for row in mipr:
            row[mpr.balance] = Decimal(row[mpr.MIV]) - Decimal(row[mpr.awarded])- Decimal(row[mpr.submitted])
            # d = []'
            # row[mpr.pe] = date([int(i) for i in row[mpr.pe]])
            m ,d, y  = row[mpr.pb].strip().split("/")
            row[mpr.pb] = date(int(y), int(m), int(d))
            m ,d, y  = row[mpr.pe].strip().split("/")
            row[mpr.pe] = date(int(y), int(m), int(d))
            if (datetime.now().year == row[mpr.pe].year):
                mb = row[mpr.pe].month -datetime.now().month
                if (mb <= 2 and mb >= 0 and row[mpr.balance] > 0):
                    print "Warning unused MIPR balance with POP END approaching. Submit MIPR drafts soon"
                if (mb < 0 and row[mpr.balance]>0):
                    print "URGENT URGENT URGENT. THIS could result in future loss of funds or a carry"
            if (datetime.now().year - row[mpr.pe].year>0 and row[mpr.balance]>0 ):
                 print "URGENT URGENT URGENT. THIS could result in future loss of funds or a carry"    
        print
        print
        for row in mipr:
            print row
    if(args.TRAVEL and args.tr):
        print "TRAVEL DATA FILE available"
        print args.TRAVEL
    if(args.eqs):
        eqss = open(args.eqs).read().split("\n") 
        for n in eqss:
            if(len(n) > 0):
                taskdic[n.split()[0]]= str(n.split()[1])       
    if(args.tf):
        ti = str(args.tf).split("/")
        # 
        contracts = []
        for to in range (0, len(ti)):
            contracts.append(taskdic[ti[to]])        
        fp = filter(lambda gto : gto[pd.contract] in contracts, people)
        people = fp
        linr = linr + "Contracts: \t" + args.tf + '\t\t'
    if(args.name):
        # print args.name.replace(".", " ")
        fpeople =filter(lambda gto: gto[pd.name] == str(args.name.replace(".", " ")), people)
        # print people[pd.name]
        people = fpeople
        linr = linr + "Person: \t" + args.name + '\t\t'
        # exit(1)
    if(args.comp):
        # print args.name.replace(".", " ")
        fpeople =filter(lambda gto: (gto[pd.company]).strip()== str(args.comp).strip(), people)
        # print people[pd.name]
        people = fpeople
        linr = linr + "Company: \t" + args.comp + '\t\t'
        # exit(1)
    if(args.exl):
        # print args.name.replace(".", " ")
        fpeople =filter(lambda gto: gto[pd.company] != str(args.exl), people)
        # print people[pd.name]
        people = fpeople
        linr = linr + "Company Excluded: \t" + args.exl + '\t\t'
        # exit(1)
    team = filter(lambda x: len(x[pd.gna]) == 0, people)
    accountants = filter(lambda x: len(x[pd.gna]) >0, people)
    if(args.r3):
        linr = linr + "Financial Report Requested" + '\t\t'
        reportdates = []
        SED_DS = []
        SED_IH = []
        SED_TOTS = []
        SSDD_DS = []
        SSDD_IH = []
        SSDD_TOTS = []
        MDA_AMT = []
        TOTS= []
        r3m = [1,2,3]
        r3m = map(lambda x:x+int(start_Date.month), r3m)
        # print r3m
        for n in r3m:
            year = start_Date.year
            if(n > 12):
                n-=12
                year = year +1
            days = int(calendar.monthrange(year, n)[1])
            y = int(year)
            month = int(n)
            reportdates.append(date(int(year), int(n), int(days)))
        for end_Date in reportdates:
            for row in people:
                row[pd.hrs] = 0
                row[pd.val] = 0
                row[pd.tr] = Decimal(rr.rr)
                row[pd.df] = 0
                row[pd.hf] = 0
            workdays = workdayFinder(start_Date, end_Date, holidays)
            # temppeople = people
            tolist, people = dates_to_funding(dateratelookup, start_Date, workdays, people, team, accountants)
            ngs = ["MIPR", "InHouse", "InHouse-SSDD", "InHouse-SED", "InHouse-MDA"]
            try:
                SEDhrs = sum(zip(*(filter(lambda gto : gto[pd.center]=="SED", people)))[pd.hrs])
            except:
                SEDhrs =  0
            try:
                SED_G_mon = sum(zip(*(filter(lambda gto : gto[pd.center]=="SED" and gto[pd.contract] in ngs , people)))[pd.val])
            except:
                SED_G_mon = 0
            try:
                SED_ds_mon=  sum(zip(*(filter(lambda gto : gto[pd.center]=="SED" and gto[pd.contract] not in ngs , people)))[pd.val])
            except:
                SED_ds_mon = 0
            try:
                SSDDhrs = sum(zip(*(filter(lambda gto : gto[pd.center]=="SSDD", people)))[pd.hrs])
            except:
                SSDDhrs = 0
            try:
                SSDD_G_mon = sum(zip(*(filter(lambda gto : gto[pd.center]=="SSDD" and gto[pd.contract] in ngs , people)))[pd.val])
            except:
                SSDD_G_mon = 0
            try:
                SSDD_ds_mon=  sum(zip(*(filter(lambda gto : gto[pd.center]=="SSDD" and gto[pd.contract] not in ngs , people)))[pd.val])
            except:
                SSDD_ds_mon = 0
            try:
                MDAhrs = sum(zip(*(filter(lambda gto : gto[pd.center]=="MDA", people)))[pd.hrs])
            except:
                MDAhrs = 0
            try:
                MDAmon=  sum(zip(*(filter(lambda gto : gto[pd.center]=="MDA", people)))[pd.val])
            except:
                MDAmon = 0
            print "\nCenter"
            print "SED: "
            print "\t Hours:       H ", round(SEDhrs, 2)
            print "\t Cost_DS:      $ ", Decimal(SED_ds_mon).quantize(cent, rounding= ROUND_UP)
            print "\t Cost_G       $ ", Decimal(SED_G_mon).quantize(cent, rounding= ROUND_UP)
            print "\t InHouseGnA:  $ ", (SED_ds_mon*Decimal(.03)).quantize(cent, rounding= ROUND_UP)
            print "\t InHouse Total $", Decimal(SED_G_mon).quantize(cent, rounding= ROUND_UP) + (SED_ds_mon*Decimal(.03)).quantize(cent, rounding= ROUND_UP)
            print "\t Total" , Decimal(SED_G_mon).quantize(cent, rounding= ROUND_UP)+(Decimal(SED_ds_mon)).quantize(cent, rounding= ROUND_UP) + (SED_ds_mon*Decimal(.03)).quantize(cent, rounding= ROUND_UP)
            print
            print "SSDD: "
            print "\t Hours:       H ", round(SSDDhrs,2)
            print "\t Cost_DS:        $ ", Decimal(SSDD_ds_mon).quantize(cent, rounding= ROUND_UP)
            print "\t Cost_G       $ ", Decimal(SSDD_G_mon).quantize(cent, rounding= ROUND_UP)
            print "\t InHouseGnA:  $ ", (SSDD_ds_mon*Decimal(.035)).quantize(cent, rounding= ROUND_UP)
            print "\t InHouse Total $", Decimal(SSDD_G_mon).quantize(cent, rounding= ROUND_UP) + (SSDD_ds_mon*Decimal(.035)).quantize(cent, rounding= ROUND_UP)
            print "\t Total" , Decimal(SSDD_G_mon).quantize(cent, rounding= ROUND_UP)+(Decimal(SSDD_ds_mon)).quantize(cent, rounding= ROUND_UP) + (SSDD_ds_mon*Decimal(.035)).quantize(cent, rounding= ROUND_UP)
            print
            print "MDA:"
            print "\t Hours:       H ", round(MDAhrs,2)
            print "\t Cost:        $ ", Decimal(MDAmon).quantize(cent, rounding= ROUND_UP)
            print
            print "*"*50
            print "FULL TOTAL : ",  Decimal(MDAmon).quantize(cent, rounding= ROUND_UP)\
            +(Decimal(SSDD_ds_mon)).quantize(cent, rounding= ROUND_UP)\
            +(SSDD_ds_mon*Decimal(.035)).quantize(cent, rounding= ROUND_UP)\
            +(Decimal(SED_ds_mon)).quantize(cent, rounding= ROUND_UP)\
            +(SED_ds_mon*Decimal(.03)).quantize(cent, rounding= ROUND_UP)\
            + Decimal(SSDD_G_mon).quantize(cent, rounding= ROUND_UP)\
            + Decimal(SED_G_mon).quantize(cent, rounding= ROUND_UP)
            print "*"*50
            SED_DS.append( Decimal(SED_ds_mon).quantize(cent, rounding= ROUND_UP))
            SED_IH.append(Decimal(SED_G_mon).quantize(cent, rounding= ROUND_UP) + (SED_ds_mon*Decimal(.03)).quantize(cent, rounding= ROUND_UP))
            SED_TOTS.append( Decimal(SED_G_mon).quantize(cent, rounding= ROUND_UP)+(Decimal(SED_ds_mon)).quantize(cent, rounding= ROUND_UP) + (SED_ds_mon*Decimal(.03)).quantize(cent, rounding= ROUND_UP))
            SSDD_DS.append(Decimal(SSDD_ds_mon).quantize(cent, rounding= ROUND_UP))
            SSDD_IH.append(Decimal(SSDD_G_mon).quantize(cent, rounding= ROUND_UP) + (SSDD_ds_mon*Decimal(.035)).quantize(cent, rounding= ROUND_UP))
            SSDD_TOTS.append(Decimal(SSDD_G_mon).quantize(cent, rounding= ROUND_UP)+(Decimal(SSDD_ds_mon)).quantize(cent, rounding= ROUND_UP) + (SSDD_ds_mon*Decimal(.035)).quantize(cent, rounding= ROUND_UP))
            MDA_AMT.append(Decimal(MDAmon).quantize(cent, rounding= ROUND_UP))
            TOTS.append(Decimal(MDAmon).quantize(cent, rounding= ROUND_UP)\
            +(Decimal(SSDD_ds_mon)).quantize(cent, rounding= ROUND_UP)\
            +(SSDD_ds_mon*Decimal(.035)).quantize(cent, rounding= ROUND_UP)\
            +(Decimal(SED_ds_mon)).quantize(cent, rounding= ROUND_UP)\
            +(SED_ds_mon*Decimal(.03)).quantize(cent, rounding= ROUND_UP)\
            + Decimal(SSDD_G_mon).quantize(cent, rounding= ROUND_UP)\
            + Decimal(SED_G_mon).quantize(cent, rounding= ROUND_UP))
        #
        #PRINT REPORT
        #
        r3name = r"Outputs/"+ str(datetime.now().strftime('%Y_%m_%d_%H_%M_%S'))+"_Financial_Lookout_3months.md.html"
        f = open(r3name, "w+")
        f.write("!!!note\n")
        f.write("**GME-S Financial Report**")
        f.write("\n")
        f.write("  | Type | Cost")
        f.write("<table border = \"1\">")
        f.write("<tr><td>Row 1, Column 1</td><td>Row 1, Column 2</td></tr><tr><td>Row 1, Column 1</td><td>Row 1, Column 2</td></tr>")
        f.write("</table>")
# ---- |:----:| ----:
# Fish |  F   | 1.00
# Axe  |  W   | 3.25
# Gold |  I   |20.50
        f.write("<!-- Markdeep: --><style class=\"fallback\">body{visibility:hidden;white-space:pre;font-family:monospace}</style><script src=\"markdeep.min.js\"></script><script src=\"https://casual-effects.com/markdeep/latest/markdeep.min.js\"></script><script>window.alreadyProcessedMarkdeep||(document.body.style.visibility=\"visible\")</script>")
        f.close()
    if (args.date): # Returns funding required to reach a certain date
        linr = linr + "Funding Required to Reach: \t" + args.date + '\t\t'
        # parse command line date/ create list of workdays between startdate and target date
        m,d ,yr= args.date.strip().split("-")
        end_Date = date(int(yr), int(m), int(d))
        workdays = workdayFinder(start_Date, end_Date, holidays)
        tolist, people = dates_to_funding(dateratelookup, start_Date, workdays, people, team, accountants)
        ngs = ["MIPR", "InHouse", "InHouse-SSDD", "InHouse-SED", "InHouse-MDA"]

        try:
            SEDhrs = sum(zip(*(filter(lambda gto : gto[pd.center]=="SED", people)))[pd.hrs])
        except:
            SEDhrs =  0
        try:
            SED_G_mon = sum(zip(*(filter(lambda gto : gto[pd.center]=="SED" and gto[pd.contract] in ngs , people)))[pd.val])
        except:
            SED_G_mon = 0
        try:
            SED_ds_mon=  sum(zip(*(filter(lambda gto : gto[pd.center]=="SED" and gto[pd.contract] not in ngs , people)))[pd.val])
        except:
            SED_ds_mon = 0
        try:
            SSDDhrs = sum(zip(*(filter(lambda gto : gto[pd.center]=="SSDD", people)))[pd.hrs])
        except:
            SSDDhrs = 0
        try:
            SSDD_G_mon = sum(zip(*(filter(lambda gto : gto[pd.center]=="SSDD" and gto[pd.contract] in ngs , people)))[pd.val])
        except:
            SSDD_G_mon = 0
        try:
            SSDD_ds_mon=  sum(zip(*(filter(lambda gto : gto[pd.center]=="SSDD" and gto[pd.contract] not in ngs , people)))[pd.val])
        except:
            SSDD_ds_mon = 0
        try:
            MDAhrs = sum(zip(*(filter(lambda gto : gto[pd.center]=="MDA", people)))[pd.hrs])
        except:
            MDAhrs = 0
        try:

            MDAmon=  sum(zip(*(filter(lambda gto : gto[pd.center]=="MDA", people)))[pd.val])
        except:
            MDAmon = 0
        #
        # Outputs Costs by branch
        #
        print "\nCenter"
        print "SED: "
        print "\t Hours:       H ", round(SEDhrs, 2)
        print "\t Cost_DS:      $ ", Decimal(SED_ds_mon).quantize(cent, rounding= ROUND_UP)
        print "\t Cost_G       $ ", Decimal(SED_G_mon).quantize(cent, rounding= ROUND_UP)
        print "\t InHouseGnA:  $ ", (SED_ds_mon*Decimal(.03)).quantize(cent, rounding= ROUND_UP)
        print "\t InHouse Total $", Decimal(SED_G_mon).quantize(cent, rounding= ROUND_UP) + (SED_ds_mon*Decimal(.03)).quantize(cent, rounding= ROUND_UP)
        print "\t Total" , Decimal(SED_G_mon).quantize(cent, rounding= ROUND_UP)+(Decimal(SED_ds_mon)).quantize(cent, rounding= ROUND_UP) + (SED_ds_mon*Decimal(.03)).quantize(cent, rounding= ROUND_UP)
        print
        print "SSDD: "
        print "\t Hours:       H ", round(SSDDhrs,2)
        print "\t Cost_DS:        $ ", Decimal(SSDD_ds_mon).quantize(cent, rounding= ROUND_UP)
        print "\t Cost_G       $ ", Decimal(SSDD_G_mon).quantize(cent, rounding= ROUND_UP)
        print "\t InHouseGnA:  $ ", (SSDD_ds_mon*Decimal(.035)).quantize(cent, rounding= ROUND_UP)
        print "\t InHouse Total $", Decimal(SSDD_G_mon).quantize(cent, rounding= ROUND_UP) + (SSDD_ds_mon*Decimal(.035)).quantize(cent, rounding= ROUND_UP)
        print "\t Total" , Decimal(SSDD_G_mon).quantize(cent, rounding= ROUND_UP)+(Decimal(SSDD_ds_mon)).quantize(cent, rounding= ROUND_UP) + (SSDD_ds_mon*Decimal(.035)).quantize(cent, rounding= ROUND_UP)
        print
        print "MDA:"
        print "\t Hours:       H ", round(MDAhrs,2)
        print "\t Cost:        $ ", Decimal(MDAmon).quantize(cent, rounding= ROUND_UP)
        print
        print "*"*50
        print "FULL TOTAL : ",  Decimal(MDAmon).quantize(cent, rounding= ROUND_UP)\
        +(Decimal(SSDD_ds_mon)).quantize(cent, rounding= ROUND_UP)\
        +(SSDD_ds_mon*Decimal(.035)).quantize(cent, rounding= ROUND_UP)\
        +(Decimal(SED_ds_mon)).quantize(cent, rounding= ROUND_UP)\
        +(SED_ds_mon*Decimal(.03)).quantize(cent, rounding= ROUND_UP)\
        + Decimal(SSDD_G_mon).quantize(cent, rounding= ROUND_UP)\
        + Decimal(SED_G_mon).quantize(cent, rounding= ROUND_UP)
        print "*"*50
        print
        ###Teams
        clrs = sorted(list(set([lin[pd.color] for lin in people])))
        cstrs = sorted(list(set([lin[pd.customer] for lin in people])))
        for n in clrs:
            print n, "Team -", sum(zip(*(filter(lambda gto : gto[pd.color]== n, people)))[pd.val])
            nteam = filter(lambda gto : gto[pd.color] == n, people)
            for ac in cstrs:
                try:
                    accost = sum(zip(*(filter(lambda gto : gto[pd.customer]== ac, nteam)))[pd.val])
                except:
                    accost = 0
                print  "\t", ac, " - ", accost
            if n == "Green":
                print "+ GNA"
                print "\tInHouse GNA Team - ", (SED_ds_mon*Decimal(.03)).quantize(cent, rounding= ROUND_UP) +(SSDD_ds_mon*Decimal(.035)).quantize(cent, rounding= ROUND_UP)
                print "\tSED - " ,(SED_ds_mon*Decimal(.03)).quantize(cent, rounding= ROUND_UP)
                print "\tSSDD - " ,(SSDD_ds_mon*Decimal(.035)).quantize(cent, rounding= ROUND_UP)
                print 
                print "Recalculated Green"
                print n, "Team -", sum(zip(*(filter(lambda gto : gto[pd.color]== n, people)))[pd.val]) + (SED_ds_mon*Decimal(.03)).quantize(cent, rounding= ROUND_UP) +(SSDD_ds_mon*Decimal(.035)).quantize(cent, rounding= ROUND_UP)
                print
        print
        #   finds unique set of tos to iterate through
        tolist = sorted(list(set([lin[pd.contract] for lin in people])))
        #
        # Outputs Cost by Task Order and by Labor Category
        #
        for to in tolist:
            tot = filter(lambda gto : gto[pd.contract]==to, people)
            hrs = sum(zip(*(tot))[pd.hrs])
            mon=  sum(zip(*tot)[pd.val])
            print "Contract: ", to,  hrs, "$",mon, "\n"
            alc = sorted(list(set([tuple(lin[pd.company:pd.loe]) for lin in tot])))
            for lis in alc:
                scf = [lambda cm : cm[pd.company] == lis[0], lambda lcc : lcc[pd.lc] ==lis[1], lambda st : st[pd.site] == lis[2]]
                scc = filter( lambda x: all(f(x) for f in scf), tot )
                print "\t Category: ", lis#, "\n"
                for row in scc:
                    print "\t\t", row[pd.hrs], (5- len(str(row[pd.hrs])))*" ",  "\t", row[pd.val], (10- len(str(row[pd.val])))*" ", "."*6, row[0]
                print "\t\t", "-"*16
                print "\t\t" ,sum(zip(*scc)[pd.hrs]), '\t', sum(zip(*scc)[pd.val]), "\n"
            print
        print
        for x in people:
            print x  
    if (args.amt): # Returns runout date and hours based on given amount
        linr = linr + "Date Projection based on Funding: \t" + args.amt + '\t\t'
        InHouseGNA = IHG = 0
        IHGssdd = 0
        IHGsed = 0
        print args.amt, "\n"
        if(len(accountants)> 0):
            ggna = (Decimal(args.amt)*Decimal(.03)).quantize(cent, rounding= ROUND_UP)
            print "Guess GNA = 3%", ggna
            #
            # loop through accountants (direct site gna) and give them rate (using start_date (date of earliest runout))
            #
            for pol in accountants:
                ratefilters = [lambda drl: drl[rd.contract]==pol[pd.contract],lambda drl: drl[rd.company] == pol[pd.company],
                    lambda drl: drl[rd.lc] == pol[pd.lc],lambda drl: drl[rd.site] == pol[pd.site],
                    lambda drl: drl[rd.dl]<=day, lambda drl: drl[rd.dg]>= day]
                day = start_Date
                rate1 = filter( lambda x: all(f(x) for f in ratefilters), dateratelookup )[0][rd.rate]
                pol[pd.tr] = rate1
            #
            # use the single rate assigned to each lc based on start_Date to calculate GNA
            #
            while(ggna>0):
                for lin in accountants:
                    # if(ggna >0):
                    mval = len(lin[pd.gna].split(" "))
                    lin[pd.hrs] += Decimal(mval)*Decimal(lin[pd.loe])
                    lin[pd.val] += (Decimal(mval)*Decimal(lin[pd.loe]) * lin[pd.tr]).quantize(cent, rounding= ROUND_UP)
                    ggna -=(Decimal(mval)*Decimal(lin[pd.loe]) * lin[pd.tr]).quantize(cent, rounding= ROUND_UP)
                if(ggna < 0): #you finished funding ggna evenly but now there may be hours that are not integer value, this condition will fix not integer hours
                    for lin in accountants:
                        mval = len(lin[pd.gna].split(" "))
                        mdf = Decimal(math.ceil(lin[pd.hrs])) - Decimal(lin[pd.hrs])
                        lin[pd.hrs] += mdf
                        lin[pd.hrs] = int(lin[pd.hrs])
                        lin[pd.val] += (mdf * lin[pd.tr]).quantize(cent, rounding= ROUND_UP)
                        lin[pd.val] = lin[pd.val].quantize(cent, rounding= ROUND_UP)
                        ggna -=(mdf * lin[pd.tr]).quantize(cent, rounding= ROUND_UP)
                        ggna = ggna.quantize(cent, rounding= ROUND_UP)
            #
            # Calculate new balance - GnA costs
            # 
            
            
            agna = ((Decimal(args.amt)*Decimal(.03)).quantize(cent, rounding= ROUND_UP) + Decimal(abs(ggna)))#.quantize(cent, rounding= ROUND_UP)
            print "Actual GNA = ", agna
            balance = Decimal(args.amt)-Decimal(agna)
            print "Balance after GNA (variables) : ",args.amt , " - ", agna , " = ", balance
            print "Stored Balance (data)", Decimal(args.amt) - sum(row[pd.val] for row in people)
            if (Decimal(args.amt) - sum(row[pd.val] for row in people) == balance):
                print "-----SUCCESS!-----GNA FUNDED WITH NO BALANCE ISSUES\n"
                print "FUNDING INHOUSE GNA BASED ON DATA"
            else:
                print "FAIL", balance, "\t", Decimal(args.amt) - sum(row[pd.val] for row in people)
                exit(1)
        else:
            print "Warning: NO GNA funding provided" 
            agna = Decimal(0)
            ggna = Decimal(0)
            balance = Decimal(args.amt)


        ####################################################################
        # All Direct Site GNA funding complete and balance has been verified
        ####################################################################
        #
        if (balance< 0): #"Funding amount too small to fund gna + team (allocating a single hour to gna people reduces balance to less than zero.)"
            n = raw_input("Would you like to fund hours to team if possible? yes/no")
            if(str(n)== "yes"):
                for row in people:
                    people[pd.val] = 0
                    people[pd.hrs] = 0
                balance = args.amt
        
        #*************************************************#
        #Use remaining balance to efficiently fund the team
        #*************************************************#
        ob = balance
        day = start_Date
        rhr = 0
        nx = 0
        adf = 0
        finalbalance = 0
        lwd =""
        while (balance > 0):
            day = start_Date + timedelta(days = ((rhr/8) + nx ))
            if (day.weekday() < 5) and (day not in holidays): #if today is a working day ---> fund team
                teamcostforday = 0
                #
                #find cost of team funding for current day and store in "teamcostforday"
                #
                for pol in team: 
                    if day>pol[pd.runout]:
                        ratefilters = [lambda drl: drl[rd.contract]==pol[pd.contract],lambda drl: drl[rd.company] == pol[pd.company],
                        lambda drl: drl[rd.lc] == pol[pd.lc],lambda drl: drl[rd.site] == pol[pd.site],
                        lambda drl: drl[rd.dl]<=day, lambda drl: drl[rd.dg]>= day]
                        try:
                            rate1 = filter( lambda x: all(f(x) for f in ratefilters), dateratelookup )[0][rd.rate]
                        except:
                            rate1 = rr.rr
                        pol[pd.tr] = rate1
                        teamcostforday += (Decimal(rate1)*Decimal(8)*Decimal(pol[pd.loe]))
                #
                #if funding is available to fund the team for current day, fund the team
                # else-->
                #
                if (balance - teamcostforday > 0): 
                    for pol in team:
                        if day>pol[pd.runout]:
                            pol[pd.df] +=1
                            pol[pd.hrs] += Decimal(8)* Decimal(pol[pd.loe])
                            pol[pd.val] += (Decimal(pol[pd.tr])*Decimal(8)*Decimal(pol[pd.loe])).quantize(cent, rounding= ROUND_UP)
                            balance -=(Decimal(pol[pd.tr])*Decimal(8)*Decimal(pol[pd.loe])).quantize(cent, rounding= ROUND_UP)
                    adf+=1
                    lwd = day
                #
                # proceed here if you do not have funds to fund the team for a current day (a day)
                #
                else:
                    #since you cannot fund the team for a day, compute the cost for funding the team for an hour
                    # and see if funding by hour is possible
                    tcfh = teamcostforhour = (teamcostforday/ Decimal(8)).quantize(cent, rounding= ROUND_UP)
                    hrfundable = balance /tcfh 
                    print "Day Funding Complete"
                    print "HR Funding Initiated"
                    #
                    # balance check
                    #
                    if(Decimal(args.amt) - sum(row[pd.val] for row in people) != balance): 
                        print "UNBALANCED balances"
                        exit(1)
                    #
                    # end of balance check
                    #
                    #
                    # Step 1: Balance hours to no decimal places to chip away at remainder if possible with split people
                    #
                    if(adf>0 and balance > 0): #This part is adjusting split 
                        spt = filter(lambda rt: (Decimal(rt[pd.loe]) >1.00 or Decimal(rt[pd.loe])<1.00) and (day>rt[pd.runout]), team)
                        for row in spt:
                            dff = Decimal(math.ceil(row[pd.hrs])) - Decimal(row[pd.hrs])
                            row[pd.hrs] += dff
                            row[pd.val] += (dff * Decimal(row[pd.tr])).quantize(cent, rounding= ROUND_UP)
                            balance -= (dff * Decimal(row[pd.tr])).quantize(cent, rounding= ROUND_UP)
                        print "Balance after adjustments:", balance
                        print "verify data", Decimal(args.amt) - sum(row[pd.val] for row in people)
                        if ((Decimal(args.amt) - sum(row[pd.val] for row in people)) == balance):
                            print "GOOD VERIFY"
                        #
                        #The following balance<0 is met when you fund the team for days and proceed to try and fund the team by hours
                        # when you clean up the split hours and you have a negative balance, this condition is met
                        # at this point everyone has whole hours, but the balance is less than 0
                        #
                        if(balance <0):
                            print 'balance < 0 CONDITION!!!!!!!!!!!'
                            rates = sorted(list(set([lin[pd.tr] for lin in team])))
                            for row in rates:
                                if (row+balance >0):
                                    tu = filter(lambda a: a[pd.tr] == row, team)
                                    print tu
                                    tu[0][pd.val] -= tu[0][pd.tr]
                                    tu[0][pd.hrs] -= 1
                                    tu[0][pd.df] -= 1
                                    tu[0][pd.hf] +=7
                                    balance += row
                                    break
                            finalbalance = balance
                            balance =0
                        else:
                            #
                            # This is where its possible to fund the team for some number of hours
                            # You can also minimize the max weight BKS problem through constraints
                            #
                            hrfundable = balance /tcfh 
                            print 
                            print "FUNDING FULL TEAM for ", int(math.floor(hrfundable)), "  HRS "
                            print "HR cost approx", tcfh
                            #
                            # Constraint for Bounded Knapsack Problem
                            # Tries to fund the team evenly by hour while making sure there is enough money to have possibilities of a 0 remainder solution
                            # 
                            wtconstraint = ks.ratio*tcfh

                            #mxwt = 3000
                            #
                            for x in range(0, int(math.floor(hrfundable))):
                                for row in team:
                                    if (balance >(wtconstraint) and (balance - Decimal(row[pd.tr]) > 0)) and day>row[pd.runout]:
                                        row[pd.hrs] += 1
                                        row[pd.val] += Decimal(row[pd.tr]).quantize(cent, rounding= ROUND_UP)
                                        row[pd.hf] += 1
                                        balance -= Decimal(row[pd.tr]).quantize(cent, rounding= ROUND_UP)
                                        # print balance, wtconstraint
                            for row in team:
                                row[pd.hrs] = int(row[pd.hrs])
                                row[pd.val] = row[pd.val].quantize(cent, rounding= ROUND_UP)
                            print "REAL BALANCE: ", Decimal(args.amt) - sum(row[pd.val] for row in people)
                            print balance
                            finalbalance = balance
                            balance = 0 
                    else: #this will only occur if you input funding less than a day
                        #"FUND BY FULL HR ONLY"
                        prevbalance = 0
                        while (balance>0):
                            for pol in team:
                                if day>pol[pd.runout]:
                                    if (balance - Decimal(pol[pd.tr]) >0):
                                        pol[pd.hrs] += 1
                                        pol[pd.val] += (Decimal(pol[pd.tr]))
                                        balance -=(Decimal(pol[pd.tr]))
                            if(prevbalance == balance):
                                break
                            prevbalance = balance
                        # print balance
                        finalbalance = balance
                        balance = 0
                nx+=1
            else:
                nx+=1
        # print people
        # filter(lambda x : len(str(x))>0 , rld)      
        finalbalance = finalbalance.quantize(cent, rounding= ROUND_DOWN)
        ############################################
        ############################################
        ############################################
        # Balancing and Thresholding Complete
        # Last step is Dynamic Knapsack
        ############################################
        ############################################
        ############################################
        print "Initial Balance: ", args.amt
        print "GNA: " , agna
        print "Team: ", ob - finalbalance
        print 
        print "##########################"
        print "This is final balance" , finalbalance
        print "verify", sum(row[pd.val] for row in people)
        print "AMT" , Decimal(args.amt) - sum(row[pd.val] for row in people)
        nb = 0
        if(Decimal(args.amt) - sum(row[pd.val] for row in people) == finalbalance):
            print "GOOD VERIFY"
            nb = finalbalance
        else:
            print "ROUNDING ISSUE?????"
            nb = (Decimal(args.amt) - sum(row[pd.val] for row in people))
        print 
        print "##########################"
        print "Funding Covers Approx:", start_Date , "-",lwd
        print "last full day of coverage", lwd
        print "possibly partially funded day", day
        tb1 = finalbalance       
        rld = sorted(list(set([lin[pd.tr] for lin in team])))
        rld = filter(lambda x : len(str(x))>0 , rld)
        # print rld
        cr = math.ceil (tb1 / rld[0])
        combos = 1
        c2 = 1
        c3 = 1
        for n in team:
            combos *= cr
        for n in rld:
            try:
                c2 *= math.ceil(tb1 / n)
                c3 *= 8
            except:
                print fb
                print "ERRROR"
                print n
        # for val in dateratelookup
        print "Combinations to try ", combos
        print " Constrained to try", c2
        print "8 Hour Constraint ", c3
        print 
        print "MAX WT", tb1
        print 
        print "Now Populating DATA"

        ####
        ##### Bounded Knapsack Setup and Function Call
        ####
        adata = filter(lambda z:z[pd.runout] < day, team)
        maxwt = tb1
        maxwt = int(maxwt*100)
        mxh = 8
        if (args.rl):
            colasi = sorted(list(set([tuple([tuple([lin[pd.contract], lin[pd.company], lin[pd.lc], lin[pd.site]]), lin[pd.tr].quantize(cent, rounding= ROUND_UP), lin[pd.tr].quantize(cent, rounding= ROUND_UP),math.ceil(tb1/ lin[pd.tr])]) for lin in adata])))
        else:
            colasi = sorted(list(set([tuple([tuple([lin[pd.contract], lin[pd.company], lin[pd.lc], lin[pd.site]]), lin[pd.tr].quantize(cent, rounding= ROUND_UP), lin[pd.tr].quantize(cent, rounding= ROUND_UP), mxh ]) for lin in adata])))
        c2 = []
        for row in colasi:
            c2.append(row)
        items = sum( ([(item, int(Decimal(100)*Decimal(wt)), int(Decimal(100)*Decimal(val)))]*int(n) for item, wt, val ,n in c2), [])
        aloc = knapsack01_dp(items, maxwt)
        ####
        ##### BKS complete
        ####

        #### Adjusting Data based on BKS results
        closer = sum(item[2] for item in aloc)
        print "This is sum of new charges" ,((Decimal(closer))/100)
        print closer
        print 50*"^"
        print "Balance after BKS", tb1 - ((Decimal(closer))/100)
        print 50*"^"
        print "BALANCE VERIFY", nb
        # print aloc
        caloc = 0
        for row in aloc:
            rt = Decimal(row[2])/ Decimal(100)
            row = row[0]
            fr = [lambda w: w[pd.contract] == row[0], lambda x: x[pd.company] == row[1], lambda y: y[pd.lc] == row[2], lambda z: z[pd.site]==row[3], lambda a: day > a[pd.runout]] 
            v = sorted(filter(lambda x: all(f(x) for f in fr), team), key = lambda x : x[pd.hrs])
            v[0][pd.hrs] += 1
            v[0][pd.val] += v[0][pd.tr]
            caloc += v[0][pd.tr]
            v[0][pd.hf] += 1
        tolist = sorted(list(set([lin[pd.contract] for lin in people])))
        # exit(1)
        ####Data Adjustment Complete
        #
        # Outputs Cost by Task Order and by Labor Category
        #
        print " Final Verification"
        print "Input Amount: ", args.amt
        total = sum(row[pd.val] for row in people)
        # print total , args.amt
        if (total == Decimal(args.amt)):
            print "SUCCESS"
            for to in tolist:
                tot = filter(lambda gto : gto[pd.contract]==to, people)
                hrs = sum(zip(*(tot))[pd.hrs])
                mon=  sum(zip(*tot)[pd.val])
                print "Contract: ", to,  hrs, "$",mon , "\n"
                alc = sorted(list(set([tuple(lin[pd.company:pd.loe]) for lin in tot])))
                for lis in alc:
                    scf = [lambda cm : cm[pd.company] == lis[0], lambda lcc : lcc[pd.lc] ==lis[1], lambda st : st[pd.site] == lis[2]]
                    scc = filter( lambda x: all(f(x) for f in scf), tot )
                    print "\t Category: ", lis, "\n"
                    for row in scc:
                        print "\t\t", row[pd.hrs], (5- len(str(row[pd.hrs])))*" ",  "\t", row[pd.val], (10- len(str(row[pd.val])))*" ", "."*6, row[0]
                    print "\t\t", "-"*16
                    print "\t\t" ,sum(zip(*scc)[pd.hrs]), '\t', sum(zip(*scc)[pd.val]), "\n"
                print
            print 
        else:
            if (total < Decimal(args.amt)):
                print "Leftover amount", Decimal(args.amt) - total
                print "SUCCESS"
                for to in tolist:
                    tot = filter(lambda gto : gto[pd.contract]==to, people)
                    hrs = sum(zip(*(tot))[pd.hrs])
                    mon=  sum(zip(*tot)[pd.val])
                    print "Contract: ", to,  hrs, "$",mon , "\n"
                    alc = sorted(list(set([tuple(lin[pd.company:pd.loe]) for lin in tot])))
                    for lis in alc:
                        scf = [lambda cm : cm[pd.company] == lis[0], lambda lcc : lcc[pd.lc] ==lis[1], lambda st : st[pd.site] == lis[2]]
                        scc = filter( lambda x: all(f(x) for f in scf), tot )
                        print "\t Category: ", lis, "\n"
                        for row in scc:
                            print "\t\t", row[pd.hrs], (5- len(str(row[pd.hrs])))*" ",  "\t", row[pd.val], (10- len(str(row[pd.val])))*" ", "."*6, row[0]
                        print "\t\t", "-"*16
                        print "\t\t" ,sum(zip(*scc)[pd.hrs]), '\t', sum(zip(*scc)[pd.val]), "\n"
                    print
                print 
            else:
                
                print "ERROR UNKNOWN TOTAL > AMT ..... EXPENSES ERROR"
                print total
                print args.amt
        ###########################  
        # Add your OWN FILTER HERE to filter by team color/ team name/ etc
        #
        # pp(people)
        #
        ngs = ["MIPR", "InHouse", "InHouse-SSDD", "InHouse-SED", "InHouse-MDA"]
        try:
            SEDhrs = sum(zip(*(filter(lambda gto : gto[pd.center]=="SED", people)))[pd.hrs])
        except:
            SEDhrs =  0
        try:
            SED_G_mon = sum(zip(*(filter(lambda gto : gto[pd.center]=="SED" and gto[pd.contract] in ngs , people)))[pd.val])
        except:
            SED_G_mon = 0
        try:
            SED_ds_mon=  sum(zip(*(filter(lambda gto : gto[pd.center]=="SED" and gto[pd.contract] not in ngs , people)))[pd.val])
        except:
            SED_ds_mon = 0
        try:
            SSDDhrs = sum(zip(*(filter(lambda gto : gto[pd.center]=="SSDD", people)))[pd.hrs])
        except:
            SSDDhrs = 0
        try:
            SSDD_G_mon = sum(zip(*(filter(lambda gto : gto[pd.center]=="SSDD" and gto[pd.contract] in ngs , people)))[pd.val])
        except:
            SSDD_G_mon = 0
        try:
            SSDD_ds_mon=  sum(zip(*(filter(lambda gto : gto[pd.center]=="SSDD" and gto[pd.contract] not in ngs , people)))[pd.val])
        except:
            SSDD_ds_mon = 0
        try:
            MDAhrs = sum(zip(*(filter(lambda gto : gto[pd.center]=="MDA", people)))[pd.hrs])
        except:
            MDAhrs = 0
        try:
            MDAmon=  sum(zip(*(filter(lambda gto : gto[pd.center]=="MDA", people)))[pd.val])
        except:
            MDAmon = 0
        #
        # Outputs Costs by branch
        #
        print "*"*50
        print "\nCenter"
        print "SED: "
        print "\t Hours:       H ", round(SEDhrs, 2)
        print "\t Cost_DS:      $ ", Decimal(SED_ds_mon).quantize(cent, rounding= ROUND_UP)
        print "\t Cost_G       $ ", Decimal(SED_G_mon).quantize(cent, rounding= ROUND_UP)
        print "\t InHouseGnA:  $ ", (SED_ds_mon*Decimal(.03)).quantize(cent, rounding= ROUND_UP)
        print "\t InHouse Total $", Decimal(SED_G_mon).quantize(cent, rounding= ROUND_UP) + (SED_ds_mon*Decimal(.03)).quantize(cent, rounding= ROUND_UP)
        print "\t Total" , Decimal(SED_G_mon).quantize(cent, rounding= ROUND_UP)+(Decimal(SED_ds_mon)).quantize(cent, rounding= ROUND_UP) + (SED_ds_mon*Decimal(.03)).quantize(cent, rounding= ROUND_UP)
        print
        print "SSDD: "
        print "\t Hours:       H ", round(SSDDhrs,2)
        print "\t Cost_DS:        $ ", Decimal(SSDD_ds_mon).quantize(cent, rounding= ROUND_UP)
        print "\t Cost_G       $ ", Decimal(SSDD_G_mon).quantize(cent, rounding= ROUND_UP)
        print "\t InHouseGnA:  $ ", (SSDD_ds_mon*Decimal(.035)).quantize(cent, rounding= ROUND_UP)
        print "\t InHouse Total $", Decimal(SSDD_G_mon).quantize(cent, rounding= ROUND_UP) + (SSDD_ds_mon*Decimal(.035)).quantize(cent, rounding= ROUND_UP)
        print "\t Total" , Decimal(SSDD_G_mon).quantize(cent, rounding= ROUND_UP)+(Decimal(SSDD_ds_mon)).quantize(cent, rounding= ROUND_UP) + (SSDD_ds_mon*Decimal(.035)).quantize(cent, rounding= ROUND_UP)
        print
        print "MDA:"
        print "\t Hours:       H ", round(MDAhrs,2)
        print "\t Cost:        $ ", Decimal(MDAmon).quantize(cent, rounding= ROUND_UP)
        print
        print "*"*50
        print "FULL TOTAL : ",  Decimal(MDAmon).quantize(cent, rounding= ROUND_UP)\
        +(Decimal(SSDD_ds_mon)).quantize(cent, rounding= ROUND_UP)\
        +(SSDD_ds_mon*Decimal(.035)).quantize(cent, rounding= ROUND_UP)\
        +(Decimal(SED_ds_mon)).quantize(cent, rounding= ROUND_UP)\
        +(SED_ds_mon*Decimal(.03)).quantize(cent, rounding= ROUND_UP)\
        + Decimal(SSDD_G_mon).quantize(cent, rounding= ROUND_UP)\
        + Decimal(SED_G_mon).quantize(cent, rounding= ROUND_UP)
        print "*"*50
        print
        for x in people:
            print x
    linr = linr+"\n"
    logruns.write(str(linr))
    logruns.close()
    return 0
#
#
#
def dates_to_funding(dateratelookup, start_Date, workdays, people ,team, accountants):
    #
    # loop through workdays and team (non GNA )list and add hrs/values
    # if day is last day...round up hours/cost/round up to nearest cent
    #
    for day in workdays:
        for pol in team:
            if day> pol[pd.runout] :
                ratefilters = [lambda drl: drl[rd.contract]==pol[pd.contract],lambda drl: drl[rd.company] == pol[pd.company],
                lambda drl: drl[rd.lc] == pol[pd.lc],lambda drl: drl[rd.site] == pol[pd.site],
                lambda drl: drl[rd.dl]<=day, lambda drl: drl[rd.dg]>= day]
                try: 
                    rate = filter( lambda x: all(f(x) for f in ratefilters), dateratelookup )[0][rd.rate]
                    pol[pd.tr] = rate
                except:
                    if(pol[pd.tr] == rr.rr):
                        rate = Decimal(rr.rr)
                    else:
                        rf2 = [lambda drl: drl[rd.contract]==pol[pd.contract],lambda drl: drl[rd.company] == pol[pd.company],
                        lambda drl: drl[rd.lc] == pol[pd.lc],lambda drl: drl[rd.site] == pol[pd.site]]
                        dts = (filter( lambda x: all(f(x) for f in rf2), dateratelookup))
                        ld= sorted(list(set(dtsitem[rd.dg] for dtsitem in dts)), reverse = True)[0]
                        yrs = day.year - ld.year
                        mplier = pow(Decimal(1.03), yrs)
                        rate = (mplier*pol[pd.tr]).quantize(cent, rounding= ROUND_UP)
                if(day == workdays[len(workdays)-1]):
                    pol[pd.hrs]+= Decimal(8)*Decimal(pol[pd.loe])
                    pol[pd.val] += rate*Decimal(8)*Decimal(pol[pd.loe])
                    fx = Decimal(math.ceil(pol[pd.hrs]))-pol[pd.hrs]
                    pol[pd.hrs]+=fx
                    pol[pd.hrs] = int(pol[pd.hrs])
                    pol[pd.val] += fx*rate
                    pol[pd.val] = pol[pd.val].quantize(cent, rounding= ROUND_UP)
                else:
                    pol[pd.hrs] +=8*Decimal(pol[pd.loe])
                    pol[pd.val] += (rate*8*Decimal(pol[pd.loe]))
    #
    # Calculates GNA by contract (direct site GNA)
    #
    tolist = sorted(list(set([lin[pd.contract] for lin in team])))
    for to in tolist:
        hrs = sum(zip(*(filter(lambda gto : gto[pd.contract]==to, team)))[pd.hrs])
        mon=  sum(zip(*(filter(lambda gto : gto[pd.contract]==to, team)))[pd.val])
        #makes a guess for GNA FEES for a task order below at atleast 3%
        gna2spend = (Decimal(mon)*Decimal(.03)).quantize(cent, rounding= ROUND_UP)
        tspend = 0
        toacts = filter(lambda acts: to in acts[pd.gna].split(" "), accountants) #finds accountants related to contract
        while(gna2spend >0):
            if (tspend == gna2spend):
                if (to == "InHouse" or to == "MIPR"): #inhouse/mipr do not have associated gna fees
                    break
                else:
                    print to, "WARNING: Running Team With no GNA"
                    break
                    # sys.exit('No Change. ERROR IN GNA SPENDING')
            tspend = gna2spend
            #
            # iterates through accountants associated with Task Order (can be more than 1)
            #
            for pol in toacts: 
                ratefilters = [lambda drl: drl[rd.contract]==pol[pd.contract],lambda drl: drl[rd.company] == pol[pd.company],
                lambda drl: drl[rd.lc] == pol[pd.lc],lambda drl: drl[rd.site] == pol[pd.site],
                lambda drl: drl[rd.dl]<=day, lambda drl: drl[rd.dg]>= day]
                day = start_Date
                try:
                    rate1 = filter( lambda x: all(f(x) for f in ratefilters), dateratelookup )[0][rd.rate]
                    pol[pd.tr] = Decimal(rate1)
                except:
                    if(pol[pd.tr] == rr.rr):
                        rate1 = Decimal(rr.rr)
                    else:
                        rf2 = [lambda drl: drl[rd.contract]==pol[pd.contract],lambda drl: drl[rd.company] == pol[pd.company],
                        lambda drl: drl[rd.lc] == pol[pd.lc],lambda drl: drl[rd.site] == pol[pd.site]]
                        dts = (filter( lambda x: all(f(x) for f in rf2), dateratelookup))
                        ld= sorted(list(set(dtsitem[rd.dg] for dtsitem in dts)), reverse = True)[0]
                        yrs = day.year - ld.year
                        mplier = pow(Decimal(1.03), yrs)
                        rate1 = (mplier*pol[pd.tr]).quantize(cent, rounding= ROUND_UP)        
                pol[pd.hrs] += Decimal(pol[pd.loe])
                pol[pd.val] += (rate1*Decimal(pol[pd.loe]))
                pol[pd.tr] = rate1
                gna2spend -= (Decimal(rate1)*Decimal(pol[pd.loe]))
        #
        # rounds up hours for GNA/fixes any cent issues present
        #
        for pol in toacts:
            wn= Decimal(math.ceil(pol[pd.hrs]))-pol[pd.hrs]
            pol[pd.hrs]+=wn
            pol[pd.hrs] = int(pol[pd.hrs])
            pol[pd.val] += wn*pol[pd.tr]
            pol[pd.val] = pol[pd.val].quantize(cent, rounding= ROUND_UP)
    # combines team and GNA team together
    # people = team + accountants
    # Filters / SUMS by branch to eventually calculate BRANCH in house GNA
    return tolist, people   
#
# Scrapes OPM gov site for holiday tables and stores holidays 
#
def webScraper():
    holidays = []
    page = requests.get('https://www.opm.gov/policy-data-oversight/snow-dismissal-procedures/federal-holidays/')
    tree = html.fromstring(page.content)
    mdic = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
    years = tree.xpath('//caption/text()')
    for x in range(0, len(years)):
        y = years[x].split()
        holxpathpre = "//*/div/table/tbody/tr["
        holxpathpost =  "]/td[1]/text()"
        for hol in range(1,11):
            pt = holxpathpre+str(hol)+holxpathpost
            month = mdic.index(str(tree.xpath(pt)[x].split(",")[1].split()[0]))+1
            day = tree.xpath(pt)[x].split(",")[1].split()[1]
            year = y[0]
            holidays.append(date(int(year), int(month), int(day)))
    return holidays
#
# Reads in Team Data
#
def teamInput(jl):
    rows = []
    people = []
    for row in jl:
        rows.append(row)
    for row in range(1,len(rows)):
        if(len(rows[row])>0):  
            # try:
            #     month, day, year= rows[row][pd.runout].strip().split("/")
            # except:
            #     print rows[row]
            month, day, year= rows[row][pd.runout].strip().split("/")
            rows[row][pd.runout] = date(int(year), int(month), int(day))
            rows[row].append(Decimal(0)) #hours
            rows[row].append(Decimal(0)) # cost
            rows[row].append(Decimal(rr.rr)) # last known rate
            rows[row].append(int(0)) # days funded
            rows[row].append(int(0)) # hours funded
            rows[row].append("")
            people.append((rows[row]))
    return people
#
# Looks through ratefiles to filter and store necessary data based on team 
#
def dataMaker(people, spt):
    lst = functools.reduce(lambda x,y: dict(list(x.items()) + list(y.items())),
                            [{c[:-4]:list((io.open(os.path.join(spt,c),
                                                        newline='')))}
                            for c in os.listdir(spt)])
    dateratelookup = []
    block  = []
    count = 0       
    for i in lst.keys():
        bs = 0
        bnds = []
        val = str(lst[i][0])
        nval = val.replace("\t\t\t\t\t\t\t\t\t\t", "")
        bnds.append(-1)
        sl = 0
        for l in range (0, len(lst[i])): ###indice finder
            if (str(lst[i][l]).startswith("\t\t\t\t\t\t")):
                bs = l
                bnds.append(bs)
        for z in range (0, len(bnds)):
            justcomp = (str(lst[i][bnds[z]+1])).split('\t\t\t\t\t')
            justcomp[0] = justcomp[0].replace('\"', '')
            justcomp[0] = justcomp[0].replace('\'', '').replace('\t','')
            justcomp[0] = justcomp[0].strip()
            justcomp[0] = justcomp[0].replace('\r', '').replace('\n', '')
            sbl = []
            if ( z == len(bnds)-1):
                en = len(lst[i])
            else:
                en = bnds[z+1]
            
            to= i
            company = justcomp[0].strip()
            tocofilters = [lambda a:a[pd.contract] == to, lambda a: a[pd.company]== company] #only look at to/comp subtables pertaining to team
            check = filter( lambda x: all(f(x) for f in tocofilters), people )
            #
            #only look at to/comp subtables pertaining to team
            #
            if(check):
                print to, company
                daterow = lst[i][bnds[z]+2]
                daterow = daterow.encode('utf-8').replace('\r', '').replace('\n', '').replace(" ", "").split("\t")
                daterow = filter(lambda x: len(x)>0, daterow)[2:]
                raterows = lst[i][(bnds[z]+3):en]
                for raterow in raterows:
                    # print to, company, raterow
                    raterow = raterow.encode('utf-8').replace('\r', '').replace('\n', '').split("\t")
                    lc = raterow[0]
                    site = raterow[1]
                    jobfilters = [lambda a:a[pd.lc] == lc,  lambda b: b[pd.site]== site]
                    check2 = filter( lambda x: all(f(x) for f in jobfilters), check )
                    #
                    # filters company table and stores relevant labor category
                    #
                    if(check2):
                        print to, company, lc, site
                        raterow = (filter(lambda x: len(x)>0, raterow))[2:]
                        for index in range(0,len(raterow)):
                            try:
                                singlerange = daterow[index].replace(' ', '').split("-")
                            except:
                                print index, daterow[index]
                                print daterow
                            dstart = singlerange[0].encode('utf-8').strip()
                            dend = singlerange[1].encode('utf-8').strip()
                            m, d, y =  dstart.split("/")
                            dstart = date(int(y),int(m) ,int(d))
                            # print dend
                            m2, d2, y2 = dend.split("/")
                            dend = date(int(y2),int(m2) ,int(d2))
                            try: 
                                dateratelookup.append(tuple([to,company,lc,site,dstart,dend, Decimal(raterow[index])]))
                            except:
                                print "ERROR IN TABLE TXT FILE" , to, company, lc, dstart, dend, raterow[index]
                                print "adding -100 as rate"
                                dateratelookup.append(tuple([to,company,lc,site,dstart,dend, Decimal(-100)]))
    return dateratelookup

#
# Finds Workdays given a startdate and enddate
#
def workdayFinder(sdate,edd, holidays):
    workdays=[]
    print sdate, " to ", edd
    num = edd-sdate
    for a in range(num.days +1):
        aday = sdate + timedelta(days = a)
        if (aday.weekday() < 5) and (aday not in holidays):
            # print aday
            workdays.append(aday)  
    return workdays
#
# Solves Bounded Knapsack Problem (Dynamic)
#
def knapsack01_dp(items, limit):
    table = [[0 for w in range(limit + 1)] for j in xrange(len(items) + 1)]
    for j in xrange(1, len(items) + 1):
        item, wt, val = items[j-1]
        for w in xrange(1, limit + 1):
            if wt > w:
                table[j][w] = table[j-1][w]
            else:
                table[j][w] = max(table[j-1][w],
                                table[j-1][w-wt] + val)

    result = []
    w = limit
    for j in range(len(items), 0, -1):
        was_added = table[j][w] != table[j-1][w]

        if was_added:
            item, wt, val = items[j-1]
            result.append(items[j-1])
            w -= wt

    return result
if __name__ == '__main__':
    main()

# <!-- Markdeep: --><style class="fallback">body{visibility:hidden;white-space:pre;font-family:monospace}</style><script src="markdeep.min.js"></script><script src="https://casual-effects.com/markdeep/latest/markdeep.min.js"></script><script>window.alreadyProcessedMarkdeep||(document.body.style.visibility="visible")</script>