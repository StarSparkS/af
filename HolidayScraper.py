from datetime import date, timedelta, datetime
from decimal import *
from lxml import html
import requests

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