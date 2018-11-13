import math,os,csv,functools,operator,io,re,sys,csv,argparse, calendar
from copy import deepcopy
from collections import defaultdict
from pprint import pprint as pp
from datetime import date, timedelta, datetime
from decimal import *
from lxml import html
import requests
from itertools import groupby
taskdic = {}
#
# Read in Inputs/create data structures
#
def main():
    args = cmdread()
    logruns = open('RUN_LOG.csv', 'a')
    linr = str("Python 2.7   ")+ str(datetime.now().strftime('%Y-%m-%d %H:%M:%S')) + "\t\t"
    linr = linr+"\n"
    logruns.write(str(linr))
    logruns.close()
    # print(args)
    pd,rd,rr,ks = getenums()
    rf = open(args.file).read().split("\n") ##
    people = teamInput(pd, rr, csv.reader(rf))
    people = cmdPare(pd,rd,rr,ks,args, people)
    team = filter(lambda x: len(x[pd.gna]) == 0, people)
    accountants = filter(lambda x: len(x[pd.gna]) >0, people)
    start_Date = (map(min, zip(*(filter(lambda x: x[pd.runout].year > 1950, team))))[pd.runout])+timedelta(days=1)
    holidays = webScraper()
    dateratelookup = dataMaker(start_Date, pd, people, args.rates)
    if(args.amt):
        expend_funds(args,pd,rd,rr,ks, args.amt, people, team, accountants, start_Date, holidays, dateratelookup )
    return
def rlc(pd, rd, pol, day, dateratelookup):
    ratefilters = [lambda drl: drl[rd.contract]==pol[pd.contract],lambda drl: drl[rd.company] == pol[pd.company],
    lambda drl: drl[rd.lc] == pol[pd.lc],lambda drl: drl[rd.site] == pol[pd.site],
    lambda drl: drl[rd.dl]<=day, lambda drl: drl[rd.dg]>= day]
    try:
        # print filter( lambda x: all(f(x) for f in ratefilters), dateratelookup )[0]
        return filter( lambda x: all(f(x) for f in ratefilters), dateratelookup )[0]
    except: 
        print pol
        # a = [lambda drl: drl[rd.contract]==pol[pd.contract],lambda drl: drl[rd.company] == pol[pd.company],
        # lambda drl: drl[rd.lc] == pol[pd.lc]]
        # b = [lambda drl: drl[rd.contract]==pol[pd.contract],lambda drl: drl[rd.company] == pol[pd.company]]
        # print "a:", filter( lambda x: all(f(x) for f in a), dateratelookup )
        # print "b:", filter( lambda x: all(f(x) for f in b), dateratelookup )
        exit(1)
    # return 0   
    #     print pd, rd, pol, day
    #     exit(1)
    # try:
    #     return filter( lambda x: all(f(x) for f in ratefilters), dateratelookup )[0]
    # except:
    #     print pol
    #     print filter( lambda x: all(f(x) for f in ratefilters), dateratelookup )
    #     exit(1)
def expend_funds(args, pd,rd,rr,ks,funds, people, team, accountants, start_Date, holidays, dateratelookup):
    cent = Decimal('0.01')
    day = start_Date
    InHouseGNA = IHG = 0
    IHGssdd = 0
    IHGsed = 0
    print funds, "\n"
    if(len(accountants)> 0):
        ggna = (Decimal(funds)*Decimal(.03))
        ggna = ggna.quantize(cent, rounding= ROUND_HALF_UP)
        print "Guess GNA = 3%", ggna
        while(ggna>0):
            for pol in accountants:
                rate = rlc(pd, rd, pol,day,dateratelookup)[rd.rate]
                # print rate
                # print rate1
                # filter( lambda x: all(f(x) for f in ratefilters), dateratelookup )[0][rd.rate] =filter( lambda x: all(f(x) for f in ratefilters), dateratelookup )[0][rd.rate] +1
                # rate1 = rate1 +1
                # print (filter( lambda x: all(f(x) for f in ratefilters), dateratelookup )[0][rd.rate])
                # print pol[0]
                mval = len(pol[pd.gna].split(" "))
                # print mval
                pol[pd.hrs] += Decimal(mval)*Decimal(pol[pd.loe])
                # print Decimal(mval)*Decimal(pol[pd.loe])
                pol[pd.val] += (Decimal(mval)*Decimal(pol[pd.loe]) * rate)
                # print (Decimal(mval)*Decimal(pol[pd.loe]) * rate)
                ggna -=(Decimal(mval)*Decimal(pol[pd.loe]) * rate)
            if(ggna < 0): #you finished funding ggna evenly but now there may be hours that are not integer value, this condition will fix not integer hours
                for pol in accountants:

                    mval = len(pol[pd.gna].split(" "))
                    rate = rlc(pd, rd, pol,day,dateratelookup)[rd.rate]
                    mdf = Decimal(math.ceil(pol[pd.hrs])) - Decimal(pol[pd.hrs])
                    # print pol[0], mval, rate, mdf, pol[pd.hrs], pol[pd.val]
                    pol[pd.hrs] += mdf
                    pol[pd.hrs] = int(pol[pd.hrs])
                    # pol[pd.val] += (mdf * rate)
                    # print rlc(pd, rd, pol,day,dateratelookup)[rd.hrs]
                    rlc(pd, rd, pol,day,dateratelookup)[rd.hrs] = pol[pd.hrs]
                    # print rlc(pd, rd, pol,day,dateratelookup)[rd.hrs]
                    rlc(pd, rd, pol,day,dateratelookup)[rd.val] = (rlc(pd, rd, pol,day,dateratelookup)[rd.hrs] * rlc(pd, rd, pol,day,dateratelookup)[rd.rate]).quantize(cent, rounding= ROUND_HALF_UP)
                    pol[pd.val] = (rate * pol[pd.hrs])
                    # print pol[pd.val]
                    # print pol[0], mval, rate, mdf, pol[pd.hrs], pol[pd.val]
                    ggna -=(mdf * rate)
                    ggna = ggna
        # for pol in accountants:
        #     print pol
        # exit(1)
        #
        # Calculate new balance - GnA costs
        # 
        agna = sum(zip(*accountants)[pd.val])
        agnac = ((Decimal(funds)*Decimal(.03)).quantize(cent, rounding= ROUND_HALF_UP) + Decimal(abs(ggna))).quantize(cent, rounding= ROUND_HALF_UP)
        agnac2 = sum(zip(*dateratelookup)[rd.val])
        print agna, " == " , agnac, " == ", agnac2
        print "Actual GNA = ", agna
        balance = Decimal(funds)-Decimal(agna)
        print "Balance after GNA (variables) : ",funds , " - ", agna , " = ", balance
        # print "Stored Balance (data)", Decimal(funds) - sum(row[pd.val] for row in people)
        if (Decimal(funds) - sum(row[pd.val] for row in people) == balance):
            print "-----SUCCESS!----- INHOUSE GNA FUNDED WITH NO BALANCE ISSUES\n"
            # print "FUNDING INHOUSE GNA BASED ON DATA"
            print balance
            print "Success"
            print "-----"
        else:
            print "FAIL", balance, "\t", Decimal(funds) - sum(row[pd.val] for row in people)
            exit(1)
    else:
        print "Warning: NO GNA funding provided" 
        agna = Decimal(0)
        ggna = Decimal(0)
        balance = Decimal(funds)


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
            balance = funds
    
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
                    try:
                        rate = rlc(pd, rd, pol,day,dateratelookup)[rd.rate]
                    except:
                        rate = rr.rr
                        print pol
                        print "rate not found!!!!~"
                        exit(1)
                    # pol[pd.tr] = rate
                    teamcostforday += (Decimal(rate)*Decimal(8)*Decimal(pol[pd.loe]))
            #
            #if funding is available to fund the team for current day, fund the team
            # else-->
            #

            warns = [];

            if (balance - teamcostforday > 0): 
                for pol in team:
                    rate = rlc(pd, rd, pol,day,dateratelookup)[rd.rate]
                    if day>pol[pd.runout]:
                        # pol[pd.df] +=1
                        pol[pd.hrs] += Decimal(8)* Decimal(pol[pd.loe])
                        pol[pd.val] += (rate*Decimal(8)*Decimal(pol[pd.loe]))
                        if pol[pd.val].quantize(cent, rounding= ROUND_DOWN) != pol[pd.val]:
                            # print pol[pd.val].quantize(cent, rounding= ROUND_DOWN), " !=", pol[pd.val]
                            # print rate
                            # print pol[pd.name]
                            # print (rate*Decimal(8))
                            if pol not in warns:
                                warns.append(pol)
                        balance -=(rate*Decimal(8)*Decimal(pol[pd.loe]))
                        rlc(pd, rd, pol,day,dateratelookup)[rd.hrs] += Decimal(8)* Decimal(pol[pd.loe])
                        # if (rlc(pd, rd, pol,day,dateratelookup)[rd.hrs].quantize(cent, rounding= ROUND_DOWN) != rlc(pd, rd, pol,day,dateratelookup)[rd.hrs]):
                        # print rlc(pd, rd, pol,day,dateratelookup)[rd.hrs]
                        rlc(pd, rd, pol,day,dateratelookup)[rd.val] = (rlc(pd, rd, pol,day,dateratelookup)[rd.hrs] * rlc(pd, rd, pol,day,dateratelookup)[rd.rate]).quantize(cent, rounding= ROUND_HALF_UP)
                adf+=1
                lwd = day
            #
            # proceed here if you do not have funds to fund the team for a current day (a day)
            #
            else:
                # exit(1)
                #since you cannot fund the team for a day, compute the cost for funding the team for an hour
                # and see if funding by hour is possible
                tcfh = teamcostforhour = (teamcostforday/ Decimal(8))
                hrfundable = balance /tcfh 
                print "Day Funding Complete"
                print "HR Funding Initiated"
                #
                # balance check
                #
                if(Decimal(funds) - sum(row[pd.val] for row in people) != balance): 
                    print "UNBALANCED balances"
                    exit(1)
                #
                # end of balance check
                #
                #
                # Step 1: Balance hours to no decimal places to chip away at remainder if possible with split people
                #
                warns2 = []
                if(adf>0 and balance > 0): #This part is adjusting split 
                    spt = filter(lambda rt: (Decimal(rt[pd.loe]) >1.00 or Decimal(rt[pd.loe])<1.00) and (day>rt[pd.runout]), team)
                    for pol in spt:
                        # print 
                        if(int(pol[pd.hrs]) !=pol[pd.hrs]):
                                
                            ratefilters = [lambda drl: drl[rd.contract]==pol[pd.contract],lambda drl: drl[rd.company] == pol[pd.company],
                            lambda drl: drl[rd.lc] == pol[pd.lc],lambda drl: drl[rd.site] == pol[pd.site],
                            lambda drl: drl[rd.hrs] > 0]
                            # print pol
                            rcls = filter( lambda x: all(f(x) for f in ratefilters), dateratelookup )
                            print pol
                            for n in rcls:
                                dff = Decimal(math.ceil(n[rd.hrs])) - Decimal(n[rd.hrs])
                                balance -= Decimal(dff) * Decimal(n[rd.rate])
                                n[rd.hrs] = Decimal(math.ceil(n[rd.hrs]))
                                n[rd.val] = Decimal(n[rd.hrs])* Decimal(n[rd.rate])
                                # n[rd.hrs] -= pol[pd.hrs]
                                # n[rd.val] -= pol[pd.val]
                                # n[rd.hrs] = math.ceil(n[rd.hrs])
                                # n[rd.val] = Decimal(n[rd.hrs]) * Decimal(n[rd.rate])
                                # pol[pd.hrs] += n[rd.hrs]
                                # pol[pd.val] += n[rd.val]
                            warns2.append(pol)
                                
                    
                        # pol[pd.hrs] = int(pol[pd.hrs])

                    # print "Adjusted "
                    # for pol in warns2:
                    #     print pol
                        
                    # for row in spt:
                    #     dff = Decimal(math.ceil(row[pd.hrs])) - Decimal(row[pd.hrs])
                    #     row[pd.hrs] += dff
                    #     if(dff > 0):
                    #         balance += row[pd.val]
                    #         row[pd.hrs] = math.ceil(row[pd.hrs])
                    #         print row[pd.hrs]
                    #     pol = row
                    #     rlc(pd, rd, pol,day,dateratelookup)[rd.hrs] += dff
                    #     rlc(pd, rd, pol,day,dateratelookup)[rd.val] = (rlc(pd, rd, pol,day,dateratelookup)[rd.hrs] * rlc(pd, rd, pol,day,dateratelookup)[rd.rate]).quantize(cent, rounding= ROUND_HALF_UP)
                    #     rate = rlc(pd, rd, pol,day,dateratelookup)[rd.rate]
                    #     row[pd.val] += (dff * Decimal(rate))
                    #     balance -= (dff * Decimal(rate))
                    #     if(dff > 0):
                    #         print row
                    #         print row[pd.hrs]
                    #         print "expected:", Decimal(math.ceil(row[pd.hrs]))* Decimal(rate)
                    #         print "current:" ,row[pd.val]
                    #         print  rlc(pd, rd, pol,day,dateratelookup)[rd.hrs]
                    #         print  rlc(pd, rd, pol,day,dateratelookup)[rd.val]

                    #         print balance
                    # print "Balance after adjustments:", balance
                    # print "verify data", Decimal(funds) - sum(row[pd.val] for row in people)
                    if ((Decimal(funds) - sum(row[pd.val] for row in people)) == balance):
                        print "GOOD VERIFY"
                    print "rework"
                    print balance
                    totalallocated = sum(zip(*dateratelookup)[rd.val])
                    balance = Decimal(funds) - Decimal(totalallocated)
                    print balance

                    print "end rework"
                    # exit(1)
                    #
                    #The following balance<0 is met when you fund the team for days and proceed to try and fund the team by hours
                    # when you clean up the split hours and you have a negative balance, this condition is met
                    # at this point everyone has whole hours, but the balance is less than 0
                    #
                    if(balance <0):
                        print 'balance < 0 CONDITION!!!!!!!!!!!'
                        rates = sorted(list(set([rlc(pd, rd, pol,day,dateratelookup)[rd.rate] for pol in team])))
                        for row in rates:
                            if (row+balance >0):
                                # tu = filter(lambda a: a[pd.tr] == row, team)
                                for pol in team:
                                    if(rlc(pd, rd, pol,day,dateratelookup)[rd.rate] == row):
                                        print pol
                                        pol[pd.val] -= rlc(pd, rd, pol,day,dateratelookup)[rd.rate]
                                        pol[pd.hrs] -= 1
                                        rlc(pd, rd, pol,day,dateratelookup)[rd.hrs] -= 1
                                        rlc(pd, rd, pol,day,dateratelookup)[rd.val] = (rlc(pd, rd, pol,day,dateratelookup)[rd.hrs] * rlc(pd, rd, pol,day,dateratelookup)[rd.rate]).quantize(cent, rounding= ROUND_HALF_UP)
                                        break
                                # tu[0][pd.df] -= 1
                                # tu[0][pd.hf] +=7
                                balance += row
                                break
                                exit(1)
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
                                pol = row
                                rate = rlc(pd, rd, pol,day,dateratelookup)[rd.rate]
                                if (balance >(wtconstraint) and (balance - Decimal(rate) > 0)) and day>row[pd.runout]:
                                    row[pd.hrs] += 1
                                    row[pd.val] += Decimal(rate)
                                    rlc(pd, rd, pol,day,dateratelookup)[rd.hrs] += 1
                                    rlc(pd, rd, pol,day,dateratelookup)[rd.val] = (rlc(pd, rd, pol,day,dateratelookup)[rd.hrs] * rlc(pd, rd, pol,day,dateratelookup)[rd.rate]).quantize(cent, rounding= ROUND_HALF_UP)
                                    # row[pd.hf] += 1
                                    balance -= Decimal(rate)
                                    # print balance, wtconstraint
                        for row in team:
                            row[pd.hrs] = int(row[pd.hrs])
                            row[pd.val] = row[pd.val]
                        print "REAL BALANCE: ", Decimal(funds) - sum(row[pd.val] for row in people)
                        print balance
                        finalbalance = balance
                        balance = 0 
                else: #this will only occur if you input funding less than a day
                    #"FUND BY FULL HR ONLY"
                    prevbalance = 0
                    while (balance>0):
                        for pol in team:
                            if day>pol[pd.runout]:
                                rate = rlc(pd, rd, pol,day,dateratelookup)[rd.rate]
                                if (balance - Decimal(rate) >0):
                                    pol[pd.hrs] += 1
                                    rlc(pd, rd, pol,day,dateratelookup)[rd.hrs] += 1
                                    rlc(pd, rd, pol,day,dateratelookup)[rd.val] = (rlc(pd, rd, pol,day,dateratelookup)[rd.hrs] * rlc(pd, rd, pol,day,dateratelookup)[rd.rate]).quantize(cent, rounding= ROUND_HALF_UP)
                                    pol[pd.val] += (Decimal(rate))
                                    balance -=(Decimal(rate))
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
    print "Initial Balance: ", funds
    print "GNA: " , agna
    print "Team: ", ob - finalbalance
    print 
    print "##########################"
    print "This is final balance" , finalbalance
    print "verify", sum(row[pd.val] for row in people)
    print "verify2", sum(zip(*dateratelookup)[rd.val])
    # exit(1)
    print "AMT" , Decimal(funds) - sum(row[pd.val] for row in people)
    print "AMT2", Decimal(funds) - sum(zip(*dateratelookup)[rd.val])
    nb = 0
    if(Decimal(funds) - sum(row[pd.val] for row in people) == finalbalance):
        print "GOOD VERIFY"
        nb = finalbalance
    else:
        print "ROUNDING ISSUE?????"
        nb = (Decimal(funds) - sum(row[pd.val] for row in people))
    print 
    print "##########################"
    print "Funding Covers Approx:", start_Date , "-",lwd
    print "last full day of coverage", lwd
    print "possibly partially funded day", day
    tb1 = finalbalance       
    rld = sorted(list(set([rlc(pd, rd, pol,day,dateratelookup)[rd.rate] for pol in team])))
    rld = filter(lambda x : len(str(x))>0 , rld)
    print rld
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
        colasi = sorted(list(set([tuple([tuple([lin[pd.contract], lin[pd.company], lin[pd.lc], lin[pd.site]]), rlc(pd, rd, lin,day,dateratelookup)[rd.rate], rlc(pd, rd, lin,day,dateratelookup)[rd.rate],math.ceil(tb1/ rlc(pd, rd, lin,day,dateratelookup)[rd.rate])]) for lin in adata])))
    else:
        colasi = sorted(list(set([tuple([tuple([lin[pd.contract], lin[pd.company], lin[pd.lc], lin[pd.site]]), rlc(pd, rd, lin,day,dateratelookup)[rd.rate], rlc(pd, rd, lin,day,dateratelookup)[rd.rate], mxh ]) for lin in adata])))
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
    print aloc
    # exit(1)
    caloc = 0
    for row in aloc:
        rt = Decimal(row[2])/ Decimal(100)
        row = row[0]
        print row
        fr = [lambda w: w[pd.contract] == row[0], lambda x: x[pd.company] == row[1], lambda y: y[pd.lc] == row[2], lambda z: z[pd.site]==row[3], lambda a: day > a[pd.runout]] 
        v = sorted(filter(lambda x: all(f(x) for f in fr), team), key = lambda x : x[pd.hrs])
        pol = v[0]
        rate = rlc(pd, rd, pol,day,dateratelookup)[rd.rate]
        v[0][pd.hrs] += 1
        rlc(pd, rd, pol,day,dateratelookup)[rd.hrs] +=1
        v[0][pd.val] += rate
        rlc(pd, rd, pol,day,dateratelookup)[rd.val] = (rlc(pd, rd, pol,day,dateratelookup)[rd.hrs] * rlc(pd, rd, pol,day,dateratelookup)[rd.rate]).quantize(cent, rounding= ROUND_HALF_UP)
        caloc += rate
        # v[0][pd.hf] += 1
    tolist = sorted(list(set([lin[pd.contract] for lin in people])))
    # exit(1)
    ####Data Adjustment Complete
    #
    # Outputs Cost by Task Order and by Labor Category
    #
    print " Final Verification"
    print "Input Amount: ", funds
    total = sum(row[pd.val] for row in people)
    # print total , funds
    if (total == Decimal(funds)):
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
        if (total < Decimal(funds)):
            print "Leftover amount", Decimal(funds) - total
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
            print funds
    ###########################  
    # Add your OWN FILTER HERE to filter by team color/ team name/ etc
    #
    # pp(people)
    #
    ngs = ["MIPR", "InHouse", "InHouse-SSDD", "InHouse-SED", "InHouse-MDA"]
    try:
        SEDhrs = sum(zip(*(filter(lambda gto : gto[pd.center]=="S3I", people)))[pd.hrs])
    except:
        SEDhrs =  0
    try:
        SED_G_mon = sum(zip(*(filter(lambda gto : gto[pd.center]=="S3I" and gto[pd.contract] in ngs , people)))[pd.val])
    except:
        SED_G_mon = 0
    try:
        SED_ds_mon=  sum(zip(*(filter(lambda gto : gto[pd.center]=="S3I" and gto[pd.contract] not in ngs , people)))[pd.val])
    except:
        SED_ds_mon = 0
    try:
        SSDDhrs = sum(zip(*(filter(lambda gto : gto[pd.center]=="S3I", people)))[pd.hrs])
    except:
        SSDDhrs = 0
    try:
        SSDD_G_mon = sum(zip(*(filter(lambda gto : gto[pd.center]=="S3I" and gto[pd.contract] in ngs , people)))[pd.val])
    except:
        SSDD_G_mon = 0
    try:
        SSDD_ds_mon=  sum(zip(*(filter(lambda gto : gto[pd.center]=="S3I" and gto[pd.contract] not in ngs , people)))[pd.val])
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
    print "S3I: "
    print "\t Hours:       H ", round(SEDhrs, 2)
    print "\t Cost_DS:      $ ", Decimal(SED_ds_mon)
    print "\t Cost_G       $ ", Decimal(SED_G_mon)
    print "\t InHouseGnA:  $ ", (SED_ds_mon*Decimal(.027))
    print "\t InHouse Total $", Decimal(SED_G_mon) + (SED_ds_mon*Decimal(.027))
    print "\t Total" , Decimal(SED_G_mon)+(Decimal(SED_ds_mon)) + (SED_ds_mon*Decimal(.027))
    print
    print "S3I: "
    print "\t Hours:       H ", round(SSDDhrs,2)
    print "\t Cost_DS:        $ ", Decimal(SSDD_ds_mon)
    print "\t Cost_G       $ ", Decimal(SSDD_G_mon)
    print "\t InHouseGnA:  $ ", (SSDD_ds_mon*Decimal(.027))
    print "\t InHouse Total $", Decimal(SSDD_G_mon) + (SSDD_ds_mon*Decimal(.027))
    print "\t Total" , Decimal(SSDD_G_mon)+(Decimal(SSDD_ds_mon)) + (SSDD_ds_mon*Decimal(.027))
    print
    print "MDA:"
    print "\t Hours:       H ", round(MDAhrs,2)
    print "\t Cost:        $ ", Decimal(MDAmon)
    print
    print "*"*50
    print "FULL TOTAL : ",  Decimal(MDAmon)\
    +(Decimal(SSDD_ds_mon))\
    +(SSDD_ds_mon*Decimal(.027))\
    +(Decimal(SED_ds_mon))\
    +(SED_ds_mon*Decimal(.027))\
    + Decimal(SSDD_G_mon)\
    + Decimal(SED_G_mon)
    print "*"*50
    print
    for x in people:
        print x
    print '\n'*20
    niceoutput = filter(lambda x: x[rd.hrs]>0, dateratelookup)
    tos = sorted(list(set([item[rd.contract] for item in dateratelookup])))
    # ratefilters = [lambda drl: drl[rd.contract]==pol[pd.contract],lambda drl: drl[rd.company] == pol[pd.company],
    # lambda drl: drl[rd.lc] == pol[pd.lc],lambda drl: drl[rd.site] == pol[pd.site], lambda drl: drl[rd.hrs] >0]
    # return filter( lambda x: all(f(x) for f in ratefilters), dateratelookup )[0]
    for a in tos:
        print "-------------------", a , "----------------------"
        ratefilters = [lambda drl: drl[rd.contract]== a, lambda drl: drl[rd.hrs] >0]
        comps= filter( lambda x: all(f(x) for f in ratefilters), niceoutput )
        comps2 = sorted(list(set([item[rd.company] for item in comps])))
        for n in comps2:
            print "#"*50
            print n
            print "#"*50
            filters2 = [lambda drl: drl[rd.contract]== a,lambda drl: drl[rd.company]== n, lambda drl: drl[rd.hrs] >0]
            lcs = filter( lambda x: all(f(x) for f in filters2), comps )
            lcs2 = sorted(list(set([item[rd.lc] for item in lcs])))
            for x in lcs:
                print x[rd.lc], " ", x[rd.site], " ", x[rd.dl], " ", x[rd.dg], " ", x[rd.hrs], " ", x[rd.val]
            # for b in lcs2:
            #     print
            #     print b
            #     print
            #     filters3 = [lambda drl: drl[rd.contract]== a,lambda drl: drl[rd.company]== n, lambda drl: drl[rd.lc]== b, lambda drl: drl[rd.hrs] >0]
            #     pts = filter( lambda x: all(f(x) for f in filters3), lcs )
            #     pts2= sorted(list(set([item[rd.site] for item in pts])))
            #     for c in pts2:
            #         print
            #         print c
            #         print
            #         filters4 = [lambda drl: drl[rd.contract]== a,lambda drl: drl[rd.company]== n, lambda drl: drl[rd.lc]== b, lambda drl: drl[rd.site]== c, lambda drl: drl[rd.hrs] >0]
            #         st = filter( lambda x: all(f(x) for f in filters4), pts )
            #         print st
            #         print
    print "End"

    balance = Decimal(funds) - Decimal(sum(zip(*dateratelookup)[rd.val]))
    print balance
    fcbs = set(peeps[pd.contract] for peeps in people)
    fcbs = list(fcbs)
    v= []
    for n in fcbs:
        # p = sum(zip(*list(filter(lambda x: x[rd.contract] == n, dateratelookup))))
        fr = filter(lambda x: x[rd.contract] == n, dateratelookup)
        p = sum(zip(*fr)[rd.val])
        print "####"
        print "####"
        print n
        print p
        print "####"
        v.append(p)
    print v
    print
    print "Input:", funds
    print "Output:", Decimal(sum(zip(*dateratelookup)[rd.val]))

    if (args.lu):
        print "OUTPUT To Be Generated"
        now = datetime.now()
        for a in tos: 
            n = a.split("-")
            n = n[len(n)-1]
            n = "TO_" + a + "_LTM_RUN_" + str(now.date()) +".csv" #+ "_" + str(now.time())
            amz = (os.path.join(sys.path[0],'ACTS',str(n)))
            toa = csv.writer(open(amz, 'wb'))
            toa.writerow([str(a)])
            toa.writerow([str(now.date())])
            toa.writerow([str(now.time())])
            toa.writerow(["Funds Allocated:"+ str(funds)])
            toa.writerow(" ")
            print "-------------------", a , "----------------------"
            ratefilters = [lambda drl: drl[rd.contract]== a, lambda drl: drl[rd.hrs] >0]
            comps= filter( lambda x: all(f(x) for f in ratefilters), niceoutput )
            comps2 = sorted(list(set([item[rd.company] for item in comps])))
            for n in comps2:
                print "#"*50
                print n
                print "#"*50

                filters2 = [lambda drl: drl[rd.contract]== a,lambda drl: drl[rd.company]== n, lambda drl: drl[rd.hrs] >0]
                lcs = filter( lambda x: all(f(x) for f in filters2), comps )
                lcs2 = sorted(list(set([(item[rd.lc], item[rd.site]) for item in lcs])))
                
                dstart = sorted(list(set([item[rd.dl] for item in lcs])))
                dend = sorted(list(set([item[rd.dg] for item in lcs])))
                print
                # print lcs 
                print lcs2
                print dstart
                print dend
                n = n.split("-")
                b = ["CONTRACTOR",(n[0].strip()), n[1].strip()]
                tds = len(dstart)
                for v in range(0, tds):
                    b.append( str(dstart[v].month) +"/"+ str(dstart[v].day) + "/"+ str(dstart[v].year) + " - " + str(dend[v].month) +"/"+ str(dend[v].day) + "/"+ str(dend[v].year))
                print b
                toa.writerow(b)
                # exit(1)
                # b = "CONTRACTOR" + ","+ str(n[0].strip()) + "," + n[1].strip() + "\n"
                # toa.writerow(["CONTRACTOR",str(n[0].strip()), n[1].strip()])
                for x in lcs2:
                   
                    b = ["CATEGORY", str(list(x)[0]), str(list(x)[1]) ]
                    for v in range(0,tds):
                        b.append(" ")
                    hrfil =[ lambda y: y[rd.lc] == list(x)[0], lambda y: y[rd.site] == list(x)[1]]
                    relh = sorted(filter( lambda x: all(f(x) for f in hrfil), lcs))
                    for x in relh:
                        # hrs = x[rd.hrs]
                        print x[rd.hrs]
                        b[3 + dstart.index(x[rd.dl])] = int(x[rd.hrs])

                    toa.writerow(b)
                    print
                    print x
                    print 
                    print
                    # print x[rd.lc], " ", x[rd.site], " ", x[rd.dl], " ", x[rd.dg], " ", x[rd.hrs], " ", x[rd.val]
                    # b= str(x[rd.lc])+ " "+ str(x[rd.site])+ " "+ str(x[rd.dl])+ " "+str(x[rd.dg])+ " "+ str(x[rd.hrs])+ " "+ str( x[rd.val]) +"\n"
                    # toa.write(b)
                toa.writerow("")
            # toa.close()
        # exit(1)
        
     #
#
#Knapsack
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

#
#  Parses commandline arguments, Stores them in args variable, Establishes commandline help
#
def cmdread():
    parser = argparse.ArgumentParser(description='Command-line, Automated Budgeting and Projection Program in Python.') 
    parser.add_argument('file', metavar='FILE',help='the input team file to read from')
    parser.add_argument('rates', metavar='RATE',help='the input rates file to read from')
    parser.add_argument('eqs', metavar='EQS',help='the input equivalency file to read from')
    parser.add_argument('log', metavar="LOG",help='Keeps track of when tests were run') 
    parser.add_argument('-tf', metavar='TFR',help="Filter One File and test only certain Team")
    parser.add_argument('-name', metavar='NAME',help="singleName (""first.last"") for projecting/funding")
    parser.add_argument('-lu', action='store_true',help="Generates ACTS LABOR UPLOAD CSV upload template")
    #features in progress
    
    parser.add_argument('-date', metavar='DATE',help="Enter Date to Find Money Required to reach Date yyyy-mm-dd")
    parser.add_argument('-amt', metavar='AMOUNT',help="Enter Amount to Find Runouts and Distribution of Hours For All task orders")
    parser.add_argument('-ksr', metavar='RATIO',help="Testing Ratio")
    parser.add_argument('-rl', action='store_true', help="Removes Balancing Limits to Burn Down Money")
 
    parser.add_argument('-comp', metavar='CMP',help="Filter by company")
    parser.add_argument('-exl', metavar="EXL", help="Runs without a certain company")

    args = parser.parse_args()
    return args 
#
# Taper data based on command line arguments
#
def cmdPare(pd,rd,rr,ks, args, people): #builds list of people relevant to calculations
    # newPeople = []
    if(args.eqs):
        eqss = open(args.eqs).read().split("\n") 
        for n in eqss:
            if(len(n) > 0):
                taskdic[n.split()[0]]= str(n.split()[1])   
    if(args.tf):
        ti = str(args.tf).split("/")
        contracts = []
        for to in range (0, len(ti)):
            contracts.append(taskdic[ti[to]])        
        fp = filter(lambda gto : gto[pd.contract] in contracts, people)
        people = fp
        # linr = linr + "Contracts: \t" + args.tf + '\t\t'
    if(args.name):
        people = filter(lambda gto: gto[pd.name] == str(args.name.replace(".", " ")), people)
        # people = filter(lambda gto: gto[pd.gna] == str(args.name.replace(".", " ")), people)
  
    return people
#
# Enum Function creates enums
#
def enum(**enums):
    return type('Enum', (), enums)
#
# Define enums for program
#
def getenums():  
    pd = enum(name=0,color=1,customer=2,center=3,contract=4,company=5,lc=6,site=7,loe=8,runout=9,gna=10,hrs=11, val = 12)
    rd = enum(contract=0,company=1,lc=2,site=3,dl=4,dg=5,rate=6,hrs=7, val = 8)
    rr = enum(rr = Decimal(130))
    ks = enum(ratio = Decimal(1)) # need to create a ratio that automically adjusts based on # of people in test and amount of money
    return [pd,rd,rr,ks]
#
# Reads in Team Data
#
def teamInput(pd,rr,jl):
    people = []
    for i, row in enumerate(jl):
        if(i>0 and len(row)>0):
            month, day, year= row[pd.runout].strip().split("/")
            row[pd.runout] = date(int(year), int(month), int(day))
            # print(row[0:4]) #person + center ,# print(row[4:8]) # key # print(row[8]) #weight
            # print(row[9]) #runout# print(row[10]) #accountant
            if(Decimal(row[8]) > 0): #Append people/lcs that are to be funded
                people.append(row+[0,0])
    return people
#
# Add Rates   
#
def dataMaker(start_Date, pd, people, spt):
    lst = functools.reduce(lambda x,y: dict(list(x.items()) + list(y.items())),
                            [{c[:-4]:list((io.open(os.path.join(spt,c),
                                                        newline='')))}
                            for c in os.listdir(spt)])
    dateratelookup = []
    block  = []
    count = 0     
    # print "hello"
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
            # print people
            #
            #only look at to/comp subtables pertaining to team
            #
            if(check):
                # print to, company
                # print (to, company)
                daterow = lst[i][bnds[z]+2]
                daterow = daterow.replace('\r', '').replace('\n', '').replace(" ", "").split("\t")
                daterow = list(filter(lambda x: len(x)>0, daterow))[2:]
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
                        # print (to, company, lc, site)
                        raterow = list(filter(lambda x: len(x)>0, raterow))[2:]
                        # print raterow
                        for index in range(0,len(raterow)):
                            try:
                                singlerange = daterow[index].replace(' ', '').split("-")
                            except:
                                print (index, daterow[index])
                                print (daterow)
                            dstart = singlerange[0].strip()
                            dend = singlerange[1].strip()
                            m, d, y =  dstart.split("/")
                            dstart = date(int(y),int(m) ,int(d))
                            m2, d2, y2 = dend.split("/")
                            dend = date(int(y2),int(m2) ,int(d2))
                            try: 
                                if(dend > start_Date):
                                    dateratelookup.append([to,company,lc,site,dstart,dend, Decimal(raterow[index]), 0, Decimal(0.00)])
                                # tc =tuple([to,company,lc,site,dstart,dend, Decimal(raterow[index])])
                                # lc[tc] =0
                            except:
                                print ("ERROR IN TABLE TXT FILE" , to, company, lc, dstart, dend, raterow[index])
                                print ("adding -100 as rate")
                                exit(1)
                                # dateratelookup.append(tuple([to,company,lc,site,dstart,dend, Decimal(-100)]))
    return dateratelookup
#
#Scrapes government holidays from opm.gov
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
if __name__ == '__main__':
    main()