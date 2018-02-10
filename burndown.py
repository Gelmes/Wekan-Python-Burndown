# burndown.py
# Author: Marco Rubio
# Date  : 2/9/2018
# Desc  : Creates a burn down plot from the wekan mongodb data

from pymongo import MongoClient
import datetime
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.cbook as cbook
import time                         # time.strptime # For datetime compairons

# Configuration Cariables
URL  = 'localhost'
PORT = 27019

def get_parenthesis(string):
    """Get number in parenthesis or return 0"""
    start = string.find("(") # Verify we have (
    end   = string.find(")") # Verify we have )
    value= 0
    if(start != -1):
        if(end != -1):
            value= int(string[start+1:end])
    return value 


# Set up database connection
client = MongoClient(URL, PORT)
print (client)
db = client.wekan
cards = db.cards.find({'boardId' : 'SHKrzWPfwbRDCr2jW'}).sort("dateLastActivity")

#Prepare for ploting
dates  = [datetime.datetime(2000,1,1)]
values = 0                          # Running Total
total  = [0]
for card in cards:
    expected = get_parenthesis(card['title'])
    print("Title   : " + card['title'])
    if(expected):
        print("Expected: " + str(expected))
        # date1 = time.strptime(prev_date     , "%Y-%m-%dT%H:%M:%S.%fZ")
        #print(card['dateLastActivity'])
        # date2 = time.strptime(card['dateLastActivity'], "%Y-%m-%dT%H:%M:%S.%fZ")
        if(card['dateLastActivity'].date() > dates[-1].date()):
            dates.append(card['dateLastActivity'])
            total.append(total[-1]+expected)
        else:
            total[-1] += expected
dates.pop(0)
total.pop(0)
print(dates)
print(total)


np_dates = np.array(dates)
np_total = np.array(total)
# Set Up Plot

days = mdates.DayLocator()  # every month
hours = mdates.HourLocator(interval=6)  # every day
dayFmt = mdates.DateFormatter('%b-%d')

fig, ax = plt.subplots()
ax.plot(np_dates, np_total)

# format the ticks
ax.xaxis.set_major_locator(days)
ax.xaxis.set_major_formatter(dayFmt)
ax.xaxis.set_minor_locator(hours)

fst = np_dates.min()
snd = np_dates.max()
datemin = datetime.date(fst.year, fst.month, fst.day)
datemax = datetime.date(snd.year, snd.month, snd.day)
ax.set_xlim(datemin, datemax)


# format the coords message box
def price(x):
    return '$%1.2f' % x
ax.format_xdata = mdates.DateFormatter('%Y-%m-%d')
ax.format_ydata = price
ax.grid(True)

# rotates and right aligns the x labels, and moves the bottom of the
# axes up to make room for them
fig.autofmt_xdate()

plt.show()
